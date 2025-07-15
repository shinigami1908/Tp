import requests

class Llama3Router:
    def __init__(self, llama3_endpoint):
        self.llama3_endpoint = llama3_endpoint

    def classify(self, user_query: str) -> str:
        prompt = f"Classify the following query as either 'jira' or 'confluence':\n\n{user_query}"
        response = requests.post(self.llama3_endpoint, json={"prompt": prompt})
        return response.json()['text'].strip().lower()


class JiraProcessor:
    def __init__(self, jira_base_url, auth_token, llama3_endpoint):
        self.jira_base_url = jira_base_url
        self.auth_token = auth_token
        self.llama3_endpoint = llama3_endpoint

    def query(self, user_query: str):
        jql_prompt = f"Convert the following into a JQL query:\n\n{user_query}"
        jql = requests.post(self.llama3_endpoint, json={"prompt": jql_prompt}).json()['text'].strip()

        api_url = f"{self.jira_base_url}/rest/api/2/search"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.get(api_url, headers=headers, params={"jql": jql})
        issues = response.json()

        format_prompt = f"Format the following Jira issues into a summary:\n\n{issues}"
        summary = requests.post(self.llama3_endpoint, json={"prompt": format_prompt}).json()['text']
        return summary


class ConfluenceProcessor:
    def __init__(self, confluence_base_url, auth_token, solar_llm_endpoint):
        self.confluence_base_url = confluence_base_url
        self.auth_token = auth_token
        self.solar_llm_endpoint = solar_llm_endpoint

    def query(self, user_query: str):
        # Step 1: Convert to CQL
        cql = f'text~"{user_query}"'
        api_url = f"{self.confluence_base_url}/rest/api/content/search"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        params = {"cql": cql, "expand": "body.storage,version"}

        response = requests.get(api_url, headers=headers, params=params)
        pages = response.json().get("results", [])

        # Step 2: Loop through documents
        relevant_docs = {}
        for page in pages:
            content = page['body']['storage']['value']
            relevance_prompt = f"Does this document help answer the query: '{user_query}'?\n\n{content}\n\nReply yes or no."
            relevance = requests.post(self.solar_llm_endpoint, json={"prompt": relevance_prompt}).json()['text'].strip().lower()

            if 'yes' in relevance:
                relevant_docs[page['title']] = {
                    "url": f"{self.confluence_base_url}{page['_links']['webui']}",
                    "content": content
                }

        if not relevant_docs:
            return "No relevant documentation found."

        # Step 3: Pass to uncensored LLM
        context = "\n\n".join([doc["content"] for doc in relevant_docs.values()])
        final_prompt = f"Answer the query using the following documents:\n\n{context}\n\nQuery: {user_query}"
        response = requests.post(self.solar_llm_endpoint, json={"prompt": final_prompt})
        return response.json()['text']


class QueryHandler:
    def __init__(self, llama3_endpoint, jira_processor, confluence_processor):
        self.router = Llama3Router(llama3_endpoint)
        self.jira_processor = jira_processor
        self.confluence_processor = confluence_processor

    def handle_query(self, user_query: str):
        kind = self.router.classify(user_query)
        if kind == 'jira':
            return self.jira_processor.query(user_query)
        elif kind == 'confluence':
            return self.confluence_processor.query(user_query)
        else:
            return "Could not classify the query. Please try again."


# Example usage
if __name__ == "__main__":
    llama3_api = "http://localhost:8000/llama3"
    solar_api = "http://localhost:9000/solar"

    jira = JiraProcessor(
        jira_base_url="https://your-domain.atlassian.net",
        auth_token="JIRA_TOKEN",
        llama3_endpoint=llama3_api
    )

    confluence = ConfluenceProcessor(
        confluence_base_url="https://your-domain.atlassian.net/wiki",
        auth_token="CONFLUENCE_TOKEN",
        solar_llm_endpoint=solar_api
    )

    handler = QueryHandler(llama3_api, jira, confluence)
    query = input("Ask your question: ")
    print(handler.handle_query(query))
