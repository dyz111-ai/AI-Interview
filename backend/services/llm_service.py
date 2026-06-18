from openai import OpenAI
from typing import Dict, List, Optional

from ..config import Config
from ..prompts.system_prompt import (
    build_interview_style_addon,
    build_summary_resume_addon,
    get_first_question_user_prompt,
    get_interview_summary_system_prompt,
    get_system_prompt,
)
from ..models.interview_settings import InterviewSettings


class LLMService:
    """DeepSeek API 服务（OpenAI 兼容接口）"""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL,
        )

    def chat(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        rag_context: str = "",
        *,
        job_role: str = "java_backend",
        question_bank_addon: Optional[str] = None,
        resume_addon: Optional[str] = None,
        interview_settings: Optional[InterviewSettings] = None,
    ) -> str:
        """
        发送消息给 LLM。
        题库附加说明优先于简历摘录；无题库时注入简历或 RAG 参考块。
        """
        try:
            system_content = get_system_prompt(job_role)
            if interview_settings:
                system_content = system_content + "\n\n" + build_interview_style_addon(interview_settings)
            if question_bank_addon:
                system_content = system_content + "\n\n" + question_bank_addon
                if Config.RESUME_IN_BANK_PHASE and resume_addon:
                    system_content = system_content + "\n\n" + resume_addon
            elif resume_addon:
                system_content = system_content + "\n\n" + resume_addon
            if rag_context:
                system_content += (
                    "\n\n【参考知识库】\n以下是与当前话题相关的知识，请基于这些内容进行追问和评估，"
                    "不要直接念出知识库内容：\n"
                    + rag_context
                )

            messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
            messages.extend(history)
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"LLM API错误: {e}")
            return "抱歉，我遇到了一些问题，请稍后重试。"

    def get_first_question(
        self,
        resume_addon: Optional[str] = None,
        *,
        job_role: str = "java_backend",
        interview_settings: Optional[InterviewSettings] = None,
    ) -> str:
        """首轮：结合简历与开场方式提问。"""
        opening = "self_intro"
        if interview_settings:
            opening = interview_settings.opening_mode
        return self.chat(
            [],
            get_first_question_user_prompt(opening),
            rag_context="",
            job_role=job_role,
            resume_addon=resume_addon,
            interview_settings=interview_settings,
        )

    def end_interview(
        self,
        history: List[Dict[str, str]],
        *,
        job_role: str = "java_backend",
        resume_plain_text: Optional[str] = None,
    ) -> str:
        """结束面试：七章《面试总结报告》，与对话人设分离。"""
        try:
            system_content = get_interview_summary_system_prompt(job_role)
            addon = build_summary_resume_addon(
                resume_plain_text or "",
                Config.SUMMARY_RESUME_MAX_CHARS,
            )
            if addon:
                system_content = system_content + "\n\n" + addon

            user_content = (
                "请根据完整面试对话历史撰写《面试总结报告》。"
                "若系统提供了简历摘录，撰写「岗位匹配」「项目表达」等相关判断时可对照参考，仍以本场对话表现为准。"
                "必须包含七大章节，章节标题须以「一、」至「七、」开头且顺序正确，不得省略任何一章。"
            )

            messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
            messages.extend(history)
            messages.append({"role": "user", "content": user_content})

            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=Config.SUMMARY_TEMPERATURE,
                max_tokens=Config.SUMMARY_MAX_TOKENS,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"LLM 总结错误: {e}")
            return "抱歉，生成面试总结时出现问题，请稍后重试。"
