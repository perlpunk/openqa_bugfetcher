#!/usr/bin/python3

from openqa_bugfetcher.issues import BaseIssue
import requests

class ProgressIssue(BaseIssue):
    prefixes = {'poo'}

    def fetch(self, conf):
        issue_id = self.bugid.split('#')[1]
        url = "https://progress.opensuse.org/issues/%s.json" % issue_id
        r = requests.get(url, headers={"X-Redmine-API-Key": conf['progress']['api_key']})
        if r.ok:
            j = r.json()['issue']
            self.title = j['subject']
            self.priority = j['priority']['name']
            self.assigned = 'assigned_to' in j
            self.assignee = j['assigned_to']['name'] if self.assigned else None
            self.open = 'closed_on' not in j
            self.status = j['status']['name']
        else:
            assert r.status_code != 401, "Wrong auth for Progress"
            self.existing = False
