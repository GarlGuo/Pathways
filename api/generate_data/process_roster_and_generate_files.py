import requests
import json
import pandas as pd
import copy
import argparse
from database.pathway_class import Course, simple_jsonify_course_list
from addr_info import *
from data_loader import *
import sys
import re

LINE_BREAK_CHARACTERS = set(["\n", "\r", "\r\n"])
NOPRINT_TRANS_TABLE = {
    i: None for i in range(0, sys.maxunicode + 1)
    if not chr(i).isprintable() and not chr(i) in LINE_BREAK_CHARACTERS
}


def make_printable(s):
    """Replace non-printable characters in a string."""
    return s.translate(NOPRINT_TRANS_TABLE)


parser = argparse.ArgumentParser(
    description='process scraped roster.json and generate csv (--csv) & pickle (--pickle) roster files'
)

parser.add_argument('-c', '--csv', action='store_true', default=False,
                    help='need to generate csv file')
parser.add_argument('-p', '--pickle', action='store_true', default=False,
                    help='need to generate pickle file')
args = parser.parse_args()

# if not args.csv and not args.pickle:
#     exit(-1)


roster_lst = ['SP23'] + [season + str(yr) for yr in range(22, 14, -1)
                         for season in ('FA', 'SP')] + ['FA14']

abbr_dict = {}

crosslistings = set()
community_course_data = []

with open(roster_rawdata_json_addr, mode='r') as file:
    loaded_data = json.load(file)


def getCrosslistings(enrollGroups):
    curr_crosslistings = []
    for one_enrollment_data in enrollGroups:
        for section in one_enrollment_data["simpleCombinations"]:
            crosslisting_course_code = section["subject"] + \
                section["catalogNbr"]
            crosslistings.add(crosslisting_course_code)
            curr_crosslistings.append(crosslisting_course_code)
    return curr_crosslistings


def getProfs(enrollGroups):
    profs = []
    last_typ = ""

    for one_enrollment_data in enrollGroups:
        for section in one_enrollment_data["classSections"]:
            typ = section['ssrComponent']
            if last_typ == "" or last_typ == typ:
                for mtg in section["meetings"]:
                    for inst in mtg["instructors"]:
                        if (not inst["firstName"]):
                            continue
                        prof = inst["firstName"][0] + ". " + inst["lastName"]
                        if prof not in profs:
                            profs.append(prof)
                last_typ = typ
            else:
                break
    return ', '.join(profs)


def process_course_credits(unitMin, unitMax):
    return str(unitMin)
    # if unitMin == unitMax:
    #     return str(unitMin)
    # else:
    #     return "[" + str(unitMin) + " - " + str(unitMax) + "]"


def split_course_code(catalog_number):
    match_result = re.search(
        '(?P<dept>[a-zA-Z]+)(?P<num>[0-9]+)', catalog_number)
    return match_result.group('dept'), match_result.group('num')


def extract_courses(subjectData, latest_courses, semester_slug):
    for subject in subjectData["data"]["subjects"]:
        if subject["value"] not in abbr_dict:
            abbr_dict[subject["value"]] = subject["descr"]
        data = loaded_data[semester_slug][subject["value"]]

        for course in data:
            course_code = course["subject"] + course["catalogNbr"]
            if course_code in crosslistings:
                continue
            if course_code not in latest_courses.keys() or \
                    latest_courses[course_code]['course_grade_style'] == 'NA':
                if 'catalogAttribute' in course and course['catalogAttribute'] == '(CU-CEL)':
                    community_course = dict()
                    community_course['course_code'] = course_code 
                    community_course['course_title'] = course["titleLong"] 
                    community_course['course_desc'] = course['description']
                    community_course_data.append(community_course)
                if course["enrollGroups"] != []:
                    prof_list = [getProfs(course["enrollGroups"])]
                    crse_components = course["enrollGroups"][0]["componentsRequired"]
                    crse_credits = process_course_credits(
                        course["enrollGroups"][0]["unitsMinimum"],
                        course["enrollGroups"][0]["unitsMaximum"]
                    )
                    crse_grading_basis = course["enrollGroups"][0]['gradingBasis']
                    curr_crosslistings = getCrosslistings(
                        course["enrollGroups"])
                else:
                    prof_list = 'na'
                    crse_components = 'na'
                    crse_credits = 'na'
                    crse_grading_basis = 'na'
                    curr_crosslistings = []

                dept_name, number = split_course_code(course_code)

                one_course_data = {
                    'course_id': course['crseId'],
                    'dept': subject['descr'],
                    'instructors': prof_list,
                    'dept_abv': dept_name,
                    'course_main_key': course_code,
                    'course_name': course_code,
                    'course_title': course["titleLong"] or 'na',
                    'course_desc': course["description"] or 'na',
                    'course_credits': crse_credits or 'na',
                    'course_grade_style': crse_grading_basis,
                    'components': crse_components,
                    'year': "20" + semester_slug[2:],
                    'course_semesters': ['Spring' if semester_slug[:2] == 'SP' else 'Fall'],
                    'offerings': [semester_slug],
                    'alt_names': curr_crosslistings,
                    'roster_link': f'https://classes.cornell.edu/browse/roster/{semester_slug}/class/{dept_name}/{number}',
                    'roster_links': [f'https://classes.cornell.edu/browse/roster/{semester_slug}/class/{dept_name}/{number}'],
                }

                latest_courses[course_code] = one_course_data
                for other_course in curr_crosslistings:
                    new_course_data = copy.deepcopy(one_course_data)
                    new_course_data['course_name'] = other_course
                    new_dept_name, new_number = split_course_code(other_course)
                    new_course_data['roster_link'] = f'https://classes.cornell.edu/browse/roster/{semester_slug}/class/{new_dept_name}/{new_number}'
                    new_course_data['roster_links'] = [new_course_data['roster_link']],
                    latest_courses[other_course] = new_course_data
            else:
                # add professor lists
                if course["enrollGroups"] != []:
                    prof_list = [getProfs(course["enrollGroups"])]
                    latest_courses[course_code]['instructors'] += prof_list

                # add offer semester
                new_semester = 'Spring' if semester_slug[:2] == 'SP' else 'Fall'
                if new_semester not in latest_courses[course_code]['course_semesters']:
                    latest_courses[course_code]['course_semesters'].append(
                        new_semester)
                offering = semester_slug
                if new_semester not in latest_courses[course_code]['offerings']:
                    latest_courses[course_code]['offerings'].append(
                        offering)

                dept_name, number = split_course_code(course_code)
                latest_courses[course_code]['roster_links'].append(
                    f'https://classes.cornell.edu/browse/roster/{semester_slug}/class/{dept_name}/{number}')


