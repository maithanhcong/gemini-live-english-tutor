// --- Main Application Logic & Gemini Live Integration ---

// 1. Lucide Icons SVG Refresh Utility
function refreshIcons() {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    try {
      window.lucide.createIcons();
    } catch (e) {
      console.debug("Lucide icon create error:", e);
    }
  }
}

// 2. Global Notyf Toast Notification Instance (Top-right on Desktop, Bottom-center on Mobile)
const notyf = typeof Notyf !== "undefined"
  ? new Notyf({
      duration: 3200,
      dismissible: true,
      position: {
        x: window.innerWidth < 768 ? "center" : "right",
        y: window.innerWidth < 768 ? "bottom" : "top",
      },
      types: [
        {
          type: "success",
          background: "#059669",
        },
        {
          type: "error",
          background: "#dc2626",
        },
      ],
    })
  : {
      success: (msg) => console.log("[Notyf Success]", msg),
      error: (msg) => console.error("[Notyf Error]", msg),
    };

// 3. SiriWave Voice Visualizer Controller
let siriWaveInstance = null;
let siriWaveDecayTimer = null;

function initVoiceVisualizer() {
  const container = document.getElementById("voice-visualizer");
  if (!container || typeof SiriWave === "undefined") return;
  container.innerHTML = "";
  try {
    siriWaveInstance = new SiriWave({
      container: container,
      style: "ios9",
      speed: 0.12,
      amplitude: 0.15,
      cover: true,
      autostart: true,
      curveDefinition: [
        { color: "56, 189, 248", supportLine: true },  // Sky blue
        { color: "99, 102, 241" },                     // Indigo
        { color: "16, 185, 129" },                     // Emerald
      ],
    });
  } catch (err) {
    console.warn("Could not init SiriWave visualizer:", err);
  }
}

function handleAudioVolumeLevel(rms, source) {
  if (!siriWaveInstance) return;
  // Dynamic scaling: min 0.15 (idle breathing) to max 2.8
  const targetAmp = Math.min(2.8, Math.max(0.15, 0.15 + rms * 14.0));
  siriWaveInstance.setAmplitude(targetAmp);

  const statusEl = document.getElementById("visualizerStatusText");
  if (statusEl) {
    if (rms > 0.02) {
      statusEl.textContent = source === "user" ? "Đang thu giọng của bạn..." : "Gia sư AI đang nói...";
    }
  }

  clearTimeout(siriWaveDecayTimer);
  siriWaveDecayTimer = setTimeout(() => {
    if (siriWaveInstance) siriWaveInstance.setAmplitude(0.15);
    if (statusEl) statusEl.textContent = "Đang sẵn sàng kết nối";
  }, 350);
}

const statusDiv = document.getElementById("status");
const interactionStatusDiv = document.getElementById("interaction-status");
const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");
const sessionEndSection = document.getElementById("session-end-section");
const restartBtn = document.getElementById("restartBtn");
const micBtn = document.getElementById("micBtn");
const cameraBtn = document.getElementById("cameraBtn");
const screenBtn = document.getElementById("screenBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const videoPreview = document.getElementById("video-preview");
const videoPlaceholder = document.getElementById("video-placeholder");
const connectBtn = document.getElementById("connectBtn");
const chatLog = document.getElementById("chat-log");

// Tab Navigation Elements
const navTabLive = document.getElementById("navTabLive");
const navTabTranslation = document.getElementById("navTabTranslation");
const tabContentLive = document.getElementById("tabContentLive");
const tabContentTranslation = document.getElementById("tabContentTranslation");

// Translation Workspace Elements
const btnSyncVocab = document.getElementById("btnSyncVocab");
const chkLearnedOnly = document.getElementById("chkLearnedOnly");
const btnGeneratePassage = document.getElementById("btnGeneratePassage");
const btnRandomToolbar = document.getElementById("btnRandomToolbar");
const statTotalWords = document.getElementById("statTotalWords");
const statLearnedWords = document.getElementById("statLearnedWords");
const statSelectedCount = document.getElementById("statSelectedCount");
const topicsContainer = document.getElementById("topicsContainer");
const vocabSearchInput = document.getElementById("vocabSearchInput");
const linkSelectAll = document.getElementById("linkSelectAll");
const linkDeselectAll = document.getElementById("linkDeselectAll");
const linkExpandAll = document.getElementById("linkExpandAll");
const linkCollapseAll = document.getElementById("linkCollapseAll");

const passageLoading = document.getElementById("passageLoading");
const passageCard = document.getElementById("passageCard");
const passageEmptyPlaceholder = document.getElementById("passageEmptyPlaceholder");
const passageUsedWords = document.getElementById("passageUsedWords");
const passageEnglishText = document.getElementById("passageEnglishText");
const btnSpeakPassage = document.getElementById("btnSpeakPassage");
const btnRandomPassage = document.getElementById("btnRandomPassage");
const txtUserTranslation = document.getElementById("txtUserTranslation");
const btnSubmitTranslation = document.getElementById("btnSubmitTranslation");
const saveStatusMsg = document.getElementById("saveStatusMsg");
const passageComparisonCard = document.getElementById("passageComparisonCard");
const compareStudentText = document.getElementById("compareStudentText");
const compareAiText = document.getElementById("compareAiText");
const btnNextRandomPassage = document.getElementById("btnNextRandomPassage");
const passageHistorySection = document.getElementById("passageHistorySection");
const passageHistoryList = document.getElementById("passageHistoryList");

// Live Sync Status Elements
const liveSyncStatusCard = document.getElementById("liveSyncStatusCard");
const liveSyncStatusText = document.getElementById("liveSyncStatusText");
const liveActiveSyncBar = document.getElementById("liveActiveSyncBar");
const liveActiveSyncText = document.getElementById("liveActiveSyncText");

// Authentication Elements
const btnOpenAuthModal = document.getElementById("btnOpenAuthModal");
const authModal = document.getElementById("authModal");
const btnCloseAuthModal = document.getElementById("btnCloseAuthModal");
const tabAuthLogin = document.getElementById("tabAuthLogin");
const tabAuthRegister = document.getElementById("tabAuthRegister");
const authModalTitle = document.getElementById("authModalTitle");
const authForm = document.getElementById("authForm");
const authUsername = document.getElementById("authUsername");
const authPassword = document.getElementById("authPassword");
const authErrorMsg = document.getElementById("authErrorMsg");
const authSuccessMsg = document.getElementById("authSuccessMsg");
const btnSubmitAuth = document.getElementById("btnSubmitAuth");
const btnSubmitAuthText = document.getElementById("btnSubmitAuthText");
const userGuestBox = document.getElementById("userGuestBox");
const userLoggedInBox = document.getElementById("userLoggedInBox");
const userAvatarChar = document.getElementById("userAvatarChar");
const headerUsername = document.getElementById("headerUsername");
const headerMasteredBadge = document.getElementById("headerMasteredBadge");
const btnLogout = document.getElementById("btnLogout");

// Mobile Bottom Sheet Elements
const btnToggleMobileVocabDrawer = document.getElementById("btnToggleMobileVocabDrawer");
const btnCloseMobileVocabDrawer = document.getElementById("btnCloseMobileVocabDrawer");
const btnDoneMobileVocab = document.getElementById("btnDoneMobileVocab");
const vocabSidebar = document.getElementById("vocabSidebar");
const vocabDrawerBackdrop = document.getElementById("vocabDrawerBackdrop");
const mobileSelectedCountHighlight = document.getElementById("mobileSelectedCountHighlight");
const sheetCountTag = document.getElementById("sheetCountTag");

// Generator Settings & Mobile Controls
const btnGeneratePassageMobile = document.getElementById("btnGeneratePassageMobile");
const btnRandomMobile = document.getElementById("btnRandomMobile");
const mobileSelectionHintText = document.getElementById("mobileSelectionHintText");
const levelPillsSelector = document.getElementById("levelPillsSelector");
const btnLengthMinus = document.getElementById("btnLengthMinus");
const btnLengthPlus = document.getElementById("btnLengthPlus");
const sentenceCountDisplay = document.getElementById("sentenceCountDisplay");
const sentenceLengthSlider = document.getElementById("sentenceLengthSlider");

// Generator Config State
let selectedDifficulty = "a0";
let selectedSentenceCount = 3;

function setSentenceCount(val) {
  const num = Math.max(2, Math.min(15, parseInt(val, 10) || 3));
  selectedSentenceCount = num;
  if (sentenceCountDisplay) sentenceCountDisplay.textContent = num;
  if (sentenceLengthSlider) sentenceLengthSlider.value = num;
}

// Auth State & Token Persistence
const AUTH_TOKEN_KEY = "study_auth_token";
let currentUser = null;
let isRegisterMode = false;

function getAuthHeaders() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

function setLoggedInUser(user, masteredCount = 0) {
  currentUser = user;
  if (userGuestBox) userGuestBox.classList.add("hidden");
  if (userLoggedInBox) userLoggedInBox.classList.remove("hidden");
  if (headerUsername) headerUsername.textContent = user.username || "Tài khoản";
  if (userAvatarChar) userAvatarChar.textContent = (user.username || "U").charAt(0).toUpperCase();
  if (headerMasteredBadge) {
    headerMasteredBadge.innerHTML = `<i data-lucide="target" class="lucide-icon"></i> ${masteredCount} từ đã học`;
    refreshIcons();
  }
}

function setLoggedOutUser() {
  currentUser = null;
  localStorage.removeItem(AUTH_TOKEN_KEY);
  if (userGuestBox) userGuestBox.classList.remove("hidden");
  if (userLoggedInBox) userLoggedInBox.classList.add("hidden");
  if (headerUsername) headerUsername.textContent = "";
  if (headerMasteredBadge) headerMasteredBadge.textContent = "";
}

async function checkAuthStatus() {
  try {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const headers = token ? { "Authorization": `Bearer ${token}` } : {};
    const res = await fetch("/api/auth/me", { headers });
    const data = await res.json();
    if (data.status === "authenticated" && data.user) {
      setLoggedInUser(data.user, data.mastered_count || 0);
    } else {
      setLoggedOutUser();
    }
  } catch (e) {
    console.warn("Auth check error:", e);
    setLoggedOutUser();
  }
}

// Mastered Words Persistence Helpers
const STORAGE_KEY_MASTERED_WORDS = "gemini_mastered_words";
let updateBackendDebounceTimer = null;

function loadMasteredWordsFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_MASTERED_WORDS);
    if (raw) {
      const arr = JSON.parse(raw);
      if (Array.isArray(arr) && arr.length > 0) {
        return new Set(arr);
      }
    }
  } catch (e) {
    console.warn("Storage load error:", e);
  }
  return new Set();
}

