<template>
  <div class="gemini-chat-bubble" :class="{ 'bubble-open': isOpen }">
    <button
      class="fab-button"
      :class="{ 'fab-pulse': hasUnread }"
      @click="togglePanel"
      aria-label="Mo tro ly Gemini AI"
    >
      <div class="fab-icon">
        <i class="fas" :class="isOpen ? 'fa-times' : 'fa-robot'"></i>
      </div>
      <div class="fab-badge" v-if="hasUnread && !isOpen">
        {{ unreadCount }}
      </div>
    </button>

    <transition name="slide-up">
      <div v-if="isOpen" class="chat-panel" :class="{ dark: isDark }">
        <div class="panel-header">
          <div class="header-content">
            <div class="ai-avatar">
              <div class="avatar-glow"></div>
              <i class="fas fa-sparkles"></i>
            </div>
            <div class="header-info">
              <h3>CodeBot</h3>
              <p class="status" :class="status">{{ statusText }}</p>
            </div>
          </div>
          <div class="header-actions">
            <button class="icon-btn" @click="toggleTheme" title="Doi theme">
              <i class="fas" :class="isDark ? 'fa-sun' : 'fa-moon'"></i>
            </button>
            <button class="icon-btn" @click="resetThread" title="Lam moi">
              <i class="fas fa-rotate"></i>
            </button>
            <button class="icon-btn" @click="togglePanel" title="Dong">
              <i class="fas fa-chevron-down"></i>
            </button>
          </div>
        </div>

        <div class="messages-container" ref="messagesContainer">
          <div class="welcome-message" v-if="messages.length === 1">
            <div class="welcome-content">
              <h4>Xin chao! Toi la CodeBot</h4>
              <p>Toi co the giup ban voi:</p>
              <div class="quick-actions">
                <button
                  v-for="action in quickActions"
                  :key="action.text"
                  class="quick-action-btn"
                  @click="sendQuickAction(action.text)"
                >
                  <i :class="action.icon"></i>
                  {{ action.text }}
                </button>
              </div>
            </div>
          </div>

          <div
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="message.role"
          >
            <div class="message-avatar">
              <div class="avatar" :class="message.role">
                <i :class="message.role === 'user' ? 'fas fa-user' : 'fas fa-robot'"></i>
              </div>
            </div>
            <div class="message-content">
              <div class="message-bubble" :class="message.role">
                <div class="message-text">
                  <div
                    v-for="(segment, idx) in formatMessage(message.text || '')"
                    :key="`${message.id}-${idx}`"
                    class="segment-block"
                  >
                    <p
                      v-if="segment.type === 'text'"
                      class="text-content"
                      v-html="renderMarkdown(segment.content)"
                    ></p>

                    <ul v-else-if="segment.type === 'list'" class="bullet-list">
                      <li v-for="(item, i) in segment.items" :key="`li-${idx}-${i}`">
                        {{ item }}
                      </li>
                    </ul>

                    <div v-else class="code-container">
                      <div class="code-header">
                        <span class="code-language">{{ segment.language || 'code' }}</span>
                        <button class="copy-btn" @click="copyCode(segment.content, $event)">
                          <i class="fas fa-copy"></i>
                        </button>
                      </div>
                      <pre class="code-block"><code>{{ segment.content }}</code></pre>
                    </div>
                  </div>
                </div>
                <div class="message-time">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="isTyping" class="typing-indicator">
            <div class="typing-avatar">
              <div class="avatar assistant">
                <i class="fas fa-robot"></i>
              </div>
            </div>
            <div class="typing-content">
              <div class="typing-dots">
                <span></span><span></span><span></span>
              </div>
              <p class="typing-text">CodeBot dang tra loi...</p>
            </div>
          </div>
        </div>

        <div class="input-container">
          <div class="input-wrapper">
            <textarea
              v-model="userInput"
              placeholder="Nhap cau hoi cua ban..."
              :disabled="isTyping"
              @keydown.enter.exact.prevent="sendMessage"
              rows="1"
              ref="textInput"
            ></textarea>
            <div class="input-actions">
              <label class="upload-btn" :class="{ uploading }" title="Tai anh de phan tich">
                <input
                  type="file"
                  accept="image/*"
                  :disabled="uploading || isTyping"
                  @change="handleFileUpload"
                />
                <i class="fas" :class="uploading ? 'fa-spinner fa-spin' : 'fa-image'"></i>
              </label>
              <button
                class="send-btn"
                @click="sendMessage"
                :disabled="isTyping || (!userInput.trim() && !attachments.length)"
                :class="{ sending: isTyping }"
              >
                <i class="fas" :class="isTyping ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
              </button>
            </div>
          </div>
          <div class="input-footer">
            <p class="disclaimer">
              CodeBot co the mac loi. Hay kiem tra thong tin quan trong.
            </p>
            <div v-if="attachments.length" class="attachment-chips">
              <div v-for="file in attachments" :key="file.localId" class="attachment-chip">
                <i class="fas fa-image"></i>
                <span>{{ file.file_name }}</span>
                <button class="remove-chip" @click="removeAttachment(file.localId)">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { sendChatMessage, uploadAttachment } from "../../services/aiService";
