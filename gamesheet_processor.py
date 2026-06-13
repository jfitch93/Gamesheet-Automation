"""
WRHL Gamesheet Processor
Phase 1: Connect to Front and list recent conversations in the WRHL Game Operations inbox.
"""

import os
import sys
import requests
from datetime import datetime

# --- Configuration ---
FRONT_API_KEY = os.environ.get("FRONT_API_KEY")
INBOX_ID = "inb_bb3is"
CHANNEL_ADDRESS = "gamesheets@winnipegrechockeyleague.com"

TAG_VERIFIED = "tag_4c3lp0"       # gs-verified
TAG_NEEDS_REVIEW = "tag_4c3lqs"   # gs-needs-review
TAG_DISCIPLINARY = "tag_4c3lsk"   # gs-disciplinary

FRONT_API_BASE = "https://api2.frontapp.com"

HEADERS = {
    "Authorization": f"Bearer {FRONT_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def check_auth():
    """Verify the API key works by fetching account info."""
    resp = requests.get(f"{FRONT_API_BASE}/me", headers=HEADERS)
    if resp.status_code == 401:
        print("ERROR: Invalid or missing FRONT_API_KEY.")
        sys.exit(1)
    resp.raise_for_status()
    me = resp.json()
    print(f"Authenticated as: {me.get('email')} ({me.get('first_name')} {me.get('last_name')})\n")


def list_inbox_conversations(limit=25):
    """
    Fetch recent conversations from the WRHL Game Operations inbox.
    Returns a list of conversation dicts.
    """
    url = f"{FRONT_API_BASE}/inboxes/{INBOX_ID}/conversations"
    params = {
        "limit": limit,
        "sort_by": "date",
        "sort_order": "desc",
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("_results", [])


def get_untagged_conversations(conversations):
    """Filter to conversations that have no tags applied."""
    untagged = []
    for conv in conversations:
        tags = conv.get("tags", [])
        if not tags:
            untagged.append(conv)
    return untagged


def format_conversation(conv):
    """Return a readable summary line for a conversation."""
    conv_id = conv.get("id", "?")
    subject = conv.get("subject") or "(no subject)"
    status = conv.get("status", "?")
    tags = [t.get("name", "") for t in conv.get("tags", [])]
    tag_str = ", ".join(tags) if tags else "none"

    # Timestamp
    ts = conv.get("created_at")
    if ts:
        dt = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M UTC")
    else:
        dt = "unknown"

    return (
        f"  ID:      {conv_id}\n"
        f"  Subject: {subject}\n"
        f"  Status:  {status}\n"
        f"  Tags:    {tag_str}\n"
        f"  Created: {dt}\n"
    )


def main():
    if not FRONT_API_KEY:
        print("ERROR: FRONT_API_KEY environment variable is not set.")
        sys.exit(1)

    print("=== WRHL Gamesheet Processor ===\n")

    # Step 1: Verify auth
    check_auth()

    # Step 2: Fetch recent conversations
    print(f"Fetching recent conversations from inbox {INBOX_ID} ({CHANNEL_ADDRESS})...\n")
    conversations = list_inbox_conversations(limit=25)
    print(f"Found {len(conversations)} conversation(s) total.\n")

    if not conversations:
        print("No conversations found.")
        return

    # Step 3: Show all conversations
    print("--- All recent conversations ---")
    for conv in conversations:
        print(format_conversation(conv))

    # Step 4: Identify untagged ones (candidates for processing)
    untagged = get_untagged_conversations(conversations)
    print(f"\n--- Untagged conversations ({len(untagged)}) ---")
    if not untagged:
        print("  None — all conversations already have tags.")
    else:
        for conv in untagged:
            print(format_conversation(conv))


if __name__ == "__main__":
    main()
