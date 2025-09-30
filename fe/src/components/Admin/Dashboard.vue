<template>
  <div class="dashboard-page-wrapper">
    <div class="container-fluid py-5">
      <h1 class="dashboard-title fw-bold mb-4">Admin System Overview</h1>
      
      <div class="row row-cols-1 row-cols-md-3 g-4 mb-5">
        <div class="col">
          <div class="card overview-card card-primary text-center h-100">
            <div class="card-body">
              <i class="bi bi-person-fill icon-lg mb-3"></i>
              <h5 class="card-title fw-bold">{{ overview.totalUsers }}</h5>
              <p class="card-text">Total Users</p>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card overview-card card-success text-center h-100">
            <div class="card-body">
              <i class="bi bi-book-fill icon-lg mb-3"></i>
              <h5 class="card-title fw-bold">{{ overview.activeCourses }}</h5>
              <p class="card-text">Active Courses</p>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card overview-card card-info text-center h-100">
            <div class="card-body">
              <i class="bi bi-cash-stack icon-lg mb-3"></i>
              <h5 class="card-title fw-bold">${{ overview.totalRevenue }}</h5>
              <p class="card-text">Total Revenue</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-6">
          <div class="card p-4 rounded-3 h-100">
            <h5 class="fw-bold mb-4">New Registrations</h5>
            <div class="chart-placeholder text-center text-muted">
              [Placeholder for a Line Chart showing new user registrations over time]
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card p-4 rounded-3 h-100">
            <h5 class="fw-bold mb-4">Course Completion Rate</h5>
            <div class="table-responsive">
              <table class="table table-borderless table-hover mb-0">
                <thead>
                  <tr class="text-muted">
                    <th scope="col">Course</th>
                    <th scope="col">Completion Rate</th>
                    <th scope="col">Students</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="course in courseCompletion" :key="course.id">
                    <td class="fw-bold">{{ course.name }}</td>
                    <td><span class="badge" :class="{'bg-success-soft text-success': course.completionRate >= 70, 'bg-warning-soft text-warning': course.completionRate < 70}">{{ course.completionRate }}%</span></td>
                    <td class="text-muted">{{ course.totalStudents }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card p-4 rounded-3 h-100">
            <h5 class="fw-bold mb-4">Revenue by Month</h5>
            <div class="chart-placeholder text-center text-muted">
              [Placeholder for a Bar Chart showing monthly revenue]
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card p-4 rounded-3 h-100">
            <h5 class="fw-bold mb-4">Revenue by Course</h5>
            <div class="table-responsive">
              <table class="table table-borderless table-hover mb-0">
                <thead>
                  <tr class="text-muted">
                    <th scope="col">Course</th>
                    <th scope="col">Total Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="course in revenueByCourse" :key="course.id">
                    <td class="fw-bold">{{ course.name }}</td>
                    <td><span class="badge bg-success-soft text-success">${{ course.revenue }}</span></td>
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
      overview: {
        totalUsers: 1547,
        activeCourses: 58,
        totalRevenue: "25,000"
      },
      courseCompletion: [
        { id: 1, name: "Advanced Web Programming", completionRate: 72, totalStudents: 45 },
        { id: 2, name: "Data Structures & Algorithms", completionRate: 65, totalStudents: 32 },
        { id: 3, name: "Mobile Development with React Native", completionRate: 85, totalStudents: 28 },
        { id: 4, name: "Introduction to Python", completionRate: 78, totalStudents: 49 },
      ],
      revenueByCourse: [
        { id: 1, name: "Advanced Web Programming", revenue: "8,500" },
        { id: 2, name: "Data Structures & Algorithms", revenue: "6,200" },
        { id: 3, name: "Mobile Development with React Native", revenue: "5,300" },
        { id: 4, name: "Introduction to Python", revenue: "5,000" },
      ]
    };
  }
};
</script>

<style scoped>
.dashboard-wrapper {
  background: linear-gradient(135deg, #f9fafb, #f1f5f9);
  min-height: 100vh;
  padding: 20px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

/* Header */
h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #222;
}
p {
  font-size: 0.95rem;
  color: #6c757d;
}

/* Stat Cards */
.card {
  border-radius: 14px;
  border: none;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}
.card h6 {
  font-size: 0.85rem;
  font-weight: 500;
  color: #6c757d;
  margin-bottom: 8px;
}
.card h3 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #111;
}
.card small {
  font-size: 0.8rem;
}

/* Tabs */
.nav-pills .nav-link {
  border-radius: 20px;
  padding: 6px 16px;
  font-weight: 500;
  color: #555;
  background: #f1f3f5;
  margin-right: 6px;
  transition: all 0.2s ease;
}
.nav-pills .nav-link.active {
  background: #111;
  color: #fff;
}
.nav-pills .nav-link:hover {
  background: #333;
  color: #fff;
}

/* Chart cards */
.card h6 {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #222;
}

/* Progress bars */
.progress {
  background: #e9ecef;
  border-radius: 4px;
}
.progress-bar {
  transition: width 0.4s ease;
}
</style>
