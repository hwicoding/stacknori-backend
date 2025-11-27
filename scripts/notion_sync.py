#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime, timezone

import requests


NOTION_VERSION = "2025-09-03"


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


def _rich_text(content: str) -> list[dict]:
    return [
        {
            "type": "text",
            "text": {"content": content},
        }
    ]


def _paragraph_block(content: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": _rich_text(content)},
    }


def _heading_block(level: int, content: str) -> dict:
    level = max(1, min(level, 3))
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": _rich_text(content)},
    }


def _list_block(block_type: str, content: str) -> dict:
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": _rich_text(content)},
    }


def _callout_block(content: str, icon: str = "💡", color: str = "default") -> dict:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": _rich_text(content),
            "icon": {"emoji": icon},
            "color": color,
        },
    }


def _divider_block() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def _todo_block(content: str, checked: bool) -> dict:
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {"checked": checked, "rich_text": _rich_text(content)},
    }


def _table_block(rows: list[list[str]], has_header: bool) -> dict:
    table_width = max((len(row) for row in rows), default=0)

    def _cells(row: list[str]) -> list[list[dict]]:
        padded = row + [""] * (table_width - len(row))
        return [[{"type": "text", "text": {"content": cell}}] for cell in padded]

    children = [
        {
            "object": "block",
            "type": "table_row",
            "table_row": {"cells": _cells(row)},
        }
        for row in rows
    ]

    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": has_header,
            "has_row_header": False,
            "children": children,
        },
    }


SECTION_MAP = {
    "0. 메타": "meta",
    "1. 작업 요약": "summary",
    "2. Troubleshooting & Decisions": "troubleshooting",
    "2. Troubleshooting": "troubleshooting",
    "3. 다음 액션": "next_actions",
}


def _extract_structured_sections(markdown_text: str) -> dict[str, list[str]]:
    sections = {value: [] for value in SECTION_MAP.values()}
    current_key: str | None = None
    heading_pattern = re.compile(r"^###\s+(.*)$")

    for line in markdown_text.splitlines():
        heading_match = heading_pattern.match(line.strip())
        if heading_match:
            mapped = SECTION_MAP.get(heading_match.group(1).strip())
            current_key = mapped
            continue
        if current_key:
            sections[current_key].append(line)

    if any(filter(None, sections.values())):
        return sections
    return {}


META_PATTERN = re.compile(r"^-\s*\*\*(.+?)\*\*:\s*(.+)$")


def _parse_meta_entries(lines: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in lines:
        match = META_PATTERN.match(line.strip())
        if match:
            entries.append((match.group(1).strip(), match.group(2).strip()))
    return entries


def _build_meta_blocks(lines: list[str]) -> tuple[list[dict], dict[str, str]]:
    entries = _parse_meta_entries(lines)
    if not entries:
        return [], {}
    rows = [["항목", "내용"]] + [[key, value] for key, value in entries]
    return [_table_block(rows, has_header=True)], {k: v for k, v in entries}


def _build_summary_blocks(lines: list[str]) -> list[dict]:
    highlights = []
    icons = ["🚀", "🛠️", "📌", "✅", "✨"]
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r"^[-*]\s*", "", stripped)
        if stripped:
            highlights.append(stripped)
    result: list[dict] = []
    for idx, text in enumerate(highlights):
        icon = icons[idx % len(icons)]
        result.append(_callout_block(text, icon, "gray_background"))
    return result


def _parse_markdown_table(lines: list[str]) -> tuple[list[list[str]], bool]:
    raw_rows = [line for line in lines if line.strip()]
    if not raw_rows:
        return []

    def is_separator(line: str) -> bool:
        segments = line.strip().strip("|").split("|")
        return all(set(seg.strip()) <= set(":-") and seg.strip() for seg in segments)

    parsed_rows = [
        [cell.strip() for cell in row.strip().strip("|").split("|")]
        for row in raw_rows
    ]
    if len(parsed_rows) >= 2 and is_separator(raw_rows[1]):
        parsed_rows.pop(1)
        has_header = True
    else:
        has_header = False
    return parsed_rows, has_header


