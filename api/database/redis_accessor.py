import redis
from database.response import Redis_RESPONSE


FIFTEEN_MIN_TO_SECONDS = 15 * 60

class Redis_Handler:

    client = redis.Redis(port=6379)  # singleton pattern

    def __init__(self, meta_category):
        super().__init__()
        self.meta_category = meta_category

    def clear_cache(self):
        self.client.flushdb()
        return Redis_RESPONSE.success()

    def make_real_key(self, key):
        return f'{self.meta_category}-{key}'

    def set_expire_time(self, key, time):
        real_key = self.make_real_key(key)
        self.client.expire(real_key, time)
        return Redis_RESPONSE.success()

    def remove_key(self, key) -> None:
        self.client.delete(self.make_real_key(key))
        return Redis_RESPONSE.success()

    def put_key(self, key, value,
                will_expire=True, sec_to_expire=FIFTEEN_MIN_TO_SECONDS):
        if will_expire:
            self.client.set(self.make_real_key(key), value, ex=sec_to_expire)
        else:
            # strongly discourage its usage due to memory constraint
            self.client.set(self.make_real_key(key), value)
        return Redis_RESPONSE.success()

    def get_key(self, key):
        res = self.client.get(self.make_real_key(key))
        if res is None:
            return Redis_RESPONSE.unfound()
        else:
            return Redis_RESPONSE.success(value=res.decode('utf-8'))

    def init_dict(self, key, dict,
                  will_expire=True, sec_to_expire=FIFTEEN_MIN_TO_SECONDS):
        real_key = self.make_real_key(key)
        self.client.hmset(real_key, dict)
        if will_expire:
            self.client.expire(real_key, sec_to_expire)
        return Redis_RESPONSE.success()

    def retrieve_dict(self, key):
        real_key = self.make_real_key(key)
        result = self.client.hgetall(real_key)
        if len(result) > 0:
            return Redis_RESPONSE.success(value=result)
        return Redis_RESPONSE.unfound()

    def init_list(self, key, value_list,
                  will_expire=True, sec_to_expire=FIFTEEN_MIN_TO_SECONDS):
        real_key = self.make_real_key(key)
        for i in value_list:
            self.client.rpush(real_key, i)
        if will_expire:
            self.client.expire(real_key, sec_to_expire)
        return Redis_RESPONSE.success()

    def get_element_from_list(self, key, idx_list) -> Redis_RESPONSE:
        if type(idx_list) == int:
            return Redis_RESPONSE.success(value=self.client.lindex(self.make_real_key(key), idx_list).decode('utf-8'))
        else:
            return Redis_RESPONSE.success(value=[self.client.lindex(self.make_real_key(key), i).decode('utf-8') for i in idx_list])

    def get_all_elements_from_list(self, key):
        res = self.client.lrange(self.make_real_key(key), 0, -1)
        return Redis_RESPONSE.success(value=[i.decode('utf-8') for i in res])

    def remove_list(self, key):
        self.remove_key(self.make_real_key(key))
        return Redis_RESPONSE.success()

    def soft_data_array(self, name, data_array, rewrite=False):
        if not rewrite:
            try:
                self.get_element_from_list(name, [0])
                # if it succeeds, we do not want to rewrite its key
                return Redis_RESPONSE.success(value=False)
            except:
                pass
        self.init_list(name, data_array)
        return Redis_RESPONSE.success(value=True)

    def array_is_exist(self, key, retrieve_all_data_if_exist=False):
        try:
            if retrieve_all_data_if_exist:
                res = self.get_all_elements_from_list(key).value
                if res != []:
                    return Redis_RESPONSE.success(value=(True, res))
                else:
                    return Redis_RESPONSE.success(value=(False, ))
            else:
                self.get_element_from_list(key, 0)
                return Redis_RESPONSE.success(value=(True,))
        except:
            return Redis_RESPONSE.success(value=(False,))


