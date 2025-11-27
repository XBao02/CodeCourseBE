<template>
  <div class="instructor-chat-container">
    <div class="chat-layout">
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <h3>Messages</h3>
          <span class="unread-badge">{{ unreadCount }}</span>
        </div>

        <div class="search-box">
          <input v-model="searchQuery" type="text" placeholder="Search students..." class="search-input">
        </div>

        <div class="student-list">
          <div v-for="student in filteredStudents" :key="student.id"
            :class="['student-item', { active: selectedStudent?.id === student.id }]" 
            @click="selectStudent(student)">
            <div class="student-header">
              <div class="student-info">
                <h5 class="student-name">{{ student.name }}</h5>
                <p class="last-message">{{ student.lastMessage }}</p>
              </div>
              <div class="student-meta">
                <span class="last-time">{{ formatTime(student.lastMessageTime) }}</span>
                <span v-if="student.unreadCount > 0" class="unread-count">{{ student.unreadCount }}</span>
              </div>
            </div>
            <div class="status-indicator" :class="student.isOnline ? 'online' : 'offline'"></div>
          </div>
        </div>
      </div>

      <!-- Main Chat Area -->
      <div class="chat-main">
        <div v-if="!selectedStudent" class="no-chat-selected">
          <div class="empty-state">
            <h4>Select a student to start messaging</h4>
          </div>
        </div>

        <div v-else class="chat-area">
          <!-- Chat Header -->
          <div class="chat-header">
            <div class="header-info">
              <h4 class="student-name">{{ selectedStudent.name }}</h4>
              <small class="status-text">{{ selectedStudent.isOnline ? 'Active' : 'Inactive' }}</small>
            </div>

            <div class="chat-actions">
              <button class="icon-btn" @click="markAsRead" title="Mark as read">✓</button>
              <button class="icon-btn" @click="viewStudentProfile" title="View profile">👤</button>
            </div>
          </div>

          <!-- Chat Messages -->
          <div class="chat-messages" ref="messagesContainer">
            <div v-for="message in currentMessages" :key="message.id"
              :class="['message', message.senderId.includes('instructor') ? 'sent' : 'received']">
              <div class="message-bubble">
                <div class="message-text">{{ message.text }}</div>
                <div class="message-meta">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>

            <!-- Typing indicator -->
            <div v-if="selectedStudent.isTyping" class="message received">
              <div class="message-bubble">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Message Input -->
          <div class="chat-input-area">
            <div class="message-input-wrapper">
              <input v-model="newMessage" 
                     @keyup.enter="sendMessage" 
                     @input="handleTyping" 
                     type="text"
                     class="message-input" 
                     placeholder="Write your message..." 
                     :disabled="sending">
              <button class="send-btn" @click="sendMessage" :disabled="!newMessage.trim() || sending">
                {{ sending ? '...' : '→' }}
              </button>
            </div>

            <!-- Quick Replies -->
            <div class="quick-replies">
              <button v-for="reply in quickReplies" :key="reply" class="quick-reply-btn"
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
  height: calc(100vh - 80px);
  width: 100%;
  background: #f8f9fa;
  margin: 20px;
  overflow: hidden;
  border-radius: 8px;
  display: flex;
}

.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

.chat-sidebar {
  width: 340px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.unread-badge {
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.search-box {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: #f9fafb;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
}

.student-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.student-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s ease;
  position: relative;
}

.student-item:hover {
  background: #f9fafb;
}

.student-item.active {
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.student-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px 0;
  font-size: 14px;
}

.last-message {
  color: #666;
  font-size: 13px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  margin-left: 8px;
}

.last-time {
  font-size: 12px;
  color: #999;
}

.unread-count {
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.status-indicator {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-indicator.online {
  background: #1f2937;
}

.status-indicator.offline {
  background: #d1d5db;
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

.empty-state {
  text-align: center;
  color: #999;
}

.empty-state h4 {
  margin: 0;
  font-size: 16px;
  color: #666;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  min-height: 0;
}

.chat-header {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-info {
  flex: 1;
}

.header-info .student-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1a1a1a;
}

.status-text {
  font-size: 13px;
  color: #666;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  background: none;
  border: 1px solid #d1d5db;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.chat-messages {
  flex: 1;
  padding: 16px 24px;
  overflow-y: auto;
  background: white;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  margin-bottom: 8px;
}

.message.sent {
  justify-content: flex-end;
}

.message.received {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 65%;
  padding: 10px 14px;
  border-radius: 12px;
  word-wrap: break-word;
}

.message.sent .message-bubble {
  background: #1f2937;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.received .message-bubble {
  background: #f0f0f0;
  color: #1a1a1a;
  border-bottom-left-radius: 4px;
}

.message-text {
  font-size: 14px;
  line-height: 1.4;
}

.message-meta {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 4px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  height: auto;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d1d5db;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.message-input-wrapper {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.message-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.message-input:disabled {
  background: #f9fafb;
  color: #999;
}

.send-btn {
  padding: 10px 16px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  background: #111827;
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-reply-btn {
  padding: 6px 12px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: #374151;
  transition: all 0.2s ease;
}

.quick-reply-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* Scrollbar */
.student-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.student-list::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.student-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.student-list::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Responsive */
@media (max-width: 768px) {
  .instructor-chat-container {
    margin: 10px;
    height: calc(100vh - 60px);
  }

  .chat-layout {
    flex-direction: column;
  }

  .chat-sidebar {
    width: 100%;
    max-height: 40vh;
    min-height: 250px;
  }

  .chat-main {
    min-height: 60vh;
  }

  .message-bubble {
    max-width: 85%;
  }
}
</style>