def _build_troubleshooting_blocks(lines: list[str]) -> list[dict]:
    cleaned_lines = [line for line in lines if line.strip()]
    if not cleaned_lines:
        return []
    rows, has_header = _parse_markdown_table(cleaned_lines)
    if not rows:
        return []
    return [_table_block(rows, has_header)]


def _build_next_action_blocks(lines: list[str]) -> list[dict]:
    blocks: list[dict] = []
    todo_pattern = re.compile(r"^[-*]\s+\[(?P<checked>[ xX])\]\s+(?P<text>.+)$")
    for line in lines:
        match = todo_pattern.match(line.strip())
        if match:
            blocks.append(
                _todo_block(
                    match.group("text").strip(),
                    match.group("checked").lower() == "x",
                )
            )
    return blocks


def build_structured_doc_blocks(markdown_text: str) -> tuple[list[dict], dict[str, str]]:
    sections = _extract_structured_sections(markdown_text)
    if not sections:
        return [], {}

    blocks: list[dict] = []
    meta_blocks, meta_map = _build_meta_blocks(sections.get("meta", []))
    if meta_blocks:
        blocks.append(_heading_block(2, "0. 메타"))
        blocks.extend(meta_blocks)
        blocks.append(_divider_block())

    summary_blocks = _build_summary_blocks(sections.get("summary", []))
    if summary_blocks:
        blocks.append(_heading_block(2, "1. 작업 요약"))
        blocks.extend(summary_blocks)
        blocks.append(_divider_block())

    troubleshooting_blocks = _build_troubleshooting_blocks(
        sections.get("troubleshooting", [])
    )
    if troubleshooting_blocks:
        blocks.append(_heading_block(2, "2. Troubleshooting & Decisions"))
        blocks.extend(troubleshooting_blocks)
        blocks.append(_divider_block())

    next_action_blocks = _build_next_action_blocks(sections.get("next_actions", []))
    if next_action_blocks:
        blocks.append(_heading_block(2, "3. 다음 액션"))
        blocks.extend(next_action_blocks)
    # remove trailing divider if exists
    if blocks and blocks[-1].get("type") == "divider":
        blocks.pop()
    return blocks, meta_map


