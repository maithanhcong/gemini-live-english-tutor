// --- Main Application Logic & Gemini Live Integration ---

// Safe Lucide Icons Creation Wrapper (Resolves Race Condition on Safari/WebKit)
function safeCreateIcons() {
  if (typeof window !== "undefined" && window.lucide && typeof window.lucide.createIcons === "function") {
    try {
      window.lucide.createIcons();
      return true;
    } catch (err) {
      console.warn("[Lucide] Render warning:", err);
      return false;
    }
  } else if (typeof lucide !== "undefined" && lucide && typeof lucide.createIcons === "function") {
    try {
      lucide.createIcons();
      return true;
    } catch (err) {
      console.warn("[Lucide] Render warning:", err);
      return false;
    }
  } else {
    // Retry shortly if the script was still parsing on WebKit/Safari
    setTimeout(() => {
      if (typeof window !== "undefined" && window.lucide && typeof window.lucide.createIcons === "function") {
        try { window.lucide.createIcons(); } catch (e) {}
      }
    }, 100);
    setTimeout(() => {
      if (typeof window !== "undefined" && window.lucide && typeof window.lucide.createIcons === "function") {
        try { window.lucide.createIcons(); } catch (e) {}
      }
    }, 400);
    return false;
  }
}

// Global alias for compatibility
const refreshIcons = safeCreateIcons;

// Ensure icons render safely once window load completes
window.addEventListener("load", () => {
  safeCreateIcons();
});

// 1.1 Safe HTML Escaper Utility
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
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
      speed: 0.14,
      amplitude: 0.15,
      cover: true,
      autostart: true,
      curveDefinition: [
        { color: "56, 189, 248", supportLine: true },  // Sky blue
        { color: "99, 102, 241" },                     // Indigo
        { color: "16, 185, 129" },                     // Emerald
      ],
    });
    window.siriWave = siriWaveInstance;
    siriWaveInstance.start();
  } catch (err) {
    console.warn("Could not init SiriWave visualizer:", err);
  }
}

function handleAudioVolumeLevel(rms, source) {
  let amplitude = Math.min(Math.max(rms * 15, 0.15), 3.0);
  if (window.siriWave) {
    window.siriWave.setAmplitude(amplitude);
  } else if (siriWaveInstance) {
    siriWaveInstance.setAmplitude(amplitude);
  }

  const statusEl = document.getElementById("visualizerStatusText");
  if (statusEl && rms > 0.015) {
    statusEl.textContent = source === "user" ? "Đang thu giọng của bạn..." : "Gia sư AI đang nói...";
  }

  clearTimeout(siriWaveDecayTimer);
  siriWaveDecayTimer = setTimeout(() => {
    if (window.siriWave) window.siriWave.setAmplitude(0.15);
    else if (siriWaveInstance) siriWaveInstance.setAmplitude(0.15);
    if (statusEl) statusEl.textContent = isSessionActive ? "Đang lắng nghe bạn..." : "Đang sẵn sàng kết nối";
  }, 280);
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

// Focus Word HUD & Pronunciation Feedback Elements
const liveFocusWordHUD = document.getElementById("liveFocusWordHUD");
const focusWordLevel = document.getElementById("focusWordLevel");
const focusWordTerm = document.getElementById("focusWordTerm");
const focusWordIpa = document.getElementById("focusWordIpa");
const focusWordPos = document.getElementById("focusWordPos");
const focusWordMeaning = document.getElementById("focusWordMeaning");
const liveFeedbackBox = document.getElementById("liveFeedbackBox");
const liveFeedbackText = document.getElementById("liveFeedbackText");

// Tab Navigation Elements (4 Tabs: Home, Live, Translation, Studio)
const navTabHome = document.getElementById("navTabHome");
const navTabLive = document.getElementById("navTabLive");
const navTabTranslation = document.getElementById("navTabTranslation");
const navTabStudio = document.getElementById("navTabStudio");
const tabContentHome = document.getElementById("tabContentHome");
const tabContentLive = document.getElementById("tabContentLive");
const tabContentTranslation = document.getElementById("tabContentTranslation");
const tabContentStudio = document.getElementById("tabContentStudio");

// Quick Action Elements on Home Tab
const btnHomeActionLive = document.getElementById("btnHomeActionLive");
const btnDashboardReadingAction = document.getElementById("btnDashboardReadingAction");
const btnExportBackup = document.getElementById("btnExportBackup");

// Translation Workspace Elements
const btnSyncVocab = document.getElementById("btnSyncVocab");
const chkLearnedOnly = document.getElementById("chkLearnedOnly");
const chkLearnedOnlyDrawer = document.getElementById("chkLearnedOnlyDrawer");
const btnGeneratePassage = document.getElementById("btnGeneratePassage");
const btnRandomToolbar = document.getElementById("btnRandomToolbar");
const statTotalWords = document.getElementById("statTotalWords");
const statLearnedWords = document.getElementById("statLearnedWords");
const statSelectedCount = document.getElementById("statSelectedCount");
const topicsContainer = document.getElementById("topicsContainer");
const vocabSearchInput = document.getElementById("vocabSearchInput");
const btnClearVocabSearch = document.getElementById("btnClearVocabSearch");
const inputCustomWord = document.getElementById("inputCustomWord");
const btnAddCustomWord = document.getElementById("btnAddCustomWord");
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
const btnOpenRegisterModal = document.getElementById("btnOpenRegisterModal");

// Dashboard & Micro-Quiz Elements
const dashboardProgressBar = document.getElementById("dashboardProgressBar");
const dashboardProgressText = document.getElementById("dashboardProgressText");
const btnDashboardQuizAction = document.getElementById("btnDashboardQuizAction");

// Quiz Modal Elements
const quizModal = document.getElementById("quizModal");
const btnCloseQuizModal = document.getElementById("btnCloseQuizModal");
const quizStepIndicator = document.getElementById("quizStepIndicator");
const quizLoadingState = document.getElementById("quizLoadingState");
const quizActiveContainer = document.getElementById("quizActiveContainer");
const quizTargetWord = document.getElementById("quizTargetWord");
const quizTargetIpa = document.getElementById("quizTargetIpa");
const quizQuestionText = document.getElementById("quizQuestionText");
const quizOptionsGrid = document.getElementById("quizOptionsGrid");
const quizExplanationBox = document.getElementById("quizExplanationBox");
const quizResultIcon = document.getElementById("quizResultIcon");
const quizResultTitle = document.getElementById("quizResultTitle");
const quizExplanationText = document.getElementById("quizExplanationText");
const btnQuizMarkMastered = document.getElementById("btnQuizMarkMastered");
const btnQuizNext = document.getElementById("btnQuizNext");
const quizCompletedView = document.getElementById("quizCompletedView");
const quizScoreText = document.getElementById("quizScoreText");
const btnQuizPlayAgain = document.getElementById("btnQuizPlayAgain");
const btnQuizDone = document.getElementById("btnQuizDone");

// Flashcard Modal Elements
const btnDashboardFlashcardAction = document.getElementById("btnDashboardFlashcardAction");
const flashcardModal = document.getElementById("flashcardModal");
const btnCloseFlashcardModal = document.getElementById("btnCloseFlashcardModal");
const flashcardCounter = document.getElementById("flashcardCounter");
const flashcardProgressBar = document.getElementById("flashcardProgressBar");
const flashcardActiveView = document.getElementById("flashcardActiveView");
const flashcardScene = document.getElementById("flashcardScene");
const flashcardCardInner = document.getElementById("flashcardCardInner");
const flashcardPos = document.getElementById("flashcardPos");
const btnFlashcardAudio = document.getElementById("btnFlashcardAudio");
const btnFlashcardAudioBack = document.getElementById("btnFlashcardAudioBack");
const flashcardWord = document.getElementById("flashcardWord");
const flashcardIpa = document.getElementById("flashcardIpa");
const flashcardMeaning = document.getElementById("flashcardMeaning");
const flashcardExampleBox = document.getElementById("flashcardExampleBox");
const flashcardExampleEn = document.getElementById("flashcardExampleEn");
const flashcardExampleVi = document.getElementById("flashcardExampleVi");
const btnFlashcardSkip = document.getElementById("btnFlashcardSkip");
const btnFlashcardMaster = document.getElementById("btnFlashcardMaster");
const flashcardCompletedView = document.getElementById("flashcardCompletedView");
const flashcardSummaryText = document.getElementById("flashcardSummaryText");
const btnFlashcardRestart = document.getElementById("btnFlashcardRestart");
const btnFlashcardDone = document.getElementById("btnFlashcardDone");

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
  updateSyncBanners();
}