function saveMasteredWordsToStorage() {
  try {
    localStorage.setItem(
      STORAGE_KEY_MASTERED_WORDS,
      JSON.stringify(Array.from(selectedWordSet))
    );
  } catch (e) {
    console.warn("Storage save error:", e);
  }
  updateSyncBanners();

  // Debounced update to backend SQLite (isolated by user_id if logged in)
  clearTimeout(updateBackendDebounceTimer);
  updateBackendDebounceTimer = setTimeout(() => {
    fetch("/api/vocab/update-selection", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ selected_words: Array.from(selectedWordSet) }),
    }).catch((err) => console.debug("Error updating selection in backend:", err));
  }, 300);
}

function updateSyncBanners() {
  const count = selectedWordSet.size;
  if (liveSyncStatusText) {
    if (count > 0) {
      liveSyncStatusText.textContent = `${count} từ đã tích chọn (thành thạo) sẽ được loại trừ hoàn toàn, Gia sư AI chỉ luyện các từ còn lại.`;
    } else {
      liveSyncStatusText.textContent = `Hiện chưa có từ nào được tích chọn. Tích chọn từ ở tab Luyện Dịch để đánh dấu từ đã thành thạo.`;
    }
  }
  if (liveActiveSyncText) {
    if (count > 0) {
      liveActiveSyncText.textContent = `Đang loại trừ ${count} từ đã thành thạo từ tab Luyện Dịch (Gia sư AI sẽ không hỏi lại)`;
    } else {
      liveActiveSyncText.textContent = `Chưa có từ nào được loại trừ (Đang luyện toàn bộ lộ trình)`;
    }
  }
  if (mobileSelectedCountHighlight) {
    mobileSelectedCountHighlight.textContent = `Đang chọn: ${count} từ`;
  }
  if (sheetCountTag) {
    sheetCountTag.textContent = `${count} từ đã chọn`;
  }
  if (headerMasteredBadge && currentUser) {
    headerMasteredBadge.innerHTML = `<i data-lucide="target" class="lucide-icon"></i> ${count} từ đã học`;
    refreshIcons();
  }
}

function syncMasteredWordsToLive() {
  updateSyncBanners();
  const masteredList = Array.from(selectedWordSet);

  // 1. Send via WebSocket if connected
  if (geminiClient && geminiClient.isConnected()) {
    geminiClient.syncMasteredWords(masteredList);
  }

  // 2. Also send via REST API to persist state on server
  fetch("/api/vocab/sync-state", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ mastered_words: masteredList }),
  }).catch((err) => console.debug("Sync state REST error:", err));
}

// State
let currentGeminiMessageDiv = null;
let currentUserMessageDiv = null;
let syncedTopics = [];
let selectedWordSet = loadMasteredWordsFromStorage();
let openTopicSet = new Set([0]); // Default topic 0 open
let currentPassageData = null;
let sessionPassageHistory = [];

