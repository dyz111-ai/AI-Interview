from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .config import Config
from .services.interview_service import InterviewService
from .models.schemas import (
    ChatRequest, ChatResponse,
    StartInterviewRequest, StartInterviewResponse,
    EndInterviewRequest, EndInterviewResponse,
    InterviewListResponse, DeleteInterviewRequest, DeleteInterviewResponse,
    ParseResumeResponse,
)
from .utils.resume_parser import extract_text_from_upload

app = FastAPI(title="AI面试系统API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

interview_service = InterviewService()

@app.get("/")
async def root():
    return {"message": "AI面试系统API运行中", "status": "ok"}

@app.post("/api/interview/parse-resume", response_model=ParseResumeResponse)
async def parse_resume(file: UploadFile = File(...)):
    """上传 PDF 或 Word（docx），返回解析后的纯文本。"""
    data = await file.read()
    if len(data) > Config.MAX_RESUME_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="文件过大")

    try:
        text = extract_text_from_upload(file.filename or "resume", data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    truncated = False
    if len(text) > Config.RESUME_MAX_CHARS:
        text = text[: Config.RESUME_MAX_CHARS]
        truncated = True

    return ParseResumeResponse(
        text=text,
        truncated=truncated,
        filename=file.filename or "",
    )


@app.post("/api/interview/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """
    开始面试（必须携带 parse-resume 得到的 resume_text）
    """
    try:
        session_id, first_question = interview_service.start_interview(
            request.session_id,
            request.resume_text,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StartInterviewResponse(
        session_id=session_id,
        first_question=first_question,
    )

@app.post("/api/interview/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    发送用户消息，获取面试官回复
    """
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id不能为空")
    if not request.user_message:
        raise HTTPException(status_code=400, detail="user_message不能为空")

    try:
        reply = interview_service.chat(request.session_id, request.user_message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ChatResponse(
        reply=reply,
        session_id=request.session_id
    )

@app.post("/api/interview/end", response_model=EndInterviewResponse)
async def end_interview(request: EndInterviewRequest):
    """
    结束面试，返回总结
    """
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id不能为空")

    summary = interview_service.end_interview(request.session_id)
    return EndInterviewResponse(summary=summary)

@app.get("/api/interview/history", response_model=InterviewListResponse)
async def get_interview_history():
    """
    获取所有面试历史记录
    """
    interviews = interview_service.get_all_interviews()
    return InterviewListResponse(
        interviews=interviews,
        total=len(interviews)
    )

@app.get("/api/interview/history/{session_id}")
async def get_interview_detail(session_id: str):
    """
    获取指定面试记录的详情
    """
    interview = interview_service.get_interview(session_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    return interview

@app.delete("/api/interview/history/{session_id}", response_model=DeleteInterviewResponse)
async def delete_interview(session_id: str):
    """
    删除指定的面试记录
    """
    success = interview_service.delete_interview(session_id)
    if success:
        return DeleteInterviewResponse(
            success=True,
            message="面试记录删除成功"
        )
    else:
        return DeleteInterviewResponse(
            success=False,
            message="面试记录不存在"
        )
