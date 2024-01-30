import pandas as pd
import argparse
from collections import OrderedDict
from addr_info import *
from data_loader import *
from database.pathway_class import Course, Pathway
from tqdm import tqdm


parser = argparse.ArgumentParser(
    description='process pathway data and generate csv & pickle pathway files'
)

parser.add_argument('-c', '--csv', action='store_true', default=False,
                    help='need to generate csv file')
parser.add_argument('-p', '--pickle', action='store_true', default=False,
                    help='need to generate pickle file')
args = parser.parse_args()

# if not args.csv and not args.c and not args.pickle and not not args.p:
#     exit(-1)

anno_df = pd.read_csv(anno_rawdata_csv_addr)
anno_df_len = len(anno_df)

roster_pickle = read_pickle_files(courses_pickle_addr)
roster_df_len = len(roster_pickle)

major_minor_df = pd.read_csv(major_minor_csv_addr)


datalist = dict()
pathway_id_to_datalist_lookup = dict()
line_lookup = dict()
excluded_netids = set()
course_lookup = dict()
major_lookup = dict()
minor_lookup = dict()


# { pathway_id: (major_list, academic_standing) }
pathway_major_mapping = dict()
# { pathway_id: (minor_list, academic_standing) }
pathway_minor_mapping = dict()


def process_roster_final():
    print("start reading roster (1nd step of processing)")
    for c in roster_pickle:
        course_lookup[c.course_name] = c
    print("finish reading roster (1nd step of processing)")


def find_last_uppercase_char_in_first_consecutive_appearance(s):
    for i, x in enumerate(s[:-1]):
        if s[i + 1].islower() and s[i].isupper():
            return s[i:]

def process_major_info():
    print("start reading major and minor info (2nd step of processing)")
    for i, line in major_minor_df.iterrows():
        # Ex. Split "-" between "BIOCHBIOCH-PHD"
        if line['ACADEMIC_PLAN_TYPE'] == 'MAJ' and not pd.isna(line['ACADEMIC_PLAN_LDESCR']):
            major_lookup[line['ACADEMIC_PLAN']] = find_last_uppercase_char_in_first_consecutive_appearance(line['ACADEMIC_PLAN_LDESCR'])
        if line['ACADEMIC_PLAN_TYPE'] == 'MIN' and not pd.isna(line['ACADEMIC_PLAN_LDESCR']):
            minor_lookup[line['ACADEMIC_PLAN']] = find_last_uppercase_char_in_first_consecutive_appearance(line['ACADEMIC_PLAN_LDESCR'])
    print("finish reading major and minor info (2nd step of processing)")


def remove_all_records_with_this_netid(netid):
    excluded_netids.add(netid)
    if netid in line_lookup:
        for j in line_lookup[netid]:
            datalist.pop(j)
        line_lookup.pop(netid)
    if netid in pathway_id_to_datalist_lookup:
        pathway_id_to_datalist_lookup.pop(netid)


def add_to_line_lookup(netid, i):
    if netid not in line_lookup:
        line_lookup[netid] = list()
    line_lookup[netid].append(i)


def get_grade_term_info(enrollment_semester):
    arr = enrollment_semester.split(',')
    return arr[0], arr[1][1:]


def get_academic_standing(term_begin_acad_level_ldescr):
    mappings = {
        "UG Freshman, First Term": 1,
        "UG Freshman, Second Term": 2,
        "UG Sophomore, First Term": 3,
        "UG Sophomore, Second Term": 4,
        "UG Junior, First Term": 5,
        "UG Junior, Second Term": 6,
        "UG Senior, First Term": 7,
        "UG Senior, Second Term": 8,
        "UG Senior+, First Term Beyond": 9,
        "UG Senior+, Second Term Beyond": 10
    }
    return mappings[term_begin_acad_level_ldescr]


# return "line" if this pathway should be filtered out
# return "all" if all pathways that contains this netid should be filtered out
# return None if this pathway should be kept
def filter_netid(line):

    # Remove non-undergraduate students exchange, and transfer students
    # Retain netid if ADMIT_TYPR_LDESCR == "UG Freshman"
    if line['ADMIT_TYPE_LDESCR'] != 'UG Freshman':
        return 'all'

    # Remove non-graduated students
    # Remove netid if GRADUATE_TERM is na (done)
    if pd.isna(line['GRADUATE_TERM']) or line['GRADUATE_TERM'] == "":
        return 'all'

    # Remove students admitted before 2014
    # Remove netid if any ACADEMIC_TERM_SDESCR < 2014
    # if int(line['ACADEMIC_TERM_SDESCR'][:4]) < 2014:
    #     return 'all'

    # Remove classes taken in winter and summer
    # Remove a single record if ACADEMIC_TERM_SDESCR is not FA or SP
    if line["ACADEMIC_TERM_SDESCR"][-2:] not in {'FA', 'SP'}:
        return "line"

    # Remove class without academic level description
    if pd.isna(line['TERM_BEGIN_ACAD_LEVEL_LDESCR']) or line['TERM_BEGIN_ACAD_LEVEL_LDESCR'] == "":
        return "line"

    # Remove class without major
    # if pd.isna(line['ACADEMIC_PLAN_MAJOR']):
    #     return "line"

