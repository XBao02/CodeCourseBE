<template>
  <div class="dashboard-wrapper p-4">
    <!-- TRẠNG THÁI ĐANG TẢI -->
    <div v-if="isLoading" class="d-flex justify-content-center align-items-center" style="min-height: 500px;">
      <div class="spinner-border text-dark" role="status">
        <span class="visually-hidden">Đang tải...</span>
      </div>
      <p class="ms-3 text-muted">Đang tìm nạp dữ liệu giáo dục mới nhất...</p>
    </div>

    <!-- NỘI DUNG CHÍNH -->
    <div v-else>
      <!-- HIỂN THỊ LỖI HOẶC CẢNH BÁO DỮ LIỆU GIẢ LẬP -->
      <div v-if="error" class="alert alert-danger d-flex align-items-center mb-4 card p-3" role="alert">
        <span class="align-middle me-2 text-danger fs-4">⚠️</span>
        <div>
          <strong>Lỗi Dữ Liệu:</strong> {{ error }}
        </div>
      </div>
      <div v-if="isMockData" class="alert alert-warning d-flex align-items-center mb-4 card p-3" role="alert">
        <span class="align-middle me-2 text-warning fs-4">💡</span>
        <div>
          <strong>Cảnh báo:</strong> Đang hiển thị **DỮ LIỆU GIẢ LẬP**. Vui lòng thay thế `'REPLACE_WITH_YOUR_ACTUAL_AUTH_TOKEN'` bằng token hợp lệ để tải dữ liệu thật.
        </div>
      </div>

      <ul class="nav nav-pills mb-4">
        <li class="nav-item" v-for="tab in tabs" :key="tab">
          <button
            class="nav-link"
            :class="{ active: activeTab === tab }"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </li>
      </ul>

      <!-- NỘI DUNG TAB TỔNG QUAN -->
      <div v-if="activeTab === 'Overview'">
        <div class="row g-3 mb-4">
          <div class="col-md-3" v-for="card in statCards" :key="card.title">
            <div class="card h-100 shadow-sm p-3">
              <h6 class="text-muted">{{ card.title }}</h6>
              <h3 class="fw-bold">{{ card.value }}</h3>
              <small :class="{'text-success': card.change > 0, 'text-danger': card.change < 0}">
                {{ card.change > 0 ? '+' : '' }}{{ card.change }}% {{ card.note }}
              </small>
            </div>
          </div>
        </div>
        <div class="row g-4 mb-4">
          <div class="col-lg-6">
            <div class="card p-3 mb-4">
              <h6 class="fw-bold">Số Lượng Học Viên Đăng Ký Theo Thời Gian</h6>
              <!-- Placeholder cho Biểu đồ Đường -->
              <div class="chart-placeholder bg-light rounded text-center text-muted p-5">
                [Placeholder Biểu đồ Đường: Xu hướng Đăng ký]
                <small v-if="lineChartData" class="mt-2 d-block">Điểm dữ liệu: {{ lineChartData.datasets[0].data.length }}</small>
              </div>
            </div>
            <div class="card p-3">
              <h6 class="fw-bold">Điểm Trung Bình Bài Quiz & Lab Theo Khóa Học</h6>
              <!-- Placeholder cho Biểu đồ Cột -->
              <div class="chart-placeholder bg-light rounded text-center text-muted p-5">
                [Placeholder Biểu đồ Cột: Phân bổ Điểm số]
                <small v-if="scoreChartData" class="mt-2 d-block">Khóa học được theo dõi: {{ scoreChartData.length }}</small>
              </div>
            </div>
          </div>

          <div class="col-lg-6">
            <div class="card p-3 mb-4">
              <h6 class="fw-bold">Tỷ Lệ Hoàn Thành Theo Trạng Thái</h6>
              <!-- Placeholder cho Biểu đồ Tròn -->
              <div class="chart-placeholder bg-light rounded text-center text-muted p-5">
                [Placeholder Biểu đồ Tròn: Trạng thái Hoàn thành]
                <small v-if="pieChartData">Hoàn thành: {{ pieChartData.completed }}%, Bỏ: {{ pieChartData.dropped }}%</small>
              </div>
            </div>
            <div class="card p-3">
              <h6 class="fw-bold">Chi Tiết Khóa Học (Tỷ lệ Hoàn thành)</h6>
              <!-- Placeholder cho Biểu đồ Thanh Tiến độ -->
              <div class="chart-placeholder bg-light rounded text-center text-muted p-5">
                [Placeholder Biểu đồ Tiến độ: Tỷ lệ Khóa học]
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- NỘI DUNG TAB ĐĂNG KÝ -->
      <div v-if="activeTab === 'Registration'">
        <div class="card p-3">
          <h6 class="fw-bold mb-3">Chi Tiết Đăng Ký Học Viên Theo Tháng</h6>
          <p class="text-muted small">Thống kê chi tiết về số lượng học viên, tăng trưởng và các khóa học phổ biến nhất.</p>
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0 table-sm"> 
              <thead class="bg-light">
                <tr>
                  <th>Tháng</th>
                  <th>Tổng cộng</th>
                  <th>Thay đổi</th>
                  <th>Khóa học</th>
                  <th>Mới</th>
                  <th>Quay lại</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in registrationDetails" :key="item.month">
                  <td class="fw-bold">{{ item.month }}</td>
                  <td>{{ item.total }}</td>

                  <td
                    class="fw-bold text-center"
                    :class="{
                      'text-success': item.change > 0,
                      'text-danger': item.change < 0,
                      'text-muted': item.change === 0
                    }"
                  >
                    <template v-if="item.change > 0">
                      <!-- Thay thế ion-icon bằng ký tự Unicode '▲' -->
                      <span class="align-middle me-1">▲</span>
                      +{{ item.change.toFixed(1) }}%
                    </template>

                    <template v-else-if="item.change < 0">
                      <!-- Thay thế ion-icon bằng ký tự Unicode '▼' -->
                      <span class="align-middle me-1">▼</span>
                      {{ item.change.toFixed(1) }}%
                    </template>

                    <template v-else>
                      <!-- Thay thế ion-icon bằng ký tự Unicode '—' -->
                      <span class="align-middle me-1">—</span> (0%)
                    </template>
                  </td>

                  <td>
                    <span class="fw-bold">{{ item.course }}</span>
                    <br>
                    <small class="text-muted">{{ item.courseStudents }} học viên</small> 
                  </td>

                  <td class="fw-bold text-primary">{{ item.new }}</td>
                  <td class="text-muted">{{ item.old }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- NỘI DUNG TAB HOÀN THÀNH -->
      <div v-if="activeTab === 'Completion'">
        
        <div class="row g-3 mb-4">
          <div class="col-md-3" v-for="stat in completionStats" :key="stat.title">
            <div class="card h-100 shadow-sm p-3">
              <h6 class="text-muted d-flex align-items-center mb-1">
                <!-- Thay thế ion-icon bằng ký tự Unicode '•' -->
                <span class="me-2 fw-bold" :class="stat.color">•</span>
                {{ stat.title }}
              </h6>
              <h3 class="fw-bold mb-0">{{ stat.value }}</h3>
            </div>
          </div>
        </div>

        <div class="card p-3">
          <h6 class="fw-bold mb-3">Hoàn Thành Khóa Học Chi Tiết</h6>
          <p class="text-muted small">Thông tin chi tiết về tiến độ và hiệu quả của từng khóa học.</p>

          <div class="table-responsive">
            <table class="table align-middle mb-0 table-sm completion-table"> 
              <thead class="bg-light">
                <tr>
                  <th>Khóa học</th>
                  <th>Tổng Học viên</th>
                  <th>Hoàn thành</th>
                  <th>Đang tiến hành</th>
                  <th>Bỏ học</th>
                  <th>Tỷ lệ</th>
                  <th>TG Trung bình</th>
                  <th>Độ khó</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in completionDetails" :key="item.course">
                  <td>
                    <span class="fw-bold">{{ item.course }}</span>
                    <br>
                    <small class="text-muted">Hoạt động: 1 giờ trước</small> 
                  </td>
                  <td class="fw-bold">{{ item.total }}</td>
                  <td class="text-success fw-bold">{{ item.completed }}</td>
                  <td class="text-warning fw-bold">{{ item.inProgress }}</td>
                  <td class="text-danger fw-bold">{{ item.dropped }}</td>
                  <td>
                    <span class="fw-bold me-2">{{ item.rate }}%</span>
                    <div class="progress" style="height: 5px; min-width: 80px;">
                      <div 
                        class="progress-bar bg-dark" 
                        role="progressbar" 
                        :style="{ width: item.rate + '%' }" 
                        :aria-valuenow="item.rate" 
                        aria-valuemin="0" 
                        aria-valuemax="100">
                      </div>
                    </div>
                  </td>
                  <td>{{ item.duration_en }}</td>
                  <td>
                    <span :class="{
                      'badge bg-success-subtle text-success': item.level === 'Basic',
                      'badge bg-warning-subtle text-warning': item.level === 'Intermediate',
                      'badge bg-danger-subtle text-danger': item.level === 'Advanced'
                    }">{{ item.level }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- NỘI DUNG TAB ĐIỂM SỐ -->
      <div v-if="activeTab === 'Scores'" class="mb-4">
        
        <div class="row g-3 mb-4">
          <div class="col-md-3" v-for="stat in scoreStats" :key="stat.title">
            <div class="card h-100 shadow-sm p-3">
              <h6 class="text-muted d-flex align-items-center mb-1">
                <!-- Thay thế ion-icon bằng ký tự Unicode '•' -->
                <span class="me-2 fw-bold" :class="stat.color">•</span>
                {{ stat.title }}
              </h6>
              <h3 class="fw-bold mb-0">{{ stat.value }}</h3>
            </div>
          </div>
        </div>
        
        <div class="score-toggle-wrapper mb-4">
            <button 
                class="score-toggle-btn" 
                :class="{ active: activeScoreTab === 'Quiz Detail' }"
                @click="activeScoreTab = 'Quiz Detail'"
            >
              Chi tiết Quiz
            </button>
            <button 
                class="score-toggle-btn" 
                :class="{ active: activeScoreTab === 'Lab Detail' }"
                @click="activeScoreTab = 'Lab Detail'"
            >
              Chi tiết Lab
            </button>
        </div>

        <!-- CHI TIẾT QUIZ -->
        <div v-if="activeScoreTab === 'Quiz Detail'" class="card p-3">
          <h6 class="fw-bold mb-3">Chi Tiết Hiệu Suất Quiz Theo Khóa Học</h6>
          <p class="text-muted small">Phân tích chi tiết về điểm trung bình, tỷ lệ hoàn thành và dữ liệu xu hướng cho các bài quiz.</p>

          <div class="table-responsive">
            <table class="table align-middle mb-0 table-sm score-table"> 
              <thead class="bg-light">
                <tr>
                  <th>Khóa học</th>
                  <th>Số Quiz</th>
                  <th>Điểm trung bình</th>
                  <th>Cao/Thấp</th>
                  <th>Tỷ lệ hoàn thành</th>
                  <th>Xu hướng</th>
                  <th>Cập nhật gần nhất</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in scoreDetails" :key="item.course">
                  <td>
                    <span class="fw-bold">{{ item.course }}</span>
                    <br>
                    <small class="text-muted">{{ item.students }} học viên</small> 
                  </td>
                  <td class="fw-bold">{{ item.numQuizzes }}</td>
                  <td 
                    class="fw-bold"
                    :class="{
                      'text-success': item.avgScore > 8,
                      'text-warning': item.avgScore >= 5 && item.avgScore < 8,
                      'text-danger': item.avgScore < 5
                    }"
                  >
                    {{ item.avgScore.toFixed(1) }}/10
                  </td>
                  <td>
                      <small>Cao: {{ item.maxScore.toFixed(1) }}</small>
                      <br>
                      <small class="text-muted">Thấp: {{ item.minScore.toFixed(1) }}</small>
                  </td>
                  <td>
                    <span class="fw-bold me-2">{{ item.completionRate }}%</span>
                    <div class="progress" style="height: 5px; min-width: 80px;">
                      <div 
                        class="progress-bar bg-dark" 
                        role="progressbar" 
                        :style="{ width: item.completionRate + '%' }" 
                        :aria-valuenow="item.completionRate" 
                        aria-valuemin="0" 
                        aria-valuemax="100">
                      </div>
                    </div>
                  </td>
                  <td 
                    class="fw-bold"
                    :class="{
                      'text-success': item.trend > 0,
                      'text-danger': item.trend < 0,
                      'text-muted': item.trend === 0
                    }"
                  >
                    <template v-if="item.trend > 0">
                      <!-- Thay thế ion-icon bằng ký tự Unicode '▲' -->
                      <span class="align-middle me-1">▲</span>
                      +{{ item.trend.toFixed(1) }}
                    </template>
                    <template v-else-if="item.trend < 0">
                      <!-- Thay thế ion-icon bằng ký tự Unicode '▼' -->
                      <span class="align-middle me-1">▼</span>
                      {{ item.trend.toFixed(1) }}
                    </template>
                    <template v-else>
                      —
                    </template>
                  </td>
                  <td class="text-muted">{{ item.lastUpdate }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- CHI TIẾT LAB -->
        <div v-if="activeScoreTab === 'Lab Detail'" class="card p-3">
          <h6 class="fw-bold mb-3">Chi Tiết Hiệu Suất Lab Theo Khóa Học</h6>
          <p class="text-muted small">Phân tích chi tiết về điểm lab, tỷ lệ hoàn thành, thời gian trung bình và độ khó.</p>

          <div class="table-responsive">
            <table class="table align-middle mb-0 table-sm score-table"> 
              <thead class="bg-light">
                <tr>
                  <th>Khóa học</th>
                  <th>Số Lab</th>
                  <th>Điểm trung bình</th>
                  <th>Cao/Thấp</th>
                  <th>Tỷ lệ hoàn thành</th>
                  <th>Thời gian TB</th>
                  <th>Độ khó</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in labDetails" :key="item.course">
                  <td>
                    <span class="fw-bold">{{ item.course }}</span>
                    <br>
                    <small class="text-muted">{{ item.students }} học viên</small> 
                  </td>
                  <td class="fw-bold">{{ item.numLabs }}</td>
                  <td 
                    class="fw-bold"
                    :class="{
                      'text-success': item.avgScore >= 8,
                      'text-warning': item.avgScore >= 5 && item.avgScore < 8,
                      'text-danger': item.avgScore < 5
                    }"
                  >
                    {{ item.avgScore.toFixed(1) }}/10
                  </td>
                  <td>
                      <small>Cao: {{ item.maxScore.toFixed(1) }}</small>
                      <br>
                      <small class="text-muted">Thấp: {{ item.minScore.toFixed(1) }}</small>
                  </td>
                  <td>
                    <span class="fw-bold me-2">{{ item.completionRate }}%</span>
                    <div class="progress" style="height: 5px; min-width: 80px;">
                      <div 
                        class="progress-bar bg-dark" 
                        role="progressbar" 
                        :style="{ width: item.completionRate + '%' }" 
                        :aria-valuenow="item.completionRate" 
                        aria-valuemin="0" 
                        aria-valuemax="100">
                      </div>
                    </div>
                  </td>
                  <td>{{ item.avgDuration_en }}</td>
                  <td>
                    <span :class="{
                      'badge bg-success-subtle text-success': item.level === 'Basic',
                      'badge bg-warning-subtle text-warning': item.level === 'Intermediate',
                      'badge bg-danger-subtle text-danger': item.level === 'Advanced'
                    }">{{ item.level }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "InstructorReports",

  data() {
    return {
      // UI State
      activeTab: "Overview",
      tabs: ["Overview", "Registration", "Completion", "Scores"],
      activeScoreTab: "Quiz Detail",
      isLoading: true,
      error: null, 
      isMockData: false, // Thêm cờ để báo hiệu dữ liệu giả lập

      // Dashboard Data (Bắt đầu với dữ liệu trống)
      statCards: [],
      completionStats: [],
      scoreStats: [],
      registrationDetails: [],
      completionDetails: [],
      scoreDetails: [],
      labDetails: [],

      // Dữ liệu Biểu đồ (Bắt đầu với giá trị null)
      lineChartData: null, 
      pieChartData: null,
      completionChartData: null,
      scoreChartData: null,
    };
  },

  mounted() {
    this.fetchDashboardData();
  },

  methods: {
    /**
     * Cung cấp dữ liệu giả lập (mock data) đầy đủ cho dashboard.
     */
    _getMockData() {
        return {
            statCards: [
                { title: 'Tổng Học Viên', value: '4,521', change: 12.5, note: 'so với tháng trước', color: 'text-success' },
                { title: 'Khóa Học Đang Hoạt Động', value: '18', change: 0, note: 'không đổi', color: 'text-muted' },
                { title: 'Tỷ Lệ Hoàn Thành TB', value: '78.9%', change: 5.1, note: 'tăng', color: 'text-success' },
                { title: 'Điểm Lab TB', value: '8.4/10', change: -1.2, note: 'giảm', color: 'text-danger' },
            ],
            completionStats: [
                { title: 'Hoàn Thành', value: '78.9%', color: 'text-success' },
                { title: 'Đang Tiến Hành', value: '15.3%', color: 'text-warning' },
                { title: 'Bỏ Học', value: '5.8%', color: 'text-danger' },
                { title: 'Quiz Đã Làm', value: '2,150', color: 'text-dark' },
            ],
            scoreStats: [
                { title: 'Điểm Quiz TB', value: '7.2/10', color: 'text-warning' },
                { title: 'Điểm Lab TB', value: '8.4/10', color: 'text-success' },
                { title: 'Tỷ Lệ Qua Môn', value: '85%', color: 'text-success' },
                { title: 'Lab Đã Hoàn Thành', value: '95%', color: 'text-success' },
            ],
            registrationDetails: [
                { month: 'Tháng 9', total: 4521, change: 12.5, course: 'Phân tích Dữ liệu', courseStudents: 850, new: 120, old: 330 },
                { month: 'Tháng 8', total: 4018, change: 5.1, course: 'Mã hóa Python', courseStudents: 780, new: 105, old: 295 },
                { month: 'Tháng 7', total: 3820, change: -2.3, course: 'Thiết kế UX/UI', courseStudents: 650, new: 90, old: 250 },
                { month: 'Tháng 6', total: 3910, change: 8.8, course: 'Kỹ sư Cloud', courseStudents: 550, new: 150, old: 300 },
            ],
            completionDetails: [
                { course: 'Phân tích Dữ liệu', total: 500, completed: 420, inProgress: 50, dropped: 30, rate: 84, duration_en: '21 days', level: 'Intermediate' },
                { course: 'Mã hóa Python', total: 650, completed: 500, inProgress: 100, dropped: 50, rate: 76.9, duration_en: '30 days', level: 'Basic' },
                { course: 'Thiết kế UX/UI', total: 300, completed: 210, inProgress: 80, dropped: 10, rate: 70, duration_en: '15 days', level: 'Advanced' },
                { course: 'Kỹ sư Cloud', total: 400, completed: 380, inProgress: 15, dropped: 5, rate: 95, duration_en: '45 days', level: 'Advanced' },
            ],
            scoreDetails: [
                { course: 'Phân tích Dữ liệu', students: 500, numQuizzes: 12, avgScore: 8.5, maxScore: 10, minScore: 4.5, completionRate: 92, trend: 0.2, lastUpdate: '1 giờ trước' },
                { course: 'Mã hóa Python', students: 650, numQuizzes: 8, avgScore: 6.8, maxScore: 9.5, minScore: 3.0, completionRate: 85, trend: -0.5, lastUpdate: '3 giờ trước' },
                { course: 'Thiết kế UX/UI', students: 300, numQuizzes: 15, avgScore: 7.9, maxScore: 10, minScore: 5.5, completionRate: 98, trend: 0.1, lastUpdate: '2 ngày trước' },
            ],
            labDetails: [
                { course: 'Phân tích Dữ liệu', students: 500, numLabs: 6, avgScore: 9.1, maxScore: 10, minScore: 6.5, completionRate: 98, avgDuration_en: '4 hours', level: 'Intermediate' },
                { course: 'Mã hóa Python', students: 650, numLabs: 4, avgScore: 7.5, maxScore: 9.0, minScore: 5.0, completionRate: 90, avgDuration_en: '3 hours', level: 'Basic' },
                { course: 'Thiết kế UX/UI', students: 300, numLabs: 7, avgScore: 8.8, maxScore: 10, minScore: 7.0, completionRate: 95, avgDuration_en: '6 hours', level: 'Advanced' },
            ],
            lineChartData: { datasets: [{ data: [1, 2, 3, 4, 5] }] },
            pieChartData: { completed: 78.9, dropped: 5.8 },
            scoreChartData: ['Data Analysis', 'Python Coding', 'UX/UI Design'],
        };
    },

    /**
     * Hàm trợ giúp để cập nhật an toàn tất cả các thuộc tính dữ liệu từ đối tượng phản hồi.
     * @param {Object} data - Đối tượng phản hồi API chứa tất cả dữ liệu dashboard.
     */
    _updateDataFromResponse(data) {
        this.statCards = data.statCards || [];
        this.completionStats = data.completionStats || [];
        this.scoreStats = data.scoreStats || [];
        this.registrationDetails = data.registrationDetails || [];
        this.completionDetails = data.completionDetails || [];
        this.scoreDetails = data.scoreDetails || [];
        this.labDetails = data.labDetails || [];
        
        this.lineChartData = data.lineChartData || null;
        this.pieChartData = data.pieChartData || null;
        this.completionChartData = data.completionChartData || null;
        this.scoreChartData = data.scoreChartData || null;
    },

    /**
     * Tìm nạp dữ liệu từ API backend với logic thử lại, đã bao gồm header xác thực.
     */
    async fetchDashboardData() {
      this.isLoading = true;
      this.error = null;
      this.isMockData = false;
      const API_URL = '/api/instructor/dashboard'; 
      const MAX_RETRIES = 3;

      const placeholderToken = 'REPLACE_WITH_YOUR_ACTUAL_AUTH_TOKEN';
      // CHỈNH SỬA: Lấy token thực tế của bạn
      const yourAuthToken = placeholderToken; 
      let loadSuccess = false;

      for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
        try {
          // 1. Thực hiện tìm nạp VỚI HEADERS XÁC THỰC
          const response = await fetch(API_URL, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${yourAuthToken}`, 
                'Content-Type': 'application/json'
            }
          });
          
          console.log(`API Response Status: ${response.status} cho URL: ${API_URL}`);

          const contentType = response.headers.get('content-type');

          if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Lỗi 401: Unauthorized. Vui lòng kiểm tra Token xác thực.');
            }
            throw new Error(`Lỗi HTTP! Trạng thái: ${response.status} cho URL: ${API_URL}`);
          }
          
          if (!contentType || !contentType.includes('application/json')) {
              // Lỗi này xảy ra nếu server trả về HTML (ví dụ: lỗi 500 hoặc trang đăng nhập)
              throw new Error(`Loại phản hồi không hợp lệ: Dự kiến JSON nhưng nhận được ${contentType || 'không có loại nội dung'} (Lỗi này thường do server hoặc xác thực không thành công).`);
          }

          const apiResponse = await response.json();

          // 2. Thành công: Cập nhật dữ liệu và thoát
          this._updateDataFromResponse(apiResponse);
          loadSuccess = true;
          console.log(`Dữ liệu dashboard được tải thành công từ API: ${API_URL}`);
          return; 

        } catch (error) {
            console.error(`Lần tìm nạp API ${attempt + 1} thất bại cho ${API_URL}:`, error.message);
            
            // 3. Xử lý thử lại hoặc thất bại cuối cùng
            if (attempt < MAX_RETRIES - 1) {
                const delay = Math.pow(2, attempt) * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            } else {
                // Thất bại cuối cùng
                if (yourAuthToken === placeholderToken) {
                    // Nếu lỗi và vẫn dùng placeholder token, tải dữ liệu giả lập
                    this.error = `API thất bại: ${error.message}. Đã chuyển sang dữ liệu giả lập.`;
                    this._updateDataFromResponse(this._getMockData());
                    this.isMockData = true;
                } else {
                    // Lỗi thật sau khi đã dùng token thật
                    this.error = `Không thể tải dữ liệu từ ${API_URL} sau ${MAX_RETRIES} lần thử. Lỗi cuối cùng: ${error.message}`;
                    this._updateDataFromResponse({});
                }
                break; 
            }
        }
      }
      this.isLoading = false;
    },
  }
}
</script>

<style scoped>
/* Bootstrap utility class for screen reader content */
.visually-hidden {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

/* New style for the loading spinner */
.spinner-border {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  vertical-align: -0.125em;
  border: 0.25em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: .75s linear infinite spinner-border;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}

/* Style for chart placeholders */
.chart-placeholder {
    height: 200px; /* Standard chart height */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    color: #94a3b8;
    border: 1px dashed #cbd5e1;
}

.dashboard-wrapper {
  background: #fff;
  min-height: 100vh;
}
.card {
  border-radius: 12px;
  border: 1px solid #eee;
}

/* ------------------------------------------------------------------- */
/* NAVIGATION TAB EFFECTS */
.nav-pills .nav-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: auto;
  min-width: 306px; 
  height: 40px;
  border-radius: 8px;
  color: #6b7280;
  text-decoration: none;
  font-weight: 600;
  background-color: #f1f5f9;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  margin-right: 10px;
}
/* Hover Effect */
.nav-pills .nav-link:hover {
  color: #111;
  background-color: #e2e8f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}
/* Active Effect*/
.nav-pills .nav-link.active {
  background-color: #111;
  color: #fff;
  transform: none; 
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* SCORE TOGGLE STYLES */
.score-toggle-wrapper {
    display: flex;
    justify-content: flex-start;
    padding: 6px;
    background-color: #f1f5f9;
    border-radius: 10px;
    width: 100%;
}

.score-toggle-btn {
    padding: 8px 15px;
    border: none;
    border-radius: 8px;
    background-color: transparent;
    color: #6b7280;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    flex-grow: 1;
    min-width: 150px;
}

.score-toggle-btn.active {
    background-color: #fff;
    color: #111;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}


/* Table Styles */
.completion-table th, .completion-table td {
  border-bottom: 1px solid #e9ecef !important;
}

.completion-table tbody tr:last-child td {
  border-bottom: none !important;
}

.completion-table .progress {
  background-color: #e9ecef;
}

.score-table th, .score-table td {
  border-bottom: 1px solid #e9ecef !important;
}

.score-table tbody tr:last-child td {
  border-bottom: none !important;
}

.score-table .progress {
  background-color: #e9ecef;
}


/* Badge Styles (Difficulty) */
.badge {
  padding: 0.5em 0.75em;
  border-radius: 0.5rem;
  font-weight: 600;
}
/* Subtle color classes for badges */
.bg-success-subtle {
  background-color: #d1e7dd !important; 
  color: #0f5132 !important;
}
.bg-warning-subtle {
  background-color: #fff3cd !important;
  color: #664d03 !important;
}
.bg-danger-subtle {
  background-color: #f8d7da !important;
  color: #842029 !important;
}

/* Custom error alert style */
.alert-danger {
  border: 1px solid #f5c2c7;
  background-color: #f8d7da;
  color: #842029;
  border-radius: 12px;
}
.alert-warning {
  border: 1px solid #ffecb5;
  background-color: #fff3cd;
  color: #664d03;
  border-radius: 12px;
}
</style>
