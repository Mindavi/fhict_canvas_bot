#!/usr/bin/env python3
import requests
import json


def main():
    active_courses = get_active_courses()
    for course in active_courses:
        print(course['name'])
    active_course_ids = get_active_course_ids(active_courses)
    print(active_course_ids)
    announcements = get_announcements_for_courses(active_course_ids[0:7])
    print(announcements)


def read_api_key():
    with open("api-key.txt", "r") as api_key_file:
        api_key = api_key_file.readline().strip()
        return api_key


def get_active_course_ids(active_courses):
    course_ids = []
    for course in active_courses:
        course_ids.append(course['id'])
    return course_ids


def get_active_courses():
    endpoint = "courses"
    courses = read_json_file("data/active_courses_response.json")
    # courses = request_data(endpoint, ["per_page=100", "enrollment_state=active"])
    return courses


def retrieve_course_permissions(course_id):
    endpoint = "courses/{}".format(course_id)
    course_data = request_data(endpoint, {"include": ["permissions"]})
    return course_data["permissions"]


def read_json_file(file_name_location):
    with open(file_name_location, "r") as json_file:
        return json.load(json_file)


def get_announcements_for_courses(course_codes):
    endpoint = "announcements"
    
    course_codes_with_prefix = []
    for course_code in course_codes:
        course_codes_with_prefix.append("course_{}".format(course_code))

    parameters = {"context_codes": course_codes_with_prefix, "per_page": 100}
    print(parameters)
    announcements = request_data(endpoint, parameters)
    return announcements


def request_data(endpoint, parameters=None):
    api_url_format = "https://fhict.instructure.com/api/v1/{}"
    url = api_url_format.format(endpoint)

    api_key = read_api_key()
    headers = {"Authorization": "Bearer {}".format(api_key)}
    response = requests.get(url, headers=headers, params=parameters)
    # TODO: error handling (e.g. response.status_code)
    # print(response.headers)
    return response.json()


if __name__ == "__main__":
    main()

