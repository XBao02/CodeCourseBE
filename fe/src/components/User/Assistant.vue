<template>
  <div class="assistant-page">
    <div class="grid-overlay"></div>
    <div class="glow glow-a"></div>
    <div class="glow glow-b"></div>

    <header class="assistant-header">
      <div class="brand">
        <span>Code</span>Course AI
      </div>

      <div class="search">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search courses or skills..."
          @keyup.enter="searchCourses"
        />
        <button type="button" @click="searchCourses">
          <i class="fas fa-search"></i>
        </button>
      </div>

      <div class="header-actions">
        <button type="button" @click="navigateToProfile">
          <i class="fas fa-user"></i>
          Profile
        </button>
        <button type="button" @click="navigateToSettings">
          <i class="fas fa-sliders-h"></i>
          Settings
        </button>
      </div>
    </header>

    <section class="workspace">
      <div class="panel chat-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Trợ lý học tập</p>
            <h2>Hỏi CodeCourse AI</h2>
            <p class="subline">
              Mô tả mục tiêu của bạn hoặc chọn nhanh một gợi ý bên cạnh.
            </p>
          </div>
          <div class="suggested-stack">
            <button
              v-for="question in suggestedQuestions"
              :key="question"
              type="button"
              @click="askQuestion(question)"
            >
              {{ question }}
            </button>
          </div>
        </div>

        <div class="message-stream" ref="messagesContainer">
          <div
            v-for="message in messages"
            :key="message.id"
            :class="['bubble', message.type === 'user' ? 'bubble-user' : 'bubble-bot']"
          >
            <button
              v-if="message.type === 'bot' && canSpeak"
              class="speak-btn"
              type="button"
              @click="speakMessage(message.text, message.id)"
              :disabled="speakingId === message.id"
              title="Nghe lại câu trả lời"
            >
              <i class="fas" :class="speakingId === message.id ? 'fa-volume-up' : 'fa-volume-high'"></i>
            </button>
            <div
              v-for="(chunk, idx) in formatReply(message.text)"
              :key="idx"
              class="reply-block"
            >
              <template v-if="chunk.type === 'heading'">
                <p class="reply-heading">{{ chunk.text }}</p>
              </template>
              <template v-else-if="chunk.type === 'list'">
                <ul class="reply-list">
                  <li v-for="(item, j) in chunk.items" :key="j">
                    <strong v-if="item.title">{{ item.title }}:</strong>
                    <span>{{ item.body }}</span>
                  </li>
                </ul>
              </template>
              <template v-else>
                <p>{{ chunk.text }}</p>
              </template>
            </div>

            <div
              v-if="message.attachments && message.attachments.length"
              class="message-attachments"
            >
              <a
                v-for="file in message.attachments"
                :key="file.localId || file.url"
                :href="file.url"
                target="_blank"
                rel="noopener"
              >
                <i class="fas fa-paperclip"></i>
                {{ file.file_name || 'Attachment' }}
              </a>
            </div>

          </div>

          <div v-if="isTyping" class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>

        <div v-if="pendingAttachments.length" class="attachment-preview">
          <div
            v-for="file in pendingAttachments"
            :key="file.localId"
            class="attachment-chip"
          >
            <i class="fas fa-paperclip"></i>
            <span>{{ file.file_name }}</span>
            <button type="button" @click="removeAttachment(file.localId)">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <form class="composer" @submit.prevent="sendMessage">
          <label class="upload-btn" :class="{ uploading }">
            <input
              type="file"
              accept="image/*,.pdf,.txt,.md"
              @change="handleFileUpload"
              :disabled="uploading"
            />
            <i class="fas" :class="uploading ? 'fa-spinner fa-spin' : 'fa-paperclip'"></i>
          </label>

          <button
            type="button"
            class="mic-btn"
            :class="{ recording: isRecording }"
            @click="toggleRecording"
            :disabled="recordingUnsupported"
            title="Thu giọng nói"
          >
            <i class="fas" :class="isRecording ? 'fa-circle' : 'fa-microphone'"></i>
          </button>

          <input
            v-model="userInput"
            type="text"
            placeholder="Nhập câu hỏi hoặc nhiệm vụ của bạn..."
            :disabled="isTyping"
          />

          <button
            type="submit"
            :disabled="isTyping || (!userInput.trim() && !pendingAttachments.length)"
            title="Gửi"
          >
            <i class="fas fa-paper-plane"></i>
          </button>
        </form>
      </div>

      <div class="panel insight-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Khóa học đề xuất</p>
            <h2>Khám phá lộ trình phù hợp</h2>
          </div>
          <select v-model="selectedLevel" @change="filterCourses">
            <option value="">Tất cả cấp độ</option>
            <option value="beginner">Cơ bản</option>
            <option value="intermediate">Trung cấp</option>
            <option value="advanced">Nâng cao</option>
          </select>
        </div>

        <div class="course-grid">
          <article
            v-for="course in filteredCourses"
            :key="course.id"
            :class="['course-card', { recommended: recommendedCourseIds.includes(course.id) }]"
            @click="selectCourse(course)"
          >
            <div class="course-icon" :style="{ background: course.gradient }">
              <i :class="course.icon"></i>
            </div>
            <div class="course-copy">
              <h3>{{ course.title }}</h3>
              <p>{{ course.description }}</p>
            </div>
            <footer>
              <span class="level" :class="`level-${course.level}`">
                {{ getLevelText(course.level) }}
              </span>
            </footer>
          </article>

          <div v-if="!filteredCourses.length" class="empty-state">
            <i class="fas fa-book-open"></i>
            <p>Không tìm thấy khóa học phù hợp</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import {
  fetchAiCourses,
  sendChatMessage,
  uploadAttachment,
} from "../../services/aiService";

