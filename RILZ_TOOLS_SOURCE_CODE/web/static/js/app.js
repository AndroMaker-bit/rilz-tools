/* ═══════════════════════════════════════════════════════════════════════════════
   RILZ WEB - APP CONTROLLER (LIQUID GLASS EDITION)
   ═══════════════════════════════════════════════════════════════════════════════ */

// ── State & Elements ────────────────────────────────────────────────────────
const state = {
  currentTheme: localStorage.getItem("rilz_theme") || "green",
  activeTab: "video",
  systemInfo: null,
  publicStartedTs: null,
  serverTimeDelta: 0,
};

// ── Initialize App ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initCyberGuard();
  initDeviceAndBatteryTelemetry();
  initHeaderClockAndUptime();
  initNavigation();
  initSettingsModal();
  initVideoTool();
  initCloudTool();
  initBypassTool();
  initImageTool();
  initQrTool();
  initCryptoTool();
  initIpTool();
  initVaultTool();
  initPdfTool();
  initStickerTool();
  fetchSystemInfo();
});

// ── Toast Notification System ───────────────────────────────────────────────
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const icons = {
    success: "✅",
    error: "❌",
    info: "⚡",
    warning: "⚠️",
  };

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${icons[type] || "⚡"}</span>
    <span style="flex:1;">${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ── Theme Manager ───────────────────────────────────────────────────────────
function initTheme() {
  try {
    localStorage.removeItem("rilz_theme");
  } catch (e) {}
  document.body.className = "";
}

// ── Navigation Tabs ─────────────────────────────────────────────────────────
function initNavigation() {
  const buttons = document.querySelectorAll(".nav-pill-btn");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.dataset.tab;
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;

  document.querySelectorAll(".nav-pill-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tabId);
  });

  document.querySelectorAll(".tab-pane").forEach((pane) => {
    pane.style.display = pane.id === `tab-${tabId}` ? "block" : "none";
  });
}

// ── Settings Modal ──────────────────────────────────────────────────────────
function initSettingsModal() {
  const modal = document.getElementById("settingsModal");
  const openBtn = document.getElementById("openSettingsBtn");
  const closeBtn = document.getElementById("closeSettingsBtn");

  if (!modal || !openBtn) return;

  const openModal = () => modal.classList.add("active");
  const closeModal = () => modal.classList.remove("active");

  openBtn.addEventListener("click", openModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("active")) {
      closeModal();
    }
  });

  // Copy share URL button
  const copyShareBtn = document.getElementById("copyShareUrlBtn");
  if (copyShareBtn) {
    copyShareBtn.addEventListener("click", () => {
      const url = copyShareBtn.dataset.url || window.location.href;
      navigator.clipboard.writeText(url).then(() => {
        showToast("Link berhasil disalin! Kirim ke temen lu 🚀", "success");
      });
    });
  }
}

// ── Device & Battery Telemetry ──────────────────────────────────────────────
function initDeviceAndBatteryTelemetry() {
  // 1. Detect Device Type
  const ua = navigator.userAgent || "";
  let deviceType = "Desktop";
  let deviceIcon = "💻";

  if (/iPhone/i.test(ua)) {
    deviceType = "iPhone";
    deviceIcon = "🍎";
  } else if (/iPad/i.test(ua)) {
    deviceType = "iPad";
    deviceIcon = "🍎";
  } else if (/Android/i.test(ua)) {
    deviceType = "Android";
    deviceIcon = "🤖";
  } else if (/Windows/i.test(ua)) {
    deviceType = "Windows";
    deviceIcon = "💻";
  } else if (/Macintosh|Mac OS X/i.test(ua)) {
    deviceType = "Mac";
    deviceIcon = "🍏";
  } else if (/Linux/i.test(ua)) {
    deviceType = "Linux";
    deviceIcon = "🐧";
  } else if (/Mobi|Mobile/i.test(ua)) {
    deviceType = "Phone";
    deviceIcon = "📱";
  }

  const devIconEl = document.getElementById("deviceIcon");
  const devTextEl = document.getElementById("deviceText");
  if (devIconEl) devIconEl.textContent = deviceIcon;
  if (devTextEl) devTextEl.textContent = deviceType;

  // 2. Battery Telemetry (navigator.getBattery API)
  const battIconEl = document.getElementById("batteryIcon");
  const battTextEl = document.getElementById("batteryText");

  const updateBattery = (battery) => {
    const level = Math.round(battery.level * 100);
    const charging = battery.charging;
    let icon = "🔋";
    if (charging) {
      icon = "⚡";
    } else if (level <= 20) {
      icon = "🪫";
    } else if (level <= 50) {
      icon = "🔋";
    }

    if (battIconEl) battIconEl.textContent = icon;
    if (battTextEl) {
      battTextEl.textContent = charging ? `${level}%⚡` : `${level}%`;
      battTextEl.style.color = level <= 20 && !charging ? "#ff1a40" : "#fff";
    }
  };

  if ("getBattery" in navigator && typeof navigator.getBattery === "function") {
    navigator.getBattery().then((battery) => {
      updateBattery(battery);
      battery.addEventListener("levelchange", () => updateBattery(battery));
      battery.addEventListener("chargingchange", () => updateBattery(battery));
    }).catch(() => {
      if (battIconEl) battIconEl.textContent = "🔌";
      if (battTextEl) battTextEl.textContent = "AC Power";
    });
  } else {
    // Battery API not supported (e.g. iOS Safari)
    if (battIconEl) battIconEl.textContent = "🔌";
    if (battTextEl) battTextEl.textContent = "Online";
  }
}

// ── Header Digital Clock & Public Uptime Ticker ─────────────────────────────
function initHeaderClockAndUptime() {
  const clockEl = document.getElementById("liveClockText");
  const uptimeEl = document.getElementById("publicUptimeText");
  if (!clockEl && !uptimeEl) return;

  function tick() {
    // 1. Digital Clock (HH:MM:SS WIB)
    if (clockEl) {
      const now = new Date();
      const h = String(now.getHours()).padStart(2, "0");
      const m = String(now.getMinutes()).padStart(2, "0");
      const s = String(now.getSeconds()).padStart(2, "0");
      clockEl.textContent = `${h}:${m}:${s} WIB`;
    }

    // 2. Public Uptime
    updatePublicUptime();
  }

  tick();
  setInterval(tick, 1000);
}

