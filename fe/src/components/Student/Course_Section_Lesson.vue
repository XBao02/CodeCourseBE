// ...existing code...
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
                        <h5 class="mb-0">Modules & Lessons</h5>
                        <div class="small text-muted">Course: {{ course.title }}</div>
                    </div>

                    <div class="card-body overflow-auto p-3" style="max-height: 70vh;">
                        <div v-if="sectionsWithLessons.length">
                            <div v-for="section in sectionsWithLessons" :key="section.id" class="mb-2">
                                <div class="d-flex align-items-center justify-content-between bg-light rounded p-2">
                                    <div>
                                        <strong>{{ section.title }}</strong>
                                        <div class="small text-muted">Thứ tự: {{ section.sortOrder }}</div>
                                    </div>
                                    <div>
                                        <button class="btn btn-sm btn-outline-secondary me-2"
                                            @click="toggleSection(section.id)">
                                            <span v-if="openSections.has(section.id)">Ẩn</span>
                                            <span v-else>Hiện</span>
                                        </button>
                                        <span class="badge bg-secondary">{{ section.lessons.length }} bài</span>
                                    </div>
                                </div>

                                <ul v-show="openSections.has(section.id)" class="list-group list-group-flush mt-2">
                                    <li v-for="lesson in section.lessons" :key="lesson.id"
                                        class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <div class="fw-semibold">{{ lesson.title }}</div>
                                            <div class="small text-muted">{{ lesson.type }} · {{
                                                formatDuration(lesson.durationSeconds) }}
                                                <span v-if="lesson.isPreview"
                                                    class="badge bg-info text-dark ms-1">Preview</span>
                                            </div>
                                        </div>
                                        <div class="d-flex align-items-center">
                                            <button class="btn btn-sm btn-outline-primary me-2"
                                                @click="selectLesson(lesson)">
                                                Mở
                                            </button>
                                            <span class="small text-muted">{{ lessonSortLabel(lesson.sortOrder)
                                                }}</span>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div v-else class="text-center text-muted py-4">
                            Không có module / bài học.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: lesson viewer + chat -->
            <div class="col-md-6 d-flex flex-column">
                <div class="card border-0 shadow-sm rounded-4 mb-3 flex-grow-1">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">{{ activeLesson ? activeLesson.title : 'Chọn bài học để bắt đầu' }}</h6>
                            <div class="small text-muted">Module: {{ activeSectionTitle }}</div>
                        </div>
                        <div>
                            <div class="small text-muted">Trạng thái: {{ enrollmentStatusLabel }}</div>
                        </div>
                    </div>

                    <div class="card-body overflow-auto p-3" style="max-height: 58vh;">
                        <div v-if="!isEnrolled" class="alert alert-warning">
                            Bạn chưa đăng ký khóa học này. <button class="btn btn-sm btn-success ms-2"
                                @click="enrollNow">Đăng ký</button>
                        </div>

                        <div v-if="activeLesson">
                            <div v-if="activeLesson.type === 'video' && activeLesson.videoUrl">
                                <div class="ratio ratio-16x9 mb-3">
                                    <iframe :src="activeLesson.videoUrl" frameborder="0" allowfullscreen></iframe>
                                </div>
                            </div>

                            <div class="mb-3">
                                <h6>Nội dung</h6>
                                <div v-if="activeLesson.content" v-html="activeLesson.content"></div>
                                <div v-else class="text-muted">Không có nội dung văn bản cho bài này.</div>
                            </div>

                            <div class="mb-3 small text-muted">
                                Loại: {{ activeLesson.type }} · Thời lượng: {{
                                    formatDuration(activeLesson.durationSeconds) }}
                            </div>
                        </div>

                        <div v-else class="text-center text-muted py-5">
                            Chưa có bài học được chọn.
                        </div>
                    </div>

                    <div class="card-footer d-flex justify-content-between align-items-center">
                        <div class="small text-muted">Số sections: {{ sectionsWithLessons.length }}</div>
                        <div>
                            <button class="btn btn-outline-secondary btn-sm me-2" @click="toggleChat">
                                {{ showChat ? 'Ẩn chat' : 'Hiện chat' }}
                            </button>
                            <button v-if="isEnrolled && activeLesson" class="btn btn-primary btn-sm"
                                @click="markDone(activeLesson)">
                                Đánh dấu đã hoàn thành
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Chat card (collapsible) -->
                <div v-show="showChat" class="card border-0 shadow-sm rounded-4">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <div>
                            <strong>Chat với giảng viên</strong>
                            <div class="small text-muted">Khóa: {{ course.title }}</div>
                        </div>
                        <div class="small text-muted">Kênh: direct</div>
                    </div>

                    <div class="card-body p-3" style="max-height: 28vh; overflow:auto;">
                        <div v-if="chatMessages.length">
                            <div v-for="msg in chatMessages" :key="msg.id" class="mb-2">
                                <div :class="msg.fromUserId === currentUserId ? 'text-end' : ''">
                                    <div
                                        :class="['d-inline-block px-3 py-2 rounded', msg.fromUserId === currentUserId ? 'bg-primary text-white' : 'bg-light text-dark']">
                                        <div class="small">{{ msg.content }}</div>
                                        <div class="small text-muted mt-1">{{ formatDateTime(msg.createdAt) }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="text-center text-muted">Chưa có tin nhắn</div>
                    </div>

                    <div class="card-footer p-2">
                        <div class="d-flex">
                            <input v-model="newMessage" class="form-control form-control-sm me-2"
                                placeholder="Nhắn tin cho giảng viên..." @keyup.enter="sendMessage" />
                            <button class="btn btn-sm btn-primary" @click="sendMessage">Gửi</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CourseSectionLesson',
    data() {
        return {
            // current user (student)
            currentUserId: 501,

            // Course (from DB Courses)
            course: {
                id: 3,
                instructorId: 13,
                title: 'Web Development Bootcamp',
                slug: 'web-development-bootcamp',
                description: 'Fullstack web development.',
                level: 'intermediate',
                price: 750000,
                currency: 'VND',
                isPublic: true,
                createdAt: '2024-03-20 09:00:00',
                updatedAt: '2024-06-15 12:00:00'
            },

            // Sections (CourseSections)
            sections: [
                { id: 201, courseId: 3, title: 'Module 1 - Basics', sortOrder: 1 },
                { id: 202, courseId: 3, title: 'Module 2 - Frontend', sortOrder: 2 },
                { id: 203, courseId: 3, title: 'Module 3 - Backend', sortOrder: 3 }
            ],

            // Lessons (Lessons)
            lessons: [
                { id: 301, sectionId: 201, title: 'Intro & Setup', type: 'video', content: '<p>Giới thiệu</p>', videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ', durationSeconds: 300, sortOrder: 1, isPreview: true },
                { id: 302, sectionId: 201, title: 'HTML Basics', type: 'article', content: '<p>HTML cơ bản</p>', videoUrl: '', durationSeconds: 600, sortOrder: 2, isPreview: false },

                { id: 303, sectionId: 202, title: 'CSS Flexbox', type: 'video', content: '<p>Flexbox</p>', videoUrl: 'https://www.youtube.com/embed/3JluqTojuME', durationSeconds: 800, sortOrder: 1, isPreview: false },
                { id: 304, sectionId: 202, title: 'Vue Basics', type: 'video', content: '<p>Vue.js</p>', videoUrl: 'https://www.youtube.com/embed/4deVCNJq3qc', durationSeconds: 1200, sortOrder: 2, isPreview: false },

                { id: 305, sectionId: 203, title: 'Node & Express', type: 'video', content: '<p>Node.js</p>', videoUrl: '', durationSeconds: 1500, sortOrder: 1, isPreview: false },
            ],

            // Enrollment (Enrollments) - simulate whether student enrolled
            enrollment: {
                id: 401,
                studentId: 501,
                courseId: 3,
                status: 'active', // pending | active | completed | cancelled
                progressPercent: 20,
                createdAt: '2024-07-01 10:00:00',
                updatedAt: '2024-07-02 10:00:00'
            },

            // Messages (Messages)
            messages: [
                { id: 1, channel: 'direct', fromUserId: 13, toUserId: 501, courseId: 3, lessonId: 301, content: 'Chào, nếu bạn cần hỗ trợ hãy hỏi.', createdAt: '2024-07-05 09:00:00', readAt: null },
                { id: 2, channel: 'direct', fromUserId: 501, toUserId: 13, courseId: 3, lessonId: 301, content: 'Cảm ơn thầy, em có câu hỏi về bài 1.', createdAt: '2024-07-05 09:05:00', readAt: null }
            ],

            // UI state
            openSections: new Set(),
            activeLesson: null,
            showChat: true,
            newMessage: ''
        };
    },
    computed: {
        // sections with their lessons
        sectionsWithLessons() {
            const map = this.sections
                .filter(s => s.courseId === this.course.id)
                .map(s => {
                    const lessons = this.lessons
                        .filter(l => l.sectionId === s.id)
                        .slice()
                        .sort((a, b) => a.sortOrder - b.sortOrder);
                    return { ...s, lessons };
                })
                .sort((a, b) => a.sortOrder - b.sortOrder);
            return map;
        },
        isEnrolled() {
            return this.enrollment && this.enrollment.courseId === this.course.id && ['active', 'completed'].includes(this.enrollment.status);
        },
        enrollmentStatusLabel() {
            return this.enrollment ? this.enrollment.status : 'not enrolled';
        },
        activeSectionTitle() {
            if (!this.activeLesson) return '-';
            const sec = this.sections.find(s => s.id === this.activeLesson.sectionId);
            return sec ? sec.title : '-';
        },
        chatMessages() {
            // show messages for this course and optionally active lesson
            return this.messages
                .filter(m => m.courseId === this.course.id && m.channel === 'direct' && (!this.activeLesson || m.lessonId === this.activeLesson.id))
                .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
        }
    },
    methods: {
        goHome() {
            this.$router.push('/student/courses').catch(() => { });
        },
        toggleSection(sectionId) {
            if (this.openSections.has(sectionId)) this.openSections.delete(sectionId);
            else this.openSections.add(sectionId);
            // force reactive update
            this.openSections = new Set(this.openSections);
        },
        selectLesson(lesson) {
            this.activeLesson = lesson;
            // open the section if not opened
            if (!this.openSections.has(lesson.sectionId)) {
                this.openSections.add(lesson.sectionId);
            }
            // mark lesson progress (simulate LessonProgress DB)
            const now = new Date().toISOString();
            // simulate add/update lesson progress
            // (in real app call API to persist)
            // here just console and keep local state
            // eslint-disable-next-line no-console
            console.log('Selected lesson', lesson.id, 'at', now);
        },
        toggleChat() {
            this.showChat = !this.showChat;
        },
        sendMessage() {
            const text = (this.newMessage || '').trim();
            if (!text) return;
            const id = (this.messages.length ? Math.max(...this.messages.map(m => m.id)) : 0) + 1;
            const msg = {
                id,
                channel: 'direct',
                fromUserId: this.currentUserId,
                toUserId: this.course.instructorId,
                courseId: this.course.id,
                lessonId: this.activeLesson ? this.activeLesson.id : null,
                content: text,
                createdAt: new Date().toISOString(),
                readAt: null
            };
            this.messages.push(msg);
            this.newMessage = '';
            // scroll container — best-effort (no direct ref used to keep code simple)
        },
        formatDuration(sec) {
            if (!sec) return '-';
            const m = Math.floor(sec / 60);
            const s = sec % 60;
            return `${m}m ${s}s`;
        },
        formatDateTime(v) {
            if (!v) return '-';
            const d = new Date(v);
            if (isNaN(d)) return v;
            return d.toLocaleString();
        },
        lessonSortLabel(order) {
            return `#${order}`;
        },
        enrollNow() {
            // simulate creating enrollment record
            this.enrollment = {
                id: Math.floor(Math.random() * 1000) + 100,
                studentId: this.currentUserId,
                courseId: this.course.id,
                status: 'active',
                progressPercent: 0,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
        },
        markDone(lesson) {
            // simulate marking lesson progress done
            // in real app persist to LessonProgress table
            // here update enrollment.progressPercent crudely
            if (!this.enrollment) return;
            const totalLessons = this.lessons.filter(l => this.sections.some(s => s.id === l.sectionId && s.courseId === this.course.id)).length || 1;
            this.enrollment.progressPercent = Math.min(100, Math.round((this.enrollment.progressPercent + Math.round(100 / totalLessons))));
            if (this.enrollment.progressPercent >= 100) this.enrollment.status = 'completed';
        }
    }
};
</script>

<style scoped>
.card {
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.ratio {
    background: #000;
}

.bg-light {
    background-color: #f8f9fa !important;
}
</style>