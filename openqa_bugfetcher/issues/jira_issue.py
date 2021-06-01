#!/usr/bin/python3

from openqa_bugfetcher.issues import BaseIssue
import requests


class JiraIssue(BaseIssue):
    prefixes = {"jsc"}

    def fetch(self, conf):
        issue_id = self.bugid.split("#")[1]
        url = "https://jira.suse.com/rest/api/2/issue/%s" % issue_id
        a = conf["jira"]
        r = requests.get(url, auth=(a["user"], a["pass"]))
        if r.ok:
            j = r.json()["fields"]
            self.title = j["summary"]
            self.priority = j["priority"]["name"]
            self.status = j["status"]["name"]
            self.open = self.status not in ("Rejected", "Resolved", "Closed")
        else:
            assert r.status_code != 401, "Wrong auth for Jira"
            self.existing = False