function updatePublicUptime() {
  const uptimeEl = document.getElementById("publicUptimeText");
  if (!uptimeEl) return;

  const nowSec = Math.floor(Date.now() / 1000) - (state.serverTimeDelta || 0);
  const startSec = state.publicStartedTs || state.sessionStartSec || (state.sessionStartSec = Math.floor(Date.now() / 1000));
  const diffSec = Math.max(0, nowSec - startSec);

  const days = Math.floor(diffSec / 86400);
  const hours = Math.floor((diffSec % 86400) / 3600);
  const mins = Math.floor((diffSec % 3600) / 60);
  const secs = diffSec % 60;

  let text = "";
  if (days > 0) {
    text = `${days}h ${String(hours).padStart(2, "0")}j ${String(mins).padStart(2, "0")}m`;
  } else {
    text = `${String(hours).padStart(2, "0")}j ${String(mins).padStart(2, "0")}m ${String(secs).padStart(2, "0")}d`;
  }
  uptimeEl.textContent = text;
}

// ── Fetch System Info (Local IP, Version & Public Uptime) ───────────────────
async function fetchSystemInfo() {
  try {
    const res = await fetch("/api/system/info");
    const data = await res.json();
    state.systemInfo = data;

    if (data.public_started_ts) {
      state.publicStartedTs = data.public_started_ts;
    }
    if (data.now_ts) {
      state.serverTimeDelta = Math.floor(Date.now() / 1000) - data.now_ts;
    }

    const ipPill = document.getElementById("localIpText");
    if (ipPill && data.local_url) {
      ipPill.textContent = data.local_ip;
    }

    const shareUrlElem = document.getElementById("shareableUrl");
    const copyShareBtn = document.getElementById("copyShareUrlBtn");
    if (shareUrlElem && data.local_url) {
      shareUrlElem.textContent = data.local_url;
      if (copyShareBtn) copyShareBtn.dataset.url = data.local_url;
    }

    updatePublicUptime();
  } catch (err) {
    console.warn("System info fetch error:", err);
  }
}

// ── Tool 1: Video Downloader ────────────────────────────────────────────────
function initVideoTool() {
  const form = document.getElementById("videoForm");
  const urlInput = document.getElementById("videoUrl");
  const btn = document.getElementById("videoSubmitBtn");
  const resultBox = document.getElementById("videoResult");
  const pasteBtn = document.getElementById("pasteVideoBtn");
  const btnModeVideo = document.getElementById("btnModeVideo");
  const btnModeAudio = document.getElementById("btnModeAudio");
  const formatModeInput = document.getElementById("videoFormatMode");
  const formatTipText = document.getElementById("formatTipText");

  if (!form) return;

  // Paste from clipboard helper
  if (pasteBtn && urlInput) {
    pasteBtn.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          urlInput.value = text.trim();
          showToast("Link berhasil ditempel dari clipboard! 📋", "info");
        }
      } catch (err) {
        showToast("Klik kanan dan Paste manual di kolom input", "warning");
      }
    });
  }

  // Format Switchers
  const setFormatMode = (mode) => {
    if (formatModeInput) formatModeInput.value = mode;
    if (mode === "audio") {
      if (btnModeAudio) {
        btnModeAudio.style.background = "var(--primary-dim)";
        btnModeAudio.style.borderColor = "var(--primary)";
        btnModeAudio.style.color = "var(--primary)";
        btnModeAudio.style.boxShadow = "0 0 15px var(--primary-glow)";
      }
      if (btnModeVideo) {
        btnModeVideo.style.background = "rgba(255,255,255,0.03)";
        btnModeVideo.style.borderColor = "var(--glass-border)";
        btnModeVideo.style.color = "var(--text-secondary)";
        btnModeVideo.style.boxShadow = "none";
      }
      if (btn) btn.innerHTML = `<span>🎵</span> Download Musik MP3 Langsung`;
      if (formatTipText) {
        formatTipText.innerHTML = `Audio otomatis diekstrak menjadi file <strong>.MP3</strong> jernih (192kbps). Langsung tersimpan.`;
      }
    } else {
      if (btnModeVideo) {
        btnModeVideo.style.background = "var(--primary-dim)";
        btnModeVideo.style.borderColor = "var(--primary)";
        btnModeVideo.style.color = "var(--primary)";
        btnModeVideo.style.boxShadow = "0 0 15px var(--primary-glow)";
      }
      if (btnModeAudio) {
        btnModeAudio.style.background = "rgba(255,255,255,0.03)";
        btnModeAudio.style.borderColor = "var(--glass-border)";
        btnModeAudio.style.color = "var(--text-secondary)";
        btnModeAudio.style.boxShadow = "none";
      }
      if (btn) btn.innerHTML = `<span>🚀</span> Download Video MP4 Langsung`;
      if (formatTipText) {
        formatTipText.innerHTML = `Video otomatis tersimpan sebagai <strong>.MP4</strong> resmi dengan audio jernih. Langsung terunduh ke perangkat.`;
      }
    }
  };

  if (btnModeVideo) {
    btnModeVideo.addEventListener("click", () => setFormatMode("video"));
  }
  if (btnModeAudio) {
    btnModeAudio.addEventListener("click", () => setFormatMode("audio"));
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = (urlInput ? urlInput.value : "").trim();
    const mode = formatModeInput ? formatModeInput.value : "video";
    const audioOnly = mode === "audio";

    if (!url) {
      showToast("Masukkan URL video terlebih dahulu", "warning");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = `<span>⏳</span> Memproses & Menyiapkan Unduhan...`;
    resultBox.classList.remove("active");

    try {
      showToast("Menghubungkan ke server target & merender media...", "info");

      const formData = new FormData();
      formData.append("url", url);
      formData.append("audio_only", audioOnly);

      const res = await fetch("/api/video/download", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Gagal memproses dan mengunduh video");
      }

      // ── TRIGGER DIRECT BROWSER DOWNLOAD IMMEDIATELY ──
      const directA = document.createElement("a");
      directA.href = data.download_url;
      directA.download = data.filename;
      document.body.appendChild(directA);
      directA.click();
      setTimeout(() => directA.remove(), 1000);

      showToast(`✅ Berhasil! File '${data.filename}' langsung diunduh ke browser.`, "success");

      const thumbHtml = data.thumbnail
        ? `<div style="text-align:center; margin-bottom:0.75rem;"><img src="${data.thumbnail}" alt="Thumbnail" style="max-height:140px; border-radius:10px; border:1px solid var(--glass-border); box-shadow:0 4px 15px rgba(0,0,0,0.5);"></div>`
        : "";

      resultBox.innerHTML = `
        ${thumbHtml}
        <div style="font-size:0.95rem; font-weight:700; color:#fff; margin-bottom:0.4rem; line-height:1.3;">
          ${data.title}
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.85rem;">
          <span style="font-size:0.75rem; background:rgba(34,197,94,0.15); border:1px solid #22c55e; color:#22c55e; padding:0.25rem 0.6rem; border-radius:6px; font-weight:700;">
            ${audioOnly ? "🎵 Audio MP3" : "🎬 Video MP4"}
          </span>
          <span style="font-size:0.75rem; background:rgba(255,255,255,0.06); border:1px solid var(--glass-border); color:var(--text-secondary); padding:0.25rem 0.6rem; border-radius:6px;">
            💾 ${data.size_mb || "N/A"} MB
          </span>
          <span style="font-size:0.75rem; background:rgba(56,189,248,0.15); border:1px solid #38bdf8; color:#38bdf8; padding:0.25rem 0.6rem; border-radius:6px;">
            ⚡ Langsung Masuk Downloads
          </span>
        </div>

        <div style="padding:0.7rem; border-radius:8px; background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.25); color:#86efac; font-size:0.82rem; margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem;">
          <span>✅</span>
          <span>Unduhan telah otomatis dimulai oleh browser! Jika belum mulai, klik tombol di bawah:</span>
        </div>

        <div style="display:flex; gap:0.5rem; flex-direction:column;">
          <a href="${data.download_url}" download="${data.filename}" class="btn-liquid-primary" style="text-decoration:none; display:flex; align-items:center; justify-content:center; gap:0.5rem; padding:0.7rem;">
            <span>📥</span> Download Ulang (${data.filename})
          </a>
        </div>
      `;
      resultBox.classList.add("active");
    } catch (err) {
      showToast(err.message, "error");
      resultBox.innerHTML = `
        <div style="color:#ef4444; font-weight:700; margin-bottom:0.4rem;">❌ Gagal Mengunduh Media</div>
        <div style="font-size:0.85rem; color:var(--text-secondary);">${err.message}</div>
      `;
      resultBox.classList.add("active");
    } finally {
      btn.disabled = false;
      const currentMode = formatModeInput ? formatModeInput.value : "video";
      btn.innerHTML = currentMode === "audio"
        ? `<span>🎵</span> Download Musik MP3 Langsung`
        : `<span>🚀</span> Download Video MP4 Langsung`;
    }
  });
}

