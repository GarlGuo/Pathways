from database_accessor import *


user_DB_Handler.client.drop_database("pathways-db")
user_DB_Handler.reset_collection()
survey_DB_Handler.reset_collection()
calibration_DB_Handler.reset_collection()
visualization_DB_Handler.reset_collection()
log_DB_Handler.reset_collection()
search_id_DB_Handler.reset_collection()
dashboard_log_DB_Handler.reset_collection()
feedback_DB_Handler.reset_collection()
user_interaction_course_DB_Handler.reset_collection()
user_interaction_pathway_DB_Handler.reset_collection()