import os
import xml.etree.ElementTree as ET


dependencies_addr = f'..{os.sep}dependencies'


def get_addr(xml_root, parent_node_name, file_child):
    xml_parent = xml_root.find(parent_node_name)
    dir_addr = xml_parent.attrib['directory']
    if os.path.isdir(dependencies_addr + os.sep + dir_addr) is False:
        os.makedirs(dependencies_addr + os.sep + dir_addr)
    f = xml_parent.find(file_child).attrib['filename'].strip()
    return dependencies_addr + os.sep + dir_addr + os.sep + f


tree = ET.parse(f'{dependencies_addr}{os.sep}addr_info.xml')
xml_root = tree.getroot()


pathway_finaldata_csv_addr = get_addr(xml_root, 'pathway-data', 'processed-file')
pathway_career_outcome_csv_addr = get_addr(xml_root, 'pathway-data', 'career-outcome-file')
pathway_testdata_csv_addr = get_addr(xml_root, 'pathway-data', 'test-file')

roster_rawdata_json_addr = get_addr(xml_root, 'roster-data', 'rawdata-file')
roster_finaldata_csv_addr = get_addr(xml_root, 'roster-data', 'processed-file')
roster_testdata_csv_addr = get_addr(xml_root, 'roster-data', 'test-file')

anno_rawdata_csv_addr = get_addr(xml_root, 'anno-data', 'rawdata-file')
anno_testdata_csv_addr = get_addr(xml_root, 'anno-data', 'test-file')

major_minor_csv_addr = get_addr(xml_root, 'major-info', 'rawdata-csv-file')

department_abbv_pickle_addr = get_addr(
    xml_root, 'pickle-files', 'dept_abv')

courses_pickle_addr = get_addr(
    xml_root, 'pickle-files', 'courses')

pathways_dictionary_pickle_addr = get_addr(
    xml_root, 'pickle-files', 'pathways_dictionary')

sample_pathways_return_json_addr = get_addr(
    xml_root, 'json-files', 'sample_pathways')
sample_calibration_return_json_addr = get_addr(
    xml_root, 'json-files', 'sample_calibration')

majors_map_to_pathways_pickle_addr = get_addr(
    xml_root, "pickle-files", 'majors_map_to_pathways'
)
minors_map_to_pathways_pickle_addr = get_addr(
    xml_root, "pickle-files", 'minors_map_to_pathways'
)
course_desc_list_pickle_addr = get_addr(
    xml_root, "pickle-files", "course_desc_list"
)
course_title_list_np_addr = get_addr(
    xml_root, "matrix-files", "course_title_list"
)
course_desc_tfidf_vectorizer_pickle_addr = get_addr(
    xml_root, "pickle-files", "course_desc_tfidf_vectorizer"
)
course_desc_idf_scores_sparse_addr = get_addr(
    xml_root, "matrix-files", "course_desc_idf_scores_sparse"
)
course_title_tfidf_vectorizer_pickle_addr = get_addr(
    xml_root, "pickle-files", "course_title_tfidf_vectorizer"
)
course_title_idf_scores_sparse_addr = get_addr(
    xml_root, "matrix-files", "course_title_idf_scores_sparse"
)
course_dept_abv_idx_np_addr = get_addr(
    xml_root, "matrix-files", "course_dept_abv_idx"
)
all_pathways_list_pickle_addr = get_addr(
    xml_root, "pickle-files", "all_pathway_list"
)
main_courses_pickle_addr = get_addr(
    xml_root, "pickle-files", "main_courses"
)
PC_dense_addr = get_addr(
    xml_root, "matrix-files", "PC_dense"
)
PC_sparse_addr = get_addr(
    xml_root, "matrix-files", "PC_sparse"
)
calibration_course_mask_np_addr = get_addr(
    xml_root, "matrix-files", "course_mask"
)
PC50_addr = get_addr(
    xml_root, "matrix-files", "PC50"
)
PC50_PCA_model_addr = get_addr(
    xml_root, "pickle-files", "PCA_PC50_model"
)

pathways_log_addr = get_addr(
    xml_root, "log", "pathways_log"
)
preenroll_query_addr_cleaned_selected = get_addr(
    xml_root, "query-data", "preenroll-query-cleaned-selected-json"
)
preenroll_query_addr_cleaned = get_addr(
    xml_root, "query-data", "preenroll-query-cleaned-json"
)