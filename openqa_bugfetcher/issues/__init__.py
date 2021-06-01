#!/usr/bin/python3

import os
from importlib import import_module
import inspect


class BaseIssue(object):
    prefixes = set()

    def __init__(self, conf, bugid):
        self.bugid = bugid
        self.title = None
        self.priority = None
        self.assigned = False
        self.assignee = None
        self.open = False
        self.status = None
        self.resolution = None
        self.existing = True
        self.fetch(conf)

    def get_dict(self):
        return {
            "title": self.title,
            "priority": self.priority,
            "assigned": int(self.assigned),
            "assignee": self.assignee,
            "open": int(self.open),
            "status": self.status,
            "resolution": self.resolution,
            "existing": int(self.existing),
        }

    def fetch(self, conf):
        pass


class IssueFetcher(object):
    def __init__(self, conf):
        self.conf = conf
        self.prefix_table = {}
        for module in os.listdir(os.path.dirname(__file__)):
            if module == "__init__.py" or module[-3:] != ".py" or module == "__pycache__":
                continue
            m = import_module("openqa_bugfetcher.issues.%s" % module[:-3])
            for name, obj in inspect.getmembers(m):
                if inspect.isclass(obj) and issubclass(obj, BaseIssue) and obj is not BaseIssue:
                    for prefix in obj.prefixes:
                        self.prefix_table[prefix] = obj

    def get_issue(self, bugid):
        assert "#" in bugid, "Bad bugid format: %s" % bugid
        prefix = bugid.split("#")[0].lower()
        assert prefix in self.prefix_table, "No implementation found for %s" % bugid
        return self.prefix_table[prefix](self.conf, bugid)
