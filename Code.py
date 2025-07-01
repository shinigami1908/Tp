import os
import json
import hashlib
import gzip
from atlassian import Confluence
from dotenv import load_dotenv
from datetime import datetime

# === Load environment ===
load_dotenv()
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

STATE_FILE = "sync_state.json"
CUMULATIVE_FILE = "output/confluence_documents.jsonl"
COMPRESSED_FILE = CUMULATIVE_FILE + ".gz"

os.makedirs("output", exist_ok=True)

# === Confluence Client ===
confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USERNAME,
    password=CONFLUENCE_API_TOKEN
)


# === Utility Functions ===
def load_json(path):
    return json.load(open(path)) if os.path.exists(path) else {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def clean_html(html):
    import re
    return re.sub('<[^<]+?>', '', html)

def hash_content(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()


# === Main Sync Logic ===
def generate_cumulative_jsonl():
    state = load_json(STATE_FILE)          # tracks last_updated & hash
    cumulative = load_json(CUMULATIVE_FILE) if os.path.exists(CUMULATIVE_FILE) else {}

    updated_state = {}
    updated_docs = {}

    spaces = confluence.get_all_spaces(start=0, limit=1000, expand="description.plain")

    for space in spaces["results"]:
        space_key = space["key"]
        space_name = space["name"]
        print(f"\n📂 Scanning space: {space_key} - {space_name}")

        pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000, status='current')

        for page in pages:
            pid = page["id"]
            title = page["title"]
            updated_at = page["version"]["when"]
            url = f"{CONFLUENCE_URL}{page['_links']['webui']}"
            key = pid  # stable unique identifier

            prev = state.get(pid, {})

            if prev and prev["last_updated"] == updated_at:
                # unchanged → keep existing
                updated_docs[key] = cumulative.get(key)
                updated_state[pid] = prev
                continue

            full = confluence.get_page_by_id(pid, expand="body.storage")
            html = full["body"]["storage"]["value"]
            text = clean_html(html)
            content_hash = hash_content(text)

            if prev and prev.get("hash") == content_hash:
                updated_docs[key] = cumulative.get(key)
                updated_state[pid] = prev
                continue

            doc = {
                "content": text,
                "metadata": {
                    "title": title,
                    "url": url,
                    "space": space_key,
                    "page_id": pid,
                    "last_updated": updated_at
                }
            }

            updated_docs[key] = doc
            updated_state[pid] = {
                "last_updated": updated_at,
                "hash": content_hash
            }

    # Write cumulative .jsonl
    with open(CUMULATIVE_FILE, "w", encoding="utf-8") as f:
        for doc in updated_docs.values():
            if doc:  # skip None
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    # GZIP compress it
    with open(CUMULATIVE_FILE, "rb") as src, gzip.open(COMPRESSED_FILE, "wb") as dst:
        dst.writelines(src)

    save_json(STATE_FILE, updated_state)

    print(f"\n✅ Cumulative file written to {CUMULATIVE_FILE}")
    print(f"📦 Compressed to {COMPRESSED_FILE}")


if __name__ == "__main__":
    generate_cumulative_jsonl()