def read_raw_roster_json_data_and_process():
    courses_data = {}

    for semester in roster_lst:
        subjects = []  # code, fullname, _
        url = "https://classes.cornell.edu/api/2.0/config/subjects.json?roster="+semester
        params = {"roster": semester}
        response = requests.get(url, params=params)
        subjectData = response.json()
        extract_courses(subjectData, courses_data, semester)

    roster_df = pd.DataFrame(courses_data.values(), dtype=str)
    roster_df.fillna('na')
    roster_df.replace(to_replace={
        'course_desc': {'': 'na'},
        'course_credits': {'': 'na'},
        'course_name': {'': 'na'},
        'course_title': {'': 'na'}
    }, inplace=True)
    return roster_df


def generate_pickle_files(roster_df):
    """
    generate pickle files for courses info and course descs info
    """
    print("start generating pickle files for roster data")
    all_courses = []
    all_main_courses = []
    dept_abv = set()
    for i, line in roster_df.iterrows():
        c = Course(line['dept'],
                   line['dept_abv'],
                   line['course_main_key'],
                   line['course_name'],
                   line['course_title'],
                   line['course_id'],
                   line['course_desc'],
                   'na',
                   line['course_credits'],
                   line['course_grade_style'],
                   line['course_semesters'],
                   line['instructors'],
                   line['offerings'],
                   line['roster_link'],
                   line['roster_links'])
        all_courses.append(c)
        dept_abv.add(line['dept_abv'])
        if line['course_main_key'] == line['course_name']:
            all_main_courses.append(c)
            
    dept_abv = list(dept_abv)
    main_course_dept_abv_idx_list = [dept_abv.index(c.dept_abv) for c in all_main_courses]
    np.save(course_dept_abv_idx_np_addr, np.array(main_course_dept_abv_idx_list))
    dump_pickle_files(all_courses, courses_pickle_addr)
    dump_pickle_files(all_main_courses, main_courses_pickle_addr)
    print("finish generating pickle files for roster data")
    return all_courses


def generate_csv_file(roster_df):
    print("start generating csv files for roster data")
    roster_csv_df = roster_df[[
        'course_id', 'dept', 'dept_abv', 'course_main_key', 'course_name',
        'course_title', 'course_desc', 'course_credits', 'course_grade_style',
        'instructors', 'offerings', 'components', 'year', 'course_semesters', 'alt_names', 'roster_links'
    ]]
    with open(roster_finaldata_csv_addr, mode='w', encoding='utf-8') as file:
        roster_csv_df.to_csv(file, lineterminator='\n', encoding='utf-8')

    with open(roster_testdata_csv_addr, mode='w', encoding='utf-8') as file:
        roster_csv_df[:300].to_csv(
            file, lineterminator='\n', encoding='utf-8')
    print("finish generating csv files for roster data")


def generate_sample_calibration_course_list_json(course_list):
    json_obj = simple_jsonify_course_list(course_list[:8])
    with open(sample_calibration_return_json_addr, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, indent=4)


# phase 1, load subjects
roster_df = read_raw_roster_json_data_and_process()
community_course_df = pd.DataFrame(community_course_data)
community_course_df.to_csv('community_course.csv',
                           encoding='utf-8', index=None)

# # phase 2, write to csv and pickle files
# if args.csv:
#     generate_csv_file(roster_df)

# if args.pickle:
#     course_list = generate_pickle_files(roster_df)
#     generate_sample_calibration_course_list_json(course_list)
