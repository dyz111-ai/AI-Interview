from openai import OpenAI
from typing import Dict, List, Optional

from ..config import Config
from ..prompts.system_prompt import (
    build_summary_resume_addon,
    get_interview_summary_system_prompt,
    get_system_prompt,
)


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
        question_bank_addon: Optional[str] = None,
        resume_addon: Optional[str] = None,
    ) -> str:
        """
        发送消息给 LLM。
        题库附加说明优先于简历摘录；无题库时注入简历或 RAG 参考块。
        """
        try:
            system_content = get_system_prompt()
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
                model="deepseek-chat",
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"LLM API错误: {e}")
            return "抱歉，我遇到了一些问题，请稍后重试。"

    def get_first_question(self, resume_addon: Optional[str] = None) -> str:
        """首轮：结合简历做自我介绍与亮点追问。"""
        return self.chat(
            [],
            "请开始面试，首先让候选人结合简历做自我介绍并你可追问简历中的亮点。",
            rag_context="",
            resume_addon=resume_addon,
        )

    def end_interview(
        self,
        history: List[Dict[str, str]],
        *,
        resume_plain_text: Optional[str] = None,
    ) -> str:
        """结束面试：七章《面试总结报告》，与对话人设分离。"""
        try:
            system_content = get_interview_summary_system_prompt()
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
                model="deepseek-chat",
                messages=messages,
                temperature=Config.SUMMARY_TEMPERATURE,
                max_tokens=Config.SUMMARY_MAX_TOKENS,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"LLM 总结错误: {e}")
            return "抱歉，生成面试总结时出现问题，请稍后重试。"
