"""Local educational web-security challenge simulator.
This module intentionally uses synthetic targets and never sends requests to external hosts.
"""
CHALLENGES=[
 {"id":"WEB-01","title":"SQL Injection Concept","difficulty":"Beginner","goal":"Identify unsafe string concatenation in a synthetic login query.","hint":"Look for user input inserted directly into SQL.","fix":"Use parameterized queries."},
 {"id":"WEB-02","title":"Reflected XSS Concept","difficulty":"Beginner","goal":"Recognize unsanitized reflected input in a synthetic page.","hint":"Search for input rendered into HTML without output encoding.","fix":"Context-aware output encoding and input validation."},
 {"id":"WEB-03","title":"IDOR Concept","difficulty":"Intermediate","goal":"Identify an object identifier trusted without authorization checks.","hint":"Authentication is not authorization.","fix":"Enforce server-side object-level authorization."},
 {"id":"WEB-04","title":"Path Traversal Concept","difficulty":"Intermediate","goal":"Recognize a file path built directly from user input.","hint":"Think about ../ sequences.","fix":"Allowlist resource IDs and canonicalize paths."},
]
def get_challenges(): return CHALLENGES
