#!/usr/bin/python3

from openqa_bugfetcher.issues import BaseIssue
from collections import OrderedDict
import requests
import json
import html

class BugzillaIssue(BaseIssue):
    prefixes = {'boo', 'bnc', 'bsc'}

    def fetch(self, conf):
        issue_id = self.bugid.split('#')[1]
        if 'user' in conf['bugzilla']:
            def json_rpc_get(url, method, params):
                get_params = OrderedDict({'method': method, 'params': json.dumps([params])})
                a = conf['bugzilla']
                return requests.get(url, params=get_params, auth=(a['user'], a['pass']))
            url = 'https://apibugzilla.suse.com/jsonrpc.cgi'

            r = json_rpc_get(url, 'Bug.get', {"ids": [issue_id]})
            assert r.status_code != 401, "Wrong auth for Bugzilla"
            assert r.status_code != 403, "Insufficient permission to access this bug (or the API at all)"
            assert r.ok
            j = r.json()
            assert j, "Empty JSON Object"
            if j['error'] and j['error']['code'] == 101:
                self.existing = False
            elif j['error'] and j['error']['code'] == 102:
                raise AssertionError("Insufficient permission to access this bug")
            else:
                b = j['result']['bugs'][0]
                self.title = b['summary']
                self.priority = b['priority']
                self.assignee = b['assigned_to']
                self.assigned = not self.assignee.endswith('@forge.provo.novell.com')
                self.open = b['is_open']
                self.status = b['status']
                self.resolution = b.get('resolution')
        else:
            # Workaround for bugzilla API unavailable from non-employee accounts
            url = "https://bugzilla.suse.com/show_bug.cgi?id=%s" % issue_id
            r = requests.get(url)
            title = r.text.split('<title>', 1)[1].split('</title>', 1)[0]
            assert title != "Access Denied", "Insufficient permission to access this bug"
            if title == "Invalid Bug ID" or title == "Search by bug number":
                self.existing = False
            else:
                self.title = html.unescape(title.split('&ndash; ', 1)[1])
                self.status = r.text.split('static_bug_status">', 1)[1].split("\n")[0]
                self.open = (self.status not in ['RESOLVED', 'VERIFIED', 'CLOSED', 'REJECTED'])
