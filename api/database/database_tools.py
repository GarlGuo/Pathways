from database_accessor import survey_DB_Handler, calibration_DB_Handler, visualization_DB_Handler
import datetime
from datetime import timedelta
from data_loader import GlobalData, remove_nonalphanumeric
from wordcloud import WordCloud


class DatabaseReporter:
    def __init__(self, data_loader, survey_DB_Handler, calibration_DB_Handler, pathway_DB_Handler) -> None:
        self.survey_DB_handler = survey_DB_Handler
        self.calibration_DB_handler = calibration_DB_Handler
        self.visualization_DB_handler = pathway_DB_Handler
        self.data_loader = data_loader
        self.word_cloud = WordCloud(background_color ='white', stopwords=data_loader.my_stop_words)

    def get_user_survey_date_slice(self, date):
        end = date + timedelta(days=1)
        return self.survey_DB_handler.collection.find({"date": {'$lt': end, '$gte': date}})

    def get_user_calibration_date_slice(self, date):
        end = date + timedelta(days=1)
        return self.calibration_DB_handler.collection.find({"date": {'$lt': end, '$gte': date}})

    def get_user_pathway_date_slice(self, date):
        end = date + timedelta(days=1)
        return self.visualization_DB_handler.collection.find({"date": {'$lt': end, '$gte': date}})

    def get_word_cloud(self, date):
        words = ""
        cursor = self.get_user_calibration_date_slice(date)
        for line in cursor:
            words += (" " + remove_nonalphanumeric(" ".join(line['interest_keywords']).lower()))
        return self.word_cloud.generate(words)

    def get_calibration_search_user_count_total_count(self, date):
        user_set = set()
        cursor = self.get_user_calibration_date_slice(date)
        for line in cursor:
            user_set.add(line['user_id'])
        return len(user_set), len(cursor)

    def get_calibration_search_top5_returned_courses(self, date):
        course_dict = dict()
        cursor = self.get_user_calibration_date_slice(date)
        for line in cursor:
            for c in line['calibration_course_list']:
                if c in course_dict:
                    course_dict[c] += 1
                else:
                    course_dict[c] = 1
        return {c: cnt for c, cnt in sorted(course_dict.items(), key=lambda c, cnt: (-cnt, c))[:min(len(course_dict), 5)]}


    def get_pathway_search_user_count_total_count(self, date):
        user_set = set()
        cursor = self.get_user_pathway_date_slice(date)
        for line in cursor:
            user_set.add(line['user_id'])
        return len(user_set), len(cursor)


    def get_pathway_search_top5_returned_pathways(self, date):
        pathway_dict = dict()
        cursor = self.get_user_pathway_date_slice(date)
        for line in cursor:
            for p in line['pathway_ids']:
                if p in pathway_dict:
                    pathway_dict[p] += 1
                else:
                    pathway_dict[p] = 1
        return {p: cnt for p, cnt in sorted(pathway_dict.items(), key=lambda c, cnt: (-cnt, c))[:min(len(pathway_dict), 5)]}


database_reporter = DatabaseReporter(GlobalData(), survey_DB_Handler, calibration_DB_Handler, visualization_DB_Handler)
