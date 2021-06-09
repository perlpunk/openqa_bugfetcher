import html
import json
from collections import OrderedDict

import requests

from openqa_bugfetcher.issues import BaseIssue


class BugzillaIssue(BaseIssue):
    prefixes = {"boo", "bnc", "bsc"}

    def fetch(self, conf):
        issue_id = self.bugid.split("#")[1]
        if "user" in conf["bugzilla"]:

            def json_rpc_get(url, method, params):
                get_params = OrderedDict({"method": method, "params": json.dumps([params])})
                cred = conf["bugzilla"]
                return requests.get(url, params=get_params, auth=(cred["user"], cred["pass"]))

            url = "https://apibugzilla.suse.com/jsonrpc.cgi"

            req = json_rpc_get(url, "Bug.get", {"ids": [issue_id]})
            assert req.status_code != 401, "Wrong auth for Bugzilla"
            assert req.status_code != 403, "Insufficient permission to access this bug (or the API at all)"
            assert req.ok
            data = req.json()
            assert data, "Empty JSON Object"
            if data["error"] and data["error"]["code"] in (100, 101):
                self.existing = False
            elif data["error"] and data["error"]["code"] == 102:
                raise AssertionError("Insufficient permission to access this bug")
            else:
                bug = data["result"]["bugs"][0]
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
