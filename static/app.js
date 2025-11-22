// frontend/app.js (Optimized & Fixed Logout Version)

// Features: sidebar history, exercise card, typing indicator, chat layout, loading screen,
// frontend login with localStorage per user

const API_CHAT = "/api/chat";
const API_SUMMARIZE = "/api/summarize";

// const BASE_URL = "https://mindease-backend-pu3a.onrender.com";


// ---- State ----
let currentUser = null;
let chats = {};
let currentChatId = null;
let typingEl = null;

// ---- DOM ----
const loadingOverlay = document.getElementById("loading-overlay");
const chatListEl = document.getElementById("chat-list");
const chatWindow = document.getElementById("chat-window");
const sidebarSearch = document.getElementById("sidebar-search");
const newChatBtn = document.getElementById("new-chat-btn");
const loginBtn = document.getElementById("login-btn");
const logoutBtn = document.getElementById("logout-btn");
const userInfoEl = document.getElementById("user-info");
const loginModal = document.getElementById("login-modal");
const loginSubmit = document.getElementById("login-submit");
const loginCancel = document.getElementById("login-cancel");
const loginName = document.getElementById("login-name");
const loginEmail = document.getElementById("login-email");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const charCount = document.getElementById("char-count");
const exerciseCard = document.getElementById("exercise-card");
const exerciseText = document.getElementById("exercise-text");
const currentTitleEl = document.getElementById("current-chat-title");

// ***** Updated Logout Modal (Option B) *****
const logoutModal = document.getElementById("logout-modal");
const logoutCancel = document.getElementById("logout-cancel");
const logoutConfirm = document.getElementById("logout-confirm");

// ---- Keys ----
const USER_KEY = "mindease_user";
const chatsKeyFor = (email) => `mindease_chats_${email}`;

// ---- Helpers ----
function showLoading(on = true) {
  if (on) loadingOverlay.classList.remove("hidden");
  else loadingOverlay.classList.add("hidden");
}

function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function loadUser() {
  const s = localStorage.getItem(USER_KEY);
  return s ? JSON.parse(s) : null;
}

function clearUser() {
  localStorage.removeItem(USER_KEY);
  currentUser = null;
}

function saveChats() {
  if (!currentUser) return;
  localStorage.setItem(chatsKeyFor(currentUser.email), JSON.stringify(chats));
}

function loadChats() {
  if (!currentUser) return (chats = {});
  const stored = localStorage.getItem(chatsKeyFor(currentUser.email));
  chats = stored ? JSON.parse(stored) : {};
}

// ---- UI Rendering ----
function renderSidebar(filter = "") {
  chatListEl.innerHTML = "";
  const ids = Object.keys(chats).sort(
    (a, b) => (chats[b].updatedAt || 0) - (chats[a].updatedAt || 0)
  );

  ids.forEach((id) => {
    const c = chats[id];
    const item = document.createElement("div");
    item.className = "chat-item";

    if (filter && !c.title.toLowerCase().includes(filter.toLowerCase())) return;

    item.innerHTML = `
      <div class="meta">
        <div class="title">${escapeHtml(c.title || "New Chat")}</div>
        <small class="category-tag">${escapeHtml(c.category || "")}</small>
      </div>
      <div class="right">
        <button class="btn small" data-open="${id}">Open</button>
      </div>
    `;

    chatListEl.appendChild(item);
    item.querySelector("[data-open]").onclick = () => loadChat(id);
  });
}

function clearChatWindow() {
  chatWindow.innerHTML = "";
  exerciseCard.style.display = "none";
}

function renderMessage(role, text, ts = Date.now(), save = true) {
  const el = document.createElement("div");
  el.className = "message " + (role === "user" ? "user" : "assistant");

  const avatar = role === "user" ? "🙂" : "🤖";
  const time = new Date(ts).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  el.innerHTML = `
    <div class="meta-row">
      <div class="avatar">${avatar}</div>
      <div style="display:flex;flex-direction:column">
        <div style="font-size:14px">${role === "user" ? "You" : "MindEase"}</div>
        <small style="color:var(--muted)">${time}</small>
      </div>
    </div>
    <div class="bubble">${escapeHtml(text)}</div>
  `;

  chatWindow.appendChild(el);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  if (save && currentChatId && chats[currentChatId]) {
    chats[currentChatId].messages.push({
      sender: role === "user" ? "user" : "bot",
      text,
      ts,
    });
    chats[currentChatId].updatedAt = Date.now();
    if (currentUser) saveChats();
    renderSidebar();
  }
}

