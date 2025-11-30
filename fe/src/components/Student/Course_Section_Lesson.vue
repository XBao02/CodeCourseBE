<template>
    <div class="container py-4" style="min-height: calc(100vh - 120px);">
        <!-- Breadcrumb card -->
        <div class="card mb-3 border-0 shadow-sm rounded-4">
            <div class="card-body d-flex justify-content-between align-items-center">
                <nav aria-label="breadcrumb" class="mb-0">
                    <ol class="breadcrumb mb-0">
                        <li class="breadcrumb-item"><a href="#" @click.prevent="goHome">Home</a></li>
                        <li class="breadcrumb-item active" aria-current="page">{{ course.title }}</li>
                    </ol>
                </nav>
                <div class="small text-muted">Slug: <strong>{{ course.slug }}</strong></div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Left: sections/modules -->
            <div class="col-md-6">
                <div class="card border-0 shadow-sm rounded-4 h-100">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Sections & Lessons</h5>
                        <div class="small text-muted">Course: {{ course.title }}</div>
                    </div>

                    <div class="card-body overflow-auto p-3" style="max-height: 70vh;">
                        <div v-if="sectionsWithLessons.length">
                            <div v-for="section in sectionsWithLessons" :key="section.id" class="mb-3">
                                <div class="d-flex align-items-center justify-content-between bg-light rounded p-2 border section-header">
                                    <div class="section-title-toggle" @click="toggleSection(section.id)" style="cursor: pointer;">
                                        <strong>{{ section.title }}</strong>
                                        <div class="small text-muted">Order: {{ section.sortOrder }}</div>
                                    </div>
                                    <div>
                                        <span class="badge bg-secondary">{{ section.lessons.length }} lessons</span>
                                    </div>
                                </div>

                                <ul v-show="openSections.has(section.id)" class="list-group list-group-flush mt-2">
                                    <li v-for="lesson in section.lessons" :key="lesson.id" class="list-group-item lesson-item">
                                        <div class="d-flex justify-content-between align-items-center w-100">
                                            <div class="lesson-basic">
                                                <div class="fw-semibold">{{ lesson.title }}</div>
                                                <div v-if="lesson.tests && lesson.tests.length" class="small text-muted mt-1">
                                                    <span class="badge bg-warning text-dark me-2">Score</span>
                                                    <span class="score-display">{{ formatLessonScore(lesson) }}</span>
                                                </div>
                                            </div>
                                            <div class="text-end">
                                                <span v-if="lesson.isCompleted" class="badge bg-success me-2">Done</span>
                                                <button class="btn btn-sm btn-outline-primary" @click="selectLesson(lesson)">Open</button>
                                            </div>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div v-else class="text-center text-muted py-4">
                            No sections / lessons.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: lesson viewer -->
            <div class="col-md-6 d-flex flex-column">
                <div class="card border-0 shadow-sm rounded-4 mb-3 flex-grow-1">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0 text-capitalize">{{ activeLesson ? (activeLesson.title || '') : 'Select a lesson to begin' }}</h6>
                            <div class="small text-muted">Section: {{ activeSectionTitle }}</div>
                        </div>
                        <div>
                            <div class="small text-muted">Status: {{ enrollmentStatusLabel }}</div>
                        </div>
                    </div>

                    <div class="card-body overflow-auto p-3" style="max-height: 58vh;">
                        <div v-if="!isEnrolled" class="alert alert-warning">
                            You are not enrolled. <button class="btn btn-sm btn-success ms-2" @click="enrollNow">Enroll</button>
                        </div>

                        <div v-if="activeLesson">
                            <div v-if="activeLesson.type === 'video' && activeLesson.videoUrl">
                                <div class="ratio ratio-16x9 mb-3">
                                    <template v-if="isDirectVideo(activeLesson.videoUrl)">
                                        <video :src="activeLesson.videoUrl" controls style="width: 100%; height: 100%;" @ended="markDone(activeLesson)"></video>
                                    </template>
                                    <template v-else>
                                        <iframe :src="computeEmbedUrl(activeLesson.videoUrl)" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen style="width: 100%; height: 100%;"></iframe>
                                    </template>
                                </div>
                            </div>

                            <div class="mb-3">
                                <h6>Content</h6>
                                <div v-if="activeLesson.content" v-html="activeLesson.content"></div>
                                <div v-else class="text-muted">No textual content for this lesson.</div>
                            </div>

                            <div class="mb-3 small text-muted">
                                Type: {{ activeLesson.type }} · Duration: {{ formatDuration(activeLesson.durationSeconds) }}
                            </div>

                            <div v-if="activeLesson.tests && activeLesson.tests.length" class="mb-3">
                                <button class="btn btn-warning btn-sm" @click="takeLessonTest">Take Test</button>
                                <span class="badge bg-secondary ms-2" v-if="activeLesson.tests[0].timeLimitMinutes">{{ activeLesson.tests[0].timeLimitMinutes }} min</span>
                                <span v-if="activeLesson.tests[0].lastScore !== undefined" class="ms-2 text-muted">Score: {{ activeLesson.tests[0].lastScore }}/{{ activeLesson.tests[0].totalScore }}</span>
                            </div>
                        </div>

                        <div v-else class="text-center text-muted py-5">No lesson selected.</div>
                    </div>

                    <div class="card-footer d-flex justify-content-between align-items-center">
                        <div class="small text-muted">Sections: {{ sectionsWithLessons.length }}</div>
                        <div>
                            <button v-if="isEnrolled && activeLesson" class="btn btn-primary btn-sm" @click="markDone(activeLesson)">Mark Complete</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { getStoredSession } from '../../services/authService'

