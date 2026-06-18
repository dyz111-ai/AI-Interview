import os
from pathlib import Path
from dotenv import load_dotenv

# 禁用OpenAI代理配置（解决httpx版本兼容性问题）
os.environ["OPENAI_DISABLE_PROXY"] = "1"

# 加载.env文件
load_dotenv()

_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
_RAG_DIR = _BACKEND_DIR / "rag"
_LOCAL_EMB = _RAG_DIR / "bge-small-en-v1.5"
# 数据目录统一在项目根目录 data/（面试历史、向量库、题库源 markdown 等）
DATA_DIR = _PROJECT_ROOT / "data"
_MODELS_BGE_ZH = _PROJECT_ROOT / "models" / "bge-small-zh-v1.5"

class Config:
    # DeepSeek配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-2f81ce925baa46d38bda44602934fec8")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

    # 支持的岗位
    SUPPORTED_JOB_ROLES = ["java_backend", "web_frontend"]
    DEFAULT_JOB_ROLE = os.getenv("DEFAULT_JOB_ROLE", "java_backend")

    # 服务器配置
    HOST = "127.0.0.1"
    PORT = 8000
    
    # CORS配置（允许前端访问）
    ALLOWED_ORIGINS = [
        "http://127.0.0.1:8765",  # run.py 默认静态页端口
        "http://localhost:8765",
        "http://127.0.0.1:5500",  # VS Code Live Server 等
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
    
    # 面试配置
    MAX_HISTORY = 10  # 最大历史轮数
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    # 结束面试时生成的长篇总结（七章报告）
    SUMMARY_MAX_TOKENS = int(os.getenv("SUMMARY_MAX_TOKENS", "3500"))
    SUMMARY_TEMPERATURE = float(os.getenv("SUMMARY_TEMPERATURE", "0.45"))
    # 注入总结提示词的简历摘录上限（字符）
    SUMMARY_RESUME_MAX_CHARS = int(os.getenv("SUMMARY_RESUME_MAX_CHARS", "8000"))

    # 简历押题
    PREDICT_MAX_TOKENS = int(os.getenv("PREDICT_MAX_TOKENS", "6000"))
    PREDICT_TEMPERATURE = float(os.getenv("PREDICT_TEMPERATURE", "0.5"))

    # RAG（向量检索）：默认关闭；与 backend.rag.ingest / RAGService 一致，持久化在项目根 data/chroma_db
    # 构建向量库：在项目根执行 python -m backend.rag.ingest
    RAG_ENABLED = os.getenv("RAG_ENABLED", "false").lower() in ("1", "true", "yes")
    RAG_DB_DIR = os.getenv("RAG_DB_DIR", str(DATA_DIR / "chroma_db"))
    RAG_COLLECTION = os.getenv("RAG_COLLECTION", "knowledge_base")
    # RAGService 使用的 SentenceTransformer 本地路径（目录不存在时可设环境变量指向其他路径或 HF 模型名）
    RAG_ST_MODEL_PATH = os.getenv(
        "RAG_ST_MODEL_PATH",
        str(_MODELS_BGE_ZH) if _MODELS_BGE_ZH.is_dir() else (
            str(_LOCAL_EMB) if _LOCAL_EMB.is_dir() else "BAAI/bge-small-zh-v1.5"
        ),
    )
    RAG_JOB_ROLE = os.getenv("RAG_JOB_ROLE", "java_backend")
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))
    RAG_CONTEXT_MAX_CHARS = int(os.getenv("RAG_CONTEXT_MAX_CHARS", "4000"))
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        str(_LOCAL_EMB) if _LOCAL_EMB.is_dir() else "BAAI/bge-small-zh-v1.5",
    )
    _default_local_only = "true" if _LOCAL_EMB.is_dir() else "false"
    EMBEDDING_LOCAL_ONLY = os.getenv("EMBEDDING_LOCAL_ONLY", _default_local_only).lower() in (
        "1",
        "true",
        "yes",
    )

    # 题库环节：用户发言满 MIN 轮后随机抽 QUESTION_BANK_SAMPLE_SIZE 道题注入提示词（需 data/chroma_db 已构建）
    QUESTION_BANK_ENABLED = os.getenv("QUESTION_BANK_ENABLED", "true").lower() in ("1", "true", "yes")
    MIN_USER_ROUNDS_BEFORE_BANK = int(os.getenv("MIN_USER_ROUNDS_BEFORE_BANK", "3"))
    QUESTION_BANK_SAMPLE_SIZE = int(os.getenv("QUESTION_BANK_SAMPLE_SIZE", "3"))
    MAX_USER_REPLIES_PER_BANK_QUESTION = int(os.getenv("MAX_USER_REPLIES_PER_BANK_QUESTION", "4"))
    QUESTION_BANK_MAX_CHARS_PER_ITEM = int(os.getenv("QUESTION_BANK_MAX_CHARS_PER_ITEM", "3500"))

    # 简历上传（解析后再开始面试）
    RESUME_MAX_CHARS = int(os.getenv("RESUME_MAX_CHARS", "12000"))
    MAX_RESUME_UPLOAD_BYTES = int(os.getenv("MAX_RESUME_UPLOAD_BYTES", str(10 * 1024 * 1024)))  # 10MB
    RESUME_MIN_CHARS_TO_START = int(os.getenv("RESUME_MIN_CHARS_TO_START", "20"))
    RESUME_IN_BANK_PHASE = os.getenv("RESUME_IN_BANK_PHASE", "false").lower() in ("1", "true", "yes")