function showTyping() {
  if (typingEl) return;

  typingEl = document.createElement("div");
  typingEl.className = "message assistant typing";

  typingEl.innerHTML = `
    <div class="meta-row">
      <div class="avatar">🤖</div>
      <div style="display:flex;flex-direction:column">
        <div style="font-size:14px">MindEase</div>
        <small style="color:var(--muted)">${new Date().toLocaleTimeString()}</small>
      </div>
    </div>
    <div class="bubble"><div class="dots"><span></span><span></span><span></span></div></div>
  `;

  chatWindow.appendChild(typingEl);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTyping() {
  if (typingEl) {
    typingEl.remove();
    typingEl = null;
  }
}

function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

// ---- Chat Logic ----
const emotionMap = {
  sad: "Sadness",
  happy: "Happiness",
  anger: "Anger",
  stress: "Stress",
  anxiety: "Anxiety",
  fear: "Fear",
  neutral: "General",
};

function createNewChat(category = "General") {
  const id = "chat_" + Date.now();
  chats[id] = {
    title: "New Chat",
    category,
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };

  if (currentUser) saveChats();
  renderSidebar();
  loadChat(id, true);
  return id;
}

function loadChat(id, fresh = false) {
  if (!chats[id]) return;

  currentChatId = id;
  clearChatWindow();

  const c = chats[id];
  currentTitleEl.textContent = c.title || "Chat";

  if (c.messages.length === 0 && fresh) {
    renderMessage(
      "assistant",
      "Hello — I'm MindEase. How are you feeling today?",
      Date.now(),
      false
    );
    return;
  }

  c.messages.forEach((m) =>
    renderMessage(
      m.sender === "user" ? "user" : "assistant",
      m.text,
      m.ts,
      false
    )
  );

  if (c.lastExercise) {
    exerciseText.textContent = c.lastExercise;
    exerciseCard.style.display = "block";
  }
}

async function summarizeTitle(text) {
  if (!text) return null;
  try {
    const res = await fetch(`/api/summarize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) return null;
    const j = await res.json();
    return j.title || null;
  } catch {
    return null;
  }
}

// ---- Send Message ----
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  if (!currentChatId) {
    currentChatId = createNewChat("Analyzing...");
  }

  renderMessage("user", text);
  userInput.value = "";
  charCount.textContent = "0";

  showTyping();

  try {
    await new Promise((r) => setTimeout(r, 300));

    const res = await fetch(`/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUser ? currentUser.email : "anon",
        text,
      }),
    });

    removeTyping();

    if (!res.ok) {
      renderMessage("assistant", "Server error. Please try again.");
      return;
    }

    const data = await res.json();

    if (data.emotion && chats[currentChatId]) {
      const emo = data.emotion.toLowerCase();
      chats[currentChatId].category = emotionMap[emo] || emo;
    }

    if (data.type === "crisis") {
      renderMessage("assistant", data.message);
      return;
    }

    if (data.coach && data.coach.reply) {
      showTyping();
      await new Promise((r) =>
        setTimeout(r, 250 + Math.min(data.coach.reply.length * 6, 1000))
      );
      removeTyping();
      renderMessage("assistant", data.coach.reply);
    }

    const ex =
      data.exercise && data.exercise.exercise
        ? data.exercise.exercise
        : null;

    if (ex) {
      chats[currentChatId].lastExercise = ex;
      exerciseText.textContent = ex;
      exerciseCard.style.display = "block";
    } else {
      exerciseCard.style.display = "none";
    }

    if (
      chats[currentChatId] &&
      (!chats[currentChatId].title ||
        chats[currentChatId].title === "New Chat")
    ) {
      const title = await summarizeTitle(text);
      if (title) {
        chats[currentChatId].title = title;
        currentTitleEl.textContent = title;
      }
    }

    if (currentUser) saveChats();
    renderSidebar();
  } catch (e) {
    removeTyping();
    renderMessage("assistant", "Network or server error.");
  }
}

// ---- Login ----
function openLogin() {
  loginModal.style.display = "flex";
}
function closeLogin() {
  loginModal.style.display = "none";
}

function doLogin() {
  const name = loginName.value.trim();
  const email = loginEmail.value.trim().toLowerCase();

  if (!name || !email) return alert("Please enter name and email");

  currentUser = { name, email };
  saveUser(currentUser);
  loadChats();
  updateUserUI();
  closeLogin();
  renderSidebar();

  const ids = Object.keys(chats).sort(
    (a, b) => (chats[b].updatedAt || 0) - (chats[a].updatedAt || 0)
  );

  if (ids.length) loadChat(ids[0]);
}

// ---- Logout (Option B: Modal Confirm) ----
function openLogoutModal() {
  logoutModal.style.display = "flex";
}

function closeLogoutModal() {
  logoutModal.style.display = "none";
   currentTitleEl.textContent = "Wlecome";
}

function doLogout() {
  clearUser();
  chats = {};
  currentChatId = null;
  updateUserUI();
  renderSidebar();
 
  clearChatWindow();
}

// ---- Update UI ----
function updateUserUI() {
  if (currentUser) {
    userInfoEl.textContent = `${currentUser.name} — ${currentUser.email}`;
    loginBtn.style.display = "none";
    logoutBtn.style.display = "inline-block";
  } else {
    userInfoEl.textContent = "Not logged in";
    loginBtn.style.display = "inline-block";
    logoutBtn.style.display = "none";
  }
}

// ---- Events ----
newChatBtn.onclick = () => createNewChat("General");
sidebarSearch.oninput = () => renderSidebar(sidebarSearch.value);
loginBtn.onclick = openLogin;

// *** Updated Logout Buttons ***
logoutBtn.onclick = openLogoutModal;
logoutCancel.onclick = closeLogoutModal;
logoutConfirm.onclick = () => {

  closeLogoutModal();
  doLogout();
};

loginSubmit.onclick = doLogin;
loginCancel.onclick = closeLogin;

sendBtn.onclick = sendMessage;

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

userInput.addEventListener("input", () => {
  charCount.textContent = userInput.value.length;
  userInput.style.height = "auto";
  userInput.style.height = Math.min(140, userInput.scrollHeight) + "px";
});

// ---- FAST INIT ----
async function init() {
  showLoading(true);

  currentUser = loadUser();
  if (currentUser) loadChats();
  updateUserUI();
  renderSidebar();

  if (currentUser) {
    const ids = Object.keys(chats).sort(
      (a, b) => (chats[b].updatedAt || 0) - (chats[a].updatedAt || 0)
    );
    if (ids.length) loadChat(ids[0]);
  }

  requestAnimationFrame(() => showLoading(false));
}

init();
