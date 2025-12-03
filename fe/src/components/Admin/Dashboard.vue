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
        <div class="stat-card" v-for="card in overviewCards" :key="card.title" :class="`card-${card.color}`">
          <div class="stat-icon">
            <i :class="card.icon"></i>
          </div>
          <div class="stat-content">
            <h6>{{ card.title }}</h6>
            <h3>{{ card.value }}</h3>
            <div class="stat-trend" v-if="card.trend">
              <span :class="`trend-${card.trend.type}`">
                <i :class="card.trend.icon"></i>
                {{ card.trend.value }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-grid">
        <!-- New Registrations -->
        <div class="chart-card">
          <div class="chart-header">
            <h5>New Registrations</h5>
            <div class="chart-actions">
              <select class="period-select" v-model="selectedPeriod">
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="registrationsChart"></canvas>
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
                <div class="progress-bar-fill" :style="{ width: course.completionRate + '%', background: course.color }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Revenue Section -->
      <div class="charts-grid">
        <!-- Monthly Revenue -->
        <div class="chart-card">
          <div class="chart-header">
            <h5>Revenue by Month</h5>
            <div class="chart-actions">
              <select class="period-select" v-model="selectedYear">
                <option value="2025">2025</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
              </select>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="revenueChart"></canvas>
          </div>
        </div>

        <!-- Revenue by Course -->
        <div class="chart-card">
          <h5>Revenue by Course</h5>
          <div class="revenue-list">
            <div v-for="course in revenueByCourse" :key="course.id" class="revenue-item">
              <div class="course-info">
                <div class="course-color" :style="{ backgroundColor: course.color }"></div>
                <span class="course-name">{{ course.name }}</span>
              </div>
              <span class="revenue-value">${{ course.revenue }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import adminService from '@/services/adminService';
Chart.register(...registerables);

export default {
  name: "AdminDashboard",
  data() {
    return {
      selectedPeriod: '30d',
      selectedYear: '2025',
      overviewTotals: { totalUsers: 0, activeCourses: 0, totalRevenue: 0 },
      courseCompletion: [],
      revenueByCourse: [],
      registrationsData: Array(12).fill(0),
      revenueByMonth: Array(12).fill(0),
      registrationsChart: null,
      revenueChart: null
    };
  },
  mounted() {
    this.fetchAnalytics();
  },
  methods: {
    async fetchAnalytics() {
      try {
        const data = await adminService.getDashboardAnalytics(this.selectedYear);
        this.overviewTotals = {
          totalUsers: Number(data.overview?.totalUsers || 0),
          activeCourses: Number(data.overview?.activeCourses || 0),
          totalRevenue: Number(data.overview?.totalRevenue || 0),
        };
        this.registrationsData = data.registrationsByMonth || Array(12).fill(0);
        this.revenueByMonth = data.revenueByMonth || Array(12).fill(0);
        this.courseCompletion = (data.courseCompletion || []).map((c, idx) => ({
          ...c,
          color: this.getColor(idx),
        }));
        this.revenueByCourse = (data.revenueByCourse || []).map((c, idx) => ({
          ...c,
          revenue: Number(c.revenue || 0),
          color: this.getColor(idx),
        }));
        this.initRegistrationsChart();
        this.initRevenueChart();
      } catch (err) {
        console.error("Failed to load analytics from API", err);
      }
    },

    getColor(index) {
      const palette = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6'];
      return palette[index % palette.length];
    },

    initRegistrationsChart() {
      const ctx = this.$refs.registrationsChart.getContext('2d');
      if (this.registrationsChart) this.registrationsChart.destroy();
      this.registrationsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          datasets: [{
            label: 'New Users',
            data: this.registrationsData,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#4f46e5',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              titleColor: '#1f2937',
              bodyColor: '#4b5563',
              borderColor: '#e5e7eb',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: false,
              callbacks: {
                label: function(context) {
                  return `New users: ${context.parsed.y}`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(0, 0, 0, 0.05)' },
              ticks: { color: '#6b7280', font: { size: 12 } }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#6b7280', font: { size: 12 } }
            }
          }
        }
      });
    },

    initRevenueChart() {
      const ctx = this.$refs.revenueChart.getContext('2d');
      if (this.revenueChart) this.revenueChart.destroy();
      this.revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          datasets: [{
            label: 'Revenue ($)',
            data: this.revenueByMonth,
            backgroundColor: Array(12).fill('rgba(79, 70, 229, 0.8)'),
            borderRadius: 6,
            borderSkipped: false,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              titleColor: '#1f2937',
              bodyColor: '#4b5563',
              borderColor: '#e5e7eb',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: false,
              callbacks: {
                label: function(context) {
                  return `Revenue: $${context.parsed.y}`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(0, 0, 0, 0.05)' },
              ticks: {
                color: '#6b7280',
                font: { size: 12 },
                callback: function(value) { return '$' + value; }
              }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#6b7280', font: { size: 12 } }
            }
          }
        }
      });
    }
  },
  watch: {
    selectedYear() {
      this.fetchAnalytics();
    }
  },
  computed: {
    overviewCards() {
      const formatNumber = (n) => Number(n || 0).toLocaleString();
      const formatCurrency = (n) => `$${Number(n || 0).toLocaleString()}`;
      return [
        { title: "Total Users", value: formatNumber(this.overviewTotals.totalUsers), icon: "fas fa-users", color: "primary" },
        { title: "Active Courses", value: formatNumber(this.overviewTotals.activeCourses), icon: "fas fa-book-open", color: "success" },
        { title: "Total Revenue", value: formatCurrency(this.overviewTotals.totalRevenue), icon: "fas fa-chart-line", color: "info" },
      ];
    }
  },
  beforeUnmount() {
    if (this.registrationsChart) this.registrationsChart.destroy();
    if (this.revenueChart) this.revenueChart.destroy();
  }
};
</script>

<style scoped>
.admin-dashboard {
  background: #f8f9fa;
  min-height: 100vh;
  padding: 40px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
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
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.dashboard-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-primary {
  border-left: 4px solid #4f46e5;
}

.card-success {
  border-left: 4px solid #10b981;
}

.card-info {
  border-left: 4px solid #0ea5e9;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.card-primary .stat-icon {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
}

.card-success .stat-icon {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.card-info .stat-icon {
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
}

.stat-content {
  flex: 1;
}

.stat-content h6 {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 4px 0;
}

.stat-content h3 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #1a1a1a;
}

.stat-trend {
  display: flex;
  align-items: center;
}

.trend-up {
  color: #10b981;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  padding: 28px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.chart-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-header h5 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.chart-actions {
  display: flex;
  gap: 12px;
}

.period-select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
  outline: none;
}

.period-select:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.chart-container {
  height: 300px;
  position: relative;
}

.course-progress-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  color: #6b7280;
  font-weight: 500;
}

.progress-bar-container {
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.revenue-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.revenue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.revenue-item:last-child {
  border-bottom: none;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.course-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
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

  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .stat-card {
    padding: 20px;
  }

  .chart-card {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>
