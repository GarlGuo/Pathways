from data_loader import GlobalData, read_pickle_files
from addr_info import *
from course_search.calibration_search_engine import CalibrationEngine
import numpy as np
from database.pathway_class import simple_jsonify_pathway_list
from numpy.lib.stride_tricks import as_strided
from deprecated import deprecated
import random


class PathwaySearchEngine:
    def __init__(self, data_loader, calibration_step_engine) -> None:
        self.data_loader = data_loader
        self.calibration_step_engine = calibration_step_engine

    def update_user_selection_courses(self, user_selection, R):
        if len(user_selection) > 0:
            # return a candidate list
            user_selection_idx = np.array([self.data_loader.main_course_map_idx[c_name] for c_name in user_selection])
            # pathways_contain_user_selection_idx = self.data_loader.PC_sparse[:, user_selection_idx].nonzero()[0]
            # set the relevance score of the selected courses as equal to the maximum value
            R[user_selection_idx] = np.max(R)
        return R

    def compute_P_score(self, R):
        # P_score = self.data_loader.PC_sparse * R_normalized.T        
        P_matrix = self.data_loader.PC_sparse.multiply(R)
        P_score = np.multiply(P_matrix.sum(axis=1), P_matrix.astype(np.uint8).sum(axis=1))
        P_score = as_strided(P_score, (P_score.shape[0],))
        return P_score
        # P_matrix = self.data_loader.PC_sparse * R
        # return P_matrix / self.data_loader.pathway_courses_count_array

    def _get_high_relevant_candidate(self, p_list, P_score, filter, lowest_number=5):
        P_slice_array = np.array(p_list, dtype=np.int32)
        P_score_slice = P_score[P_slice_array]
        ret = P_slice_array[filter(P_score, P_score_slice)]
        if len(ret) < lowest_number:
            return P_slice_array[np.argsort(-P_score_slice)][:min(lowest_number, len(P_slice_array))]
        else:
            return ret

    @staticmethod
    def local_relative_level_score_filter(P_score, P_score_slice, relative_level=0.75):
        return np.where(P_score_slice > relative_level * np.max(P_score_slice))

    @staticmethod
    def global_relative_level_score_filter(P_score, P_score_slice, relative_level=0.75):
        return np.where(P_score_slice > relative_level * np.max(P_score))

    def _get_pathway_candidate_and_relevance_score_default(self, P_score, R):
        return set(np.argsort(-P_score)[:20]), P_score, R

    def _get_pathway_candidate_and_relevance_score_major_mixed(self, P_score, R, user_majors):
        P_slice = set()
        for major in user_majors:
            if major in self.data_loader.majors_map_to_pathways:
                m_candidate_pathways = self.data_loader.majors_map_to_pathways[major]
                relevant_P_major_idx = self._get_high_relevant_candidate(m_candidate_pathways, P_score, PathwaySearchEngine.local_relative_level_score_filter, lowest_number=10)
                P_slice.update(relevant_P_major_idx)
                if len(relevant_P_major_idx) < 5 and major in self.data_loader.minors_map_to_pathways: # too few candidates in this major
                    filter_f = lambda _, P_score_slice: np.where(P_score_slice > 0.75 * np.max(P_score[m_candidate_pathways]))
                    relevant_P_minor_idx = self._get_high_relevant_candidate(self.data_loader.minors_map_to_pathways[major], P_score, filter_f)
                    P_slice.update(relevant_P_minor_idx)
            
        if len(P_slice) > 0:
            if len(P_slice) < 5: # too few candidates
                for p in np.argsort(-P_score):
                    if len(P_slice) == 5: break # maybe we shall adjust this number
                    if p not in P_slice: P_slice.add(p)

            return list(P_slice), P_score, R
        else:
            return self._get_pathway_candidate_and_relevance_score_default(P_score, R)


    def _get_pathway_candidate_and_relevance_score_major_partitioned(self, P_score, R, user_majors):
        major_P_map = dict()
        P_uniqueness_checker = set() # ensure uniqueness of pathway across different majors
        for major in user_majors:
            if major in self.data_loader.majors_map_to_pathways:
                m_candidate_pathways = self.data_loader.majors_map_to_pathways[major]
                # we can replace it with global score filter
                relevant_P_major_idx = self._get_high_relevant_candidate(m_candidate_pathways, P_score, PathwaySearchEngine.local_relative_level_score_filter)
                p_list = []
                for p in relevant_P_major_idx:
                    if p not in P_uniqueness_checker:
                        p_list.append(p)
                        P_uniqueness_checker.add(p)
                if len(p_list) < 5 and major in self.data_loader.minors_map_to_pathways: # too few candidates in this major
                    max_major_score = np.max(P_score[m_candidate_pathways])
                    minor_P_score_filter = lambda _, P_score_slice: np.where(P_score_slice > 0.75 * max_major_score)
                    relevant_P_minor_idx = self._get_high_relevant_candidate(self.data_loader.minors_map_to_pathways[major], P_score, minor_P_score_filter) 
                    for p in relevant_P_minor_idx:
                        if p not in P_uniqueness_checker:
                            p_list.append(p)
                            P_uniqueness_checker.add(p)
                if len(p_list) > 0:
                    major_P_map[major] = p_list

        if len(major_P_map) > 0:
            total_candidate_count = sum(len(p_list) for p_list in major_P_map.values())
            if total_candidate_count < 5:
                return self._get_pathway_candidate_and_relevance_score_major_mixed(self, P_score, R, user_majors)
            else:
                return major_P_map, P_score, R
        else:
            return self._get_pathway_candidate_and_relevance_score_default(P_score, R)


    def get_pathway_candidate_and_relevance_score(self, user_selection, user_majors,
                                                  interest_keywords, major_partitioned=True):
        R = self.calibration_step_engine.get_relevance_score(interest_keywords, use_redis=True)
        R = self.update_user_selection_courses(user_selection, R)
        P_score = self.compute_P_score(R)
        if major_partitioned:
            return self._get_pathway_candidate_and_relevance_score_major_partitioned(P_score, R, user_majors)
        else:
            return self._get_pathway_candidate_and_relevance_score_major_mixed(P_score, R, user_majors)


