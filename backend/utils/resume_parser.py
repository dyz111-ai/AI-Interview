"""从 PDF / Word(.docx) 字节中提取纯文本。"""
from __future__ import annotations

import io
import re
from pathlib import Path


def normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        if t.strip():
            parts.append(t)
    return normalize_text("\n".join(parts))


def extract_docx_text(data: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return normalize_text("\n".join(parts))


def extract_text_from_upload(filename: str, data: bytes) -> str:
    if not data:
        raise ValueError("文件为空")

    suffix = Path(filename or "").suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(data)
    if suffix == ".docx":
        return extract_docx_text(data)
    if suffix == ".doc":
        raise ValueError("暂不支持旧版 .doc，请将简历另存为 .docx 或导出为 PDF 后再上传")

    raise ValueError("仅支持 PDF 或 Word（.docx）")