class TTL_Redis_Handler(Redis_Handler):
    def __init__(self):
        super().__init__("ttl")
    
    def save_ttl_key(self, key, time):
        self.put_key(key, time, sec_to_expire=time)
        return Redis_RESPONSE.success()
    
    def retrieve_ttl_key(self, key):
        result = self.get_key(key)
        if Redis_RESPONSE.is_unfound(result):
            return result
        return Redis_RESPONSE(value=int(result.value))


class Calibration_Redis_Handler(Redis_Handler):
    def __init__(self, ttl_redis_handler: TTL_Redis_Handler):
        super().__init__('calibration-handler')
        self.ttl_redis_handler = ttl_redis_handler

        FIFTEEN_MIN = 15 * 60
        HALF_HOUR = 30 * 60

        self.next_ttl_lookup = {i: i + 60 for i in range(FIFTEEN_MIN, HALF_HOUR, 60)}
        self.next_ttl_lookup[HALF_HOUR] = HALF_HOUR
        self.BASE_TIME = FIFTEEN_MIN


    # requires: R_map is a map with format [nonzero_idx: relevance_score]
    def save_none_zero_relevance_score(self, interest_keyword, R_map):  
        result = self.init_dict(interest_keyword, R_map)
        if result.is_successful():
            return self.ttl_redis_handler.save_ttl_key(interest_keyword, FIFTEEN_MIN_TO_SECONDS)
        return result
        
    def compute_next_ttl(self, current_ttl):
        return self.next_ttl_lookup.get(current_ttl) or 15 * 60 # default set to 15 minutes

    def retrieve_none_zero_relevance_score(self, interest_keyword): 
        result = self.retrieve_dict(interest_keyword)
        if Redis_RESPONSE.is_unfound(result):
            return result
        else:
            value = {int(idx): float(r) for idx, r in result.value.items()}
            ttl = self.ttl_redis_handler.retrieve_ttl_key(interest_keyword)
            if ttl.is_successful():
                next_ttl = self.compute_next_ttl(ttl.value)
            else:
                next_ttl = 15 * 60
            self.set_expire_time(interest_keyword, next_ttl)
            self.ttl_redis_handler.save_ttl_key(interest_keyword, next_ttl)
            return Redis_RESPONSE.success(value=value)
    


class Course_Redis_Handler(Redis_Handler):

    def __init__(self):
        super().__init__('course-array')

    def construct_course_name_key(self, query):
        return f'{query}-course-names'

    def construct_course_json_key(self, query):
        return f'{query}-course-json'

    def add_course_names_dict_string(self, query, course_names_dict_str):
        course_name_key = self.construct_course_name_key(query)
        return self.put_key(course_name_key, course_names_dict_str)

    def courses_names_dict_string_is_exist(self, query):
        course_name_key = self.construct_course_name_key(query)
        res = self.get_key(course_name_key)
        if res.is_successful():
            return Redis_RESPONSE.success(value=(True, res.value))
        else:
            return Redis_RESPONSE.success(value=(False,))

    def add_course_jsons_string(self, query, course_jsons):
        course_json_key = self.construct_course_json_key(query)
        return self.put_key(course_json_key, course_jsons)

    def get_course_jsons_string(self, query):
        course_json_key = self.construct_course_json_key(query)
        return self.get_key(course_json_key)

    def course_jsons_string_is_exist(self, query, retrieve_all_data_if_exist=False):
        course_json_key = self.construct_course_json_key(query)
        res = self.get_key(course_json_key)
        if res.is_successful():
            return Redis_RESPONSE.success(value=(True, res.value))
        else:
            return Redis_RESPONSE.success(value=(False,))


# course_Redis_Handler = Course_Redis_Handler()

# calibration_new_redis_handler.save_none_zero_relevance_score('key', {1:2.5, 3:4.5})
# print(calibration_new_redis_handler.retrieve_none_zero_relevance_score('key').value)
# print(calibration_new_redis_handler.retrieve_none_zero_relevance_score('key').value)
