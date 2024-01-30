import pymongo
from pymongo.collection import Collection
from pymongo import MongoClient
from pymongo import ReturnDocument
from datetime import datetime
from enum import Enum
from database.response import DB_RESPONSE
import threading
from bson import ObjectId


class DB_Handler:

    # initialize a static client for each handler (singleton pattern)
    client = MongoClient('localhost', 27017)

    def __init__(self, collection):
        super().__init__()
        self.db = self.client["pathways-db"]
        self.collection_name = collection
        self.collection = self.db[collection]

    def reset_collection(self) -> Collection:
        self.collection.drop()
        return self.collection

    def reset_index(self, index_dict) -> None:
        if len(self.collection.index_information()) > 0:
            self.collection.drop_indexes()
        self.collection.create_index(index_dict)

    def make_default_obj(self) -> dict:
        return dict()

    def __len__(self):
        return self.collection.count_documents()

    @property
    def length(self):
        return len(self)


class Course_DB_Handler(DB_Handler):

    def __init__(self):
        super().__init__('course-data')

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('course_name', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, course_name, course_title, course_credits, course_desc):
        default_item = super().make_default_obj()
        default_item['search_id'] = search_id
        default_item['course_name'] = course_name
        default_item['course_title'] = course_title
        default_item['course_credits'] = course_credits
        default_item['course_desc'] = course_desc
        default_item['saved_user_ids'] = []
        return default_item

    def initialize_course_if_not_exists(self,
                                        course_name,
                                        course_title,
                                        course_credits,
                                        course_desc,
                                        user_id=None) -> DB_RESPONSE:
        if self.collection.find_one({"course_name": course_name}) is None:
            obj = self.make_default_obj(
                course_name,
                course_title,
                course_credits,
                course_desc
            )
            if user_id is not None:
                obj['user_id'].append(user_id)
            self.collection.insert_one(obj)
        return DB_RESPONSE.success()

    def find_one_course(self, course_name) -> DB_RESPONSE:
        return DB_RESPONSE.success(value=self.collection.find_one({"course_name": course_name}))

    def course_exist(self, course_name) -> DB_RESPONSE:
        res = (self.collection.find_one({"course_name": course_name}) != None)
        return DB_RESPONSE.success(value=res)

    def add_one_user(self, user_id, course_name) -> DB_RESPONSE:
        self.collection.update_one(
            {"course_name": course_name},
            {"$push": {"saved_user_ids": user_id}}
        )
        return DB_RESPONSE.success()

    def remove_one_user(self, user_id, course_name) -> DB_RESPONSE:
        self.collection.update_one(
            {"course_name": course_name},
            {"$pull": {"saved_user_ids": user_id}}
        )
        return DB_RESPONSE.success()


class Pathway_DB_Handler(DB_Handler):

    def __init__(self):
        super().__init__('pathway-data')

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('pathway_id', pymongo.ASCENDING)])

    def make_default_obj(self, pathway_id, courses):
        default_item = super().make_default_obj()
        default_item['pathway_id'] = pathway_id
        default_item['courses'] = courses
        default_item['saved_user_ids'] = []
        return default_item

    def initialize_pathway_if_not_exists(self, pathway_id, courses):
        if self.collection.find_one({"pathway_id": pathway_id}) is None:
            self.collection.insert_one(
                self.make_default_obj(pathway_id, courses))
        return DB_RESPONSE.success()

    def pathway_exist(self, pathway_id) -> DB_RESPONSE:
        res = (self.collection.find_one({"pathway_id": pathway_id}) != None)
        return DB_RESPONSE.success(value=res)

    def get_pathway(self, pathway_id) -> DB_RESPONSE:
        res = self.collection.find_one({'pathway_id': pathway_id})
        if res is None:
            return DB_RESPONSE.errors(f'pathway {pathway_id} does not exist')
        else:
            return DB_RESPONSE.success(value=res)

    def add_one_user(self, user_id, pathway_id) -> DB_RESPONSE:
        if self.pathway_exist(pathway_id) is False:
            return DB_RESPONSE.errors(f"pathway {pathway_id} does not exist")

        self.collection.update_one(
            {"pathway_id": pathway_id},
            {"$push": {"saved_user_ids": user_id}}
        )
        return DB_RESPONSE.success()

    def remove_one_user(self, user_id, pathway_id) -> DB_RESPONSE:
        if self.pathway_exist(pathway_id) is False:
            return DB_RESPONSE.errors(f"pathway {pathway_id} does not exist")

        self.collection.update_one(
            {"pathway_id": pathway_id},
            {"$pull": {"saved_user_ids": user_id}}
        )
        return DB_RESPONSE.success()


