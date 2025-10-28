<template>
  <div class="dashboard-wrapper p-4">
    <!-- Header -->
    <h2 class="fw-bold mb-2">Dashboard Instructor - Báo Cáo & Thống Kê</h2>
    <p class="text-muted mb-4">Theo dõi hiệu suất và tiến độ học tập của học viên trong các khóa lập trình</p>

    <!-- Top Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-3" v-for="card in statCards" :key="card.title">
        <div class="card h-100 shadow-sm p-3">
          <h6 class="text-muted">{{ card.title }}</h6>
          <h3 class="fw-bold">{{ card.value }}</h3>
          <small :class="{ 'text-success': card.change > 0, 'text-danger': card.change < 0 }">
            {{ card.change > 0 ? '+' : '' }}{{ card.change }}% {{ card.note }}
          </small>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-pills mb-4">
      <li class="nav-item" v-for="tab in tabs" :key="tab">
        <button class="nav-link" :class="{ active: activeTab === tab }" @click="activeTab = tab">{{ tab }}</button>
      </li>
    </ul>

    <!-- Charts & Reports -->
    <div v-if="activeTab === 'Tổng Quan'">
      <div class="row g-4 mb-4">
        <!-- Line chart -->
        <div class="col-lg-6">
          <div class="card p-3">
            <h6 class="fw-bold">Số Lượng Học Viên Đăng Ký Theo Thời Gian</h6>
            <line-chart :data="lineChartData"></line-chart>
          </div>
        </div>
        <!-- Pie chart -->
        <div class="col-lg-6">
          <div class="card p-3">
            <h6 class="fw-bold">Tổng Quan Tỷ Lệ Hoàn Thành</h6>
            <pie-chart :data="pieChartData"></pie-chart>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Progress bars -->
        <div class="col-lg-6">
          <div class="card p-3">
            <h6 class="fw-bold">Chi Tiết Theo Khóa Học</h6>
            <div v-for="course in courseProgress" :key="course.name" class="mb-2">
              <div class="d-flex justify-content-between">
                <span>{{ course.name }}</span>
                <span>{{ course.done }}/{{ course.total }} ({{ course.percent }}%)</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-primary" :style="{ width: course.percent + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
        <!-- Bar chart -->
        <div class="col-lg-6">
          <div class="card p-3">
            <h6 class="fw-bold">Điểm Trung Bình Quiz & Lab</h6>
            <bar-chart :data="barChartData"></bar-chart>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Giả sử bạn tạo sẵn 3 component LineChart, PieChart, BarChart dùng Chart.js hoặc Recharts
import LineChart from "../Instructor/BarChart.vue";
import PieChart from "../Instructor/PieChart.vue";
import BarChart from "../Instructor/LineChart.vue";
export default {
  name: "InstructorReports",
  data() {
    return {
      activeTab: "Tổng Quan",
      tabs: ["Tổng Quan", "Đăng Ký", "Hoàn Thành", "Điểm Số"],
      statCards: [
        { title: "Tổng Học Viên", value: "1,247", change: 12.5, note: "So với tháng trước" },
        { title: "Khóa Học Đang Hoạt Động", value: "15", change: 2, note: "Khóa học mới được mở" },
        { title: "Tỷ Lệ Hoàn Thành Trung Bình", value: "68%", change: 5.2, note: "Cải thiện so với quý trước" },
        { title: "Điểm Trung Bình", value: "8.1/10", change: 0.3, note: "Trên tất cả bài kiểm tra" }
      ],
      lineChartData: [45, 55, 60, 58, 70, 72, 80, 90, 100, 115, 120, 118],
      pieChartData: { completed: 68, dropped: 7, inProgress: 25 },
      barChartData: [
        { label: "JavaScript", quiz: 8, lab: 7 },
        { label: "React", quiz: 7.5, lab: 7 },
        { label: "Node.js", quiz: 6.8, lab: 6.5 },
        { label: "Python", quiz: 8.5, lab: 8 },
        { label: "Database", quiz: 7.2, lab: 6.9 },
      ],
      courseProgress: [
        { name: "JavaScript Cơ Bản", done: 102, total: 120, percent: 85 },
        { name: "React Framework", done: 71, total: 98, percent: 72 },
        { name: "Node.js Backend", done: 49, total: 85, percent: 58 },
        { name: "Python Programming", done: 100, total: 110, percent: 91 },
        { name: "Database Design", done: 47, total: 75, percent: 63 }
      ]
    }
  }
}
</script>

<style scoped>
.dashboard-wrapper {
  background: #fff;
  min-height: 100vh;
}

.card {
  border-radius: 12px;
  border: 1px solid #eee;
}

.nav-pills .nav-link.active {
  background-color: #111;
}
</style>
