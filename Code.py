import requests
from requests.auth import HTTPBasicAuth

# Config
JIRA_DOMAIN = "your-domain.atlassian.net"
EMAIL = "your-email@example.com"
API_TOKEN = "your-api-token"
PROJECT_KEY = "ABC"  # Your specific project
FIX_VERSION_NAME = "1.0.0"

BASE_URL = f"https://{JIRA_DOMAIN}"
AUTH = HTTPBasicAuth(EMAIL, API_TOKEN)
HEADERS = {"Accept": "application/json"}

def search_issues_by_fix_version(project_key, fix_version):
    jql = f'project = "{project_key}" AND fixVersion = "{fix_version}"'
    url = f"{BASE_URL}/rest/api/2/search"
    start_at = 0
    max_results = 50
    issues = []

    while True:
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
            "fields": "key,summary,status,assignee"
        }
        response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
        response.raise_for_status()
        data = response.json()
        issues.extend(data["issues"])
        if start_at + max_results >= data["total"]:
            break
        start_at += max_results

    return issues

# Run
issues = search_issues_by_fix_version(PROJECT_KEY, FIX_VERSION_NAME)

# Output
print(f"Found {len(issues)} issues in project '{PROJECT_KEY}' with Fix Version '{FIX_VERSION_NAME}':")
for issue in issues:
    key = issue["key"]
    summary = issue["fields"]["summary"]
    status = issue["fields"]["status"]["name"]
    assignee = issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned"
    print(f"{key}: {summary} | Status: {status} | Assignee: {assignee}")
