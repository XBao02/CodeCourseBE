<template>
  <div class="instructor-chat-container">
    <div class="chat-layout">
      <div class="chat-sideb">
        <div class="sidebar-head">
          <h5 class="mb-0">Danh sách học viên</h5>
          <div class="d-flex align-items-center">
            <span class="badge bg-primary me-2">{{ unreadCount }}</span>
            <button class="btn btn-sm btn-outline-light" @click="refreshStudentList">
              <i class="bx bx-refresh"></i>
            </button>
          </div>
        </div>

        <div class="search-box">
          <div class="input-group">
            <span class="input-group-text">
              <i class="bx bx-search"></i>
            </span>
            <input v-model="searchQuery" type="text" class="form-control" placeholder="Tìm kiếm học viên...">
          </div>
        </div>

        <div class="student-list">
          <div v-for="student in filteredStudents" :key="student.id"
            :class="['student-item', { 'active': selectedStudent?.id === student.id }]" @click="selectStudent(student)">
            <div class="d-flex align-items-center">
              <div class="position-relative">
                <UserAvatar :name="student.name" size="medium" />
                <span :class="['status-indicator', student.isOnline ? 'online' : 'offline']"></span>
              </div>

              <div class="student-info flex-grow-1 ms-3">
                <div class="d-flex justify-content-between align-items-start">
                  <h6 class="student-name mb-0">{{ student.name }}</h6>
                  <small class="text-muted">{{ formatTime(student.lastMessageTime) }}</small>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                  <p class="last-message mb-0">{{ student.lastMessage }}</p>
                  <span v-if="student.unreadCount > 0" class="badge bg-danger rounded-pill">
                    {{ student.unreadCount }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Chat Area -->
      <div class="chat-main">
        <div v-if="!selectedStudent" class="no-chat-selected">
          <div class="text-center">
            <i class="bx bx-chat fs-1 text-muted mb-3"></i>
            <h5 class="text-muted">Chọn một học viên để bắt đầu trò chuyện</h5>
          </div>
        </div>

        <div v-else class="chat-area">
          <!-- Chat Header -->
          <div class="chat-head">
            <div class="d-flex align-items-center">
              <div class="position-relative">
                <UserAvatar :name="selectedStudent.name" size="medium" />
                <span :class="['status-indicator', selectedStudent.isOnline ? 'online' : 'offline']"></span>
              </div>
              <div class="ms-3">
                <h6 class="mb-0">{{ selectedStudent.name }}</h6>
                <small class="text-muted">
                  {{ selectedStudent.isOnline ? 'Đang hoạt động' : 'Không hoạt động' }}
                </small>
              </div>
            </div>

            <div class="chat-actions">
              <button class="btn btn-sm btn-outline-primary me-2" @click="markAsRead">
                <i class="bx bx-check-double"></i>
              </button>
              <button class="btn btn-sm btn-outline-info" @click="viewStudentProfile">
                <i class="bx bx-user"></i>
              </button>
            </div>
          </div>

          <!-- Chat Messages -->
          <div class="chat-messages" ref="messagesContainer">
            <div v-for="message in currentMessages" :key="message.id"
              :class="['message', message.senderId.includes('instructor') ? 'message-sent' : 'message-received']">
              <div class="message-content">
                <div class="message-text">{{ message.text }}</div>
                <div class="message-time">
                  {{ formatTime(message.timestamp) }}
                  <i v-if="message.senderId.includes('instructor')"
                    :class="['bx', message.status === 'read' ? 'bx-check-double text-primary' : 'bx-check']"></i>
                </div>
              </div>
            </div>

            <!-- Typing indicator -->
            <div v-if="selectedStudent.isTyping" class="message message-received">
              <div class="message-content typing-indicator">
                <div class="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Message Input -->
          <div class="chat-input">
            <div class="input-group">
              <input v-model="newMessage" @keyup.enter="sendMessage" @input="handleTyping" type="text"
                class="form-control" placeholder="Nhập phản hồi cho học viên..." :disabled="sending">
              <button class="btn btn-primary" @click="sendMessage" :disabled="!newMessage.trim() || sending">
                <i v-if="sending" class="bx bx-loader bx-spin"></i>
                <i v-else class="bx bx-send"></i>
              </button>
            </div>

            <!-- Quick Replies -->
            <div class="quick-replies mt-2">
              <button v-for="reply in quickReplies" :key="reply" class="btn btn-sm btn-outline-secondary me-2 mb-1"
                @click="useQuickReply(reply)">
                {{ reply }}
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import chatService from '../../services/chatService.js';
import UserAvatar from '../common/UserAvatar.vue';

export default {
  name: 'InstructorChat',
  components: {
    UserAvatar
  },
  data() {
    return {
      students: [],
      selectedStudent: null,
      conversations: {},
      newMessage: '',
      searchQuery: '',
      sending: false,
      quickReplies: [
        'Cảm ơn em đã hỏi!',
        'Em có thể tham khảo tài liệu này',
        'Tôi sẽ giải thích chi tiết',
        'Làm tốt lắm!',
        'Hãy thử làm theo các bước sau'
      ],
      currentInstructorId: 'instructor_1', // This should come from authentication
      typingTimer: null,
      chatInterval: null
    }
  },
  computed: {
    filteredStudents() {
      if (!this.searchQuery) return this.students;
      return this.students.filter(student =>
        student.name.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
    unreadCount() {
      return this.students.reduce((total, student) => total + student.unreadCount, 0);
    },
    currentMessages() {
      if (!this.selectedStudent) return [];
      return chatService.getConversation(this.selectedStudent.id, this.currentInstructorId);
    }
  },
  async mounted() {
    // Connect to chat service
    await chatService.connect(this.currentInstructorId, 'instructor');

    // Load students and conversations
    this.loadStudents();

    // Set up event listeners
    this.setupEventListeners();

    // Start polling for updates
    this.startChatPolling();
  },
  beforeUnmount() {
    // Clean up
    this.removeEventListeners();
    chatService.disconnect();

    if (this.chatInterval) {
      clearInterval(this.chatInterval);
    }
    if (this.typingTimer) {
      clearTimeout(this.typingTimer);
    }
  },
  methods: {
    loadStudents() {
      this.students = chatService.getStudentsWithLastMessages(this.currentInstructorId);
    },

    setupEventListeners() {
      // Listen for new messages and updates
      chatService.on('message-received', this.handleMessageReceived);
      chatService.on('message-sent', this.handleMessageSent);
      chatService.on('message-delivered', this.handleMessageDelivered);
      chatService.on('message-read', this.handleMessageRead);
      chatService.on('typing-status', this.handleTypingStatus);
      chatService.on('user-connected', this.handleUserConnected);
      chatService.on('user-disconnected', this.handleUserDisconnected);
    },

    removeEventListeners() {
      chatService.off('message-received', this.handleMessageReceived);
      chatService.off('message-sent', this.handleMessageSent);
      chatService.off('message-delivered', this.handleMessageDelivered);
      chatService.off('message-read', this.handleMessageRead);
      chatService.off('typing-status', this.handleTypingStatus);
      chatService.off('user-connected', this.handleUserConnected);
      chatService.off('user-disconnected', this.handleUserDisconnected);
    },

    handleMessageReceived({ message }) {
      // Update student list and current conversation
      this.loadStudents();

      if (this.selectedStudent?.id === message.senderId) {
        this.scrollToBottom();

        // Auto-mark as read if chat is open
        setTimeout(() => {
          this.markAsRead();
        }, 1000);
      }
    },

    handleMessageSent({ message }) {
      if (this.selectedStudent?.id === message.receiverId) {
        this.scrollToBottom();
      }
      this.loadStudents();
    },

    handleMessageDelivered() {
      // Update message status
    },

    handleMessageRead() {
      // Update message status
    },

    handleTypingStatus({ userId, isTyping }) {
      const student = this.students.find(s => s.id === userId);
      if (student) {
        student.isTyping = isTyping;
      }
    },

    handleUserConnected({ userId }) {
      const student = this.students.find(s => s.id === userId);
      if (student) {
        student.isOnline = true;
      }
    },

    handleUserDisconnected({ userId }) {
      const student = this.students.find(s => s.id === userId);
      if (student) {
        student.isOnline = false;
      }
    },

    selectStudent(student) {
      this.selectedStudent = student;

      // Mark messages as read
      if (student.unreadCount > 0) {
        const conversationId = chatService.getConversationId(student.id, this.currentInstructorId);
        chatService.markAsRead(conversationId, this.currentInstructorId);
        this.loadStudents(); // Refresh to update unread count
      }

      this.scrollToBottom();
    },

    async sendMessage() {
      if (!this.newMessage.trim() || this.sending || !this.selectedStudent) return;

      this.sending = true;

      try {
        await chatService.sendMessage(this.selectedStudent.id, this.newMessage);
        this.newMessage = '';
        this.loadStudents(); // Refresh student list
        this.scrollToBottom();
      } catch (error) {
        console.error('Failed to send message:', error);
        alert('Không thể gửi tin nhắn. Vui lòng thử lại.');
      } finally {
        this.sending = false;
      }
    },

    useQuickReply(reply) {
      this.newMessage = reply;
      this.sendMessage();
    },

    handleTyping() {
      if (!this.selectedStudent) return;

      // Send typing indicator to student
      chatService.setTyping(this.selectedStudent.id, true);

      if (this.typingTimer) {
        clearTimeout(this.typingTimer);
      }

      this.typingTimer = setTimeout(() => {
        chatService.setTyping(this.selectedStudent.id, false);
      }, 1000);
    },

    markAsRead() {
      if (!this.selectedStudent) return;

      const conversationId = chatService.getConversationId(this.selectedStudent.id, this.currentInstructorId);
      chatService.markAsRead(conversationId, this.currentInstructorId);
      this.loadStudents();
    },

    viewStudentProfile() {
      if (!this.selectedStudent) return;

      const studentInfo = chatService.getUser(this.selectedStudent.id);
      alert(`Thông tin học viên:
Tên: ${studentInfo.name}
Email: ${studentInfo.email}
Trạng thái: ${this.selectedStudent.isOnline ? 'Đang hoạt động' : 'Không hoạt động'}`);
    },

    refreshStudentList() {
      this.loadStudents();
    },

    startChatPolling() {
      // Refresh student list every 10 seconds
      this.chatInterval = setInterval(() => {
        this.loadStudents();
      }, 10000);
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },

    formatTime(timestamp) {
      if (!timestamp) return '';

      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / (1000 * 60));
      const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));

      if (diffMins < 1) return 'Vừa xong';
      if (diffMins < 60) return `${diffMins}p`;
      if (diffHrs < 24) return `${diffHrs}h`;

      return date.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit'
      });
    }
  }
}
</script>

