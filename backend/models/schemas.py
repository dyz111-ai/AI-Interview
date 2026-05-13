from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    """聊天请求模型"""
    session_id: str
    user_message: str

class ChatResponse(BaseModel):
    """聊天响应模型"""
    reply: str
    session_id: str

class StartInterviewRequest(BaseModel):
    """开始面试请求（须先解析简历并得到 resume_text）"""

    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: Optional[str] = None
    resume_text: str = Field(
        ...,
        min_length=1,
        description="解析后的简历全文",
        validation_alias=AliasChoices("resume_text", "resumeText"),
    )


class ParseResumeResponse(BaseModel):
    """简历解析响应"""
    text: str
    truncated: bool = False
    filename: str = ""

class StartInterviewResponse(BaseModel):
    """开始面试响应"""
    session_id: str
    first_question: str

class EndInterviewRequest(BaseModel):
    """结束面试请求"""
    session_id: str

class EndInterviewResponse(BaseModel):
    """结束面试响应"""
    summary: str

class Message(BaseModel):
    """消息模型"""
    role: str
    content: str

class InterviewRecord(BaseModel):
    """面试记录模型"""
    session_id: str
    created_at: str
    updated_at: str
    messages: List[Message]
    summary: str

class InterviewListResponse(BaseModel):
    """面试列表响应"""
    interviews: List[InterviewRecord]
    total: int

class DeleteInterviewRequest(BaseModel):
    """删除面试请求"""
    session_id: str

class DeleteInterviewResponse(BaseModel):
    """删除面试响应"""
    success: bool
    message: str