# get major and minor list of one row of pathway record, and update the global major, minor mapping


def retrieve_major_minor_info_and_update_mapping_list(one_pathway_data, academic_standing, netid):
    abbreviated_majors = one_pathway_data['ACADEMIC_PLAN_MAJOR'].split(',') if not pd.isna(one_pathway_data['ACADEMIC_PLAN_MAJOR']) else []
    abbreviated_minors = one_pathway_data['ACADEMIC_PLAN_MINOR'].split(',') if not pd.isna(one_pathway_data['ACADEMIC_PLAN_MINOR']) else []
    majors = []
    minors = []

    for major in abbreviated_majors:
        if major in major_lookup:
            majors.append(major_lookup[major])

    for minor in abbreviated_minors:
        if minor in minor_lookup:
            minors.append(minor_lookup[minor])

    if len(majors) > 0:
        if netid in pathway_major_mapping:
            _, term = pathway_major_mapping[netid]
            if academic_standing > term:
                pathway_major_mapping[netid] = majors, academic_standing
        else:
            pathway_major_mapping[netid] = majors, academic_standing

    if len(minors) > 0:
        if netid in pathway_minor_mapping:
            _, term = pathway_minor_mapping[netid]
            if academic_standing > term:
                pathway_minor_mapping[netid] = minors, academic_standing
        else:
            pathway_minor_mapping[netid] = minors, academic_standing


def process_anno_and_left_join_with_roster_data_step_1():
    print("start processing & joining anno with roster data (3nd step of processing)")
    counter = tqdm(range(len(anno_df)))
    for i, pathway in anno_df.iterrows():
        counter.update(1)

        netid = pathway['anon-netid']
        if netid in excluded_netids:
            continue

        filter_result = filter_netid(pathway)

        if filter_result == "line":
            continue

        if filter_result == "all":
            remove_all_records_with_this_netid(netid)
            continue

        one_line_data = None
        academic_standing = get_academic_standing(
            pathway['TERM_BEGIN_ACAD_LEVEL_LDESCR'])
        retrieve_major_minor_info_and_update_mapping_list(
            pathway, academic_standing, netid)

        course_nbr = pathway['SUBJECT'] + str(pathway['CATALOG_NBR'])
        if course_nbr in course_lookup:
            course_info_in_roster = course_lookup[course_nbr]
            one_line_data = {
                'dept': course_info_in_roster.dept,
                'dept_abv': course_info_in_roster.dept_abv,
                'course_name': course_nbr,
                'course_main_key': course_info_in_roster.course_main_key,
                'course_title':  course_info_in_roster.course_title,
                'course_id': course_info_in_roster.course_id,
                'course_desc': course_info_in_roster.course_desc,
                'semester': pathway['ACADEMIC_TERM_SDESCR'],
                'course_semester': course_info_in_roster.course_semesters,
                'course_credits': pathway['UNT_TAKEN'] if pathway['UNT_TAKEN'] != 'na' else 0,
                'course_grade_style': course_info_in_roster.course_grade_style,
                'instructors': course_info_in_roster.instructors,
                'offerings': course_info_in_roster.offerings,
                'roster_link': course_info_in_roster.roster_link,
                'roster_links':  course_info_in_roster.roster_links,
                'pathway_id': netid,
                'academic_standing': academic_standing
            }
        else:
            one_line_data = {
                'dept': 'na',
                'dept_abv': pathway['SUBJECT'],
                'course_name': course_nbr,
                'course_main_key': course_nbr,
                'course_title':  'na',
                'course_id': 'na',
                'course_desc': 'na',
                'semester': pathway['ACADEMIC_TERM_SDESCR'],
                'course_semester': 'na',
                'course_credits': pathway['UNT_TAKEN'] if pathway['UNT_TAKEN'] != 'na' else 0,
                'course_grade_style': 'na',
                'instructors': 'na',
                'offerings': 'na',
                # course not present in roster, so synthesizing a roster link is useless
                'roster_link': '',
                'roster_links':  '',
                'pathway_id': netid,
                'academic_standing': academic_standing
            }

        add_to_line_lookup(netid, i)
        datalist[i] = one_line_data

        if netid not in pathway_id_to_datalist_lookup:
            pathway_id_to_datalist_lookup[netid] = [one_line_data]
        else:
            pathway_id_to_datalist_lookup[netid].append(one_line_data)

    print("finish processing & joining all anno with roster data (3nd step of processing)")