// ── Tool 2: Cloud Storage Ripper ────────────────────────────────────────────
function initCloudTool() {
  const form = document.getElementById("cloudForm");
  const btn = document.getElementById("cloudSubmitBtn");
  const resultBox = document.getElementById("cloudResult");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = document.getElementById("cloudUrl").value.trim();

    if (!url) {
      showToast("Masukkan URL file cloud", "warning");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = `<span>⚡</span> Mem-bypass Cloud Storage...`;

    try {
      const formData = new FormData();
      formData.append("url", url);

      const res = await fetch("/api/cloud/rip", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      resultBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
          <span style="font-weight:700; color:var(--primary);">🎯 Bypass ${data.service} Berhasil!</span>
          <span class="brand-badge">${data.service}</span>
        </div>
        <div style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:1rem; word-break:break-all;">
          ${data.direct_download_url}
        </div>
        <div style="display:flex; gap:0.75rem;">
          <a href="${data.direct_download_url}" target="_blank" class="btn-liquid-primary" style="text-decoration:none; text-align:center;">
            🚀 Download File Langsung
          </a>
          <button type="button" class="btn-liquid-secondary" onclick="navigator.clipboard.writeText('${data.direct_download_url}').then(() => showToast('Link disalin!'))">
            📋 Salin Link
          </button>
        </div>
      `;
      resultBox.classList.add("active");
      showToast("Direct download link siap!", "success");
    } catch (err) {
      showToast(err.message, "error");
      resultBox.innerHTML = `<div style="color:#ff4d6d;">❌ ${err.message}</div>`;
      resultBox.classList.add("active");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<span>🔓</span> Bypass & Ambil Direct Link`;
    }
  });
}

