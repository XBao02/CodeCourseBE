<template>
  <section class="learning-path-ai" v-if="userId">
    <div class="header">
      <div>
        <p class="kicker">Lộ trình học AI</p>
        <h2>Skill Profile & Timeline</h2>
      </div>
      <div class="summary">
        <p class="label">Level đề xuất</p>
        <p class="value">{{ skillProfile?.level?.toUpperCase() || "PENDING" }}</p>
      </div>
    </div>

    <div v-if="loading" class="status">Đang tải lộ trình...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>
    <div v-else class="grid">
      <article class="card profile-card">
        <header>
          <h3>Skill profile</h3>
          <p class="subtitle">Các khóa học phù hợp với năng lực của bạn</p>
        </header>
        <div class="pill-container">
          <span class="pill" v-for="skill in skillProfile?.strengths || []" :key="`str-${skill}`">
            {{ skill }}
          </span>
          <span v-if="!(skillProfile?.strengths?.length)" class="muted">Chưa có strength</span>
        </div>
        <div class="pill-container">
          <span class="pill pill--weak" v-for="skill in skillProfile?.weaknesses || []" :key="`weak-${skill}`">
            {{ skill }}
          </span>
          <span v-if="!(skillProfile?.weaknesses?.length)" class="muted">Chưa có weakness</span>
        </div>
        <div class="courses">
          <article
            v-for="course in recommendedCourses"
            :key="course.id"
            class="course-card course-card--flex"
          >
            <div class="course-card__info">
              <h4>{{ course.title }}</h4>
              <p>{{ course.level || "Khóa học" }} · {{ course.slug }}</p>
            </div>
            <button class="go-to-course-btn" @click="goToCourse(course)">Đi đến khóa học</button>
          </article>
          <p v-if="!recommendedCourses.length" class="muted">No recommended courses yet.</p>
        </div>
      </article>

      <article class="card timeline-card">
        <header>
          <h3>Lộ trình học theo tuần dựa trên các khóa học này</h3>
        </header>
        <div v-if="timeline?.length" class="timeline">
          <article v-for="week in timeline" :key="`week-${week.week}`" class="timeline-item">
            <header>
              <span class="week-label">Tuần {{ week.week }}</span>
              <h4>{{ week.title }}</h4>
            </header>
            <p class="desc">{{ week.description }}</p>
            <ul class="topics">
              <li v-for="course in getCoursesByIds(week.course_ids || [])" :key="course.id">
                {{ course.title }}
              </li>
            </ul>
          </article>
        </div>
        <p v-else class="status muted">Chưa có timeline cho bạn.</p>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { getStoredSession } from "@/services/authService";

const session = computed(() => getStoredSession());
const userId = computed(() => session.value?.user?.id || null);
const loading = ref(true);
const error = ref("");
const skillProfile = ref(null);
const recommendedCourses = ref([]);
const timeline = ref([]);
const router = useRouter();

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api",
  timeout: 15000,
});

client.interceptors.request.use((config) => {
  if (session.value?.access_token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${session.value.access_token}`;
  }
  return config;
});

const loadPath = async () => {
  if (!userId.value) {
    error.value = "Vui lòng đăng nhập để xem lộ trình.";
    loading.value = false;
    return;
  }
  try {
    const { data } = await client.get(`/learning-path/${userId.value}`);
    skillProfile.value = data.skill_profile || null;
    recommendedCourses.value = skillProfile.value?.recommended_courses || [];
    timeline.value = data.timeline || [];
  } catch (err) {
    error.value = err?.response?.data?.error || "Không thể tải lộ trình từ API.";
  } finally {
    loading.value = false;
  }
};

const getCoursesByIds = (ids = []) => {
  if (!ids.length) {
    return [];
  }
  return recommendedCourses.value.filter((course) => ids.includes(course.id));
};

const goToCourse = (course) => {
  if (!course || !course.id) {
    return;
  }
  router
    .push({
      name: "StudentCourseStore",
      query: {
        courseId: course.id,
      },
    })
    .catch(() => {});
};

onMounted(loadPath);
</script>

<style scoped>
.learning-path-ai {
  background: #fff;
  border-radius: 18px;
  padding: 28px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 20px;
}
.kicker {
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.2em;
  color: #2563eb;
  margin: 0 0 4px;
}
.header h2 {
  margin: 0;
  font-size: 2rem;
}
.summary {
  text-align: right;
}
.label {
  margin: 0;
  font-size: 0.8rem;
  color: #64748b;
}
.value {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}
.card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.profile-card .subtitle {
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
}
.pill-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.pill {
  background: #eef2ff;
  color: #1d4ed8;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.85rem;
}
.pill--weak {
  background: #fee2e2;
  color: #b91c1c;
}
.muted {
  color: #64748b;
  font-size: 0.9rem;
}
.courses {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.course-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px;
  background: #f8fafc;
}
.course-card--flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.course-card__info {
  flex: 1;
}
.course-card h4 {
  margin: 0;
  font-size: 1rem;
}
.course-card p {
  margin: 4px 0 0;
  font-size: 0.85rem;
  color: #475569;
}
.go-to-course-btn {
  border: none;
  border-radius: 8px;
  padding: 6px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  background: #2563eb;
  color: #fff;
  transition: background 0.2s ease;
}
.go-to-course-btn:hover {
  background: #1d4ed8;
}
.timeline-card header h3 {
  margin: 0;
}
.timeline {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.timeline-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #dbeafe;
}
.timeline-item header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.week-label {
  font-size: 0.8rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #2563eb;
}
.timeline-item h4 {
  margin: 0;
}
.desc {
  margin: 6px 0;
  color: #1e293b;
}
.topics {
  margin: 0;
  padding-left: 18px;
  color: #475569;
}
.status {
  color: #475569;
  font-weight: 600;
}
.status.error {
  color: #dc2626;
}
.status.muted {
  font-weight: 400;
}
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  .summary {
    text-align: left;
  }
}
</style>