def process_anno_and_left_join_with_roster_data_step_2():
    print("start filtering pathway data (4nd step of processing)")
    netid_toremove_list = []
    for pathway_id, idx_list in line_lookup.items():
        na_course_desc = sum(datalist[i]['course_desc'] == 'na' for i in idx_list)
        na_course_desc_credits = sum(float(datalist[i]['course_credits']) for i in idx_list if datalist[i]['course_desc'] == 'na')

        semesters = {datalist[i]['academic_standing'] for i in idx_list}
        total_credits = sum(float(datalist[i]['course_credits']) for i in idx_list)

        per_semester_course_dict = dict()
        for i in idx_list:
            semester = datalist[i]['academic_standing']
            if semester in per_semester_course_dict:
                per_semester_course_dict[semester][0] += 1
                per_semester_course_dict[semester][1] += float(datalist[i]['course_credits'])
            else:
                per_semester_course_dict[semester] = [1, float(datalist[i]['course_credits'])]

        max_per_semester_course_count = max(float(c_pair[0]) for c_pair in per_semester_course_dict.values())
        max_per_semester_course_credit = max(float(c_pair[1]) for c_pair in per_semester_course_dict.values())

        min_per_semester_course_count = min(float(c_pair[0]) for c_pair in per_semester_course_dict.values())
        min_per_semester_course_credit = min(float(c_pair[1]) for c_pair in per_semester_course_dict.values())

        major_list = pathway_major_mapping.get(pathway_id) or []
        minor_list = pathway_minor_mapping.get(pathway_id) or []
        if na_course_desc > .2 * len(idx_list) or na_course_desc_credits > .2 * total_credits:
            netid_toremove_list.append(pathway_id)
        elif total_credits < 100 or total_credits > 160:
            netid_toremove_list.append(pathway_id)
        elif len(semesters) < 7 or len(semesters) > 10:
            netid_toremove_list.append(pathway_id)
        elif max_per_semester_course_count > 9 or max_per_semester_course_credit > 26:
            netid_toremove_list.append(pathway_id)
        elif min_per_semester_course_count < 4 or min_per_semester_course_credit < 12:
            netid_toremove_list.append(pathway_id)

        if len(major_list) > 0:
            major_list = major_list[0]
        if len(minor_list) > 0:
            minor_list = minor_list[0]
        for i in idx_list:
            datalist[i]['majors'] = major_list
            datalist[i]['minors'] = minor_list
        
        if len(major_list) >= 3 or len(minor_list) >= 3:
            netid_toremove_list.append(pathway_id)
        
    for id in netid_toremove_list:
        remove_all_records_with_this_netid(id)
    print("finish filtering pathway data (4nd step of processing)")


def count_statistics():
    total_netid_count = (len(line_lookup) + len(excluded_netids))
    print(f"Total pathway records in raw anno file: {anno_df_len}")
    print(f"Total netids in raw anno file: {total_netid_count}")
    print(f"Filtered netids {len(excluded_netids)} ({len(excluded_netids) / total_netid_count * 100:.3f}%)")
    print(f"Remaining pathway records {len(datalist)} ({len(datalist) / anno_df_len * 100:.3f}%)")
    print(f"Remaining netids {len(pathway_id_to_datalist_lookup)} ({len(pathway_id_to_datalist_lookup) / total_netid_count * 100:.3f}%)")
    print()

def add_career_outcome():
    print('start adding career outcome to pathway df')

    # open csv at pathway_career_outcome_csv_addr
    # read the csv into a dataframe
    # make a dictionary mapping pathway_id (anon-netid) to their career_outcome
    id_career_dict = dict()
    with open(pathway_career_outcome_csv_addr, mode='r', encoding='utf-8') as file:
        career_outcome_csv = pd.read_csv(file, encoding='utf-8')
        for i in range(len(career_outcome_csv)):
            id_career_dict[career_outcome_csv.iloc[i]['anon-netid']] = {
                'primary_sit': career_outcome_csv.iloc[i]['primary_sit'],
                'emp_sit': career_outcome_csv.iloc[i]['emp_sit'],
                'employment_sector': career_outcome_csv.iloc[i]['emp_sector'],
                'employment_field': career_outcome_csv.iloc[i]['emp_field'],
                'grad_field': career_outcome_csv.iloc[i]['grad_field'],
                'grad_degree': career_outcome_csv.iloc[i]['grad_degree'],
            }
            # replace na values with empty string, otherwise it will be nan
            # and frontend will not be able to parse it
            for key in id_career_dict[career_outcome_csv.iloc[i]['anon-netid']]:
                if pd.isna(id_career_dict[career_outcome_csv.iloc[i]['anon-netid']][key]):
                    id_career_dict[career_outcome_csv.iloc[i]['anon-netid']][key] = ''

    # TODO: update this so it matches na values in the csv
    NONEXIST_ID_OUTCOME = {
        'primary_sit': '',
        'emp_sit': '',
        'employment_sector': '',
        'employment_field': '',
        'grad_field': '',
        'grad_degree': '',
    }

    # import pdb; pdb.set_trace()
    # not all pathway_id's are in the career_outcome_csv
    for i in datalist:
        if datalist[i]['pathway_id'] in id_career_dict:
            datalist[i]['career_outcome'] = id_career_dict[datalist[i]['pathway_id']]
        else:
            datalist[i]['career_outcome'] = NONEXIST_ID_OUTCOME

    print("finish adding career outcome to pathway data")

