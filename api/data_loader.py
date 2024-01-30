import pandas as pd
import numpy as np
import pickle
import nltk
from autocorrect import Speller
from addr_info import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text
import scipy.sparse
from sklearn.decomposition import PCA
import re
from tqdm import tqdm


def dump_pickle_files(data, pickle_addr):
    with open(pickle_addr, 'wb') as f:
        pickle.dump(data, f)


def read_pickle_files(pickle_addr):
    with open(pickle_addr, 'rb') as f:
        return pickle.load(f)


def remove_nonalphanumeric(str):
    regex = re.compile('[^0-9a-zA-Z]+')
    return regex.sub(' ', str)

###
# attributes in Picked_Data:
# all_courses: a list of Course objects
# all_pathways: a list of Pathway objects
# all_majors: a list of major string
# all_minors: a list of minor string
###


class GlobalData:

    def prepare_independent_data(self):
        self.speller = Speller(lang='en')
        self.my_stop_words = text.ENGLISH_STOP_WORDS.union(
            ["hi", "i'm", "college", "university", "want", "wish", "hello", "interested", "interest",
             "interests", "i", "learn", "more", "about", 'course', 'courses', 'anything', 'something',
             'lecture', 'discussion', 'class', 'instructor', 'professor', 'prof', 'teacher', 'like', 'know'])
        self.stemmer = nltk.stem.SnowballStemmer("english", ignore_stopwords=True)

    def find_last_uppercase_char_in_first_consecutive_appearance(self, s):
        for i, x in enumerate(s[:-1]):
            if s[i + 1].islower() and s[i].isupper():
                return s[i:]

    def __init__(self, course_data=False, course_desc_list=False, 
                 pathway_data=False, major_and_minor_data=False, 
                 course_title_list=False, PC=False, calibration_course_mask=False,
                 global_PCA_model=False, local_PCA_model=False):
        self.prepare_independent_data()
        if course_data:
            self.courses_list = read_pickle_files(courses_pickle_addr)
            self.main_courses_list = read_pickle_files(
                main_courses_pickle_addr)
            self.course_dept_abv_idx_list = np.load(
                course_dept_abv_idx_np_addr)
            self.courses_cnt = len(self.courses_list)
            self.main_course_cnt = len(self.main_courses_list)
            self.main_course_map_idx = {
                c.course_name: i for i, c in enumerate(self.main_courses_list)
            }
            self.course_dictionary = {
                c.course_name: c for c in self.courses_list
            }

        if course_desc_list:
            self.processed_course_desc_list = read_pickle_files(course_desc_list_pickle_addr)
            self.compute_course_desc_model()

        if course_title_list:
            self.processed_course_title_list = np.load(
                course_title_list_np_addr).tolist()
            self.compute_course_title_model()

        if pathway_data:
            self.pathways_dictionary = read_pickle_files(
                pathways_dictionary_pickle_addr)
            self.all_pathways_list = read_pickle_files(
                all_pathways_list_pickle_addr
            )
            self.pathway_courses_count_array = np.array([
                p.get_total_course_count() for p in self.all_pathways_list
            ])
            self.pathways_cnt = len(self.pathways_dictionary)

        if major_and_minor_data:
            major_and_minor_list = pd.read_csv(major_minor_csv_addr)
            major_df = major_and_minor_list[major_and_minor_list['ACADEMIC_PLAN_TYPE'] == 'MAJ']
            minor_df = major_and_minor_list[major_and_minor_list['ACADEMIC_PLAN_TYPE'] == 'MIN']
            self.all_majors = [self.find_last_uppercase_char_in_first_consecutive_appearance(str(x))
                               for x in major_df['ACADEMIC_PLAN_LDESCR'] if not pd.isna(x)]
            self.all_minors = [self.find_last_uppercase_char_in_first_consecutive_appearance(str(x))
                               for x in minor_df['ACADEMIC_PLAN_LDESCR'] if not pd.isna(x)]
            self.majors_map_to_pathways = read_pickle_files(
                majors_map_to_pathways_pickle_addr)
            self.minors_map_to_pathways = read_pickle_files(
                minors_map_to_pathways_pickle_addr)

        if PC:
            self.PC_dense = np.load(PC_dense_addr)
            self.PC_sparse = scipy.sparse.load_npz(PC_sparse_addr)

        if calibration_course_mask:
            self.calibration_course_mask = np.load(
                calibration_course_mask_np_addr)

        if global_PCA_model:
            self.PC50 = np.load(PC50_addr)

        if local_PCA_model:            
            self.PCA_major_lookup_list = {
                major: PCA(n_components=min(5, len(pathway_list))).fit_transform(self.PC_dense[np.array(pathway_list)]) for major, pathway_list in self.majors_map_to_pathways.items()
            }


    def new_tf_idf_vectorizer(self, **keywords):
        return TfidfVectorizer(stop_words=list(self.my_stop_words), **keywords)

    def preprocess_query(self, query):
        spell_checked = [self.speller(word)
                         for word in remove_nonalphanumeric(query).split()]
        return ' '.join(self.stemmer.stem(s) for s in spell_checked)

    def process_course_desc_list(self):
        print("start processing course desc list")
        unprocessed_list = [c.course_desc if c.course_desc != 'na' else ' ' for c in self.main_courses_list]
        course_desc_list = []
        for i in tqdm(range(len(unprocessed_list))):
            course_desc_list.append(self.preprocess_query(unprocessed_list[i]))
        dump_pickle_files(course_desc_list, course_desc_list_pickle_addr)
        self.processed_course_desc_list = course_desc_list
        print("finish processing course desc list")

    def compute_course_desc_model(self):
        self.course_desc_tfidf_vectorizer = self.new_tf_idf_vectorizer(ngram_range=(1, 2), max_df=0.1)
        self.course_desc_sparse_idf_scores = self.course_desc_tfidf_vectorizer.fit_transform(self.processed_course_desc_list)

    def compute_course_title_model(self):
        self.course_title_tfidf_vectorizer = self.new_tf_idf_vectorizer(ngram_range=(1, 2), max_df=0.3, binary=True)
        self.course_title_sparse_idf_scores = self.course_title_tfidf_vectorizer.fit_transform(self.processed_course_title_list)

    def process_course_title(self):
        print("start processing course title")
        unprocessed_list = [c.course_title if c.course_title != 'na' else ' ' for c in self.main_courses_list]
        processed_course_title_list = []
        for i in tqdm(range(len(unprocessed_list))):
            processed_course_title_list.append(self.preprocess_query(unprocessed_list[i]))
        np.save(course_title_list_np_addr, np.array(processed_course_title_list))
        print("finish processing course title")


    # def process_PC_dense(self):
    #     print("start processing PC-dense matrix")
    #     PC_dense = np.zeros((self.pathways_cnt, self.main_course_cnt))
    #     course_lookup = {c.course_name: i for i, c in enumerate(self.main_courses_list)}
    #     for i, p in enumerate(self.all_pathways_list):
    #         total_number_of_course_credits = sum(c.course_credits for c_list in p.academic_standing_maps_to_courses.values() for c in c_list)
    #         for c_list in p.academic_standing_maps_to_courses.values():
    #             for c in c_list:
    #                 if c.course_main_key in course_lookup:
    #                     PC_dense[i, course_lookup[c.course_main_key]] += c.course_credits / total_number_of_course_credits
    #     self.PC_dense = PC_dense
    #     np.save(PC_dense_addr, PC_dense)
    #     print("finish processing PC-dense matrix")

    def process_PC(self):
        print("start processing PC-dense matrix")
        PC_dense = np.zeros((self.pathways_cnt, self.main_course_cnt))
        course_lookup = {c.course_name: i for i, c in enumerate(self.main_courses_list)}
        for i, p in enumerate(self.all_pathways_list):
            total_course_count = p.get_total_course_count()
            for c_list in p.academic_standing_maps_to_courses.values():
                for c in c_list:
                    if c.course_main_key in course_lookup:
                        PC_dense[i, course_lookup[c.course_main_key]] += 1 / total_course_count
        self.PC_dense = PC_dense
        np.save(PC_dense_addr, PC_dense)
        print("finish processing PC-dense matrix")

        print("start processing PC_sparse matrix")
        self.PC_sparse = scipy.sparse.csr_matrix(PC_dense)
        scipy.sparse.save_npz(PC_sparse_addr, self.PC_sparse)
        print("finish processing PC_sparse matrix")

        print("start processing PC50 matrix")
        self.PC50 = PCA(50).fit_transform(PC_dense)
        np.save(PC50_addr, self.PC50)
        print("finish processing PC50 matrix")


    def check_course_eligible_in_calibration(self, c):
        if int(c.course_main_key[-4:]) >= 5000:
            return False
        else:
            return True

    def process_calibration_course_mask(self):
        print("start reprocessing course mask")
        mask = np.ones(self.main_course_cnt, dtype=np.uint8)
        for i, c in enumerate(self.main_courses_list):
            mask[i] = self.check_course_eligible_in_calibration(c)
        np.save(calibration_course_mask_np_addr, mask)
        self.calibration_course_mask = mask
        print("finish reprocessing course mask")