def to_notion_blocks(markdown_text: str) -> list[dict]:
    blocks: list[dict] = []
    paragraph_buffer: list[str] = []
    table_buffer: list[str] = []
    callout_buffer: list[str] = []
    callout_icon = "💡"
    callout_color = "default"

    todo_pattern = re.compile(r"^[-*]\s+\[(?P<checked>[ xX])\]\s+(?P<text>.+)$")
    callout_pattern = re.compile(
        r"^>\s*(?:\[\!(?P<label>[A-Z]+)\])?\s*(?P<text>.*)$", re.IGNORECASE
    )

    def callout_meta(label: str | None) -> tuple[str, str]:
        icon_map = {
            "INFO": ("ℹ️", "blue_background"),
            "TIP": ("💡", "yellow_background"),
            "SUCCESS": ("✅", "green_background"),
            "WARNING": ("⚠️", "orange_background"),
            "DANGER": ("⛔", "red_background"),
            "QUOTE": ("📝", "default"),
        }
        if not label:
            return "💬", "default"
        return icon_map.get(label.upper(), ("💬", "default"))

    def flush_paragraph() -> None:
        if not paragraph_buffer:
            return
        text = " ".join(paragraph_buffer).strip()
        if text:
            blocks.append(_paragraph_block(text))
        paragraph_buffer.clear()

    def flush_callout() -> None:
        nonlocal callout_buffer, callout_icon, callout_color
        if not callout_buffer:
            return
        text = " ".join(callout_buffer).strip()
        if text:
            blocks.append(_callout_block(text, callout_icon, callout_color))
        callout_buffer = []
        callout_icon, callout_color = "💡", "default"

    def flush_table() -> None:
        nonlocal table_buffer
        if not table_buffer:
            return

        def parse_row(line: str) -> list[str]:
            return [cell.strip() for cell in line.strip().strip("|").split("|")]

        def is_separator(line: str) -> bool:
            segments = line.strip().strip("|").split("|")
            return all(set(seg.strip()) <= set(":-") and seg.strip() for seg in segments)

        rows = [parse_row(line) for line in table_buffer if line.strip()]
        has_header = False
        if len(rows) >= 2 and is_separator(table_buffer[1]):
            has_header = True
            rows.pop(1)

        if rows:
            blocks.append(_table_block(rows, has_header))
        else:
            for line in table_buffer:
                paragraph_buffer.append(line.strip())
            flush_paragraph()

        table_buffer = []

    lines = markdown_text.splitlines()
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            flush_paragraph()
            flush_callout()
            flush_table()
            continue

        callout_match = callout_pattern.match(stripped)
        if callout_match:
            flush_paragraph()
            flush_table()
            label = callout_match.group("label")
            text = callout_match.group("text")
            if label:
                flush_callout()
                icon, color = callout_meta(label)
                callout_icon, callout_color = icon, color
            callout_buffer.append(text)
            continue
        else:
            flush_callout()

        if stripped == "---":
            flush_paragraph()
            flush_table()
            blocks.append(_divider_block())
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            table_buffer.append(stripped)
            continue
        else:
            flush_table()

        if stripped.startswith("#"):
            flush_paragraph()
            level = len(stripped) - len(stripped.lstrip("#"))
            content = stripped[level:].strip()
            if content:
                blocks.append(_heading_block(level, content))
            continue

        todo_match = todo_pattern.match(stripped)
        if todo_match:
            flush_paragraph()
            blocks.append(
                _todo_block(
                    todo_match.group("text").strip(),
                    todo_match.group("checked").lower() == "x",
                )
            )
            continue

        if stripped.startswith(("- ", "* ")):
            flush_paragraph()
            blocks.append(_list_block("bulleted_list_item", stripped[2:].strip()))
            continue

        if stripped[0].isdigit():
            try:
                number_part, rest = stripped.split(". ", 1)
            except ValueError:
                number_part, rest = "", ""
            if number_part.isdigit() and rest:
                flush_paragraph()
                blocks.append(
                    _list_block("numbered_list_item", rest.strip())
                )
                continue

        paragraph_buffer.append(stripped)

    flush_paragraph()
    flush_callout()
    flush_table()
    return blocks


def _parse_date_value(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw).date().isoformat()
    except ValueError:
        return None


def _build_repository_text(repo: str | None) -> list[dict]:
    if not repo:
        return []
    return [
        {
            "type": "text",
            "text": {
                "content": repo,
                "link": {"url": f"https://github.com/{repo}"},
            },
        }
    ]


def _build_commit_text(repo: str | None, sha: str | None) -> list[dict]:
    if not sha:
        return []
    short_sha = sha[:7]
    link_url = f"https://github.com/{repo}/commit/{sha}" if repo else None
    text_obj: dict = {
        "content": short_sha,
    }
    if link_url:
        text_obj["link"] = {"url": link_url}
    return [{"type": "text", "text": text_obj}]


def create_notion_page(
    token: str, database_id: str, title: str, markdown_text: str
) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }

    structured_blocks, meta_map = build_structured_doc_blocks(markdown_text)
    children = structured_blocks or to_notion_blocks(markdown_text)

    timestamp = datetime.now(timezone.utc).astimezone()
    page_date = (
        _parse_date_value(meta_map.get("Date"))
        or timestamp.date().isoformat()
    )

    repo_from_meta = meta_map.get("Repository")
    repo_from_env = os.environ.get("GITHUB_REPOSITORY")
    repository_value = repo_from_meta or repo_from_env

    commit_sha = os.environ.get("GITHUB_SHA")

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
        "children": children,
    }

    if page_date:
        payload["properties"]["Date"] = {"date": {"start": page_date}}

    repo_rich_text = _build_repository_text(repository_value)
    if repo_rich_text:
        payload["properties"]["Repository"] = {"rich_text": repo_rich_text}

    commit_rich_text = _build_commit_text(repository_value, commit_sha)
    if commit_rich_text:
        payload["properties"]["Commit"] = {"rich_text": commit_rich_text}

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