// Helper auto-select words when no words are ticked yet
function autoSelectDefaultWords() {
  if (syncedTopics && syncedTopics.length > 0) {
    // 1. Ưu tiên các từ đã đánh dấu 'Đã học = TRUE' trong Excel
    for (const topic of syncedTopics) {
      for (const w of topic.words) {
        if (w.learned) {
          selectedWordSet.add(w.word);
        }
      }
    }
    // 2. Nếu không có từ nào đánh dấu learned, lấy 5 từ đầu tiên
    if (selectedWordSet.size === 0) {
      let count = 0;
      for (const topic of syncedTopics) {
        for (const w of topic.words) {
          selectedWordSet.add(w.word);
          count++;
          if (count >= 5) break;
        }
        if (count >= 5) break;
      }
    }
    renderTopics();
    updateSelectedCount();
  }
}

// Cập nhật số lượng đếm từ ngay khi khởi tạo từ bộ nhớ đệm
try {
  updateSelectedCount();
} catch (e) {}

// Media & Live Client
const mediaHandler = new MediaHandler();
mediaHandler.onAudioVolume = handleAudioVolumeLevel;

let isSessionActive = false;

const geminiClient = new GeminiClient({
  onOpen: async () => {
    console.log("[Live] Socket opened");
    isSessionActive = true;
    statusDiv.textContent = "Connected";
    statusDiv.className = "status connected";
    authSection.classList.add("hidden");
    appSection.classList.remove("hidden");

    if (siriWaveInstance) {
      siriWaveInstance.start();
    }
    refreshIcons();

    updateSyncBanners();

    // Auto-start recording so tutor hears student right away
    try {
      await mediaHandler.startAudio((data) => {
        if (geminiClient.isConnected()) {
          geminiClient.send(data);
        }
      });
      micBtn.innerHTML = `<i data-lucide="mic-off" class="lucide-icon"></i> Stop Mic`;
      refreshIcons();
    } catch (e) {
      console.warn("[Live] Auto-start mic warning:", e);
    }

    console.log("[Live] Session ready");

    // Send personalized tutor intro instruction reflecting mastered words
    const masteredList = Array.from(selectedWordSet);
    let introPrompt = `System: Chào học viên ngắn gọn bằng tiếng Việt với vai trò Gia sư Tiếng Anh 1:1 cá nhân hóa. Giới thiệu bạn đồng hành theo Lộ trình 1000 từ vựng cốt lõi và Sổ tay phát âm. `;
    if (masteredList.length > 0) {
      introPrompt += `Học viên đã tích chọn thành thạo ${masteredList.length} từ ở tab Luyện Dịch. Gia sư tuyệt đối KHÔNG yêu cầu học viên đọc lại hay kiểm tra lại các từ này, mà hãy tập trung hỏi và luyện các từ còn lại chưa học. `;
    }
    introPrompt += `Hãy hỏi học viên hôm nay muốn bắt đầu luyện từ nào trong số các từ chưa học nhé!`;
    geminiClient.sendText(introPrompt);
  },
  onMessage: (event) => {
    if (typeof event.data === "string") {
      try {
        const msg = JSON.parse(event.data);
        handleJsonMessage(msg);
      } catch (e) {
        console.error("[Live] Parse error:", e);
      }
    } else {
      mediaHandler.playAudio(event.data);
    }
  },
  onClose: (e) => {
    console.log("[Live] Socket closed:", e);
    statusDiv.textContent = "Disconnected";
    statusDiv.className = "status disconnected";
    if (interactionStatusDiv) {
      interactionStatusDiv.className = "interaction-status hidden";
    }
    if (siriWaveInstance) {
      siriWaveInstance.stop();
    }
    if (isSessionActive) {
      showSessionEnd();
    } else {
      notyf.error("Không thể kết nối đến máy chủ đàm thoại Gemini Live.");
      resetUI();
    }
    isSessionActive = false;
  },
  onError: (e) => {
    console.error("[Live] WS Error:", e);
    statusDiv.textContent = "Connection Error";
    statusDiv.className = "status error";
  },
});

function handleJsonMessage(msg) {
  if (msg.type === "interaction_status") {
    if (interactionStatusDiv) {
      if (msg.status === "IN_PROGRESS") {
        interactionStatusDiv.textContent = "Processing...";
        interactionStatusDiv.className = "interaction-status in-progress";
      } else if (msg.status === "REQUIRES_ACTION") {
        interactionStatusDiv.textContent = "Ready";
        interactionStatusDiv.className = "interaction-status requires-action";
        currentGeminiMessageDiv = null;
        currentUserMessageDiv = null;
      }
    }
  } else if (msg.type === "interrupted") {
    mediaHandler.stopAudioPlayback();
    currentGeminiMessageDiv = null;
    currentUserMessageDiv = null;
  } else if (msg.type === "turn_complete") {
    currentGeminiMessageDiv = null;
    currentUserMessageDiv = null;
  } else if (msg.type === "user") {
    if (currentUserMessageDiv) {
      currentUserMessageDiv.textContent += msg.text;
      chatLog.scrollTop = chatLog.scrollHeight;
    } else {
      currentUserMessageDiv = appendMessage("user", msg.text);
    }
  } else if (msg.type === "gemini") {
    if (currentGeminiMessageDiv) {
      currentGeminiMessageDiv.textContent += msg.text;
      chatLog.scrollTop = chatLog.scrollHeight;
    } else {
      currentGeminiMessageDiv = appendMessage("gemini", msg.text);
    }
  }
}

