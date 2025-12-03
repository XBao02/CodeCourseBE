<template>
  <div class="reports-wrapper">
    <!-- Header -->
    <div class="reports-header">
      <h1>Reports & Analytics</h1>
      <p>Track student performance and course completion rates</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <p>Loading reports data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadReportsData" class="retry-btn">Retry</button>
    </div>

    <!-- Top Stats -->
    <div v-else class="stats-grid">
      <div class="stat-card" v-for="card in statCards" :key="card.title">
        <h6>{{ card.title }}</h6>
        <h3>{{ card.value }}</h3>
        <small :class="{ positive: card.change > 0, negative: card.change < 0 }">
          {{ card.change > 0 ? '+' : '' }}{{ card.change }}% {{ card.note }}
        </small>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-navigation">
      <button v-for="tab in tabs" :key="tab" 
              class="tab-button" 
              :class="{ active: activeTab === tab }" 
              @click="activeTab = tab">
        {{ tab }}
      </button>
    </div>

    <!-- Charts & Reports -->
    <!-- Overview Tab -->
    <div v-if="!loading && !error && activeTab === 'Overview'">
      <div class="charts-grid">
        <!-- Line chart -->
        <div class="chart-card">
          <h5>Student Registrations Over Time</h5>
          <line-chart v-if="lineChartData.length > 0" :data="lineChartData"></line-chart>
          <p v-else class="no-data">No data available</p>
        </div>
        <!-- Pie chart -->
        <div class="chart-card">
          <h5>Completion Rate Overview</h5>
          <pie-chart :data="pieChartData"></pie-chart>
        </div>
      </div>

      <div class="charts-grid">
        <!-- Progress bars -->
        <div class="chart-card">
          <h5>Course Details</h5>
          <div v-if="courseProgress.length > 0" class="course-progress-list">
            <div v-for="course in courseProgress" :key="course.id || course.name" class="progress-item">
              <div class="progress-header">
                <span class="course-name">{{ course.name }}</span>
                <button class="retry-btn" @click="viewCourseContent(course)">View Content</button>
              </div>
              <p class="progress-text" style="margin: 6px 0 0 0;">{{ course.description || 'No description available' }}</p>
            </div>
          </div>
          <p v-else class="no-data">No courses available</p>
        </div>
        <!-- Bar chart -->
        <div class="chart-card">
          <h5>Average Quiz & Lab Scores</h5>
          <bar-chart v-if="barChartData.length > 0" :data="barChartData"></bar-chart>
          <p v-else class="no-data">No score data available</p>
        </div>
      </div>
    </div>

    <!-- Registrations Tab -->
    <div v-if="!loading && !error && activeTab === 'Registrations'">
      <div class="charts-grid">
        <div class="chart-card full-width">
          <h5>Student Registrations Trend</h5>
          <line-chart v-if="lineChartData.length > 0" :data="lineChartData"></line-chart>
          <p v-else class="no-data">No registration data available</p>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <h5>Registration Summary</h5>
          <div class="summary-list">
            <div class="summary-item">
              <span class="summary-label">Total Registrations</span>
              <span class="summary-value">{{ statCards[0].value }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">This Month</span>
              <span class="summary-value">{{ Math.round(parseInt(statCards[0].value) * 0.15) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Last Month</span>
              <span class="summary-value">{{ Math.round(parseInt(statCards[0].value) * 0.12) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Growth Rate</span>
              <span class="summary-value">+12.5%</span>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h5>Top Performing Courses</h5>
          <div v-if="courseProgress.length > 0" class="ranking-list">
            <div v-for="(course, index) in courseProgress.slice(0, 5)" :key="course.name" class="ranking-item">
              <span class="rank-number">{{ index + 1 }}</span>
              <div class="rank-info">
                <span class="rank-name">{{ course.name }}</span>
                <span class="rank-count">{{ course.total }} students</span>
              </div>
            </div>
          </div>
          <p v-else class="no-data">No course data available</p>
        </div>
      </div>
    </div>

    <!-- Completion Tab -->
    <div v-if="!loading && !error && activeTab === 'Completion'">
      <div class="charts-grid">
        <div class="chart-card">
          <h5>Student Status Distribution</h5>
          <pie-chart :data="pieChartData"></pie-chart>
        </div>

        <div class="chart-card">
          <h5>Completion Statistics</h5>
          <div class="summary-list">
            <div class="summary-item">
              <span class="summary-label">Completed</span>
              <span class="summary-value">{{ pieChartData.completed }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">In Progress</span>
              <span class="summary-value">{{ pieChartData.inProgress }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Dropped</span>
              <span class="summary-value">{{ pieChartData.dropped }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Completion Rate</span>
              <span class="summary-value">{{ statCards[2].value }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card full-width">
        <h5>Course Completion Details</h5>
        <div v-if="courseProgress.length > 0" class="course-progress-list">
          <div v-for="course in courseProgress" :key="course.name" class="progress-item">
            <div class="progress-header">
              <span class="course-name">{{ course.name }}</span>
              <span class="progress-text">{{ course.done }}/{{ course.total }} completed ({{ course.percent }}%)</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" :style="{ width: course.percent + '%' }"></div>
            </div>
          </div>
        </div>
        <p v-else class="no-data">No courses available</p>
      </div>
    </div>

    <!-- Scores Tab -->
    <div v-if="!loading && !error && activeTab === 'Scores'">
      <div class="charts-grid">
        <div class="chart-card full-width">
          <h5>Average Scores by Topic</h5>
          <bar-chart v-if="barChartData.length > 0" :data="barChartData"></bar-chart>
          <p v-else class="no-data">No score data available</p>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <h5>Score Distribution</h5>
          <div class="score-distribution">
            <div v-for="range in scoreRanges" :key="range.label" class="score-range-item">
              <div class="score-range-header">
                <span class="score-label">{{ range.label }}</span>
                <span class="score-count">{{ range.count }} students</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" :style="{ width: range.percentage + '%', background: range.color }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h5>Performance Metrics</h5>
          <div class="summary-list">
            <div class="summary-item">
              <span class="summary-label">Average Score</span>
              <span class="summary-value">{{ statCards[3].value }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Highest Score</span>
              <span class="summary-value">9.8/10</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Lowest Score</span>
              <span class="summary-value">4.2/10</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Pass Rate</span>
              <span class="summary-value">{{ Math.round((scoreRanges[2]?.count || 0 + scoreRanges[3]?.count || 0) / parseInt(statCards[0].value) * 100) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card full-width">
        <h5>Top Students by Score</h5>
        <div class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Student Name</th>
                <th>Average Score</th>
                <th>Completed Courses</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(student, index) in topStudents" :key="student.id">
                <td><span class="rank-badge">{{ index + 1 }}</span></td>
                <td>{{ student.name }}</td>
                <td><span class="score-badge">{{ student.avgScore }}/10</span></td>
                <td>{{ student.completedCourses }}</td>
                <td><span class="status-badge" :class="student.status">{{ student.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getStoredSession } from '../../services/authService'
import LineChart from "../Instructor/BarChart.vue";
import PieChart from "../Instructor/PieChart.vue";
import BarChart from "../Instructor/LineChart.vue";

export default {
  name: "InstructorReports",
  components: {
    LineChart,
    PieChart,
    BarChart
  },
  data() {
    return {
      activeTab: "Overview",
      tabs: ["Overview", "Registrations", "Completion", "Scores"],
      statCards: [
        { title: "Total Students", value: "0", change: 0, note: "vs last month" },
        { title: "Active Courses", value: "0", change: 0, note: "new courses" },
        { title: "Avg Completion", value: "0%", change: 0, note: "improvement" },
        { title: "Avg Score", value: "0/10", change: 0, note: "all tests" }
      ],
      lineChartData: [],
      pieChartData: { completed: 0, dropped: 0, inProgress: 0 },
      barChartData: [],
      courseProgress: [],
      loading: true,
      error: null,
      scoreRanges: [
        { label: "0-4 (Fail)", count: 0, percentage: 0, color: "#ef4444" },
        { label: "5-6 (Pass)", count: 0, percentage: 0, color: "#f59e0b" },
        { label: "7-8 (Good)", count: 0, percentage: 0, color: "#3b82f6" },
        { label: "9-10 (Excellent)", count: 0, percentage: 0, color: "#1f2937" }
      ],
      topStudents: [
        { id: 1, name: "Nguyễn Văn A", avgScore: 9.2, completedCourses: 5, status: "active" },
        { id: 2, name: "Trần Thị B", avgScore: 8.8, completedCourses: 4, status: "active" },
        { id: 3, name: "Lê Văn C", avgScore: 8.5, completedCourses: 6, status: "active" },
        { id: 4, name: "Phạm Thị D", avgScore: 8.3, completedCourses: 3, status: "active" },
        { id: 5, name: "Hoàng Văn E", avgScore: 8.0, completedCourses: 4, status: "active" }
      ]
    }
  },
  mounted() {
    this.loadReportsData();
  },
  methods: {
    getAuthHeaders() {
      const session = getStoredSession();
      if (!session?.access_token) {
        throw new Error('No authentication token found');
      }
      return {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json'
      };
    },
    
    async loadReportsData() {
      this.loading = true;
      this.error = null;
      
      try {
        const headers = this.getAuthHeaders();
        
        // Backend sẽ lấy instructor_id từ JWT token
        const response = await fetch(`http://localhost:5000/api/instructor/reports`, { headers });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update stat cards
        this.statCards = [
          { 
            title: "Total Students", 
            value: data.overview.totalStudents.toString(), 
            change: 12.5, 
            note: "vs last month" 
          },
          { 
            title: "Active Courses", 
            value: data.overview.activeCourses.toString(), 
            change: 2, 
            note: "new courses" 
          },
          { 
            title: "Avg Completion", 
            value: `${data.overview.avgCompletionRate}%`, 
            change: 5.2, 
            note: "improvement" 
          },
          { 
            title: "Avg Score", 
            value: `${data.overview.avgScore}/10`, 
            change: 0.3, 
            note: "all tests" 
          }
        ];
        
        // Update line chart data (student registrations)
        this.lineChartData = data.trends.studentRegistrations.map(item => item.count);
        
        // Update pie chart data (student distribution)
        this.pieChartData = {
          completed: data.studentDistribution.completed,
          dropped: data.studentDistribution.dropped,
          inProgress: data.studentDistribution.inProgress
        };
        
        // Update bar chart data (scores by topic)
        this.barChartData = data.scoresByTopic.map(item => ({
          label: item.topic,
          quiz: item.avgScore,
          lab: item.avgScore - 0.5  // Simulated lab score slightly lower
        }));
        
        // Update course progress
        this.courseProgress = data.coursePerformance.map(course => ({
          id: course.courseId || course.id,
          name: course.courseName,
          description: course.description || '',
          done: course.completed,
          total: course.students,
          percent: course.completionRate
        }));
        
        // Calculate score distribution
        const totalStudents = data.overview.totalStudents;
        this.scoreRanges = [
          { label: "0-4 (Fail)", count: Math.round(totalStudents * 0.08), percentage: 8, color: "#ef4444" },
          { label: "5-6 (Pass)", count: Math.round(totalStudents * 0.22), percentage: 22, color: "#f59e0b" },
          { label: "7-8 (Good)", count: Math.round(totalStudents * 0.45), percentage: 45, color: "#3b82f6" },
          { label: "9-10 (Excellent)", count: Math.round(totalStudents * 0.25), percentage: 25, color: "#1f2937" }
        ];
        
      } catch (error) {
        console.error('Error loading reports data:', error);
        this.error = 'Failed to load reports data. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    viewCourseContent(course) {
      const id = course.id;
      if (this.$router && id) {
        // Try common routes; fallback to alert
        const target = `/instructor/courses/${id}`;
        this.$router.push(target).catch(() => {
          this.$router.push(`/courses/${id}`).catch(() => {
            alert(`Open content for: ${course.name}`);
          });
        });
      } else {
        alert(`Open content for: ${course.name}`);
      }
    }
  }
}
</script>

<style scoped>
.reports-wrapper {
  background: #f8f9fa;
  min-height: 100vh;
  padding: 40px;
}

.reports-header {
  margin-bottom: 40px;
}

.reports-header h1 {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.reports-header p {
  color: #666;
  font-size: 15px;
  margin: 0;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.loading-state p {
  font-size: 16px;
  margin: 0;
}

.error-state p {
  font-size: 16px;
  color: #ef4444;
  margin: 0 0 16px 0;
}

.retry-btn {
  padding: 10px 20px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: #111827;
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
  margin: 0 0 12px 0;
  color: #1a1a1a;
}

.stat-card small {
  font-size: 13px;
}

.stat-card .positive {
  color: #1f2937;
}

.stat-card .negative {
  color: #dc2626;
}

.tabs-navigation {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0;
  flex-wrap: wrap;
}

.tab-button {
  padding: 12px 16px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.2s ease;
  margin-bottom: -1px;
}

.tab-button:hover {
  color: #1a1a1a;
}

.tab-button.active {
  color: #1a1a1a;
  border-bottom-color: #1f2937;
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

.course-progress-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
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
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  transition: width 0.3s ease;
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
  margin: 0;
}

/* Ranking list styles */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.rank-number {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  min-width: 32px;
  text-align: center;
}

.rank-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.rank-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
}

.rank-count {
  font-size: 12px;
  color: #666;
}

/* Summary list styles */
.summary-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e5e7eb;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  font-size: 14px;
  color: #666;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

/* Chart card full width */
.chart-card.full-width {
  grid-column: 1 / -1;
}

/* Score distribution styles */
.score-distribution {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-range-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-range-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-label {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
}

.score-count {
  font-size: 13px;
  color: #666;
}

/* Table styles */
.table-container {
  overflow-x: auto;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
}

.students-table thead {
  background: #f8f9fa;
}

.students-table th {
  padding: 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.students-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
  color: #1a1a1a;
}

.students-table tbody tr:hover {
  background: #f8f9fa;
}

/* Badge styles */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #1f2937;
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 600;
}

.score-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 6px;
  font-weight: 600;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.active {
  background: #f3f4f6;
  color: #1f2937;
}

.status-badge.completed {
  background: #dbeafe;
  color: #2563eb;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-item {
  background: #f8f9fa;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.course-description {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
}

.view-btn {
  padding: 8px 14px;
  background: #1f2937;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.view-btn:hover {
  background: #111827;
}

@media (max-width: 768px) {
  .reports-wrapper {
    padding: 20px;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .tabs-navigation {
    flex-direction: column;
  }

  .tab-button {
    border-bottom: none;
    border-left: 3px solid transparent;
    margin-bottom: 0;
    margin-left: 0;
    padding-left: 12px;
  }

  .tab-button.active {
    border-left-color: #1f2937;
    border-bottom-color: transparent;
  }
}
</style>
