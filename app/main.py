from pathlib import Path

from flask import Flask, jsonify, render_template, request

from app.agent import PersonalAgent
from app.storage import JsonStore


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "agent_memory.json"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
agent = PersonalAgent(JsonStore(str(DATA_FILE)))


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", ""))
    return jsonify(agent.reply(message))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