import MarkdownIt from "markdown-it";

const SYSTEM_PROMPT = [
  "Ban la CodeBot – tro ly chuyen ve lap trinh va thuat toan.",
  "Chi tra loi cac cau hoi lien quan:",
  "- Thuat toan, cau truc du lieu",
  "- Viet code, sua code, toi uu code",
  "- Giai thich loi chuong trinh",
  "Moi cau tra loi co gang co:",
  "1) Giai thich y tuong / tu duy thuat toan",
  "2) Dua code hoan chinh trong ngon ngu nguoi dung yeu cau (mac dinh Python neu khong chi dinh)",
  "3) Neu do phuc tap (Big-O) neu phu hop",
  "Quy tac bo sung:",
  "- Code dat trong ```python / ```cpp / ```javascript ... de de copy; indent 4 spaces, snake_case, PEP8 cho Python, docstring ngan.",
  "- Neu co anh kem code/sodo: trich noi dung tu anh, hien code trong code block, giai thich ngam gon, khong suy doan ngoai anh.",
  "- Neu thieu thong tin, hoi lai dung trong tam, khong suy doan dai dong.",
  "- Lich su tu choi noi dung khong lien quan lap trinh (yeu duong, boi toan,...).",
].join("\\n");

export default {
  name: "GeminiChatBubble",
  data() {
    return {
      isOpen: false,
      isTyping: false,
      isDark: false,
      userInput: "",
      uploading: false,
      attachments: [],
      hasUnread: false,
      unreadCount: 0,
      md: new MarkdownIt({
        html: false,
        linkify: true,
        breaks: true,
      }),
      messages: [
        {
          id: this.generateId(),
          role: "assistant",
          text: "Xin chao! Toi la CodeBot, tro ly lap trinh cua ban. Toi co the giup gi cho ban?",
          timestamp: new Date(),
        },
      ],
      quickActions: [
        { icon: "fas fa-code", text: "Giai thich doan code nay" },
        { icon: "fas fa-bug", text: "Sua loi trong code" },
        { icon: "fas fa-lightbulb", text: "Goi y giai phap" },
        { icon: "fas fa-book", text: "Giai thich khai niem" },
      ],
    };
  },
  computed: {
    status() {
      return this.isTyping ? "typing" : "online";
    },
    statusText() {
      return this.isTyping ? "Dang tra loi..." : "Truc tuyen";
    },
  },
  methods: {
    generateId() {
      return Date.now().toString(36) + Math.random().toString(36).slice(2);
    },
    togglePanel() {
      this.isOpen = !this.isOpen;
      this.hasUnread = false;
      this.unreadCount = 0;
      this.$nextTick(() => {
        this.scrollToBottom();
        if (this.isOpen) {
          this.$refs.textInput?.focus();
        }
      });
    },
    toggleTheme() {
      this.isDark = !this.isDark;
    },
    resetThread() {
      this.messages = [
        {
          id: this.generateId(),
          role: "assistant",
          text: "Cuoc tro chuyen da duoc lam moi. Ban can ho tro gi?",
          timestamp: new Date(),
        },
      ];
      this.userInput = "";
      this.scrollToBottom();
    },
    formatMessage(text) {
      const safeText = String(text ?? "");
      const segments = [];
      const parts = safeText.split(/(```[\s\S]*?```)/g);

      parts.forEach((part) => {
        const trimmed = part.trim();
        if (!trimmed) return;
        const isCodeBlock = trimmed.startsWith("```") && trimmed.endsWith("```");
        if (isCodeBlock) {
          const langMatch = trimmed.match(/^```(\w+)?/);
          const language = langMatch && langMatch[1] ? langMatch[1] : "python";
          const codeContent = trimmed
            .replace(/^```(\w+)?\n?/, "")
            .replace(/```$/, "")
            .trim();
          segments.push({ type: "code", content: codeContent, language });
        } else {
          const listLines = trimmed
            .split("\n")
            .map((line) => line.trim())
            .filter(Boolean);
          const bulletItems = listLines.filter((line) => /^[-*•]/.test(line));
          if (bulletItems.length && bulletItems.length === listLines.length) {
            segments.push({
              type: "list",
              items: bulletItems.map((line) => line.replace(/^[-*•]\s*/, "")),
            });
          } else {
            segments.push({ type: "text", content: trimmed });
          }
        }
      });

      return segments.length ? segments : [{ type: "text", content: safeText }];
    },
    renderMarkdown(raw) {
      return this.md.render(String(raw || ""));
    },
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    async sendMessage() {
      const content = this.userInput.trim();
      if ((!content && !this.attachments.length) || this.isTyping) return;

      const userMessage = {
        id: this.generateId(),
        role: "user",
        text: content || "(Da gui anh de phan tich)",
        timestamp: new Date(),
      };
      this.messages.push(userMessage);
      this.userInput = "";
      this.isTyping = true;
      this.scrollToBottom();

      try {
        const attachmentNote = this.attachments
          .map((file) => `Attachment: ${file.file_name} - ${file.url}`)
          .join("\n");
        const prompt = `${SYSTEM_PROMPT}\n\nNguoi dung: ${content || "Phan tich anh"}${
          attachmentNote ? `\n${attachmentNote}` : ""
        }\n\nTro ly:`;
        const response = await sendChatMessage({
          prompt,
          attachments: this.attachments,
        });
        const reply =
          response?.reply?.trim() ||
          "Xin loi, toi khong the tra loi ngay luc nay. Vui long thu lai.";

        this.messages.push({
          id: this.generateId(),
          role: "assistant",
          text: reply,
          timestamp: new Date(),
        });
      } catch (error) {
        console.error("Gemini error:", error);
        this.messages.push({
          id: this.generateId(),
          role: "assistant",
          text: "Ket noi that bai. Vui long kiem tra mang va thu lai.",
          timestamp: new Date(),
        });
      } finally {
        this.isTyping = false;
        this.attachments = [];
        this.scrollToBottom();
      }
    },
    sendQuickAction(text) {
      this.userInput = text;
      this.sendMessage();
    },
    async handleFileUpload(event) {
      const file = event.target.files && event.target.files[0];
      event.target.value = "";
      if (!file || this.uploading) return;
      this.uploading = true;
      try {
        const uploaded = await uploadAttachment(file);
        const descriptor = {
          localId: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
          file_name: uploaded?.file_name || file.name,
          url: uploaded?.url || "",
          mime: uploaded?.mime || file.type,
        };
        this.attachments.push(descriptor);
      } catch (error) {
        console.error("Upload failed:", error);
        alert("Tai anh that bai. Thu lai nhe.");
      } finally {
        this.uploading = false;
      }
    },
    removeAttachment(id) {
      this.attachments = this.attachments.filter((file) => file.localId !== id);
    },
    async copyCode(code, event) {
      try {
        await navigator.clipboard.writeText(code);
        const btn = event?.target?.closest(".copy-btn");
        const icon = btn?.querySelector("i");
        const original = icon?.className;
        if (icon) {
          icon.className = "fas fa-check";
          setTimeout(() => {
            icon.className = original || "fas fa-copy";
          }, 2000);
        }
      } catch (err) {
        console.error("Copy failed:", err);
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
    autoResize() {
      const textarea = this.$refs.textInput;
      if (textarea) {
        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
      }
    },
  },
  watch: {
    userInput() {
      this.autoResize();
    },
    isOpen(newVal) {
      if (newVal) {
        this.hasUnread = false;
        this.unreadCount = 0;
      }
    },
  },
  mounted() {
    setTimeout(() => {
      if (!this.isOpen) {
        this.hasUnread = true;
        this.unreadCount = 1;
      }
    }, 10000);
  },
};
</script>

<style scoped>
.gemini-chat-bubble {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 10000;
}

.fab-button {
  position: relative;
  width: 60px;
  height: 60px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.fab-button:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6);
}

.fab-button.fab-pulse {
  animation: pulse 2s infinite;
}

.fab-icon {
  font-size: 1.4rem;
}

.fab-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 2px 4px;
  border-radius: 12px;
  background: #ff7eb6;
  color: white;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-panel {
  position: absolute;
  bottom: 78px;
  right: 0;
  width: min(420px, 92vw);
  max-height: 640px;
  background: #f9fafb;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 16px 48px rgba(15, 23, 42, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  background: #ffffff;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  position: relative;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: linear-gradient(135deg, #3b82f6, #22d3ee);
  display: grid;
  place-items: center;
  color: white;
  font-size: 1.2rem;
  overflow: hidden;
}

.avatar-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.35), transparent 60%);
}

.header-info h3 {
  margin: 0;
  color: #0f172a;
  font-size: 1.05rem;
}

.status {
  margin: 2px 0 0;
  font-size: 0.86rem;
  color: #475569;
}

.status.online {
  color: #16a34a;
}

.status.typing {
  color: #d97706;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: rgba(15, 23, 42, 0.04);
  color: #0f172a;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.messages-container {
  padding: 14px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 420px;
  background: #f9fafb;
}

.chat-panel.dark {
  background: linear-gradient(180deg, #0b1020 0%, #0f172a 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
}

.chat-panel.dark .panel-header {
  background: rgba(15, 23, 42, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.chat-panel.dark .header-info h3 {
  color: #e2e8f0;
}

.chat-panel.dark .status {
  color: #cbd5e1;
}

.chat-panel.dark .icon-btn {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.06);
  color: #e2e8f0;
}

.chat-panel.dark .messages-container {
  background: transparent;
}

.chat-panel.dark .welcome-message {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
}

.chat-panel.dark .quick-action-btn {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #e2e8f0;
}

.chat-panel.dark .message-bubble {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
}

.chat-panel.dark .message-bubble.user {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
}

.chat-panel.dark .text-content,
.chat-panel.dark .bullet-list {
  color: #e2e8f0;
}

.chat-panel.dark .code-container {
  background: #0f172a;
  border-color: rgba(148, 163, 184, 0.2);
}

.chat-panel.dark .code-header {
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
}

.chat-panel.dark .code-block {
  color: #cbd5e1;
}

.chat-panel.dark .message-time {
  color: #cbd5e1;
}

.chat-panel.dark .typing-dots span {
  background: #34d399;
}

.chat-panel.dark .input-container {
  background: rgba(0, 0, 0, 0.15);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.chat-panel.dark .input-wrapper textarea {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
}

.chat-panel.dark .upload-btn {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
}

.chat-panel.dark .send-btn {
  background: linear-gradient(135deg, #60a5fa, #34d399);
}

.chat-panel.dark .input-footer {
  color: #cbd5e1;
}

.chat-panel.dark .attachment-chip {
  background: rgba(96, 165, 250, 0.18);
  color: #e2e8f0;
  border-color: rgba(96, 165, 250, 0.35);
}

.welcome-message {
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 12px;
  color: #0f172a;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.quick-action-btn {
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: rgba(255, 255, 255, 0.9);
  color: #0f172a;
  border-radius: 12px;
  padding: 6px 10px;
  cursor: pointer;
}

.message {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: flex-start;
}

.message-avatar .avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: white;
}

.message-avatar .avatar.user {
  background: #3b82f6;
}

.message-avatar .avatar.assistant {
  background: #10b981;
}

.message-content {
  display: flex;
}

.message-bubble {
  padding: 10px 12px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  color: #0f172a;
  max-width: 100%;
  width: fit-content;
}

.message-bubble.user {
  background: #e0f2fe;
  border-color: rgba(37, 99, 235, 0.3);
}

.message-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.text-content {
  margin: 0;
  line-height: 1.5;
  color: #0f172a;
}

.text-content :deep(p) {
  margin: 0 0 6px;
}

.text-content :deep(ul) {
  margin: 0 0 6px 1.2rem;
  padding: 0;
  list-style: disc;
}

.text-content :deep(li) {
  margin: 2px 0;
}

.bullet-list {
  margin: 0;
  padding-left: 1.2rem;
  color: #0f172a;
  line-height: 1.5;
}

.bullet-list li {
  margin-bottom: 4px;
}

.code-container {
  background: #f8fafc;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 10px;
  overflow: hidden;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: #e2e8f0;
  color: #0f172a;
}

.code-language {
  font-size: 0.85rem;
}

.copy-btn {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.code-block {
  margin: 0;
  padding: 10px;
  font-family: "Fira Code", "JetBrains Mono", monospace;
  font-size: 0.9rem;
  color: #0f172a;
  overflow-x: auto;
}

.message-time {
  margin-top: 4px;
  font-size: 0.75rem;
  color: #475569;
}

.typing-indicator {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: center;
}

.typing-dots {
  display: inline-flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  animation: blink 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.input-container {
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  padding: 12px;
  background: #ffffff;
}

.input-wrapper {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
}

.input-wrapper textarea {
  width: 100%;
  min-height: 42px;
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  background: #ffffff;
  color: #0f172a;
  padding: 10px;
  resize: none;
}

.input-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.upload-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: 1px dashed rgba(15, 23, 42, 0.2);
  background: #ffffff;
  color: #0f172a;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.upload-btn input {
  display: none;
}

.upload-btn.uploading {
  opacity: 0.7;
  cursor: not-allowed;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #3b82f6, #22d3ee);
  color: white;
  cursor: pointer;
}

.input-footer {
  margin-top: 6px;
  color: #475569;
  font-size: 0.82rem;
}

.attachment-chips {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 10px;
  background: #e0f2fe;
  color: #0f172a;
  border: 1px solid rgba(37, 99, 235, 0.2);
  font-size: 0.9rem;
}

.remove-chip {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.08);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.4;
  }
  40% {
    opacity: 1;
  }
}
</style>