class Search_ID_Handler(DB_Handler):
    def __init__(self):
        super().__init__('search-start')
        self.collection_lock = threading.Lock()

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('search_id', pymongo.DESCENDING),
                             ('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, user_id) -> dict:
            default_item = super().make_default_obj()
            default_item['search_id'] = search_id
            default_item['user_id'] = user_id
            default_item['date'] = datetime.now()
            return default_item

    def generate_search_id(self, user_id):
        new_search_id = str(ObjectId())
        self.collection.insert_one(self.make_default_obj(new_search_id, user_id))
        return new_search_id
        

class Search_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('search')
        self.collection_lock = threading.Lock()

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('search_id', pymongo.DESCENDING),
                             ('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, user_id, is_major_declared, majors, customized_majors, interest_keywords) -> dict:
            default_item = super().make_default_obj()
            default_item['search_id'] = search_id
            default_item['user_id'] = user_id
            default_item['is_major_declared'] = is_major_declared
            default_item['majors'] = majors
            default_item['customized_majors'] = customized_majors
            default_item['interest_keywords'] = interest_keywords
            default_item['date'] = datetime.now()
            return default_item

    def insert_search(self, search_id, user_id, is_major_declared, majors, customized_majors, interest_keywords) -> DB_RESPONSE:
        self.collection.insert_one(self.make_default_obj(search_id, user_id, is_major_declared, majors, customized_majors, interest_keywords))  
        return DB_RESPONSE.success()

class Calibration_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('calibration')
        self.collection_lock = threading.Lock()

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('search_id', pymongo.DESCENDING),
                             ('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, batch_number, user_id, calibration_course_list, user_selected_courses, algorithm_data_dict) -> dict:
            default_item = super().make_default_obj()
            default_item['search_id'] = search_id
            default_item['batch_number'] = batch_number
            default_item['user_id'] = user_id
            default_item["courses_presented"] = [calibration_course_list]
            default_item["user_selected_courses"] = user_selected_courses
            default_item['algorithm-data'] = [algorithm_data_dict]
            default_item['date'] = datetime.now()
            return default_item

    def insert_one_calibration(self, search_id, batch_number, user_id, calibration_course_list, user_selected_courses, algorithm_data_dict) -> DB_RESPONSE:
        # generate search id and insert search id is a two-step op and we need a lock in language level 
        self.collection.insert_one(self.make_default_obj(search_id, batch_number, user_id, calibration_course_list, user_selected_courses, algorithm_data_dict))  
        return DB_RESPONSE.success()

    def update_calibration_on_loaded_batch_click(self, user_id, search_id, batch_number, courses_presented, algorithm_data_dict) -> DB_RESPONSE:
        self.collection.find_one_and_update(
            {"search_id": search_id, "user_id": user_id}, 
            {"$set": {"batch_number": batch_number, "date": datetime.now()}, "$push": {"courses_presented": courses_presented, "algorithm-data": algorithm_data_dict}})
        return DB_RESPONSE.success()

    def update_calibration_on_click_search(self, user_id, search_id, user_selected_courses) -> DB_RESPONSE:
        self.collection.find_one_and_update(
            {"search_id": search_id, "user_id": user_id}, 
            {"$set": {"user_selected_courses": user_selected_courses, "date": datetime.now()}})
        return DB_RESPONSE.success()



class Visualization_DB_Handler(DB_Handler):

    def __init__(self):
        super().__init__('visualization-data')

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('search_id', pymongo.DESCENDING),
                            ('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, user_id, is_major_declared, majors, interest_keywords, user_selected_courses, pathway_ids, algorithm_data_dict, customized_majors) -> dict:
        default_item = super().make_default_obj()
        default_item['search_id'] = search_id
        default_item['user_id'] = user_id
        default_item['is_major_declared'] = is_major_declared
        default_item['majors'] = majors
        default_item['customized_majors'] = customized_majors
        default_item['interest_keywords'] = interest_keywords
        default_item['user_selected_courses'] = user_selected_courses
        default_item['algorithm-data'] = algorithm_data_dict
        default_item['user_visible'] = True
        default_item['date'] = datetime.now()
        return default_item

    def insert_one_visualization(self, search_id, user_id, is_major_declared, majors, interest_keywords, user_selected_courses, pathway_ids, algorithm_data_dict, customized_majors) -> DB_RESPONSE:
        self.collection.insert_one(self.make_default_obj(
            search_id, user_id, is_major_declared, majors, interest_keywords, user_selected_courses, pathway_ids, algorithm_data_dict, customized_majors))
        return DB_RESPONSE.success()

    def get_all_visualization_for_user(self, user_id) -> DB_RESPONSE:
        res = self.collection.find({'user_id': user_id})
        if res is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        else:
            return DB_RESPONSE.success(value=[i for i in res])

    def remove_one_visualization_from_user(self, user_id, id):
        self.collection.find_one_and_delete(
            {"user_id": user_id,"_id": ObjectId(id)})

    def get_all_visible_visualization_for_user(self, user_id) -> DB_RESPONSE:
        res = self.collection.find({'user_id': user_id, "user_visible": True})
        if res is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        else:
            return DB_RESPONSE.success(value=[i for i in res])

    def remove_visibility_one_visualization_from_user(self, user_id, id):
        self.collection.find_one_and_update(
            {"user_id": user_id,"_id": ObjectId(id)}, 
            {"$set": {"user_visible": False}})
        return DB_RESPONSE.success()

    def get_recent_visualization_for_user(self, user_id) -> DB_RESPONSE: 
        res = self.collection.find_one({'user_id': user_id}, sort=[('date', pymongo.DESCENDING)])
        if res is None: 
            return DB_RESPONSE.success(value=None)
        else:
            return DB_RESPONSE.success(value=res)

class Saved_Pathway_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('saved-pathway-data')

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('search_id', pymongo.DESCENDING),
                            ('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, user_id, search_id, pathway_id, order_and_color) -> dict:
        default_item = super().make_default_obj()
        default_item['search_id'] = search_id
        default_item['user_id'] = user_id
        default_item['pathway_id'] = pathway_id 
        default_item['order_and_color'] = order_and_color
        return default_item

    def insert_pathway_order_and_color(self, user_id, search_id, pathway_id, order_and_color):
        self.collection.insert_one(self.make_default_obj(
            user_id, search_id, pathway_id, order_and_color))
        return DB_RESPONSE.success()

    def get_pathway_order_and_color(self, user_id, search_id, pathway_id):
        res = self.collection.find_one({'user_id': user_id, 'search_id': search_id, 'pathway_id': pathway_id})
        if res is None:
            return DB_RESPONSE.errors(f'pathway {pathway_id} in search_id {search_id} for user {user_id} does not exist')
        else:
            return DB_RESPONSE.success(value=res["order_and_color"])

class Survey_DB_Handler(DB_Handler):

    def __init__(self):
        super().__init__('survey-data')

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, user_id, answer_seq) -> dict:
        default_item = super().make_default_obj()
        default_item['search_id'] = search_id
        default_item['user_id'] = user_id
        default_item['answer_seq'] = answer_seq
        default_item['date'] = datetime.now()
        return default_item

    def insert_survey(self, search_id, user_id, answer_seq) -> DB_RESPONSE:
        obj = self.make_default_obj(search_id, user_id, answer_seq)
        self.collection.insert_one(obj)
        return DB_RESPONSE.success()


class Log_DB_Handler(DB_Handler):

    class LOG_TYPE(Enum):
        SAVE_COURSE = 'save_course'
        SAVE_PATHWAY = 'save_pathway'
        SAVE_SURVEY = 'save_survey'
        SEARCH = 'search'

    def __init__(self):
        super().__init__('logs')

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, user_id, log_type):
        default_item = super().make_default_obj()
        default_item['search_id'] = search_id
        default_item['user_id'] = user_id
        default_item['log_type'] = log_type.value
        default_item['date'] = datetime.now()
        return default_item

    def make_save_course_log(self, search_id, user_id, course_name):
        obj = self.make_default_obj(search_id, user_id, Log_DB_Handler.LOG_TYPE.SAVE_COURSE)
        obj['saved_course_name'] = course_name
        return obj

    def make_save_pathway_log(self, search_id, user_id, pathway_id):
        obj = self.make_default_obj(search_id, user_id, Log_DB_Handler.LOG_TYPE.SAVE_PATHWAY)
        obj['saved_pathway_id'] = pathway_id
        return obj

    def make_save_survey_log(self, search_id, user_id):
        return self.make_default_obj(search_id, user_id, Log_DB_Handler.LOG_TYPE.SAVE_SURVEY)

    def make_search_log(self, search_id, user_id):
        return self.make_default_obj(search_id, user_id, Log_DB_Handler.LOG_TYPE.SEARCH)

    def insert_one_log(self, search_id, user_id, log_type, **kargs):
        if log_type == 'search':
            self.collection.insert_one(self.make_search_log(search_id, user_id))
            return DB_RESPONSE(successOrNot=True)
        elif log_type == 'save_course':
            self.collection.insert_one(self.make_save_course_log(search_id, user_id, kargs['course_name']))
            return DB_RESPONSE(successOrNot=True)
        elif log_type == 'save_pathway':
            self.collection.insert_one(self.make_save_pathway_log(search_id, user_id, kargs['pathway_id']))
            return DB_RESPONSE(successOrNot=True)
        elif log_type == 'save_survey':
            self.collection.insert_one(self.make_save_survey_log(search_id, user_id))
            return DB_RESPONSE(successOrNot=True)
        else:
            return DB_RESPONSE.unsupported_operation(log_type)


class User_DB_Handler(DB_Handler):

    def __init__(self):
        super().__init__('user-data')

    def reset_collection(self):
        super().reset_collection()
        super().reset_index([
            ('user_id', pymongo.ASCENDING)
        ])

    def make_default_obj(self, old_user_id, new_user_id, full_name, affiliation):
        default_item = super().make_default_obj()
        default_item['user_id'] = old_user_id
        default_item['new_user_id'] = new_user_id
        default_item['saved_course_names'] = []
        default_item['saved_pathway_ids_to_names'] = {}
        default_item['closed_survey'] = False
        default_item['full_name'] = full_name
        default_item['interacted_pathway_ids'] = {}
        default_item['number_of_dashboard_visits'] = 0
        default_item['affiliation'] = affiliation
        return default_item

    def get_user_full_name(self, user_id) -> DB_RESPONSE: 
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        else:
            return DB_RESPONSE.success(value=user_entry['full_name'] if 'full_name' in user_entry else "")

    def initialize_user_if_not_exists(self, old_user_id, new_user_id, full_name, affiliation) -> DB_RESPONSE:
        if self.collection.find_one({"user_id": old_user_id}) is None:
            self.collection.insert_one(self.make_default_obj(old_user_id, new_user_id, full_name, affiliation))
            return DB_RESPONSE.success(value=False)
        elif 'full_name' not in self.collection.find_one({"user_id": old_user_id}): 
            self.collection.find_one_and_update(
            {"user_id": old_user_id},
            {"$set": {"full_name": (full_name), "affiliation": affiliation}}
            )
            return DB_RESPONSE.success(value=True)
        else:
            return DB_RESPONSE.success(value=True)

    def get_all_pathway_ids_for_user(self, user_id) -> DB_RESPONSE:
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        elif 'saved_pathway_ids_to_names' not in user_entry:
            return DB_RESPONSE.errors(f"saved_pathway_ids_to_names didn't exist in user_entry for user {user_id}")
        else:
            return DB_RESPONSE.success(value=user_entry['saved_pathway_ids_to_names'])

    def get_all_course_names_for_user(self, user_id) -> DB_RESPONSE:
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        else:
            return DB_RESPONSE.success(value=user_entry['saved_course_names'])

    def get_number_of_dashboard_visits(self, user_id) -> DB_RESPONSE:
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        elif 'number_of_dashboard_visits' not in user_entry:
            self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": {"number_of_dashboard_visits": 0}}
                )
            return DB_RESPONSE.success(value=0)
        else:
            return DB_RESPONSE.success(value=user_entry['number_of_dashboard_visits'])
    
    def increment_number_of_dashboard_visits(self, user_id) -> DB_RESPONSE:
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        elif 'number_of_dashboard_visits' not in user_entry:
            self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": {"number_of_dashboard_visits": 1}}
                )
            return DB_RESPONSE.success(value=1)
        else:
            self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$inc": {"number_of_dashboard_visits": 1}}
            )
            return DB_RESPONSE.success(value=self.collection.find_one({"user_id": user_id})['number_of_dashboard_visits'])

    def remove_one_course_for_user(self, user_id, course_name) -> DB_RESPONSE:
        self.collection.update_many(
            {"user_id": user_id},
            {"$pull": {"saved_course_names": { "course_name": course_name } }}
        )
        return DB_RESPONSE.success()

    def remove_one_pathway_for_user(self, user_id, pathway_id, name) -> DB_RESPONSE:
        self.collection.find_one_and_update(
            {"user_id": user_id},
            {"$unset": {"saved_pathway_ids_to_names." + pathway_id: name}}
        )
        return DB_RESPONSE.success()

    def add_one_course_for_user(self, user_id, search_id, course_name) -> DB_RESPONSE:
        self.collection.find_one_and_update(
            {"user_id": user_id, 'saved_course_names.course_name': {"$ne": course_name}},
            {"$addToSet": {"saved_course_names": {"course_name": course_name, "search_id": search_id, "date": datetime.now()}}}
        )
        return DB_RESPONSE.success()

    def add_one_pathway_for_user(self, user_id, name, search_id, pathway_id) -> DB_RESPONSE:
        pathway = self.collection.find_one({"user_id": user_id, "saved_pathway_ids_to_names." + pathway_id:{"$exists":True}})
        if pathway is None:
            self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": {"saved_pathway_ids_to_names." + pathway_id: {"name": name, "search_id": search_id, "date": datetime.now()}}}
            )
            return DB_RESPONSE.success(value="success")
        else:
            self.collection.find_one_and_update(
                {"user_id": user_id},
                [{"$set": {"saved_pathway_ids_to_names." + pathway_id: {"name": name}}}]
            )
            return DB_RESPONSE.success(value="already exists")

    def close_survey_for_user(self, user_id) -> DB_RESPONSE:
        self.collection.find_one_and_update(
            {"user_id": user_id},
            {"$set": {"closed_survey": True}}
        )
        return DB_RESPONSE.success()

    def add_pathway_interaction(self, user_id, pathway_id) -> DB_RESPONSE:
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        else:
            new_user_entry = self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": {"interacted_pathway_ids." + pathway_id: datetime.now()}},
                return_document=ReturnDocument.AFTER
            )
            return DB_RESPONSE.success(value=len(new_user_entry["interacted_pathway_ids"]))


    def get_number_of_pathway_interactions(self, user_id) -> DB_RESPONSE:
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        elif 'interacted_pathway_ids' not in user_entry:
            self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": {"interacted_pathway_ids": {}}}
                )
            return DB_RESPONSE.success(value=0)
        else:
            return DB_RESPONSE.success(value=len(user_entry["interacted_pathway_ids"]))
                 

