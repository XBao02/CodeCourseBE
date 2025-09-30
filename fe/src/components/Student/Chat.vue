<template>
  <div class="chat-container">
    <!-- Header -->
    <div class="chat-head">
      <div class="d-flex align-items-center">
        <UserAvatar 
          :name="instructorName" 
          size="medium"
        />
        <div class="ms-3">
          <h6 class="mb-0">Chat với Giảng viên</h6>
          <small class="text-muted">{{ onlineStatus ? 'Đang hoạt động' : 'Không hoạt động' }}</small>
        </div>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-primary" @click="refreshChat">
          <i class="bx bx-refresh"></i>
        </button>
      </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="message in messages" 
        :key="message.id"
        :class="['message', message.senderId === currentStudentId ? 'message-sent' : 'message-received']"
      >
        <div class="message-content">
          <div class="message-text">{{ message.text }}</div>
          <div class="message-time">
            {{ formatTime(message.timestamp) }}
            <i 
              v-if="message.senderId === currentStudentId" 
              :class="['bx', message.status === 'read' ? 'bx-check-double text-primary' : 'bx-check']"
            ></i>
          </div>
        </div>
      </div>
      
      <!-- Typing indicator -->
      <div v-if="isInstructorTyping" class="message message-received">
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
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage"
          @input="handleTyping"
          type="text" 
          class="form-control" 
          placeholder="Nhập tin nhắn của bạn..."
          :disabled="sending"
        >
        <button 
          class="btn btn-primary" 
          @click="sendMessage"
          :disabled="!newMessage.trim() || sending"
        >
          <i v-if="sending" class="bx bx-loader bx-spin"></i>
          <i v-else class="bx bx-send"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import chatService from '../../services/chatService.js';
import UserAvatar from '../common/UserAvatar.vue';

export default {
  name: 'StudentChat',
  components: {
    UserAvatar
  },
  data() {
    return {
      messages: [],
      newMessage: '',
      currentStudentId: 'student_1', // This should come from authentication
      instructorId: 'instructor_1',
      instructorName: 'GV. Nguyễn Văn Thầy',
      onlineStatus: false,
      sending: false,
      isInstructorTyping: false,
      typingTimer: null,
      chatInterval: null
    }
  },
  async mounted() {
    // Connect to chat service
    await chatService.connect(this.currentStudentId, 'student');
    
    // Load existing conversation
    this.loadConversation();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Check instructor online status
    this.onlineStatus = chatService.isUserOnline(this.instructorId);
    
    this.scrollToBottom();
  },
  beforeUnmount() {
    // Clean up
    this.removeEventListeners();
    chatService.disconnect();
    
    if (this.typingTimer) {
      clearTimeout(this.typingTimer);
    }
  },
  methods: {
    loadConversation() {
      this.messages = chatService.getConversation(this.currentStudentId, this.instructorId);
    },
    
    setupEventListeners() {
      // Listen for new messages
      chatService.on('message-received', this.handleMessageReceived);
      chatService.on('message-delivered', this.handleMessageDelivered);
      chatService.on('message-read', this.handleMessageRead);
      chatService.on('typing-status', this.handleTypingStatus);
      chatService.on('user-connected', this.handleUserConnected);
      chatService.on('user-disconnected', this.handleUserDisconnected);
    },
    
    removeEventListeners() {
      chatService.off('message-received', this.handleMessageReceived);
      chatService.off('message-delivered', this.handleMessageDelivered);
      chatService.off('message-read', this.handleMessageRead);
      chatService.off('typing-status', this.handleTypingStatus);
      chatService.off('user-connected', this.handleUserConnected);
      chatService.off('user-disconnected', this.handleUserDisconnected);
    },
    
    handleMessageReceived({ message }) {
      if (message.senderId === this.instructorId) {
        this.loadConversation();
        this.scrollToBottom();
        
        // Mark as read after a short delay
        setTimeout(() => {
          const conversationId = chatService.getConversationId(this.currentStudentId, this.instructorId);
          chatService.markAsRead(conversationId, this.currentStudentId);
        }, 1000);
      }
    },
    
    handleMessageDelivered({ messageId }) {
      this.loadConversation();
    },
    
    handleMessageRead({ messageId }) {
      this.loadConversation();
    },
    
    handleTypingStatus({ userId, isTyping }) {
      if (userId === this.instructorId) {
        this.isInstructorTyping = isTyping;
        if (isTyping) {
          this.scrollToBottom();
        }
      }
    },
    
    handleUserConnected({ userId }) {
      if (userId === this.instructorId) {
        this.onlineStatus = true;
      }
    },
    
    handleUserDisconnected({ userId }) {
      if (userId === this.instructorId) {
        this.onlineStatus = false;
      }
    },
    
    async sendMessage() {
      if (!this.newMessage.trim() || this.sending) return;
      
      this.sending = true;
      
      try {
        await chatService.sendMessage(this.instructorId, this.newMessage);
        this.loadConversation();
        this.newMessage = '';
        this.scrollToBottom();
      } catch (error) {
        console.error('Failed to send message:', error);
        alert('Không thể gửi tin nhắn. Vui lòng thử lại.');
      } finally {
        this.sending = false;
      }
    },
    
    handleTyping() {
      // Send typing indicator to instructor
      chatService.setTyping(this.instructorId, true);
      
      if (this.typingTimer) {
        clearTimeout(this.typingTimer);
      }
      
      this.typingTimer = setTimeout(() => {
        chatService.setTyping(this.instructorId, false);
      }, 1000);
    },
    
    refreshChat() {
      this.loadConversation();
      this.onlineStatus = chatService.isUserOnline(this.instructorId);
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
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
      const diffMins = Math.floor(diffMs / (1000 * 60));
      
      if (diffMins < 1) return 'Vừa xong';
      if (diffMins < 60) return `${diffMins} phút trước`;
      if (diffHrs < 24) return `${diffHrs} giờ trước`;
      
      return date.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  background: #fff;
  margin: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-head {
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
} 

.chat-header .status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  min-height: 0;
  background: #f8f9fa;
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

.message-sent .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.message-received .message-time {
  color: #6c757d;
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
  font-size: 0.95rem;
}

.chat-input .form-control:focus {
  box-shadow: none;
}

.chat-input .btn {
  border: none;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

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

/* Scrollbar */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive */
@media (max-width: 768px) {
  .chat-container {
    margin: 0.5rem;
    height: calc(100vh - 80px);
    border-radius: 8px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-header {
    padding: 0.75rem 1rem;
  }
  
  .chat-input {
    padding: 0.75rem 1rem;
  }
}

@media (max-width: 576px) {
  .chat-container {
    margin: 0.25rem;
    height: calc(100vh - 70px);
    border-radius: 6px;
  }
  
  .chat-header {
    padding: 0.5rem 0.75rem;
  }
  
  .chat-messages {
    padding: 0.75rem;
  }
  
  .chat-input {
    padding: 0.5rem 0.75rem;
  }
  
  .message-content {
    max-width: 90%;
    padding: 0.5rem 0.75rem;
  }
}
</style>