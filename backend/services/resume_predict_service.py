"""简历押题服务：单次 LLM 生成结构化 Q&A。"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List

from openai import OpenAI

from ..config import Config
from ..prompts.resume_predict_prompt import (
    build_resume_predict_user_prompt,
    get_resume_predict_system_prompt,
)


class ResumePredictService:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL,
        )

    def generate(
        self,
        resume_text: str,
        question_count: int = 12,
        focus_areas: List[str] | None = None,
    ) -> Dict[str, Any]:
        focus_areas = focus_areas or []
        count = max(6, min(20, int(question_count)))

        system_content = get_resume_predict_system_prompt()
        user_content = build_resume_predict_user_prompt(
            resume_text,
            count,
            focus_areas,
            Config.RESUME_MAX_CHARS,
        )

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            temperature=Config.PREDICT_TEMPERATURE,
            max_tokens=Config.PREDICT_MAX_TOKENS,
        )
        raw = (response.choices[0].message.content or "").strip()
        data = self._parse_json_payload(raw)
        sections = self._normalize_sections(data.get("sections"))

        return {
            "predict_id": str(uuid.uuid4())[:8],
            "generated_at": datetime.now().isoformat(),
            "question_count": count,
            "sections": sections,
        }

    def _parse_json_payload(self, raw: str) -> Dict[str, Any]:
        if not raw:
            raise ValueError("模型返回为空")

        cleaned = raw.strip()
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
        if fence:
            cleaned = fence.group(1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise ValueError("无法解析模型返回的 JSON，请重试") from None

    def _normalize_sections(self, sections: Any) -> List[Dict[str, Any]]:
        if not isinstance(sections, list):
            return []

        out: List[Dict[str, Any]] = []
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            category = str(sec.get("category") or "其他").strip()
            items_in = sec.get("items")
            if not isinstance(items_in, list):
                continue

            items: List[Dict[str, Any]] = []
            for it in items_in:
                if not isinstance(it, dict):
                    continue
                q = str(it.get("question") or "").strip()
                if not q:
                    continue
                points = it.get("answer_points")
                if isinstance(points, list):
                    points = [str(p).strip() for p in points if str(p).strip()]
                else:
                    points = []
                items.append(
                    {
                        "question": q,
                        "why_ask": str(it.get("why_ask") or "").strip(),
                        "answer_points": points,
                        "sample_answer": str(it.get("sample_answer") or "").strip(),
                    }
                )
            if items:
                out.append({"category": category, "items": items})
        return out
