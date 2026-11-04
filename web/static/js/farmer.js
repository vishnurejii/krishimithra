/**
 * KrishiMitra AI - Farmer Facing Portal Logic
 * Handles Malayalam/English bilingual switching, Voice-to-Text (SpeechRecognition),
 * Text-to-Speech audio readout, scheme search, eligibility check, and RAG Chatbot.
 */

let currentLang = 'en'; // 'en' or 'ml'
let isRecording = false;
let recognition = null;

const I18N = {
  en: {
    heroTitle: "Kerala Agriculture Scheme Intelligence",
    heroDesc: "Discover, verify and apply for agricultural subsidies, crop insurance, and farmer welfare benefits across Kerala.",
    searchPlaceholder: "Ask anything (e.g. Subsidy for Pepper, PM-KISAN documents, Wayanad schemes)...",
    searchBtn: "Search",
    eligibilityTitle: "Check Your Eligibility",
    eligibilityDesc: "Input your land size and crops to find exact subsidies you can claim.",
    chatTitle: "KrishiMitra AI Assistant",
    chatPlaceholder: "Ask in Malayalam or English...",
    chatWelcome: "Namaskaram! I am KrishiMitra AI. Ask me about any Kerala or Central agriculture schemes, subsidies, or application guidelines.",
    allSchemes: "All Schemes",
    paddy: "Paddy (നെല്ല്)",
    coconut: "Coconut (തെങ്ങ്)",
    pepper: "Pepper (കുരുമുളക്)",
    cardamom: "Cardamom (ഏലം)",
    banana: "Banana (വാഴ)",
    dairy: "Dairy (ക്ഷീരം)"
  },
  ml: {
    heroTitle: "കേരള കാർഷിക പദ്ധതി വിവര സഹായി",
    heroDesc: "കേരളത്തിലെ കർഷകർക്കുള്ള എല്ലാ സർക്കാർ സബ്സിഡികളും ആനുകൂല്യങ്ങളും കൃത്യമായി അറിയാനും അപേക്ഷിക്കാനും.",
    searchPlaceholder: "ചോദിക്കൂ (ഉദാ: കുരുമുളക് സബ്സിഡി, പി.എം കിസാൻ രേഖകൾ, വയനാട് പദ്ധതികൾ)...",
    searchBtn: "തിരയുക",
    eligibilityTitle: "നിങ്ങളുടെ അർഹത പരിശോധിക്കുക",
    eligibilityDesc: "ഭൂമിയുടെ അളവും വിളകളും നൽകി നിങ്ങൾക്ക് ലഭിക്കുന്ന സബ്സിഡികൾ കണ്ടെത്തൂ.",
    chatTitle: "കൃഷിമിത്ര എ.ഐ സഹായി",
    chatPlaceholder: "മലയാളത്തിലോ ഇംഗ്ലീഷിലോ ചോദിക്കൂ...",
    chatWelcome: "നമസ്കാരം! ഞാൻ കൃഷിമിത്ര എ.ഐ. കേരളത്തിലെയും കേന്ദ്രത്തിലെയും എല്ലാ കാർഷിക പദ്ധതികളെക്കുറിച്ചും സബ്സിഡികളെക്കുറിച്ചും ചോദിക്കാം.",
    allSchemes: "എല്ലാ പദ്ധതികളും",
    paddy: "നെല്ല്",
    coconut: "തെങ്ങ്",
    pepper: "കുരുമുളക്",
    cardamom: "ഏലം",
    banana: "വാഴ",
    dairy: "ക്ഷീരവികസനം"
  }
};

document.addEventListener("DOMContentLoaded", () => {
  setupLanguageToggle();
  setupVoiceInput();
  loadSchemesList();
  setupEligibilityForm();
  setupChatWidget();
});

function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'ml' : 'en';
  document.getElementById("langToggleBtn").textContent = currentLang === 'en' ? 'മലയാളം' : 'English';
  
  const dict = I18N[currentLang];
  document.getElementById("heroTitle").textContent = dict.heroTitle;
  document.getElementById("heroDesc").textContent = dict.heroDesc;
  document.getElementById("globalSearchInput").placeholder = dict.searchPlaceholder;
  document.getElementById("searchSubmitBtn").textContent = dict.searchBtn;
  document.getElementById("eligibilityCardTitle").textContent = dict.eligibilityTitle;
  document.getElementById("chatTitleText").textContent = dict.chatTitle;
  document.getElementById("chatInputField").placeholder = dict.chatPlaceholder;
  
  loadSchemesList();
}

