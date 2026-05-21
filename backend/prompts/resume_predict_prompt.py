"""简历押题：根据简历生成可能问题与回答要点。"""
from __future__ import annotations

from typing import List

from .system_prompt import _FOCUS_LABELS


def get_resume_predict_system_prompt() -> str:
    return (
        "你是一名资深 Java 后端技术面试官，擅长根据候选人简历预测技术面可能问题，"
        "并给出可背诵的答题要点框架。"
        "目标岗位：Java 后端开发工程师。"
        "输出必须是合法 JSON，且仅输出 JSON，不要 Markdown 代码块标记，不要任何前后说明文字。"
        "JSON 结构如下："
        '{"sections":[{"category":"分类名","items":[{"question":"问题","why_ask":"为何可能问",'
        '"answer_points":["要点1","要点2"],"sample_answer":"可选参考回答"}]}]}'
        "要求："
        "1 问题必须能对应简历中的项目、技能或经历，why_ask 一句话说明考察点。"
        "2 answer_points 每条为简短提纲，共 3 到 6 条，不要写成长篇标准答案。"
        "3 sample_answer 可选，2 到 4 句口语化表述，严禁编造简历未提及的技术或项目细节；"
        "信息不足时 sample_answer 写「请结合你真实项目数据补充」。"
        "4 分类尽量覆盖：自我介绍与求职动机、项目经历深挖、Java基础与集合并发、"
        "Spring与框架、数据库缓存与中间件、综合与开放题；可按题量合并或减少类别。"
        "5 各分类 items 数量按重要程度分配，项目类应占一定比例。"
        "6 全文使用简体中文。"
    )


def build_resume_predict_user_prompt(
    resume_text: str,
    question_count: int,
    focus_areas: List[str],
    resume_max_chars: int,
) -> str:
    text = (resume_text or "").strip()
    if len(text) > resume_max_chars:
        text = text[:resume_max_chars] + "\n（以下简历已截断）"

    focus_line = ""
    if focus_areas:
        labels = [_FOCUS_LABELS.get(k, k) for k in focus_areas]
        focus_line = "请优先侧重以下方向出题：" + "；".join(labels) + "。\n"

    return (
        f"请根据以下简历预测约 {question_count} 道可能面试题（全部分类合计），"
        f"并给出每题的 why_ask、answer_points、sample_answer。\n"
        f"{focus_line}\n"
        f"【候选人简历】\n{text}"
    )