function appendMessage(type, text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${type}`;
  msgDiv.textContent = text;
  chatLog.appendChild(msgDiv);
  chatLog.scrollTop = chatLog.scrollHeight;
  return msgDiv;
}

// Connect Button Handler
connectBtn.onclick = async () => {
  console.log("[Live] Requesting mic & audio setup...");
  statusDiv.textContent = "Connecting...";
  connectBtn.disabled = true;

  try {
    // 1. Request and verify microphone access upfront
    console.log("[Live] Requesting mic...");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      console.log("[Live] Mic permission granted.");
    } catch (micErr) {
      console.error("[Live] Mic permission denied/unavailable:", micErr);
      notyf.error("Vui lòng cấp quyền Microphone để bắt đầu!");
      statusDiv.textContent = "Cần cấp quyền Mic";
      statusDiv.className = "status error";
      connectBtn.disabled = false;
      return;
    }

    // 2. Initialize AudioContext and Worklet module
    await mediaHandler.initializeAudio();

    // 3. Connect WebSocket
    console.log("[Live] Socket connecting...");
    const masteredList = Array.from(selectedWordSet);
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    geminiClient.connect(masteredList, token);
  } catch (error) {
    console.error("[Live] Connection error:", error);
    notyf.error("Lỗi kết nối đàm thoại: " + (error.message || error));
    statusDiv.textContent = "Connection Failed: " + error.message;
    statusDiv.className = "status error";
    connectBtn.disabled = false;
  }
};

// Controls
disconnectBtn.onclick = () => {
  geminiClient.disconnect();
};

micBtn.onclick = async () => {
  if (mediaHandler.isRecording) {
    mediaHandler.stopAudio();
    micBtn.innerHTML = `<i data-lucide="mic" class="lucide-icon"></i> Start Mic`;
    refreshIcons();
  } else {
    try {
      await mediaHandler.startAudio((data) => {
        if (geminiClient.isConnected()) {
          geminiClient.send(data);
        }
      });
      micBtn.innerHTML = `<i data-lucide="mic-off" class="lucide-icon"></i> Stop Mic`;
      refreshIcons();
    } catch (e) {
      notyf.error("Không thể ghi âm microphone: " + e.message);
    }
  }
};

cameraBtn.onclick = async () => {
  if (cameraBtn.textContent.includes("Stop Camera")) {
    mediaHandler.stopVideo(videoPreview);
    cameraBtn.innerHTML = `<i data-lucide="video" class="lucide-icon"></i> Start Camera`;
    screenBtn.innerHTML = `<i data-lucide="monitor" class="lucide-icon"></i> Share Screen`;
    videoPlaceholder.classList.remove("hidden");
    refreshIcons();
  } else {
    if (mediaHandler.videoStream) {
      mediaHandler.stopVideo(videoPreview);
      screenBtn.innerHTML = `<i data-lucide="monitor" class="lucide-icon"></i> Share Screen`;
    }

    try {
      await mediaHandler.startVideo(videoPreview, (base64Data) => {
        if (geminiClient.isConnected()) {
          geminiClient.sendImage(base64Data);
        }
      });
      cameraBtn.innerHTML = `<i data-lucide="video-off" class="lucide-icon"></i> Stop Camera`;
      screenBtn.innerHTML = `<i data-lucide="monitor" class="lucide-icon"></i> Share Screen`;
      videoPlaceholder.classList.add("hidden");
      refreshIcons();
    } catch (e) {
      notyf.error("Không thể truy cập camera: " + e.message);
    }
  }
};

screenBtn.onclick = async () => {
  if (screenBtn.textContent.includes("Stop Sharing")) {
    mediaHandler.stopVideo(videoPreview);
    screenBtn.innerHTML = `<i data-lucide="monitor" class="lucide-icon"></i> Share Screen`;
    cameraBtn.innerHTML = `<i data-lucide="video" class="lucide-icon"></i> Start Camera`;
    videoPlaceholder.classList.remove("hidden");
    refreshIcons();
  } else {
    if (mediaHandler.videoStream) {
      mediaHandler.stopVideo(videoPreview);
      cameraBtn.innerHTML = `<i data-lucide="video" class="lucide-icon"></i> Start Camera`;
    }

    try {
      await mediaHandler.startScreen(
        videoPreview,
        (base64Data) => {
          if (geminiClient.isConnected()) {
            geminiClient.sendImage(base64Data);
          }
        },
        () => {
          screenBtn.innerHTML = `<i data-lucide="monitor" class="lucide-icon"></i> Share Screen`;
          videoPlaceholder.classList.remove("hidden");
          refreshIcons();
        }
      );
      screenBtn.innerHTML = `<i data-lucide="monitor-off" class="lucide-icon"></i> Stop Sharing`;
      cameraBtn.innerHTML = `<i data-lucide="video" class="lucide-icon"></i> Start Camera`;
      videoPlaceholder.classList.add("hidden");
      refreshIcons();
    } catch (e) {
      notyf.error("Không thể chia sẻ màn hình: " + e.message);
    }
  }
};

sendBtn.onclick = sendText;
textInput.onkeypress = (e) => {
  if (e.key === "Enter") sendText();
};

function sendText() {
  const text = textInput.value.trim();
  if (text && geminiClient.isConnected()) {
    geminiClient.sendText(text);
    appendMessage("user", text);
    textInput.value = "";
  }
}

function resetUI() {
  authSection.classList.remove("hidden");
  appSection.classList.add("hidden");
  sessionEndSection.classList.add("hidden");

  mediaHandler.stopAudio();
  mediaHandler.stopVideo(videoPreview);
  videoPlaceholder.classList.remove("hidden");

  micBtn.innerHTML = `<i data-lucide="mic" class="lucide-icon"></i> Start Mic`;
  cameraBtn.innerHTML = `<i data-lucide="video" class="lucide-icon"></i> Start Camera`;
  screenBtn.innerHTML = `<i data-lucide="monitor" class="lucide-icon"></i> Share Screen`;
  chatLog.innerHTML = "";
  connectBtn.disabled = false;
  refreshIcons();
}

function showSessionEnd() {
  appSection.classList.add("hidden");
  sessionEndSection.classList.remove("hidden");
  mediaHandler.stopAudio();
  mediaHandler.stopVideo(videoPreview);
}

restartBtn.onclick = () => {
  resetUI();
};

// ─── TAB SWITCHING LOGIC ────────────────────────────────────────────────────
navTabLive.onclick = () => {
  navTabLive.classList.add("active");
  navTabTranslation.classList.remove("active");
  tabContentLive.classList.remove("hidden");
  tabContentTranslation.classList.add("hidden");

  // Synchronize vocabulary state to backend / Live session
  syncMasteredWordsToLive();
  refreshIcons();
};

navTabTranslation.onclick = () => {
  navTabTranslation.classList.add("active");
  navTabLive.classList.remove("active");
  tabContentTranslation.classList.remove("hidden");
  tabContentLive.classList.add("hidden");

  // Auto sync if first time opened
  if (syncedTopics.length === 0) {
    syncVocabFromExcel();
  }
  refreshIcons();
};

// ─── TRANSLATION WORKSPACE: EXCEL SYNC & VOCABULARY SELECTION ───────────────
btnSyncVocab.onclick = () => {
  syncVocabFromExcel();
};

chkLearnedOnly.onchange = () => {
  syncVocabFromExcel();
};

async function syncVocabFromExcel() {
  btnSyncVocab.disabled = true;
  btnSyncVocab.innerHTML = `<span class="btn-icon"><i data-lucide="loader-2" class="lucide-icon spin"></i></span> Đang đồng bộ...`;
  refreshIcons();

  try {
    const learnedOnly = chkLearnedOnly.checked;
    const response = await fetch(`/api/vocab/sync?learned_only=${learnedOnly}`, {
      headers: getAuthHeaders(),
    });
    const data = await response.json();

    if (data.status === "success") {
      statTotalWords.textContent = data.total_words;
      statLearnedWords.textContent = data.learned_count;
      syncedTopics = data.topics || [];

      // Phục hồi chính xác trạng thái tích chọn từ CSDL SQLite theo user_id
      if (Array.isArray(data.selected_words) && data.selected_words.length > 0) {
        selectedWordSet = new Set(data.selected_words);
        try {
          localStorage.setItem(
            STORAGE_KEY_MASTERED_WORDS,
            JSON.stringify(data.selected_words)
          );
        } catch (e) {}
        updateSyncBanners();
      } else if (selectedWordSet.size === 0) {
        // Tự động tích chọn tất cả các từ đã học (TRUE) từ Excel để đồng bộ số lượng chính xác
        for (const topic of syncedTopics) {
          for (const w of topic.words) {
            if (w.learned) {
              selectedWordSet.add(w.word);
            }
          }
        }
        // Nếu không có từ nào đánh dấu learned, tự động chọn tất cả từ của các chủ đề hiện tại
        if (selectedWordSet.size === 0) {
          for (const topic of syncedTopics) {
            for (const w of topic.words) {
              selectedWordSet.add(w.word);
            }
          }
        }
        saveMasteredWordsToStorage();
      }

      renderTopics();
      updateSelectedCount();
      notyf.success(`Đã đồng bộ ${data.total_words} từ cốt lõi (${data.learned_count} từ đã học)!`);
    } else {
      notyf.error("Lỗi đồng bộ dữ liệu: " + (data.message || "Unknown error"));
    }
  } catch (err) {
    console.error("Sync error:", err);
    notyf.error("Không thể kết nối đến máy chủ để đọc dữ liệu từ vựng.");
  } finally {
    btnSyncVocab.disabled = false;
    btnSyncVocab.innerHTML = `<span class="btn-icon"><i data-lucide="refresh-cw" class="lucide-icon"></i></span> Đồng bộ từ Excel`;
    refreshIcons();
  }
}

function renderTopics() {
  const searchTerm = (vocabSearchInput.value || "").toLowerCase().trim();
  topicsContainer.innerHTML = "";

  if (syncedTopics.length === 0) {
    topicsContainer.innerHTML = `<div class="empty-state"><p>Không tìm thấy từ vựng nào phù hợp.</p></div>`;
    return;
  }

  const fragment = document.createDocumentFragment();

  syncedTopics.forEach((topic, tIdx) => {
    // Filter words matching search
    const filteredWords = topic.words.filter((w) => {
      if (!searchTerm) return true;
      return (
        w.word.toLowerCase().includes(searchTerm) ||
        w.meaning.toLowerCase().includes(searchTerm) ||
        w.ipa.toLowerCase().includes(searchTerm)
      );
    });

    if (filteredWords.length === 0) return;

    // If searching, auto-expand topics with matching results
    if (searchTerm) {
      openTopicSet.add(tIdx);
    }

    const isOpen = openTopicSet.has(tIdx);
    const topicGroup = document.createElement("div");
    topicGroup.className = `topic-group ${isOpen ? "open" : ""}`;

    // Header (Parent Row)
    const topicHeader = document.createElement("div");
    topicHeader.className = "topic-header";
    topicHeader.title = "Nhấp để mở rộng / thu gọn danh sách từ";

    const titleArea = document.createElement("div");
    titleArea.className = "topic-title-area";

    // Arrow indicator
    const arrow = document.createElement("span");
    arrow.className = "topic-arrow";
    arrow.innerHTML = `<i data-lucide="chevron-right" class="topic-chevron"></i>`;

    // Parent Checkbox (Cha)
    const chkTopic = document.createElement("input");
    chkTopic.type = "checkbox";
    chkTopic.className = "topic-checkbox";
    chkTopic.title = "Tích / Bỏ tích toàn bộ chủ đề này";

    const titleSpan = document.createElement("span");
    titleSpan.className = "topic-name";
    titleSpan.textContent = topic.name;

    titleArea.appendChild(arrow);
    titleArea.appendChild(chkTopic);
    titleArea.appendChild(titleSpan);

    const countBadge = document.createElement("span");
    countBadge.className = "topic-count-badge";

    topicHeader.appendChild(titleArea);
    topicHeader.appendChild(countBadge);

    // Body (Children Words List)
    const topicBody = document.createElement("div");
    topicBody.className = "topic-body";

    // Synchronize parent checkbox and badge state based on selected children
    const updateTopicState = () => {
      const selectedCount = filteredWords.filter((w) => selectedWordSet.has(w.word)).length;
      const total = filteredWords.length;

      if (selectedCount === total && total > 0) {
        chkTopic.checked = true;
        chkTopic.indeterminate = false;
        countBadge.className = "topic-count-badge all-selected";
        countBadge.textContent = `Đã chọn hết (${total})`;
      } else if (selectedCount > 0) {
        chkTopic.checked = false;
        chkTopic.indeterminate = true;
        countBadge.className = "topic-count-badge active";
        countBadge.textContent = `Đã chọn: ${selectedCount}/${total}`;
      } else {
        chkTopic.checked = false;
        chkTopic.indeterminate = false;
        countBadge.className = "topic-count-badge";
        countBadge.textContent = `${total} từ`;
      }
    };

    // Accordion Toggle: click anywhere on header (except the checkbox)
    topicHeader.onclick = (e) => {
      if (e.target === chkTopic) return;
      const willBeOpen = !topicGroup.classList.contains("open");
      topicGroup.classList.toggle("open", willBeOpen);
      if (willBeOpen) {
        openTopicSet.add(tIdx);
      } else {
        openTopicSet.delete(tIdx);
      }
    };

    // Parent Checkbox Handler (Cha -> All Con)
    chkTopic.onclick = (e) => {
      e.stopPropagation();
      const willSelect = chkTopic.checked;
      filteredWords.forEach((w) => {
        if (willSelect) selectedWordSet.add(w.word);
        else selectedWordSet.delete(w.word);
      });

      // Update all child rows directly in DOM
      topicBody.querySelectorAll(".word-row").forEach((rowEl, rIdx) => {
        const w = filteredWords[rIdx];
        if (!w) return;
        const isSel = selectedWordSet.has(w.word);
        rowEl.classList.toggle("selected", isSel);
        const cEl = rowEl.querySelector(".word-checkbox");
        if (cEl) cEl.checked = isSel;
      });

      updateTopicState();
      updateSelectedCount();
    };

    // Render Children Word Rows (Con)
    filteredWords.forEach((w) => {
      const isSelected = selectedWordSet.has(w.word);
      const row = document.createElement("div");
      row.className = `word-row ${isSelected ? "selected" : ""}`;

      const wChk = document.createElement("input");
      wChk.type = "checkbox";
      wChk.className = "word-checkbox";
      wChk.checked = isSelected;

      const toggleWord = (checked) => {
        if (checked) selectedWordSet.add(w.word);
        else selectedWordSet.delete(w.word);
        wChk.checked = checked;
        row.classList.toggle("selected", checked);
        updateTopicState();
        updateSelectedCount();
      };

      wChk.onclick = (e) => {
        e.stopPropagation();
        toggleWord(wChk.checked);
      };

      row.onclick = () => {
        toggleWord(!wChk.checked);
      };

      const meta = document.createElement("div");
      meta.className = "word-meta";

      const topLine = document.createElement("div");
      topLine.className = "word-top-line";

      const term = document.createElement("span");
      term.className = "word-term";
      term.textContent = w.word;

      const ipa = document.createElement("span");
      ipa.className = "word-ipa";
      ipa.textContent = w.ipa;

      const pos = document.createElement("span");
      pos.className = "word-pos";
      pos.textContent = `[${w.pos}]`;

      topLine.appendChild(term);
      if (w.ipa) topLine.appendChild(ipa);
      if (w.pos) topLine.appendChild(pos);

      const meaning = document.createElement("div");
      meaning.className = "word-meaning";
      meaning.textContent = w.meaning;

      meta.appendChild(topLine);
      meta.appendChild(meaning);

      row.appendChild(wChk);
      row.appendChild(meta);
      topicBody.appendChild(row);
    });

    // Initialize parent topic state
    updateTopicState();

    topicGroup.appendChild(topicHeader);
    topicGroup.appendChild(topicBody);
    fragment.appendChild(topicGroup);
  });

  topicsContainer.appendChild(fragment);
  refreshIcons();
}

function updateSelectedCount() {
  const count = selectedWordSet.size;
  statSelectedCount.textContent = count;
  if (mobileSelectedCountHighlight) {
    mobileSelectedCountHighlight.textContent = `Đang chọn: ${count} từ`;
  }
  if (sheetCountTag) {
    sheetCountTag.textContent = `${count} từ đã chọn`;
  }
  btnGeneratePassage.disabled = count === 0;
  if (btnRandomToolbar) btnRandomToolbar.disabled = count === 0;
  if (btnDoneMobileVocab) btnDoneMobileVocab.disabled = count === 0;
  // Cụm nút trên Mobile luôn giữ màu sắc nổi bật, sẵn sàng bấm (bấm khi 0 từ sẽ tự động chọn từ)
  if (btnGeneratePassageMobile) btnGeneratePassageMobile.disabled = false;
  if (btnRandomMobile) btnRandomMobile.disabled = false;
  if (mobileSelectionHintText) {
    mobileSelectionHintText.textContent = `Đang chọn: ${count} từ cốt lõi`;
  }
  saveMasteredWordsToStorage();
  if (geminiClient && geminiClient.isConnected()) {
    geminiClient.syncMasteredWords(Array.from(selectedWordSet));
  }
}

// Quick Select / Deselect All Handlers
linkSelectAll.onclick = () => {
  syncedTopics.forEach((t) => {
    t.words.forEach((w) => selectedWordSet.add(w.word));
  });
  renderTopics();
  updateSelectedCount();
};

linkDeselectAll.onclick = () => {
  selectedWordSet.clear();
  renderTopics();
  updateSelectedCount();
};

if (linkExpandAll) {
  linkExpandAll.onclick = () => {
    syncedTopics.forEach((_, idx) => openTopicSet.add(idx));
    renderTopics();
  };
}

if (linkCollapseAll) {
  linkCollapseAll.onclick = () => {
    openTopicSet.clear();
    renderTopics();
  };
}

vocabSearchInput.oninput = () => {
  renderTopics();
};

// ─── GENERATE PASSAGE & RANDOM EXERCISE FLOW ────────────────────────────────
async function requestGeneratePassage(randomChange = false) {
  if (selectedWordSet.size === 0) {
    autoSelectDefaultWords();
  }
  if (selectedWordSet.size === 0) {
    notyf.error("Vui lòng tích chọn ít nhất 1 từ vựng trong danh sách trước khi tạo bài tập.");
    return;
  }

  btnGeneratePassage.disabled = true;
  if (btnRandomToolbar) btnRandomToolbar.disabled = true;
  if (btnRandomPassage) btnRandomPassage.disabled = true;
  if (btnGeneratePassageMobile) btnGeneratePassageMobile.disabled = true;
  if (btnRandomMobile) btnRandomMobile.disabled = true;

  passageEmptyPlaceholder.classList.add("hidden");
  passageCard.classList.add("hidden");
  passageLoading.classList.remove("hidden");
  const loadingSub = document.getElementById("passageLoadingSubtext");
  if (loadingSub) {
    const lvlNames = {
      a0: "Khởi động (A0)",
      a1: "Căn bản (A1)",
      a2: "Sơ cấp (A2)",
      b1_minus: "Tiền trung cấp (B1-)",
      b1: "Trung cấp (B1)",
      beginner: "Khởi động (A0)",
      elementary: "Căn bản (A1)",
      intermediate: "Trung cấp (B1)",
    };
    loadingSub.textContent = `Đang lồng ghép từ vựng đã chọn vào đoạn văn ${selectedSentenceCount} câu (Mức độ: ${lvlNames[selectedDifficulty] || "Cơ bản"}).`;
  }
  if (passageComparisonCard) passageComparisonCard.classList.add("hidden");
  saveStatusMsg.textContent = "";

  const selectedList = Array.from(selectedWordSet);

  try {
    const res = await fetch("/api/passage/generate", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        selected_words: selectedList,
        random_change: randomChange,
        level: selectedDifficulty,
        sentence_count: selectedSentenceCount,
      }),
    });

    const data = await res.json();
    if (data.status === "success" && data.data) {
      currentPassageData = data.data;
      displayGeneratedPassage(currentPassageData);
      notyf.success("Đoạn văn AI đã sẵn sàng để luyện dịch!");
      refreshIcons();
    } else {
      notyf.error("Lỗi khi tạo đoạn văn: " + (data.message || "Unknown error"));
      passageEmptyPlaceholder.classList.remove("hidden");
    }
  } catch (err) {
    console.error("Passage generation error:", err);
    notyf.error("Không thể kết nối đến máy chủ: " + err.message);
    passageEmptyPlaceholder.classList.remove("hidden");
  } finally {
    passageLoading.classList.add("hidden");
    const hasSelection = selectedWordSet.size > 0;
    btnGeneratePassage.disabled = !hasSelection;
    if (btnRandomToolbar) btnRandomToolbar.disabled = !hasSelection;
    if (btnRandomPassage) btnRandomPassage.disabled = false;
    if (btnGeneratePassageMobile) btnGeneratePassageMobile.disabled = false;
    if (btnRandomMobile) btnRandomMobile.disabled = false;
  }
}

function displayGeneratedPassage(data) {
  // Target pills
  passageUsedWords.innerHTML = "";
  const words = data.used_words || [];
  words.forEach((w) => {
    const pill = document.createElement("span");
    pill.className = "target-pill";
    pill.textContent = w;
    passageUsedWords.appendChild(pill);
  });

  // Meta badge for level & sentence count
  const levelLabels = {
    a0: "Khởi động (A0)",
    a1: "Căn bản (A1)",
    a2: "Sơ cấp (A2)",
    b1_minus: "Tiền trung cấp (B1-)",
    b1: "Trung cấp (B1)",
    beginner: "Khởi động (A0)",
    elementary: "Căn bản (A1)",
    intermediate: "Trung cấp (B1)",
  };
  const lvlName = levelLabels[data.level || selectedDifficulty] || "Cơ bản";
  const sCount = data.sentence_count || selectedSentenceCount;
  const metaBadge = document.createElement("span");
  metaBadge.className = "target-meta-pill";
  metaBadge.innerHTML = `<i data-lucide="target" class="lucide-icon"></i> ${lvlName} (${sCount} câu)`;
  passageUsedWords.appendChild(metaBadge);
  refreshIcons();

  // English text
  passageEnglishText.textContent = data.english_passage || "";

  // Reset practice input & hide comparison card (bản dịch đáp án hoàn toàn ẩn lúc này)
  txtUserTranslation.value = "";
  saveStatusMsg.textContent = "";
  if (passageComparisonCard) passageComparisonCard.classList.add("hidden");

  passageCard.classList.remove("hidden");
}

// Speak English Passage aloud using browser SpeechSynthesis
btnSpeakPassage.onclick = () => {
  const text = passageEnglishText.textContent.trim();
  if (!text || !window.speechSynthesis) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.95; // Slightly slower for clear learning
  window.speechSynthesis.speak(utterance);
};

// ─── SUBMIT TRANSLATION & COMPARE (NỘP BÀI & ĐỐI CHIẾU ĐÁP ÁN) ───────────────
btnSubmitTranslation.onclick = async () => {
  if (!currentPassageData) return;
  const myTranslation = txtUserTranslation.value.trim();
  if (!myTranslation) {
    notyf.error("Vui lòng nhập bản dịch của bạn vào ô thực hành trước khi nộp bài!");
    txtUserTranslation.focus();
    return;
  }

  btnSubmitTranslation.disabled = true;
  btnSubmitTranslation.innerHTML = `<span class="btn-icon"><i data-lucide="loader-2" class="lucide-icon spin"></i></span> Đang chấm và đối chiếu...`;
  refreshIcons();
  saveStatusMsg.className = "save-status-msg";
  saveStatusMsg.textContent = "";

  try {
    const res = await fetch("/api/passage/submit-translation", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        used_words: (currentPassageData.used_words || []).join(", "),
        english_passage: currentPassageData.english_passage || "",
        vietnamese_translation: currentPassageData.vietnamese_translation || "",
        my_translation: myTranslation,
      }),
    });

    const data = await res.json();
    if (data.status === "success") {
      // 1. Hiển thị đối chiếu song song
      compareStudentText.textContent = myTranslation;
      compareAiText.textContent = currentPassageData.vietnamese_translation || data.vietnamese_translation;
      passageComparisonCard.classList.remove("hidden");

      // Cuộn êm đến bảng đối chiếu
      passageComparisonCard.scrollIntoView({ behavior: "smooth", block: "nearest" });

      // 2. Thêm vào lịch sử phiên làm việc
      addToSessionHistory({
        english_passage: currentPassageData.english_passage,
        vietnamese_translation: currentPassageData.vietnamese_translation,
        my_translation: myTranslation,
      });

      saveStatusMsg.className = "save-status-msg success";
      saveStatusMsg.innerHTML = `<i data-lucide="check-circle-2" class="lucide-icon"></i> Đã nộp bài và đối chiếu thành công!`;
      notyf.success("Đã nộp bài và đối chiếu đáp án thành công!");
    } else {
      saveStatusMsg.className = "save-status-msg error";
      saveStatusMsg.innerHTML = `<i data-lucide="alert-circle" class="lucide-icon"></i> Lỗi: ${data.message || "Không thể nộp bài"}`;
      notyf.error(data.message || "Không thể nộp bài");
    }
  } catch (err) {
    saveStatusMsg.className = "save-status-msg error";
    saveStatusMsg.innerHTML = `<i data-lucide="alert-circle" class="lucide-icon"></i> Lỗi kết nối: ${err.message}`;
    notyf.error("Lỗi kết nối: " + err.message);
  } finally {
    btnSubmitTranslation.disabled = false;
    btnSubmitTranslation.innerHTML = `<span class="btn-icon"><i data-lucide="send" class="lucide-icon"></i></span> Nộp bài & Đối chiếu đáp án`;
    refreshIcons();
  }
};

// Event Listeners for Passage Generation
btnGeneratePassage.onclick = () => requestGeneratePassage(false);
if (btnRandomToolbar) btnRandomToolbar.onclick = () => requestGeneratePassage(true);
if (btnRandomPassage) btnRandomPassage.onclick = () => requestGeneratePassage(true);
if (btnNextRandomPassage) btnNextRandomPassage.onclick = () => requestGeneratePassage(true);

// Mobile Generator Action Buttons
if (btnGeneratePassageMobile) {
  btnGeneratePassageMobile.onclick = () => {
    if (selectedWordSet.size === 0) {
      autoSelectDefaultWords();
    }
    requestGeneratePassage(false);
  };
}
if (btnRandomMobile) {
  btnRandomMobile.onclick = () => {
    if (selectedWordSet.size === 0) {
      autoSelectDefaultWords();
    }
    requestGeneratePassage(true);
  };
}

// Generator Settings Listeners (Difficulty Pills & Length Controls)
if (levelPillsSelector) {
  const pills = levelPillsSelector.querySelectorAll(".level-pill");
  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      pills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      selectedDifficulty = pill.dataset.level || "a0";
    });
  });
}

if (btnLengthMinus) {
  btnLengthMinus.addEventListener("click", () => {
    setSentenceCount(selectedSentenceCount - 1);
  });
}

if (btnLengthPlus) {
  btnLengthPlus.addEventListener("click", () => {
    setSentenceCount(selectedSentenceCount + 1);
  });
}

if (sentenceLengthSlider) {
  sentenceLengthSlider.addEventListener("input", (e) => {
    setSentenceCount(e.target.value);
  });
}

function addToSessionHistory(data) {
  sessionPassageHistory.unshift(data);
  passageHistorySection.classList.remove("hidden");
  passageHistoryList.innerHTML = "";

  sessionPassageHistory.slice(0, 5).forEach((item) => {
    const histItem = document.createElement("div");
    histItem.className = "history-item";

    const eng = document.createElement("div");
    eng.className = "history-eng";
    eng.textContent = item.english_passage;

    const vie = document.createElement("div");
    vie.className = "history-vie";
    vie.textContent = `→ ${item.vietnamese_translation}`;

    histItem.appendChild(eng);
    histItem.appendChild(vie);
    passageHistoryList.appendChild(histItem);
  });
}

// ─── AUTH MODAL & FORM HANDLERS ─────────────────────────────────────────────
function openAuthModal(register = false) {
  isRegisterMode = register;
  switchAuthTab(register);
  if (authErrorMsg) authErrorMsg.classList.add("hidden");
  if (authSuccessMsg) authSuccessMsg.classList.add("hidden");
  if (authUsername) authUsername.value = "";
  if (authPassword) authPassword.value = "";
  if (authModal) authModal.classList.remove("hidden");
  refreshIcons();
  setTimeout(() => { if (authUsername) authUsername.focus(); }, 100);
}

function closeAuthModal() {
  if (authModal) authModal.classList.add("hidden");
}

function switchAuthTab(register) {
  isRegisterMode = register;
  if (register) {
    if (tabAuthRegister) tabAuthRegister.classList.add("active");
    if (tabAuthLogin) tabAuthLogin.classList.remove("active");
    if (authModalTitle) authModalTitle.textContent = "Đăng Ký Tài Khoản";
    if (btnSubmitAuthText) btnSubmitAuthText.textContent = "Đăng Ký & Bắt Đầu Học";
  } else {
    if (tabAuthLogin) tabAuthLogin.classList.add("active");
    if (tabAuthRegister) tabAuthRegister.classList.remove("active");
    if (authModalTitle) authModalTitle.textContent = "Đăng Nhập Tài Khoản";
    if (btnSubmitAuthText) btnSubmitAuthText.textContent = "Đăng Nhập Ngay";
  }
  if (authErrorMsg) authErrorMsg.classList.add("hidden");
  if (authSuccessMsg) authSuccessMsg.classList.add("hidden");
  refreshIcons();
}

if (btnOpenAuthModal) btnOpenAuthModal.onclick = () => openAuthModal(false);
if (btnCloseAuthModal) btnCloseAuthModal.onclick = closeAuthModal;
if (tabAuthLogin) tabAuthLogin.onclick = () => switchAuthTab(false);
if (tabAuthRegister) tabAuthRegister.onclick = () => switchAuthTab(true);

if (authModal) {
  authModal.onclick = (e) => {
    if (e.target === authModal) closeAuthModal();
  };
}

if (authForm) {
  authForm.onsubmit = async (e) => {
    e.preventDefault();
    const username = (authUsername.value || "").trim();
    const password = (authPassword.value || "").trim();

    if (!username || username.length < 3) {
      showAuthError("Tên đăng nhập phải có ít nhất 3 ký tự.");
      notyf.error("Tên đăng nhập phải có ít nhất 3 ký tự.");
      return;
    }
    if (!password || password.length < 4) {
      showAuthError("Mật khẩu phải có ít nhất 4 ký tự.");
      notyf.error("Mật khẩu phải có ít nhất 4 ký tự.");
      return;
    }

    btnSubmitAuth.disabled = true;
    const origText = btnSubmitAuthText.textContent;
    btnSubmitAuthText.textContent = "Đang xử lý...";
    if (authErrorMsg) authErrorMsg.classList.add("hidden");

    try {
      const endpoint = isRegisterMode ? "/api/auth/register" : "/api/auth/login";
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();

      if (data.status === "success") {
        if (data.token) {
          localStorage.setItem(AUTH_TOKEN_KEY, data.token);
        }
        setLoggedInUser(data.user, data.mastered_count || 0);
        closeAuthModal();
        notyf.success(isRegisterMode ? "Đăng ký tài khoản thành công!" : `Đăng nhập thành công! Chào mừng ${data.user?.username || "học viên"}`);
        // Xóa sạch trạng thái cũ và tải lại chính xác trạng thái từ vựng riêng của người dùng mới này
        selectedWordSet.clear();
        await syncVocabFromExcel();
      } else {
        showAuthError(data.message || "Đã xảy ra lỗi. Vui lòng thử lại.");
        notyf.error(data.message || "Đã xảy ra lỗi. Vui lòng thử lại.");
      }
    } catch (err) {
      showAuthError("Không thể kết nối đến máy chủ: " + err.message);
      notyf.error("Không thể kết nối đến máy chủ: " + err.message);
    } finally {
      btnSubmitAuth.disabled = false;
      btnSubmitAuthText.textContent = origText;
    }
  };
}

function showAuthError(msg) {
  if (authErrorMsg) {
    authErrorMsg.textContent = msg;
    authErrorMsg.classList.remove("hidden");
  }
}

if (btnLogout) {
  btnLogout.onclick = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: getAuthHeaders(),
      });
    } catch (e) {
      console.warn("Logout error:", e);
    }
    setLoggedOutUser();
    selectedWordSet.clear();
    notyf.success("Đã đăng xuất tài khoản.");
    await syncVocabFromExcel();
  };
}

// ─── MOBILE VOCAB BOTTOM SHEET / MODAL HANDLERS ─────────────────────────────
function openMobileVocabSheet() {
  if (vocabSidebar) {
    vocabSidebar.classList.add("show-drawer");
    vocabSidebar.classList.add("mobile-open");
    vocabSidebar.classList.add("active");
  }
  if (vocabDrawerBackdrop) {
    vocabDrawerBackdrop.classList.remove("hidden");
    vocabDrawerBackdrop.classList.add("active");
  }
  document.body.style.overflow = "hidden";
}

function closeMobileVocabSheet() {
  if (vocabSidebar) {
    vocabSidebar.classList.remove("show-drawer");
    vocabSidebar.classList.remove("mobile-open");
    vocabSidebar.classList.remove("active");
  }
  if (vocabDrawerBackdrop) {
    vocabDrawerBackdrop.classList.add("hidden");
    vocabDrawerBackdrop.classList.remove("active");
  }
  document.body.style.overflow = "";
  updateSelectedCount();
  updateSyncBanners();
}

if (btnToggleMobileVocabDrawer) {
  btnToggleMobileVocabDrawer.onclick = openMobileVocabSheet;
}

if (btnCloseMobileVocabDrawer) {
  btnCloseMobileVocabDrawer.onclick = closeMobileVocabSheet;
}

if (btnDoneMobileVocab) {
  btnDoneMobileVocab.onclick = () => {
    closeMobileVocabSheet();
    if (selectedWordSet.size > 0) {
      requestGeneratePassage(false);
    }
  };
}

if (vocabDrawerBackdrop) {
  vocabDrawerBackdrop.onclick = closeMobileVocabSheet;
}

const btnPlaceholderOpenDrawer = document.getElementById("btnPlaceholderOpenDrawer");
if (btnPlaceholderOpenDrawer) {
  btnPlaceholderOpenDrawer.onclick = () => {
    if (window.innerWidth < 768) {
      openMobileVocabSheet();
    } else {
      const search = document.getElementById("vocabSearchInput");
      if (search) search.focus();
    }
  };
}

const btnPlaceholderStartGenerate = document.getElementById("btnPlaceholderStartGenerate");
if (btnPlaceholderStartGenerate) {
  btnPlaceholderStartGenerate.onclick = () => {
    if (selectedWordSet.size === 0) {
      autoSelectDefaultWords();
    }
    requestGeneratePassage(false);
  };
}

// Tự động đóng Bottom Sheet khi xoay ngang hoặc mở rộng màn hình lên Tablet / iPad (>= 768px)
window.addEventListener("resize", () => {
  if (window.innerWidth >= 768) {
    closeMobileVocabSheet();
  }
});

// ─── INITIAL APP STARTUP ────────────────────────────────────────────────────
initVoiceVisualizer();
refreshIcons();

checkAuthStatus().finally(() => {
  updateSyncBanners();
  syncVocabFromExcel();
  refreshIcons();
});