// ── Tool 3: Link Bypass & Unshortener ────────────────────────────────────────
function initBypassTool() {
  const form = document.getElementById("bypassForm");
  const btn = document.getElementById("bypassSubmitBtn");
  const resultBox = document.getElementById("bypassResult");
  const pasteBtn = document.getElementById("pasteBypassBtn");
  const urlInput = document.getElementById("bypassUrl");

  if (!form) return;

  if (pasteBtn && urlInput) {
    pasteBtn.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          urlInput.value = text.trim();
          showToast("Link berhasil ditempel dari clipboard! 📋", "info");
        }
      } catch (err) {
        showToast("Klik kanan dan Paste manual di kolom input", "warning");
      }
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = (urlInput ? urlInput.value : "").trim();

    if (!url) {
      showToast("Masukkan URL yang mau dibongkar", "warning");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = `<span>⏳</span> Membongkar proteksi Safelink & token...`;

    try {
      const formData = new FormData();
      formData.append("url", url);

      const res = await fetch("/api/link/bypass", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      let hopsHtml = data.hops
        .map(
          (hop, i) => `
        <div style="font-size:0.82rem; padding:0.4rem 0.6rem; background:rgba(255,255,255,0.03); border-radius:6px; margin-bottom:0.35rem; display:flex; gap:0.5rem; word-break:break-all;">
          <span style="color:var(--primary); font-weight:700;">#${i + 1}</span>
          <span style="color:var(--text-secondary);">${hop}</span>
        </div>
      `
        )
        .join("");

      const isFailedSafelink = data.is_safelink || data.final_url === data.original_url;

      const headerTitle = isFailedSafelink
        ? `<div style="color:#f59e0b; font-weight:800; font-size:1rem; margin-bottom:0.75rem; display:flex; align-items:center; gap:0.5rem;">
             <span>⚠️</span> Safelink Memerlukan Verifikasi CAPTCHA Manual:
           </div>
           <div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.75rem; line-height:1.4;">
             Situs safelink ini menggunakan proteksi anti-bot / Cloudflare Turnstile ketat sehingga token link tujuan belum bisa diambil otomatis tanpa interaksi manusia.
           </div>`
        : `<div style="color:var(--primary); font-weight:800; font-size:1rem; margin-bottom:0.75rem; display:flex; align-items:center; gap:0.5rem;">
             <span>🎯</span> Target Asli Berhasil Terbongkar! (${data.hop_count} Redirect Hops):
           </div>`;

      resultBox.innerHTML = `
        ${headerTitle}
        <div style="padding:0.85rem; background:var(--primary-dim); border:1px solid var(--primary-border); border-radius:10px; margin-bottom:1rem; word-break:break-all; box-shadow:0 0 15px var(--primary-glow);">
          <div style="font-size:0.75rem; color:var(--text-secondary); margin-bottom:0.25rem;">${isFailedSafelink ? "Halaman Safelink:" : "Direct Target URL:"}</div>
          <strong style="color:#fff; font-size:0.95rem;">${data.final_url}</strong>
        </div>
        <div style="margin-bottom:1rem;">
          <div style="font-size:0.85rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.4rem;">Jalur Bypass & Redirect:</div>
          ${hopsHtml}
        </div>
        <div style="display:flex; gap:0.75rem;">
          <a href="${data.final_url}" target="_blank" class="btn-liquid-primary" style="text-decoration:none; text-align:center; flex:1;">
            🌐 Buka Target di Tab Baru
          </a>
          <button type="button" class="btn-liquid-secondary" onclick="navigator.clipboard.writeText('${data.final_url}').then(() => showToast('Target URL disalin! 🚀'))">
            📋 Salin URL
          </button>
        </div>
      `;
      resultBox.classList.add("active");
      if (isFailedSafelink) {
        showToast("Safelink memuat CAPTCHA manual", "warning");
      } else {
        showToast("Safelink berhasil ditembus ke target asli!", "success");
      }
    } catch (err) {
      showToast(err.message, "error");
      resultBox.innerHTML = `<div style="color:#ff4d6d;">❌ ${err.message}</div>`;
      resultBox.classList.add("active");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<span>⚡</span> Bongkar Safelink Sekarang`;
    }
  });
}

// ── Tool 4: Image Lab (HD & Background Remover) ─────────────────────────────
function initImageTool() {
  const form = document.getElementById("imageForm");
  const fileInput = document.getElementById("imageFileInput");
  const dropzone = document.getElementById("imageDropzone");
  const dropText = document.getElementById("imageDropText");
  const btn = document.getElementById("imageSubmitBtn");
  const resultBox = document.getElementById("imageResult");

  if (!form || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      dropText.innerHTML = `<strong>${fileInput.files[0].name}</strong> (${(fileInput.files[0].size / 1024).toFixed(1)} KB)`;
    }
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      dropText.innerHTML = `<strong>${fileInput.files[0].name}</strong> (${(fileInput.files[0].size / 1024).toFixed(1)} KB)`;
    }
  });

  // Toggle HD scale vs RM BG tolerance fields dynamically
  const modeRadios = document.querySelectorAll('input[name="imageMode"]');
  const hdGroup = document.getElementById("hdGroup");
  const rmbgGroup = document.getElementById("rmbgGroup");
  const syncImageModeUI = () => {
    const activeMode = document.querySelector('input[name="imageMode"]:checked')?.value || "hd";
    if (hdGroup) hdGroup.style.display = activeMode === "hd" ? "block" : "none";
    if (rmbgGroup) rmbgGroup.style.display = activeMode === "rmbg" ? "block" : "none";
  };
  modeRadios.forEach((r) => r.addEventListener("change", syncImageModeUI));
  syncImageModeUI();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!fileInput.files || fileInput.files.length === 0) {
      showToast("Pilih file gambar terlebih dahulu", "warning");
      return;
    }

    const mode = document.querySelector('input[name="imageMode"]:checked').value;
    const endpoint = mode === "rmbg" ? "/api/image/rmbg" : "/api/image/hd";

    btn.disabled = true;
    btn.innerHTML = `<span>⏳</span> Memproses visual AI...`;

    try {
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      if (mode === "hd") {
        const scale = document.getElementById("hdScale").value;
        formData.append("scale", scale);
      } else {
        const tol = document.getElementById("rmbgTolerance").value;
        formData.append("tolerance", tol);
      }

      showToast("Sedang memproses gambar di server...", "info");

      const res = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: "Server mengembalikan status error " + res.status }));
        throw new Error(err.error || "Gagal memproses gambar");
      }

      const blob = await res.blob();
      const imgUrl = window.URL.createObjectURL(blob);

      resultBox.innerHTML = `
        <div style="color:var(--primary); font-weight:700; margin-bottom:0.75rem;">
          ✨ Hasil Pemrosesan Gambar:
        </div>
        <div style="text-align:center; background:rgba(0,0,0,0.4); border-radius:12px; padding:1rem; margin-bottom:1rem;">
          <img src="${imgUrl}" style="max-width:100%; max-height:350px; border-radius:8px; box-shadow:0 10px 30px rgba(0,0,0,0.5);" />
        </div>
        <a href="${imgUrl}" download="rilz_${mode}_output.png" class="btn-liquid-primary" style="text-decoration:none; text-align:center;">
          📥 Download Gambar Hasil PNG
        </a>
      `;
      resultBox.classList.add("active");
      showToast("Gambar berhasil diproses!", "success");
    } catch (err) {
      showToast(err.message, "error");
      resultBox.innerHTML = `<div style="color:#ff4d6d;">❌ ${err.message}</div>`;
      resultBox.classList.add("active");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<span>✨</span> Eksekusi Visual Sekarang`;
    }
  });
}

// ── Tool 5: QR Code Generator ───────────────────────────────────────────────
function initQrTool() {
  const form = document.getElementById("qrForm");
  const input = document.getElementById("qrText");
  const btn = document.getElementById("qrSubmitBtn");
  const resultBox = document.getElementById("qrResult");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) {
      showToast("Masukkan teks atau link untuk QR code", "warning");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = `<span>⏳</span> Membuat QR...`;

    try {
      const formData = new FormData();
      formData.append("text", text);
      formData.append("fill_color", getComputedStyle(document.documentElement).getPropertyValue("--primary").trim() || "#00ff88");
      formData.append("back_color", "#05080f");

      const res = await fetch("/api/qr", {
        method: "POST",
        body: formData,
      });

      const blob = await res.blob();
      const qrUrl = window.URL.createObjectURL(blob);

      resultBox.innerHTML = `
        <div style="text-align:center; padding:1.5rem; background:rgba(0,0,0,0.4); border-radius:16px; margin-bottom:1rem;">
          <img src="${qrUrl}" style="width:240px; height:240px; border-radius:12px; border:2px solid var(--primary-border); box-shadow:0 0 30px var(--primary-glow);" />
        </div>
        <a href="${qrUrl}" download="rilz_qr_${Date.now()}.png" class="btn-liquid-primary" style="text-decoration:none; text-align:center;">
          📥 Download QR Code PNG High-Res
        </a>
      `;
      resultBox.classList.add("active");
      showToast("QR Code berhasil dibuat!", "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<span>📱</span> Generate QR Matrix`;
    }
  });
}