class User_Interaction_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('user-interaction-data')

    def is_survey_closed_for_user(self, user_id) -> DB_RESPONSE:
        user_entry = self.collection.find_one({"user_id": user_id})
        if user_entry is None:
            return DB_RESPONSE.errors(f'user {user_id} does not exist')
        else:
            return DB_RESPONSE.success(value=user_entry['closed_survey'])


class User_Interaction_Course_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('user-interaction-course-data')

    
    def reset_collection(self):
        super().reset_collection()
        super().reset_index([
            ('search_id', pymongo.DESCENDING),
            ('user_id', pymongo.ASCENDING)
        ])

    def make_default_obj(self, search_id, user_id, course_name, pathway_id, pathway_pos_idx):
        default_item = super().make_default_obj()
        default_item['search_id'] = search_id
        default_item['user_id'] = user_id
        default_item['course_code'] = course_name
        default_item['pathway_id'] = pathway_id
        default_item['pathway_pos_idx'] = pathway_pos_idx
        default_item['date'] = datetime.now()
        return default_item

    def insert_interaction(self, search_id, user_id, course_name, pathway_id, vis_pos_idx):
        self.collection.insert_one(self.make_default_obj(search_id, user_id, course_name, pathway_id, vis_pos_idx))
        return DB_RESPONSE.success()


