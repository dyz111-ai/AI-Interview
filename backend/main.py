from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .config import Config
from .services.interview_service import InterviewService
from .services.resume_predict_service import ResumePredictService
from .services.question_bank_browse_service import QuestionBankBrowseService
from .models.schemas import (
    ChatRequest, ChatResponse,
    StartInterviewRequest, StartInterviewResponse,
    EndInterviewRequest, EndInterviewResponse,
    InterviewListResponse, DeleteInterviewRequest, DeleteInterviewResponse,
    ParseResumeResponse,
    ResumePredictRequest,
    ResumePredictResponse,
    QuestionBankListResponse,
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
resume_predict_service = ResumePredictService()
question_bank_browse_service = QuestionBankBrowseService()

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


@app.post("/api/resume-predict/generate", response_model=ResumePredictResponse)
async def generate_resume_predict(request: ResumePredictRequest):
    """根据简历生成可能面试题与回答要点。"""
    raw = (request.resume_text or "").strip()
    if len(raw) < Config.RESUME_MIN_CHARS_TO_START:
        raise HTTPException(
            status_code=400,
            detail=f"简历有效内容过短（至少约 {Config.RESUME_MIN_CHARS_TO_START} 个字符）",
        )
    try:
        result = resume_predict_service.generate(
            raw,
            question_count=request.question_count,
            focus_areas=request.focus_areas,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"押题生成失败: {e}") from e

    if not result.get("sections"):
        raise HTTPException(status_code=500, detail="未生成有效题目，请重试")

    return ResumePredictResponse(**result)


@app.get("/api/question-bank/list", response_model=QuestionBankListResponse)
async def list_question_bank(job_role: str = "java_backend"):
    """浏览本地面试题库（Markdown 源文件）。"""
    result = question_bank_browse_service.list_questions(job_role=job_role)
    return QuestionBankListResponse(**result)


@app.post("/api/interview/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """
    开始面试（必须携带 parse-resume 得到的 resume_text）
    """
    try:
        session_id, first_question = interview_service.start_interview(
            request.session_id,
            request.resume_text,
            request.settings,
            request.job_role,
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
