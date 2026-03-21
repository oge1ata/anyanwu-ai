const BACKEND_URL = "http://127.0.0.1:8000"; // Change this for production

const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

const STORAGE_KEY = "anyanwu_chat_messages";
let storedMessages = [];

function loadStoredMessages() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY) || "[]";
    storedMessages = JSON.parse(raw);
  } catch (e) {
    storedMessages = [];
  }
  // populate UI without re-saving
  storedMessages.forEach((m) => appendMessage(m.sender, m.text, m.type, false));
}

function saveMessage(sender, text, type) {
  storedMessages.push({ sender, text, type });
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(storedMessages));
  } catch (e) {
    // ignore storage failures (e.g., quota)
  }
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  // Show user message (appendMessage will persist)
  appendMessage("You", message, "user");
  userInput.value = "";

  try {
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error("Backend error");
    }

    const data = await response.json();
    appendMessage("Anyanwu ☀️", data.reply, "bot");

  } catch (error) {
    console.error(error);
    appendMessage(
      "System",
      "⚠️ Anyanwu is resting. Make sure the backend is running.",
      "bot"
    );
  }
}

function appendMessage(sender, text, type, save = true) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", type);

  const label = document.createElement("strong");
  label.textContent = `${sender}: `;
  const content = document.createTextNode(text);
  messageDiv.appendChild(label);
  messageDiv.appendChild(content);

  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (save) saveMessage(sender, text, type);
}

// Events
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// initialize
loadStoredMessages();

// On every page load, check if Anyanwu queued any scheduled messages while the app was closed
// (5am wake-up or 9pm check-in). They show up here in the chat automatically.
async function checkScheduledMessages() {
  try {
    const response = await fetch(`${BACKEND_URL}/check-in`);
    if (!response.ok) return;
    const data = await response.json();
    data.messages.forEach((msg) => appendMessage("Anyanwu ☀️", msg, "bot"));
  } catch (e) {
    // Backend not running — silently skip, don't clutter the UI
  }
}

checkScheduledMessages();

