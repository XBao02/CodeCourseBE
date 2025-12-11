<template>
  <div class="dashboard-wrapper">
    <!-- Header -->
    <div class="dashboard-header">
      <h1>My Dashboard</h1>
      <p>Track your learning progress and achievements</p>
    </div>

    <div class="placement-cta">
      <button class="outline-btn" :disabled="!loggedUserId" @click="goToPlacementLanguagePicker">
        Làm lại bài test đầu vào
      </button>
    </div>

    <PlacementTestStart />

    <!-- Stats Grid -->
    <div v-if="loading" class="content-card"><p>Loading...</p></div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <h6>COURSES ENROLLED</h6>
          <h3>{{ stats.enrolled }}</h3>
        </div>
        <div class="stat-card">
          <h6>COMPLETED COURSES</h6>
          <h3>{{ stats.completed }}</h3>
        </div>
      </div>

      <div class="content-card">
        <LearningPathAI />
      </div>

      <!-- Enrolled Courses -->
      <div class="content-card">
        <h5>My Courses</h5>
        <div class="courses-grid">
          <div v-for="c in courses" :key="c.id" class="course-card" :class="{ 'course-completed': isCourseMarkedCompleted(c.id) }">
            <div class="course-header">
              <h6>{{ c.title }}</h6>
              <div class="course-status-badge" v-if="isCourseMarkedCompleted(c.id)">
                <span class="completion-icon">✓</span>
                <span>Completed</span>
              </div>
            </div>
            <p class="course-meta">Level: {{ c.level || '-' }} · {{ c.isPublic ? 'Public' : 'Private' }}</p>
            <div class="course-actions">
              <button class="open-btn" @click="openCourse(c)" :class="{ 'completed-btn': isCourseMarkedCompleted(c.id) }">
                {{ isCourseMarkedCompleted(c.id) ? 'Review Course' : 'Continue Learning' }}
              </button>
            </div>
          </div>
          <div v-if="!courses.length" class="course-card empty-state">
            <p>No courses enrolled yet</p>
            <router-link to="/student/course-store" class="browse-btn">Browse Courses</router-link>
          </div>
        </div>
      </div>

      <!-- Completed Courses Section (if any) -->
      <div class="content-card" v-if="completedCourses.length > 0">
        <h5>Recently Completed Courses</h5>
        <div class="completed-courses-list">
          <div v-for="c in completedCourses" :key="'completed-' + c.id" class="completed-course-item">
            <div class="completed-course-info">
              <div class="completion-badge">
                <span class="completion-icon">🎉</span>
              </div>
              <div class="course-details">
                <h6>{{ c.title }}</h6>
                <p class="completion-date">Completed recently</p>
              </div>
            </div>
            <button class="review-btn" @click="openCourse(c)">Review</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { getStoredSession } from '../../services/authService'
import PlacementTestStart from '@/components/Student/PlacementTestStart.vue'
import LearningPathAI from '@/components/Student/LearningPathAI.vue'
import { getCompletedCourseIds, listenCompletedCoursesChange } from '@/utils/completedCoursesStorage'

export default {
  name: 'StudentDashboard',
  data() {
    return {
      loading: true,
      courses: [],
      learningPath: [],
      stats: { enrolled: 0, completed: 0, pending: 0, testsTaken: 0, avgScore: 0 },
      studentId: null,
      completedCourseIds: getCompletedCourseIds(),
      completedCoursesListener: null,
    }
  },
  async mounted() {
    this.completedCoursesListener = listenCompletedCoursesChange(this.syncCompletedCourses)
    await this.loadData()
  },
  beforeUnmount() {
    if (this.completedCoursesListener) {
      this.completedCoursesListener()
      this.completedCoursesListener = null
    }
  },
  computed: {
    loggedUserId() {
      return getStoredSession()?.user?.id || null
    },
    completedCourses() {
      const completedIds = getCompletedCourseIds()
      return this.courses.filter(c => completedIds.has(c.id))
    },
  },
  methods: {
    authHeaders() {
      const session = getStoredSession()
      return session?.access_token
        ? { Authorization: `Bearer ${session.access_token}` }
        : {}
    },
    async loadData() {
      this.loading = true
      try {
        // Get my courses (also returns studentId)
        const myCoursesRes = await axios.get('http://localhost:5000/api/student/my-courses', { headers: this.authHeaders() })
        const mc = myCoursesRes.data || {}
        this.studentId = mc.studentId || null
        this.courses = Array.isArray(mc.courses) ? mc.courses : []
        // Stats from courses list
        this.stats.enrolled = this.courses.length
        
        // Count completed courses from localStorage (user marked as completed)
        const completedIds = getCompletedCourseIds()
        this.stats.completed = this.courses.filter(c => completedIds.has(c.id)).length
        this.stats.pending = this.courses.length - this.stats.completed

        // Test metrics (average score and attempts)
        try {
          const tm = await axios.get('http://localhost:5000/api/student/test-metrics', { headers: this.authHeaders() })
          const m = tm.data || {}
          this.stats.testsTaken = m.testsTaken || 0
          this.stats.avgScore = typeof m.averagePercentage === 'number' ? m.averagePercentage : 0
        } catch (e) {
          console.warn('test-metrics not available yet', e?.response?.data || e?.message)
          this.stats.testsTaken = 0
          this.stats.avgScore = 0
        }

        // Learning path
        if (this.studentId) {
          const plansRes = await axios.get(`http://localhost:5000/api/student/study-plans/${this.studentId}`, { headers: this.authHeaders() })
          const plans = (plansRes.data?.studyPlans || [])
          const items = plans.flatMap(p => p.items || [])
          this.learningPath = items.map(it => ({
            id: it.id,
            courseId: it.courseId,
            courseTitle: (this.courses.find(c => c.id === it.courseId)?.title) || `Course #${it.courseId}`,
            status: it.status || 'not started',
          }))
        }
      } catch (e) {
        console.error('Student dashboard load error:', e)
      } finally {
        this.loading = false
      }
    },
    statusClass(s) {
      const v = (s || '').toLowerCase()
      if (v.includes('complete')) return 'status-completed'
      if (v.includes('progress')) return 'status-progress'
      return 'status-not-started'
    },
    openCourse(course) {
      if (!course?.id) return
      this.$router.push({ name: 'StudentCourseLesson', params: { courseId: course.id } }).catch(()=>{})
    },
    goToPlacementLanguagePicker() {
      if (!this.loggedUserId) return
      this.$router
        .push({
          path: '/student/placement/select-language',
          query: { userId: this.loggedUserId },
        })
        .catch(() => {})
    },
    isCourseMarkedCompleted(courseId) {
      return this.completedCourseIds.has(courseId)
    },
    syncCompletedCourses() {
      this.completedCourseIds = getCompletedCourseIds()
      
      // Recalculate stats when completed courses change
      const completedIds = getCompletedCourseIds()
      this.stats.completed = this.courses.filter(c => completedIds.has(c.id)).length
      this.stats.pending = this.courses.length - this.stats.completed
    },
  },
  components: {
    PlacementTestStart,
    LearningPathAI,
  },
}
</script>