export default {
    name: 'CourseSectionLesson',
    data() {
        return {
            course: { id: null, instructorId: null, title: '', slug: '', description: '', level: '', price: 0, currency: 'VND', isPublic: true, createdAt: '', updatedAt: '' },
            sections: [],
            enrollment: null,
            openSections: new Set(),
            activeLesson: null
        };
    },
    mounted() { this.bootstrapData(); },
    computed: {
        sectionsWithLessons() { return (this.sections || []).slice().sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0)); },
        isEnrolled() { return this.enrollment && this.enrollment.courseId === this.course.id && ['active', 'completed'].includes(this.enrollment.status); },
        enrollmentStatusLabel() { return this.enrollment ? this.enrollment.status : 'not enrolled'; },
        activeSectionTitle() { if (!this.activeLesson) return '-'; const sec = (this.sections || []).find(s => s.id === this.activeLesson.sectionId); return sec ? sec.title : '-'; }
    },
    methods: {
        authHeaders() {
            const session = getStoredSession();
            return session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
        },
        async bootstrapData() {
            const courseId = Number(this.$route.params.courseId); if (!courseId) return;
            try {
                const res = await axios.get(`http://localhost:5000/api/student/course/${courseId}/sections-lessons`, { headers: this.authHeaders() });
                const payload = res.data || {}; this.course = payload.course || this.course; this.sections = Array.isArray(payload.sections) ? payload.sections : [];
                const opened = new Set(); for (const s of this.sections) opened.add(s.id); this.openSections = opened;
                this.enrollment = { id: 0, studentId: 0, courseId, status: 'active', progressPercent: 0, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
            } catch (e) { console.error('Failed loading sections-lessons:', e); }
        },
        goHome() { this.$router.push('/student/courses').catch(() => {}); },
        toggleSection(id) { if (this.openSections.has(id)) this.openSections.delete(id); else this.openSections.add(id); this.openSections = new Set(this.openSections); },
        selectLesson(lesson) { this.activeLesson = lesson; if (!this.openSections.has(lesson.sectionId)) { this.openSections.add(lesson.sectionId); this.openSections = new Set(this.openSections); } },
        takeLessonTest() { if (!this.activeLesson || !this.activeLesson.tests || !this.activeLesson.tests.length) return; const test = this.activeLesson.tests[0]; this.$router.push({ name: 'StudentTestTaking', params: { courseId: this.course.id, testId: test.id } }); },
        formatDuration(sec) { if (!sec) return '-'; const m = Math.floor(sec / 60); const s = sec % 60; return `${m}m ${s}s`; },
        enrollNow() { this.enrollment = { id: Math.floor(Math.random()*1000)+100, studentId: 0, courseId: this.course.id, status: 'active', progressPercent: 0, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() }; },
        async markDone(lesson) {
            if (!lesson) return;
            try {
                const res = await axios.post(
                    'http://localhost:5000/api/student/lesson-progress/complete',
                    { lessonId: lesson.id },
                    { headers: this.authHeaders() }
                );
                if (res.data && res.data.success) {
                    const section = (this.sections||[]).find(s=>s.id===lesson.sectionId);
                    if (section) {
                        const l = (section.lessons||[]).find(x=>x.id===lesson.id);
                        if (l) l.isCompleted = true;
                    }
                }
            } catch(e){
                console.error('markDone error:', e);
            }
        },
        computeEmbedUrl(url) {
            if (!url) return '';
            if (url.includes('drive.google.com')) {
                const idMatch = url.match(/\/file\/d\/([^/]+)/) || url.match(/[?&]id=([^&]+)/);
                const fileId = idMatch && idMatch[1] ? idMatch[1] : null;
                if (fileId) return `https://drive.google.com/file/d/${fileId}/preview`;
                if (url.includes('/view')) return url.replace('/view','/preview');
                return url;
            }
            if (url.includes('youtube.com') || url.includes('youtu.be')) {
                const id = (url.match(/[?&]v=([^&#]+)/)||[])[1]
                    || (url.match(/youtu\.be\/([^?&#]+)/)||[])[1]
                    || (url.match(/embed\/([^?&#]+)/)||[])[1];
                return id ? `https://www.youtube.com/embed/${id}` : url;
            }
            return url;
        },
        isDirectVideo(url){
            if(!url) return false;
            const lower=url.toLowerCase();
            return lower.endsWith('.mp4')||lower.endsWith('.webm')||lower.endsWith('.ogg');
        },
        formatLessonScore(lesson) {
            const test = lesson.tests && lesson.tests[0];
            if (!test) return '';
            const total = (test.totalScore !== undefined ? test.totalScore :
                           test.total_score !== undefined ? test.total_score :
                           test.maxScore !== undefined ? test.maxScore :
                           test.max_score !== undefined ? test.max_score : 10);
            const scored = (test.lastScore !== undefined ? test.lastScore :
                            test.score !== undefined ? test.score : 0);
            return `${scored}/${total}`;
        },
    }
};
</script>

<style scoped>
.container {
    max-width: 1200px;
}

.card {
    border-radius: 0.5rem;
}

.breadcrumb {
    background: transparent;
}

.section-header {
    cursor: pointer;
}

.lesson-item {
    transition: background 0.3s;
}

.lesson-item:hover {
    background: #f8f9fa;
}

.btn-primary {
    background-color: #007bff;
    border-color: #007bff;
}

.btn-primary:hover {
    background-color: #0056b3;
    border-color: #004085;
}

.btn-warning {
    background-color: #ffc107;
    border-color: #ffc107;
}

.btn-warning:hover {
    background-color: #e0a800;
    border-color: #d39e00;
}

.text-muted {
    color: #6c757d !important;
}

.text-capitalize {
    text-transform: capitalize !important;
}

.ratio {
    --bs-aspect-ratio: 56.25%;
}
</style>