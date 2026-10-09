const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const exampleButtons = document.querySelectorAll(".example-btn");

function appendMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  article.appendChild(bubble);
  messagesEl.appendChild(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(message) {
  appendMessage("user", message);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    appendMessage("agent", data.reply || "暂时没有返回内容。");
  } catch (error) {
    appendMessage("agent", "请求失败，请检查服务是否已启动。");
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = inputEl.value.trim();
  if (!message) {
    return;
  }

  inputEl.value = "";
  await sendMessage(message);
});

exampleButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const message = button.dataset.message;
    if (message) {
      await sendMessage(message);
    }
  });
});
