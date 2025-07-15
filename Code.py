import os
import requests
from playwright.sync_api import sync_playwright


class TachyonPlaywrightClient:
    def __init__(self, playground_url):
        self.playground_url = playground_url

    def get_response(self, prompt: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.playground_url)

            # Wait for input box and paste the prompt
            page.fill("textarea", prompt)
            page.click("button:has-text('Run')")

            # Wait for response to appear
            page.wait_for_selector(".output", timeout=30000)
            output = page.query_selector(".output").inner_text()

            browser.close()
            return output.strip()


class ConfluenceFetcher:
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.auth_token = auth_token

    def fetch_docs_by_cql(self, cql: str) -> list:
        url = f"{self.base_url}/rest/api/content/search"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/json"
        }
        params = {
            "cql": cql,
            "expand": "body.storage"
        }

        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()

        pages = []
        for page in data.get("results", []):
            title = page.get("title", "")
            html = page.get("body", {}).get("storage", {}).get("value", "")
            clean_text = self._strip_html_tags(html)
            pages.append((title, clean_text))

        return pages

    @staticmethod
    def _strip_html_tags(html):
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, "html.parser").get_text()


class ConfluenceTachyonQuerySystem:
    def __init__(self, tachyon_url, confluence_url, confluence_token):
        self.tachyon = TachyonPlaywrightClient(tachyon_url)
        self.confluence = ConfluenceFetcher(confluence_url, confluence_token)

    def handle_query(self, user_query: str, save_txt_path="context.txt"):
        print("→ Asking Tachyon to generate CQL...")
        cql_prompt = f"Convert this user query into a CQL to search Confluence:\n\n{user_query}"
        cql = self.tachyon.get_response(cql_prompt)

        print(f"→ CQL received: {cql}")
        docs = self.confluence.fetch_docs_by_cql(cql)

        print(f"→ Saving {len(docs)} relevant documents to {save_txt_path}")
        with open(save_txt_path, "w", encoding="utf-8") as f:
            for title, text in docs:
                f.write(f"# {title}\n{text}\n\n")

        print("→ Asking Tachyon to answer the question using these docs...")
        with open(save_txt_path, "r", encoding="utf-8") as f:
            context = f.read()

        final_prompt = f"Use the following documentation to answer this question:\n\nQuestion: {user_query}\n\nDocuments:\n{context}"
        answer = self.tachyon.get_response(final_prompt)
        return answer


# --- Example usage ---
if __name__ == "__main__":
    TACHYON_URL = "http://localhost:3000/playground"   # Adjust if hosted elsewhere
    CONFLUENCE_URL = "https://your-domain.atlassian.net/wiki"
    CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

    system = ConfluenceTachyonQuerySystem(TACHYON_URL, CONFLUENCE_URL, CONFLUENCE_TOKEN)
    user_query = input("Ask your question: ")
    response = system.handle_query(user_query)
    print("\n🎯 Final Answer:\n", response)
