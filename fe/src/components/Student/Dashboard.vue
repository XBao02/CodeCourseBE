<template>
  <!-- <<<<<<< HEAD
  <div class="dashboard-page">
    <div class="container py-5">
      <div class="prep-kit-card p-4 rounded-3 d-flex justify-content-between align-items-center mb-5">
        <div>
          <span class="badge text-bg-primary new-badge mb-2">New</span>
          <h2 class="h4 fw-bold">Software Engineer Prep Kit</h2>
          <p class="text-muted mb-0">53 Practice Challenges • 1 Mock Test • 1 Mock Interview • 1 Role Certification</p>
        </div>
        <button class="btn btn-primary start-btn rounded-pill px-4 py-2">Start Preparation</button>
      </div>

      <h3 class="h5 fw-bold mb-4">Continue Practicing</h3>
      <div class="row g-4 mb-5">
        <div class="col-md-6">
          <div class="practice-card d-flex justify-content-between align-items-center p-4 rounded-3">
            <div class="d-flex align-items-center gap-3">
              <div class="practice-icon bg-icon-python rounded-3">
                <i class="bi bi-file-earmark-code-fill"></i>
              </div>
              <div>
                <h4 class="h6 fw-bold mb-1">Python</h4>
                <div class="progress" style="width: 200px; height: 8px;">
                  <div class="progress-bar" role="progressbar" style="width: 38%;" aria-valuenow="38" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <small class="text-muted mt-1 d-block">38% <span class="ms-2">[25 points to next star]</span></small>
              </div>
            </div>
            <button class="btn btn-icon">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
        <div class="col-md-6">
          <div class="practice-card d-flex justify-content-between align-items-center p-4 rounded-3">
            <div class="d-flex align-items-center gap-3">
              <div class="practice-icon bg-icon-problemsolving rounded-3">
                <i class="bi bi-gear-fill"></i>
              </div>
              <div>
                <h4 class="h6 fw-bold mb-1">Problem Solving</h4>
                <div class="progress" style="width: 200px; height: 8px;">
                  <div class="progress-bar" role="progressbar" style="width: 90%;" aria-valuenow="90" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <small class="text-muted mt-1 d-block">90% <span class="ms-2">[10 points to next star]</span></small>
              </div>
            </div>
            <button class="btn btn-icon">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card p-4 rounded-3 h-100">
            <h5 class="fw-bold mb-4">Upcoming Deadlines</h5>
            <ul class="list-group list-group-flush">
              <li v-for="task in deadlines" :key="task.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-0">{{ task.name }}</h6>
                  <small class="text-muted">{{ task.course }}</small>
                </div>
                <span class="badge rounded-pill bg-danger">{{ task.dueDate }}</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div class="col-lg-6">
          <div class="card p-4 rounded-3 h-100">
            <h5 class="fw-bold mb-4">Recent Activity</h5>
            <ul class="list-group list-group-flush">
              <li v-for="activity in recentActivity" :key="activity.id" class="list-group-item d-flex align-items-center gap-3">
                <i :class="activity.iconClass" class="activity-icon"></i>
                <div>
                  <p class="mb-0">{{ activity.text }}</p>
                  <small class="text-muted">{{ activity.time }}</small>
                </div>
              </li>
            </ul>
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
      deadlines: [
        { id: 1, name: "Assignment 3: Vue.js Router", course: "Advanced Web Programming", dueDate: "Oct 25" },
        { id: 2, name: "Quiz on Data Structures", course: "Data Structures & Algorithms", dueDate: "Nov 01" },
        { id: 3, name: "Project Proposal", course: "Mobile Development", dueDate: "Nov 15" }
      ],
      recentActivity: [
        { id: 1, text: "Submitted a solution for 'Reverse a Linked List'", time: "2 hours ago", iconClass: "bi bi-check-circle-fill text-success" },
        { id: 2, text: "Completed 'Lecture 3: Scoped CSS'", time: "1 day ago", iconClass: "bi bi-play-circle-fill text-primary" },
        { id: 3, text: "Passed 'Introduction to Python' Test", time: "3 days ago", iconClass: "bi bi-star-fill text-warning" }
      ]
    };
  }
};
</script>

