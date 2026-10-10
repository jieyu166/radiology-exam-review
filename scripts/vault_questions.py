#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vault/questions 題卡的唯讀讀取器，供稽核／lint／抽取腳本共用。

解析規則全部重用 ``scripts/vault_site/compiler.py``（``discover_sources`` 與
``_question_projection``），本模組只把投影結果整理成扁平的 :class:`QuestionCard`，
不自行複製 frontmatter／選項／答案的解析邏輯。

欄位對應（相對於題卡 Markdown）：

* ``id``／``year``／``subspecialty``／``concepts``／``reference``：frontmatter。
  ``concepts`` 只取 frontmatter 清單（不含 body 的 ``[[wikilink]]``），
  ``reference`` 非字串時依 compiler 規則降級為 ``""``。
* ``stem``：``??`` 之前、第一個選項行之前的題幹，去掉開頭的 ``#tag`` 串。
* ``options``：``{"A": "...", ...}``，依 compiler 投影的選項行範圍切出，
  選項字母後的文字（含續行）；續行以換行相接。
* ``explanation``：``??`` 之後的全部原文（**含 ``**Ans: X**`` 行**與
  ``## 概念``／``![[...]]`` 等尾段），不做任何清理；呼叫端若需純詳解請自行過濾。
* ``correct_answer``：compiler 投影的 ``correctAnswer``；多重答案時以逗號串接
  ``acceptedAnswers``（例如 ``"B,D"``）；``answerStatus`` 為 unresolved／
  no_valid_answer 時為 ``""``。

略過規則：

* 只掃 ``vault/questions``（``kind == "question"``）。
* 底線開頭檔名與 ``publish: false`` 的題卡依 compiler 的排除原因略過（不警告）。
* 缺 ``??`` 邊界或 compiler 回報任何 hard error 的題卡：stderr 印一行警告
  （含 relative path 與錯誤代碼）並略過。
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vault_site.compiler import OPTION_RE, SourceNote, _question_projection, discover_sources  # noqa: E402

_LEADING_TAGS_RE = re.compile(r"^(?:#\S+\s*)+")


@dataclass
class QuestionCard:
    id: str
    year: list[int]
    subspecialty: str
    correct_answer: str
    concepts: list[str]
    reference: str
    stem: str
    options: dict[str, str] = field(default_factory=dict)
    explanation: str = ""
    path: Path = field(default_factory=Path)


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _as_year_list(value: Any) -> list[int]:
    years: list[int] = []
    for item in _as_str_list(value):
        try:
            years.append(int(item))
        except ValueError:
            continue
    return years


def _subspecialty(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(_as_str_list(value))
    return str(value).strip() if value is not None else ""


def _strip_option_prefix(line: str) -> str:
    match = OPTION_RE.match(line)
    return match.group(3).strip() if match else line.strip()


def _card_from_note(note: SourceNote, projection: dict[str, Any], concepts: list[str]) -> QuestionCard:
    lines = note.text.splitlines()
    front_start = projection["front"]["startLine"] - 1          # 0-based body start
    separator = projection["front"]["endLine"] - 1              # 0-based index of ``??``
    options_meta = projection["options"]
    first_option = options_meta[0]["startLine"] - 1 if options_meta else separator

    stem_lines = lines[front_start:first_option]
    stem = "\n".join(stem_lines).strip()
    stem = _LEADING_TAGS_RE.sub("", stem, count=1).strip()

    options: dict[str, str] = {}
    for meta in options_meta:
        start, end = meta["startLine"] - 1, meta["endLine"]
        chunk = lines[start:end]
        if not chunk:
            continue
        text_lines = [_strip_option_prefix(chunk[0])] + [item.strip() for item in chunk[1:]]
        options[meta["letter"]] = "\n".join(item for item in text_lines if item).strip()

    explanation = "\n".join(lines[projection["back"]["startLine"] - 1:]).strip()

    accepted = projection.get("acceptedAnswers") or []
    if projection.get("correctAnswer"):
        correct_answer = str(projection["correctAnswer"])
    else:
        correct_answer = ",".join(accepted)

    return QuestionCard(
        id=note.note_id,
        year=_as_year_list(note.frontmatter.get("year")),
        subspecialty=_subspecialty(note.frontmatter.get("subspecialty")),
        correct_answer=correct_answer,
        concepts=concepts,
        reference=str(projection.get("reference") or ""),
        stem=stem,
        options=options,
        explanation=explanation,
        path=note.source_path,
    )


def iter_question_cards(vault_root: Path) -> Iterator[QuestionCard]:
    """依 relative path 排序逐張產出 vault/questions 的 :class:`QuestionCard`。"""
    for note in discover_sources(Path(vault_root)):
        if note.kind != "question" or note.excluded_reason:
            continue
        # 先快照 frontmatter concepts：compiler 的 _question_projection 會把 body 的
        # [[wikilink]] 就地 append 進 note.frontmatter["concepts"]，之後再讀會混入 body 連結。
        concepts = _as_str_list(note.frontmatter.get("concepts"))
        projection, errors = _question_projection(note)
        if projection is None or errors:
            codes = ",".join(sorted({str(item.get("code")) for item in errors})) or "no_projection"
            print(f"[vault_questions] 略過 {note.relative_path}：{codes}", file=sys.stderr)
            continue
        yield _card_from_note(note, projection, concepts)


__all__ = ["QuestionCard", "iter_question_cards"]