function setupLanguageToggle() {
  const btn = document.getElementById("langToggleBtn");
  if (btn) btn.addEventListener("click", toggleLanguage);
}

// Voice Recognition (Web Speech API)
function setupVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const voiceBtn = document.getElementById("voiceSearchBtn");
  
  if (!SpeechRecognition) {
    if (voiceBtn) voiceBtn.title = "Voice recognition not supported in this browser";
    return;
  }
  
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  
  recognition.onstart = () => {
    isRecording = true;
    voiceBtn.classList.add("recording");
  };
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("globalSearchInput").value = transcript;
    performSearch(transcript);
  };
  
  recognition.onerror = (e) => {
    console.warn("Speech recognition error:", e);
    isRecording = false;
    voiceBtn.classList.remove("recording");
  };
  
  recognition.onend = () => {
    isRecording = false;
    voiceBtn.classList.remove("recording");
  };
  
  voiceBtn.addEventListener("click", () => {
    if (isRecording) {
      recognition.stop();
    } else {
      recognition.lang = currentLang === 'ml' ? 'ml-IN' : 'en-IN';
      recognition.start();
    }
  });
}

// Load Schemes List
async function loadSchemesList(crop = '', district = '') {
  const container = document.getElementById("schemesListContainer");
  container.innerHTML = `<div style="text-align:center; padding: 2rem; color: #64748b;">Loading schemes from official registry...</div>`;
  
  let url = `/api/schemes/?`;
  if (crop) url += `crop=${encodeURIComponent(crop)}&`;
  if (district) url += `district=${encodeURIComponent(district)}&`;
  
  try {
    const resp = await fetch(url);
    const data = await resp.json();
    
    if (!data.schemes || data.schemes.length === 0) {
      container.innerHTML = `
        <div style="background: white; padding: 2rem; border-radius: 14px; text-align: center; border: 1px solid #e2e8f0;">
          <p style="font-weight: 600; color: #64748b;">No schemes found matching the selected filter.</p>
        </div>`;
      return;
    }
    
    container.innerHTML = data.schemes.map(s => `
      <div class="scheme-card" id="scheme-${s.id}">
        <div class="scheme-card-header">
          <h3 class="scheme-card-title">${currentLang === 'ml' && s.malayalam_name ? s.malayalam_name : s.name}</h3>
          <span class="badge ${s.status === 'ACTIVE' ? 'badge-active' : 'badge-pending'}">${s.status}</span>
        </div>
        <p style="font-size: 0.9rem; color: #475569;">${s.department} &bull; ${s.level} Level</p>
        <div class="scheme-benefit-highlight">
          <strong>Benefit:</strong> ${s.benefits_summary}
        </div>
        <div class="scheme-meta">
          <span><strong>Eligible Crops:</strong> ${s.crops.length ? s.crops.join(', ') : 'Allied Crops'}</span>
          <span><strong>Verified:</strong> ${s.last_verified || 'Pending'}</span>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 0.75rem;">
          ${s.portal_url ? `<a href="${s.portal_url}" target="_blank" style="font-size: 0.85rem; font-weight: 700; color: #059669; text-decoration: none;">Apply on Official Portal &rarr;</a>` : ''}
          <button onclick="askAboutScheme('${escape(s.name)}')" style="background:none; border:none; color: #4338ca; font-size: 0.85rem; font-weight: 700; cursor: pointer;">Ask KrishiMitra AI</button>
        </div>
      </div>
    `).join("");
    
  } catch (err) {
    container.innerHTML = `<div style="color: red; padding: 1rem;">Failed to load schemes: ${err}</div>`;
  }
}

function filterByCrop(cropName, btnElem) {
  document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
  if (btnElem) btnElem.classList.add("active");
  loadSchemesList(cropName);
}

// Search
function performSearch(query) {
  if (!query) query = document.getElementById("globalSearchInput").value.trim();
  if (!query) return;
  
  // Submit to chat assistant
  addChatMessage(query, 'user');
  queryAssistant(query);
}

