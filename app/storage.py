import json
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.save({"todos": [], "notes": []})

    def load(self) -> dict[str, Any]:
        with self.file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, payload: dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
