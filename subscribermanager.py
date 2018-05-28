#!/usr/bin/env python3
class SubscriberManager:
    def __init__(self, file_name):
        self.file_name = file_name

    def read_subscribers(self):
        with open(self.file_name, 'r') as subscriber_file:
            subscribers = []
            lines = subscriber_file.readlines()
            for line in lines:
                line = line.strip()
                contains_comment = '#' in line
                if not contains_comment and len(line) != 0: 
                    subscribers.append(line)
            return subscribers