const HISTORY_KEY = "assistant_chat_history";

export default {
  name: "AssistantPage",
  data() {
    return {
      messages: [],
      userInput: "",
      isTyping: false,
      searchQuery: "",
      selectedLevel: "",
      loading: false,
      uploading: false,
      courses: [],
      recommendedCourseIds: [],
      pendingAttachments: [],
      suggestedQuestions: [
        "Tôi muốn học lập trình web từ con số 0",
        "Đã biết Python, muốn học nâng cao",
        "Gợi ý khóa học về Data Science",
        "Khóa học cho người mới bắt đầu",
        "Cần lộ trình ôn phỏng vấn Frontend",
      ],
      voices: [],
      voiceListener: null,
      speakingId: null,
      recognition: null,
      isRecording: false,
      recordingUnsupported: false,
      autoSpeak: true,
      lastMessageFromVoice: false,
      preferredVoiceName: "vi-VN Female",
      voicePreferences: [
        /vi.*female/i,
        /nu/i,
        /vietnam.*female/i,
        /vi/i,
        /female/i,
        /en/i,
      ],
    };
  },
  computed: {
    filteredCourses() {
      let filtered = this.courses;
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        filtered = filtered.filter(
          (course) =>
            course.title.toLowerCase().includes(q) ||
            course.description.toLowerCase().includes(q) ||
            (course.tags || []).some((tag) => tag.toLowerCase().includes(q))
        );
      }
      if (this.selectedLevel) {
        filtered = filtered.filter((course) => course.level === this.selectedLevel);
      }
      return filtered;
    },
    canSpeak() {
      return typeof window !== "undefined" && "speechSynthesis" in window;
    },
    canRecord() {
      return typeof window !== "undefined" &&
        ("webkitSpeechRecognition" in window || "SpeechRecognition" in window);
    },
  },
  async mounted() {
    this.loadHistory();
    await this.loadCourses();
    this.initVoices();
    this.initRecorder();
    this.scrollToBottom();
  },
  beforeUnmount() {
    if (this.canSpeak) {
      window.speechSynthesis.cancel();
      if (this.voiceListener) {
        window.speechSynthesis.removeEventListener("voiceschanged", this.voiceListener);
        this.voiceListener = null;
      }
    }
    if (this.recognition) {
      this.recognition.stop();
      this.recognition = null;
    }
  },
  methods: {
    loadHistory() {
      if (typeof window === "undefined") return;
      try {
        const raw = window.localStorage.getItem(HISTORY_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) {
            this.messages = parsed;
          }
        }
      } catch (error) {
        console.warn("Unable to load chat history:", error);
      }
    },
    persistHistory() {
      if (typeof window === "undefined") return;
      try {
        const payload = JSON.stringify(this.messages.slice(-50));
        window.localStorage.setItem(HISTORY_KEY, payload);
      } catch (error) {
        console.warn("Unable to persist chat history:", error);
      }
    },
    async loadCourses() {
      this.loading = true;
      try {
        const remote = await fetchAiCourses();
        this.courses = Array.isArray(remote) && remote.length
          ? remote
          : this.buildMockCourses();
      } catch (error) {
        console.error("Error loading courses:", error);
        this.courses = this.buildMockCourses();
        this.showError("Không thể tải danh sách khóa học");
      } finally {
        this.loading = false;
      }
    },
    buildMockCourses() {
      return [
        {
          id: 1,
          title: "HTML & CSS Cơ Bản",
          description:
            "Xây dựng trang web đầu tiên với HTML, CSS và bố cục responsive hiện đại.",
          duration: 20,
          enrolled: 1250,
          rating: 4.8,
          level: "beginner",
          icon: "fab fa-html5",
          gradient: "linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)",
          tags: ["HTML", "CSS", "Frontend"],
        },
        {
          id: 2,
          title: "JavaScript Nâng Cao",
          description:
            "Làm chủ ES6+, bất đồng bộ và kiến trúc hiện đại cho ứng dụng lớn.",
          duration: 30,
          enrolled: 890,
          rating: 4.9,
          level: "advanced",
          icon: "fab fa-js-square",
          gradient: "linear-gradient(135deg, #2575fc 0%, #6a11cb 100%)",
          tags: ["JavaScript", "Patterns"],
        },
        {
          id: 3,
          title: "Python cho Data Science",
          description:
            "Làm việc với Pandas, trực quan hóa dữ liệu và bước đầu Machine Learning.",
          duration: 40,
          enrolled: 2100,
          rating: 4.7,
          level: "intermediate",
          icon: "fab fa-python",
          gradient: "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
          tags: ["Python", "Data"],
        },
        {
          id: 4,
          title: "React.js từ Zero đến Hero",
          description:
            "Hooks, state machines và testing để tự tin triển khai sản phẩm thực tế.",
          duration: 35,
          enrolled: 1750,
          rating: 4.8,
          level: "intermediate",
          icon: "fab fa-react",
          gradient: "linear-gradient(135deg, #00b894 0%, #00cec9 100%)",
          tags: ["React", "Frontend"],
        },
        {
          id: 5,
          title: "Node.js Backend Development",
          description: "Thiết kế API với Express, JWT và kết nối cơ sở dữ liệu an toàn.",
          duration: 25,
          enrolled: 980,
          rating: 4.6,
          level: "intermediate",
          icon: "fab fa-node-js",
          gradient: "linear-gradient(135deg, #fd79a8 0%, #e84393 100%)",
          tags: ["Node", "Backend"],
        },
        {
          id: 6,
          title: "UI/UX Design Fundamentals",
          description: "Tư duy sản phẩm, wireframe và làm việc hiệu quả với Figma.",
          duration: 18,
          enrolled: 650,
          rating: 4.5,
          level: "beginner",
          icon: "fas fa-palette",
          gradient: "linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%)",
          tags: ["Design", "UI/UX"],
        },
      ];
    },
    async sendMessage({ fromVoice = false } = {}) {
      if (this.isTyping) return;
      const trimmed = this.userInput.trim();
      if (!trimmed && !this.pendingAttachments.length) return;

      const attachmentsCopy = this.pendingAttachments.map((file) => ({ ...file }));
      const displayText = trimmed || "Tin nhắn kèm tệp đính kèm";
      const userId = Date.now();
      this.userInput = "";
      this.pendingAttachments = [];

      this.messages.push({
        id: userId,
        type: "user",
        text: displayText,
        attachments: attachmentsCopy,
      });
      this.persistHistory();
      this.scrollToBottom();

      this.isTyping = true;
      try {
        let payload = trimmed || "Tin nhắn kèm tệp đính kèm";
        if (attachmentsCopy.length) {
          const attachmentNote = attachmentsCopy
            .map((file) => `Attachment: ${file.file_name} - ${file.url}`)
            .join("\n");
          payload = `${payload}\n\n${attachmentNote}`;
        }

        this.lastMessageFromVoice = fromVoice;
        const response = await this.getAIResponse(payload);
        const botId = Date.now() + 1;
        this.messages.push({
          id: botId,
          type: "bot",
          text: this.normalizeResponse(response.text),
          suggestions: response.suggestions,
        });
        this.persistHistory();
        if (this.canSpeak && this.autoSpeak && this.lastMessageFromVoice) {
          this.speakMessage(response.text, botId);
        }
      } catch (error) {
        console.error("Error getting AI response:", error);
        this.showError("Có lỗi khi kết nối AI");
      } finally {
        this.isTyping = false;
        this.scrollToBottom();
      }
    },
    async getAIResponse(userMessage) {
      try {
        const response = await sendChatMessage(userMessage);
        const replyText = (response?.reply || "").trim();
        const suggestions = response?.suggestions || [];
        const recommendations = Array.isArray(response?.recommendations)
          ? response.recommendations
          : [];
        this.recommendedCourseIds = recommendations;

        if (replyText) {
          return { text: this.normalizeResponse(replyText), suggestions };
        }
        return this.composeLocalResponse(userMessage);
      } catch (error) {
        console.error("AI service error:", error);
        return this.composeLocalResponse(userMessage);
      }
    },
    composeLocalResponse(userMessage = "") {
      const lower = userMessage.toLowerCase();
      let text =
        "Cảm ơn bạn đã chia sẻ! Mình gửi vài gợi ý để bạn bắt đầu đúng hướng.";
      let suggestions = [
        "Lộ trình học Web",
        "Khóa phổ biến nhất",
        "Gợi ý khóa nâng cao",
      ];
      let recommendations = [];

      if (lower.includes("web")) {
        text =
          "Học web nên vững HTML/CSS trước, sau đó luyện JavaScript và React để triển khai end-to-end.";
        suggestions = ["Khóa HTML & CSS", "Khóa JavaScript", "Khóa React chuyên sâu"];
        recommendations = [1, 2, 4];
      } else if (lower.includes("python") || lower.includes("data")) {
        text =
          "Python + Data Science là lựa chọn tuyệt vời. Hãy bắt đầu với Python cho Data rồi mở rộng sang Machine Learning.";
        suggestions = ["Python nâng cao", "Machine Learning cơ bản", "Data visualization"];
        recommendations = [3];
      } else if (lower.includes("backend") || lower.includes("api")) {
        text =
          "Backend tập trung vào API sạch và bảo mật. Node.js với Express giúp bạn xây dựng dịch vụ nhanh chóng.";
        suggestions = ["Lộ trình Backend", "Bảo mật API?", "Chọn database nào?"];
        recommendations = [5];
      } else if (lower.includes("design") || lower.includes("ui") || lower.includes("ux")) {
        text =
          "Thiết kế UI/UX cần nhiều nghiên cứu và thực hành. Bắt đầu với fundamentals rồi tạo case study thực tế.";
        suggestions = ["Tips cho người mới UI/UX", "Cách viết case study", "Công cụ thiết kế nên học"];
        recommendations = [6];
      } else if (lower.includes("beginner") || lower.includes("start") || lower.includes("mới")) {
        text =
          "Nếu bạn mới bắt đầu, hãy chọn các khóa nền tảng để xây dựng sự tự tin trước khi tăng độ khó.";
        suggestions = ["Lộ trình khởi động", "Mất bao lâu để đi làm?", "Học gì sau kiến thức cơ bản?"];
        recommendations = [1, 6];
      }

      this.recommendedCourseIds = recommendations;
      return { text: this.normalizeResponse(text), suggestions };
    },
    askQuestion(question) {
      this.userInput = question;
      this.sendMessage();
    },
    searchCourses() {
      // filtered by computed; no extra action
      console.log("Searching for:", this.searchQuery);
    },
    filterCourses() {
      console.log("Filter level:", this.selectedLevel);
    },
    selectCourse(course) {
      const message = `Tôi quan tâm đến khóa học "${course.title}"`;
      this.userInput = message;
      this.sendMessage();
    },
    async handleFileUpload(event) {
      if (this.uploading) return;
      const file = event.target.files && event.target.files[0];
      event.target.value = "";
      if (!file) return;

      this.uploading = true;
      try {
        const uploaded = await uploadAttachment(file);
        const descriptor = {
          localId: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
          file_name: uploaded?.file_name || file.name,
          url: uploaded?.url || "",
          mime: uploaded?.mime || file.type,
        };
        this.pendingAttachments.push(descriptor);
      } catch (error) {
        console.error("Upload error:", error);
        this.showError("Không thể tải tệp lên");
      } finally {
        this.uploading = false;
      }
    },
    removeAttachment(id) {
      this.pendingAttachments = this.pendingAttachments.filter(
        (file) => file.localId !== id
      );
    },
    initVoices() {
      if (!this.canSpeak) return;
      const synth = window.speechSynthesis;
      const load = () => {
        this.voices = synth.getVoices();
      };
      this.voiceListener = load;
      synth.addEventListener("voiceschanged", load);
      load();
    },
    speakMessage(text, id) {
      if (!this.canSpeak || !text) return;
      const synth = window.speechSynthesis;
      synth.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "vi-VN";
      utterance.rate = 0.82;
      utterance.pitch = 1.2;
      utterance.volume = 1;
      if (this.voices.length) {
        utterance.voice = this.pickPreferredVoice();
      }
      utterance.onend = () => {
        this.speakingId = null;
      };
      utterance.onerror = () => {
        this.speakingId = null;
      };
      this.speakingId = id;
      synth.speak(utterance);
    },
    initRecorder() {
      if (!this.canRecord) {
        this.recordingUnsupported = true;
        return;
      }
      const SpeechRec =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRec();
      this.recognition.lang = "vi-VN";
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.onstart = () => {
        this.isRecording = true;
      };
      this.recognition.onerror = () => {
        this.isRecording = false;
        this.showError("Không thể nhận diện giọng nói.");
      };
      this.recognition.onend = () => {
        this.isRecording = false;
      };
      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.userInput = `${this.userInput} ${transcript}`.trim();
        this.$nextTick(() => this.sendMessage({ fromVoice: true }));
      };
    },
    toggleRecording() {
      if (!this.recognition) {
        this.showError("Trình duyệt chưa hỗ trợ thu giọng nói.");
        return;
      }
      if (this.isRecording) {
        this.recognition.stop();
        this.isRecording = false;
      } else {
        try {
          this.recognition.start();
        } catch (error) {
          console.warn("Recorder error:", error);
          this.isRecording = false;
        }
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
    getLevelText(level) {
      const map = {
        beginner: "Cơ bản",
        intermediate: "Trung cấp",
        advanced: "Nâng cao",
      };
      return map[level] || level;
    },
    navigateToProfile() {
      this.$router.push("/profile");
    },
    navigateToSettings() {
      this.$router.push("/settings");
    },
    showError(message) {
      alert(message);
    },
    normalizeResponse(text = "") {
      return text
        .replace(/`([^`]+)`/g, "$1")
        .replace(/\*\*(.*?)\*\*/g, "$1")
        .replace(/[\*_]+/g, "")
        .replace(/#+\s*/g, "")
        .replace(/\r/g, "")
        .trim();
    },
    formatReply(rawText = "") {
      const text = this.normalizeResponse(rawText);
      if (!text) return [];

      const lines = text.split("\n").map((line) => line.trim());
      const blocks = [];
      let currentList = null;

      const flushList = () => {
        if (currentList && currentList.items.length) {
          blocks.push({ type: "list", items: currentList.items });
        }
        currentList = null;
      };

      for (const line of lines) {
        if (!line) {
          flushList();
          continue;
        }

        const listMatch = line.match(/^(\d+\.|-)\s+(.*)$/);
        if (listMatch) {
          if (!currentList) {
            currentList = { items: [] };
          }
          const body = listMatch[2];
          const titleMatch = body.match(/^([^:]+):\s*(.*)$/);
          currentList.items.push({
            title: titleMatch ? titleMatch[1] : "",
            body: titleMatch ? titleMatch[2] : body,
          });
          continue;
        }

        flushList();

        if (line.length <= 80 && /^[A-Z0-9À-Ỵ].*/i.test(line)) {
          blocks.push({ type: "heading", text: line });
        } else {
          blocks.push({ type: "paragraph", text: line });
        }
      }

      flushList();
      return blocks;
    },
    pickPreferredVoice() {
      const normalizedPreferred = (this.preferredVoiceName || "").toLowerCase();
      if (normalizedPreferred) {
        const direct = this.voices.find((voice) =>
          `${voice.name} ${voice.lang}`.toLowerCase().includes(normalizedPreferred)
        );
        if (direct) return direct;
      }
      for (const pattern of this.voicePreferences) {
        const match = this.voices.find((voice) => {
          const target = `${voice.name} ${voice.lang}`.toLowerCase();
          return pattern.test(target);
        });
        if (match) return match;
      }
      return this.voices[0];
    },
  },
};
</script>

<style scoped>
:root {
  color-scheme: dark;
}

.assistant-page {
  position: relative;
  min-height: 100vh;
  padding: 2.5rem clamp(1.5rem, 5vw, 4rem) 3rem;
  background: radial-gradient(circle at 20% 20%, #1b1f3b, #080911 70%);
  color: #f4f6fb;
  font-family: "Inter", "Space Grotesk", -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
  overflow: hidden;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(transparent 95%, rgba(148, 163, 184, 0.1) 5%),
    linear-gradient(90deg, transparent 95%, rgba(148, 163, 184, 0.1) 5%);
  background-size: 60px 60px;
  opacity: 0.25;
  pointer-events: none;
}

.glow {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
}

.glow-a {
  top: -110px;
  right: 8%;
  background: rgba(59, 130, 246, 0.5);
}

.glow-b {
  bottom: -130px;
  left: 10%;
  background: rgba(52, 211, 153, 0.45);
}

.assistant-header {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 24px;
  background: rgba(5, 7, 15, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  backdrop-filter: blur(18px);
}

.brand {
  font-size: 1.4rem;
  font-weight: 700;
}

.brand span {
  color: #60a5fa;
}

.search {
  flex: 1;
  display: flex;
  gap: 0.8rem;
  min-width: 260px;
}

.search input {
  flex: 1;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.85rem 1.2rem;
  color: #f8fafc;
}

.search button {
  width: 50px;
  border-radius: 16px;
  border: none;
  background: #60a5fa;
  color: #050911;
  font-size: 1rem;
  cursor: pointer;
}

.header-actions {
  display: flex;
  gap: 0.6rem;
}

.header-actions button {
  border-radius: 999px;
  padding: 0.7rem 1.3rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(340px, 1.05fr) minmax(260px, 0.9fr);
  gap: 1.5rem;
}

.panel {
  border-radius: 32px;
  padding: 1.8rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(8, 11, 23, 0.85);
  box-shadow: 0 50px 100px rgba(6, 8, 15, 0.65);
}

.panel-heading {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.panel-heading select {
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  padding: 0.55rem 1.1rem;
  appearance: none;
  background-image:
    linear-gradient(120deg, rgba(96, 165, 250, 0.2), rgba(52, 211, 153, 0.2)),
    url("data:image/svg+xml,%3Csvg width='14' height='14' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M3 5l4 4 4-4' stroke='%23f8fafc' stroke-width='2' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left top, calc(100% - 0.9rem) 50%;
  padding-right: 2.5rem;
  cursor: pointer;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.25em;
  font-size: 0.75rem;
  color: #60a5fa;
  margin: 0 0 0.35rem;
}

.subline {
  color: rgba(226, 232, 240, 0.7);
  margin: 0.35rem 0 0;
}

.suggested-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  max-width: 460px;
}

.suggested-stack button {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: transparent;
  color: rgba(226, 232, 240, 0.85);
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.85rem;
}

.message-stream {
  height: 420px;
  overflow-y: auto;
  padding-right: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-stream::-webkit-scrollbar {
  width: 10px;
}

.message-stream::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 999px;
}

.message-stream::-webkit-scrollbar-thumb {
  background: linear-gradient(120deg, #60a5fa, #34d399);
  border-radius: 999px;
}

.message-stream::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(120deg, #84ccf7, #4ade80);
}

.bubble {
  border-radius: 20px;
  padding: 1rem 1.2rem;
  line-height: 1.5;
  font-size: 0.95rem;
  max-width: 90%;
  position: relative;
}

.bubble-user {
  align-self: flex-end;
  background: linear-gradient(130deg, #60a5fa, #34d399);
  color: #04121f;
}

.bubble-bot {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.speak-btn {
  position: absolute;
  top: 0.4rem;
  right: 0.4rem;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(226, 232, 240, 0.8);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.speak-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reply-block + .reply-block {
  margin-top: 0.75rem;
}

.reply-heading {
  font-weight: 600;
  color: #93c5fd;
  margin: 0;
}

.reply-list {
  margin: 0;
  padding-left: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.reply-list li {
  list-style: disc;
  font-size: 0.95rem;
  color: rgba(226, 232, 240, 0.9);
}

.typing-indicator {
  display: inline-flex;
  gap: 6px;
  padding: 0.6rem 1rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  animation: pulse 1.3s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes pulse {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  50% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.message-attachments {
  margin-top: 0.6rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.message-attachments a {
  border-radius: 999px;
  padding: 0.2rem 0.75rem;
  background: rgba(96, 165, 250, 0.18);
  color: #93c5fd;
  text-decoration: none;
  font-size: 0.8rem;
}

.attachment-preview {
  margin-top: 1.2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.9rem;
  background: rgba(96, 165, 250, 0.18);
  border-radius: 999px;
  font-size: 0.9rem;
}

.attachment-chip button {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.composer {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-top: 1.2rem;
}

.upload-btn {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  border: 1px dashed rgba(148, 163, 184, 0.5);
  display: grid;
  place-items: center;
  color: #60a5fa;
  cursor: pointer;
}

.upload-btn input {
  display: none;
}

.mic-btn {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  border: 1px dashed rgba(148, 163, 184, 0.4);
  background: transparent;
  color: #fef3c7;
  cursor: pointer;
  display: grid;
  place-items: center;
}

.mic-btn.recording {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.6);
}

.composer input {
  flex: 1;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.9rem 1.1rem;
  color: inherit;
}

.composer button[type="submit"] {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(120deg, #60a5fa, #34d399);
  color: #04121f;
  font-size: 1.1rem;
  cursor: pointer;
}

.insight-panel .course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1rem;
}

.course-card {
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(6, 9, 18, 0.9);
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  cursor: pointer;
}

.course-card.recommended {
  border-color: #60a5fa;
  box-shadow: 0 0 25px rgba(96, 165, 250, 0.45);
}

.course-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #0f172a;
  font-size: 1.2rem;
}

.course-copy h3 {
  margin: 0;
  font-size: 1rem;
}

.course-copy p {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(226, 232, 240, 0.75);
}

.course-card footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  font-size: 0.85rem;
  color: rgba(226, 232, 240, 0.75);
}

.course-card .level {
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.75rem;
}

.level-beginner {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.level-intermediate {
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
}

.level-advanced {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 2rem;
  color: rgba(226, 232, 240, 0.6);
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

@media (max-width: 960px) {
  .workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .assistant-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between;
  }
}
</style>
