import copy
from typing import *

from data_loader import GlobalData
from course_search.calibration_search_engine import CalibrationEngine
from pathway_search_engine import PathwaySearchEngine
import numpy as np
from database.pathway_class import simple_jsonify_pathway_list
from sklearn.decomposition import PCA
import math
from collections import Counter


TOTAL_DISTANCE = "total_distance"
CENTROID_DISTANCE = "centroid_distance"

GLOBAL_PLAIN = "global pathways embeddings + no partition"
GLOBAL_MAJOR_PARTITIONED = "global pathways embeddings + major partitioned selection"
LOCAL_MAJOR_PARTITIONED = "local pathways embeddings + major partitioned selection" # train multiple model and simply put together


class PathwaySearchEngineMaxIntragroup(PathwaySearchEngine):

    def __init__(self, data_loader: GlobalData, calibration_step_engine: CalibrationEngine, determinisitic=False, 
                 runs=3, max_iter=100, measure=CENTROID_DISTANCE) -> None:
        super().__init__(data_loader, calibration_step_engine)
        self.determinisitic = determinisitic
        self.runs = runs
        self.max_iter = max_iter
        self.measure_type = measure
        self.group_measure = {
            TOTAL_DISTANCE: self.compute_total_avg_distance,
            CENTROID_DISTANCE: self.compute_centroid_distance
        }[measure]
        self.prob_group_measure = {
            TOTAL_DISTANCE: self.compute_avg_diameter_prob,
            CENTROID_DISTANCE: self.compute_centroid_diameter_prob
        }[measure]

    def generate_algorithm_analysis_global_plain(self, ret_P_idx, P_scores, R_scores, pathway_candidate_idx_set, intragroup_d, global_candidate_d):
        P_ranking = np.argsort(-P_scores)
        pathway_candidate_idx_list = list(pathway_candidate_idx_set)
        candidate_P_ranking = np.argsort(-P_scores[pathway_candidate_idx_list])        
        ret_dict = {
            "global candidate intragroup d": global_candidate_d,
            "ret intragroup_d": intragroup_d,
            "ret": [
                {
                    "idx": int(x),
                    "P scores": P_scores[x].tolist(),
                } for x in ret_P_idx # there are some nonuser selected major
            ],
            "candidates": [
                {
                    "idx": int(i),
                    "P scores": P_scores[i],
                } for i in pathway_candidate_idx_set 
            ],
            "top global relevant pathways": [
                {
                    "idx": int(i),
                    "P scores": P_scores[i],
                } for i in P_ranking[:3] 
            ],
            "top relevant candidate pathways": [
                {
                    "idx": int(pathway_candidate_idx_list[i]),
                    "P scores": P_scores[pathway_candidate_idx_list[i]],
                } for i in candidate_P_ranking[:3] 
            ],
        }
        for i, p in enumerate(ret_P_idx):
            p = self.data_loader.PC_sparse[p, :]
            p_score_slice = p.multiply(R_scores).tocsr()
            p_score_nnz_idx = p_score_slice.nonzero()[1]
            nnz_PC_dict = {
                self.data_loader.main_courses_list[x].course_title.replace('.', '_'): p_score_slice[0, x] for x in p_score_nnz_idx
            }
            nonrelevant_courses = list({
              self.data_loader.main_courses_list[x].course_title.replace('.', '_') for x in p.nonzero()[1] if x not in set(p_score_nnz_idx)
            })
            ret_dict["ret"][i]["relevant courses"] = dict(sorted(nnz_PC_dict.items(), key=(lambda kv: (-kv[1], kv[0]))))
            ret_dict["ret"][i]["nonrelevant courses"] = sorted(nonrelevant_courses)
        return ret_dict

    def generate_algorithm_analysis_global_major_partitioned(self, ret_P_idx, P_scores, R_scores, major_pathway_idx_list_map, intragroup_d, global_candidate_d, major_candidate_d_map):
        P_ranking = np.argsort(-P_scores)
        ret_dict = {
            "global candidate intragroup d": global_candidate_d,
            "ret intragroup_d": intragroup_d,
            "candidates": [],
            "ret": [
                {
                    "idx": int(x),
                    "P scores": P_scores[x].tolist(),
                } for x in ret_P_idx # there are some nonuser selected major
            ],
            "top global relevant pathways": [
                {
                    "idx": int(i),
                    "P scores": P_scores[i],
                } for i in P_ranking[:3] 
            ]
        }

        for i, (m, p_list) in enumerate(major_pathway_idx_list_map.items()):
            major_data_dict = dict()
            major_data_dict["major-name"] = m
            major_data_dict["pathway-list"] = [
                {
                    "idx": int(p),
                    "P scores": P_scores[p]
                } for p in p_list
            ]
            major_data_dict["major candidate d"] = major_candidate_d_map[m]
            m_candidate_P_ranking = np.argsort(-P_scores[p_list])        
            major_data_dict["top relevant major candidate pathways"] = [
                {
                    "idx": int(p_list[i]),
                    "P scores": P_scores[p_list[i]],
                } for i in m_candidate_P_ranking[:min(3, len(m_candidate_P_ranking))] 
            ]
            ret_dict["candidates"].append(major_data_dict)

        for i, p in enumerate(ret_P_idx):
            p = self.data_loader.PC_sparse[p, :]
            p_score_slice = p.multiply(R_scores).tocsr()
            p_score_nnz_idx = p_score_slice.nonzero()[1]
            nnz_PC_dict = {
                self.data_loader.main_courses_list[x].course_title: p_score_slice[0, x] for x in p_score_nnz_idx
            }
            nonrelevant_courses = list({
              self.data_loader.main_courses_list[x].course_title for x in p.nonzero()[1] if x not in set(p_score_nnz_idx)
            })
            ret_dict["ret"][i]["relevant courses"] = dict(sorted(nnz_PC_dict.items(), key=(lambda kv: (-kv[1], kv[0]))))
            ret_dict["ret"][i]["nonrelevant courses"] = sorted(nonrelevant_courses)
        return ret_dict

    # 1 / [N * (N - 1)] * sum d(i, j)
    def compute_total_avg_distance(self, group, PC_reduced):
        N = len(group)
        vec = PC_reduced[group, :]
        d = np.sqrt(((vec[:,None,:] - vec) ** 2).sum(axis=2))
        row_result = np.sum(d, axis=0)
        return row_result, 1 / (N * (N - 1)) * np.sum(row_result)

    # 1 / N * sum d(i, avg_i)
    def compute_centroid_distance(self, group, PC_reduced_slice):
        N = len(group)
        group_PC50 = PC_reduced_slice[group, :]
        centroid = np.mean(group_PC50, axis=0)
        d = np.sqrt(np.sum((group_PC50 - centroid) ** 2, axis=1))
        return d, np.sum(d) / N

    def compute_avg_diameter_prob(self, candidate_list, group, PC_reduced):
        group_length = len(group)
        d = np.zeros((len(candidate_list), group_length))
        for i in range(group_length):
            d[:, i] =  np.sqrt(np.sum((PC_reduced[candidate_list, :] - PC_reduced[group[i], :]) ** 2, axis=1))
        d = np.sum(d, axis=1)
        return d / np.sum(d)

    def compute_centroid_diameter_prob(self, candidate_list, group, PC_reduced):
        centroid = np.mean(PC_reduced[group, :], axis=0)
        d = np.sqrt(np.sum((PC_reduced[candidate_list, :] - centroid) ** 2, axis=1))
        return d / np.sum(d)

    def _plain_initialization(self, PC_reduced, size=5):
        init_group = np.random.choice(np.arange(PC_reduced.shape[0]), size=size, replace=False)
        _, d = self.group_measure(init_group, PC_reduced)
        return d, init_group

    def _try_out_one_point(self, group, new_point, d, PC_slice):
        return_group = group[:]
        new_group = set(group) | {new_point}
        pop_point = None
        for old_point_i in group:
            new_group.remove(old_point_i)
            _, new_d = self.group_measure(list(new_group), PC_slice)
            if new_d > d:
                d = new_d
                return_group = list(copy.deepcopy(new_group))
                pop_point = old_point_i
            new_group.add(old_point_i)
        return d, return_group, pop_point

    def _computation_conservative_criteria(self, group):
        return len(group) > 100 and self.measure_type == PathwaySearchEngineMaxIntragroup.TOTAL_DISTANCE

    def _plain_one_run(self, PC_reduced, size=5):
        length = PC_reduced.shape[0]
        d, group = self._plain_initialization(PC_reduced, size=size)
        candidate_list = list(set(range(length)) - set(group.tolist()))
        counter = 0
        while True:
            candidate_prob = self.prob_group_measure(candidate_list, group, PC_reduced)
            p_permutation = np.random.choice(candidate_list, size=len(candidate_list), p=candidate_prob, replace=False)
            for p in p_permutation:
                if counter >= min(self.max_iter, 2 * len(candidate_list)): return d, group
                counter += 1 
                new_d, group, pop_point = self._try_out_one_point(group, p, d, PC_reduced)
                if new_d > d: 
                    d = new_d
                    candidate_list.remove(p)
                    candidate_list.append(pop_point)
                    break # the group has been updated. need to recompute the prob of all candidate list

    def maximize_intragroup_global_plain(self, pathway_candidate_idx_set, P_scores, R_scores, size=5):
        pathway_candidate_idx_list = np.array(list(pathway_candidate_idx_set))
        if len(pathway_candidate_idx_set) >= 50:
            PC_reduced_slice = PCA(10).fit_transform(self.data_loader.PC_dense[pathway_candidate_idx_list, :])
        else:
            PC_reduced_slice = self.data_loader.PC50[pathway_candidate_idx_list, :]
        
        if len(pathway_candidate_idx_list) > 5:
            d, group = 0, []
            for _ in range(self.runs):
                new_d, new_group = self._plain_one_run(PC_reduced_slice, size=size)
                if new_d > d:
                    group = new_group
                    d = new_d
        else:
            group = np.arange(5)
            _, d = self.group_measure(np.arange(5), PC_reduced_slice)

        _, candidate_d = self.group_measure(np.arange(len(pathway_candidate_idx_list)), PC_reduced_slice)
        ret_P_idx = [pathway_candidate_idx_list[i] for i in group]
        pathways_ret_array = [self.data_loader.all_pathways_list[i] for i in ret_P_idx]
        return simple_jsonify_pathway_list(pathways_ret_array), \
               self.generate_algorithm_analysis_global_plain(ret_P_idx, P_scores, R_scores, pathway_candidate_idx_list, d, candidate_d)


    # major_pathway_idx_list_map maps major_name to pathway_idx list
    def _major_partitioned_initialization(self, PC_reduced, major_pathway_idx_list_map):
        major_group_set_map = dict()
        init_group = []
        major_cnt = len(major_pathway_idx_list_map)
        per_major_reservation = int(math.floor(5 / major_cnt))
        remaining_choice_lookup = Counter(np.random.choice(np.arange(major_cnt), size=5-major_cnt*per_major_reservation, replace=False))
        
        for i, (major, major_idx_list) in enumerate(major_pathway_idx_list_map.items()):
            one_major_group = np.random.choice(major_idx_list, size=remaining_choice_lookup[i] + per_major_reservation, replace=False)
            major_group_set_map[major] = set(one_major_group)
            init_group.extend(one_major_group.tolist())
        _, d = self.group_measure(init_group, PC_reduced)
        return d, major_group_set_map, set(init_group)

    def _major_partitioned_try_out_one_point(self, major_points: Set[int], group_set: Set[int], new_point, d, PC_reduced):
        return_group = copy.deepcopy(group_set)
        new_group = group_set | {new_point}
        point_to_drop = None
        for old_point_i in major_points:
            new_group.remove(old_point_i)
            _, new_d = self.group_measure(list(new_group), PC_reduced)
            if new_d > d:
                d = new_d
                return_group = copy.deepcopy(new_group)
                point_to_drop = old_point_i
            new_group.add(old_point_i)
        return d, return_group, point_to_drop

    def _major_partitioned_one_run(self, PC_reduced, major_pathway_candidate_idx_list_map):
        d, major_group_set_map, group_set = self._major_partitioned_initialization(PC_reduced, major_pathway_candidate_idx_list_map)
        major_candidate_set = {
            major : list(set(idx_list) - major_group_set_map[major]) for major, idx_list in major_pathway_candidate_idx_list_map.items()
        }
        counter = 0
        total_candidate_count = sum(len(idx_list) for idx_list in major_pathway_candidate_idx_list_map.values())
        while True:
            for m, m_candidate_list in major_candidate_set.items():
                major_candidate_prob = self.prob_group_measure(m_candidate_list, list(group_set), PC_reduced)
                for p in np.random.choice(m_candidate_list, size=len(m_candidate_list), p=major_candidate_prob, replace=False):
                    if counter >= min(self.max_iter, 2 * total_candidate_count): 
                        return d, list(group_set)
                    counter += 1 
                    new_d, group_set, point_to_drop = self._major_partitioned_try_out_one_point(major_group_set_map[m], group_set, p, d, PC_reduced)
                    if new_d > d: 
                        d = new_d
                        m_candidate_list.append(point_to_drop)
                        m_candidate_list.remove(p)
                        major_group_set_map[m].remove(point_to_drop)
                        break # the group has been updated. need to recompute the prob of all candidate list

    def maximize_intragroup_major_partitioned(self, major_pathway_idx_list_map, P_scores, R_scores):
        major_candidate_idx_list_map = {m : [] for m in major_pathway_idx_list_map.keys()}
        candidate_pathway_lookup_list = []
        counter = 0
        for m, p_list in major_pathway_idx_list_map.items():
            for p in p_list:
                candidate_pathway_lookup_list.append(p) 
                major_candidate_idx_list_map[m].append(counter)
                counter += 1
            
        if len(candidate_pathway_lookup_list) >= 50:
            PC_reduced_slice = PCA(10).fit_transform(self.data_loader.PC_dense[candidate_pathway_lookup_list, :])
        else:
            PC_reduced_slice = self.data_loader.PC50[candidate_pathway_lookup_list, :] 
        
        if counter > 5:
            d, group = -np.inf, []
            for _ in range(self.runs):
                new_d, new_group = self._major_partitioned_one_run(PC_reduced_slice, major_candidate_idx_list_map)
                if new_d >= d:
                    group = new_group
                    d = new_d
        else:
            group = np.arange(5)
            _, d = self.group_measure(np.arange(counter), PC_reduced_slice)

        _, global_candidate_d = self.group_measure(np.arange(counter), PC_reduced_slice)
        ret_P_idx = [candidate_pathway_lookup_list[i] for i in group]
        pathways_ret_array = [self.data_loader.all_pathways_list[candidate_pathway_lookup_list[i]] for i in group]
        
        # algorithm analysis
        major_candidate_d_map = dict()
        for m, p_list in major_candidate_idx_list_map.items():
            _, m_candidate_d = self.group_measure(p_list, PC_reduced_slice)
            major_candidate_d_map[m] = m_candidate_d
        
        return simple_jsonify_pathway_list(pathways_ret_array), \
                self.generate_algorithm_analysis_global_major_partitioned(ret_P_idx, P_scores, R_scores, major_pathway_idx_list_map, d, global_candidate_d, major_candidate_d_map)


    def global_plain_maximization(self, user_selection, user_majors, interest_keywords):
        pathway_candidate_idx_set, P_scores, R_scores = self.get_pathway_candidate_and_relevance_score(user_selection, user_majors, interest_keywords, major_partitioned=False)
        return self.maximize_intragroup_global_plain(pathway_candidate_idx_set, P_scores, R_scores, size=5)

    def major_partitioned_maximization(self, user_selection, user_majors, interest_keywords):
        major_pathway_idx_list_map, P_scores, R_scores = self.get_pathway_candidate_and_relevance_score(user_selection, user_majors, interest_keywords, major_partitioned=True)
        if not isinstance(major_pathway_idx_list_map, dict):
            pathway_candidate_idx_set = major_pathway_idx_list_map
            return self.maximize_intragroup_global_plain(pathway_candidate_idx_set, P_scores, R_scores, size=5)
        else:
            return self.maximize_intragroup_major_partitioned(major_pathway_idx_list_map, P_scores, R_scores)

    def pathway_search(self, user_selection, user_majors, interest_keywords, predetermined_algo_type=None):
        if self.determinisitic:
            np.random.seed(0)
        
        if predetermined_algo_type is None: # production version
            if 5 > len(user_majors) > 1:
                return self.major_partitioned_maximization(user_selection, user_majors, interest_keywords)
            else:
                return self.global_plain_maximization(user_selection, user_majors, interest_keywords)
        
        elif predetermined_algo_type == GLOBAL_PLAIN:
            return self.major_partitioned_maximization(user_selection, user_majors, interest_keywords)

        elif predetermined_algo_type == GLOBAL_MAJOR_PARTITIONED:
            return self.major_partitioned_maximization(user_selection, user_majors, interest_keywords)
        
        elif predetermined_algo_type == LOCAL_MAJOR_PARTITIONED:
            pass
