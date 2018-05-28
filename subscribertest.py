#!/usr/bin/env python3
import subscribermanager

manager = subscribermanager.SubscriberManager('subscribers.txt')
print(manager.read_subscribers())
