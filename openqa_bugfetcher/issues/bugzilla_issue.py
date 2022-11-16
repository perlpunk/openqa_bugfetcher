import html
import json

import requests

from openqa_bugfetcher.issues import BaseIssue


# error codes:
# https://github.com/bugzilla/bugzilla/blob/master/Bugzilla/WebService/Constants.pm#L160


class BugzillaIssue(BaseIssue):
    prefixes = {"boo", "bnc", "bsc"}

    def fetch(self, conf):
        issue_id = self.bugid.split("#")[1]
        if "user" in conf["bugzilla"]:

            def rest_get_bug(issue_id):
                url = f"https://bugzilla.suse.com/rest/bug/{issue_id}"
                get_params = {}
                a = conf["bugzilla"]
                if a.get("api_key"):
                    get_params["api_key"] = a["api_key"]
                return requests.get(url, params=get_params)

            req = rest_get_bug(issue_id)
            assert req.status_code != 401, "Wrong auth for Bugzilla"
            assert req.status_code != 403, "Insufficient permission to access this bug (or the API at all)"
            assert req.ok, "Server Status != 200: %s" % req.text
            data = req.json()
            assert data, "Empty JSON Object"
            if data.get("error"):
                if data["code"] in (100, 101):
                    self.existing = False
                elif data["code"] in (102, 113):
                    raise AssertionError("Insufficient permission to access this bug")
                else:
                    raise AssertionError("Bugzilla Error %(code)i: %(message)s" % data)
            else:
                bug = data["bugs"][0]
                self.title = bug["summary"]
                self.priority = bug["priority"]
                self.assignee = bug["assigned_to"]
                self.assigned = not self.assignee.endswith("@forge.provo.novell.com")
                self.open = bug["is_open"]
                self.status = bug["status"]
                self.resolution = bug.get("resolution")
        else:
            # Workaround for bugzilla API unavailable from non-employee accounts
            url = "https://bugzilla.suse.com/show_bug.cgi?id=%s" % issue_id
            req = requests.get(url)
            title = req.text.split("<title>", 1)[1].split("</title>", 1)[0]
            assert title != "Access Denied", "Insufficient permission to access this bug"
            if title in ("Invalid Bug ID", "Search by bug number"):
                self.existing = False
            else:
                self.title = html.unescape(title.split("&ndash; ", 1)[1])
                self.status = req.text.split('static_bug_status">', 1)[1].split("\n")[0]
                self.open = self.status not in [
                    "RESOLVED",
                    "VERIFIED",
                    "CLOSED",
                    "REJECTED",
                ]
