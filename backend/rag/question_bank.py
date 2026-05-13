"""
从 Chroma 向量库随机抽取面试题文档（不加载 Embedding 模型，仅读持久化数据）。
"""
from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


def sample_random_question_texts(
    db_dir: str,
    collection_name: str,
    job_role: str,
    k: int,
    max_chars_per_item: int,
) -> Tuple[List[str], int]:
    """
    随机抽取 k 条文档正文（过长则截断）。
    返回 (文本列表, 库内总条数)；失败返回 ([], 0)。
    """
    try:
        import chromadb
    except ImportError:
        logger.warning("未安装 chromadb，无法抽取题库")
        return [], 0

    path = Path(db_dir)
    if not path.is_dir():
        return [], 0

    try:
        client = chromadb.PersistentClient(path=str(path.resolve()))
        coll = client.get_collection(name=collection_name)
    except Exception as e:
        logger.warning("打开 Chroma 集合失败: %s", e)
        return [], 0

    try:
        # 优先「面试题库」category；否则按 job_role（历史数据）
        raw = coll.get(where={"category": "面试题库"}, include=["documents", "metadatas"])
        ids = raw.get("ids") or []
        if not ids:
            raw = coll.get(where={"job_role": job_role}, include=["documents", "metadatas"])
            ids = raw.get("ids") or []
    except Exception as e:
        logger.warning("读取题库 id 失败: %s", e)
        return [], 0

    total = len(ids)
    if total == 0:
        return [], 0

    take = min(k, total)
    sample_ids = random.sample(ids, take)

    try:
        got = coll.get(ids=sample_ids, include=["documents"])
        docs = got.get("documents") or []
    except Exception as e:
        logger.warning("按 id 拉取文档失败: %s", e)
        return [], total

    texts: List[str] = []
    for doc in docs:
        if not doc:
            continue
        text = doc.strip()
        if max_chars_per_item > 0 and len(text) > max_chars_per_item:
            text = text[: max_chars_per_item] + "\n...(已截断)"
        texts.append(text)

    return texts, total
