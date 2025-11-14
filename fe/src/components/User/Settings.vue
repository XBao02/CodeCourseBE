<template>
  <section class="settings-page">
    <header class="hero">
      <div>
        <p class="eyebrow">Tu? ch?nh tài kho?n</p>
        <h1>Cài d?t tr?i nghi?m h?c t?p</h1>
        <p class="subline">Ði?u ch?nh thông báo, ch? d? và tu? ch?n chatbot.</p>
      </div>
    </header>

    <div class="grid">
      <article class="panel">
        <h2>Thông báo</h2>
        <div class="setting" v-for="item in notificationOptions" :key="item.label">
          <div>
            <p class="label">{{ item.label }}</p>
            <p class="desc">{{ item.desc }}</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="item.enabled" />
            <span></span>
          </label>
        </div>
      </article>

      <article class="panel">
        <h2>Ch? d? & giao di?n</h2>
        <div class="theme-picker">
          <button
            v-for="theme in themes"
            :key="theme.id"
            :class="['theme-chip', { active: activeTheme === theme.id }]"
            @click="activeTheme = theme.id"
          >
            <span :style="{ background: theme.preview }"></span>
            {{ theme.label }}
          </button>
        </div>
        <label>Font ch?
          <select v-model="ui.font">
            <option value="Inter">Inter</option>
            <option value="Space Grotesk">Space Grotesk</option>
            <option value="Public Sans">Public Sans</option>
          </select>
        </label>
      </article>

      <article class="panel">
        <h2>Chatbot</h2>
        <div class="setting">
          <div>
            <p class="label">T? d?ng d?c tr? l?i</p>
            <p class="desc">Ch? b?t khi câu h?i d?n t? micro theo yêu c?u tru?c dó.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="chat.autoSpeak" />
            <span></span>
          </label>
        </div>
        <label>Gi?ng ua thích
          <select v-model="chat.voice">
            <option value="vi-VN Female">N? Vi?t Nam</option>
            <option value="vi-VN Male">Nam Vi?t Nam</option>
            <option value="en-US Female">English Female</option>
          </select>
        </label>
        <div class="range">
          <span>T?c d?</span>
          <input type="range" min="0.6" max="1.2" step="0.05" v-model.number="chat.rate" />
          <strong>{{ chat.rate.toFixed(2) }}x</strong>
        </div>
      </article>

      <article class="panel">
        <h2>B?o m?t</h2>
        <div class="setting">
          <div>
            <p class="label">Xác th?c hai l?p</p>
            <p class="desc">B?o v? tài kho?n khi dang nh?p ? thi?t b? l?.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="security.mfa" />
            <span></span>
          </label>
        </div>
        <button type="button" class="ghost" @click="resetPassword">Ð?i m?t kh?u</button>
      </article>
    </div>
  </section>
</template>

<script>
export default {
  name: "UserSettings",
  data() {
    return {
      notificationOptions: [
        {
          label: "C?p nh?t khóa h?c",
          desc: "Thông báo khi có bài h?c ho?c quiz m?i",
          enabled: true,
        },
        {
          label: "Nh?c l?ch h?c",
          desc: "T? d?ng g?i remind qua email h?ng ngày",
          enabled: false,
        },
        {
          label: "Thông báo AI",
          desc: "Báo khi chatbot ph?n h?i file dính kèm",
          enabled: true,
        },
      ],
      themes: [
        { id: "midnight", label: "Midnight", preview: "linear-gradient(120deg,#0f172a,#1e293b)" },
        { id: "sunset", label: "Sunset", preview: "linear-gradient(120deg,#fb923c,#f472b6)" },
        { id: "forest", label: "Forest", preview: "linear-gradient(120deg,#34d399,#0f766e)" },
      ],
      activeTheme: "midnight",
      ui: {
        font: "Inter",
      },
      chat: {
        autoSpeak: true,
        voice: "vi-VN Female",
        rate: 0.82,
      },
      security: {
        mfa: true,
      },
    };
  },
  methods: {
    resetPassword() {
      alert("Tính nang d?i m?t kh?u dang du?c k?t n?i v?i backend.");
    },
  },
};
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  padding: 3rem clamp(1.5rem, 5vw, 4rem);
  background: radial-gradient(circle at 15% 20%, #1c2343, #05060f 70%);
  color: #e2e8f0;
}

.hero {
  margin-bottom: 2rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.panel {
  border-radius: 28px;
  padding: 1.8rem;
  background: rgba(8, 11, 23, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.setting {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
}

.setting:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  margin: 0;
}

.desc {
  margin: 0;
  color: rgba(226, 232, 240, 0.65);
  font-size: 0.9rem;
}

.switch {
  position: relative;
  width: 46px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch span {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.4);
  transition: 0.2s;
}

.switch span::after {
  content: "";
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #0f172a;
  top: 3px;
  left: 4px;
  transition: 0.2s;
}

.switch input:checked + span {
  background: linear-gradient(120deg, #60a5fa, #34d399);
}

.switch input:checked + span::after {
  transform: translateX(18px);
  background: #fff;
}

.theme-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  margin-bottom: 1.2rem;
}

.theme-chip {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: transparent;
  padding: 0.45rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: inherit;
  cursor: pointer;
}

.theme-chip span {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: inline-block;
}

.theme-chip.active {
  border-color: #60a5fa;
  box-shadow: 0 0 12px rgba(96, 165, 250, 0.4);
}

select,
button,
input[type="range"] {
  width: 100%;
  margin-top: 0.5rem;
}

select {
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(255, 255, 255, 0.04);
  color: inherit;
  padding: 0.6rem 0.8rem;
}

.range {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.6rem;
  align-items: center;
  margin-top: 1rem;
}

input[type="range"] {
  accent-color: #60a5fa;
}

.ghost {
  width: 100%;
  margin-top: 1rem;
  border-radius: 16px;
  border: 1px solid rgba(248, 250, 252, 0.35);
  background: transparent;
  color: inherit;
  padding: 0.8rem 1rem;
  cursor: pointer;
}
</style>
