"""
构建向量知识库。
运行方式：在项目根目录执行 python -m backend.rag.ingest
"""
import re
import uuid
from pathlib import Path
from typing import List, Tuple

import chromadb
from sentence_transformers import SentenceTransformer

from ..config import Config

# ── 路径配置（与 backend.config 中项目根 data/ 一致）────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIRS = [
    (ROOT / "data" / "java_backend", "java_backend"),
    (ROOT / "data" / "web_frontend", "web_frontend"),
]
CHROMA_DIR = ROOT / "data" / "chroma_db"

# ── 向量库配置（集合名默认与 Config.RAG_COLLECTION 一致）──────────
COLLECTION_NAME = "knowledge_base"

# ── 切块参数 ──────────────────────────────────────────────
MIN_CHARS = 80        # 低于此长度合并到下一块
MAX_CHARS = 900       # 超过此长度按段落再拆

CATEGORY_LABEL = {
    "interview_questions":  "面试题库",
    "core_knowledge":       "核心知识",
    "database":             "数据库",
    "engineering_practice": "工程实践",
    "best_practices":       "最佳实践",
    "html_css":             "HTML与CSS",
    "javascript":           "JavaScript",
    "framework":            "前端框架",
    "browser":              "浏览器原理",
    "engineering":          "前端工程化",
    "algorithm":            "算法",
}


# ── 文本处理 ──────────────────────────────────────────────

def strip_frontmatter(text: str) -> str:
    """去掉 YAML frontmatter（--- ... ---）"""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip()
    return text


def split_by_h2(text: str) -> List[Tuple[str, str]]:
    """
    按 ## 标题切分，返回 [(heading, content), ...]。
    文档开头没有 ## 的部分归入 heading='' 的块。
    """
    lines = text.splitlines()
    chunks: List[Tuple[str, str]] = []
    heading = ""
    buf: List[str] = []

    for line in lines:
        if line.startswith("## "):
            if buf:
                chunks.append((heading, "\n".join(buf).strip()))
            heading = line[3:].strip()
            buf = []
        else:
            buf.append(line)

    if buf:
        chunks.append((heading, "\n".join(buf).strip()))

    return chunks


def split_long_chunk(heading: str, content: str) -> List[Tuple[str, str]]:
    """
    若 content 超过 MAX_CHARS，先按 ### 子标题拆，
    仍然过长则按双换行（段落）拆。
    """
    if len(content) <= MAX_CHARS:
        return [(heading, content)]

    # 按 ### 子标题拆
    sub_pattern = re.compile(r'^### (.+)$', re.MULTILINE)
    parts = sub_pattern.split(content)

    if len(parts) > 1:
        result = []
        # parts: [pre, title1, body1, title2, body2, ...]
        if parts[0].strip():
            result.append((heading, parts[0].strip()))
        for i in range(1, len(parts), 2):
            sub_title = parts[i].strip()
            sub_body = parts[i + 1].strip() if i + 1 < len(parts) else ""
            if sub_body:
                result.append((f"{heading} > {sub_title}", sub_body))
        return result

    # 没有子标题，按段落拆
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    result = []
    buf = ""
    for para in paragraphs:
        if len(buf) + len(para) > MAX_CHARS and buf:
            result.append((heading, buf.strip()))
            buf = para
        else:
            buf = buf + "\n\n" + para if buf else para
    if buf:
        result.append((heading, buf.strip()))
    return result


def merge_short_chunks(chunks: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """把过短的 chunk 合并到下一个"""
    merged = []
    i = 0
    while i < len(chunks):
        h, c = chunks[i]
        if len(c) < MIN_CHARS and i + 1 < len(chunks):
            next_h, next_c = chunks[i + 1]
            chunks[i + 1] = (next_h, c + "\n\n" + next_c)
            i += 1
        else:
            merged.append((h, c))
            i += 1
    return merged


def parse_file(path: Path) -> List[Tuple[str, str]]:
    """读取并切分一个 Markdown 文件，返回 [(heading, content)]"""
    for enc in ("utf-8", "gbk", "utf-8-sig"):
        try:
            text = path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        print(f"  [跳过] 无法解码：{path.name}")
        return []
    text = strip_frontmatter(text)

    raw_chunks = split_by_h2(text)

    expanded = []
    for heading, content in raw_chunks:
        if not content:
            continue
        expanded.extend(split_long_chunk(heading, content))

    return merge_short_chunks(expanded)


# ── 主流程 ────────────────────────────────────────────────

def build_index():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    embed_model = Config.RAG_ST_MODEL_PATH
    print(f"加载 Embedding 模型：{embed_model}")
    model = SentenceTransformer(embed_model)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # 若已存在则删除重建（幂等）
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print("已清除旧向量库，重新构建")

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    all_texts, all_ids, all_metas = [], [], []

    for data_dir, domain in DATA_DIRS:
        md_files = list(data_dir.rglob("*.md")) + list(data_dir.rglob("*.MD"))
        print(f"[{domain}] 共发现 {len(md_files)} 个 Markdown 文件")

        for md_path in md_files:
            category_dir = md_path.parent.name
            category_label = CATEGORY_LABEL.get(category_dir, category_dir)
            filename = md_path.stem

            chunks = parse_file(md_path)

            for idx, (heading, content) in enumerate(chunks):
                # 拼入标题前缀，给模型更多上下文
                heading_prefix = f"【{heading}】\n" if heading else ""
                full_text = f"{heading_prefix}{content}"

                all_texts.append(full_text)
                all_ids.append(str(uuid.uuid4()))
                meta = {
                    "domain": domain,
                    "source": filename,
                    "category": category_label,
                    "heading": heading,
                    "chunk_idx": idx,
                }
                # 仅面试题库块带 job_role，供 question_bank 与旧库两种过滤方式兼容
                if category_label == "面试题库":
                    meta["job_role"] = domain

                all_metas.append(meta)

            print(f"  {category_label}/{filename}  →  {len(chunks)} 块")

    print(f"\n共 {len(all_texts)} 个 chunk，开始向量化...")
    embeddings = model.encode(all_texts, show_progress_bar=True, batch_size=32)

    # 分批写入（ChromaDB 单次上限约 5000）
    batch = 500
    for start in range(0, len(all_texts), batch):
        collection.add(
            ids=all_ids[start:start + batch],
            documents=all_texts[start:start + batch],
            embeddings=embeddings[start:start + batch].tolist(),
            metadatas=all_metas[start:start + batch],
        )

    print(f"向量库构建完成，共写入 {len(all_texts)} 条，存储于：{CHROMA_DIR}")


if __name__ == "__main__":
    build_index()
