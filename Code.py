import os, json, hashlib
from atlassian import Confluence
from tachyon import TachyonClient, Document
from dotenv import load_dotenv

load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
TACHYON_API_KEY = os.getenv("TACHYON_API_KEY")

STATE_FILE = "sync/state.json"
os.makedirs("sync", exist_ok=True)

confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USERNAME,
    password=CONFLUENCE_API_TOKEN
)
tachyon = TachyonClient(api_key=TACHYON_API_KEY)


def load_state():
    return json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}

def save_state(state):
    json.dump(state, open(STATE_FILE, "w"), indent=2)

def clean_html(html):
    import re
    return re.sub('<[^<]+?>', '', html)

def hash_content(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()

def sync_confluence():
    state = load_state()
    updated = {}

    pages = confluence.get_all_pages_from_space(SPACE_KEY, start=0, limit=1000, status='current')
    updated_docs = []

    for page in pages:
        pid = page["id"]
        title = page["title"]
        updated_at = page["version"]["when"]
        previous = state.get(pid, {})

        if previous and previous["last_updated"] == updated_at:
            updated[pid] = previous
            continue

        full = confluence.get_page_by_id(pid, expand="body.storage")
        html = full["body"]["storage"]["value"]
        text = clean_html(html)
        content_hash = hash_content(text)

        if previous and previous["hash"] == content_hash:
            updated[pid] = previous
            continue

        url = f"{CONFLUENCE_URL}{page['_links']['webui']}"
        doc = Document(
            content=text,
            metadata={
                "title": title,
                "url": url,
                "page_id": pid,
                "last_updated": updated_at
            }
        )
        updated_docs.append(doc)

        updated[pid] = {
            "last_updated": updated_at,
            "hash": content_hash
        }

    if updated_docs:
        print(f"Uploading {len(updated_docs)} updated documents...")
        tachyon.upload_documents(updated_docs)
    else:
        print("No changes detected.")

    save_state(updated)







from tachyon import TachyonClient
from dotenv import load_dotenv
import os

load_dotenv()
client = TachyonClient(api_key=os.getenv("TACHYON_API_KEY"))

def ask_question(question: str):
    response = client.query(question, top_k=5)
    answer = response.generated_answer
    sources = [
        {"title": doc.metadata.get("title"), "url": doc.metadata.get("url")}
        for doc in response.source_documents
    ]
    return {
        "answer": answer,
        "sources": sources
    }





from sync.confluence_sync import sync_confluence
from tachyon.query_engine import ask_question

# 1. Run sync
sync_confluence()

# 2. Ask a question
query = "How do I configure VPN access?"
result = ask_question(query)

print("Answer:")
print(result["answer"])
print("\nSources:")
for src in result["sources"]:
    print(f"- {src['title']}: {src['url']}")




