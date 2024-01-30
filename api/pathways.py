from flask import Flask, abort, jsonify, request, redirect
from addr_info import *
import os
import database as database
import auth as auth
import hashlib
from data_loader import GlobalData, read_pickle_files
from course_search.calibration_search_engine import CalibrationEngineImpl
from pathway_search.pathway_search_engine_maxintragroupdist import PathwaySearchEngineMaxIntragroup
from database.redis_accessor import *
from logger import pathways_system_logger


ttl_redis_handler = TTL_Redis_Handler()
calibration_new_redis_handler = Calibration_Redis_Handler(ttl_redis_handler)
calibration_new_redis_handler.clear_cache()

data_loader = GlobalData(course_data=True, pathway_data=True,
                        major_and_minor_data=True, course_desc_list=True,
                        course_title_list=True, PC=True,
                        calibration_course_mask=True,
                        global_PCA_model=True, local_PCA_model=False)

calibration_engine = CalibrationEngineImpl(calibration_new_redis_handler, data_loader, determinisitic=False)
pathway_engine = PathwaySearchEngineMaxIntragroup(data_loader, calibration_engine, determinisitic=False)

app = Flask(__name__)

# define secret key for session
app.config.update(SECRET_KEY=os.urandom(24))


# The following is some example code for how to use the authentication module.
# Note that while the best way (that I'm aware of) to handle session data across
# React and Flask is to assign each session a token and then pass it with each React
# request, this is not the ideal way to store sessions because they never get removed.
# In a more concrete implementation, we should account for session expiry. This is an example only.

app_home = "http://localhost:3000"
auth_conf = auth.init_auth(
    idp_metadata="https://shibidp-test.cit.cornell.edu/idp/shibboleth",
    metadata_endpoint="http://localhost:5000/auth/metadata",
    consumer_endpoint="http://localhost:5000/auth/consume",
)
sessions = {}


@app.route("/auth/metadata")
def auth_metadata():
    try:
        result = auth.serve_metadata(auth_conf)
        pathways_system_logger.log_info(f"/auth/metadata")
        return result
    except BaseException as e:
        pathways_system_logger.log_exception(e)
        abort(500, description="We are sorry that we got an error in our server")


@app.route("/auth/sso", methods=["POST"])
def auth_sso():
    try:
        result = auth.serve_sso_redirect(request, auth_conf, "exampleToken")
        pathways_system_logger.log_info(f"/auth/sso")
        return jsonify({"url": result})
    except BaseException as e:
        pathways_system_logger.log_exception(e)
        abort(500, description="We are sorry that we got an error in our server")


salt = b"$2b$12$Il6f/xw2EdC/4J0NE82TTe"

@app.route("/auth/consume", methods=["POST"])
def auth_consume():
    try:
        results = auth.consume_response(request, auth_conf)
        old_hashed_id = hashlib.md5(results["netId"].encode()).hexdigest()
        new_hashed_id = hashlib.sha256(results["netId"].encode("utf8") + salt).hexdigest()
        sessions[old_hashed_id] = {
            "loggedIn": not results["errored"],
            "netId": results["netId"],
            "email": results["email"],
            "name": results["fullName"],
        }
        full_name = results["fullName"]
        affiliation = None
        if 'primaryAffiliation' in results:
            affiliation = results["primaryAffiliation"]
        result = redirect(app_home + "?" + "hashed_id=" + old_hashed_id, 302)
        pathways_system_logger.log_info(f"/auth/consume - {results['netId']}")
        database.user_entry(old_hashed_id, new_hashed_id, full_name, affiliation)
        return result
    except BaseException as e:
        pathways_system_logger.log_exception(e)
        abort(500, description="We are sorry that we got an error in our server")


