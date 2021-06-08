from openqa_bugfetcher.issues import BugzillaBaseIssue


class BugzillaKDEIssue(BugzillaBaseIssue):
    prefixes = {"kde"}
    disabled_assigne = "@kde.org"
    url = "https://bugs.kde.org/jsonrpc.cgi"
