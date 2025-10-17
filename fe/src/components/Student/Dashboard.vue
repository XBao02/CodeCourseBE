<template>
  <div class="container py-5">
    <!--  PHẦN THỐNG KÊ -->
    <div class="row g-4 mb-5">
      <!-- Lặp qua các chỉ số thống kê -->
      <div class="col-md-3" v-for="stat in stats" :key="stat.title">
        <div class="card border-0 shadow-sm h-100 text-center p-3 rounded-4 hover-card">
          <h6 class="text-muted mb-2">{{ stat.title }}</h6>
          <h2 class="fw-bold text-primary">{{ stat.value }}</h2>
        </div>
      </div>
    </div>

    <!--  LỘ TRÌNH HỌC TẬP -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3 fw-bold text-primary">🎯 Learning Path</h5>
        <ul class="list-group list-group-flush">
          <!-- Lặp qua danh sách lộ trình -->
          <li class="list-group-item d-flex justify-content-between align-items-center" v-for="path in learningPath"
            :key="path.name">
            <span>{{ path.name }}</span>
            <!-- Đổi màu badge theo trạng thái -->
            <span class="badge px-3 py-2" :class="{
              'bg-success': path.status === 'Completed',
              'bg-warning text-dark': path.status === 'In Progress',
              'bg-secondary': path.status === 'Not Started'
            }">
              {{ path.status }}
            </span>
          </li>
        </ul>
      </div>
    </div>

    <!--  KHÓA HỌC ĐÃ ĐĂNG KÝ -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3 fw-bold text-primary">📚 Enrolled Courses</h5>
        <div class="row g-3">
          <!-- Lặp qua danh sách khóa học -->
          <div class="col-md-6" v-for="course in courses" :key="course.id">
            <div class="card h-100 border-0 shadow-sm rounded-4">
              <div class="card-body">
                <h6 class="card-title fw-semibold">{{ course.title }}</h6>
                <p class="text-muted small">{{ course.description }}</p>
                <!-- Thanh tiến độ -->
                <div class="progress" style="height: 20px;">
                  <div class="progress-bar progress-bar-striped bg-info fw-bold" role="progressbar"
                    :style="{ width: course.progress + '%' }">
                    {{ course.progress }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!--  TIẾN ĐỘ TỔNG QUAN -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3 fw-bold text-primary">📈 Overall Progress</h5>
        <div class="progress" style="height: 30px;">
          <div class="progress-bar bg-success fw-bold" role="progressbar" :style="{ width: overallProgress + '%' }">
            {{ overallProgress }}%
          </div>
        </div>
      </div>
    </div>

    <!--  NÚT LÀM BÀI KIỂM TRA KỸ NĂNG -->
    <div class="text-center mt-5" v-if="!showTest">
      <button class="btn btn-primary btn-lg shadow px-5 rounded-pill" @click="startTest">
        Take Skill Test
      </button>
    </div>

    <!--  FORM LÀM BÀI KIỂM TRA -->
    <div v-if="showTest" class="card border-0 shadow-sm mt-4 rounded-4">
      <div class="card-body">
        <h5 class="fw-bold mb-4 text-center text-primary">Skill Test</h5>

        <!-- Lặp qua từng câu hỏi -->
        <div v-for="(question, index) in testQuestions" :key="index" class="mb-4">
          <h6>{{ index + 1 }}. {{ question.question }}</h6>
          <!-- Hiển thị các lựa chọn đáp án -->
          <div class="form-check" v-for="option in question.options" :key="option">
            <input class="form-check-input" type="radio" :name="'q' + index" :value="option" v-model="question.selected"
              :disabled="submitted" />
            <label class="form-check-label">{{ option }}</label>
          </div>
        </div>

        <!-- Nút nộp bài và làm lại -->
        <div class="text-center mt-4">
          <!-- Khi chưa nộp -->
          <button v-if="!submitted" class="btn btn-success px-4 rounded-pill" @click="submitTest">
            Submit Test
          </button>

          <!-- Khi đã nộp xong -->
          <div v-else>
            <div class="alert alert-info text-center fs-5 mb-4">
              🎉 Your Score: <strong>{{ score }}/{{ testQuestions.length }}</strong>
            </div>
            <!-- Nút làm lại (random lại câu hỏi) -->
            <button class="btn btn-outline-primary px-4 rounded-pill" @click="resetTest">
              🔁 Retake Test (Random)
            </button>
          </div>
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
/*  Hiệu ứng hover cho các thẻ thống kê */
.hover-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}
</style>
