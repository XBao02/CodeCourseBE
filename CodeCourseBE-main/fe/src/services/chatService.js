// Chat Service - Quản lý giao tiếp giữa Student và Instructor
import { reactive } from 'vue';

// Simulated WebSocket or Socket.IO connection
class ChatService {
  constructor() {
    this.isConnected = false;
    this.currentUser = null;
    this.listeners = {};
    
    // Shared state between Student and Instructor
    this.state = reactive({
      conversations: {},
      users: {},
      onlineUsers: new Set(),
      typingUsers: {}
    });
    
    this.initializeDemo();
  }

  // Initialize with demo data
  initializeDemo() {
    this.state.conversations = {
      'student_1-instructor_1': [
        {
          id: 1,
          senderId: 'instructor_1',
          receiverId: 'student_1',
          text: 'Chào em! Em có thắc mắc gì về bài học hôm nay không?',
          timestamp: new Date(Date.now() - 3600000),
          status: 'read'
        },
        {
          id: 2,
          senderId: 'student_1',
          receiverId: 'instructor_1',
          text: 'Dạ em có câu hỏi về phần Vue Router ạ',
          timestamp: new Date(Date.now() - 300000),
          status: 'delivered'
        }
      ],
      'student_2-instructor_1': [
        {
          id: 1,
          senderId: 'student_2',
          receiverId: 'instructor_1',
          text: 'Thầy có thể giải thích thêm về lifecycle hooks không ạ?',
          timestamp: new Date(Date.now() - 2400000),
          status: 'read'
        },
        {
          id: 2,
          senderId: 'instructor_1',
          receiverId: 'student_2',
          text: 'Chắc chắn rồi! Lifecycle hooks là các hàm được gọi tại các thời điểm khác nhau trong vòng đời của component...',
          timestamp: new Date(Date.now() - 2100000),
          status: 'read'
        },
        {
          id: 3,
          senderId: 'student_2',
          receiverId: 'instructor_1',
          text: 'Cảm ơn thầy đã giải đáp!',
          timestamp: new Date(Date.now() - 1800000),
          status: 'read'
        }
      ],
      'student_3-instructor_1': [
        {
          id: 1,
          senderId: 'student_3',
          receiverId: 'instructor_1',
          text: 'Thầy ơi, em không hiểu phần components',
          timestamp: new Date(Date.now() - 900000),
          status: 'delivered'
        }
      ]
    };

    this.state.users = {
      'student_1': {
        id: 'student_1',
        name: 'Nguyễn Văn An',
        role: 'student',
        avatar: null,
        email: 'an.nguyen@student.edu.vn'
      },
      'student_2': {
        id: 'student_2',
        name: 'Trần Thị Bình',
        role: 'student',
        avatar: null,
        email: 'binh.tran@student.edu.vn'
      },
      'student_3': {
        id: 'student_3',
        name: 'Lê Hoàng Cường',
        role: 'student',
        avatar: null,
        email: 'cuong.le@student.edu.vn'
      },
      'instructor_1': {
        id: 'instructor_1',
        name: 'GV. Nguyễn Văn Thầy',
        role: 'instructor',
        avatar: null,
        email: 'thay.nguyen@instructor.edu.vn'
      }
    };

    this.state.onlineUsers = new Set(['student_1', 'instructor_1', 'student_3']);
  }

  // Connect to chat service
  connect(userId, userRole) {
    this.currentUser = { id: userId, role: userRole };
    this.isConnected = true;
    this.state.onlineUsers.add(userId);
    
    // Simulate connection
    this.emit('user-connected', { userId, userRole });
    
    return Promise.resolve({ success: true });
  }

  // Disconnect from chat service
  disconnect() {
    if (this.currentUser) {
      this.state.onlineUsers.delete(this.currentUser.id);
      this.emit('user-disconnected', { userId: this.currentUser.id });
    }
    
    this.isConnected = false;
    this.currentUser = null;
  }

  // Send message
  sendMessage(receiverId, text) {
    if (!this.isConnected || !this.currentUser) {
      return Promise.reject(new Error('Not connected'));
    }

    const message = {
      id: Date.now() + Math.random(),
      senderId: this.currentUser.id,
      receiverId,
      text: text.trim(),
      timestamp: new Date(),
      status: 'sent'
    };

    const conversationId = this.getConversationId(this.currentUser.id, receiverId);
    
    if (!this.state.conversations[conversationId]) {
      this.state.conversations[conversationId] = [];
    }

    this.state.conversations[conversationId].push(message);

    // Simulate delivery
    setTimeout(() => {
      message.status = 'delivered';
      this.emit('message-delivered', { messageId: message.id, conversationId });
      
      // Simulate read after a delay
      setTimeout(() => {
        message.status = 'read';
        this.emit('message-read', { messageId: message.id, conversationId });
      }, Math.random() * 3000 + 1000);
    }, 500);

    this.emit('message-sent', { message, conversationId });
    
    return Promise.resolve(message);
  }

