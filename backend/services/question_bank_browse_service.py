"""
浏览本地面试题库 Markdown（data/{job_role}/interview_questions/）。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent

JOB_ROLE_DIRS: Dict[str, Path] = {
    "java_backend": ROOT / "data" / "java_backend" / "interview_questions",
    "web_frontend": ROOT / "data" / "web_frontend" / "interview_questions",
}

H3_NUMBERED = re.compile(r"^### (\d+)\.\s*(.+)$")
STRUCTURED_TITLE = re.compile(r"^## (题目\d+)\s*$")


def _extract_meta_field(block: str, label: str) -> str:
    m = re.search(rf"-\s*{re.escape(label)}[：:]\s*(.+)", block)
    return m.group(1).strip() if m else ""


def _extract_subsection(block: str, title: str) -> str:
    m = re.search(
        rf"### {re.escape(title)}\s*\n(.*?)(?=\n### |\Z)",
        block,
        re.DOTALL,
    )
    return m.group(1).strip() if m else ""


def _parse_structured_file(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if "题目1" not in text and not STRUCTURED_TITLE.search(text):
        return []

    items: List[Dict[str, Any]] = []
    parts = re.split(r"^## (题目\d+)\s*$", text, flags=re.MULTILINE)
    for i in range(1, len(parts), 2):
        title = parts[i]
        block = parts[i + 1] if i + 1 < len(parts) else ""
        question = _extract_subsection(block, "面试题")
        if not question:
            continue
        meta_block = _extract_subsection(block, "元数据")
        topic = _extract_meta_field(meta_block, "主题")
        items.append(
            {
                "id": f"{path.stem}:{title}",
                "source": path.name,
                "category": topic or "结构化题库",
                "topic": topic,
                "difficulty": _extract_meta_field(meta_block, "难度"),
                "question": question,
                "answer": _extract_subsection(block, "标准回答"),
                "follow_ups": _extract_subsection(block, "追问点"),
            }
        )
    return items


def _parse_h3_numbered_file(path: Path) -> List[Dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    items: List[Dict[str, Any]] = []
    category = "未分类"
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            heading = line[3:].strip()
            if not heading.startswith("题目"):
                category = heading
            i += 1
            continue

        m = H3_NUMBERED.match(line)
        if m:
            num, q_text = m.group(1), m.group(2).strip()
            i += 1
            answer_lines: List[str] = []
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith("## ") or H3_NUMBERED.match(nxt):
                    break
                answer_lines.append(nxt)
                i += 1
            answer = "\n".join(answer_lines).strip()
            items.append(
                {
                    "id": f"{path.stem}:{category}:{num}",
                    "source": path.name,
                    "category": category,
                    "topic": category,
                    "difficulty": "",
                    "question": q_text,
                    "answer": answer,
                    "follow_ups": "",
                }
            )
            continue
        i += 1

    return items


def _parse_file(path: Path) -> List[Dict[str, Any]]:
    structured = _parse_structured_file(path)
    if structured:
        return structured
    return _parse_h3_numbered_file(path)


class QuestionBankBrowseService:
    """读取并解析面试题库 Markdown 文件。"""

    def list_questions(self, job_role: str = "java_backend") -> Dict[str, Any]:
        base = JOB_ROLE_DIRS.get(job_role)
        if not base or not base.is_dir():
            return {
                "job_role": job_role,
                "total": 0,
                "sources": [],
                "categories": [],
                "items": [],
                "message": f"未找到题库目录：{job_role}/interview_questions",
            }

        md_files = sorted(base.glob("*.md")) + sorted(base.glob("*.MD"))
        all_items: List[Dict[str, Any]] = []
        for md in md_files:
            try:
                all_items.extend(_parse_file(md))
            except OSError:
                continue

        sources = sorted({item["source"] for item in all_items})
        categories = sorted({item["category"] for item in all_items if item.get("category")})

        return {
            "job_role": job_role,
            "total": len(all_items),
            "sources": sources,
            "categories": categories,
            "items": all_items,
            "message": "",
        }
