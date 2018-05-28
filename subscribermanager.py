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
                is_comment = '#' in line
                if not is_comment and len(line) != 0 and line.lstrip('-').isdecimal():
                    subscribers.append(line)
            return subscribers


    def add_subscriber(self, subscriber):
        subscriber = str(subscriber)
        current_subscribers = self.read_subscribers()
        if subscriber in current_subscribers:
            return False
        current_subscribers.append(subscriber)
        with open(self.file_name, 'w') as subscriber_file:
            print("Current subscribers: {}".format(current_subscribers))
            subscribers_to_write = list(map(lambda x: "{}\n".format(x), current_subscribers))
            subscriber_file.writelines(subscribers_to_write)
            return True
        return False


    def delete_subscriber(self, subscriber):
        subscriber = str(subscriber)
        current_subscribers = self.read_subscribers()
        if subscriber not in current_subscribers:
            return False
        current_subscribers.remove(subscriber)
        with open(self.file_name, 'w') as subscriber_file:
            subscribers_to_write = list(map(lambda x: "{}\n".format(x), current_subscribers))
            subscriber_file.writelines(subscribers_to_write)
            return True
        return False