function setLoggedOutUser() {
  currentUser = null;
  localStorage.removeItem(AUTH_TOKEN_KEY);
  if (userGuestBox) userGuestBox.classList.remove("hidden");
  if (userLoggedInBox) userLoggedInBox.classList.add("hidden");
  if (headerUsername) headerUsername.textContent = "";
  if (headerMasteredBadge) headerMasteredBadge.textContent = "";
  updateSyncBanners();
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
  const count = selectedWordSet ? selectedWordSet.size : 0;
  const total = totalVocabCount || 2850;
  const rawPct = total > 0 ? (count / total) * 100 : 0;
  const pctStr = rawPct.toFixed(1);
  const displayPct = pctStr.indexOf(".0") !== -1 ? parseInt(pctStr, 10) : pctStr;

  if (dashboardProgressText) {
    dashboardProgressText.textContent = `${count} / ${total.toLocaleString("vi-VN")} từ (${displayPct}%)`;
  }
  if (dashboardProgressBar) {
    const barPct = Math.min(100, Math.max(0, Math.round(rawPct)));
    dashboardProgressBar.style.width = `${barPct}%`;
  }

  const settingsMasteredCount = document.getElementById("settingsMasteredCount");
  if (settingsMasteredCount) {
    settingsMasteredCount.textContent = `${count} từ`;
  }

  if (liveSyncStatusText) {
    if (count > 0) {
      liveSyncStatusText.textContent = `${count} từ đã tích chọn (thành thạo) sẽ được loại trừ hoàn toàn, AuraSpeak AI chỉ luyện các từ còn lại.`;
    } else {
      liveSyncStatusText.textContent = `Hiện chưa có từ nào được tích chọn. Tích chọn từ ở tab Luyện Dịch để đánh dấu từ đã thành thạo.`;
    }
  }
  if (liveActiveSyncText) {
    if (count > 0) {
      liveActiveSyncText.textContent = `Đang loại trừ ${count} từ đã thành thạo từ tab Luyện Dịch (AuraSpeak AI sẽ không hỏi lại)`;
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

  const headerMobileMasteredCount = document.getElementById("headerMobileMasteredCount");
  if (headerMobileMasteredCount) {
    headerMobileMasteredCount.textContent = count;
  }

  const liveActiveSyncSubText = document.getElementById("liveActiveSyncSubText");
  if (liveActiveSyncSubText) {
    if (count > 0) {
      liveActiveSyncSubText.textContent = `Đang loại trừ ${count} từ đã thành thạo từ tab Luyện Dịch`;
    } else {
      liveActiveSyncSubText.textContent = `Chưa có từ nào được loại trừ`;
    }
  }

  if (headerMasteredBadge && currentUser) {
    headerMasteredBadge.textContent = `${count} từ đã học`;
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
let totalVocabCount = 2850;
window.allWordsCache = [];
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
    let introPrompt = `System: Chào học viên ngắn gọn bằng tiếng Việt với vai trò Gia sư Tiếng Anh 1:1 cá nhân hóa. Giới thiệu bạn đồng hành theo Lộ trình chuẩn Oxford 3000 và Sổ tay phát âm. `;
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
      notyf.error("Không thể kết nối đến máy chủ đàm thoại AuraSpeak AI.");
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
    if (liveFeedbackText && msg.text) {
      const lower = msg.text.toLowerCase();
      if (lower.indexOf("âm") !== -1 || lower.indexOf("phát âm") !== -1 || lower.indexOf("sound") !== -1 || lower.indexOf("/s/") !== -1 || lower.indexOf("/z/") !== -1 || lower.indexOf("/t/") !== -1 || lower.indexOf("/d/") !== -1) {
        liveFeedbackText.textContent = msg.text;
      }
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
if (connectBtn) {
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
}

// Controls
if (disconnectBtn) {
  disconnectBtn.onclick = () => {
    if (geminiClient) geminiClient.disconnect();
  };
}

if (micBtn) {
  micBtn.onclick = async () => {
    if (!mediaHandler) return;
    if (mediaHandler.isRecording) {
      mediaHandler.stopAudio();
      micBtn.innerHTML = `<i data-lucide="mic" class="lucide-icon"></i> Start Mic`;
      refreshIcons();
    } else {
      try {
        await mediaHandler.startAudio((data) => {
          if (geminiClient && geminiClient.isConnected()) {
            geminiClient.send(data);
          }
        });
        micBtn.innerHTML = `<i data-lucide="mic-off" class="lucide-icon"></i> Stop Mic`;
        refreshIcons();
      } catch (e) {
        if (typeof notyf !== "undefined") notyf.error("Không thể ghi âm microphone: " + e.message);
      }
    }
  };
}

if (cameraBtn) {
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

}

if (screenBtn) {
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

}

if (sendBtn) sendBtn.onclick = sendText;
if (textInput) {
  textInput.onkeypress = (e) => {
    if (e.key === "Enter") sendText();
  };
}

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

if (restartBtn) {
  restartBtn.onclick = () => {
    resetUI();
  };
}

// ─── TAB SWITCHING LOGIC (4 TABS: HOME, LIVE, TRANSLATION, STUDIO) ────────────────
function switchMainTab(target) {
  // target: 'home' | 'live' | 'translation' | 'studio'
  if (navTabHome) navTabHome.classList.toggle("active", target === "home");
  if (navTabLive) navTabLive.classList.toggle("active", target === "live");
  if (navTabTranslation) navTabTranslation.classList.toggle("active", target === "translation");
  if (navTabStudio) navTabStudio.classList.toggle("active", target === "studio");

  if (tabContentHome) tabContentHome.classList.toggle("hidden", target !== "home");
  if (tabContentLive) tabContentLive.classList.toggle("hidden", target !== "live");
  if (tabContentTranslation) tabContentTranslation.classList.toggle("hidden", target !== "translation");
  if (tabContentStudio) tabContentStudio.classList.toggle("hidden", target !== "studio");

  if (target === "home") {
    updateSyncBanners();
  } else if (target === "live") {
    syncMasteredWordsToLive();
    updateFocusWordHUD();
  } else if (target === "translation" && syncedTopics.length === 0) {
    syncVocabFromExcel();
  }
  refreshIcons();
}

if (navTabHome) navTabHome.onclick = () => switchMainTab("home");
if (navTabLive) navTabLive.onclick = () => switchMainTab("live");
if (navTabTranslation) navTabTranslation.onclick = () => switchMainTab("translation");
if (navTabStudio) navTabStudio.onclick = () => switchMainTab("studio");

// Quick Actions on Home
if (btnHomeActionLive) {
  btnHomeActionLive.onclick = () => switchMainTab("live");
}
if (btnDashboardReadingAction) {
  btnDashboardReadingAction.onclick = () => switchMainTab("translation");
}

// Backup & Export Excel
if (btnExportBackup) {
  btnExportBackup.onclick = () => {
    window.open("/api/vocab/export", "_blank");
  };
}

// Sync check between Desktop and Mobile Drawer for "Chỉ từ Đã học"
function handleLearnedOnlyToggle(isChecked) {
  if (chkLearnedOnly) chkLearnedOnly.checked = isChecked;
  if (chkLearnedOnlyDrawer) chkLearnedOnlyDrawer.checked = isChecked;
  syncVocabFromExcel();
}

if (chkLearnedOnly) {
  chkLearnedOnly.onchange = () => handleLearnedOnlyToggle(chkLearnedOnly.checked);
}
if (chkLearnedOnlyDrawer) {
  chkLearnedOnlyDrawer.onchange = () => handleLearnedOnlyToggle(chkLearnedOnlyDrawer.checked);
}

// Focus Word HUD Controller (Tab 2: Đàm Thoại)
function updateFocusWordHUD(wordObj) {
  if (!wordObj) {
    if (window.allWordsCache && window.allWordsCache.length > 0) {
      const candidates = window.allWordsCache.filter(function(w) {
        return !selectedWordSet.has(w.word);
      });
      if (candidates.length > 0) {
        wordObj = candidates[Math.floor(Math.random() * candidates.length)];
      } else {
        wordObj = window.allWordsCache[0];
      }
    }
  }
  if (!wordObj) {
    wordObj = {
      word: "comfortable",
      ipa: "/ˈkʌmftəbl/",
      pos: "adj",
      meaning: "thoải mái, tiện nghi, dễ chịu",
      level: "A2"
    };
  }
  if (focusWordTerm) focusWordTerm.textContent = wordObj.word || "";
  if (focusWordIpa) focusWordIpa.textContent = wordObj.ipa || "";
  if (focusWordPos) focusWordPos.textContent = wordObj.pos ? `[${wordObj.pos}]` : "";
  if (focusWordMeaning) focusWordMeaning.textContent = wordObj.meaning || "";
  if (focusWordLevel) focusWordLevel.textContent = wordObj.level || "A2";
}

// ─── TRANSLATION WORKSPACE: SQLITE SYNC & VOCABULARY SELECTION ───────────────
if (btnSyncVocab) {
  btnSyncVocab.onclick = () => {
    syncVocabFromExcel();
  };
}

async function syncVocabFromExcel() {
  btnSyncVocab.disabled = true;
  btnSyncVocab.innerHTML = `<span class="btn-icon"><i data-lucide="loader-2" class="lucide-icon spin"></i></span> Đang đồng bộ...`;
  refreshIcons();

  try {
    const learnedOnly = chkLearnedOnly ? chkLearnedOnly.checked : false;
    const response = await fetch(`/api/vocab/sync?learned_only=${learnedOnly}`, {
      headers: getAuthHeaders(),
    });
    const data = await response.json();

    if (data.status === "success") {
      totalVocabCount = data.total_words || 2850;
      if (statTotalWords) statTotalWords.textContent = totalVocabCount.toLocaleString("vi-VN");
      if (statLearnedWords) statLearnedWords.textContent = (data.learned_count !== undefined && data.learned_count !== null ? data.learned_count : 0);
      syncedTopics = data.topics || [];

      // Rebuild window.allWordsCache for fast searching and flashcards
      window.allWordsCache = [];
      for (let t = 0; t < syncedTopics.length; t++) {
        const top = syncedTopics[t];
        if (top && Array.isArray(top.words)) {
          for (let w = 0; w < top.words.length; w++) {
            const wordObj = top.words[w];
            window.allWordsCache.push({
              word: wordObj.word,
              ipa: wordObj.ipa || "",
              pos: wordObj.pos || "",
              meaning: wordObj.meaning || "",
              topic: top.name,
              learned: !!wordObj.learned
            });
          }
        }
      }

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
        // Tự động tích chọn tất cả các từ đã học (TRUE) từ database để đồng bộ số lượng chính xác
        for (let i = 0; i < syncedTopics.length; i++) {
          const topic = syncedTopics[i];
          for (let j = 0; j < topic.words.length; j++) {
            const w = topic.words[j];
            if (w.learned) {
              selectedWordSet.add(w.word);
            }
          }
        }
        // Nếu không có từ nào đánh dấu learned, tự động chọn tất cả từ của các chủ đề hiện tại
        if (selectedWordSet.size === 0) {
          for (let i = 0; i < syncedTopics.length; i++) {
            const topic = syncedTopics[i];
            for (let j = 0; j < topic.words.length; j++) {
              selectedWordSet.add(topic.words[j].word);
            }
          }
        }
        saveMasteredWordsToStorage();
      }

      renderTopics();
      updateSelectedCount();
      updateSyncBanners();
      notyf.success(`Đã đồng bộ ${totalVocabCount} từ chuẩn Oxford 3000 (${data.learned_count} từ đã học)!`);
    } else {
      notyf.error("Lỗi đồng bộ dữ liệu: " + (data.message || "Unknown error"));
    }
  } catch (err) {
    console.error("Sync error:", err);
    notyf.error("Không thể kết nối đến máy chủ để đọc dữ liệu từ vựng.");
  } finally {
    btnSyncVocab.disabled = false;
    btnSyncVocab.innerHTML = `<span class="btn-icon"><i data-lucide="refresh-cw" class="lucide-icon"></i></span> Đồng bộ CSDL`;
    refreshIcons();
  }
}

// Lazy Rendering: render child word rows only when a topic accordion is open
function renderTopicChildren(topic, topicBody, chkTopic, countBadge) {
  topicBody.innerHTML = "";
  const words = topic.words || [];

  const updateTopicState = () => {
    let selectedCount = 0;
    for (let i = 0; i < words.length; i++) {
      if (selectedWordSet.has(words[i].word)) selectedCount++;
    }
    const total = words.length;
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

  words.forEach((w) => {
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
      updateSyncBanners();
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
    ipa.textContent = w.ipa || "";

    const pos = document.createElement("span");
    pos.className = "word-pos";
    pos.textContent = w.pos ? `[${w.pos}]` : "";

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
}

// Debounced search results renderer: capped at max 60 words for 60fps performance
function renderSearchResults(searchTerm) {
  topicsContainer.innerHTML = "";
  const q = searchTerm.toLowerCase().trim();
  const matchedWords = [];
  const cache = (window.allWordsCache && window.allWordsCache.length > 0) ? window.allWordsCache : [];

  if (cache.length > 0) {
    for (let i = 0; i < cache.length; i++) {
      const item = cache[i];
      if (
        (item.word && item.word.toLowerCase().indexOf(q) !== -1) ||
        (item.meaning && item.meaning.toLowerCase().indexOf(q) !== -1) ||
        (item.ipa && item.ipa.toLowerCase().indexOf(q) !== -1)
      ) {
        matchedWords.push(item);
        if (matchedWords.length >= 60) break;
      }
    }
  } else {
    // Fallback if window.allWordsCache not populated yet
    for (let t = 0; t < syncedTopics.length; t++) {
      const top = syncedTopics[t];
      for (let w = 0; w < top.words.length; w++) {
        const item = top.words[w];
        if (
          (item.word && item.word.toLowerCase().indexOf(q) !== -1) ||
          (item.meaning && item.meaning.toLowerCase().indexOf(q) !== -1) ||
          (item.ipa && item.ipa.toLowerCase().indexOf(q) !== -1)
        ) {
          matchedWords.push({
            word: item.word,
            ipa: item.ipa || "",
            pos: item.pos || "",
            meaning: item.meaning || "",
            topic: top.name
          });
          if (matchedWords.length >= 60) break;
        }
      }
      if (matchedWords.length >= 60) break;
    }
  }

  if (matchedWords.length === 0) {
    const safeTerm = searchTerm.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    topicsContainer.innerHTML = `<div class="empty-state"><p>Không tìm thấy từ vựng nào khớp với "<strong>${safeTerm}</strong>".</p></div>`;
    return;
  }

  const resultContainer = document.createElement("div");
  resultContainer.className = "search-results-panel";

  const header = document.createElement("div");
  header.className = "search-results-header";
  header.innerHTML = `<span>Tìm thấy <strong>${matchedWords.length}</strong> từ ${matchedWords.length >= 60 ? "(hiển thị 60 kết quả nhanh nhất)" : ""}</span>`;
  resultContainer.appendChild(header);

  const list = document.createElement("div");
  list.className = "search-results-list";

  matchedWords.forEach((w) => {
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
      updateSelectedCount();
      updateSyncBanners();
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
    ipa.textContent = w.ipa || "";

    const pos = document.createElement("span");
    pos.className = "word-pos";
    pos.textContent = w.pos ? `[${w.pos}]` : "";

    topLine.appendChild(term);
    if (w.ipa) topLine.appendChild(ipa);
    if (w.pos) topLine.appendChild(pos);

    if (w.topic) {
      const topicTag = document.createElement("span");
      topicTag.className = "word-topic-tag";
      topicTag.textContent = w.topic;
      topLine.appendChild(topicTag);
    }

    const meaning = document.createElement("div");
    meaning.className = "word-meaning";
    meaning.textContent = w.meaning;

    meta.appendChild(topLine);
    meta.appendChild(meaning);

    row.appendChild(wChk);
    row.appendChild(meta);
    list.appendChild(row);
  });

  resultContainer.appendChild(list);
  topicsContainer.appendChild(resultContainer);
  refreshIcons();
}

function renderTopics() {
  const searchTerm = (vocabSearchInput ? vocabSearchInput.value : "").toLowerCase().trim();
  topicsContainer.innerHTML = "";

  if (btnClearVocabSearch) {
    if (searchTerm) {
      btnClearVocabSearch.classList.remove("hidden");
    } else {
      btnClearVocabSearch.classList.add("hidden");
    }
  }

  if (searchTerm) {
    renderSearchResults(searchTerm);
    return;
  }

  if (!syncedTopics || syncedTopics.length === 0) {
    topicsContainer.innerHTML = `<div class="empty-state"><p>Không tìm thấy từ vựng nào phù hợp.</p></div>`;
    return;
  }

  const fragment = document.createDocumentFragment();

  syncedTopics.forEach((topic, tIdx) => {
    const isOpen = openTopicSet.has(tIdx);
    const topicGroup = document.createElement("div");
    topicGroup.className = `topic-group ${isOpen ? "open" : ""}`;

    // Header (Parent Row)
    const topicHeader = document.createElement("div");
    topicHeader.className = "topic-header";
    topicHeader.title = "Nhấp để mở rộng / thu gọn danh sách từ";

    const titleArea = document.createElement("div");
    titleArea.className = "topic-title-area";

    const arrow = document.createElement("span");
    arrow.className = "topic-arrow";
    arrow.innerHTML = `<i data-lucide="chevron-right" class="topic-chevron"></i>`;

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

    // Synchronize parent checkbox and badge state
    const words = topic.words || [];
    let selectedCount = 0;
    for (let i = 0; i < words.length; i++) {
      if (selectedWordSet.has(words[i].word)) selectedCount++;
    }
    const total = words.length;

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

    // Lazy load: ONLY render child DOM elements when this topic is open!
    if (isOpen) {
      renderTopicChildren(topic, topicBody, chkTopic, countBadge);
    }

    // Accordion Toggle: click anywhere on header (except the checkbox)
    topicHeader.onclick = (e) => {
      if (e.target === chkTopic) return;
      const willBeOpen = !topicGroup.classList.contains("open");
      topicGroup.classList.toggle("open", willBeOpen);
      if (willBeOpen) {
        openTopicSet.add(tIdx);
        if (topicBody.children.length === 0) {
          renderTopicChildren(topic, topicBody, chkTopic, countBadge);
        }
      } else {
        openTopicSet.delete(tIdx);
      }
    };

    // Parent Checkbox Handler (Cha -> All Con)
    chkTopic.onclick = (e) => {
      e.stopPropagation();
      const willSelect = chkTopic.checked;
      words.forEach((w) => {
        if (willSelect) selectedWordSet.add(w.word);
        else selectedWordSet.delete(w.word);
      });

      // Update rendered child rows if present in DOM
      if (topicBody.children.length > 0) {
        topicBody.querySelectorAll(".word-row").forEach((rowEl, rIdx) => {
          const w = words[rIdx];
          if (!w) return;
          const isSel = selectedWordSet.has(w.word);
          rowEl.classList.toggle("selected", isSel);
          const cEl = rowEl.querySelector(".word-checkbox");
          if (cEl) cEl.checked = isSel;
        });
      }

      if (willSelect && words.length > 0) {
        countBadge.className = "topic-count-badge all-selected";
        countBadge.textContent = `Đã chọn hết (${words.length})`;
      } else {
        countBadge.className = "topic-count-badge";
        countBadge.textContent = `${words.length} từ`;
      }
      chkTopic.indeterminate = false;

      updateSelectedCount();
      updateSyncBanners();
    };

    topicGroup.appendChild(topicHeader);
    topicGroup.appendChild(topicBody);
    fragment.appendChild(topicGroup);
  });

  topicsContainer.appendChild(fragment);
  refreshIcons();
}

function updateSelectedCount() {
  const count = selectedWordSet ? selectedWordSet.size : 0;
  if (statSelectedCount) statSelectedCount.textContent = count;
  if (mobileSelectedCountHighlight) {
    mobileSelectedCountHighlight.textContent = `Đang chọn: ${count} từ`;
  }
  if (sheetCountTag) {
    sheetCountTag.textContent = `${count} từ đã chọn`;
  }
  if (btnGeneratePassage) btnGeneratePassage.disabled = count === 0;
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
if (linkSelectAll) {
  linkSelectAll.onclick = () => {
    syncedTopics.forEach((t) => {
      t.words.forEach((w) => selectedWordSet.add(w.word));
    });
    renderTopics();
    updateSelectedCount();
  };
}

if (linkDeselectAll) {
  linkDeselectAll.onclick = () => {
    selectedWordSet.clear();
    renderTopics();
    updateSelectedCount();
  };
}

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

// Debounced search on input (250ms delay for 60fps)
let vocabSearchDebounceTimer = null;
if (vocabSearchInput) {
  vocabSearchInput.oninput = () => {
    const val = (vocabSearchInput.value || "").trim();
    if (btnClearVocabSearch) {
      if (val.length > 0) {
        btnClearVocabSearch.classList.remove("hidden");
      } else {
        btnClearVocabSearch.classList.add("hidden");
      }
    }
    clearTimeout(vocabSearchDebounceTimer);
    vocabSearchDebounceTimer = setTimeout(() => {
      renderTopics();
    }, 250);
  };
}

if (btnClearVocabSearch) {
  btnClearVocabSearch.onclick = () => {
    if (vocabSearchInput) {
      vocabSearchInput.value = "";
      vocabSearchInput.focus();
    }
    btnClearVocabSearch.classList.add("hidden");
    renderTopics();
  };
}

// ─── ADD CUSTOM WORD HANDLER ───────────────────────────────────────────────
async function handleAddNewCustomWord() {
  if (!inputCustomWord) return;
  const word = (inputCustomWord.value || "").trim().toLowerCase();
  if (!word) {
    notyf.error("Vui lòng nhập từ tiếng Anh cần thêm.");
    inputCustomWord.focus();
    return;
  }

  if (!/^[a-zA-Z\s'-]+$/.test(word)) {
    notyf.error("Từ vựng chỉ nên chứa các chữ cái tiếng Anh.");
    return;
  }

  if (btnAddCustomWord) {
    btnAddCustomWord.disabled = true;
    btnAddCustomWord.innerHTML = `<i data-lucide="loader-2" class="lucide-icon spin"></i> <span>Đang thêm...</span>`;
    refreshIcons();
  }

  try {
    const res = await fetch("/api/vocab/custom-word", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ word: word })
    });
    const data = await res.json();

    if (data.status === "success") {
      const newWord = data.word;
      const meaning = data.meaning_vi || "";
      const ipa = data.ipa || "";
      const pos = data.pos || "word";
      const topicName = data.topic || "Từ tùy chỉnh";

      // 1. Add to selectedWordSet
      selectedWordSet.add(newWord);

      // 2. Add to window.allWordsCache if not already there
      let existingInCache = false;
      if (!window.allWordsCache) window.allWordsCache = [];
      for (let i = 0; i < window.allWordsCache.length; i++) {
        if (window.allWordsCache[i].word.toLowerCase() === newWord.toLowerCase()) {
          existingInCache = true;
          window.allWordsCache[i].meaning = meaning;
          window.allWordsCache[i].ipa = ipa;
          window.allWordsCache[i].pos = pos;
          break;
        }
      }
      if (!existingInCache) {
        window.allWordsCache.unshift({
          word: newWord,
          ipa: ipa,
          pos: pos,
          meaning: meaning,
          topic: topicName,
          learned: true
        });
        totalVocabCount++;
        if (statTotalWords) statTotalWords.textContent = totalVocabCount.toLocaleString("vi-VN");
      }

      // 3. Add to syncedTopics
      let foundTopic = null;
      for (let t = 0; t < syncedTopics.length; t++) {
        if (syncedTopics[t].name === topicName) {
          foundTopic = syncedTopics[t];
          break;
        }
      }
      if (!foundTopic) {
        foundTopic = { name: topicName, words: [] };
        syncedTopics.unshift(foundTopic);
        openTopicSet.add(0);
      }
      let foundWordInTopic = false;
      for (let w = 0; w < foundTopic.words.length; w++) {
        if (foundTopic.words[w].word.toLowerCase() === newWord.toLowerCase()) {
          foundWordInTopic = true;
          break;
        }
      }
      if (!foundWordInTopic) {
        foundTopic.words.unshift({
          word: newWord,
          ipa: ipa,
          pos: pos,
          meaning: meaning,
          learned: true
        });
      }

      inputCustomWord.value = "";
      saveMasteredWordsToStorage();
      updateSelectedCount();
      updateSyncBanners();
      renderTopics();

      const notifMsg = data.is_new 
        ? `Đã thêm từ "${newWord}" (${meaning}) vào lộ trình học!`
        : `Từ "${newWord}" đã có trong từ điển và được đánh dấu thành thạo!`;
      notyf.success(notifMsg);
    } else {
      notyf.error("Lỗi khi thêm từ: " + (data.detail || data.message || "Không xác định"));
    }
  } catch (err) {
    console.error("Add custom word error:", err);
    notyf.error("Không thể kết nối đến máy chủ để thêm từ mới.");
  } finally {
    if (btnAddCustomWord) {
      btnAddCustomWord.disabled = false;
      btnAddCustomWord.innerHTML = `<i data-lucide="plus"></i> <span>Thêm</span>`;
      refreshIcons();
    }
  }
}

if (btnAddCustomWord) {
  btnAddCustomWord.onclick = handleAddNewCustomWord;
}
if (inputCustomWord) {
  inputCustomWord.onkeydown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddNewCustomWord();
    }
  };
}

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
    loadingSub.textContent = `Đang lồng ghép từ vựng đã chọn vào bài đọc ${selectedSentenceCount} câu (Mức độ: ${lvlNames[selectedDifficulty] || "Cơ bản"}).`;
  }
  if (passageComparisonCard) passageComparisonCard.classList.add("hidden");
  saveStatusMsg.textContent = "";

  const selectedList = Array.from(selectedWordSet);
  const startTime = performance.now();

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

    const elapsedSec = ((performance.now() - startTime) / 1000).toFixed(1);
    const data = await res.json();
    if (data.status === "success" && data.data) {
      currentPassageData = data.data;
      displayGeneratedPassage(currentPassageData, elapsedSec);
      notyf.success("Bài đọc AI đã sẵn sàng để luyện dịch!");
      refreshIcons();
    } else {
      notyf.error("Lỗi khi tạo bài đọc: " + (data.message || "Unknown error"));
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

function displayGeneratedPassage(data, elapsedSec) {
  if (!data) return;
  // Target pills
  if (passageUsedWords) passageUsedWords.innerHTML = "";
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

  // Latency Speed Badge
  const speedBadge = document.getElementById("passageSpeedBadge");
  if (speedBadge) {
    if (elapsedSec) {
      const modelLabel = data.cached ? "Tức thì" : "AI Engine";
      speedBadge.innerHTML = `<i data-lucide="zap" class="lucide-icon"></i> ⚡ ${elapsedSec}s • ${modelLabel}`;
      speedBadge.classList.remove("hidden");
    } else {
      speedBadge.classList.add("hidden");
    }
  }

  refreshIcons();

  // English text
  if (passageEnglishText) passageEnglishText.textContent = data.english_passage || "";

  // Reset practice input & hide comparison card
  if (txtUserTranslation) txtUserTranslation.value = "";
  if (saveStatusMsg) saveStatusMsg.textContent = "";
  if (passageComparisonCard) passageComparisonCard.classList.add("hidden");
  if (passageCard) passageCard.classList.remove("hidden");
}

// Speak English Passage aloud using browser SpeechSynthesis
if (btnSpeakPassage) {
  btnSpeakPassage.onclick = () => {
    const text = passageEnglishText ? passageEnglishText.textContent.trim() : "";
    if (!text || !window.speechSynthesis) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.95; // Slightly slower for clear learning
    window.speechSynthesis.speak(utterance);
  };
}

// ─── SUBMIT TRANSLATION & COMPARE (NỘP BÀI & ĐỐI CHIẾU ĐÁP ÁN) ───────────────
if (btnSubmitTranslation) {
  btnSubmitTranslation.onclick = async () => {
    if (!currentPassageData) return;
    const myTranslation = txtUserTranslation ? txtUserTranslation.value.trim() : "";
    if (!myTranslation) {
      notyf.error("Vui lòng nhập bản dịch của bạn vào ô thực hành trước khi nộp bài!");
      if (txtUserTranslation) txtUserTranslation.focus();
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

      // 1.1 Hiển thị chấm điểm và đánh giá AI nếu có
      const evalBox = document.getElementById("compareEvaluationBox");
      const evalScore = document.getElementById("evalScoreText");
      const evalFeedback = document.getElementById("evalFeedbackText");
      const evalSuggRow = document.getElementById("evalSuggestionRow");
      const evalSuggText = document.getElementById("evalSuggestionText");

      if (data.evaluation && evalBox) {
        if (evalScore) evalScore.textContent = data.evaluation.score || "8.5";
        if (evalFeedback) evalFeedback.textContent = data.evaluation.feedback || "Bản dịch đã diễn đạt tốt ý nghĩa.";
        if (data.evaluation.suggested_improvement && evalSuggText && evalSuggRow) {
          evalSuggText.textContent = data.evaluation.suggested_improvement;
          evalSuggRow.classList.remove("hidden");
        } else if (evalSuggRow) {
          evalSuggRow.classList.add("hidden");
        }
        evalBox.classList.remove("hidden");
      }

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
}

// Event Listeners for Passage Generation
if (btnGeneratePassage) btnGeneratePassage.onclick = () => requestGeneratePassage(false);
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
if (btnOpenRegisterModal) btnOpenRegisterModal.onclick = () => openAuthModal(true);
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
        const username = (data.user && data.user.username) ? data.user.username : "học viên";
        const successMsg = isRegisterMode 
          ? "Đăng ký tài khoản thành công!" 
          : "Đăng nhập thành công! Chào mừng " + username;
        notyf.success(successMsg);
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

// ─── MOBILE VOCAB FULL-SCREEN OVERLAY HANDLERS (100% CLEAN, ZERO BACKDROP) ───
function openMobileVocabDrawer() {
  var drawer = document.getElementById("vocabDrawer") || document.getElementById("vocabSidebar");
  if (drawer) {
    drawer.classList.remove("hidden");
    // Force layout reflow before adding active for smooth slide animation
    void drawer.offsetWidth;
    drawer.classList.add("active");
    drawer.classList.add("mobile-open");
    drawer.classList.add("show-drawer");
    document.body.style.overflow = "hidden"; // Prevent scrolling of background page
  }
}

function closeMobileVocabDrawer() {
  var drawer = document.getElementById("vocabDrawer") || document.getElementById("vocabSidebar");
  if (drawer) {
    drawer.classList.remove("active");
    drawer.classList.remove("mobile-open");
    drawer.classList.remove("show-drawer");
    setTimeout(function() {
      if (drawer && !drawer.classList.contains("active")) {
        drawer.classList.add("hidden");
        document.body.style.overflow = ""; // Restore background page scrolling
      }
    }, 300);
  } else {
    document.body.style.overflow = "";
  }
  updateSelectedCount();
  updateSyncBanners();
}

// Aliases for compatibility
var openMobileVocabSheet = openMobileVocabDrawer;
var closeMobileVocabSheet = closeMobileVocabDrawer;

if (btnToggleMobileVocabDrawer) {
  btnToggleMobileVocabDrawer.onclick = openMobileVocabDrawer;
}

if (btnCloseMobileVocabDrawer) {
  btnCloseMobileVocabDrawer.onclick = closeMobileVocabDrawer;
}

if (btnDoneMobileVocab) {
  btnDoneMobileVocab.onclick = function() {
    closeMobileVocabDrawer();
    if (selectedWordSet.size > 0) {
      requestGeneratePassage(false);
    }
  };
}

if (vocabDrawerBackdrop) {
  vocabDrawerBackdrop.onclick = closeMobileVocabDrawer;
}

var btnPlaceholderOpenDrawer = document.getElementById("btnPlaceholderOpenDrawer");
if (btnPlaceholderOpenDrawer) {
  btnPlaceholderOpenDrawer.onclick = function() {
    if (window.innerWidth < 768) {
      openMobileVocabDrawer();
    } else {
      var search = document.getElementById("vocabSearchInput");
      if (search) search.focus();
    }
  };
}

var btnPlaceholderStartGenerate = document.getElementById("btnPlaceholderStartGenerate");
if (btnPlaceholderStartGenerate) {
  btnPlaceholderStartGenerate.onclick = function() {
    if (selectedWordSet.size === 0) {
      autoSelectDefaultWords();
    }
    requestGeneratePassage(false);
  };
}

// Auto close overlay when resized or rotated to Tablet / Desktop (>= 768px)
window.addEventListener("resize", function() {
  if (window.innerWidth >= 768) {
    closeMobileVocabDrawer();
    var drawer = document.getElementById("vocabDrawer") || document.getElementById("vocabSidebar");
    if (drawer) {
      drawer.classList.remove("hidden");
    }
  }
});

// ─── INITIAL APP STARTUP & RESILIENT DOM INIT ───────────────────────────────
function initApplication() {
  // 1. Render all static icons immediately
  try {
    if (typeof window !== "undefined" && window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  } catch (err) {
    console.warn("[Init] Early Lucide render error:", err);
  }

  // 2. Initialize Theme
  try {
    initTheme();
  } catch (err) {
    console.warn("[Init] Theme error:", err);
  }

  try {
    const tabHome = document.getElementById("navTabHome");
    const tabLive = document.getElementById("navTabLive");
    const tabTrans = document.getElementById("navTabTranslation");
    const tabStudio = document.getElementById("navTabStudio");
    if (tabHome) tabHome.onclick = (e) => { e.preventDefault(); switchMainTab("home"); };
    if (tabLive) tabLive.onclick = (e) => { e.preventDefault(); switchMainTab("live"); };
    if (tabTrans) tabTrans.onclick = (e) => { e.preventDefault(); switchMainTab("translation"); };
    if (tabStudio) tabStudio.onclick = (e) => { e.preventDefault(); switchMainTab("studio"); };
  } catch (err) {
    console.warn("[Init] Tab binding error:", err);
  }

  try {
    initVoiceVisualizer();
  } catch (err) {
    console.warn("[Init] SiriWave error:", err);
  }

  try {
    refreshIcons();
  } catch (err) {
    console.warn("[Init] Lucide error:", err);
  }

  try {
    checkAuthStatus().finally(() => {
      updateSyncBanners();
      syncVocabFromExcel();
      refreshIcons();
    });
  } catch (err) {
    console.warn("[Init] Auth sync error:", err);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApplication);
} else {
  initApplication();
}


// ─── THEME SWITCHER (DARK / LIGHT MODE) ────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem("app_theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  setTheme(saved);
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("app_theme", theme);
  const isDark = theme === "dark";
  const btnThemeToggle = document.getElementById("btnThemeToggle");
  if (btnThemeToggle) {
    btnThemeToggle.innerHTML = `<i data-lucide="${isDark ? 'sun' : 'moon'}" class="lucide-icon"></i>`;
    btnThemeToggle.title = isDark ? "Chuyển sang giao diện Sáng" : "Chuyển sang giao diện Tối";
  }
  const btnModalThemeToggle = document.getElementById("btnModalThemeToggle");
  if (btnModalThemeToggle) {
    btnModalThemeToggle.innerHTML = `<i data-lucide="${isDark ? 'sun' : 'moon'}" class="lucide-icon"></i> ${isDark ? 'Chế độ Sáng' : 'Chế độ Tối'}`;
  }
  const currentThemeText = document.getElementById("settingsCurrentThemeText");
  if (currentThemeText) {
    currentThemeText.textContent = isDark ? "Tối (Dark Mode)" : "Sáng (Light Mode)";
  }
  refreshIcons();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  setTheme(current === "dark" ? "light" : "dark");
}

const btnThemeToggle = document.getElementById("btnThemeToggle");
if (btnThemeToggle) btnThemeToggle.onclick = toggleTheme;

const btnModalThemeToggle = document.getElementById("btnModalThemeToggle");
if (btnModalThemeToggle) btnModalThemeToggle.onclick = toggleTheme;

// ─── SETTINGS DROPDOWN POPOVER CONTROLLER ──────────────────────────────────
const btnSettings = document.getElementById("btnSettings");
const settingsDropdown = document.getElementById("settingsDropdown") || document.getElementById("settingsModal");
const btnCloseSettingsModal = document.getElementById("btnCloseSettingsModal");

function openSettingsDropdown() {
  if (!settingsDropdown) return;
  const usernameDisplay = document.getElementById("settingsUsernameDisplay");
  const userIdDisplay = document.getElementById("settingsUserIdDisplay");
  const avatarChar = document.getElementById("settingsAvatarChar");
  const masteredCount = document.getElementById("settingsMasteredCount");

  if (currentUser) {
    if (usernameDisplay) usernameDisplay.textContent = currentUser.username;
    if (userIdDisplay) userIdDisplay.textContent = `#${currentUser.id}`;
    if (avatarChar) avatarChar.textContent = currentUser.username.charAt(0).toUpperCase();
  } else {
    if (usernameDisplay) usernameDisplay.textContent = "Khách (Chưa đăng nhập)";
    if (userIdDisplay) userIdDisplay.textContent = "#GUEST";
    if (avatarChar) avatarChar.textContent = "G";
  }
  if (masteredCount) masteredCount.textContent = `${selectedWordSet.size} từ`;

  switchSettingsTab("tabSettingsProfile");
  settingsDropdown.classList.remove("hidden");
  refreshIcons();
}

function closeSettingsDropdown() {
  if (settingsDropdown) settingsDropdown.classList.add("hidden");
}

function toggleSettingsDropdown() {
  if (!settingsDropdown) return;
  if (settingsDropdown.classList.contains("hidden")) {
    openSettingsDropdown();
  } else {
    closeSettingsDropdown();
  }
}

// Backward compatibility aliases
const openSettingsModal = openSettingsDropdown;
const closeSettingsModal = closeSettingsDropdown;

if (btnSettings) {
  btnSettings.onclick = (e) => {
    e.stopPropagation();
    toggleSettingsDropdown();
  };
}

if (btnCloseSettingsModal) {
  btnCloseSettingsModal.onclick = (e) => {
    e.stopPropagation();
    closeSettingsDropdown();
  };
}

// Click outside to close dropdown
document.addEventListener("click", (e) => {
  if (settingsDropdown && !settingsDropdown.classList.contains("hidden")) {
    if (!settingsDropdown.contains(e.target) && (!btnSettings || !btnSettings.contains(e.target))) {
      closeSettingsDropdown();
    }
  }
});

// Escape key to close
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && settingsDropdown && !settingsDropdown.classList.contains("hidden")) {
    closeSettingsDropdown();
  }
});
function switchSettingsTab(targetId) {
  const tabBtns = document.querySelectorAll(".settings-tab-btn");
  const tabPanes = document.querySelectorAll(".settings-tab-pane");

  tabBtns.forEach((btn) => {
    if (btn.dataset.tab === targetId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  tabPanes.forEach((pane) => {
    if (pane.id === targetId) {
      pane.classList.add("active");
    } else {
      pane.classList.remove("active");
    }
  });
  refreshIcons();
}

document.querySelectorAll(".settings-tab-btn").forEach((btn) => {
  btn.onclick = () => switchSettingsTab(btn.dataset.tab);
});

// Change Password Handler
const formChangePassword = document.getElementById("formChangePassword");
if (formChangePassword) {
  formChangePassword.onsubmit = async (e) => {
    e.preventDefault();
    if (!currentUser) {
      notyf.error("Vui lòng đăng nhập để thực hiện đổi mật khẩu!");
      return;
    }
    const oldPass = document.getElementById("inputOldPassword").value;
    const newPass = document.getElementById("inputNewPassword").value;
    const confirmPass = document.getElementById("inputConfirmPassword").value;

    if (newPass !== confirmPass) {
      notyf.error("Mật khẩu mới và xác nhận mật khẩu không trùng khớp!");
      return;
    }

    const btnSubmit = document.getElementById("btnSubmitChangePassword");
    btnSubmit.disabled = true;

    try {
      const res = await fetch("/api/auth/change-password", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ old_password: oldPass, new_password: newPass }),
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        notyf.success(data.message || "Đổi mật khẩu thành công!");
        formChangePassword.reset();
        closeSettingsModal();
      } else {
        notyf.error(data.detail || data.message || "Không thể đổi mật khẩu.");
      }
    } catch (err) {
      notyf.error("Lỗi kết nối khi đổi mật khẩu: " + err.message);
    } finally {
      btnSubmit.disabled = false;
    }
  };
}

// Reset Vocab Handler
const btnResetVocab = document.getElementById("btnResetVocab");
if (btnResetVocab) {
  btnResetVocab.onclick = async () => {
    if (!confirm("Bạn có chắc chắn muốn đặt lại toàn bộ từ vựng đã tích về 0 không?")) return;
    try {
      const res = await fetch("/api/user/reset-vocab", {
        method: "POST",
        headers: getAuthHeaders(),
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        selectedWordSet.clear();
        updateMasteredCount();
        renderTopics();
        updateSyncBanners();
        notyf.success(data.message || "Đã đặt lại tiến độ từ vựng về mặc định!");
        closeSettingsModal();
      } else {
        notyf.error(data.detail || data.message || "Không thể đặt lại từ vựng.");
      }
    } catch (err) {
      notyf.error("Lỗi: " + err.message);
    }
  };
}

// Reset History Handler
const btnResetHistory = document.getElementById("btnResetHistory");
if (btnResetHistory) {
  btnResetHistory.onclick = async () => {
    if (!confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử bài tập luyện dịch không?")) return;
    try {
      const res = await fetch("/api/user/reset-history", {
        method: "POST",
        headers: getAuthHeaders(),
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (passageHistoryList) passageHistoryList.innerHTML = "";
        notyf.success(data.message || "Đã xóa toàn bộ lịch sử bài dịch!");
        closeSettingsModal();
      } else {
        notyf.error(data.detail || data.message || "Không thể xóa lịch sử.");
      }
    } catch (err) {
      notyf.error("Lỗi: " + err.message);
    }
  };
}



// ─── TAB 3: AI TRANSLATOR STUDIO CONTROLLER ─────────────────────────────────
let studioSourceLang = "en";
let studioTargetLang = "vi";
let studioRecognition = null;
let isStudioListening = false;

const studioSourceText = document.getElementById("studioSourceText");
const studioCharCount = document.getElementById("studioCharCount");
const btnDoTranslate = document.getElementById("btnDoTranslate");
const btnSwapStudioLang = document.getElementById("btnSwapStudioLang");
const btnStudioClear = document.getElementById("btnStudioClear");
const btnStudioMic = document.getElementById("btnStudioMic");
const btnStudioSpeak = document.getElementById("btnStudioSpeak");
const btnStudioCopy = document.getElementById("btnStudioCopy");
const studioTargetOutput = document.getElementById("studioTargetOutput");
const studioTargetPlaceholder = document.getElementById("studioTargetPlaceholder");
const studioLoadingIndicator = document.getElementById("studioLoadingIndicator");
const studioModelName = document.getElementById("studioModelName");
const studioInsightsCard = document.getElementById("studioInsightsCard");
const studioGrammarNotes = document.getElementById("studioGrammarNotes");
const studioKeyWordsList = document.getElementById("studioKeyWordsList");
const studioAltPhrasingsList = document.getElementById("studioAltPhrasingsList");
const sourcePaneTitle = document.getElementById("sourcePaneTitle");
const targetPaneTitle = document.getElementById("targetPaneTitle");
const studioSourceFlag = document.getElementById("studioSourceFlag");
const studioSourceTitle = document.getElementById("studioSourceTitle");
const studioTargetFlag = document.getElementById("studioTargetFlag");
const studioTargetTitle = document.getElementById("studioTargetTitle");

// Character Counter
if (studioSourceText && studioCharCount) {
  studioSourceText.addEventListener("input", () => {
    studioCharCount.textContent = studioSourceText.value.length;
  });
}

// Clear Button
if (btnStudioClear) {
  btnStudioClear.onclick = () => {
    if (studioSourceText) studioSourceText.value = "";
    if (studioCharCount) studioCharCount.textContent = "0";
    if (studioTargetOutput) {
      studioTargetOutput.textContent = "";
      studioTargetOutput.classList.add("hidden");
    }
    if (studioTargetPlaceholder) studioTargetPlaceholder.classList.remove("hidden");
    if (studioInsightsCard) studioInsightsCard.classList.add("hidden");
    const studioSpeedBadge = document.getElementById("studioSpeedBadge");
    if (studioSpeedBadge) studioSpeedBadge.classList.add("hidden");
  };
}

// Swap Languages (EN <-> VI)
if (btnSwapStudioLang) {
  btnSwapStudioLang.onclick = () => {
    const temp = studioSourceLang;
    studioSourceLang = studioTargetLang;
    studioTargetLang = temp;

    // Update labels & flags
    if (studioSourceLang === "en") {
      if (studioSourceFlag) studioSourceFlag.textContent = "🇺🇸";
      if (studioSourceTitle) studioSourceTitle.textContent = "Tiếng Anh (English)";
      if (studioTargetFlag) studioTargetFlag.textContent = "🇻🇳";
      if (studioTargetTitle) studioTargetTitle.textContent = "Tiếng Việt (Vietnamese)";
      if (sourcePaneTitle) sourcePaneTitle.textContent = "Văn bản gốc (English)";
      if (targetPaneTitle) targetPaneTitle.textContent = "Bản dịch AI (Tiếng Việt)";
      if (studioSourceText) studioSourceText.placeholder = "Nhập văn bản tiếng Anh cần dịch (hoặc nói micro)...";
    } else {
      if (studioSourceFlag) studioSourceFlag.textContent = "🇻🇳";
      if (studioSourceTitle) studioSourceTitle.textContent = "Tiếng Việt (Vietnamese)";
      if (studioTargetFlag) studioTargetFlag.textContent = "🇺🇸";
      if (studioTargetTitle) studioTargetTitle.textContent = "Tiếng Anh (English)";
      if (sourcePaneTitle) sourcePaneTitle.textContent = "Văn bản gốc (Tiếng Việt)";
      if (targetPaneTitle) targetPaneTitle.textContent = "Bản dịch AI (English)";
      if (studioSourceText) studioSourceText.placeholder = "Nhập văn bản tiếng Việt cần dịch (hoặc nói micro)...";
    }

    // Swap text contents if target text already exists
    if (studioTargetOutput && studioTargetOutput.textContent.trim()) {
      const prevTarget = studioTargetOutput.textContent.trim();
      studioSourceText.value = prevTarget;
      studioCharCount.textContent = prevTarget.length;
      studioTargetOutput.textContent = "";
      studioTargetOutput.classList.add("hidden");
      if (studioTargetPlaceholder) studioTargetPlaceholder.classList.remove("hidden");
      if (studioInsightsCard) studioInsightsCard.classList.add("hidden");
      // Trigger new translation in new direction
      executeLiveTranslation();
    }
    refreshIcons();
  };
}

// Execute Live Translation
async function executeLiveTranslation() {
  const text = studioSourceText ? studioSourceText.value.trim() : "";
  if (!text) {
    notyf.error("Vui lòng nhập hoặc nói văn bản cần dịch!");
    return;
  }

  const startTime = performance.now();
  const studioSpeedBadge = document.getElementById("studioSpeedBadge");
  if (studioSpeedBadge) studioSpeedBadge.classList.add("hidden");

  // UI loading state
  if (btnDoTranslate) btnDoTranslate.disabled = true;
  if (studioTargetPlaceholder) studioTargetPlaceholder.classList.add("hidden");
  if (studioTargetOutput) studioTargetOutput.classList.add("hidden");
  if (studioLoadingIndicator) studioLoadingIndicator.classList.remove("hidden");
  if (studioInsightsCard) studioInsightsCard.classList.add("hidden");

  try {
    const res = await fetch("/api/translate/live", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(currentUser && currentUser.token ? { "Authorization": `Bearer ${currentUser.token}` } : {})
      },
      body: JSON.stringify({
        text: text,
        source_lang: studioSourceLang,
        target_lang: studioTargetLang
      })
    });

    const elapsedSec = ((performance.now() - startTime) / 1000).toFixed(1);
    const data = await res.json();
    if (data.status === "error") {
      notyf.error(data.message || "Lỗi dịch thuật từ AI.");
      if (studioTargetPlaceholder) studioTargetPlaceholder.classList.remove("hidden");
      return;
    }

    // Render translation
    if (studioTargetOutput) {
      studioTargetOutput.textContent = data.translation || "(Không có kết quả dịch)";
      studioTargetOutput.classList.remove("hidden");
    }

    if (studioModelName) {
      studioModelName.textContent = "AI Translator";
    }

    if (studioSpeedBadge) {
      studioSpeedBadge.innerHTML = `<i data-lucide="zap" class="lucide-icon"></i> ⚡ ${elapsedSec}s • AI Engine`;
      studioSpeedBadge.classList.remove("hidden");
    }

    // Render Grammar & Insights
    if (data.grammar_notes || (data.key_words && data.key_words.length > 0) || (data.alternative_phrasings && data.alternative_phrasings.length > 0)) {
      if (studioGrammarNotes) {
        studioGrammarNotes.textContent = data.grammar_notes || "Cấu trúc câu tự nhiên, chuẩn ngữ cảnh bản xứ.";
      }

      // Key words
      if (studioKeyWordsList) {
        studioKeyWordsList.innerHTML = "";
        const words = data.key_words || [];
        if (words.length > 0) {
          const kwBlock = document.getElementById("studioKeyWordsBlock");
          if (kwBlock) kwBlock.classList.remove("hidden");
          words.forEach(w => {
            const card = document.createElement("div");
            card.className = "studio-keyword-card";
            card.innerHTML = `
              <div class="keyword-top">
                <span class="keyword-word">${escapeHtml(w.word || "")}</span>
                ${w.pos ? `<span class="keyword-pos">${escapeHtml(w.pos)}</span>` : ""}
              </div>
              ${w.ipa ? `<span class="keyword-ipa">${escapeHtml(w.ipa)}</span>` : ""}
              <div class="keyword-meaning">${escapeHtml(w.meaning || "")}</div>
            `;
            studioKeyWordsList.appendChild(card);
          });
        } else {
          const kwBlock = document.getElementById("studioKeyWordsBlock");
          if (kwBlock) kwBlock.classList.add("hidden");
        }
      }

      // Alternative phrasings
      if (studioAltPhrasingsList) {
        studioAltPhrasingsList.innerHTML = "";
        const alts = data.alternative_phrasings || [];
        if (alts.length > 0) {
          const altBlock = document.getElementById("studioAltPhrasingsBlock");
          if (altBlock) altBlock.classList.remove("hidden");
          alts.forEach(alt => {
            const li = document.createElement("li");
            li.className = "studio-alt-item";
            li.innerHTML = `<i data-lucide="check" class="lucide-icon"></i> <span>${escapeHtml(alt)}</span>`;
            studioAltPhrasingsList.appendChild(li);
          });
        } else {
          const altBlock = document.getElementById("studioAltPhrasingsBlock");
          if (altBlock) altBlock.classList.add("hidden");
        }
      }

      if (studioInsightsCard) studioInsightsCard.classList.remove("hidden");
    }

    refreshIcons();
  } catch (err) {
    notyf.error("Lỗi kết nối khi gửi bản dịch: " + err.message);
    if (studioTargetPlaceholder) studioTargetPlaceholder.classList.remove("hidden");
  } finally {
    if (studioLoadingIndicator) studioLoadingIndicator.classList.add("hidden");
    if (btnDoTranslate) btnDoTranslate.disabled = false;
  }
}

if (btnDoTranslate) {
  btnDoTranslate.onclick = executeLiveTranslation;
}

// Copy to Clipboard
if (btnStudioCopy) {
  btnStudioCopy.onclick = () => {
    const text = studioTargetOutput ? studioTargetOutput.textContent.trim() : "";
    if (!text) {
      notyf.error("Chưa có bản dịch để sao chép!");
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        notyf.success("Đã sao chép bản dịch vào bộ nhớ tạm!");
      }).catch(() => {
        notyf.error("Không thể tự động sao chép.");
      });
    } else {
      notyf.error("Trình duyệt không hỗ trợ clipboard API.");
    }
  };
}

// TTS Text-To-Speech Playback
if (btnStudioSpeak) {
  btnStudioSpeak.onclick = () => {
    const text = studioTargetOutput ? studioTargetOutput.textContent.trim() : "";
    if (!text) {
      notyf.error("Chưa có nội dung để đọc phát âm!");
      return;
    }
    if (!window.speechSynthesis) {
      notyf.error("Trình duyệt không hỗ trợ phát âm giọng nói (SpeechSynthesis)!");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = studioTargetLang === "vi" ? "vi-VN" : "en-US";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
    notyf.success(`Đang đọc bản dịch (${studioTargetLang.toUpperCase()})...`);
  };
}

// Voice STT Input (SpeechRecognition - Lazy & Safe WebKit Init)
if (btnStudioMic) {
  btnStudioMic.onclick = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      notyf.error("Trình duyệt không hỗ trợ nhận diện giọng nói (SpeechRecognition). Vui lòng dùng Chrome, Edge hoặc Safari mới nhất.");
      return;
    }

    if (isStudioListening) {
      if (studioRecognition) {
        try {
          studioRecognition.stop();
        } catch (e) {
          console.debug("STT stop error:", e);
        }
      }
      return;
    }

    try {
      if (!studioRecognition) {
        studioRecognition = new SpeechRecognition();
        studioRecognition.continuous = false;
        studioRecognition.interimResults = false;

        studioRecognition.onstart = () => {
          isStudioListening = true;
          btnStudioMic.classList.add("btn-recording-pulse");
          btnStudioMic.innerHTML = `<i data-lucide="mic" class="lucide-icon"></i> <span>Đang nghe...</span>`;
          refreshIcons();
        };

        studioRecognition.onresult = (event) => {
          const transcript = event.results && event.results[0] && event.results[0][0] && event.results[0][0].transcript;
          if (transcript && studioSourceText) {
            const currentVal = studioSourceText.value.trim();
            studioSourceText.value = currentVal ? `${currentVal} ${transcript}` : transcript;
            if (studioCharCount) studioCharCount.textContent = studioSourceText.value.length;
            notyf.success("Đã nhận diện giọng nói!");
          }
        };

        studioRecognition.onerror = (e) => {
          console.warn("STT Error:", e.error);
          if (e.error !== "no-speech") {
            notyf.error("Lỗi nhận diện âm thanh: " + (e.error || "Không rõ"));
          }
        };

        studioRecognition.onend = () => {
          isStudioListening = false;
          btnStudioMic.classList.remove("btn-recording-pulse");
          btnStudioMic.innerHTML = `<i data-lucide="mic" class="lucide-icon"></i> <span class="btn-label-mobile-hidden">Nói micro</span>`;
          refreshIcons();
        };
      }

      studioRecognition.lang = studioSourceLang === "en" ? "en-US" : "vi-VN";
      studioRecognition.start();
    } catch (err) {
      console.warn("Start STT failed:", err);
      isStudioListening = false;
      btnStudioMic.classList.remove("btn-recording-pulse");
      btnStudioMic.innerHTML = `<i data-lucide="mic" class="lucide-icon"></i> <span class="btn-label-mobile-hidden">Nói micro</span>`;
      refreshIcons();
      notyf.error("Không thể bật micro nhận diện giọng nói: " + (err.message || err));
    }
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// DASHBOARD QUICK ACTIONS & MICRO-QUIZ LOGIC
// ─────────────────────────────────────────────────────────────────────────────

// Dashboard Quick Action: Luyện Đọc Theo Từ
if (btnDashboardReadingAction) {
  btnDashboardReadingAction.onclick = function() {
    switchMainTab("translation");
    requestGeneratePassage(false);
  };
}

// Micro-Quiz State Management
let currentQuizData = null;
let currentQuizIndex = 0;
let quizScore = 0;
let isQuizAnswered = false;

function openQuizModal() {
  if (!quizModal) return;
  quizModal.classList.remove("hidden");
  fetchAndStartQuiz();
}

function closeQuizModal() {
  if (!quizModal) return;
  quizModal.classList.add("hidden");
  currentQuizData = null;
  currentQuizIndex = 0;
  quizScore = 0;
  isQuizAnswered = false;
}

async function fetchAndStartQuiz() {
  if (!quizModal) return;
  if (quizLoadingState) quizLoadingState.classList.remove("hidden");
  if (quizActiveContainer) quizActiveContainer.classList.add("hidden");
  if (quizCompletedView) quizCompletedView.classList.add("hidden");
  if (quizExplanationBox) quizExplanationBox.classList.add("hidden");

  try {
    const payload = {
      count: 3,
      selected_words: selectedWordSet ? Array.from(selectedWordSet) : []
    };
    const res = await fetch("/api/quiz/generate-unchecked", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error("HTTP " + res.status);
    }

    const data = await res.json();
    if (data && data.status === "success" && Array.isArray(data.quiz) && data.quiz.length > 0) {
      currentQuizData = data.quiz;
      currentQuizIndex = 0;
      quizScore = 0;
      renderCurrentQuizQuestion();
    } else {
      const errMsg = (data && data.message) ? data.message : "Không thể tạo bộ câu hỏi quiz từ vựng.";
      notyf.error(errMsg);
      closeQuizModal();
    }
  } catch (err) {
    console.error("Quiz generation error:", err);
    notyf.error("Lỗi khi kết nối sinh bài quiz: " + (err.message || err));
    closeQuizModal();
  } finally {
    if (quizLoadingState) quizLoadingState.classList.add("hidden");
  }
}

function renderCurrentQuizQuestion() {
  if (!currentQuizData || currentQuizIndex >= currentQuizData.length) {
    showQuizCompletion();
    return;
  }

  isQuizAnswered = false;
  if (quizActiveContainer) quizActiveContainer.classList.remove("hidden");
  if (quizCompletedView) quizCompletedView.classList.add("hidden");
  if (quizExplanationBox) quizExplanationBox.classList.add("hidden");

  const q = currentQuizData[currentQuizIndex];

  if (quizStepIndicator) {
    quizStepIndicator.textContent = "Câu hỏi " + (currentQuizIndex + 1) + " / " + currentQuizData.length;
  }
  if (quizTargetWord) {
    quizTargetWord.textContent = q.target_word || "...";
  }
  if (quizTargetIpa) {
    quizTargetIpa.textContent = q.ipa || "/.../";
  }
  if (quizQuestionText) {
    quizQuestionText.textContent = q.question || "";
  }

  // Render 4 Options
  if (quizOptionsGrid) {
    quizOptionsGrid.innerHTML = "";
    const options = Array.isArray(q.options) ? q.options : [];
    options.forEach(function(optText) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quiz-option-btn";
      btn.textContent = optText;
      btn.onclick = function() {
        handleQuizOptionClick(optText, q, btn);
      };
      quizOptionsGrid.appendChild(btn);
    });
  }

  // Reset "Đã thuộc từ này -> Tích ngay vào sổ" button
  if (btnQuizMarkMastered) {
    const targetWord = (q.target_word || "").toLowerCase().trim();
    const alreadyMastered = selectedWordSet && selectedWordSet.has(targetWord);
    btnQuizMarkMastered.disabled = alreadyMastered;
    if (alreadyMastered) {
      btnQuizMarkMastered.innerHTML = '<i data-lucide="check" class="lucide-icon"></i> <span>✓ Đã có trong sổ tay</span>';
    } else {
      btnQuizMarkMastered.innerHTML = '<i data-lucide="check-circle" class="lucide-icon"></i> <span>Đã thuộc từ này &rarr; Tích ngay vào sổ</span>';
    }
  }

  // Update Next button label
  if (btnQuizNext) {
    const isLast = currentQuizIndex === currentQuizData.length - 1;
    btnQuizNext.innerHTML = isLast 
      ? '<span>Xem kết quả</span> <i data-lucide="award" class="lucide-icon"></i>' 
      : '<span>Câu tiếp theo</span> <i data-lucide="arrow-right" class="lucide-icon"></i>';
  }

  refreshIcons();
}

function normalizeQuizAnswer(str) {
  if (!str) return "";
  return str.toString().trim().toLowerCase().replace(/^[a-d]\.\s*/i, "");
}

function handleQuizOptionClick(selectedText, questionObj, clickedBtn) {
  if (isQuizAnswered) return;
  isQuizAnswered = true;

  const userClean = normalizeQuizAnswer(selectedText);
  const correctClean = normalizeQuizAnswer(questionObj.correct_answer);
  const targetClean = normalizeQuizAnswer(questionObj.target_word);

  const isCorrect = (userClean === correctClean) || (userClean === targetClean);

  // Disable all option buttons and highlight correct/wrong
  if (quizOptionsGrid) {
    const allBtns = quizOptionsGrid.querySelectorAll(".quiz-option-btn");
    for (let i = 0; i < allBtns.length; i++) {
      const btn = allBtns[i];
      btn.disabled = true;
      const btnClean = normalizeQuizAnswer(btn.textContent);
      if (btnClean === correctClean || btnClean === targetClean) {
        btn.classList.add("quiz-option-correct");
      }
    }
  }

  if (isCorrect) {
    quizScore++;
    clickedBtn.classList.add("quiz-option-correct");
    if (quizResultIcon) {
      quizResultIcon.innerHTML = '<i data-lucide="check-circle-2" class="lucide-icon text-emerald-500"></i>';
    }
    if (quizResultTitle) {
      quizResultTitle.textContent = "Chính xác! Bạn ghi nhớ rất tốt!";
      quizResultTitle.className = "quiz-result-title text-emerald-500";
    }
  } else {
    clickedBtn.classList.add("quiz-option-wrong");
    if (quizResultIcon) {
      quizResultIcon.innerHTML = '<i data-lucide="alert-circle" class="lucide-icon text-rose-500"></i>';
    }
    if (quizResultTitle) {
      quizResultTitle.textContent = "Chưa đúng! Đáp án chính xác là: " + (questionObj.correct_answer || "");
      quizResultTitle.className = "quiz-result-title text-rose-500";
    }
  }

  // Show explanation
  if (quizExplanationText) {
    quizExplanationText.textContent = questionObj.explanation_vi || "Hãy ghi nhớ từ vựng và ngữ cảnh này!";
  }
  if (quizExplanationBox) {
    quizExplanationBox.classList.remove("hidden");
  }

  refreshIcons();
}

function showQuizCompletion() {
  if (quizActiveContainer) quizActiveContainer.classList.add("hidden");
  if (quizExplanationBox) quizExplanationBox.classList.add("hidden");
  if (quizCompletedView) quizCompletedView.classList.remove("hidden");

  const total = currentQuizData ? currentQuizData.length : 0;
  if (quizScoreText) {
    quizScoreText.textContent = "Bạn đã trả lời đúng " + quizScore + "/" + total + " câu hỏi từ vựng chưa thuộc.";
  }
  refreshIcons();
}

// Mark word as mastered directly from Quiz
if (btnQuizMarkMastered) {
  btnQuizMarkMastered.onclick = function() {
    if (!currentQuizData || !currentQuizData[currentQuizIndex]) return;
    const targetWord = (currentQuizData[currentQuizIndex].target_word || "").trim();
    if (!targetWord) return;

    // Add to local Set
    selectedWordSet.add(targetWord);

    // Sync across checkboxes in the UI if rendered
    const wordRows = document.querySelectorAll(".word-row");
    for (let i = 0; i < wordRows.length; i++) {
      const row = wordRows[i];
      const wName = row.querySelector(".word-name");
      if (wName && wName.textContent.trim().toLowerCase() === targetWord.toLowerCase()) {
        const chk = row.querySelector(".word-checkbox");
        if (chk) chk.checked = true;
        row.classList.add("selected");
      }
    }

    // Update parent topics and counts
    updateSelectedCount();
    updateSyncBanners();

    // Disable button with success label
    btnQuizMarkMastered.disabled = true;
    btnQuizMarkMastered.innerHTML = '<i data-lucide="check" class="lucide-icon"></i> <span>✓ Đã lưu vào sổ tay!</span>';
    refreshIcons();

    notyf.success('Đã thêm "' + targetWord + '" vào sổ tay từ vựng thành thạo!');
  };
}

// Quiz Navigation Buttons
if (btnQuizNext) {
  btnQuizNext.onclick = function() {
    currentQuizIndex++;
    renderCurrentQuizQuestion();
  };
}

if (btnQuizPlayAgain) {
  btnQuizPlayAgain.onclick = function() {
    fetchAndStartQuiz();
  };
}

if (btnQuizDone) {
  btnQuizDone.onclick = function() {
    closeQuizModal();
  };
}

if (btnDashboardQuizAction) {
  btnDashboardQuizAction.onclick = function() {
    openQuizModal();
  };
}

if (btnCloseQuizModal) {
  btnCloseQuizModal.onclick = function() {
    closeQuizModal();
  };
}

if (quizModal) {
  quizModal.onclick = function(e) {
    if (e.target === quizModal) {
      closeQuizModal();
    }
  };
}

document.addEventListener("keydown", function(e) {
  if (e.key === "Escape" && quizModal && !quizModal.classList.contains("hidden")) {
    closeQuizModal();
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// FLASHCARDS FEATURE (100% LOCAL, ZERO-LATENCY, NO AI OVERHEAD)
// ─────────────────────────────────────────────────────────────────────────────

let currentFlashcardDeck = [];
let currentFlashcardIndex = 0;
let flashcardMasteredThisSession = 0;
let isCardFlipped = false;

function speakWord(text) {
  if (typeof window !== "undefined" && "speechSynthesis" in window) {
    try {
      window.speechSynthesis.cancel();
      var utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn("Speech synthesis error:", e);
    }
  }
}

function getUnmasteredVocabList() {
  var list = [];
  if (syncedTopics && syncedTopics.length > 0) {
    for (var i = 0; i < syncedTopics.length; i++) {
      var topic = syncedTopics[i];
      if (topic && topic.words) {
        for (var j = 0; j < topic.words.length; j++) {
          var w = topic.words[j];
          if (w && w.word && (!selectedWordSet || !selectedWordSet.has(w.word))) {
            list.push(w);
          }
        }
      }
    }
  }
  return list;
}

function shuffleArray(arr) {
  var copy = arr.slice();
  for (var i = copy.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var temp = copy[i];
    copy[i] = copy[j];
    copy[j] = temp;
  }
  return copy;
}

async function openFlashcardModal() {
  if (!flashcardModal) return;
  if (!syncedTopics || syncedTopics.length === 0) {
    await syncVocabFromExcel();
  }

  var unmastered = getUnmasteredVocabList();
  if (unmastered.length === 0) {
    var all = [];
    if (syncedTopics && syncedTopics.length > 0) {
      for (var i = 0; i < syncedTopics.length; i++) {
        var t = syncedTopics[i];
        if (t && t.words) {
          for (var j = 0; j < t.words.length; j++) {
            all.push(t.words[j]);
          }
        }
      }
    }
    if (all.length === 0) {
      notyf.error("Chưa có dữ liệu từ vựng để mở thẻ lật.");
      return;
    }
    notyf.success("Bạn đã tích thuộc tất cả từ! Bắt đầu lượt ôn tập ngẫu nhiên.");
    unmastered = all;
  }

  var shuffled = shuffleArray(unmastered);
  var deckSize = Math.min(20, shuffled.length);
  currentFlashcardDeck = shuffled.slice(0, deckSize);
  currentFlashcardIndex = 0;
  flashcardMasteredThisSession = 0;

  flashcardModal.classList.remove("hidden");
  renderCurrentFlashcard();
}

function closeFlashcardModal() {
  if (!flashcardModal) return;
  flashcardModal.classList.add("hidden");
  currentFlashcardDeck = [];
  currentFlashcardIndex = 0;
  isCardFlipped = false;
  if (flashcardCardInner) {
    flashcardCardInner.classList.remove("is-flipped");
  }
}

function renderCurrentFlashcard() {
  if (!currentFlashcardDeck || currentFlashcardIndex >= currentFlashcardDeck.length) {
    showFlashcardCompletion();
    return;
  }

  isCardFlipped = false;
  if (flashcardCardInner) {
    flashcardCardInner.classList.remove("is-flipped");
  }

  if (flashcardActiveView) flashcardActiveView.classList.remove("hidden");
  if (flashcardCompletedView) flashcardCompletedView.classList.add("hidden");

  var item = currentFlashcardDeck[currentFlashcardIndex];
  var total = currentFlashcardDeck.length;

  if (flashcardCounter) {
    flashcardCounter.textContent = "Thẻ " + (currentFlashcardIndex + 1) + " / " + total;
  }

  if (flashcardProgressBar) {
    var pct = Math.round(((currentFlashcardIndex + 1) / total) * 100);
    flashcardProgressBar.style.width = pct + "%";
  }

  if (flashcardWord) {
    flashcardWord.textContent = item.word || "";
  }

  if (flashcardIpa) {
    flashcardIpa.textContent = item.ipa || "/.../";
  }

  if (flashcardPos) {
    flashcardPos.textContent = item.pos || "word";
  }

  if (flashcardMeaning) {
    flashcardMeaning.textContent = item.meaning || "";
  }

  if (item.example) {
    var parts = item.example.split(/[\/\n]/);
    var exEn = parts[0] ? parts[0].trim() : item.example;
    var exVi = parts[1] ? parts[1].trim() : "";
    if (flashcardExampleEn) flashcardExampleEn.textContent = exEn ? '"' + exEn + '"' : "";
    if (flashcardExampleVi) flashcardExampleVi.textContent = exVi ? "(" + exVi + ")" : "";
    if (flashcardExampleBox) flashcardExampleBox.classList.remove("hidden");
  } else {
    if (flashcardExampleBox) flashcardExampleBox.classList.add("hidden");
  }

  refreshIcons();
}

function flipFlashcard() {
  if (!flashcardCardInner) return;
  isCardFlipped = !isCardFlipped;
  flashcardCardInner.classList.toggle("is-flipped", isCardFlipped);
}

function skipCurrentFlashcard() {
  currentFlashcardIndex++;
  renderCurrentFlashcard();
}

function masterCurrentFlashcard() {
  if (!currentFlashcardDeck || !currentFlashcardDeck[currentFlashcardIndex]) return;
  var w = currentFlashcardDeck[currentFlashcardIndex];
  var wordName = (w.word || "").trim();
  if (!wordName) return;

  selectedWordSet.add(wordName);

  // Sync checkboxes in sidebar DOM
  var wordRows = document.querySelectorAll(".word-row");
  for (var i = 0; i < wordRows.length; i++) {
    var row = wordRows[i];
    var wNameEl = row.querySelector(".word-name") || row.querySelector(".word-term");
    if (wNameEl && wNameEl.textContent.trim().toLowerCase() === wordName.toLowerCase()) {
      var chk = row.querySelector(".word-checkbox");
      if (chk) chk.checked = true;
      row.classList.add("selected");
    }
  }

  updateSelectedCount();
  updateSyncBanners();
  flashcardMasteredThisSession++;

  notyf.success('Đã thuộc "' + wordName + '" & lưu vào sổ tay!');

  currentFlashcardIndex++;
  renderCurrentFlashcard();
}

function showFlashcardCompletion() {
  if (flashcardActiveView) flashcardActiveView.classList.add("hidden");
  if (flashcardCompletedView) flashcardCompletedView.classList.remove("hidden");

  if (flashcardSummaryText) {
    flashcardSummaryText.textContent = "Bạn đã tích thuộc " + flashcardMasteredThisSession + " từ vựng trong lượt ôn tập này.";
  }
  refreshIcons();
}

// Flashcard Event Bindings
if (flashcardScene) {
  flashcardScene.onclick = function() {
    flipFlashcard();
  };
}

if (btnFlashcardAudio) {
  btnFlashcardAudio.onclick = function(e) {
    e.stopPropagation();
    if (currentFlashcardDeck && currentFlashcardDeck[currentFlashcardIndex]) {
      speakWord(currentFlashcardDeck[currentFlashcardIndex].word);
    }
  };
}

if (btnFlashcardAudioBack) {
  btnFlashcardAudioBack.onclick = function(e) {
    e.stopPropagation();
    if (currentFlashcardDeck && currentFlashcardDeck[currentFlashcardIndex]) {
      speakWord(currentFlashcardDeck[currentFlashcardIndex].word);
    }
  };
}

if (btnFlashcardSkip) {
  btnFlashcardSkip.onclick = function(e) {
    e.stopPropagation();
    skipCurrentFlashcard();
  };
}

if (btnFlashcardMaster) {
  btnFlashcardMaster.onclick = function(e) {
    e.stopPropagation();
    masterCurrentFlashcard();
  };
}

if (btnFlashcardRestart) {
  btnFlashcardRestart.onclick = function() {
    openFlashcardModal();
  };
}

if (btnFlashcardDone) {
  btnFlashcardDone.onclick = function() {
    closeFlashcardModal();
  };
}

if (btnCloseFlashcardModal) {
  btnCloseFlashcardModal.onclick = function() {
    closeFlashcardModal();
  };
}

if (flashcardModal) {
  flashcardModal.onclick = function(e) {
    if (e.target === flashcardModal) {
      closeFlashcardModal();
    }
  };
}

if (btnDashboardFlashcardAction) {
  btnDashboardFlashcardAction.onclick = function() {
    openFlashcardModal();
  };
}

// Touch swipe gestures on flashcardScene (iPad & Mobile)
var touchStartX = 0;
var touchEndX = 0;
if (flashcardScene) {
  flashcardScene.addEventListener("touchstart", function(e) {
    if (e.changedTouches && e.changedTouches[0]) {
      touchStartX = e.changedTouches[0].screenX;
    }
  }, { passive: true });

  flashcardScene.addEventListener("touchend", function(e) {
    if (e.changedTouches && e.changedTouches[0]) {
      touchEndX = e.changedTouches[0].screenX;
      var diffX = touchEndX - touchStartX;
      if (Math.abs(diffX) > 60) {
        if (diffX < 0) {
          skipCurrentFlashcard();
        } else {
          masterCurrentFlashcard();
        }
      }
    }
  }, { passive: true });
}

// Keyboard shortcuts for Flashcard modal
document.addEventListener("keydown", function(e) {
  if (flashcardModal && !flashcardModal.classList.contains("hidden")) {
    if (e.key === "Escape") {
      closeFlashcardModal();
    } else if (e.code === "Space" || e.key === " ") {
      e.preventDefault();
      flipFlashcard();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      skipCurrentFlashcard();
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      masterCurrentFlashcard();
    }
  }
});