  // Get conversation between two users
  getConversation(userId1, userId2) {
    const conversationId = this.getConversationId(userId1, userId2);
    return this.state.conversations[conversationId] || [];
  }

  // Get all conversations for a user
  getConversationsForUser(userId) {
    const conversations = {};
    
    Object.keys(this.state.conversations).forEach(conversationId => {
      if (conversationId.includes(userId)) {
        const otherUserId = conversationId.split('-').find(id => id !== userId);
        conversations[otherUserId] = this.state.conversations[conversationId];
      }
    });
    
    return conversations;
  }

  // Get students with their last messages (for instructor)
  getStudentsWithLastMessages(instructorId) {
    const students = [];
    
    Object.values(this.state.users)
      .filter(user => user.role === 'student')
      .forEach(student => {
        const conversation = this.getConversation(student.id, instructorId);
        const lastMessage = conversation[conversation.length - 1];
        const unreadCount = conversation.filter(msg => 
          msg.senderId === student.id && msg.status !== 'read'
        ).length;

        students.push({
          ...student,
          isOnline: this.state.onlineUsers.has(student.id),
          lastMessage: lastMessage ? lastMessage.text : 'Chưa có tin nhắn',
          lastMessageTime: lastMessage ? lastMessage.timestamp : null,
          unreadCount,
          isTyping: this.state.typingUsers[student.id] || false
        });
      });

    // Sort by last message time
    return students.sort((a, b) => {
      if (!a.lastMessageTime) return 1;
      if (!b.lastMessageTime) return -1;
      return new Date(b.lastMessageTime) - new Date(a.lastMessageTime);
    });
  }

  // Set typing status
  setTyping(receiverId, isTyping) {
    if (!this.currentUser) return;
    
    this.state.typingUsers[this.currentUser.id] = isTyping;
    
    this.emit('typing-status', {
      userId: this.currentUser.id,
      receiverId,
      isTyping
    });

    // Auto-stop typing after 3 seconds
    if (isTyping) {
      setTimeout(() => {
        if (this.state.typingUsers[this.currentUser.id]) {
          this.setTyping(receiverId, false);
        }
      }, 3000);
    }
  }

  // Mark messages as read
  markAsRead(conversationId, userId) {
    const conversation = this.state.conversations[conversationId];
    if (conversation) {
      conversation.forEach(message => {
        if (message.senderId !== userId && message.status !== 'read') {
          message.status = 'read';
        }
      });
      
      this.emit('messages-read', { conversationId, userId });
    }
  }

  // Get user info
  getUser(userId) {
    return this.state.users[userId];
  }

  // Check if user is online
  isUserOnline(userId) {
    return this.state.onlineUsers.has(userId);
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (this.listeners[event]) {
      const index = this.listeners[event].indexOf(callback);
      if (index > -1) {
        this.listeners[event].splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  // Helper methods
  getConversationId(userId1, userId2) {
    // Always put instructor first for consistency
    const user1 = this.state.users[userId1];
    const user2 = this.state.users[userId2];
    
    if (user1?.role === 'instructor') {
      return `${userId2}-${userId1}`;
    } else if (user2?.role === 'instructor') {
      return `${userId1}-${userId2}`;
    } else {
      // Both are same role, sort alphabetically
      return [userId1, userId2].sort().join('-');
    }
  }

  // Get instructor for student
  getInstructorForStudent(studentId) {
    // In a real app, this would come from course enrollment
    return 'instructor_1';
  }

  // Simulate new messages (for demo)
  simulateIncomingMessage(fromUserId, toUserId, text) {
    const message = {
      id: Date.now() + Math.random(),
      senderId: fromUserId,
      receiverId: toUserId,
      text,
      timestamp: new Date(),
      status: 'delivered'
    };

    const conversationId = this.getConversationId(fromUserId, toUserId);
    
    if (!this.state.conversations[conversationId]) {
      this.state.conversations[conversationId] = [];
    }

    this.state.conversations[conversationId].push(message);
    this.emit('message-received', { message, conversationId });
    
    return message;
  }
}

// Create singleton instance
const chatService = new ChatService();

// Auto-simulation for demo
if (process.env.NODE_ENV === 'development') {
  setInterval(() => {
    if (Math.random() > 0.9) { // 10% chance every 5 seconds
      const messages = [
        'Thầy ơi, em có thêm câu hỏi',
        'Em đã hiểu rồi ạ',
        'Phần này hơi khó hiểu',
        'Cảm ơn thầy!'
      ];
      
      const students = ['student_1', 'student_2', 'student_3'];
      const randomStudent = students[Math.floor(Math.random() * students.length)];
      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      
      chatService.simulateIncomingMessage(randomStudent, 'instructor_1', randomMessage);
    }
  }, 5000);
}

export default chatService;
