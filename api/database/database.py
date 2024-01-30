from database_accessor import *
import json
from bson.json_util import dumps
from bson.json_util import loads


def user_entry(old_user_id, new_user_id, full_name, affiliation):
    """
    Returns True if user already exists in the database/ if the user has 
    logged into the website before. 

    Returns False if user is new/ if it is the user's first time
    logging into website. The new user would have been initialized
    in the database when this function is called. 

    [user_id] is a string that represents the hashed id of the user
    [full_name] is a string that represents the full name of the user, extracted
    during authentication by Cornell IDP when user logs in. 
    [affiliation] is a string that represents the user's affiliation with Cornell, 
    extracted during authentication by Cornell IDP when user logs in. The most common
    affiliation is "student". 
    """
    return user_DB_Handler.initialize_user_if_not_exists(old_user_id, new_user_id, full_name, affiliation).value


def get_user_full_name(user_id):
    """
    Returns user's full name given their user id. If user does not exist 
    in the database, an error is raised. 

    [user_id] is a string that represents the hashed id of the user
    """
    return user_DB_Handler.get_user_full_name(user_id).value


def load_courses(user_id):
    """
    Returns a list of all the saved courses by user corresponding to the 
    given user_id. 

    If the user does not have any saved courses, or user does not exist in
    the database, an empty list is returned. 

    [user_id] is a string that represents the hashed id of the user
    """
    course_name_list = user_DB_Handler.get_all_course_names_for_user(user_id)
    if hasattr(course_name_list, "value"):
        return course_name_list.value
    else:
        return []


def course_entry(user_id, course_name, course_title, course_credits, course_description, user_save_course):
    """
    THIS FUNCTION IS DEPRECATED. It was used by initial versions of Pathways the 
    following way:

    course_entry checks for the existence of the course
    with course name 'course_name', and adds the course if
    its not found. If the course is found, the list of user's ids
    corresponding to users who saved the course is updated with 'user_id'
    'user_save_course' is true when this function is called in order to save
    a course by a user. Otherwise, it is false (for the potential case where
    a pathway is saved, without the individual courses being saved)

    """
    course_DB_Handler.initialize_course_if_not_exists(
        course_name,
        course_title,
        course_credits,
        course_description
    )

    if user_save_course:
        user_entry(user_id)
        course_DB_Handler.add_one_user(user_id, course_name)
        user_DB_Handler.add_one_course_for_user(user_id, course_name)

    return course_name


def pathway_entry(user_id, pathway_id, courses, query, save_date, name=None):
    """
    THIS FUNCTION IS DEPRECATED. It was used by initial versions of Pathways the 
    following way:

    pathway_entry checks for the existence of the pathway
    found from the get parameter in the database, and adds
    the pathway if its not found. If not found, the pathway is
    created. The user who saved the pathway's document is updated
    with the id of the pathway save document
    """
    if not pathway_DB_Handler.pathway_exist(pathway_id).value:
        course_names_array = []
        for course in json.loads(courses):
            course_names_array.append(
                course_entry(
                    user_id,
                    course["course_name"],
                    course["course_title"],
                    course["course_credits"],
                    course["course_desc"],
                    False
                )
            )
        pathway_DB_Handler.initialize_pathway_if_not_exists(
            pathway_id, courses)
    else:
        pathway_DB_Handler.add_one_user(user_id, pathway_id)
    user_DB_Handler.add_one_pathway_for_user(user_id, pathway_id, name)

def save_calibration_data(search_id, batch_number, user_id, calibration_course_list, user_selected_courses, algorithm_data_dict):
    """
    Inserts calibration data into database. Returns success if insertion is successful. 
    Raises error otherwise.

    [search_id] is the search id of the calibration data. 
    [batch_number] is the number of batch the user has gone through when looking 
    through suggested/calibration courses to finalize search result. 
    [user_id] is the user's id.
    [calibration_course_list] is a list of calibration courses  
    [user_selected_courses] is a list of courses the user has selected among the 
    calibration courses.
    [algorithm_data_dict] is the search algorithm result in a dictionary format
    """
    res = calibration_DB_Handler.insert_one_calibration(
         search_id, batch_number, user_id, calibration_course_list, user_selected_courses, algorithm_data_dict
    )
    return res

