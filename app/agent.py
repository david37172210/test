from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from app.storage import JsonStore


class PersonalAgent:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def reply(self, message: str) -> dict[str, Any]:
        text = message.strip()
        if not text:
            return {"reply": "请输入内容，我可以帮你记笔记、管理待办、查看今日摘要。"}

        data = self.store.load()

        note_text = self._extract_note(text)
        if note_text:
            data["notes"].append(
                {
                    "content": note_text,
                    "created_at": self._now_text(),
                }
            )
            self.store.save(data)
            return {"reply": f"已帮你记下：{note_text}"}

        todo_text = self._extract_todo(text)
        if todo_text:
            data["todos"].append(
                {
                    "title": todo_text,
                    "done": False,
                    "created_at": self._now_text(),
                }
            )
            self.store.save(data)
            return {"reply": f"已添加待办：{todo_text}"}

        finish_index = self._extract_finish_index(text)
        if finish_index is not None:
            if 0 <= finish_index < len(data["todos"]):
                data["todos"][finish_index]["done"] = True
                self.store.save(data)
                return {
                    "reply": f"已完成待办：{data['todos'][finish_index]['title']}"
                }
            return {"reply": "没有找到对应编号的待办，请先用“查看待办”确认序号。"}

        if self._want_list_todos(text):
            return {"reply": self._format_todos(data["todos"])}

        if self._want_summary(text):
            return {"reply": self._format_summary(data)}

        if self._want_notes(text):
            return {"reply": self._format_notes(data["notes"])}

        if self._want_profile(text):
            return {
                "reply": (
                    "我是你的个人 Agent 示例版，当前支持 4 类能力："
                    "聊天引导、记录笔记、管理待办、输出今日摘要。"
                )
            }

        return {
            "reply": (
                "我已经收到你的消息。你可以试试这些指令：\n"
                "1. 记住：明天和小王开会\n"
                "2. 添加待办：整理简历\n"
                "3. 查看待办\n"
                "4. 完成待办 1\n"
                "5. 今日摘要"
            )
        }

    def _extract_note(self, text: str) -> str | None:
        patterns = [
            r"^(?:记住|帮我记一下|记录一下)[:：]?\s*(.+)$",
            r"^备注[:：]?\s*(.+)$",
        ]
        return self._match_first(patterns, text)

    def _extract_todo(self, text: str) -> str | None:
        patterns = [
            r"^(?:添加待办|新增待办|加入待办)[:：]?\s*(.+)$",
            r"^待办[:：]?\s*(.+)$",
        ]
        return self._match_first(patterns, text)

    def _extract_finish_index(self, text: str) -> int | None:
        match = re.search(r"(?:完成待办|完成事项)[:：]?\s*(\d+)", text)
        if not match:
            return None
        return int(match.group(1)) - 1

    def _want_list_todos(self, text: str) -> bool:
        keywords = ["查看待办", "列出待办", "我的待办", "待办列表"]
        return any(keyword in text for keyword in keywords)

    def _want_notes(self, text: str) -> bool:
        keywords = ["查看笔记", "我的笔记", "笔记列表"]
        return any(keyword in text for keyword in keywords)

    def _want_summary(self, text: str) -> bool:
        keywords = ["今日摘要", "今天总结", "今日总结", "总结一下"]
        return any(keyword in text for keyword in keywords)

    def _want_profile(self, text: str) -> bool:
        keywords = ["你是谁", "你能做什么", "个人信息", "agent介绍"]
        return any(keyword in text.lower() for keyword in keywords)

    def _format_todos(self, todos: list[dict[str, Any]]) -> str:
        if not todos:
            return "当前还没有待办事项。"

        lines = ["你的待办如下："]
        for index, todo in enumerate(todos, start=1):
            status = "已完成" if todo["done"] else "未完成"
            lines.append(f"{index}. [{status}] {todo['title']}")
        return "\n".join(lines)

    def _format_notes(self, notes: list[dict[str, Any]]) -> str:
        if not notes:
            return "当前还没有笔记。"

        lines = ["你的笔记如下："]
        for index, note in enumerate(notes[-5:], start=1):
            lines.append(f"{index}. {note['content']} ({note['created_at']})")
        return "\n".join(lines)

    def _format_summary(self, data: dict[str, Any]) -> str:
        total = len(data["todos"])
        completed = sum(1 for item in data["todos"] if item["done"])
        pending = total - completed
        notes = len(data["notes"])
        return (
            "今日摘要：\n"
            f"- 待办总数：{total}\n"
            f"- 已完成：{completed}\n"
            f"- 未完成：{pending}\n"
            f"- 已记录笔记：{notes}"
        )

    def _match_first(self, patterns: list[str], text: str) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def _now_text(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