# class PathwaySearchEngineImpl(PathwaySearchEngine):
#     def __init__(self, data_loader: GlobalData, redis_handler,
#                  calibration_step_engine: CalibrationEngine, determinisitic=False) -> None:
#         super().__init__(data_loader, redis_handler, calibration_step_engine)
#         self.determinisitic = determinisitic

#     def get_nonmajor_pathways_count(self):
#         return np.random.choice([0, 1, 2], p=[2/3, 1/4, 1/12])

#     def generate_algorithm_analysis(self, 
#                                     ret_P_idx, P_scores, R_scores, 
#                                     PC50_slice, PC50_direction_idx_list,
#                                     pathway_candidate_idx_set,
#                                     pathways_contain_user_selection_idx):
#         ret_dict = {
#             "PC50 direction": PC50_direction_idx_list.tolist(),
#             "ret": [
#                 {
#                     "idx": x,
#                     "P scores": P_scores[x],
#                     "PC50 slice": PC50_slice[i].tolist() if i < PC50_slice.shape[0] else [],
#                 } for i, x in enumerate(ret_P_idx) # there are some nonuserselected major
#             ],
#             "candidates": {
#                 "same major": [
#                     {
#                         "idx": i,
#                         "P scores": P_scores[i],
#                     } for i in pathway_candidate_idx_set 
#                 ],
#                 "user-selection": [
#                     {
#                         "idx": i,
#                         "P scores": P_scores[i],
#                     } for i in pathways_contain_user_selection_idx 
#                 ]
#             }
#         }
#         for i, p in enumerate(ret_P_idx):
#             p = self.data_loader.PC_sparse[i, :]
#             p_score_slice = p.multiply(R_scores).tocsr()
#             p_score_nnz_idx = p_score_slice.nonzero()[1]
#             nnz_PC_dict = {
#                 self.data_loader.main_courses_list[x].course_name: p_score_slice[0, x] for x in p_score_nnz_idx
#             }
#             nonrelevant_courses = list({
#               self.data_loader.main_courses_list[x].course_name for x in p.nonzero()[1] if x not in set(p_score_nnz_idx)
#             })
#             ret_dict["ret"][i]["nonzero PC"] = dict(sorted(nnz_PC_dict.items(), key=(lambda kv: (-kv[1], kv[0]))))
#             ret_dict["ret"][i]["ret nonrelevant courses"] = sorted(nonrelevant_courses)
#         return ret_dict