def update_calibration_on_loaded_batch_click(user_id, search_id, batch_number, courses_presented, algorithm_data_dict):
    """
    Updates corresponding calibration data into database. This function
    should be called when the user loads another batch of suggested/calibration
    courses.

    Returns success if update is successful. 
    Raises error otherwise.

    [user_id] is the user's id.
    [search_id] is the search id of the calibration data. 
    [batch_number] is the number of batch the user has gone through when looking 
    through suggested/calibration courses to finalize search result. 
    [courses_presented] is a list of calibration courses presented when the
    user requests for another batch of suggested/calibration courses. 
    [algorithm_data_dict] is the search algorithm result in a dictionary format
    """
    res = calibration_DB_Handler.update_calibration_on_loaded_batch_click(user_id, search_id, batch_number, courses_presented, algorithm_data_dict)
    return res

def update_calibration_on_click_search(user_id, search_id, user_selected_courses):
    """
    Updates corresponding calibration data into database. This function
    should be called when the user requests for the final search results/visualizations.

    Returns success if update is successful. 
    Raises error otherwise.

    [user_id] is the user's id.
    [search_id] is the search id of the calibration data. 
    [user_selected_courses] is a list of courses the user has selected among the 
    calibration courses.
    """
    res = calibration_DB_Handler.update_calibration_on_click_search(user_id, search_id, user_selected_courses)
    return res


def save_visualization_data(search_id, user_id, is_major_declared, majors, interest_keywords, user_selected_courses, pathway_ids, algorithm_data_dict, customized_majors):
    """
    Inserts visualization data into database. This function
    should be called when the user requests for the final search results/visualizations. 

    Raises error if insertion is unsuccessful.

    [search_id] is the search id of the specific search when the function is called. 
    [user_id] is the user's id.
    [is_major_declared] is a boolean of whether the user selected that they have declared
    their major (True) or not (False)
    [interest_keywords] is a list of keywords the user has inputted for their interests. 
    [user_selected_courses] is a list of courses user has selected from a batch of 
    suggested/calibration courses.
    [pathway_ids] is a list of ID's of the pathways the algorithm has given to the user
    given the user's inputs. 
    [algorithm_data_dict] is the search algorithm result in a dictionary format
    [customized_majors] is a string of customized major user has inputted
    if their major is not in the list of official majors. This happens when
    the user selects "Other" as their major. 
    """
    visualization_DB_Handler.insert_one_visualization(
        search_id, user_id, is_major_declared, majors, interest_keywords, user_selected_courses, pathway_ids, algorithm_data_dict, customized_majors)


def unsave_query(user_id, id, search_id):
    """
    Removes the visibility of the query from the user's past queries (makes visibility
    to False instead of True), and logs dashboard action "UNSAVE HISTORY". 
    
    Raises error if removal is unsuccessful.

    [user_id] is user's id.
    [id] is the id of the query. This is not equivalent to search_id, since 
    queries that were done before search_id was implemented into production could have been 
    unsaved. 
    [search_id] is search id of the query if it exists. 
    """
    res = visualization_DB_Handler.remove_visibility_one_visualization_from_user(
        user_id, id)
    dashboard_log_DB_Handler.add_action_to_log(user_id, "UNSAVE HISTORY", search_id, None, None, None)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)


def get_all_query(user_id):
    """
    Returns a list of all saved queries (queries where visibility is True) for 
    user with id user_id. Raises error if user does not exist in database.

    [user_id] is user's id. 
    """
    return visualization_DB_Handler.get_all_visible_visualization_for_user(user_id).value

    
