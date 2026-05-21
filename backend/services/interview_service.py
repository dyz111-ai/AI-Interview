from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Optional

from ..config import Config
from ..models.interview_settings import InterviewSettings
from ..models.session import InterviewSession
from ..prompts.system_prompt import build_question_bank_addon, build_resume_addon
from ..rag.question_bank import sample_random_question_texts
from ..rag.rag_service import RAGService
from ..services.llm_service import LLMService
from ..utils.history_manager import HistoryManager


class InterviewService:
    """面试业务逻辑服务"""

    def __init__(self) -> None:
        self.llm_service = LLMService()
        self.sessions: Dict[str, InterviewSession] = {}
        self.history_manager = HistoryManager()
        self.rag_service: Optional[RAGService] = None
        if Config.RAG_ENABLED:
            try:
                self.rag_service = RAGService()
            except Exception as e:
                print(f"RAG 服务初始化失败（将在无 RAG 检索模式下运行）: {e}")
                self.rag_service = None

    def start_interview(
        self,
        session_id: Optional[str],
        resume_text: str,
        settings: Optional[InterviewSettings] = None,
    ) -> tuple[str, str]:
        """
        开始面试（须携带 parse-resume 得到的 resume_text）
        :return: (session_id, first_question)
        """
        raw = (resume_text or "").strip()
        if len(raw) < Config.RESUME_MIN_CHARS_TO_START:
            raise ValueError(
                f"简历有效内容过短（至少约 {Config.RESUME_MIN_CHARS_TO_START} 个字符），"
                "请先上传 PDF 或 Word（docx）并解析成功后再开始"
            )

        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        stored = raw[: Config.RESUME_MAX_CHARS]
        interview_settings = settings if settings is not None else InterviewSettings()
        session = InterviewSession(
            session_id=session_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            resume_plain_text=stored,
            settings=interview_settings,
        )

        resume_addon = build_resume_addon(stored)
        first_question = self.llm_service.get_first_question(
            resume_addon=resume_addon,
            interview_settings=interview_settings,
        )

        session.add_message("assistant", first_question)
        self.sessions[session_id] = session

        return session_id, first_question

    def chat(self, session_id: str, user_message: str) -> str:
        """处理用户消息，返回面试官回复。"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("会话不存在或已结束，请先上传简历并成功开始面试")

        session.add_message("user", user_message)
        session.user_turn_count += 1

        if session.bank_started and session.bank_question_texts:
            session.bank_turns_on_current += 1
            max_per = Config.MAX_USER_REPLIES_PER_BANK_QUESTION
            nq = len(session.bank_question_texts)
            if session.bank_turns_on_current > max_per and session.current_question_index < nq - 1:
                session.current_question_index += 1
                session.bank_turns_on_current = 1
        elif (
            Config.QUESTION_BANK_ENABLED
            and not session.bank_started
            and session.user_turn_count >= session.settings.min_rounds_before_bank
        ):
            texts, _total = sample_random_question_texts(
                Config.RAG_DB_DIR,
                Config.RAG_COLLECTION,
                Config.RAG_JOB_ROLE,
                session.settings.bank_sample_size,
                Config.QUESTION_BANK_MAX_CHARS_PER_ITEM,
            )
            if texts:
                session.bank_started = True
                session.bank_question_texts = texts
                session.current_question_index = 0
                session.bank_turns_on_current = 1

        history = session.get_history_for_llm()

        bank_addon = None
        if session.bank_started and session.bank_question_texts:
            bank_addon = build_question_bank_addon(
                session.bank_question_texts,
                session.current_question_index,
                session.bank_turns_on_current,
                Config.MAX_USER_REPLIES_PER_BANK_QUESTION,
            )

        resume_addon = None
        if session.resume_plain_text and not session.bank_started:
            resume_addon = build_resume_addon(session.resume_plain_text)

        rag_context = ""
        # 题库阶段不再做相似度 RAG，避免与抽题材料打架
        if self.rag_service and Config.RAG_ENABLED and not (
            session.bank_started and session.bank_question_texts
        ):
            try:
                k = max(1, Config.RAG_TOP_K)
                chunks = self.rag_service.query(user_message, n_results=k)
                rag_context = self.rag_service.format_context(chunks)
                max_chars = Config.RAG_CONTEXT_MAX_CHARS
                if max_chars > 0 and len(rag_context) > max_chars:
                    rag_context = rag_context[:max_chars] + "\n...(已截断)"
            except Exception as e:
                print(f"RAG 检索失败: {e}")

        reply = self.llm_service.chat(
            history,
            user_message,
            rag_context,
            question_bank_addon=bank_addon,
            resume_addon=resume_addon,
            interview_settings=session.settings,
        )

        session.add_message("assistant", reply)
        return reply

    def end_interview(self, session_id: str) -> str:
        """结束面试，返回总结并写入历史。"""
        session = self.sessions.get(session_id)
        if not session:
            return "未找到面试会话。"

        history = session.get_history_for_llm()
        summary = self.llm_service.end_interview(
            history,
            resume_plain_text=session.resume_plain_text or None,
        )

        messages = [{"role": msg.role, "content": msg.content} for msg in session.history]

        existing = self.history_manager.get_interview(session_id)
        if existing:
            self.history_manager.update_interview(session_id, messages, summary)
        else:
            self.history_manager.add_interview(session_id, messages, summary)

        del self.sessions[session_id]
        return summary

    def get_all_interviews(self) -> list:
        return self.history_manager.get_interviews()

    def get_interview(self, session_id: str) -> Optional[dict]:
        return self.history_manager.get_interview(session_id)

    def delete_interview(self, session_id: str) -> bool:
        return self.history_manager.delete_interview(session_id)
