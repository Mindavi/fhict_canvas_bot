#!/usr/bin/env python3
import canvas
import datetime


def main():
    client = canvas.Canvas("https://fhict.instructure.com", read_api_key())

    previous_day = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5)
    announcements = client.get_announcements_after(previous_day)

    for announcement in announcements:
        title = announcement["title"]
        author = announcement["author"]["display_name"]
        post_time = announcement["posted_at"]
        message = announcement["message"]
        print(announcement)
        print("title: {}\n\tpost time: {}\n\tauthor: {} \n\tmessage: {}".format(title, post_time, author, message))


def read_api_key():
    with open("api-key.txt", "r") as api_key_file:
        api_key = api_key_file.readline().strip()
        return api_key


if __name__ == "__main__":
    main()