def load_pathways(user_id):
    """
    Returns a dictionary where key represents the saved pathway id and value
    represents another dictionary that stores the pathway's name, search id, 
    and the date that the pathway was stored. 

    If user does not exist in database, raises error. 

    [user_id] is user's id. 
    """
    res = user_DB_Handler.get_all_pathway_ids_for_user(user_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    else:
        return res.value


def get_pathway(pathway_id):
    """
    Given a pathway_id, returns the pathway's information. Raises error 
    if pathway does not exist in database. 

    [pathway_id] is the id of the specified pathway. 
    """
    return pathway_DB_Handler.get_pathway(pathway_id).value


def unsave_course(user_id, search_id, course_name):
    """
    Removes coures from user's list of saved courses in database. Also 
    logs dashboard action "UNSAVE COURSE". 

    [user_id] is user's id. 
    [search_id] is the search ID of when the user saved this course. 
    [course_name] is the name of the course that the user saved. 
    """
    user_DB_Handler.remove_one_course_for_user(user_id, course_name)
    dashboard_log_DB_Handler.add_action_to_log(user_id, "UNSAVE COURSE", search_id, None, None, course_name)


def save_course(user_id, course_name, search_id, pathway_id, vis_pos_idx):
    """
    Saves course to user's list of saved courses in database. Also logs
    dashboard action "SAVE COURSE".

    [user_id] is user's id. 
    [course_name] is the name of the course that is trying to be saved. 
    [search_id] is the search ID of when the user is saving this course.
    [pathway_id] is the ID of the pathway this course is in/ where it is being 
    saved from. 
    [vis_pos_idx] is the visualization position index of the pathway this course 
    is in. 
    """
    user_DB_Handler.add_one_course_for_user(user_id, search_id, course_name)
    dashboard_log_DB_Handler.add_action_to_log(user_id, "SAVE COURSE", search_id, pathway_id, vis_pos_idx, course_name)


def unsave_pathway(user_id, search_id, pathway_id, name):
    """
    Removes pathway from user's dictionary of saved pathways in database. Also logs
    dashboard action "UNSAVE PATHWAY".

    Raises error if removal or logging dashboard action is unsuccessful. 

    [user_id] is user's id. 
    [search_id] is the search ID of when the user is unsaving this pathway.
    [pathway_id] is the ID of the pathway this course is in/ where it is being 
    saved from. 
    [name] is the name of the pathway user inputted when saving the pathway. 
    """
    res = user_DB_Handler.remove_one_pathway_for_user(user_id, pathway_id, name)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    res = dashboard_log_DB_Handler.add_action_to_log(user_id, "UNSAVE PATHWAY", search_id, pathway_id, None, None)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)


def save_pathway(user_id, name, search_id, pathway_id, vis_pos_idx):
    """
    Adds pathway to user's dictionary of saved pathways in database. Also logs
    dashboard action "SAVE PATHWAY".

    If addition and logging dashboard action is successful, a dictionary with 
    "msg" as key and "success" is returned. 

    If the pathway already exists in the user's dictionary of saved pathways
    (i.e. user has saved this pathway before), a dictionary with "msg" as key
    and "Already Exists" value is returned. 

    Raises error if addition or logging dashboard action is unsuccessful. 

    [user_id] is user's id. 
    [name] is the name of the pathway user inputted when saving the pathway. 
    [search_id] is the search ID of when the user is saving this pathway.
    [pathway_id] is the ID of the pathway this course is in/ where it is being 
    saved from. 
    [vis_pos_idx] is the visualization position index of the pathway this course 
    is in. 
    """
    res = user_DB_Handler.add_one_pathway_for_user(user_id, name, search_id, pathway_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    if res.value == "already exists":
        return {"msg": "Already Exists"}
    else:
        res = dashboard_log_DB_Handler.add_action_to_log(user_id, "SAVE PATHWAY", search_id, pathway_id, vis_pos_idx, None)
        if res.is_unsuccessful():
            raise RuntimeError(res.error)
        return {"msg": "success"}


def save_survey(search_id, user_id, answer_seq):
    """
    Inserts survey input into database. If insertion is unsuccessful, raises error.

    [search_id] is the search ID of when the user submits or closes out of the survey. 
    [user_id] is the user's id. 
    [answer_seq] is a list of answers of the survey. 
    """
    res = survey_DB_Handler.insert_survey(search_id, user_id, answer_seq)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)


def save_user_course_interaction(search_id, user_id, course_name, pathway_id, vis_pos_idx):
    """
    Inserts user's course interaction into database. If insertion is unsuccessful, raises error. 

    [search_id] is the search ID. 
    [user_id] is the user's id. 
    [course_name] is the name of the course the user has interacted with.
    [pathway_id] is the ID of the pathway the interacted course is in. 
    [vis_pos_idx] is the visualization position index of the pathway this course 
    is in. 
    """
    res = user_interaction_course_DB_Handler.insert_interaction(search_id, user_id, course_name, pathway_id, vis_pos_idx)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)


def close_survey(user_id):
    """
    THIS FUNCTION IS CURRENTLY IRRELEVANT FOR THE CURRENT VERSION OF PATHWAYS. 

    Sets user's attribute "closed_survey" to False. If setting is unsuccessful, 
    raises error. 

    [user_ID] is the user's id. 
    """
    res = user_DB_Handler.close_survey_for_user(user_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)


def save_user_pathway_interaction(search_id, user_id, pathway_id, vis_pos_idx):
    """
    Inserts user's pathway interaction into database. If insertion is unsuccessful, raises error. 

    [search_id] is the search ID. 
    [user_id] is the user's id. 
    [pathway_id] is the ID of the pathway the interacted course is in. 
    [vis_pos_idx] is the visualization position index of the pathway.
    """
    res = user_interaction_pathway_DB_Handler.insert_interaction(search_id, user_id, pathway_id, vis_pos_idx)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)