#     def select_pathways_based_on_5PC_projection(self, pathway_candidate_idx_set,
#                                                 pathways_contain_user_selection_idx, P_scores, R_scores, 
#                                                 simple_json=False, simple_json_production=False):
#         PC50_direction_idx_list = np.random.permutation(50)[:5]
#         pathway_candidate_idx_set = list(pathway_candidate_idx_set)
#         PC50_slice = self.data_loader.PC50[np.ix_(pathway_candidate_idx_set, PC50_direction_idx_list)]
#         ret_P_idx = []
#         used_pathway_id_set = set()
#         nonmajor_cnt_needed = min(self.get_nonmajor_pathways_count(), len(pathways_contain_user_selection_idx))
        
#         # add pathways that are relevant and have longest projection on one PC direction
#         for i in np.arange(5-nonmajor_cnt_needed):
#             pathway_PC_one_direction_sorted_idx = np.argsort(np.abs(PC50_slice[:, i]))
#             for j in pathway_PC_one_direction_sorted_idx:
#                 p = self.data_loader.all_pathways_list[pathway_candidate_idx_set[j]]
#                 if p.pathway_id not in used_pathway_id_set:
#                     ret_P_idx.append(pathway_candidate_idx_set[j])
#                     used_pathway_id_set.add(p.pathway_id)
#                     break
        
#         # add nonmajor pathways that contain user's selection
#         nonmajor_cnt_real_added = 0
#         for i in pathways_contain_user_selection_idx:
#             if nonmajor_cnt_real_added == nonmajor_cnt_needed: 
#                 break
#             p = self.data_loader.all_pathways_list[i]
#             if p.pathway_id not in used_pathway_id_set:
#                 ret_P_idx.append(i)
#                 used_pathway_id_set.add(p.pathway_id)
#                 nonmajor_cnt_real_added += 1

#         # fill the gap by the most relevant pathways, no matter of the major
#         if len(ret_P_idx) < 5:
#             P_score_sorted_indices = np.argsort(P_scores)
#             i = 0
#             while len(ret_P_idx) < 5:
#                 p = self.data_loader.all_pathways_list[P_score_sorted_indices[i]]
#                 if p.pathway_id not in used_pathway_id_set:
#                     ret_P_idx.append(P_score_sorted_indices[i])
#                     used_pathway_id_set.add(p.pathway_id)
#                 i += 1

#         pathways_ret_array = [self.data_loader.all_pathways_list[i] for i in ret_P_idx]
#         if simple_json:
#             return simple_jsonify_pathway_list(pathways_ret_array, production=simple_json_production), \
#                 self.generate_algorithm_analysis(ret_P_idx, P_scores, R_scores, 
#                                                 PC50_slice, PC50_direction_idx_list, 
#                                                 pathway_candidate_idx_set,
#                                                 pathways_contain_user_selection_idx)
#         else:
#             return jsonify_pathway_list(pathways_ret_array), \
#                 self.generate_algorithm_analysis(ret_P_idx, P_scores, R_scores, 
#                                                 PC50_slice, PC50_direction_idx_list,
#                                                 pathway_candidate_idx_set,
#                                                 pathways_contain_user_selection_idx)

#     @deprecated(version='v1.2', reason="New pathway searching algorithm is available")
#     def pathway_search(self, user_selection, user_majors,
#                        interest_keywords, simple_json=False, simple_json_production=False):
#         if self.determinisitic:
#             np.random.seed(0)
#         pathway_candidate_idx_set, pathways_contain_user_selection_idx, P_scores, R_scores = \
#             self.get_pathway_candidate_and_relevance_score(
#                 user_selection, user_majors, interest_keywords
#             )
#         return self.select_pathways_based_on_5PC_projection(pathway_candidate_idx_set,
#                                                            pathways_contain_user_selection_idx, 
#                                                            P_scores, R_scores, 
#                                                            simple_json=simple_json, 
#                                                            simple_json_production=simple_json_production)


class ToyPathwaySearchEngine:
    def __init__(self, pathways_dictionary) -> None:
        self.pathways_list = list(pathways_dictionary.values())
    
    def pathway_search(self, *args, **kws):
        pathways = np.random.choice(self.pathways_list, size=5, replace=False)
        return simple_jsonify_pathway_list(pathways), dict()