// Eligibility Checker
function setupEligibilityForm() {
  const form = document.getElementById("eligibilityForm");
  if (!form) return;
  
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const resultBox = document.getElementById("eligibilityResultBox");
    resultBox.style.display = "block";
    resultBox.innerHTML = `<div style="padding: 1rem; text-align: center; color: #64748b;">Evaluating schemes against your profile...</div>`;
    
    const payload = {
      district: document.getElementById("elDistrict").value,
      farmer_type: document.getElementById("elFarmerType").value,
      total_land_acres: parseFloat(document.getElementById("elLandAcres").value) || 1.0,
      primary_crops: [document.getElementById("elCrop").value],
      annual_income: 150000.0,
      caste_category: document.getElementById("elCategory").value
    };
    
    try {
      const resp = await fetch("/api/eligibility/evaluate/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      const res = data.result;
      
      if (!res.eligible_schemes || res.eligible_schemes.length === 0) {
        resultBox.innerHTML = `
          <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 1rem; border-radius: 8px; color: #991b1b; font-size: 0.9rem;">
            No direct matches found. Please consult your local Krishi Bhavan for customized local-body projects.
          </div>`;
        return;
      }
      
      resultBox.innerHTML = `
        <div style="background: #f0fdf4; border: 1px solid #86efac; padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem;">
          <h4 style="color: #166534; font-weight: 700; margin-bottom: 0.25rem;">You qualify for ${res.eligible_schemes.length} Scheme(s)!</h4>
          <p style="font-size: 0.85rem; color: #15803d;">Matched criteria: Landholding, District notification, and Crops.</p>
        </div>
        ${res.eligible_schemes.map(s => `
          <div style="background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
            <div style="font-weight: 700; color: #064e3b; font-size: 0.95rem;">${s.scheme_name}</div>
            <div style="font-size: 0.85rem; color: #059669; font-weight: 600; margin: 0.25rem 0;">${s.estimated_benefit}</div>
            <div style="font-size: 0.8rem; color: #475569;"><strong>Required:</strong> ${s.required_documents.join(", ")}</div>
            <a href="${s.official_application_portal}" target="_blank" style="display:inline-block; margin-top: 0.5rem; font-size: 0.8rem; font-weight: 700; color: #4338ca; text-decoration: none;">Apply Online &rarr;</a>
          </div>
        `).join("")}
      `;
    } catch (err) {
      resultBox.innerHTML = `<div style="color: red;">Error: ${err}</div>`;
    }
  });
}

// Chat Assistant Widget
function setupChatWidget() {
  const sendBtn = document.getElementById("chatSendBtn");
  const input = document.getElementById("chatInputField");
  
  if (!sendBtn || !input) return;
  
  sendBtn.addEventListener("click", () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    addChatMessage(text, 'user');
    queryAssistant(text);
  });
  
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      sendBtn.click();
    }
  });
}

function addChatMessage(text, sender) {
  const container = document.getElementById("chatMessagesContainer");
  const msgDiv = document.createElement("div");
  msgDiv.className = `message message-${sender}`;
  msgDiv.innerHTML = text.replace(/\n/g, "<br>");
  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

async function queryAssistant(query) {
  const container = document.getElementById("chatMessagesContainer");
  
  // Loading placeholder
  const loadingDiv = document.createElement("div");
  loadingDiv.className = "message message-bot";
  loadingDiv.id = "chatLoadingMsg";
  loadingDiv.textContent = currentLang === 'ml' ? "പരിശോധിക്കുന്നു..." : "Consulting official government guidelines...";
  container.appendChild(loadingDiv);
  container.scrollTop = container.scrollHeight;
  
  try {
    const resp = await fetch("/api/chat/ask/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, language: currentLang })
    });
    const data = await resp.json();
    loadingDiv.remove();
    
    if (data.status === "success") {
      const res = data.response;
      let html = res.answer.replace(/\n/g, "<br>");
      
      if (res.citations && res.citations.length > 0) {
        html += `<div class="citation-box"><strong>Official Citation:</strong><br>`;
        html += res.citations.map(c => `
          &bull; ${c.source_document} (Page ${c.page_number}) &mdash; <a href="${c.source_url}" target="_blank" style="color:#059669;">Official Document</a> (Verified: ${c.verified_at})
        `).join("<br>");
        html += `</div>`;
      }
      
      addChatMessage(html, 'bot');
    } else {
      addChatMessage("Sorry, I could not retrieve details at this moment.", 'bot');
    }
  } catch (err) {
    loadingDiv.remove();
    addChatMessage(`Error: ${err}`, 'bot');
  }
}

function askAboutScheme(schemeName) {
  const query = `What are the eligibility conditions and benefits for ${unescape(schemeName)}?`;
  addChatMessage(query, 'user');
  queryAssistant(query);
  document.getElementById("chatInputField").scrollIntoView({ behavior: 'smooth' });
}
