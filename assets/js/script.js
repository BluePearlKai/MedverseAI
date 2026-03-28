// 1. Updated Login to save User ID
const API_URL = "http://127.0.0.1:5000";

// --- LOGIN & SIGNUP ---
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem("user_id", data.user_id);
            window.location.href = "index.html";
        } else { alert(data.error); }
    } catch (e) { alert("Server is offline!"); }
}

// --- ACCOUNT PAGE DATA ---
// Function to fetch and display user data
async function loadAccountProfile() {
    const userId = localStorage.getItem("user_id");
    
    if (!userId) {
        console.warn("No user_id found. Please login.");
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/profile/${userId}`);
        const user = await response.json();

        if (response.ok) {
            // 1. Update Sidebar text
            document.getElementById("sidebarName").textContent = user.full_name;
            document.getElementById("sidebarEmail").textContent = user.email;

            // 2. Update Input field values
            document.getElementById("accName").value = user.full_name;
            document.getElementById("accEmail").value = user.email;

            // 3. Update the unique ID display
            document.getElementById("accID").textContent = "MV-" + userId.padStart(4, '0');
        }
    } catch (error) {
        console.error("Database connection error:", error);
    }
}

// Ensure the function runs when the page loads
window.onload = () => {
    const path = window.location.pathname;
    if (path.includes("account.html")) {
        loadAccountProfile();
    }
    // (Include your other path checks for reports.html or index.html here)
};

function logout() {
    localStorage.removeItem("user_id");
    window.location.href = "login.html";
}

// Trigger load on page load
if (window.location.pathname.includes("account.html")) {
    window.onload = loadAccountProfile;
}


function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById("uploadText").innerText = "Selected File:";
        document.getElementById("uploadSubtext").innerText = file.name;
        document.getElementById("uploadSubtext").style.color = "#00eaff";
        document.querySelector(".upload-area").style.borderColor = "#00eaff";
    }
}

function goToResult() {
    const langSelect = document.getElementById("languageSelect");
    if (langSelect) {
        localStorage.setItem("medverse_language", langSelect.value);
    }

    const loader = document.getElementById("loadingScreen");
    if (loader) {
        loader.style.display = "flex";
    }

    setTimeout(() => {
        window.location.href = "result.html";
    }, 3000);
}

function saveAccountDetails() {
    alert("Account details updated successfully.");
}


let originalReportText = "Your cholesterol levels are slightly elevated. White blood cell count is normal. No immediate critical risks detected. Lifestyle improvements are recommended.";

const resultPageOriginalTextMap = {
    brandLabel: "MedVerse AI",
    navHome: "Home",
    navReports: "Reports",
    navAccount: "Account",
    resultTitle: "Medical Report Analysis",
    summaryHeading: "AI Summary",
    translateBtn: "Translate",
    riskHeading: "Risk Assessment",
    riskLabel: "Low Risk",
    questionsHeading: "Doctor-Ready Questions",
    q1: "Should I adjust my diet?",
    q2: "Is further testing required?",
    q3: "Are lifestyle changes enough?",
    downloadBtn: "Download Full Report",
    disclaimerText: "Not a Medical Diagnosis. Consult a Professional."
};

const fallbackLanguages = [
    "english", "hindi", "tamil", "marathi", "assamese", "bengali", "spanish", "dogri",
    "gujarati", "kannada", "kashmiri", "konkani", "maithili", "malayalam", "manipuri",
    "nepali", "odia", "punjabi", "sanskrit", "santali", "sindhi", "telugu", "urdu"
];

const DEFAULT_BACKEND_BASE_URL = "http://127.0.0.1:5000";

function getBackendBaseUrl() {
    const saved = (localStorage.getItem("medverse_backend_url") || "").trim();
    if (saved) {
        return saved.replace(/\/$/, "");
    }
    return DEFAULT_BACKEND_BASE_URL;
}

function getReadableErrorMessage(error) {
    if (!error) {
        return "Unknown error";
    }

    if (typeof error === "string") {
        return error;
    }

    return error.message || "Unknown error";
}

function getLastAnalysis() {
    try {
        const raw = localStorage.getItem("medverse_last_analysis");
        return raw ? JSON.parse(raw) : null;
    } catch (error) {
        console.warn("Could not parse stored analysis.", error);
        return null;
    }
}

function applyStoredAnalysisToResultPage() {
    const analysis = getLastAnalysis();
    if (!analysis) {
        return;
    }

    if (analysis.summary) {
        originalReportText = analysis.summary;
    }

    const riskLabel = document.getElementById("riskLabel");
    if (riskLabel && analysis.risk_level) {
        riskLabel.textContent = analysis.risk_level;
    }

    const questions = Array.isArray(analysis.doctor_questions) ? analysis.doctor_questions : [];
    ["q1", "q2", "q3"].forEach((id, index) => {
        const el = document.getElementById(id);
        if (el && questions[index]) {
            el.textContent = questions[index];
        }
    });
}

async function fetchFromBackend(path, options = {}) {
    const url = `${getBackendBaseUrl()}${path}`;

    try {
        return await fetch(url, options);
    } catch (error) {
        throw new Error(
            `Could not reach backend at ${getBackendBaseUrl()}. Start Flask with: .venv\\Scripts\\python.exe app.py`
        );
    }
}

function toLabel(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

function applyResultPageTexts(textMap) {
    Object.keys(textMap).forEach((id) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = textMap[id];
        }
    });
}

async function fetchSupportedLanguages() {
    try {
        const response = await fetchFromBackend("/languages");
        if (!response.ok) {
            return fallbackLanguages;
        }

        const data = await response.json();
        if (Array.isArray(data.supported_languages) && data.supported_languages.length > 0) {
            return data.supported_languages;
        }
    } catch (error) {
        console.warn("Could not load language list from backend. Using fallback list.");
    }

    return fallbackLanguages;
}

async function setupResultLanguageDropdown() {
    const langSelect = document.getElementById("resultLangSelect");
    if (!langSelect) {
        return;
    }

    const selectedLanguage = localStorage.getItem("medverse_language") || "english";
    const languages = await fetchSupportedLanguages();

    langSelect.innerHTML = "";
    languages.forEach((lang) => {
        const option = document.createElement("option");
        option.value = lang;
        option.textContent = toLabel(lang);
        if (lang === selectedLanguage) {
            option.selected = true;
        }
        langSelect.appendChild(option);
    });

    if (!languages.includes(selectedLanguage)) {
        langSelect.value = "english";
        localStorage.setItem("medverse_language", "english");
    }
}

async function translateSummaryText(targetLang) {
    if ((targetLang || "english").toLowerCase() === "english") {
        return originalReportText;
    }

    const response = await fetchFromBackend("/translate_result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            text: originalReportText,
            target_lang: targetLang
        })
    });

    if (!response.ok) {
        const responseText = await response.text();
        let message = `Server error ${response.status}`;

        try {
            const errData = JSON.parse(responseText);
            message = errData.error || message;
        } catch (parseError) {
            if (responseText) {
                message = responseText;
            }
        }

        throw new Error(message);
    }

    const data = await response.json();
    return data.translated_text;
}

async function translateResultPageUI(targetLang) {
    if ((targetLang || "english").toLowerCase() === "english") {
        applyResultPageTexts(resultPageOriginalTextMap);
        return;
    }

    const ids = Object.keys(resultPageOriginalTextMap);
    const texts = ids.map((id) => resultPageOriginalTextMap[id]);

    const response = await fetchFromBackend("/translate_batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            texts,
            target_lang: targetLang
        })
    });

    if (!response.ok) {
        const responseText = await response.text();
        let message = `Server error ${response.status}`;

        try {
            const errData = JSON.parse(responseText);
            message = errData.error || message;
        } catch (parseError) {
            if (responseText) {
                message = responseText;
            }
        }

        throw new Error(message);
    }

    const data = await response.json();
    const translatedTexts = Array.isArray(data.translated_texts) ? data.translated_texts : [];

    if (translatedTexts.length !== ids.length) {
        throw new Error("Translated text count mismatch");
    }

    const translatedMap = {};
    ids.forEach((id, index) => {
        translatedMap[id] = translatedTexts[index];
    });

    applyResultPageTexts(translatedMap);
}

async function typeEffect() {
    const typingContainer = document.getElementById("typingText");
    if (!typingContainer) {
        return;
    }

    const targetLang = localStorage.getItem("medverse_language") || "english";
    let text = originalReportText;

    try {
        text = await translateSummaryText(targetLang);
    } catch (error) {
        console.warn("Summary translation failed. Using English summary.", error.message);
    }

    typingContainer.innerHTML = "";

    let i = 0;
    const speed = 35;

    const typing = setInterval(() => {
        if (i < text.length) {
            typingContainer.innerHTML += text.charAt(i);
            i += 1;
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: "smooth"
            });
        } else {
            clearInterval(typing);
        }
    }, speed);
}

async function manualTranslate() {
    const langSelect = document.getElementById("resultLangSelect");
    const typingContainer = document.getElementById("typingText");

    if (!langSelect || !typingContainer) {
        return;
    }

    const targetLang = langSelect.value || "english";
    localStorage.setItem("medverse_language", targetLang);

    typingContainer.innerText = "Translating...";

    try {
        await translateResultPageUI(targetLang);
        const translatedSummary = await translateSummaryText(targetLang);
        typingContainer.innerText = translatedSummary;
    } catch (error) {
        console.warn("Translation backend error:", error);
        typingContainer.innerText = `Error: ${getReadableErrorMessage(error)}`;
    }
}

async function initializeResultPage() {
    applyStoredAnalysisToResultPage();
    await setupResultLanguageDropdown();

    const targetLang = localStorage.getItem("medverse_language") || "english";

    try {
        await translateResultPageUI(targetLang);
    } catch (error) {
        console.warn("UI translation failed. Using English UI.", error.message);
        applyResultPageTexts(resultPageOriginalTextMap);
    }

    await typeEffect();
}

if (window.location.pathname.includes("result.html")) {
    window.onload = initializeResultPage;
}

function handleSignup(event) {
    event.preventDefault();

    const name = document.getElementById("fullname").value;
    alert("Welcome to MedVerse AI, " + name + "!");

    window.location.href = "index.html";
}

// 2. Real Upload Logic (Replaces fakeUpload)
function fakeUpload() {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) {
            return;
        }

        const userId = localStorage.getItem('user_id');
        if (!userId) {
            alert("Please login first.");
            window.location.href = "login.html";
            return;
        }
        
        const formData = new FormData();
        formData.append('report_file', file);
        formData.append('user_id', userId);

        try {
            const response = await fetch(`${getBackendBaseUrl()}/upload`, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (!response.ok) {
                alert(data.error || "Upload failed.");
                return;
            }

            if (data.analysis) {
                localStorage.setItem("medverse_last_analysis", JSON.stringify(data.analysis));
            }

            alert("Report analyzed successfully!");
            window.location.href = "result.html";
        } catch (error) {
            alert(`Upload failed: ${getReadableErrorMessage(error)}`);
        }
    };
    input.click();
}

// 3. Load Reports Logic
async function loadReports() {
    const userId = localStorage.getItem('user_id');
    const listContainer = document.getElementById('historyList'); // Must match HTML ID
    const emptyBox = document.getElementById('emptyState');

    if (!userId) return;

    try {
        const response = await fetch(`http://127.0.0.1:5000/history/${userId}`);
        const reports = await response.json();

        if (reports.length > 0) {
            emptyBox.style.display = 'none';
            listContainer.style.display = 'block';
            
            let html = '<h2 style="color: #00eaff; margin-bottom: 20px;">Recent Analyses</h2>';
            reports.forEach(r => {
                html += `
                    <div class="history-item">
                        <div>
                            <h4>${r.file_name}</h4>
                            <small>${new Date(r.upload_date).toLocaleDateString()}</small>
                        </div>
                        <button class="account-btn">View</button>
                    </div>`;
            });
            listContainer.innerHTML = html;
        }
    } catch (e) {
        console.error("Fetch error:", e);
    }
}

// Add this to the very end of script.js
document.addEventListener("DOMContentLoaded", () => {
    if (window.location.pathname.includes("reports.html")) {
        console.log("Reports page ready. Calling loadReports...");
        loadReports();
    }
});
