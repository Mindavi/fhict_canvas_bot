#!/usr/bin/env python3
import requests
import json
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def main():
    active_courses = get_stored_active_courses()
    for course in active_courses:
        course_name = course["name"] 
        print(course_name)
        course_id = course["id"]
        #announcements = get_announcements_for_course(course_id)
        announcements = get_stored_announcements()
        for announcement in announcements:
            author = announcement["author"]["display_name"]
            title = announcement["title"]
            message = strip_tags(announcement["message"])
            # TODO: remove html from message
            print("Author: {}\nTitle: {}\nMessage: {}".format(author, title, message))


def get_stored_active_courses():
    courses = read_json_file("data/active_courses_response.json")
    return courses


def get_stored_announcements():
    announcements = read_json_file("data/discussion_topic_announcements_response.json")
    return announcements


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
    courses = request_data(endpoint, ["per_page=100", "enrollment_state=active"])
    return courses


def retrieve_course_permissions(course_id):
    endpoint = "courses/{}".format(course_id)
    course_data = request_data(endpoint, {"include": ["permissions"]})
    return course_data["permissions"]


def read_json_file(file_name_location):
    with open(file_name_location, "r") as json_file:
        return json.load(json_file)


def get_announcements_for_course(course_id):
    endpoint = "courses/{}/discussion_topics".format(course_id)
    parameters = {"per_page": "10", "only_announcements": "true"}
    announcements = request_data(endpoint, parameters)
    return announcements


def get_announcements_for_courses(course_codes):
    endpoint = "announcements"
    
    course_codes_with_prefix = []
    for course_code in course_codes:
        course_codes_with_prefix.append("course_{}".format(course_code))

    parameters = {"context_codes": course_codes_with_prefix, "per_page": "100"}
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