// ── Tool 6: Crypto & Password Keygen ─────────────────────────────────────────
function initCryptoTool() {
  const passBtn = document.getElementById("genPassBtn");
  const passLength = document.getElementById("passLength");
  const passLengthVal = document.getElementById("passLengthVal");
  const passOutput = document.getElementById("passOutput");

  if (passLength && passLengthVal) {
    passLength.addEventListener("input", () => {
      passLengthVal.textContent = passLength.value;
    });
  }

  if (passBtn) {
    passBtn.addEventListener("click", () => {
      const length = parseInt(passLength.value, 10) || 18;
      const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+~`|}{[]:;?><,./-=";
      let pass = "";
      const arr = new Uint32Array(length);
      window.crypto.getRandomValues(arr);
      for (let i = 0; i < length; i++) {
        pass += chars[arr[i] % chars.length];
      }
      passOutput.value = pass;
      showToast("Password super aman berhasil digenerate!", "success");
    });
  }

  const copyPassBtn = document.getElementById("copyPassBtn");
  if (copyPassBtn && passOutput) {
    copyPassBtn.addEventListener("click", () => {
      if (!passOutput.value) return;
      navigator.clipboard.writeText(passOutput.value).then(() => {
        showToast("Password disalin ke clipboard!", "success");
      });
    });
  }

  // Hash Generator
  const hashForm = document.getElementById("hashForm");
  if (hashForm) {
    hashForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = document.getElementById("hashInput").value;
      if (!text) return;

      const formData = new FormData();
      formData.append("text", text);

      const res = await fetch("/api/hash", { method: "POST", body: formData });
      const data = await res.json();
      const resultBox = document.getElementById("hashResult");

      resultBox.innerHTML = `
        <div style="margin-bottom:0.75rem;">
          <div style="font-size:0.75rem; color:var(--text-secondary);">MD5:</div>
          <input class="glass-input" readonly value="${data.md5}" onclick="this.select(); navigator.clipboard.writeText(this.value); showToast('MD5 disalin!')" style="font-family:monospace; margin-bottom:0.5rem;" />
        </div>
        <div style="margin-bottom:0.75rem;">
          <div style="font-size:0.75rem; color:var(--text-secondary);">SHA-256:</div>
          <input class="glass-input" readonly value="${data.sha256}" onclick="this.select(); navigator.clipboard.writeText(this.value); showToast('SHA-256 disalin!')" style="font-family:monospace; margin-bottom:0.5rem;" />
        </div>
      `;
      resultBox.classList.add("active");
    });
  }
}

// ── Tool 7: IP Recon ────────────────────────────────────────────────────────
function initIpTool() {
  const form = document.getElementById("ipForm");
  const resultBox = document.getElementById("ipResult");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const target = document.getElementById("ipTarget").value.trim();

    try {
      const url = target ? `/api/ip?target=${encodeURIComponent(target)}` : "/api/ip";
      const res = await fetch(url);
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      resultBox.innerHTML = `
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:0.75rem; margin-bottom:1rem;">
          <div style="padding:0.75rem; background:rgba(255,255,255,0.03); border-radius:8px;">
            <div style="font-size:0.75rem; color:var(--text-secondary);">IP Query:</div>
            <strong style="color:var(--primary); font-size:1.1rem;">${data.ip}</strong>
          </div>
          <div style="padding:0.75rem; background:rgba(255,255,255,0.03); border-radius:8px;">
            <div style="font-size:0.75rem; color:var(--text-secondary);">Lokasi:</div>
            <strong>${data.city}, ${data.region}, ${data.country} (${data.country_code})</strong>
          </div>
          <div style="padding:0.75rem; background:rgba(255,255,255,0.03); border-radius:8px;">
            <div style="font-size:0.75rem; color:var(--text-secondary);">ISP / Org:</div>
            <strong>${data.isp} (${data.org || 'N/A'})</strong>
          </div>
          <div style="padding:0.75rem; background:rgba(255,255,255,0.03); border-radius:8px;">
            <div style="font-size:0.75rem; color:var(--text-secondary);">ASN:</div>
            <strong>${data.asn}</strong>
          </div>
        </div>
        <a href="${data.maps_url}" target="_blank" class="btn-liquid-secondary" style="display:inline-block; text-decoration:none;">
          📍 Buka Koordinat di Google Maps (${data.lat}, ${data.lon})
        </a>
      `;
      resultBox.classList.add("active");
    } catch (err) {
      showToast(err.message, "error");
    }
  });
}

// ── Tool 8: Vault Web ───────────────────────────────────────────────────────
function initVaultTool() {
  const searchInput = document.getElementById("vaultSearchInput");
  const resultBox = document.getElementById("vaultResult");
  const noteForm = document.getElementById("vaultNoteForm");

  if (searchInput) {
    let timeout = null;
    searchInput.addEventListener("input", () => {
      clearTimeout(timeout);
      const q = searchInput.value.trim();
      if (!q) {
        resultBox.classList.remove("active");
        return;
      }
      timeout = setTimeout(async () => {
        try {
          const res = await fetch(`/api/vault/search?keyword=${encodeURIComponent(q)}`);
          const data = await res.json();
          if (!data.success || data.results.length === 0) {
            resultBox.innerHTML = `<div style="color:var(--text-dim);">Tidak ada snippet/catatan ditemukan untuk keyword ini.</div>`;
            resultBox.classList.add("active");
            return;
          }

          let html = data.results
            .map(
              (item) => `
            <div style="padding:0.85rem; background:rgba(255,255,255,0.03); border:1px solid var(--glass-border); border-radius:10px; margin-bottom:0.75rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:var(--primary); font-size:1rem;">${item.title}</strong>
                <span class="brand-badge">${item.category}</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-secondary); margin:0.4rem 0;">${item.description || item.filepath}</div>
              <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:var(--text-dim);">
                <span>Tags: ${item.tags || '—'}</span>
                <span>${(item.size_bytes / 1024).toFixed(1)} KB • ${item.created_at.slice(0, 10)}</span>
              </div>
            </div>
          `
            )
            .join("");

          resultBox.innerHTML = html;
          resultBox.classList.add("active");
        } catch (err) {
          console.error(err);
        }
      }, 300);
    });
  }

  if (noteForm) {
    noteForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const title = document.getElementById("vaultNoteTitle").value.trim();
      const content = document.getElementById("vaultNoteContent").value.trim();
      const tags = document.getElementById("vaultNoteTags").value.trim();

      if (!title || !content) {
        showToast("Judul dan isi catatan wajib diisi", "warning");
        return;
      }

      const formData = new FormData();
      formData.append("title", title);
      formData.append("content", content);
      formData.append("tags", tags);

      try {
        const res = await fetch("/api/vault/note", { method: "POST", body: formData });
        const data = await res.json();
        if (data.success) {
          showToast("Catatan tersimpan aman di Vault!", "success");
          noteForm.reset();
        } else {
          showToast(data.error, "error");
        }
      } catch (err) {
        showToast(err.message, "error");
      }
    });
  }
}

// ── Cyber Anti-Inspect & Anti-Theft Guard ──────────────────────────────────
function initCyberGuard() {
  // 1. Disable Right-Click Context Menu
  document.addEventListener("contextmenu", (e) => {
    // Allow right click inside standard input fields if needed
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") {
      return true;
    }
    e.preventDefault();
    showToast("🛡️ AKSES DILINDUNGI: Klik kanan & inspeksi elemen dinonaktifkan!", "warning");
    return false;
  });

  // 2. Block DevTools & Source Inspection Shortcuts
  document.addEventListener("keydown", (e) => {
    // F12
    if (e.key === "F12" || e.keyCode === 123) {
      e.preventDefault();
      showToast("⛔ F12 DevTools diblokir oleh Cyber Shield!", "error");
      return false;
    }
    // Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C (Inspect Element / Console)
    if (
      e.ctrlKey &&
      e.shiftKey &&
      (e.key === "I" || e.key === "i" || e.key === "J" || e.key === "j" || e.key === "C" || e.key === "c")
    ) {
      e.preventDefault();
      showToast("⛔ Shortcut inspeksi kode diblokir!", "error");
      return false;
    }
    // Ctrl+U (View Source)
    if (e.ctrlKey && (e.key === "u" || e.key === "U")) {
      e.preventDefault();
      showToast("⛔ View Source diblokir oleh Cyber Shield!", "error");
      return false;
    }
    // Ctrl+S (Save Page)
    if (e.ctrlKey && (e.key === "s" || e.key === "S")) {
      e.preventDefault();
      return false;
    }
  });

  // 3. Cyber Console Warning Banner
  try {
    const banner = `
  ██████╗ ██╗██╗     ███████╗    ███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
  ██╔══██╗██║██║     ╚══███╔╝    ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
  ██████╔╝██║██║       ███╔╝     ███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝ 
  ██╔══██╗██║██║      ███╔╝      ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝  
  ██║  ██║██║███████╗███████╗    ███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║   
  ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝    ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝   
  [ RILZ CYBER SECURITY SHIELD ACTIVE — UNAUTHORIZED INSPECTION RESTRICTED ]
    `;
    console.log("%c" + banner, "color: #ff1a40; font-weight: bold; font-family: monospace; font-size: 11px;");
    console.log(
      "%c⛔ PERINGATAN: Source code, aset, dan sistem ini dilindungi RILZ CYBER SECURITY SHIELD.\nDilarang menduplikasi atau mengeksploitasi sistem ini.",
      "color: #ff1a40; font-size: 13px; font-weight: 800;"
    );
  } catch (err) {}

  // 4. Settings Modal PIN Management
  const savePinBtn = document.getElementById("savePinBtn");
  const oldPinInput = document.getElementById("oldMasterPin");
  const newPinInput = document.getElementById("newMasterPin");

  if (savePinBtn && newPinInput) {
    savePinBtn.addEventListener("click", async () => {
      const oldPin = (oldPinInput ? oldPinInput.value : "").trim();
      const newPin = newPinInput.value.trim();

      if (!oldPin || !newPin) {
        showToast("Masukkan PIN saat ini dan PIN baru", "warning");
        return;
      }

      if (newPin.length < 4) {
        showToast("PIN baru minimal 4 karakter", "warning");
        return;
      }

      savePinBtn.disabled = true;
      savePinBtn.innerHTML = "<span>⏳</span> Menyimpan...";

      try {
        const formData = new FormData();
        formData.append("current_pin", oldPin);
        formData.append("new_pin", newPin);

        const res = await fetch("/api/security/update-pin", {
          method: "POST",
          body: formData,
        });

        const data = await res.json();
        if (data.success) {
          showToast("Master PIN berhasil diperbarui! 🛡️", "success");
          if (oldPinInput) oldPinInput.value = "";
          newPinInput.value = "";
        } else {
          showToast(data.error || "Gagal mengubah PIN", "error");
        }
      } catch (err) {
        showToast(err.message, "error");
      } finally {
        savePinBtn.disabled = false;
        savePinBtn.innerHTML = "💾 Simpan PIN Baru";
      }
    });
  }
}

// ── Tool: PDF Toolkit Suite ────────────────────────────────────────────────
function initPdfTool() {
  const tabBtns = document.querySelectorAll(".pdf-tab-btn");
  if (!tabBtns.length) return;

  // Tab switching
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const tab = btn.dataset.tab;
      document.querySelectorAll(".pdf-pane").forEach((p) => (p.style.display = "none"));
      const activePane = document.getElementById(`tab-${tab}`);
      if (activePane) activePane.style.display = "block";
    });
  });

  // Setup click & drag-drop helper
  const setupDropzone = (zoneId, inputId, labelId, isMultiple = false) => {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const label = document.getElementById(labelId);
    if (!zone || !input) return;

    zone.addEventListener("click", () => input.click());
    zone.addEventListener("dragover", (e) => {
      e.preventDefault();
      zone.classList.add("dragover");
    });
    zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
    zone.addEventListener("drop", (e) => {
      e.preventDefault();
      zone.classList.remove("dragover");
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        updateLabel();
      }
    });

    const updateLabel = () => {
      if (input.files.length === 1) {
        label.innerText = `📄 ${input.files[0].name} (${(input.files[0].size / 1024).toFixed(1)} KB)`;
      } else if (input.files.length > 1) {
        label.innerText = `📑 ${input.files.length} file dipilih`;
      }
    };

    input.addEventListener("change", updateLabel);
  };

  setupDropzone("dropzoneCompress", "fileCompress", "labelCompress");
  setupDropzone("dropzoneMerge", "filesMerge", "labelMerge", true);
  setupDropzone("dropzoneImages", "filesImages", "labelImages", true);

  // 1. Compress Form
  const compressForm = document.getElementById("compressForm");
  const resultCompress = document.getElementById("resultCompress");
  const btnCompress = document.getElementById("btnCompressSubmit");

  if (compressForm) {
    compressForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fileInput = document.getElementById("fileCompress");
      const quality = document.getElementById("qualityCompress").value;
      if (!fileInput.files.length) {
        showToast("Pilih file PDF yang mau dikompres", "warning");
        return;
      }

      btnCompress.disabled = true;
      btnCompress.innerHTML = "<span>⏳</span> Mengompres PDF & merampingkan stream...";

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      formData.append("quality", quality);

      try {
        const res = await fetch("/api/pdf/compress", { method: "POST", body: formData });
        const data = await res.json();
        if (data.success) {
          const isZeroSave = !data.saved_percent || data.saved_percent <= 0;
          const statusTitle = isZeroSave ? "Dokumen PDF Sudah Optimal" : "PDF Berhasil Dikompres!";
          const statusIcon = isZeroSave ? "ℹ️" : "✅";
          const subText = isZeroSave 
            ? "PDF ini sudah dalam kondisi paling ringkas, ukuran dipertahankan tanpa mengurangi kualitas." 
            : `Berhasil memangkas <strong>${data.saved_percent}%</strong> ukuran file (${data.orig_str} ➔ ${data.comp_str})!`;

          resultCompress.innerHTML = `
            <div style="color:#10b981; font-weight:800; font-size:1.05rem; margin-bottom:0.75rem; display:flex; align-items:center; gap:0.5rem;">
              <span>${statusIcon}</span> ${statusTitle}
            </div>
            <div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:0.85rem;">
              ${subText}
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-bottom:1rem;">
              <div style="background:rgba(255,255,255,0.03); border:1px solid var(--glass-border); border-radius:10px; padding:0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:var(--text-secondary);">Ukuran Awal</div>
                <strong style="font-size:1rem; color:#fff;">${data.orig_str}</strong>
              </div>
              <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#10b981;">Ukuran Hasil (${data.saved_percent || 0}% Hemat)</div>
                <strong style="font-size:1rem; color:#10b981;">${data.comp_str}</strong>
              </div>
            </div>
            <a href="${data.download_url}" download class="btn-liquid-primary" style="text-decoration:none; text-align:center; display:flex; justify-content:center;">
              📥 Download PDF Ramping (${data.comp_str})
            </a>
          `;
          resultCompress.classList.add("active");
          showToast(isZeroSave ? "PDF sudah dalam ukuran optimal!" : `PDF berhasil dirampingkan ${data.saved_percent}%! 🚀`, "success");
        } else {
          showToast(data.error || "Gagal mengompres PDF", "error");
          resultCompress.innerHTML = `<div style="color:#ff4d6d; padding:0.8rem; background:rgba(255,77,109,0.1); border-radius:8px; border:1px solid rgba(255,77,109,0.3);">❌ ${data.error || "Gagal mengompres PDF"}</div>`;
          resultCompress.classList.add("active");
        }
      } catch (err) {
        showToast(err.message, "error");
        resultCompress.innerHTML = `<div style="color:#ff4d6d; padding:0.8rem; background:rgba(255,77,109,0.1); border-radius:8px; border:1px solid rgba(255,77,109,0.3);">❌ ${err.message}</div>`;
        resultCompress.classList.add("active");
      } finally {
        btnCompress.disabled = false;
        btnCompress.innerHTML = "<span>⚡</span> Kompres PDF Sekarang";
      }
    });
  }

  // 2. Merge Form
  const mergeForm = document.getElementById("mergeForm");
  const resultMerge = document.getElementById("resultMerge");
  const btnMerge = document.getElementById("btnMergeSubmit");

  if (mergeForm) {
    mergeForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const filesInput = document.getElementById("filesMerge");
      if (!filesInput.files || filesInput.files.length < 2) {
        showToast("Pilih minimal 2 file PDF untuk digabungkan", "warning");
        return;
      }

      btnMerge.disabled = true;
      btnMerge.innerHTML = "<span>⏳</span> Menggabungkan seluruh halaman PDF...";

      const formData = new FormData();
      for (let i = 0; i < filesInput.files.length; i++) {
        formData.append("files", filesInput.files[i]);
      }

      try {
        const res = await fetch("/api/pdf/merge", { method: "POST", body: formData });
        const data = await res.json();
        if (data.success) {
          resultMerge.innerHTML = `
            <div style="color:var(--primary); font-weight:800; font-size:1.05rem; margin-bottom:0.75rem; display:flex; align-items:center; gap:0.5rem;">
              <span>✅</span> ${data.total_files} PDF Berhasil Digabung!
            </div>
            <div style="background:var(--primary-dim); border:1px solid var(--primary-border); border-radius:10px; padding:0.85rem; margin-bottom:1rem;">
              <div style="font-size:0.85rem; color:#fff;">Total Halaman: <strong>${data.total_pages} Halaman</strong></div>
              <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.2rem;">Ukuran Gabungan: ${data.size_str}</div>
            </div>
            <a href="${data.download_url}" download class="btn-liquid-primary" style="text-decoration:none; text-align:center; display:flex; justify-content:center;">
              📥 Download Dokumen PDF Gabungan
            </a>
          `;
          resultMerge.classList.add("active");
          showToast(`Berhasil gabung ${data.total_files} file jadi ${data.total_pages} halaman! 🚀`, "success");
        } else {
          showToast(data.error || "Gagal menggabungkan PDF", "error");
        }
      } catch (err) {
        showToast(err.message, "error");
      } finally {
        btnMerge.disabled = false;
        btnMerge.innerHTML = "<span>🔗</span> Gabungkan Semua PDF";
      }
    });
  }

  // 3. Images to PDF Form
  const imagesForm = document.getElementById("imagesForm");
  const resultImages = document.getElementById("resultImages");
  const btnImages = document.getElementById("btnImagesSubmit");

  if (imagesForm) {
    imagesForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const filesInput = document.getElementById("filesImages");
      if (!filesInput.files || !filesInput.files.length) {
        showToast("Pilih minimal 1 file gambar", "warning");
        return;
      }

      btnImages.disabled = true;
      btnImages.innerHTML = "<span>⏳</span> Mengonversi foto menjadi halaman PDF...";

      const formData = new FormData();
      for (let i = 0; i < filesInput.files.length; i++) {
        formData.append("files", filesInput.files[i]);
      }

      try {
        const res = await fetch("/api/pdf/images-to-pdf", { method: "POST", body: formData });
        const data = await res.json();
        if (data.success) {
          resultImages.innerHTML = `
            <div style="color:var(--primary); font-weight:800; font-size:1.05rem; margin-bottom:0.75rem; display:flex; align-items:center; gap:0.5rem;">
              <span>✅</span> ${data.total_pages} Foto Disatukan ke PDF!
            </div>
            <div style="background:var(--primary-dim); border:1px solid var(--primary-border); border-radius:10px; padding:0.85rem; margin-bottom:1rem;">
              <div style="font-size:0.85rem; color:#fff;">Total Halaman: <strong>${data.total_pages} Halaman</strong></div>
              <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.2rem;">Ukuran PDF: ${data.size_str}</div>
            </div>
            <a href="${data.download_url}" download class="btn-liquid-primary" style="text-decoration:none; text-align:center; display:flex; justify-content:center;">
              📥 Download PDF dari Foto
            </a>
          `;
          resultImages.classList.add("active");
          showToast(`Berhasil mengubah ${data.total_pages} foto jadi PDF! 🚀`, "success");
        } else {
          showToast(data.error || "Gagal membuat PDF", "error");
        }
      } catch (err) {
        showToast(err.message, "error");
      } finally {
        btnImages.disabled = false;
        btnImages.innerHTML = "<span>📄</span> Buat Dokumen PDF dari Foto";
      }
    });
  }
}

// ── Tool: WhatsApp Sticker & GIF Converter ─────────────────────────────────
function initStickerTool() {
  const form = document.getElementById("stickerForm");
  if (!form) return;

  const modeBtns = document.querySelectorAll(".mode-btn");
  const durationSetting = document.getElementById("durationSetting");
  const durationRange = document.getElementById("durationRange");
  const durationVal = document.getElementById("durationVal");
  const dropzone = document.getElementById("dropzoneSticker");
  const input = document.getElementById("mediaInput");
  const label = document.getElementById("dropzoneLabel");
  const icon = document.getElementById("dropzoneIcon");
  const btn = document.getElementById("btnStickerSubmit");
  const resultBox = document.getElementById("resultSticker");

  let currentMode = "wa_animated";

  modeBtns.forEach((b) => {
    b.addEventListener("click", () => {
      modeBtns.forEach((mb) => mb.classList.remove("active"));
      b.classList.add("active");
      currentMode = b.dataset.mode;

      if (currentMode === "wa_static") {
        durationSetting.style.display = "none";
        icon.innerText = "🖼️";
        label.innerText = "Pilih Foto / Gambar (PNG, JPG, WebP)";
        input.accept = "image/*";
      } else {
        durationSetting.style.display = "block";
        icon.innerText = currentMode === "gif" ? "🎬" : "✨";
        label.innerText = "Pilih Video atau GIF yang Mau Diubah";
        input.accept = "video/*,image/gif";
      }
    });
  });

  if (durationRange && durationVal) {
    durationRange.addEventListener("input", (e) => {
      durationVal.innerText = `${parseFloat(e.target.value).toFixed(1)} Detik`;
    });
  }

  if (dropzone && input) {
    dropzone.addEventListener("click", () => input.click());
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        updateLabel();
      }
    });

    const updateLabel = () => {
      if (input.files.length) {
        label.innerText = `🎬 ${input.files[0].name} (${(input.files[0].size / 1024).toFixed(1)} KB)`;
      }
    };
    input.addEventListener("change", updateLabel);
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!input.files.length) {
      showToast("Pilih file video atau foto terlebih dahulu", "warning");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = `<span>⏳</span> Memproses konversi dengan FFmpeg engine...`;

    const formData = new FormData();
    formData.append("file", input.files[0]);
    formData.append("mode", currentMode);
    formData.append("duration", durationRange ? durationRange.value : 6.0);
    formData.append("fps", 15);

    try {
      const res = await fetch("/api/sticker/convert", { method: "POST", body: formData });
      const data = await res.json();
      if (data.success) {
        const isWa = currentMode.startsWith("wa");
        const statusBadge = isWa
          ? data.wa_compliant
            ? '<span style="color:#10b981; font-weight:700;">✅ Sesuai Standar WhatsApp (&le; 500KB)</span>'
            : '<span style="color:#f59e0b; font-weight:700;">⚠️ Mendekati batas WhatsApp</span>'
          : '<span style="color:#10b981; font-weight:700;">✅ Looping GIF Siap Pakai</span>';

        resultBox.innerHTML = `
          <div style="color:var(--primary); font-weight:800; font-size:1.05rem; margin-bottom:1rem; text-align:center;">
            🎉 Konversi Berhasil!
          </div>
          <div class="preview-box">
            <img src="${data.preview_url}?t=${Date.now()}" alt="Preview Stiker">
          </div>
          <div style="background:var(--primary-dim); border:1px solid var(--primary-border); border-radius:12px; padding:0.85rem; margin-bottom:1rem; text-align:center;">
            <div style="font-size:0.85rem; color:#fff; margin-bottom:0.25rem;">Ukuran File: <strong>${data.size_str}</strong></div>
            <div style="font-size:0.75rem;">${statusBadge}</div>
          </div>
          <div style="display:flex; gap:0.6rem;">
            <a href="${data.download_url}" download="${data.filename}" class="btn-liquid-primary" style="flex:1; text-decoration:none; text-align:center; display:flex; justify-content:center;">
              📥 Download ${isWa ? "Stiker (.webp)" : "GIF (.gif)"}
            </a>
          </div>
        `;
        resultBox.classList.add("active");
        showToast("Stiker berhasil dibuat! 🚀", "success");
      } else {
        showToast(data.error || "Gagal mengonversi stiker", "error");
      }
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<span>⚡</span> Konversi Stiker Sekarang`;
    }
  });
}
