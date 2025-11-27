<template>
  <div class="dashboard-wrapper">
    <!-- Header -->
    <div class="dashboard-header">
      <h1>My Dashboard</h1>
      <p>Track your learning progress and achievements</p>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.title">
        <h6>{{ stat.title }}</h6>
        <h3>{{ stat.value }}</h3>
      </div>
    </div>

    <!-- Learning Path -->
    <div class="content-card">
      <h5>Learning Path</h5>
      <div class="learning-path-list">
        <div class="path-item" v-for="path in learningPath" :key="path.name">
          <span class="path-name">{{ path.name }}</span>
          <span class="path-status" :class="{
            'status-completed': path.status === 'Completed',
            'status-progress': path.status === 'In Progress',
            'status-not-started': path.status === 'Not Started'
          }">
            {{ path.status }}
          </span>
        </div>
      </div>
    </div>

    <!-- Enrolled Courses -->
    <div class="content-card">
      <h5>Enrolled Courses</h5>
      <div class="courses-grid">
        <div class="course-card" v-for="course in courses" :key="course.id">
          <h6>{{ course.title }}</h6>
          <p>{{ course.description }}</p>
          <div class="progress-container">
            <div class="progress-header">
              <span class="progress-label">Progress</span>
              <span class="progress-value">{{ course.progress }}%</span>
            </div>
            <div class="progress-bar-wrapper">
              <div class="progress-bar-fill" :style="{ width: course.progress + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Overall Progress -->
    <div class="content-card">
      <h5>Overall Progress</h5>
      <div class="overall-progress">
        <div class="progress-header">
          <span class="progress-label">Total Completion</span>
          <span class="progress-value">{{ overallProgress }}%</span>
        </div>
        <div class="progress-bar-wrapper large">
          <div class="progress-bar-fill" :style="{ width: overallProgress + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Skill Test Button -->
    <div class="test-section" v-if="!showTest">
      <button class="action-button" @click="startTest">
        Take Skill Test
      </button>
    </div>

    <!-- Skill Test Form -->
    <div v-if="showTest" class="content-card test-card">
      <h5>Skill Test</h5>

      <div class="test-questions">
        <div v-for="(question, index) in testQuestions" :key="index" class="question-item">
          <h6>{{ index + 1 }}. {{ question.question }}</h6>
          <div class="options-list">
            <label class="option-label" v-for="option in question.options" :key="option">
              <input type="radio" :name="'q' + index" :value="option" v-model="question.selected" :disabled="submitted" />
              <span>{{ option }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="test-actions">
        <button v-if="!submitted" class="action-button" @click="submitTest">
          Submit Test
        </button>

        <div v-else class="test-result">
          <div class="result-score">
            Your Score: <strong>{{ score }}/{{ testQuestions.length }}</strong>
          </div>
          <button class="action-button secondary" @click="resetTest">
            Retake Test
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "StudentDashboard",
  data() {
    return {
      //  Thống kê tổng quan của học viên
      stats: [
        { title: "Courses Enrolled", value: 4 },
        { title: "Completed Courses", value: 2 },
        { title: "Pending Courses", value: 2 },
        { title: "Skill Tests Taken", value: 1 },
      ],
      //  Lộ trình học tập
      learningPath: [
        { name: "HTML & CSS Basics", status: "Completed" },
        { name: "JavaScript Fundamentals", status: "In Progress" },
        { name: "Vue.js Framework", status: "Not Started" },
      ],
      //  Khóa học học viên đã tham gia
      courses: [
        { id: 1, title: "Frontend Development", description: "Learn HTML, CSS, JS", progress: 80 },
        { id: 2, title: "Vue.js Advanced", description: "Master Vue ecosystem", progress: 40 },
      ],
      //  Tiến độ tổng thể
      overallProgress: 60,

      //  Trạng thái hiển thị form test
      showTest: false,
      //  Đã nộp bài hay chưa
      submitted: false,
      //  Điểm số đạt được
      score: 0,

      //  Câu hỏi gốc (nguồn dữ liệu bài test)
      baseQuestions: [
        {
          question: "Which HTML tag is used to define a hyperlink?",
          options: ["<link>", "<a>", "<href>", "<hyper>"],
          correct: "<a>",
        },
        {
          question: "Which of the following is a JavaScript framework?",
          options: ["Laravel", "Vue.js", "Django", "Flask"],
          correct: "Vue.js",
        },
        {
          question: "What does CSS stand for?",
          options: [
            "Computer Style Sheets",
            "Creative Style Sheets",
            "Cascading Style Sheets",
            "Colorful Style Sheets",
          ],
          correct: "Cascading Style Sheets",
        },
        {
          question: "Which HTML tag is used for inserting a line break?",
          options: ["<break>", "<br>", "<lb>", "<newline>"],
          correct: "<br>",
        },
        {
          question: "Which of these is not a JavaScript data type?",
          options: ["Boolean", "Undefined", "Float", "Object"],
          correct: "Float",
        },
      ],

      //  Danh sách câu hỏi sau khi được chọn hoặc xáo trộn
      testQuestions: [],
    };
  },

  methods: {
    //  Bắt đầu làm bài kiểm tra
    startTest() {
      this.showTest = true;
      this.loadRandomQuestions(); // Gọi hàm load câu hỏi ngẫu nhiên
    },

    //  Nộp bài và tính điểm
    submitTest() {
      this.submitted = true;
      // Đếm số câu đúng
      this.score = this.testQuestions.filter(
        (q) => q.selected === q.correct
      ).length;
    },

    //  Làm lại bài kiểm tra (ngẫu nhiên câu hỏi mới)
    resetTest() {
      this.submitted = false;
      this.score = 0;
      this.loadRandomQuestions(); // Trộn lại câu hỏi
    },

    //  Hàm xáo trộn mảng (Fisher–Yates Shuffle)
    shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    },

    //  Load ngẫu nhiên 3 câu hỏi (và xáo trộn thứ tự đáp án)
    loadRandomQuestions() {
      // Sao chép mảng câu hỏi gốc rồi xáo trộn thứ tự
      const shuffled = this.shuffleArray([...this.baseQuestions]);
      // Chọn 3 câu đầu và gán lại giá trị selected = null
      this.testQuestions = shuffled.slice(0, 3).map((q) => ({
        ...q,
        selected: null,
        options: this.shuffleArray([...q.options]), // Xáo luôn cả thứ tự đáp án
      }));
    },
  },
};
</script>

