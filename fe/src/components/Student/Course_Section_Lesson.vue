
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
                                    <div class="section-title-toggle" @click="toggleSection(section.id)" style="cursor: pointer;">
                                        <strong>{{ section.title }}</strong>
                                        <div class="small text-muted">Thứ tự: {{ section.sortOrder }}</div>
                                    </div>
                                    <div>
                                        <span class="badge bg-secondary">{{ section.lessons.length }} bài</span>
                                    </div>
                                </div>

                                <ul v-show="openSections.has(section.id)" class="list-group list-group-flush mt-2">
                                    <li v-for="lesson in section.lessons" :key="lesson.id"
                                        class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <div class="fw-semibold">{{ (lesson.title || '').toLowerCase() }}</div>
                                            <div class="small text-muted">{{ lesson.type }} · {{
                                                formatDuration(lesson.durationSeconds) }}
                                                <span v-if="lesson.isPreview"
                                                    class="badge bg-info text-dark ms-1">Preview</span>
                                            </div>
                                        </div>
                                        <div class="d-flex align-items-center">
                                            <span v-if="lesson.isCompleted" class="badge bg-success me-2">Đã xong</span>
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
                            <h6 class="mb-0">{{ activeLesson ? (activeLesson.title || '').toLowerCase() : 'Chọn bài học để bắt đầu' }}</h6>
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
                                    <template v-if="isDirectVideo(activeLesson.videoUrl)">
                                        <video :src="activeLesson.videoUrl" controls style="width: 100%; height: 100%;"
                                            @ended="markDone(activeLesson)"></video>
                                    </template>
                                    <template v-else>
                                        <iframe :src="computeEmbedUrl(activeLesson.videoUrl)" frameborder="0"
                                            allow="autoplay; encrypted-media" allowfullscreen
                                            style="width: 100%; height: 100%;"></iframe>
                                    </template>
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
import axios from 'axios';

export default {
    name: 'CourseSectionLesson',
    data() {
        return {
            // current user (student) - tạm thời mock
            currentUserId: 1,

            // Course info
            course: {
                id: null,
                instructorId: null,
                title: '',
                slug: '',
                description: '',
                level: '',
                price: 0,
                currency: 'VND',
                isPublic: true,
                createdAt: '',
                updatedAt: ''
            },

            // Sections + lessons from backend
            sections: [],

            // Enrollment info (đơn giản: trạng thái/tiến độ)
            enrollment: null,

            // Messages (mock local)
            messages: [],

            // UI state
            openSections: new Set(),
            activeLesson: null,
            showChat: true,
            newMessage: ''
        };
    },
    mounted() {
        this.bootstrapData();
    },
    beforeUnmount() {},
    computed: {
        // sections with their lessons (đã là dạng tổ hợp từ backend)
        sectionsWithLessons() {
            return (this.sections || []).slice().sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0));
        },
        isEnrolled() {
            return this.enrollment && this.enrollment.courseId === this.course.id && ['active', 'completed'].includes(this.enrollment.status);
        },
        enrollmentStatusLabel() {
            return this.enrollment ? this.enrollment.status : 'not enrolled';
        },
        activeSectionTitle() {
            if (!this.activeLesson) return '-';
            const sec = (this.sections || []).find(s => s.id === this.activeLesson.sectionId);
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
        async bootstrapData() {
            const courseId = Number(this.$route.params.courseId);
            if (!courseId) return;
            try {
                const res = await axios.get(`http://localhost:5000/api/student/course/${courseId}/sections-lessons`);
                const payload = res.data || {};
                this.course = payload.course || this.course;
                this.sections = Array.isArray(payload.sections) ? payload.sections : [];

                // Mặc định mở tất cả sections
                const opened = new Set();
                for (const s of this.sections) opened.add(s.id);
                this.openSections = opened;

                // Giả lập enrollment trạng thái active khi vào trang học
                this.enrollment = {
                    id: 0,
                    studentId: this.currentUserId,
                    courseId,
                    status: 'active',
                    progressPercent: 0,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };

            } catch (e) {
                // eslint-disable-next-line no-console
                console.error('Lỗi tải sections-lessons:', e);
            }
        },
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

            // Không còn khởi tạo YouTube Player ở đây, dùng iframe/video trực tiếp
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
            // Trang học yêu cầu đã đăng ký; ở đây chỉ cập nhật local
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
        async markDone(lesson) {
            if (!lesson) return;
            try {
                const res = await axios.post('http://localhost:5000/api/student/lesson-progress/complete', {
                    lessonId: lesson.id
                });
                if (res.data && res.data.success) {
                    // cập nhật cục bộ
                    const section = (this.sections || []).find(s => s.id === lesson.sectionId);
                    if (section) {
                        const l = (section.lessons || []).find(x => x.id === lesson.id);
                        if (l) l.isCompleted = true;
                    }
                }
            } catch (e) {
                // eslint-disable-next-line no-console
                console.error('Lỗi markDone:', e);
            }
        },
        computeEmbedUrl(url) {
            if (!url) return '';
            // Google Drive links -> /preview
            if (url.includes('drive.google.com')) {
                // Normalize to file/d/{id}/preview if possible
                // Examples:
                // - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
                // - https://drive.google.com/open?id=FILE_ID
                // - https://drive.google.com/uc?id=FILE_ID&export=download
                const idMatch =
                    url.match(/\/file\/d\/([^/]+)/) ||
                    url.match(/[?&]id=([^&]+)/);
                const fileId = idMatch && idMatch[1] ? idMatch[1] : null;
                if (fileId) {
                    return `https://drive.google.com/file/d/${fileId}/preview`;
                }
                // Fallback to original (may already be /preview)
                if (url.includes('/view')) return url.replace('/view', '/preview');
                return url;
            }
            // YouTube fallbacks
            if (url.includes('youtube.com') || url.includes('youtu.be')) {
                // Prefer embed format
                const id =
                    (url.match(/[?&]v=([^&#]+)/) || [])[1] ||
                    (url.match(/youtu\.be\/([^?&#]+)/) || [])[1] ||
                    (url.match(/embed\/([^?&#]+)/) || [])[1];
                return id ? `https://www.youtube.com/embed/${id}` : url;
            }
            // Otherwise return raw URL (handled by <video> if direct)
            return url;
        },
        isDirectVideo(url) {
            if (!url) return false;
            const lower = url.toLowerCase();
            return lower.endsWith('.mp4') || lower.endsWith('.webm') || lower.endsWith('.ogg');
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