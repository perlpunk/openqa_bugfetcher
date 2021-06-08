#!/usr/bin/python3

import requests
from openqa_bugfetcher.issues import BaseIssue


class GitHubIssue(BaseIssue):
    prefixes = {"gh"}

    def fetch(self, conf):
        try:
            repo, issue_id = self.bugid.split("#")[1:]
            url = "https://api.github.com/repos/%s/issues/%s" % (repo, issue_id)
            auth = None
            if "client_id" in conf["github"] and "client_secret" in conf["github"]:
                auth = (conf["github"]["client_id"], conf["github"]["client_secret"])
            r = requests.get(url, auth=auth)
            assert r.status_code != 403, "Github ratelimiting"
            if r.ok:
                j = r.json()
                self.title = j["title"]
                self.assigned = bool(j["assignee"])
                self.assignee = j["assignee"]["login"] if self.assigned else None
                self.status = j["state"]
                self.open = self.status != "closed"
            else:
                self.existing = False
        except ValueError:
            self.existing = False