<style scoped>
.dashboard-wrapper {
  background: #f8f9fa;
  min-height: 100vh;
  padding: 40px;
}

.dashboard-header {
  margin-bottom: 40px;
}

.dashboard-header h1 {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.dashboard-header p {
  color: #666;
  font-size: 15px;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stat-card h6 {
  font-size: 13px;
  color: #666;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 8px 0;
}

.stat-card h3 {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
  color: #1a1a1a;
}

.content-card {
  background: white;
  padding: 28px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.content-card h5 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 24px 0;
}

.learning-path-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.path-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.path-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
}

.path-status {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: 500;
}

.status-completed {
  background: #dbeafe;
  color: #2563eb;
}

.status-progress {
  background: #fef3c7;
  color: #d97706;
}

.status-not-started {
  background: #f3f4f6;
  color: #6b7280;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.course-card {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.course-card h6 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.course-card p {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px 0;
}

.progress-container {
  margin-top: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.progress-value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 600;
}

.progress-bar-wrapper {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-wrapper.large {
  height: 12px;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  transition: width 0.3s ease;
}

.overall-progress {
  max-width: 600px;
}

.test-section {
  text-align: center;
  padding: 40px 0;
}

.action-button {
  padding: 12px 32px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.action-button.secondary {
  background: white;
  color: #1f2937;
  border: 1px solid #d1d5db;
}

.action-button.secondary:hover {
  background: #f8f9fa;
  border-color: #9ca3af;
}

.test-card {
  max-width: 800px;
  margin: 0 auto;
}

.test-questions {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 32px;
}

.question-item h6 {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-label:hover {
  background: #e5e7eb;
}

.option-label input[type="radio"] {
  cursor: pointer;
}

.option-label span {
  font-size: 14px;
  color: #1a1a1a;
}

.test-actions {
  text-align: center;
}

.test-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.result-score {
  font-size: 18px;
  color: #1a1a1a;
  padding: 20px 32px;
  background: #eff6ff;
  border-radius: 8px;
}

.result-score strong {
  font-size: 24px;
  color: #3b82f6;
}

@media (max-width: 768px) {
  .dashboard-wrapper {
    padding: 20px;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }
}
</style>
