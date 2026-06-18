from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from .interview_settings import InterviewSettings

class Message(BaseModel):
    """单条消息"""
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: datetime

class InterviewSession(BaseModel):
    """面试会话"""
    session_id: str
    created_at: datetime
    last_active: datetime
    history: List[Message] = Field(default_factory=list)

    # 用户已累计发言次数（每条用户消息 +1）
    user_turn_count: int = 0
    # 满回合后随机题库是否已启用
    bank_started: bool = False
    # 抽取到的题目正文（通常 3 条）
    bank_question_texts: List[str] = Field(default_factory=list)
    # 当前聚焦第几题（0..2）
    current_question_index: int = 0
    # 当前题下用户已发言轮数（本题内计数，切换题目时重置）
    bank_turns_on_current: int = 0

    # 解析后的简历正文（整场会话保留，第一阶段注入模型）
    resume_plain_text: str = ""

    # 面试岗位
    job_role: str = "java_backend"

    # 设置页传入的本场配置
    settings: InterviewSettings = Field(default_factory=InterviewSettings)

    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.history.append(Message(
            role=role,
            content=content,
            timestamp=datetime.now()
        ))
        self.last_active = datetime.now()
    
    def get_history_for_llm(self) -> List[Dict[str, str]]:
        """转换为LLM需要的格式"""
        return [{"role": msg.role, "content": msg.content} for msg in self.history]