<style scoped>
.instructor-chat-container {
  height: calc(100vh - 100px);
  width: 100%;
  background: #f8f9fa;
  margin: 1rem;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

.chat-sideb {
  width: 350px;
  background: white;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  min-width: 300px;
  max-width: 400px;
}

.sidebar-head {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.search-box {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  flex-shrink: 0;
}

.search-box .input-group-text {
  background: transparent;
  border: none;
  color: #6c757d;
}

.search-box .form-control {
  border: none;
  box-shadow: none;
  background: #f8f9fa;
}

.student-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.student-item {
  padding: 1rem 1.5rem;
  cursor: pointer;
  border-bottom: 1px solid #f8f9fa;
  transition: all 0.2s ease;
}

.student-item:hover {
  background: #f8f9fa;
}

.student-item.active {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}



.status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-indicator.online {
  background: #4caf50;
}

.status-indicator.offline {
  background: #9e9e9e;
}

.student-name {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.last-message {
  color: #6c757d;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: white;
}

.no-chat-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  min-height: 0;
}

.chat-head {
  padding: 1rem 1.5rem;
  background: white;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: #f8f9fa;
  min-height: 0;
}

.message {
  margin-bottom: 1rem;
  display: flex;
}

.message-sent {
  justify-content: flex-end;
}

.message-received {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  position: relative;
}

.message-sent .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-received .message-content {
  background: white;
  color: #333;
  border: 1px solid #e9ecef;
  border-bottom-left-radius: 4px;
}

.message-text {
  word-wrap: break-word;
  line-height: 1.4;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-input {
  padding: 1rem 1.5rem;
  background: white;
  border-top: 1px solid #e9ecef;
  flex-shrink: 0;
}

.chat-input .input-group {
  border-radius: 25px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-input .form-control {
  border: none;
  padding: 0.75rem 1rem;
}

.chat-input .form-control:focus {
  box-shadow: none;
}

.chat-input .btn {
  border: none;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.quick-replies .btn {
  font-size: 0.8rem;
  padding: 0.25rem 0.75rem;
}

/* Typing indicator */
.typing-indicator {
  background: white !important;
  border: 1px solid #e9ecef !important;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6c757d;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {

  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }

  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Scrollbar */
.student-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  overflow-y: auto;
  width: 46px;
}

.student-list::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.student-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Responsive */
@media (max-width: 768px) {
  .instructor-chat-container {
    margin: 0.5rem;
    height: calc(100vh - 80px);
    border-radius: 8px;
  }

  .chat-layout {
    flex-direction: column;
  }

  .chat-sideb {
    width: 100%;
    max-width: none;
    height: 40vh;
    min-height: 300px;
  }

  .chat-main {
    height: 60vh;
  }

  .message-content {
    max-width: 85%;
  }
}

@media (max-width: 576px) {
  .instructor-chat-container {
    margin: 0.25rem;
    height: calc(100vh - 70px);
    border-radius: 6px;
  }

  .chat-sideb {
    height: 35vh;
    min-height: 250px;
  }

  .sidebar-head {
    padding: 1rem;
  }

  .search-box {
    padding: 0.75rem 1rem;
  }

  .student-item {
    padding: 0.75rem 1rem;
  }

  .chat-head {
    padding: 0.75rem 1rem;
  }

  .chat-input {
    padding: 0.75rem 1rem;
  }
}
</style>
