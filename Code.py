import imaplib
import email

# === CONFIGURATION ===
IMAP_SERVER = "outlook.office365.com"   # For Office 365 / Outlook.com
EMAIL_ACCOUNT = "your_email@outlook.com"
PASSWORD = "your_password"
SUBJECT_FILTER = "Invoice"

# Connect with Basic Auth
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_ACCOUNT, PASSWORD)
mail.select("inbox")

# Search emails matching subject
status, data = mail.search(None, f'(SUBJECT "{SUBJECT_FILTER}")')

if status == "OK":
    email_ids = data[0].split()
    print(f"Found {len(email_ids)} emails with subject containing '{SUBJECT_FILTER}'\n")

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        print("From:", msg["From"])
        print("Subject:", msg["Subject"])
        print("Date:", msg["Date"])
        print()
else:
    print("Search failed:", status)

mail.logout()
