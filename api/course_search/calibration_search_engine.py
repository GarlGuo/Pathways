import numpy as np
from data_loader import GlobalData, remove_nonalphanumeric, read_pickle_files
from database.pathway_class import simple_jsonify_course_list
import scipy.sparse
from addr_info import *
from database.redis_accessor import Calibration_Redis_Handler
from database.response import Redis_RESPONSE


class CalibrationEngine:
    def __init__(self, redis_handler, data_loader) -> None:
        self.data_loader = data_loader
        self.redis_handler = redis_handler


# requires: t shouldn't be too large
def exponential_weight(t):
    return 2 ** (t - 1)

# def linear_weight(t):
#     return t

class CalibrationEngineImpl(CalibrationEngine):

    def __init__(self, redis_handler: Calibration_Redis_Handler,
                 data_loader: GlobalData,
                 determinisitic=False) -> None:
        super().__init__(redis_handler, data_loader)
        self.powerset_lookup = {
            1: [],
            2: [[0, 1]],
            3: [[0, 1], [0, 2], [1, 2], [0, 1, 2]]
        }
        self.powerset_weight_lookup = {
            i: exponential_weight(i) for i in range(1, 4)
        }
        self.calibration_batch_num_map_relevance_score_lookup = {
            0: 0.5,
            1: 0.3,
            2: 0.15,
            3: 0.1,
            4: 0.05,
            5: 0.03
        }

        self.course_dept_abv_list = set(
            c.dept_abv for c in self.data_loader.courses_list)
        self.arange_course_cnt = np.arange(self.data_loader.courses_cnt)
        self.course_idx_dept_abv_pair_list = np.zeros(
            dtype=[('index', np.int64), ('dept_abv', np.int64)],
            shape=(self.data_loader.main_course_cnt, )
        )
        self.course_idx_dept_abv_pair_list['index'] = np.arange(self.data_loader.main_course_cnt)
        self.course_idx_dept_abv_pair_list['dept_abv'] = self.data_loader.course_dept_abv_idx_list

        self.deterministic = determinisitic

    # return a sparse array as QC matrix (shape as (# of queries, # of courses))
    def cosine_similarity_on_course_desc_idf_score(self, query_list):
        idf_score = self.data_loader.course_desc_tfidf_vectorizer.transform(
            query_list)
        return idf_score @ self.data_loader.course_desc_sparse_idf_scores.T

    def cosine_similarity_on_course_title_idf_score(self, query_list):
        idf_score = self.data_loader.course_title_tfidf_vectorizer.transform(
            query_list)
        return idf_score @ self.data_loader.course_title_sparse_idf_scores.T

        # ret = []
        # for q in query_list:
        #     if len([qi for qi in q.split() if qi]) == 1:
        #         idf_score = self.data_loader.course_title_unigram_tfidf_vectorizer.transform([q])
        #         ret.append(idf_score @ self.data_loader.course_title_unigram_sparse_idf_scores.T)
        #     else:
        #         idf_score = self.data_loader.course_title_bigram_tfidf_vectorizer.transform([q])
        #         ret.append(idf_score @ self.data_loader.course_title_bigram_sparse_idf_scores.T)
        # return scipy.sparse.vstack(ret, format='csr')

    # return a np.boolean mask array
    def exact_match_string(self, string_list, string):
        return scipy.sparse.csr_matrix(np.core.defchararray.find(string_list, string) != -1)

    # requires: batch_num should be a natural number
    def calibration_relevance_score_cutline(self, batch_num):
        if batch_num >= 6:
            return 0.03
        else:
            return self.calibration_batch_num_map_relevance_score_lookup[batch_num]

    def course_title_exact_match_keywords(self, keyword_list):
        processed_query_list = np.array(
            [self.data_loader.preprocess_query(q) for q in keyword_list])
        return scipy.sparse.vstack([self.exact_match_string(
            self.data_loader.course_title_list, q) for q in processed_query_list])

    def sparse_prod_axis0(self, A):
        # Valid mask of row length that has all non-zeros along each col
        # Thanks to @hpaulj on this!
        valid_mask = A.getnnz(axis=0) == A.shape[0]
        # Initialize o/p array of zeros
        out = np.zeros(A.shape[1], dtype=A.dtype)
        # Set valid positions with prod of each col from valid ones
        out[valid_mask] = np.prod(A[:, valid_mask].A, axis=0)
        return scipy.sparse.csr_matrix(out)

    # requires: 1 <= len(keyword_list) <= 3
    def course_powerset_match_query(self, QC):
        K = QC.shape[0]
        ret = scipy.sparse.csr_matrix(QC.sum(axis=0))
        for idx_list in self.powerset_lookup[K]:
            t = len(idx_list)
            ret += self.powerset_weight_lookup[t] * \
                self.sparse_prod_axis0(QC[idx_list, :]).power(1/t)
        return ret.toarray().reshape(QC.shape[1],)

    # input: shape of QC = (# of queries, # of courses)
    def course_span_match_query(self, QC, threshold=0.1, weight_aggregator=exponential_weight):
        threshold = (threshold * QC.max(axis=1)).toarray()
        QC_greater_than_threshold = np.vstack([QC[i] > threshold[i] for i in range(QC.shape[0])])
        none_zero_prod = np.prod(QC.toarray(), axis=0, where=QC_greater_than_threshold, keepdims=False)
        nnz_indice = none_zero_prod != 1
        nnz_count_axis0 = np.sum(QC_greater_than_threshold[:, nnz_indice], axis=0).A1
        ret = np.zeros(QC.shape[1])
        ret[nnz_indice] = weight_aggregator(nnz_count_axis0) * (none_zero_prod[nnz_indice] ** (1/nnz_count_axis0))
        return ret

    def get_interest_keywords_in_redis_saveable_format(self, interest_keywords):
        return ','.join(remove_nonalphanumeric(s) for s in interest_keywords)

    def retrieve_redis_data(self, interest_keywords):
        try:
            redis_nonzero_relevance_dict = \
                self.redis_handler.retrieve_none_zero_relevance_score(
                    interest_keywords)
            if Redis_RESPONSE.is_unfound(redis_nonzero_relevance_dict):
                return (False,)
            redis_nonzero_relevance_dict = redis_nonzero_relevance_dict.value
            ret = np.zeros(self.data_loader.main_course_cnt)
            for k, v in redis_nonzero_relevance_dict.items():
                ret[k] = v
            return (True, ret)
        except:
            return (False,)

    def save_redis_data(self, interest_keywords, relevance_score):
        try:
            nonzero_idx_map_score = dict()
            for idx in relevance_score.nonzero()[0]:
                nonzero_idx_map_score[int(idx)] = float(relevance_score[idx])
            return self.redis_handler.save_none_zero_relevance_score(interest_keywords, nonzero_idx_map_score)
        except BaseException as e:
            return Redis_RESPONSE.errors(str(e))

    def should_filter_course_at_runtime(self, c):
        return int(c.course_main_key[-4:]) >= 5000

    def generate_algorithm_data(self, ret_C_idx, R, CD, CT, CD_raw, CT_raw):
        R_ranking = np.argsort(-R)
        return {
            "first 3 courses R": [(R[c_idx], self.data_loader.main_courses_list[c_idx].course_title) for c_idx in R_ranking[:3]],
            "R": R[ret_C_idx].tolist(), 
            "CD": CD[ret_C_idx].tolist(), 
            "CT": CT[ret_C_idx].tolist(),
            "CD_raw": CD_raw[:, ret_C_idx].T.toarray().tolist(), 
            "CT_raw": CT_raw[:, ret_C_idx].T.toarray().tolist()
        }
    
    def select_batch(self, R, CD, CT, CD_raw, CT_raw, dept_abv_map_course_courseidx_list):
        dept_abvs_c_cidx_items = list(dept_abv_map_course_courseidx_list.items())
        ret_course_array = []
        ret_C_idx = []
        selected_course_main_key = set()
        for course_idx_pair_lst in np.random.permutation(np.arange(len(dept_abvs_c_cidx_items))):
            course_idx_pair_lst = dept_abvs_c_cidx_items[course_idx_pair_lst][1]
            length = len(course_idx_pair_lst)
            for i in np.random.permutation(np.arange(length))[:min(2, length)]:
                if len(ret_course_array) == 8:
                    break
                c, idx = course_idx_pair_lst[i]
                selected_course_main_key.add(c.course_main_key)
                ret_course_array.append(c)
                ret_C_idx.append(idx)
        while len(ret_course_array) < 8:
            i = np.random.randint(0, self.data_loader.main_course_cnt)
            c = self.data_loader.main_courses_list[i]
            if c.course_main_key not in selected_course_main_key and not self.should_filter_course_at_runtime(c):
                ret_course_array.append(c)
                ret_C_idx.append(i)
        return ret_course_array, self.generate_algorithm_data(ret_C_idx, R, CD, CT, CD_raw, CT_raw)

    def compute_relevance_score(self, interest_keywords):
        redis_key = self.get_interest_keywords_in_redis_saveable_format(
            interest_keywords)
        interest_keywords = [self.data_loader.preprocess_query(s) for s in interest_keywords]
        CD_raw = self.cosine_similarity_on_course_desc_idf_score(interest_keywords)
        CT_raw = self.cosine_similarity_on_course_title_idf_score(interest_keywords)
        CD = self.course_span_match_query(CD_raw, threshold=0.3)
        CT = self.course_span_match_query(CT_raw, threshold=0.5)
        # if len(interest_keywords) > 3:
        #     CD = self.course_span_match_query(CD_raw, threshold=0.3)
        #     CT = self.course_span_match_query(CT_raw, threshold=0.5)
        # else:
        #     CD = self.course_powerset_match_query(CD_raw)
        #     CT = self.course_powerset_match_query(CT_raw)
        alpha = 2/3
        R = alpha * CD + (1 - alpha) * CT
        self.save_redis_data(redis_key, R)
        return R, CD, CT, CD_raw, CT_raw        

    def get_relevance_score(self, interest_keywords, use_redis=False):
        if not use_redis:
            return self.compute_relevance_score(interest_keywords)
        redis_key = self.get_interest_keywords_in_redis_saveable_format(
            interest_keywords)
        redis_result = self.retrieve_redis_data(redis_key)
        if redis_result[0]:
            return redis_result[1]
        else:
            return self.compute_relevance_score(interest_keywords)[0]

    def compute_dept_abv_map_course_list(self, R, batch_num):
        calibr_R_cutline = self.calibration_relevance_score_cutline(
            batch_num)
        course_idx_dept_abv_pair_list = \
            self.course_idx_dept_abv_pair_list[(R > calibr_R_cutline * np.max(R)) &
                                               (self.data_loader.calibration_course_mask)]
        dept_abv_map_course_list = dict()
        for course_idx, dept_abv in course_idx_dept_abv_pair_list:
            c = self.data_loader.main_courses_list[course_idx]
            if dept_abv not in dept_abv_map_course_list:
                dept_abv_map_course_list[dept_abv] = [(c, course_idx)]
            else:
                dept_abv_map_course_list[dept_abv].append((c, course_idx))
        return dept_abv_map_course_list

    def calibration_step(self, interest_keywords, batch_num):
        if self.deterministic:
            np.random.seed(0)
        R_normalized, CD, CT, CD_raw, CT_raw = self.get_relevance_score(interest_keywords)
        dept_abv_map_course_courseidx_list = self.compute_dept_abv_map_course_list(R_normalized, batch_num)
        courses_batch, algorithm_data_dict = \
            self.select_batch(R_normalized, CD, CT, CD_raw, CT_raw, dept_abv_map_course_courseidx_list)
        return simple_jsonify_course_list(courses_batch), algorithm_data_dict


class ToyCalibrationEngineImpl(CalibrationEngine):
    def __init__(self, *args, **kws):
        super().__init__(None, None)
        self.courses_list = read_pickle_files(courses_pickle_addr)
    
    def calibration_step(self, *args, **kw):
        return simple_jsonify_course_list(np.random.choice(self.courses_list, size=8, replace=False)), dict()