def process_pathway_and_get_dataframe():
    process_roster_final()
    process_major_info()
    process_anno_and_left_join_with_roster_data_step_1()
    process_anno_and_left_join_with_roster_data_step_2()
    add_career_outcome()
    count_statistics()
    pathway_df = pd.DataFrame(list(datalist.values()))
    return pathway_df


def generate_csv(pathway_df):
    print("start generating csv for pathway data")

    pathway_csv_df = pathway_df[[
        'majors',
        'minors',
        'dept',
        'dept_abv',
        'course_main_key',
        'course_name',
        'course_title',
        'course_id',
        'course_desc',
        'semester',
        'course_credits',
        'course_grade_style',
        'pathway_id',
        'academic_standing',
        'career_outcome',
    ]]

    with open(pathway_finaldata_csv_addr, mode='w', encoding='utf-8') as file:
        pathway_csv_df.to_csv(file, lineterminator='\n', encoding='utf-8')

    pathway_csv_test_df = pathway_csv_df[:200]
    with open(pathway_testdata_csv_addr, mode='w', encoding='utf-8') as file:
        pathway_csv_test_df.to_csv(file, lineterminator='\n', encoding='utf-8')

    print("finish generating csv for pathway data")


def generate_pickle(pathway_id_to_datalist_lookup):
    """
    generate pickle files for courses info and course descs info
    """
    print("start generating pickle files for pathway data")
    pathways_dictionary = dict()
    all_pathway_list = []
    for pathway_id, datalist_of_this_netid in pathway_id_to_datalist_lookup.items():
        academic_standing_maps_to_courses = dict()
        course_main_keys_map_units = dict()
        for data in datalist_of_this_netid:
            course = Course(data['dept'], data['dept_abv'], data['course_main_key'],
                            data['course_name'], data['course_title'], data['course_id'], data['course_desc'],
                            data['semester'], data['course_credits'], data['course_grade_style'], data['course_semester'],
                            data['instructors'], data['offerings'], data['roster_link'], data['roster_links'])
            course_main_key = course.get_course_main_key()
            course_main_keys_map_units[course_main_key] = data['course_credits'] + \
                (course_main_keys_map_units.get(course_main_key) or 0)
            current_course_academic_standing = data['academic_standing']
            if current_course_academic_standing not in academic_standing_maps_to_courses:
                academic_standing_maps_to_courses[current_course_academic_standing] = []
            academic_standing_maps_to_courses[current_course_academic_standing].append(course)

        # TODO: add career outcome, change Pathway class
        current_pathway_instance = Pathway(
            pathway_id, course_main_keys_map_units, academic_standing_maps_to_courses,
            data['majors'], data['minors'], data['career_outcome']
        )
        pathways_dictionary[pathway_id] = current_pathway_instance
        all_pathway_list.append(current_pathway_instance)
    dump_pickle_files(pathways_dictionary, pathways_dictionary_pickle_addr)
    dump_pickle_files(all_pathway_list, all_pathways_list_pickle_addr)
    print("finish generating pickle files for pathway data")
    return list(pathways_dictionary.values())


def generate_major_mapping_and_minor_mapping(pathways_list):
    majors_map_to_pathways, minors_map_to_pathways = dict(), dict()
    for i, p in enumerate(pathways_list):
        for major in p.majors:
            if major not in majors_map_to_pathways:
                majors_map_to_pathways[major] = []
            majors_map_to_pathways[major].append(i)
        for minor in p.minors:
            if minor not in minors_map_to_pathways:
                minors_map_to_pathways[minor] = []
            minors_map_to_pathways[minor].append(i)

    dump_pickle_files(minors_map_to_pathways, minors_map_to_pathways_pickle_addr)
    dump_pickle_files(majors_map_to_pathways, majors_map_to_pathways_pickle_addr)


pathway_df = process_pathway_and_get_dataframe()

print("All data processing is done. Start generating new data files from processed data")
if args.csv or args.c:
    generate_csv(pathway_df)

if args.pickle or args.p:
    pathway_list = generate_pickle(pathway_id_to_datalist_lookup)
    generate_major_mapping_and_minor_mapping(pathway_list)
