/**
 * 3D Bharat Chatbot Widget
 * Include on any page with: <script src="chatbot-widget.js"></script>
 * (also requires config.js to be loaded first, for window.API_BASE_URL)
 */
(function () {
  const API_BASE = window.API_BASE_URL || "http://localhost:5000";
  let conversationHistory = [];

  // ---- Styles ----
  const style = document.createElement("style");
  style.textContent = `
    #bharat-chat-toggle {
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      width: 60px; height: 60px; border-radius: 50%;
      background: #b8860b; color: white; border: none;
      font-size: 26px; cursor: pointer; box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }
    #bharat-chat-panel {
      position: fixed; bottom: 96px; right: 24px; z-index: 9999;
      width: 340px; max-width: 90vw; height: 460px; max-height: 70vh;
      background: #1e1e1e; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);
      display: none; flex-direction: column; overflow: hidden;
      font-family: Arial, sans-serif; color: #fff;
    }
    #bharat-chat-panel.open { display: flex; }
    #bharat-chat-header {
      background: #b8860b; padding: 12px 16px; font-weight: bold;
      display: flex; justify-content: space-between; align-items: center;
    }
    #bharat-chat-close { cursor: pointer; background: none; border: none; color: white; font-size: 18px; }
    #bharat-chat-messages {
      flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px;
    }
    .bharat-msg { max-width: 85%; padding: 8px 12px; border-radius: 10px; font-size: 14px; line-height: 1.4; }
    .bharat-msg.user { align-self: flex-end; background: #b8860b; color: white; }
    .bharat-msg.bot { align-self: flex-start; background: #333; color: #eee; }
    #bharat-chat-inputrow { display: flex; border-top: 1px solid #333; }
    #bharat-chat-input {
      flex: 1; border: none; padding: 10px; font-size: 14px; background: #2a2a2a; color: white;
    }
    #bharat-chat-input:focus { outline: none; }
    #bharat-chat-send {
      background: #b8860b; color: white; border: none; padding: 0 16px; cursor: pointer; font-size: 14px;
    }
  `;
  document.head.appendChild(style);

  // ---- Markup ----
  const toggleBtn = document.createElement("button");
  toggleBtn.id = "bharat-chat-toggle";
  toggleBtn.innerText = "💬";

  const panel = document.createElement("div");
  panel.id = "bharat-chat-panel";
  panel.innerHTML = `
    <div id="bharat-chat-header">
      <span>3D Bharat Assistant</span>
      <button id="bharat-chat-close">✕</button>
    </div>
    <div id="bharat-chat-messages"></div>
    <div id="bharat-chat-inputrow">
      <input id="bharat-chat-input" type="text" placeholder="Ask about a place, or how to book..." />
      <button id="bharat-chat-send">Send</button>
    </div>
  `;

  document.body.appendChild(toggleBtn);
  document.body.appendChild(panel);

  const messagesEl = panel.querySelector("#bharat-chat-messages");
  const inputEl = panel.querySelector("#bharat-chat-input");
  const sendBtn = panel.querySelector("#bharat-chat-send");
  const closeBtn = panel.querySelector("#bharat-chat-close");

  function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = `bharat-msg ${sender}`;
    div.innerText = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function openPanel() {
    panel.classList.add("open");
    if (messagesEl.children.length === 0) {
      addMessage("Namaste! Ask me about any historical place, or how to book a trip, take a quiz, or find your way around.", "bot");
    }
    inputEl.focus();
  }

  toggleBtn.addEventListener("click", () => {
    panel.classList.contains("open") ? panel.classList.remove("open") : openPanel();
  });
  closeBtn.addEventListener("click", () => panel.classList.remove("open"));

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;
    addMessage(text, "user");
    inputEl.value = "";
    conversationHistory.push({ role: "user", text });

    const thinking = document.createElement("div");
    thinking.className = "bharat-msg bot";
    thinking.innerText = "...";
    messagesEl.appendChild(thinking);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    try {
      const res = await fetch(`${API_BASE}/api/chatbot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: conversationHistory }),
      });
      const data = await res.json();
      thinking.remove();
      const reply = data.reply || data.error || "Something went wrong.";
      addMessage(reply, "bot");
      conversationHistory.push({ role: "model", text: reply });
    } catch (err) {
      thinking.remove();
      addMessage("Could not reach the chatbot server. Is the backend running?", "bot");
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });
})();
