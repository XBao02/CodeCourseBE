<template>
  <div class="admin-dashboard">
    <div class="dashboard-wrapper">

      <!-- Header -->
      <div class="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>Overview of platform performance and statistics</p>
      </div>

      <!-- Overview Cards -->
      <div class="stats-grid">
        <div class="stat-card" v-for="card in overviewCards" :key="card.title">
          <h6>{{ card.title }}</h6>
          <h3>{{ card.value }}</h3>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-grid">
        <!-- New Registrations -->
        <div class="chart-card">
          <h5>New Registrations</h5>
          <div class="chart-placeholder">
            <p>Line Chart — User registrations over time</p>
          </div>
        </div>

        <!-- Completion Rate -->
        <div class="chart-card">
          <h5>Course Completion Rate</h5>
          <div class="course-progress-list">
            <div v-for="course in courseCompletion" :key="course.id" class="progress-item">
              <div class="progress-header">
                <span class="course-name">{{ course.name }}</span>
                <span class="progress-text">{{ course.completionRate }}% ({{ course.totalStudents }} students)</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" :style="{ width: course.completionRate + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Revenue Section -->
      <div class="charts-grid">
        <!-- Monthly Revenue -->
        <div class="chart-card">
          <h5>Revenue by Month</h5>
          <div class="chart-placeholder">
            <p>Bar Chart — Monthly revenue trend</p>
          </div>
        </div>

        <!-- Revenue by Course -->
        <div class="chart-card">
          <h5>Revenue by Course</h5>
          <div class="revenue-list">
            <div v-for="course in revenueByCourse" :key="course.id" class="revenue-item">
              <span class="course-name">{{ course.name }}</span>
              <span class="revenue-value">${{ course.revenue }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: "AdminDashboard",
  data() {
    return {
      overviewCards: [
        { title: "Total Users", value: 1547, icon: "bi bi-people-fill", color: "primary" },
        { title: "Active Courses", value: 58, icon: "bi bi-journal-code", color: "success" },
        { title: "Total Revenue", value: "$25,000", icon: "bi bi-cash-coin", color: "info" },
      ],
      courseCompletion: [
        { id: 1, name: "Advanced Web Programming", completionRate: 72, totalStudents: 45 },
        { id: 2, name: "Data Structures & Algorithms", completionRate: 65, totalStudents: 32 },
        { id: 3, name: "React Native Mobile Dev", completionRate: 85, totalStudents: 28 },
        { id: 4, name: "Intro to Python", completionRate: 78, totalStudents: 49 },
      ],
      revenueByCourse: [
        { id: 1, name: "Advanced Web Programming", revenue: "8,500" },
        { id: 2, name: "Data Structures & Algorithms", revenue: "6,200" },
        { id: 3, name: "React Native Mobile Dev", revenue: "5,300" },
        { id: 4, name: "Intro to Python", revenue: "5,000" },
      ],
    };
  },
};
</script>

<style scoped>
.admin-dashboard {
  background: #f8f9fa;
  min-height: 100vh;
  padding: 40px;
}

.dashboard-wrapper {
  max-width: 1400px;
  margin: 0 auto;
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

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  padding: 28px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.chart-card h5 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 24px 0;
}

.chart-placeholder {
  background: #f8f9fa;
  border: 2px dashed #e5e7eb;
  border-radius: 6px;
  padding: 40px 20px;
  text-align: center;
}

.chart-placeholder p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.course-progress-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
}

.progress-text {
  font-size: 13px;
  color: #666;
}

.progress-bar-container {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #1f2937, #374151);
  transition: width 0.3s ease;
}

.revenue-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.revenue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e5e7eb;
}

.revenue-item:last-child {
  border-bottom: none;
}

.revenue-value {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 20px;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
