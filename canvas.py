#!/usr/bin/env python3
import requests
from dateutil import parser

class Canvas:
    """
    canvas_url: the url your institution uses to access canvas
    (e.g.) https://canvas.instructure.com
    """
    def __init__(self, canvas_url, api_key):
        self.canvas_url = canvas_url
        self.api_key = api_key
 
    """
    Request data at endpoint given some parameters
    parameters is a dict
    """
    def request_data(self, endpoint, parameters=None):
        api_url_format = "{}/api/v1/{}"
        url = api_url_format.format(self.canvas_url, endpoint)

        api_key = self.api_key
        headers = {"Authorization": "Bearer {}".format(api_key)}
        response = requests.get(url, headers=headers, params=parameters)
        # TODO: error handling (e.g. response.status_code)
        return response.json()

    def get_active_courses(self):
        endpoint = "courses"
        courses = self.request_data(endpoint, {"per_page": 100, "enrollment_state": "active"})
        return courses

    def get_announcements_for_course(self, course_id):
        endpoint = "courses/{}/discussion_topics".format(course_id)
        parameters = {"per_page": "10", "only_announcements": "true"}
        announcements = self.request_data(endpoint, parameters)
        return announcements


    def get_announcements_after(self, datetime):
        courses = self.get_active_courses()
        found_announcements = []
        for course in courses:
            announcements = self.get_announcements_for_course(course["id"])
            for announcement in announcements:
                post_time = parser.parse(announcement["posted_at"])
                if (post_time > datetime):
                    found_announcements.append(announcement)
        return found_announcements
