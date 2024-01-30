import requests
import json
from addr_info import roster_rawdata_json_addr


def get_courses(semester_slug, course_dict, subjectData):
    url = "https://classes.cornell.edu/api/2.0/search/classes.json"
    course_dict[semester_slug] = {}
    for subject in subjectData["data"]["subjects"]:
        print("Loading: " + subject["descr"] + " - " +
              subject["value"] + " ...." + semester_slug)

        params = {"roster": semester_slug, "subject": subject["value"]}
        response = requests.get(url, params=params)

        classData = response.json()

        course_dict[semester_slug][subject["value"]
                                   ] = classData["data"]["classes"]

latest_roster = ['SP23']
roster_lst = ['SP23'] + [season + str(yr) for yr in range(22, 14, -1)
                         for season in ('FA', 'SP')] + ['FA14']

# phase 2, load courses
courses = {}

for semester in roster_lst:
    url = "https://classes.cornell.edu/api/2.0/config/subjects.json?roster=" + semester
    params = {"roster": semester}
    response = requests.get(url, params=params)
    subjectData = response.json()
    get_courses(semester, courses, subjectData)

with open(roster_rawdata_json_addr, mode='w') as file:
    json.dump(courses, file)
