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
        self.session = requests.Session() # this might help doing multiple requests after each other quicker, as they are done to the same server
 
    """
    Request data at endpoint given some parameters
    parameters is a dict
    """
    def request_data(self, endpoint, parameters=None):
        api_url_format = "{}/api/v1/{}"
        url = api_url_format.format(self.canvas_url, endpoint)

        api_key = self.api_key
        headers = {"Authorization": "Bearer {}".format(api_key)}
        response = self.session.get(url, headers=headers, params=parameters)
        return response.ok, response.json()

    def get_active_courses(self):
        endpoint = "courses"
        ok, courses_or_error = self.request_data(endpoint, {"per_page": 100, "enrollment_state": "active"})
        return ok, courses_or_error

    def get_announcements_for_course(self, course_id):
        endpoint = "courses/{}/discussion_topics".format(course_id)
        parameters = {"per_page": "10", "only_announcements": "true"}
        ok, announcements_or_error = self.request_data(endpoint, parameters)
        return ok, announcements_or_error


    def get_announcements_after(self, datetime):
        ok, courses_or_error = self.get_active_courses()
        if not ok:
            error = courses_or_error
            return ok, error 
        courses = courses_or_error
        found_announcements = []
        for course in courses_or_error:
            ok, announcements_or_error = self.get_announcements_for_course(course["id"])
            if not ok:
                error = announcements_or_error
                return ok, error
            announcements = announcements_or_error
            for announcement in announcements:
                post_time = parser.parse(announcement["posted_at"])
                if (post_time > datetime):
                    found_announcements.append(announcement)
        return ok, found_announcements