@app.route("/get_user_full_name", methods = ["GET", "POST"])
def get_user_full_name():
    """
    Returns user's full name if it exists (returns empty string otherwise)
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            full_name = database.get_user_full_name(user_id)
            name = {"full_name": full_name}
            pathways_system_logger.log_info(f"get_user_full_name - {user_id}")
            return name
        else:
            pathways_system_logger.log_warning(f"get_user_full_name - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(e)
        abort(500, description="We are sorry that we got an error in our server")


def string_list_to_list(s):
    """
    Converts stringified list to a list
    ex. "['hello']" to ["hello"]

    Prerequisite: items in stringified list are in single quotes
    """
    return list(map(str.strip,s.strip('][').replace("'", '').split(',')))


@app.route('/load_courses', methods=['GET', 'POST'])
def load_courses():
    """
    Returns all the saved courses by the given user
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            courses = database.load_courses(user_id)
            for course in courses:
                if course['course_name'] in data_loader.course_dictionary:
                    one_course_data = data_loader.course_dictionary[course['course_name']]
                    course['course_title'] = one_course_data.get_course_title()
                    course['course_desc'] = one_course_data.get_course_desc()
                    course['offerings'] = string_list_to_list(one_course_data.get_offerings())
                    course['instructors'] = string_list_to_list(one_course_data.get_instructors())
                    course['roster_links'] = string_list_to_list(one_course_data.get_roster_links())
                else:
                    course['course_title'] = "Not offered"
                    course['course_desc'] = "No description"
                    course['offerings'] = None
                    course['instructors'] = None
                    course['roster_links'] = None
                if course['course_desc'] is None or course['course_desc'] == "na":
                    course['course_desc'] = "No description"
            courses.sort(key = lambda x: x['date'], reverse=True)
            courses_json = jsonify(courses)
            pathways_system_logger.log_info(f"load_courses - {user_id}")
            return courses_json
        else:
            pathways_system_logger.log_warning(f"load_courses - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"load_courses - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/load_pathways', methods=['GET', 'POST'])
def load_pathways():
    """
    Returns saved pathways for a given user
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            try:
                pathway_ids_to_names = database.load_pathways(user_id)
            except BaseException as e:
                pathways_system_logger.log_exception(f"load_pathways - {str(e)}")
                abort(500, description="We are sorry that we got an error in our server")
            pathways = []
            for pathway_id in pathway_ids_to_names.keys():
                saved_pathway_info = pathway_ids_to_names[pathway_id]
                if "name" not in saved_pathway_info or "search_id" not in saved_pathway_info or "date" not in saved_pathway_info:
                    continue
                one_pathway_data = data_loader.pathways_dictionary[pathway_id]
                pathway = {}
                pathway['pathway_id'] = pathway_id
                pathway['majors'] = one_pathway_data.get_majors()
                pathway['minors'] = one_pathway_data.get_minors()
                pathway['name'] = pathway_ids_to_names[pathway_id]['name']
                pathway['search_id'] = pathway_ids_to_names[pathway_id]['search_id']
                pathway['date'] = pathway_ids_to_names[pathway_id]['date']
                pathways.append(pathway)
            pathways.sort(key=lambda x: x['date'], reverse=True)
            pathways_json = jsonify(pathways)
            pathways_system_logger.log_info(f"load_pathways - {user_id}")
            return pathways_json
        else:
            pathways_system_logger.log_warning(f"load_pathways - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"load_pathways - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/get_pathway', methods = ['GET', 'POST'])
def get_pathway():
    """
    Returns pathway visualization given pathway id
    """
    try:
        if request.is_json:
            pathway_id = request.json["pathway_id"]
            if pathway_id not in  data_loader.pathways_dictionary:
                return {"msg": "Pathway not found"}
            pathway_data = data_loader.pathways_dictionary[pathway_id]
            pathways_json = pathway_data.simple_jsonify()
            if "hashed_id" in request.json and "search_id" in request.json:
                user_id = request.json["hashed_id"]
                search_id = request.json["search_id"]
                courses = database.get_pathway_order_and_color(user_id, search_id, pathway_id)
                pathways_json["courses"] = courses
                database.add_action_to_dashboard_log(user_id, "INTERACT PATHWAY", search_id, pathway_id, None, None)
            pathways_json["msg"] = "Pathway found"
            pathways_system_logger.log_info(f"get_pathway - {pathway_id}")
            return pathways_json
        else:
            pathways_system_logger.log_warning(f"get_pathway - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"get_pathway - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/save_course', methods=['GET', 'POST'])
def save_course():
    """
    Saves course for the given user
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            course_name = request.json["course_name"]
            search_id = request.json["search_id"]
            pathway_id = request.json["pathway_id"]
            vis_pos_idx = request.json["visualization_position_index"]
            database.save_course(user_id, course_name, search_id, pathway_id, vis_pos_idx)
            pathways_system_logger.log_info(f"save_course - {user_id}")
            return jsonify()
        else:
            pathways_system_logger.log_warning(f"save_course - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"save_course - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/unsave_course', methods=['GET', 'POST'])
def unsave_course():
    """
    Unsaves course for given user. 
    """
    try:
        user_id = request.json["hashed_id"]
        search_id = request.json["search_id"]
        pathways_system_logger.log_info(f"unsave_course - {user_id} - start")
        course_name = request.json["course_name"]
        database.unsave_course(user_id, search_id, course_name)
        pathways_system_logger.log_info(f"unsave_course - {user_id} - finished")
        return jsonify()
    except BaseException as e:
        pathways_system_logger.log_exception(f"unsave_course - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/save_pathway', methods=['GET', 'POST'])
def save_pathway():
    """
    Saves pathway for given user
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            search_id = request.json["search_id"]
            pathway_id = request.json["pathway_id"]
            pathway_name = request.json["name"]
            vis_pos_idx = request.json["visualization_position_index"]
            order_and_color = request.json["order_and_color"]
            res = database.save_pathway(user_id, pathway_name, search_id, pathway_id, vis_pos_idx)
            if "msg" in res:
                if res["msg"] == "success":
                    database.insert_pathway_order_and_color(user_id, search_id, pathway_id, order_and_color["courses"])
                    pathways_system_logger.log_info(f"save_pathway - {user_id}")
                    return {"msg": "success"}
                else:
                    return {"msg": "Pathway already saved"}
        else:
            pathways_system_logger.log_warning(f"save_pathway - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"save_pathway - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/unsave_pathway', methods=['GET', 'POST'])
def unsave_pathway():
    """
    Unsaves pathway for given user. 
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            search_id = request.json["search_id"]
            pathway_id = request.json["pathway_id"]
            pathway_name = request.json["name"]
            database.unsave_pathway(user_id, search_id, pathway_id, pathway_name)
            pathways_system_logger.log_info(f"unsave_pathway - {user_id}")
            return jsonify()
        else:
            pathways_system_logger.log_warning(f"unsave_pathway - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"unsave_pathway - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/save_history', methods=['GET', 'POST'])
def save_history_query():
    """
    Saves searched query for given user
    """
    try:
        user_id = request.json["hashed_id"]
        pathways_system_logger.log_info(f"save_history - {user_id} - start")
        query = request.json["query"]
        is_major_declared = request.json["is_major_declared"]
        majors = request.json["majors"]
        interest_keywords = request.json["interest_keywords"]
        database.save_query(user_id, query, is_major_declared, majors, interest_keywords)
        pathways_system_logger.log_info(f"save_history - {user_id} - finished")
        return jsonify()
    except BaseException as e:
        pathways_system_logger.log_exception(f"save_history - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/get_history', methods=['GET', 'POST'])
def get_history_query():
    """
    Returns all past saved queries by given user. Any query that the user
    "removed" from their search history (i.e. the visibility of this query
    for the user was set to False) will not be in the returned object. 
    """
    try:
        user_id = request.json["hashed_id"]
        pathways_system_logger.log_info(f"get_history - {user_id} - start")
        queries = database.get_all_query(user_id)
        for query in queries:
            query['_id'] = str(query['_id'])
            if 'search_id' in query:
                query['search_id'] = str(query['search_id'])
            else:
                query['search_id'] = None
        queries.sort(key = lambda x: x["date"], reverse=True)
        queries = jsonify(queries)
        pathways_system_logger.log_info(f"get_history - {user_id} - finished")
        return queries
    except BaseException as e:
        pathways_system_logger.log_exception(f"get_history - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/unsave_history', methods=['GET', 'POST'])
def unsave_history_query():
    """
    Unsaves searched history from given user
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            id = request.json["_id"]
            search_id = request.json["search_id"]
            database.unsave_query(
                user_id, id, search_id)
            pathways_system_logger.log_info(f"unsave_history - {user_id}")
            return jsonify()
        else:
            pathways_system_logger.log_warning(f"unsave_history - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"unsave_history - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


@app.route('/save_survey', methods=['POST'])
def save_survey():
    """
    Saves survey result into database. 
    """
    try:
        search_id = request.json['search_id']
        user_id = request.json["hashed_id"]
        pathways_system_logger.log_info(f"save_survey - {user_id} - start")
        answer_arr = request.json["answer_seq"]
        database.save_survey(search_id, user_id, answer_arr)
        pathways_system_logger.log_info(f"save_survey - {user_id} - finished")
        return jsonify()
    except BaseException as e:
        pathways_system_logger.log_exception(f"save_survey - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


def check_calibration_format(user_id, is_major_declared, majors, interest_keywords, batch_number):
    if type(user_id) != str or len(user_id) == 0:
        return False
    if type(is_major_declared) != bool:
        return False
    if type(majors) != list or any(type(m) != str for m in majors):
        return False
    if type(interest_keywords) != list or len(interest_keywords) == 0 or \
        any(type(m) != str for m in interest_keywords):
        return False
    if type(batch_number) != int or batch_number < 0:
        return False
    return True


@app.route('/get_suggested_courses', methods=['POST'])
def get_suggested_courses():
    """
    Endpoint for saving visualization form inputs and returning search result
    """
    try:
        search_id = request.json['search_id']
        user_id = request.json["hashed_id"]
        pathways_system_logger.log_info(f"get_suggested_courses - {user_id} - start")
        is_major_declared = request.json["is_major_declared"]
        majors = request.json["majors"]
        customized_majors = request.json["customized_majors"]
        interest_keywords = request.json['interest_keywords']
        batch_number = request.json['batch_number']
        if not check_calibration_format(user_id, is_major_declared, majors, interest_keywords, batch_number):
            abort(404)

        calibration_step_json, algorithm_data_dict = calibration_engine.calibration_step(interest_keywords, batch_number)
        calibration_course_list = [course["course_name"] for course in calibration_step_json["courses"]]
        if batch_number == 0:
            # Log for Search Log 
            database.insert_search(search_id, user_id, is_major_declared, majors, customized_majors, interest_keywords)
            # Log new calibration record
            database.save_calibration_data(search_id, batch_number, user_id, calibration_course_list, None, algorithm_data_dict)
        else:
            # Update previous calibration record with new batch number and add to the list of presented courses during calibration
            database.update_calibration_on_loaded_batch_click(user_id, search_id, batch_number, calibration_course_list, algorithm_data_dict)
        pathways_system_logger.log_info(f"get_suggested_courses - {user_id} - finished")
        calibration_step_json['search_id'] = search_id
        return jsonify(calibration_step_json)
    except BaseException as e:
        pathways_system_logger.log_exception(f"get_suggested_courses - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")


def check_visualization_format(user_id, is_major_declared, majors, interest_keywords, user_selected_courses):
    if type(user_id) != str or len(user_id) == 0:
        return False
    if type(is_major_declared) != bool:
        return False
    if type(majors) != list or any(type(m) != str or len(m) == 0 for m in majors):
        return False
    if type(interest_keywords) != list or len(interest_keywords) == 0 or \
        any(type(m) != str for m in interest_keywords):
        return False
    if type(user_selected_courses) != list or \
        any(type(m) != str or len(m) == 0 for m in user_selected_courses):
        return False
    return True


@app.route('/get_visualization', methods=['POST'])
def get_visualization():
    """
    Endpoint for saving visualization form inputs and returning search result
    """
    try:
        search_id = request.json['search_id']
        user_id = request.json["hashed_id"]
        pathways_system_logger.log_info(f"get_visualization - {user_id} - start")
        is_major_declared = request.json["is_major_declared"]
        majors = request.json["majors"]
        customized_majors = request.json["customized_majors"]
        interest_keywords = request.json['interest_keywords']
        user_selected_courses = [c['course_name'] for c in request.json['suggested_courses']]
        if not check_visualization_format(user_id, is_major_declared, majors, interest_keywords, user_selected_courses):
            abort(404)

        # Final update to calibration log 
        database.update_calibration_on_click_search(user_id, search_id, user_selected_courses)

        pathways_json, algorithm_data_dict = pathway_engine.pathway_search(user_selected_courses, majors, interest_keywords)
        pathway_ids = [pathway["pathway_id"] for pathway in pathways_json["pathways"]]
        database.save_visualization_data(search_id, user_id, is_major_declared, majors, interest_keywords, user_selected_courses, pathway_ids, algorithm_data_dict, customized_majors)
        database.add_pathway_interaction_for_user(user_id, pathways_json["pathways"][0]["pathway_id"])
        pathways_system_logger.log_info(f"get_visualization - {user_id} - finished")
        return jsonify(pathways_json)
    except BaseException as e:
        pathways_system_logger.log_exception(f"get_visualization - {str(e)}")
        abort(500, description="We are sorry that we got an error in our server")

# TODO: given pathway id, return career outcome, blocked by career outcome data from generate_data.sh
@app.route('/get_career_outcome', methods=['GET'])
def get_career_outcome(pathway_id):
    pass

@app.route('/record_user_course_interaction', methods=['POST'])
def record_user_course_interaction():
    """
    Endpoint for recording user interaction with course on visualization
    """
    try:
        pathways_system_logger.log_info(f"record_user_course_interaction - start")
        search_id = request.json['search_id']
        user_id = request.json["hashed_id"]
        course_name = request.json["course_name"]
        pathway_id = request.json["pathway_id"]
        vis_pos_idx = request.json["visualization_position_index"]
        vis_pos_idx = int(vis_pos_idx)
        database.save_user_course_interaction(search_id, user_id, course_name, pathway_id, vis_pos_idx)
        pathways_system_logger.log_info(f"record_user_course_interaction - finished")
        return jsonify()
    except BaseException as e:
        pathways_system_logger.log_exception(f"record_user_course_interaction - {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/new_search_id', methods=['POST'])
def get_new_search_id():
    """
    Generates and returns new search ID. 
    """
    try:
        user_id = request.json['hashed_id']
        pathways_system_logger.log_info(f"new_search_id - {user_id} - start")
        new_search_id = database.generate_search_id(user_id)
        pathways_system_logger.log_info(f"new_search_id - {user_id} - finished")
        return jsonify({'search_id': new_search_id})
    except BaseException as e:
        pathways_system_logger.log_exception(f"new_search_id - {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/record_user_pathway_interaction', methods=['POST'])
def record_user_pathway_interaction():
    """
    Endpoint for recording user interaction with course on visualization
    """
    try:
        search_id = request.json['search_id']
        user_id = request.json["hashed_id"]
        pathways_system_logger.log_info(f"record_user_pathway_interaction - {user_id} - start")
        vis_pos_idx = request.json["visualization_position_index"]
        vis_pos_idx = int(vis_pos_idx)
        pathway_id = request.json["pathway_id"]
        database.save_user_pathway_interaction(search_id, user_id, pathway_id, vis_pos_idx)
        pathways_system_logger.log_info(f"record_user_pathway_interaction - {user_id} - finished")
        return jsonify()
    except BaseException as e:
        pathways_system_logger.log_exception(f"record_user_pathway_interaction - {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/set_feedback', methods = ['POST'])
def set_feedback():
    """
    Endpoint for setting feedback from a user
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            feedback = request.json["feedback"]
            database.save_feedback(user_id, feedback)
            pathways_system_logger.log_info(f"set_feedback - {user_id}")
            return jsonify()
        else:
            pathways_system_logger.log_warning(f"set_feedback - not json input: {str(request)}")
            abort(400, description="The query parameters are not in json")
    except BaseException as e:
        pathways_system_logger.log_exception(f"record_user_pathway_interaction - {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/add_user_visualization_interaction', methods=['POST'])
def increment_user_visualization_interaction():
    """
    Endpoint for recording user interaction with visualization. After adding
    the specified pathway id into the set of unique pathway ids user has
    interacted with, the endpoint returns whether the user should have a survey
    popped or not 
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            pathway_id = request.json["pathway_id"]
            res = database.add_pathway_interaction_for_user(user_id, pathway_id)
            show_survey = False
            # THIS x variable will change!
            x = 5
            if res == 3 or (res > 3 and (res - 3)%x == 0):
                show_survey = True
            return jsonify({"show_survey": show_survey})
        else:
            pathways_system_logger.log_warning(f"increment_user_visualization_interaction - not json input: {str(request)}")

            abort(404, description = "The query parameters are in the wrong format")
    except BaseException as e:
        pathways_system_logger.log_warning(f"increment_user_visualization_interaction - : {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/get_show_survey', methods=['POST'])
def get_show_survey():
    """
    Returns whether the user should have a survey show or not. 
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            res = database.get_number_of_pathway_interactions_for_user(user_id)
            show_survey = False
            # THIS x variable will change!
            x = 5
            if res == 3 or (res > 3 and (res - 3)%x == 0):
                show_survey = True
            return jsonify({"show_survey": show_survey})
        else:
            pathways_system_logger.log_warning(f"get_show_survey - not json input: {str(request)}")

            abort(404, description = "The query parameters are in the wrong format")
    except BaseException as e:
        pathways_system_logger.log_warning(f"get_show_survey - : {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/log_dashboard_course_interaction', methods = ['POST'])
def log_dashboard_course_interaction():
    """
    Logs dashboard's course interaction
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            search_id = request.json["search_id"]
            course_name = request.json["course_name"]
            database.add_action_to_dashboard_log(user_id, "INTERACT COURSE", search_id, None, None, course_name)
            return {"status": "success"}
        else:
            pathways_system_logger.log_warning(f"save_dashboard_action - not json input: {str(request)}")
            abort(404, description = "The query parameters are in the wrong format")
    except BaseException as e:
        pathways_system_logger.log_warning(f"save_dashboard_action - : {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/log_dashboard_course_interaction_in_pathway', methods = ['POST'])
def log_dashboard_course_interaction_in_pathway():
    """
    Logs dashboard's course interaction
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            search_id = request.json["search_id"]
            pathway_id = request.json["pathway_id"]
            course_name = request.json["course_name"]
            database.add_action_to_dashboard_log(user_id, "INTERACT COURSE IN PATHWAY", search_id,pathway_id, None, course_name)
            return {"status": "success"}
        else:
            pathways_system_logger.log_warning(f"save_dashboard_action - not json input: {str(request)}")
            abort(404, description = "The query parameters are in the wrong format")
    except BaseException as e:
        pathways_system_logger.log_warning(f"save_dashboard_action - : {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/visit_dashboard', methods = ['POST'])
def visit_dashboard():
    """
    Increments user's visited number of times to dashboard
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            res = database.increment_number_of_dashboard_visits(user_id)
            database.add_action_to_dashboard_log(user_id, "VISIT DASHBOARD", None, None, None, None)
            return {"number_of_dashboard_visits": res}
        else:
            pathways_system_logger.log_warning(f"visit_dashboard - not json input: {str(request)}")
            abort(404, description = "The query parameters are in the wrong format")
    except BaseException as e:
        pathways_system_logger.log_warning(f"visit_dashboard - : {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")


@app.route('/get_number_of_dashboard_visits', methods = ['POST'])
def get_number_of_dashboard_visits():
    """
    Returns user's visited number of times to dashboard
    """
    try:
        if request.is_json:
            user_id = request.json["hashed_id"]
            res = database.get_number_of_dashboard_visits(user_id)
            return {"number_of_dashboard_visits": res}
        else:
            pathways_system_logger.log_warning(f"get_number_of_dashboard_visits - not json input: {str(request)}")
            abort(404, description = "The query parameters are in the wrong format")
    except BaseException as e:
        pathways_system_logger.log_warning(f"get_number_of_dashboard_visits - : {str(e)}")
        abort(500, description = "We are sorry that we got an error in our server")

if __name__ == '__main__':
    app.run()
