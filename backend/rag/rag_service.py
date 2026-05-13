"""
RAG 检索服务：与 Config 中的 data/chroma_db、集合名、本地 embedding 路径对齐。
仅在 RAG_ENABLED=true 且向量库存在时由 InterviewService 初始化。
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import chromadb
from sentence_transformers import SentenceTransformer

from ..config import Config

logger = logging.getLogger(__name__)


class RAGService:
    """按当前用户消息做相似度检索，结果格式化为 prompt 片段。"""

    def __init__(self) -> None:
        chroma_dir = Path(Config.RAG_DB_DIR)
        if not chroma_dir.is_dir():
            raise FileNotFoundError(f"RAG 向量库目录不存在: {chroma_dir}（可先运行 python -m backend.rag.ingest）")

        model_path = Config.RAG_ST_MODEL_PATH
        logger.info("RAGService：加载 Embedding 模型 %s", model_path)
        self._model = SentenceTransformer(model_path)

        client = chromadb.PersistentClient(path=str(chroma_dir.resolve()))
        self._collection = client.get_collection(Config.RAG_COLLECTION)
        logger.info(
            "RAGService：集合 %s 已加载，共 %s 条",
            Config.RAG_COLLECTION,
            self._collection.count(),
        )

    def query(self, text: str, n_results: int = 5, category: Optional[str] = None) -> List[str]:
        """
        检索与 text 最相关的知识片段。
        category 非空时按元数据 category 过滤（与 ingest 写入的标签一致）。
        """
        embedding = self._model.encode([text])[0].tolist()
        where = {"category": category} if category else None

        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        docs = result["documents"][0]
        distances = result["distances"][0]

        # 余弦距离下，过大视为不相关（与旧实现阈值一致）
        filtered = [doc for doc, dist in zip(docs, distances) if dist < 0.6]
        return filtered

    def format_context(self, chunks: List[str]) -> str:
        """把检索到的 chunk 列表格式化为可注入 prompt 的字符串"""
        if not chunks:
            return ""
        parts = [f"[参考知识 {i+1}]\n{chunk}" for i, chunk in enumerate(chunks)]
        return "\n\n".join(parts)