def generate_search_id(user_id):
    """
    Returns a new search ID.  

    [user_id] is the user's id. 
    """
    return search_id_DB_Handler.generate_search_id(user_id)


def save_feedback(user_id, feedback):
    """
    Inserts feedback into database. Raises error if insertion is unsuccessful.

    [user_id] is the user's id. 
    [feedback] is a string that represents the user's feedback. 
    """
    return feedback_DB_Handler.insert_feedback(user_id, feedback)


def add_pathway_interaction_for_user(user_id, pathway_id):
    """
    Adds pathway interaction into database. Raises error if insertion is unsuccessful.

    [user_id] is the user's id.
    [pathway_id] is the pathway id.
    """
    res = user_DB_Handler.add_pathway_interaction(user_id, pathway_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    return res.value


def get_number_of_pathway_interactions_for_user(user_id):
    """
    Returns the number of unique pathways user has interacted with.

    [user_id] is the user's id
    """
    res = user_DB_Handler.get_number_of_pathway_interactions(user_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    return res.value


def insert_pathway_order_and_color(user_id, search_id, pathway_id, order_and_color):
    """
    Inserts pathway data, including the order and the color, into database. 
    If insertion is unsuccessful, raises error.

    [user_id] is the user's id. 
    [search_id] is the search ID. 
    [pathway_id] is the pathway's ID. 
    [order_and_color] is the pathway data that includes the ordering and color. 
    """
    res = saved_pathway_DB_Handler.insert_pathway_order_and_color(user_id, search_id, pathway_id, order_and_color)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    return res


def get_pathway_order_and_color(user_id, search_id, pathway_id):
    """
    Returns pathway data, including the order and the color, from database. 
    If fetching is unsuccessful, such as the pathway information for this user is 
    not in the database, raises error.

    [user_id] is the user's id. 
    [search_id] is the search ID. 
    [pathway_id] is the pathway's ID. 
    """
    res = saved_pathway_DB_Handler.get_pathway_order_and_color(user_id, search_id, pathway_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    return loads(dumps(res.value))


def add_action_to_dashboard_log(user_id, action, search_id, pathway_id, visualization_position_index, course_name):
    """
    Adds dashboard log into database. Raises error if insertion is unsuccessful. 

    [user_id] is the user's id. 
    [action] is a string that represents the dashboard action. 
    [search_id] is the search ID. 
    [pathway_id] is the pathway's ID. 
    [visualization_position_index] is the visualization position index of the relevant object.  
    [course_name] is the course related to the dashhboard action. 
    """
    res = dashboard_log_DB_Handler.add_action_to_log(user_id, action, search_id, pathway_id, visualization_position_index, course_name)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    return res


def get_number_of_dashboard_visits(user_id):
    """
    Returns the number of times the user has visited the dashboard. If user does
    not exist, raises error. If the user has never visited the dashboard, returns 0. 

    [user_id] is the user's id. 
    """
    res = user_DB_Handler.get_number_of_dashboard_visits(user_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    if hasattr(res, "value"):
        return res.value
    else:
        return 0 


def increment_number_of_dashboard_visits(user_id):
    """
    Increments the number of times the user has visited the dashboard. If 
    user exists, returns the number of times the user has visited the dashboard, 
    including this visit. If user does not exist, raises error. 
    If other errors arise, 0 is returned. 

    [user_id] is the user's id. 
    """
    res = user_DB_Handler.increment_number_of_dashboard_visits(user_id)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)
    if hasattr(res, "value"):
        return res.value
    else:
        return 0 


def insert_search(search_id, user_id, is_major_declared, majors, customized_majors, interest_keywords):
    """
    Inserts search data into search log database. 

    [search_id] is the search ID. 
    [user_id] is the user's id.
    [is_major_declared] is a boolean of whether the user has declared their major (True) or not (False)
    [majors] is a list of majors the user has chosen.
    [customized_majors] is a string of customized major if the user selected "Other" for their major. 
    [interest_keywords] is a list of keywords user has submitted for their interests. 
    """
    return search_db_handler.insert_search(search_id, user_id, is_major_declared, majors, customized_majors, interest_keywords)


def write_to_log(search_id, user_id, log_type, **kwargs):
    res = log_DB_Handler.insert_one_log(search_id, user_id, log_type, **kwargs)
    if res.is_unsuccessful():
        raise RuntimeError(res.error)


