<template>
  <div class="admin-dashboard py-4">
    <div class="container-fluid">

      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 class="fw-bold text-dark">🎓 Admin Dashboard Overview</h3>
        <small class="text-muted">Updated: {{ new Date().toLocaleDateString() }}</small>
      </div>

      <!-- Overview Cards -->
      <div class="row g-3 mb-4">
        <div class="col-12 col-md-4" v-for="card in overviewCards" :key="card.title">
          <div :class="`card border-0 shadow-sm text-center h-100 p-3 gradient-${card.color}`">
            <div class="card-body">
              <i :class="`${card.icon} icon-lg mb-2 text-${card.color}`"></i>
              <h3 class="fw-bold mb-1">{{ card.value }}</h3>
              <p class="text-muted small mb-0">{{ card.title }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="row g-3 mb-4">
        <!-- New Registrations -->
        <div class="col-lg-6">
          <div class="card p-3 h-100 shadow-sm border-0">
            <h6 class="fw-bold text-primary mb-3">📈 New Registrations</h6>
            <div class="chart-placeholder">
              <i class="bi bi-graph-up-arrow fs-2 text-secondary mb-2"></i>
              <p class="text-muted small mb-0">[Line Chart — User registrations over time]</p>
            </div>
          </div>
        </div>

        <!-- Completion Rate -->
        <div class="col-lg-6">
          <div class="card p-3 h-100 shadow-sm border-0">
            <h6 class="fw-bold text-primary mb-3">🎯 Course Completion Rate</h6>
            <div class="table-responsive small">
              <table class="table table-borderless align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Course</th>
                    <th>Completion</th>
                    <th>Students</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="course in courseCompletion" :key="course.id">
                    <td class="fw-semibold">{{ course.name }}</td>
                    <td style="width: 40%">
                      <div class="progress rounded-pill" style="height: 8px;">
                        <div class="progress-bar" :class="course.completionRate >= 70 ? 'bg-success' : 'bg-warning'"
                          :style="{ width: course.completionRate + '%' }"></div>
                      </div>
                      <small class="text-muted">{{ course.completionRate }}%</small>
                    </td>
                    <td class="text-muted">{{ course.totalStudents }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Revenue Section -->
      <div class="row g-3">
        <!-- Monthly Revenue -->
        <div class="col-lg-6">
          <div class="card p-3 h-100 shadow-sm border-0">
            <h6 class="fw-bold text-primary mb-3">💰 Revenue by Month</h6>
            <div class="chart-placeholder">
              <i class="bi bi-bar-chart-line fs-2 text-secondary mb-2"></i>
              <p class="text-muted small mb-0">[Bar Chart — Monthly revenue trend]</p>
            </div>
          </div>
        </div>

        <!-- Revenue by Course -->
        <div class="col-lg-6">
          <div class="card p-3 h-100 shadow-sm border-0">
            <h6 class="fw-bold text-primary mb-3">🏆 Revenue by Course</h6>
            <div class="table-responsive small">
              <table class="table table-borderless align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Course</th>
                    <th>Total Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="course in revenueByCourse" :key="course.id">
                    <td class="fw-semibold">{{ course.name }}</td>
                    <td>
                      <span class="badge bg-success-soft text-success fw-semibold px-3 py-2">
                        ${{ course.revenue }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
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
  background: #f8fafc;
  font-family: "Inter", "Segoe UI", sans-serif;
  min-height: 100vh;
}

/* Gradient Cards */
.gradient-primary {
  background: linear-gradient(145deg, #e3f2fd, #ffffff);
}

.gradient-success {
  background: linear-gradient(145deg, #e8f5e9, #ffffff);
}

.gradient-info {
  background: linear-gradient(145deg, #e0f7fa, #ffffff);
}

.icon-lg {
  font-size: 2rem;
}

/* Hover effect */
.card {
  border-radius: 14px;
  transition: all 0.25s ease;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

/* Chart placeholder */
.chart-placeholder {
  background: #f9fafb;
  border: 2px dashed #dee2e6;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  color: #6c757d;
}

/* Table style */
.table th {
  font-weight: 600;
  color: #495057;
}

.table td {
  color: #555;
}

/* Badge */
.bg-success-soft {
  background-color: #eaf8ee !important;
}

/* Progress bar animation */
.progress-bar {
  transition: width 0.4s ease-in-out;
}
</style>
