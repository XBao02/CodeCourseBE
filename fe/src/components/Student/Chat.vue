<template>
  <div class="chat-shell">
    <aside class="sidebar">
      <div class="sidebar__header">
        <div>
          <p class="eyebrow">Đang học</p>
          <h4 class="title">Trò chuyện</h4>
        </div>
        <button class="ghost-btn" @click="loadThreads" :disabled="loadingThreads">
          {{ loadingThreads ? "..." : "↻" }}
        </button>
      </div>

      <div class="search-box">
        <i class="bx bx-search"></i>
        <input v-model="query" placeholder="Tìm khóa hoặc giảng viên..." />
      </div>

      <div class="thread-list">
        <button
          v-for="thread in filteredThreads"
          :key="threadKey(thread)"
          class="thread"
          :class="selectedThreadKey === threadKey(thread) ? 'is-active' : ''"
          @click="selectThread(thread)"
        >
          <div class="thread__avatar">{{ (thread.instructorName || "GV")[0] }}</div>
          <div class="thread__body">
            <div class="thread__row">
              <span class="thread__name">{{ thread.instructorName || "Giảng viên" }}</span>
              <span class="thread__time">{{ thread.lastAt ? formatTime(thread.lastAt) : "" }}</span>
            </div>
            <div class="thread__course">{{ thread.courseTitle }}</div>
            <div class="thread__preview">
              {{ thread.lastMessage ? truncate(thread.lastMessage) : "Chưa có tin nhắn" }}
            </div>
          </div>
          <span v-if="thread.unread" class="badge">{{ thread.unread }}</span>
        </button>
      </div>
    </aside>

    <section class="conversation" v-if="selectedThreadKey">
      <header class="conversation__header">
        <div class="head">
          <div class="head__avatar">{{ (selectedThread?.instructorName || "GV")[0] }}</div>
          <div>
            <div class="head__name">{{ selectedThread?.instructorName }}</div>
            <div class="head__meta">{{ selectedThread?.courseTitle }}</div>
          </div>
        </div>
        <button class="ghost-btn" @click="refreshMessages" :disabled="loadingMessages">
          {{ loadingMessages ? "..." : "Làm mới" }}
        </button>
      </header>

      <div class="messages" ref="messagesContainer">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="msg-row"
          :class="msg.fromUserId === currentUserId ? 'mine' : 'theirs'"
        >
          <div class="bubble">
            <div v-if="isImage(msg)" class="attach-image">
              <img :src="resolveUrl(msg.attachmentUrl || msg.content)" alt="attachment" />
            </div>
            <div v-else-if="isFile(msg)" class="attach-file">
              <a :href="resolveUrl(msg.attachmentUrl || msg.content)" target="_blank" rel="noopener">
                📎 {{ msg.attachmentName || msg.content || "Tệp đính kèm" }}
              </a>
            </div>
            <div v-if="msg.content && !isImage(msg) && !isFile(msg)" class="text">
              {{ msg.content }}
            </div>
            <div class="time">{{ formatTime(msg.createdAt) }}</div>
          </div>
        </div>
      </div>

      <footer class="composer">
        <div class="composer__left">
          <label class="attach-btn">
            📎
            <input type="file" class="hidden-input" @change="handleFile" />
          </label>
          <div v-if="attachmentName" class="attach-chip">
            {{ attachmentName }}
            <button @click="clearAttachment">×</button>
          </div>
        </div>
        <textarea
          v-model="draft"
          @keyup.enter.exact.prevent="send"
          class="composer__input"
          rows="1"
          placeholder="Nhập tin nhắn..."
          :disabled="sending || !selectedThreadKey"
        ></textarea>
        <button class="send-btn" @click="send" :disabled="sending || (!draft.trim() && !attachmentFile)">
          {{ sending ? "Đang gửi..." : "Gửi" }}
        </button>
      </footer>
    </section>

    <section v-else class="empty">
      <p>Chọn khóa học để bắt đầu trò chuyện.</p>
    </section>
  </div>
</template>

<script>
import { onMounted, onBeforeUnmount, ref, computed } from "vue";
import { getStoredSession } from "../../services/authService";
import chatService from "../../services/chatService";