class User_Interaction_Pathway_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('user-interaction-pathway-data')
    
    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, search_id, user_id, pathway_id, vis_pos_idx):
        default_item = super().make_default_obj()
        default_item['search_id'] = search_id
        default_item['user_id'] = user_id
        default_item['pathway_id'] = pathway_id
        default_item['vis_pos_idx'] = vis_pos_idx
        default_item['date'] = datetime.now()
        return default_item

    def insert_interaction(self, search_id, user_id, pathway_id, vis_pos_idx):
        self.collection.insert_one(self.make_default_obj(search_id, user_id, pathway_id, vis_pos_idx))
        return DB_RESPONSE.success()


class Feedback_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('feedback-data')
    
    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, user_id, feedback):
        default_item = super().make_default_obj()
        default_item['user_id'] = user_id
        default_item['feedback'] = feedback
        default_item['date'] = datetime.now()
        return default_item

    def insert_feedback(self, user_id, feedback):
        self.collection.insert_one(self.make_default_obj(user_id, feedback))
        return DB_RESPONSE.success()


class Dashboard_Log_DB_Handler(DB_Handler):
    def __init__(self):
        super().__init__('dashboard')
    
    def reset_collection(self):
        super().reset_collection()
        super().reset_index([('user_id', pymongo.ASCENDING)])

    def make_default_obj(self, user_id, action, search_id, pathway_id, visualization_position_index, course_name):
        default_item = super().make_default_obj()
        default_item['user_id'] = user_id
        #"SAVE PATHWAY", "UNSAVE PATHWAY", "SAVE COURSE", "UNSAVE COURSE", "UNSAVE HISTORY", "INTERACT PATHWAY", "INTERACT COURSE", "INTERACT COURSE IN PATHWAY"
        default_item['action'] = action
        default_item['search_id'] = search_id
        default_item['pathway_id'] = pathway_id
        default_item['visualization_position_index'] = visualization_position_index
        default_item['course_code'] = course_name
        default_item['date'] = datetime.now()
        return default_item

    def add_action_to_log(self, user_id, action, search_id, pathway_id, visualization_position_index, course_name):
        self.collection.insert_one(self.make_default_obj(user_id, action, search_id, pathway_id, visualization_position_index, course_name))
        return DB_RESPONSE.success()

# simplified singleton pattern
user_DB_Handler = User_DB_Handler()
course_DB_Handler = Course_DB_Handler()
pathway_DB_Handler = Pathway_DB_Handler()
survey_DB_Handler = Survey_DB_Handler()
calibration_DB_Handler = Calibration_DB_Handler()
visualization_DB_Handler = Visualization_DB_Handler()
search_id_DB_Handler = Search_ID_Handler()
log_DB_Handler = Log_DB_Handler()
user_interaction_course_DB_Handler = User_Interaction_Course_DB_Handler()
user_interaction_pathway_DB_Handler = User_Interaction_Pathway_DB_Handler()
feedback_DB_Handler = Feedback_DB_Handler()
dashboard_log_DB_Handler = Dashboard_Log_DB_Handler()
saved_pathway_DB_Handler = Saved_Pathway_DB_Handler()
search_db_handler = Search_DB_Handler()