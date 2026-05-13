import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ..config import DATA_DIR

class HistoryManager:
    """面试历史数据管理器"""

    def __init__(self, data_dir: Optional[str] = None):
        # 默认写入项目根目录 data/，与工作目录无关
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.history_file = self.data_dir / "interview_history.json"
        self._ensure_data_dir()
        self._ensure_history_file()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_history_file(self):
        """确保历史文件存在"""
        if not self.history_file.exists():
            self._save_history([])

    def _load_history(self) -> List[dict]:
        """从文件加载历史记录"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_history(self, history: List[dict]):
        """保存历史记录到文件"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def add_interview(self, session_id: str, messages: List[dict], summary: str = "") -> dict:
        """
        添加面试记录
        :param session_id: 会话ID
        :param messages: 消息列表
        :param summary: 面试总结
        :return: 创建的面试记录
        """
        history = self._load_history()

        interview = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": messages,
            "summary": summary
        }

        history.insert(0, interview)
        self._save_history(history)

        return interview

    def update_interview(self, session_id: str, messages: List[dict], summary: str = ""):
        """
        更新面试记录
        :param session_id: 会话ID
        :param messages: 更新后的消息列表
        :param summary: 面试总结
        """
        history = self._load_history()

        for interview in history:
            if interview["session_id"] == session_id:
                interview["messages"] = messages
                interview["updated_at"] = datetime.now().isoformat()
                if summary:
                    interview["summary"] = summary
                break

        self._save_history(history)

    def get_interviews(self) -> List[dict]:
        """
        获取所有面试记录
        :return: 按时间倒序排列的面试记录列表
        """
        return self._load_history()

    def get_interview(self, session_id: str) -> Optional[dict]:
        """
        获取指定会话的面试记录
        :param session_id: 会话ID
        :return: 面试记录，如果不存在返回 None
        """
        history = self._load_history()

        for interview in history:
            if interview["session_id"] == session_id:
                return interview

        return None

    def delete_interview(self, session_id: str) -> bool:
        """
        删除指定的面试记录
        :param session_id: 会话ID
        :return: 是否删除成功
        """
        history = self._load_history()
        original_length = len(history)

        history = [i for i in history if i["session_id"] != session_id]

        if len(history) < original_length:
            self._save_history(history)
            return True

        return False

    def clear_all(self):
        """清空所有面试记录"""
        self._save_history([])