<style scoped>
/* Main Page Styling */
.dashboard-page {
  background-color: #f5f6f7;
  min-height: 100vh;
}

/* Common Card Styling */
.card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
}

/* Prep Kit Card Styling */
.prep-kit-card {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}

.new-badge {
  background-color: #3e506b !important;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.6rem;
}

.start-btn {
  background-color: #00bf75;
  border-color: #00bf75;
  color: white;
  font-weight: 500;
}

/* Practice Cards Styling */
.practice-card {
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: box-shadow 0.2s ease-in-out;
}

.practice-card:hover {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.practice-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.bg-icon-python {
  background-color: #4b8bac; /* Màu xanh của Python */
  color: white;
}

.bg-icon-problemsolving {
  background-color: #f77e20;
  color: white;
}

.progress {
  height: 8px;
  background-color: #e0e0e0;
}

.progress-bar {
  background-color: #00bf75;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #a0a0a0;
}

.activity-icon {
  font-size: 1.2rem;
  width: 25px;
  text-align: center;
}
</style>
======= -->
  <!-- Statistics Cards -->
  <div class="container">
    <div class="row mt-5">
      <div class="col-md-3" v-for="stat in stats" :key="stat.title">
        <div class="card text-center shadow-sm">
          <div class="card-body">
            <h5 class="card-title">{{ stat.title }}</h5>
            <p class="display-6 fw-bold">{{ stat.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Learning Path -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-3">Learning Path</h5>
        <ul class="list-group">
          <li class="list-group-item d-flex justify-content-between align-items-center" v-for="path in learningPath"
            :key="path.name">
            {{ path.name }}
            <span class="badge" :class="{
              'bg-success': path.status === 'Completed',
              'bg-warning': path.status === 'In Progress',
              'bg-secondary': path.status === 'Not Started'
            }">
              {{ path.status }}
            </span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Enrolled Courses -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-3">Enrolled Courses</h5>
        <div class="row">
          <div class="col-md-6 mb-3" v-for="course in courses" :key="course.id">
            <div class="card h-100">
              <div class="card-body">
                <h6 class="card-title">{{ course.title }}</h6>
                <p class="text-muted small">{{ course.description }}</p>
                <div class="progress">
                  <div class="progress-bar" role="progressbar" :style="{ width: course.progress + '%' }">
                    {{ course.progress }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Progress Tracking -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-3">Overall Progress</h5>
        <div class="progress" style="height: 30px;">
          <div class="progress-bar bg-info fw-bold" role="progressbar" :style="{ width: overallProgress + '%' }">
            {{ overallProgress }}%
          </div>
        </div>
      </div>
    </div>

    <!-- Skill Test -->
    <div class="text-center">
      <router-link to="/skill-test" class="btn btn-primary btn-lg shadow">
        Take Skill Test
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "StudentDashboard",
  data() {
    return {
      stats: [
        { title: "Courses Enrolled", value: 4 },
        { title: "Completed Courses", value: 2 },
        { title: "Pending Courses", value: 2 },
        { title: "Skill Tests Taken", value: 1 },
      ],
      learningPath: [
        { name: "HTML & CSS Basics", status: "Completed" },
        { name: "JavaScript Fundamentals", status: "In Progress" },
        { name: "Vue.js Framework", status: "Not Started" },
      ],
      courses: [
        { id: 1, title: "Frontend Development", description: "Learn HTML, CSS, JS", progress: 80 },
        { id: 2, title: "Vue.js Advanced", description: "Master Vue ecosystem", progress: 40 },
      ],
      overallProgress: 60,
    };
  },
};
</script>
