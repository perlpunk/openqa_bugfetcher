from openqa_bugfetcher.issues import BugzillaBaseIssue


class BugzillaGnomeIssue(BugzillaBaseIssue):
    prefixes = {"bgo"}
    disabled_assigne = "@gnome.bugs"
    url = "https://bugzilla.gnome.org/jsonrpc.cgi"
