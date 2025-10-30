<template>
  <div class="dashboard-wrapper p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-bold mb-0">Admin Dashboard</h4>
      <div class="d-flex align-items-center">
        <small class="text-muted me-3">{{ reportDate }}</small>
        <ion-icon name="notifications-outline" class="header-icon me-2"></ion-icon>
        <ion-icon name="calendar-outline" class="header-icon me-2"></ion-icon>
        <ion-icon name="settings-outline" class="header-icon"></ion-icon>
      </div>
    </div>

    <!-- Top Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-3" v-for="card in topStats" :key="card.title">
        <div class="card h-100 shadow-sm p-3 text-center">
          <h6 class="text-muted">{{ card.title }}</h6>
          <h3 class="fw-bold">{{ card.value }}</h3>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-lg-6">
        <div class="card p-3 mb-4">
          <h6 class="fw-bold">Recent Users</h6>
          <div class="table-responsive">
            <table class="table align-middle mb-0 table-sm">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>FullName</th>
                  <th>Role</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.Id">
                  <td>{{ user.Email }}</td>
                  <td>{{ user.FullName }}</td>
                  <td>{{ user.Role }}</td>
                  <td>{{ new Date(user.CreatedAt).toLocaleDateString() }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card p-3 mb-4">
          <h6 class="fw-bold">Courses</h6>
          <ul class="list-group list-group-flush">
            <li
              v-for="course in courses"
              :key="course.Id"
              class="list-group-item d-flex justify-content-between align-items-center"
            >
              {{ course.Title }}
              <span class="text-muted small">{{ course.InstructorName }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card p-3 mb-4">
          <h6 class="fw-bold">User Growth</h6>
          <div class="table-responsive">
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Month</th>
                  <th>New Users</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in userGrowth" :key="r.report_year + '-' + r.report_month">
                  <td>{{ r.report_year }}</td>
                  <td>{{ r.report_month }}</td>
                  <td>{{ r.new_users_count }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card p-3">
          <h6 class="fw-bold mb-3">Database Summary</h6>
          <ul class="list-group list-group-flush">
            <li class="list-group-item">Total Users: {{ summary.totalUsers }}</li>
            <li class="list-group-item">Students: {{ summary.totalStudents }}</li>
            <li class="list-group-item">Instructors: {{ summary.totalInstructors }}</li>
            <li class="list-group-item">Courses: {{ summary.totalCourses }}</li>
            <li class="list-group-item text-success">Active Courses: {{ summary.totalActiveCourses }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AdminDashboard",
  data() {
    return {
      reportDate: new Date().toLocaleString(),
      topStats: [],
      users: [],
      courses: [],
      summary: {},
      userGrowth: [],
    };
  },
  mounted() {
    this.fetchSummary();
    this.fetchUsers();
    this.fetchCourses();
    this.fetchUserGrowth();
  },
  methods: {
    async fetchSummary() {
      try {
        const res = await axios.get("http://127.0.0.1:5001/api/reports/summary");
        this.summary = res.data;
        this.topStats = [
          { title: "Total Users", value: res.data.totalUsers },
          { title: "Active Courses", value: res.data.totalActiveCourses },
          { title: "Students", value: res.data.totalStudents },
          { title: "Instructors", value: res.data.totalInstructors },
        ];
      } catch (err) {
        console.error("❌ Error fetching summary:", err);
      }
    },
    async fetchUsers() {
      try {
        const res = await axios.get("http://127.0.0.1:5001/");
        this.users = res.data.users || [];
      } catch (err) {
        console.error("❌ Error fetching users:", err);
      }
    },
    async fetchCourses() {
      try {
        const res = await axios.get("http://127.0.0.1:5001/api/courses");
        this.courses = res.data.courses || [];
      } catch (err) {
        console.error("❌ Error fetching courses:", err);
      }
    },
    async fetchUserGrowth() {
      try {
        const res = await axios.get("http://127.0.0.1:5001/api/reports/user-growth");
        this.userGrowth = res.data.userGrowth || [];
      } catch (err) {
        console.error("❌ Error fetching user growth:", err);
      }
    },
  },
};
</script>

<style scoped>
.dashboard-wrapper {
  background: #fff;
  min-height: 100vh;
}
.header-icon {
  font-size: 1.5rem;
  color: #495057;
  cursor: pointer;
}
.card {
  border-radius: 12px;
  border: 1px solid #eee;
}
.table-sm th,
.table-sm td {
  padding: 6px 10px;
}
</style>
