#!/usr/bin/env python3
import json
import os
import sys
import textwrap
from datetime import datetime, timezone

import requests


NOTION_VERSION = "2022-06-28"


def log(message: str) -> None:
    print(f"[notion-sync] {message}")


def set_output(key: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as fh:
        fh.write(f"{key}={value}\n")


def read_doc_log(doc_path: str) -> str:
    if not os.path.exists(doc_path):
        log(f"{doc_path} 경로를 찾을 수 없어 스킵합니다.")
        return ""
    with open(doc_path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def to_paragraph_blocks(markdown_text: str) -> list[dict]:
    paragraphs = []
    for block in markdown_text.split("\n\n"):
        normalized = block.strip()
        if not normalized:
            continue
        paragraphs.append(normalized)

    if not paragraphs:
        paragraphs = [markdown_text.strip()]

    notion_blocks = []
    for para in paragraphs:
        for piece in textwrap.wrap(
            para, width=1800, replace_whitespace=False, drop_whitespace=False
        ):
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": piece},
                            }
                        ]
                    },
                }
            )
    return notion_blocks


def create_notion_page(
    token: str, database_id: str, title: str, markdown_text: str
) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title,
                        }
                    }
                ]
            }
        },
        "children": to_paragraph_blocks(markdown_text),
    }
    response = requests.post(
        "https://api.notion.com/v1/pages", headers=headers, data=json.dumps(payload)
    )
    if response.status_code >= 400:
        log(f"Notion API 오류: {response.status_code} {response.text}")
        response.raise_for_status()
    page_id = response.json().get("id", "")
    log(f"Notion 페이지 생성 성공 (id={page_id})")
    return page_id


def main() -> None:
    doc_path = os.environ.get("DOC_LOG_PATH", "DOC_LOG.md")
    notion_token = os.environ.get("NOTION_API_KEY")
    notion_db_id = os.environ.get("NOTION_DATABASE_ID")

    if not notion_token or not notion_db_id:
        log("NOTION_API_KEY 또는 NOTION_DATABASE_ID가 설정되지 않았습니다.")
        sys.exit(1)

    doc_text = read_doc_log(doc_path)
    if not doc_text:
        log("DOC_LOG.md 내용이 비어 있어 업로드를 생략합니다.")
        set_output("sync_performed", "false")
        return

    timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    title = f"DOC LOG - {timestamp}"

    create_notion_page(notion_token, notion_db_id, title, doc_text)
    set_output("sync_performed", "true")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log(f"예상치 못한 오류: {exc}")
        raise