<style scoped>
/* Keep existing styles from scaffold if any */
.dashboard-wrapper { background: #f8f9fa; min-height: 100vh; padding: 40px; }
.dashboard-header { margin-bottom: 24px; }
.dashboard-header h1 { font-size: 32px; font-weight: 700; }
.dashboard-header p { color:#666; }
.stats-grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-bottom:24px; }
.stat-card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:20px; }
.content-card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:20px; margin-bottom:20px; }
.learning-path-list { display:flex; flex-direction:column; gap:10px; }
.path-item { display:flex; justify-content:space-between; }
.path-status { padding:2px 8px; border-radius:10px; font-size:12px; }
.status-completed { background:#d1fae5; color:#065f46; }
.status-progress { background:#fef3c7; color:#92400e; }
.status-not-started { background:#e5e7eb; color:#374151; }
.courses-grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap:16px; }
.course-card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:16px; display:flex; flex-direction:column; gap:12px; }
.course-card.course-completed { border-color:#10b981; background:#f0fdf4; }
.course-header { display:flex; justify-content:space-between; align-items:flex-start; }
.course-status-badge { display:flex; align-items:center; gap:4px; background:#dcfce7; color:#047857; padding:4px 8px; border-radius:6px; font-size:12px; font-weight:600; }
.completion-icon { font-size:14px; }
.open-btn { align-self:flex-start; background:#2563eb; color:#fff; border:none; padding:8px 14px; border-radius:6px; font-size:14px; cursor:pointer; font-weight:500; }
.open-btn:hover { background:#1d4ed8; }
.open-btn.completed-btn { background:#10b981; }
.open-btn.completed-btn:hover { background:#059669; }
.course-actions { display:flex; align-items:center; gap:10px; margin-top:auto; }
.course-done-label { font-size:12px; font-weight:600; color:#047857; background:#dcfce7; padding:4px 10px; border-radius:999px; line-height:1; }
.progress-bar-wrapper { width:100%; height:8px; background:#eef2f7; border-radius:8px; overflow:hidden; }
.progress-bar-wrapper.large { height:12px; }
.progress-bar-fill { height:100%; background:#3b82f6; }
.placement-cta { margin: 16px 0; display: flex; justify-content: flex-end; }
.outline-btn { border: 1px solid #2563eb; border-radius: 10px; padding: 10px 16px; background: transparent; color: #2563eb; font-weight: 600; cursor: pointer; transition: background 0.2s ease; }
.outline-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.outline-btn:not(:disabled):hover { background: rgba(37, 99, 235, 0.08); }

/* Completed Courses Section */
.completed-courses-list { display:flex; flex-direction:column; gap:12px; }
.completed-course-item { display:flex; justify-content:space-between; align-items:center; padding:12px; background:#f8fafc; border-radius:8px; border-left:4px solid #10b981; }
.completed-course-info { display:flex; align-items:center; gap:12px; }
.completion-badge { width:40px; height:40px; background:#dcfce7; border-radius:50%; display:flex; align-items:center; justify-content:center; }
.course-details h6 { margin:0; font-size:16px; font-weight:600; }
.completion-date { margin:0; font-size:12px; color:#6b7280; }
.review-btn { background:#10b981; color:#fff; border:none; padding:8px 16px; border-radius:6px; font-size:14px; cursor:pointer; font-weight:500; }
.review-btn:hover { background:#059669; }
.empty-state { text-align:center; }
.browse-btn { display:inline-block; margin-top:8px; background:#2563eb; color:#fff; text-decoration:none; padding:8px 16px; border-radius:6px; font-size:14px; font-weight:500; }
.browse-btn:hover { background:#1d4ed8; }
</style>
