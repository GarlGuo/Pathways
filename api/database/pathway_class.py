import json
from typing import List


class Course:
    def __init__(self, dept, dept_abv, course_main_key,
                 course_name, course_title, course_id,
                 course_desc,
                 semester_taken, course_credits, course_grade_style,
                 course_semesters, instructors, offerings, roster_link, roster_links):
        self.dept = dept
        self.dept_abv = dept_abv
        self.course_main_key = course_main_key
        self.course_name = course_name
        self.course_title = course_title
        self.course_id = course_id
        self.course_desc = course_desc
        self.semester_taken = semester_taken
        self.course_credits = course_credits
        self.course_grade_style = course_grade_style
        self.course_semesters = course_semesters
        self.instructors = instructors
        self.offerings = offerings
        self.roster_link = roster_link,
        self.roster_links = roster_links

    def get_dept(self):
        return self.dept

    def get_dept_abv(self):
        return self.dept_abv

    def get_course_main_key(self):
        return self.course_main_key

    def get_course_name(self):
        return self.course_name

    def get_course_title(self):
        return self.course_title

    def get_course_id(self):
        return self.course_id

    def get_course_desc(self):
        return self.course_desc

    def get_course_semesters(self):
        return self.course_semesters

    def get_course_credits(self):
        return self.course_credits

    def get_course_grade_style(self):
        return self.course_grade_style

    def get_semester_taken(self):
        return self.semester_taken

    def get_instructors(self):
        return self.instructors

    def get_roster_link(self):
        return self.roster_link

    def get_roster_links(self):
        return self.roster_links

    def get_offerings(self):
        return self.offerings

    def __str__(self):
        return self.course_name

    def simple_jsonify(self):
        return dict(course_name=self.course_name,
                    course_title=self.course_title,
                    roster_link=self.roster_link)


class Pathway:
    # pathway_id is a string that takes the anonymous student id
    # classes is a list of course objects (chrono ordered)
    # class_descriptions is a string of an aggregate of the courses descs
    # career outcome is a dictionary of the career outcome
    def __init__(self, pathway_id, course_main_keys, academic_standing_maps_to_courses, majors, minors, career_outcome):
        self.pathway_id = pathway_id
        self.course_main_keys = course_main_keys
        # {1: [course1, course2], 2: [], 3: [],...}
        self.academic_standing_maps_to_courses = academic_standing_maps_to_courses
        self.majors = majors
        self.minors = minors
        self.career_outcome = career_outcome

    def get_id(self):
        return self.pathway_id

    def get_courses(self):
        return self.course_main_keys

    def get_total_course_count(self):
        return sum(len(c_list) for c_list in self.academic_standing_maps_to_courses.values())

    def get_course_names(self):
        return self.course_main_keys

    def get_course_descs(self):
        return self.course_descs

    def get_majors(self):
        return self.majors

    def get_minors(self):
        return self.minors
    
    def get_career_outcome(self):
        return self.career_outcome

    def get_academic_standing_maps_to_courses(self):
        return self.academic_standing_maps_to_courses

    def set_id(self, pathway_id):
        self.pathway_id = pathway_id

    def set_courses(self, courses):
        self.course_main_keys = courses

    def add_course(self, course):
        self.course_main_keys.append(course)
        self.course_main_keys.append(course.course_name)
        self.course_descs += " " + str(course.course_desc)

    def set_course_descriptions(self, course_descs):
        self.course_descs = course_descs

    def __str__(self):
        return self.pathway_id + " " + str(self.course_main_keys)

    def simple_jsonify(self):
        # import pdb; pdb.set_trace()
        return dict(pathway_id=self.pathway_id,
                    minors=self.minors,
                    majors=self.majors,
                    courses={academic_standing: [c.simple_jsonify() for c in course] 
                            for academic_standing, course in sorted(self.academic_standing_maps_to_courses.items())},
                    career_outcome=self.career_outcome)

def simple_jsonify_course_list(course_list: List[Course]):
    return dict(count=len(course_list), courses=[c.simple_jsonify() for c in course_list])

def simple_jsonify_pathway_list(pathway_list: List[Pathway]):
    return dict(count=len(pathway_list), pathways=[p.simple_jsonify() for p in pathway_list])

def complex_encoder(obj):
    if hasattr(obj, "jsonify"):
        return obj.jsonify()
    else:
        return json.JSONEncoder.default(obj)