export default {
  name: "StudentChat",
  setup() {
    const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";
    const apiOrigin = (() => {
      try {
        return new URL(apiBase).origin;
      } catch (e) {
        return "";
      }
    })();

    const threads = ref([]);
    const query = ref("");
    const selectedThread = ref(null);
    const selectedThreadKey = ref(null);
    const messages = ref([]);
    const draft = ref("");
    const sending = ref(false);
    const loadingThreads = ref(false);
    const loadingMessages = ref(false);
    const pollTimer = ref(null);
    const currentUserId = ref(null);
    const messagesContainer = ref(null);
    const lastTimestamp = ref(null);
    const attachmentFile = ref(null);
    const attachmentName = ref("");

    const threadKey = (t) => `${t.courseId}-${t.instructorId}`;

    const filteredThreads = computed(() => {
      const q = query.value.trim().toLowerCase();
      if (!q) return threads.value;
      return threads.value.filter(
        (t) =>
          (t.courseTitle || "").toLowerCase().includes(q) ||
          (t.instructorName || "").toLowerCase().includes(q)
      );
    });

    const loadThreads = async () => {
      loadingThreads.value = true;
      try {
        const data = await chatService.fetchThreads();
        threads.value = data;
        if (!selectedThreadKey.value && data.length) {
          selectThread(data[0]);
        }
      } catch (err) {
        console.error("Load threads failed", err);
      } finally {
        loadingThreads.value = false;
      }
    };

    const refreshMessages = async () => {
      if (!selectedThread.value) return;
      loadingMessages.value = true;
      try {
        const msgs = await chatService.fetchMessages({
          courseId: selectedThread.value.courseId,
          since: lastTimestamp.value,
        });
        if (lastTimestamp.value && msgs.length) {
          messages.value.push(...msgs);
        } else if (!lastTimestamp.value) {
          messages.value = msgs;
        }
        if (msgs.length) {
          lastTimestamp.value = msgs[msgs.length - 1].createdAt;
          scrollBottom();
        }
      } catch (err) {
        console.error("Load messages failed", err);
      } finally {
        loadingMessages.value = false;
      }
    };

    const selectThread = async (thread) => {
      selectedThread.value = thread;
      selectedThreadKey.value = threadKey(thread);
      messages.value = [];
      lastTimestamp.value = null;
      await refreshMessages();
      startPolling();
    };

    const send = async () => {
      if ((!draft.value.trim() && !attachmentFile.value) || !selectedThread.value || sending.value)
        return;
      sending.value = true;
      try {
        let uploaded = null;
        if (attachmentFile.value) {
          uploaded = await chatService.uploadAttachment(attachmentFile.value);
        }
        const sent = await chatService.sendMessage({
          courseId: selectedThread.value.courseId,
          content: uploaded?.message_type === "image" ? "" : draft.value.trim(),
          attachment_url: uploaded?.content,
          attachment_type: uploaded?.message_type,
          attachment_name: uploaded?.original_filename,
          message_type: uploaded?.message_type || "text",
        });
        messages.value.push(sent);
        draft.value = "";
        lastTimestamp.value = sent.createdAt;
        attachmentFile.value = null;
        attachmentName.value = "";
        scrollBottom();
      } catch (err) {
        console.error("Send message failed", err);
      } finally {
        sending.value = false;
      }
    };

    const handleFile = (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const allowed = ["jpg", "jpeg", "png", "webp", "pdf", "docx", "zip", "txt"];
      const ext = file.name.split(".").pop().toLowerCase();
      if (!allowed.includes(ext)) {
        alert("Định dạng không hỗ trợ");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        alert("Kích thước tối đa 10MB");
        return;
      }
      attachmentFile.value = file;
      attachmentName.value = file.name;
    };

    const clearAttachment = () => {
      attachmentFile.value = null;
      attachmentName.value = "";
    };

    const startPolling = () => {
      if (pollTimer.value) clearInterval(pollTimer.value);
      pollTimer.value = setInterval(refreshMessages, 5000);
    };

    const stopPolling = () => {
      if (pollTimer.value) clearInterval(pollTimer.value);
    };

    const truncate = (text = "", len = 40) =>
      text.length > len ? `${text.slice(0, len)}...` : text;

    const formatTime = (iso) => {
      if (!iso) return "";
      const d = new Date(iso);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    };

    const scrollBottom = () => {
      requestAnimationFrame(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    const isImage = (msg) => {
      const mt = (msg.messageType || msg.attachmentType || "").toLowerCase();
      if (mt === "image") return !!(msg.attachmentUrl || msg.content);
      const src = (msg.attachmentUrl || msg.content || "").toLowerCase();
      return [".jpg", ".jpeg", ".png", ".webp"].some((ext) => src.endsWith(ext));
    };

    const isFile = (msg) => {
      const mt = (msg.messageType || msg.attachmentType || "").toLowerCase();
      if (mt === "file") return !!(msg.attachmentUrl || msg.content);
      const src = (msg.attachmentUrl || msg.content || "").toLowerCase();
      return [".pdf", ".docx", ".zip", ".txt"].some((ext) => src.endsWith(ext));
    };

    const resolveUrl = (path) => {
      if (!path) return "";
      if (path.startsWith("http://") || path.startsWith("https://")) return path;
      if (apiOrigin && path.startsWith("/")) return apiOrigin + path;
      return path;
    };

    onMounted(() => {
      const session = getStoredSession();
      currentUserId.value = session?.user?.id || null;
      loadThreads();
    });

    onBeforeUnmount(() => {
      stopPolling();
    });

    return {
      threads,
      query,
      filteredThreads,
      selectedThread,
      selectedThreadKey,
      messages,
      draft,
      sending,
      loadingThreads,
      loadingMessages,
      attachmentName,
      messagesContainer,
      loadThreads,
      refreshMessages,
      selectThread,
      send,
      handleFile,
      clearAttachment,
      truncate,
      formatTime,
      isImage,
      isFile,
      resolveUrl,
      threadKey,
      currentUserId,
    };
  },
};
</script>

<style scoped>
.chat-shell {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
  height: calc(100vh - 120px);
  padding: 16px;
  background: #f5f7fb;
}
.sidebar {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(20, 30, 80, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar__header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
  color: #6b7280;
  margin: 0;
}
.title {
  margin: 2px 0 0;
  font-size: 18px;
  font-weight: 700;
}
.ghost-btn {
  border: 1px solid #e5e7eb;
  background: #fff;
  border-radius: 10px;
  padding: 8px 10px;
  cursor: pointer;
  color: #111827;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px 12px;
}
.search-box input {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 12px;
}
.thread-list {
  overflow-y: auto;
  flex: 1;
}
.thread {
  width: 100%;
  border: none;
  background: transparent;
  padding: 12px 16px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
  cursor: pointer;
}
.thread.is-active {
  background: #eef2ff;
}
.thread__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2563eb;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
}
.thread__body {
  text-align: left;
}
.thread__row {
  display: flex;
  justify-content: space-between;
  font-weight: 700;
  color: #111827;
}
.thread__course {
  font-size: 13px;
  color: #6b7280;
}
.thread__preview {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}
.thread__time {
  font-size: 12px;
  color: #9ca3af;
}
.badge {
  background: #ef4444;
  color: #fff;
  padding: 3px 8px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 12px;
}
.conversation,
.empty {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(20, 30, 80, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.conversation__header {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f1f1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.head__avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #16a34a;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
}
.head__name {
  font-weight: 700;
  font-size: 16px;
}
.head__meta {
  font-size: 12px;
  color: #6b7280;
}
.messages {
  flex: 1;
  padding: 18px;
  overflow-y: auto;
  background: linear-gradient(180deg, #f7f9fc, #eef2f7);
}
.msg-row {
  display: flex;
  margin-bottom: 12px;
}
.msg-row.mine {
  justify-content: flex-end;
}
.msg-row.theirs {
  justify-content: flex-start;
}
.bubble {
  max-width: 70%;
  padding: 12px 14px;
  border-radius: 16px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
  background: #e6f4ff;
  color: #0b172a;
}
.msg-row.mine .bubble {
  background: #0f93ff;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.msg-row.theirs .bubble {
  background: #e8f5e9;
  color: #0b172a;
  border-bottom-left-radius: 4px;
}
.text {
  white-space: pre-wrap;
  word-break: break-word;
}
.time {
  margin-top: 6px;
  font-size: 11px;
  opacity: 0.75;
}
.composer {
  padding: 14px 16px;
  border-top: 1px solid #f1f1f1;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: end;
}
.composer__input {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 10px 12px;
  resize: none;
  font-family: inherit;
}
.send-btn {
  background: #0f93ff;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}
.composer__left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.attach-btn {
  border: 1px solid #e5e7eb;
  background: #fff;
  border-radius: 10px;
  padding: 8px 10px;
  cursor: pointer;
  font-size: 16px;
}
.hidden-input {
  display: none;
}
.attach-chip {
  background: #eef2ff;
  color: #1f2937;
  padding: 6px 10px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.attach-chip button {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
}
.attach-image img {
  max-width: 240px;
  border-radius: 10px;
  display: block;
}
.attach-file a {
  color: #1d4ed8;
  text-decoration: underline;
}
.empty {
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-weight: 600;
}
</style>
