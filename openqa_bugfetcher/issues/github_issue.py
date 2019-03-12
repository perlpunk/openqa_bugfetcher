#!/usr/bin/python3

from openqa_bugfetcher.issues import BaseIssue
import requests

class GitHubIssue(BaseIssue):
    prefixes = {'gh'}

    def fetch(self, conf):
        repo, issue_id = self.bugid.split('#')[1:]
        url = "https://api.github.com/repos/%s/issues/%s" % (repo, issue_id)
        r = requests.get(url, params=conf['github'])
        if r.ok:
            j = r.json()
            self.title = j['title']
            self.assigned = bool(j['assignee'])
            self.assignee = j['assignee']['login'] if self.assigned else None
            self.status = j['state']
            self.open = self.status != "closed"
        else:
            self.existing = False
