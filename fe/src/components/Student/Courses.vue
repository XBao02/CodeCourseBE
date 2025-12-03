<template>
    <div class="courses-wrapper">
        <!-- Header -->
        <div class="courses-header">
            <div>
                <h1>My Courses</h1>
                <p>Your enrolled courses</p>
            </div>
            <div class="header-info">
                <span>{{ registeredCourses.length }} courses enrolled</span>
            </div>
        </div>

        <div class="courses-layout single">
            <!-- Right: My Courses (only) -->
            <div class="courses-column">
                <div class="content-card">
                    <div class="card-header">
                        <h5>My Courses</h5>
                        <span class="count">{{ registeredCourses.length }}</span>
                    </div>
                    <div class="card-body">
                        <div v-if="registeredCourses.length" class="enrolled-courses-list">
                            <div v-for="course in registeredCourses" :key="'reg-' + course.id" class="enrolled-course-item">
                                <img :src="course.image" class="enrolled-course-image" @error="onImgError($event)" />
                                <div class="enrolled-course-details">
                                    <h6>{{ course.title }}</h6>
                                    <p class="enrolled-course-meta">
                                        Level: {{ course.level }} · {{ formatPrice(course.price, course.currency) }}
                                    </p>
                                </div>
                                <button class="action-button small" @click="enterCourse(course)">
                                    Start Learning
                                </button>
                            </div>
                        </div>
                        <div v-else class="empty-state">
                            <p>You haven't enrolled in any courses yet</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import { getStoredSession } from "../../services/authService";

const api = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 15000,
    headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use((config) => {
    const session = getStoredSession();
    if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
});

export default {
    data() {
        return {
            courses: [],
            myCourses: [],
            placeholderUrl: 'https://th.bing.com/th/id/R.3566b6dc407982faae0488c840a60a55?rik=5eM0TcgU0gC7MA&pid=ImgRaw&r=0',
        };
    },

    computed: {
        registeredCourses() {
            return Array.isArray(this.myCourses) ? this.myCourses : [];
        },
    },

    mounted() {
        this.loadData();
    },

    methods: {
        async loadData() {
            const session = getStoredSession();
            const studentId = session?.user?.studentId || session?.user?.id;
            try {
                const allRes = await api.get(`/api/student/courses`);
                const allCourses = Array.isArray(allRes.data?.courses) ? allRes.data.courses : [];
                this.courses = allCourses.map(c => ({
                    id: c.id,
                    title: c.title,
                    level: c.level || "beginner",
                    price: Number(c.price || 0),
                    currency: c.currency || "VND",
                    isPublic: c.is_public === true || c.isPublic === true,
                    image: c.image_url || c.thumbnail || c.image || this.placeholderUrl,
                }));

                if (studentId) {
                    const mineRes = await api.get(`/api/student/my-courses`, { params: { student_id: studentId } });
                    const mineCourses = Array.isArray(mineRes.data?.courses) ? mineRes.data.courses : [];
                    this.myCourses = mineCourses.map(c => ({
                        id: c.id,
                        title: c.title,
                        level: c.level || "beginner",
                        price: Number(c.price || 0),
                        currency: c.currency || "VND",
                        image: c.image_url || c.thumbnail || c.image || this.placeholderUrl,
                    }));
                } else {
                    this.myCourses = [];
                }
            } catch (err) {
                console.error("Failed to load courses", err);
                this.courses = [];
                this.myCourses = [];
            }
        },

        formatPrice(p, c) {
            try {
                const price = Number(p || 0);
                if (!price) return "Free";
                const currency = c || "USD";
                return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(price);
            } catch {
                return String(p);
            }
        },

        enterCourse(course) {
            this.$router.push({ name: "StudentCourseLesson", params: { courseId: course.id } }).catch(() => { });
        },
        onImgError(e){
            if(e && e.target && e.target.src !== this.placeholderUrl){
                e.target.src = this.placeholderUrl;
            }
        }
    },
};
</script>

<style scoped>
.courses-wrapper { background:#f8f9fa; min-height:100vh; padding:40px; }
.courses-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:40px; }
.courses-header h1 { font-size:32px; font-weight:600; color:#1a1a1a; margin:0 0 8px; letter-spacing:-0.5px; }
.courses-header p { color:#666; font-size:15px; margin:0; }
.header-info { font-size:14px; color:#666; }
.courses-layout.single { display:grid; grid-template-columns: 1fr; gap:24px; }
.courses-column { display:flex; flex-direction:column; }
.content-card { background:#fff; border-radius:8px; border:1px solid #e5e7eb; overflow:hidden; display:flex; flex-direction:column; }
.card-header { padding:20px 24px; border-bottom:1px solid #e5e7eb; display:flex; justify-content:space-between; align-items:center; }
.card-header h5 { font-size:18px; font-weight:600; }
.card-body { padding:20px; overflow-y:auto; }
.enrolled-courses-list { display:flex; flex-direction:column; gap:12px; }
.enrolled-course-item { display:flex; gap:12px; align-items:center; padding:12px; background:#f8f9fa; border-radius:6px; }
.enrolled-course-image { width:80px; height:55px; object-fit:cover; border-radius:4px; flex-shrink:0; }
.enrolled-course-details { flex:1; }
.enrolled-course-details h6 { font-size:14px; font-weight:600; color:#1a1a1a; margin:0 0 4px; }
.enrolled-course-meta { font-size:12px; color:#666; margin:0; }
.action-button.small { padding:6px 16px; font-size:13px; background:linear-gradient(135deg,#3b82f6,#2563eb); color:#fff; border:none; border-radius:6px; cursor:pointer; }
.action-button.small:hover { background:linear-gradient(135deg,#2563eb,#1d4ed8); }
.empty-state { text-align:center; padding:60px 20px; color:#999; }
</style>