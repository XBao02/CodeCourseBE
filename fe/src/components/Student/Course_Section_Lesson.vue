<template>
    <div class="container py-4" style="min-height: calc(100vh - 120px);">
        <div class="card mb-3 border-0 shadow-sm rounded-4">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <nav aria-label="breadcrumb" class="mb-0">
                        <ol class="breadcrumb mb-0">
                            <li class="breadcrumb-item"><a href="#" @click.prevent="goHome">Home</a></li>
                            <li class="breadcrumb-item active" aria-current="page">{{ course.title }}</li>
                        </ol>
                    </nav>
                    <div class="small text-muted">Slug: <strong>{{ course.slug }}</strong></div>
                </div>
                
                <!-- Course Progress Bar -->
                <div class="d-flex justify-content-between align-items-center">
                    <div class="flex-grow-1 me-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="small fw-semibold">Course Progress</span>
                            <span class="small text-muted">{{ completedLessonsCount }}/{{ totalLessonsCount }} lessons</span>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar" 
                                 :class="courseCompleted ? 'bg-success' : 'bg-primary'"
                                 :style="`width: ${courseProgressPercent}%`" 
                                 role="progressbar">
                            </div>
                        </div>
                    </div>
                    <div v-if="courseCompleted" class="badge bg-success px-3 py-2">
                        🎉 Completed!
                    </div>
                    <div v-else class="badge bg-secondary px-3 py-2">
                        {{ courseProgressPercent }}%
                    </div>
                </div>
            </div>
        </div>

        <div class="row g-4">
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
                                                <span v-if="lesson.completed || lesson.isCompleted" class="badge bg-success me-2">✓ Done</span>
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
                                
                                <span v-if="activeLesson.tests[0].lastScore !== undefined && activeLesson.tests[0].lastScore !== null" class="ms-2 text-muted">
                                    Score: {{ activeLesson.tests[0].lastScore }}/10
                                </span>
                            </div>
                        </div>

                        <div v-else class="text-center text-muted py-5">No lesson selected.</div>
                    </div>

                                        <div class="card-footer d-flex justify-content-between align-items-center">
                        <div class="small text-muted">Sections: {{ sectionsWithLessons.length }}</div>
                        <div class="d-flex align-items-center gap-2">
                            <button 
                                v-if="isEnrolled && activeLesson && !activeLesson.completed" 
                                class="btn btn-primary btn-sm" 
                                @click="markDone(activeLesson)">
                                Mark Complete
                            </button>
                            <span 
                                v-else-if="activeLesson && activeLesson.completed" 
                                class="badge bg-success px-3 py-2">
                                ✓ Completed
                            </span>
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
import {
  addCompletedCourseId,
  getCompletedCourseIds,
  removeCompletedCourseId,
} from '@/utils/completedCoursesStorage'

export default {
    name: 'CourseSectionLesson',
    data() {
        return {
            course: { id: null, instructorId: null, title: '', slug: '', description: '', level: '', price: 0, currency: 'VND', isPublic: true, createdAt: '', updatedAt: '' },
            sections: [],
            enrollment: null,
            openSections: new Set(),
            activeLesson: null,
            courseCompleted: false
        };
    },
    mounted() { 
        this.bootstrapData(); 
        
        // Set up completion status check
        this.$nextTick(() => {
            if (this.course?.id) {
                this.courseCompleted = getCompletedCourseIds().has(this.course.id);
            }
        });
    },
    watch: {
        // Watch for changes in total lesson count to detect course structure changes
        totalLessonsCount(newCount, oldCount) {
            if (oldCount > 0 && newCount !== oldCount) {
                console.log(`📊 Total lessons changed: ${oldCount} → ${newCount}, rechecking completion status`);
                this.$nextTick(() => {
                    this.syncCourseCompletion();
                });
            }
        },
        
        // Watch for changes in completed lesson count to update completion status
        completedLessonsCount(newCount, oldCount) {
            if (oldCount !== undefined && newCount !== oldCount) {
                console.log(`✅ Completed lessons changed: ${oldCount} → ${newCount}`);
                this.$nextTick(() => {
                    this.syncCourseCompletion();
                });
            }
        }
    },
    computed: {
        sectionsWithLessons() { return (this.sections || []).slice().sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0)); },
        isEnrolled() { return this.enrollment && this.enrollment.courseId === this.course.id && ['active', 'completed'].includes(this.enrollment.status); },
        enrollmentStatusLabel() { return this.enrollment ? this.enrollment.status : 'not enrolled'; },
        activeSectionTitle() { if (!this.activeLesson) return '-'; const sec = (this.sections || []).find(s => s.id === this.activeLesson.sectionId); return sec ? sec.title : '-'; },
        
        totalLessonsCount() {
            let total = 0;
            for (const section of this.sections || []) {
                if (section.lessons && Array.isArray(section.lessons)) {
                    total += section.lessons.length;
                }
            }
            return total;
        },
        
        completedLessonsCount() {
            let completed = 0;
            for (const section of this.sections || []) {
                if (section.lessons && Array.isArray(section.lessons)) {
                    completed += section.lessons.filter(lesson => lesson.completed).length;
                }
            }
            return completed;
        },
        
        courseProgressPercent() {
            if (this.totalLessonsCount === 0) return 0;
            return Math.round((this.completedLessonsCount / this.totalLessonsCount) * 100);
        }
    },
    methods: {
        authHeaders() {
            const session = getStoredSession();
            return session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
        },
        async bootstrapData() {
            const courseId = Number(this.$route.params.courseId); if (!courseId) return;
            
            // Store previous lesson count to detect changes
            const previousLessonCount = this.totalLessonsCount;
            
            try {
                const res = await axios.get(`http://localhost:5000/api/student/course/${courseId}/sections-lessons`, { headers: this.authHeaders() });
                const payload = res.data || {}; 
                this.course = payload.course || this.course; 
                this.sections = Array.isArray(payload.sections) ? payload.sections : [];
                const opened = new Set(); 
                for (const s of this.sections) opened.add(s.id); 
                this.openSections = opened;
                this.enrollment = { id: 0, studentId: 0, courseId, status: 'active', progressPercent: 0, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
                
                // Check if lesson count changed
                const newLessonCount = this.totalLessonsCount;
                if (previousLessonCount > 0 && previousLessonCount !== newLessonCount) {
                    console.log(`⚠️ Lesson count changed: ${previousLessonCount} → ${newLessonCount}`);
                    // Force recheck completion status
                    this.handleCourseStructureChange(previousLessonCount, newLessonCount);
                }
                
                // Sync course completion status after data is loaded
                this.syncCourseCompletion();
            } catch (e) { console.error('Failed loading sections-lessons:', e); }
        },
        goHome() { this.$router.push('/student/courses').catch(() => {}); },
        toggleSection(id) { if (this.openSections.has(id)) this.openSections.delete(id); else this.openSections.add(id); this.openSections = new Set(this.openSections); },
        selectLesson(lesson) { this.activeLesson = lesson; if (!this.openSections.has(lesson.sectionId)) { this.openSections.add(lesson.sectionId); this.openSections = new Set(this.openSections); } },
        takeLessonTest() { if (!this.activeLesson || !this.activeLesson.tests || !this.activeLesson.tests.length) return; const test = this.activeLesson.tests[0]; this.$router.push({ name: 'StudentTestTaking', params: { courseId: this.course.id, testId: test.id } }); },
        formatDuration(sec) { if (!sec) return '-'; const m = Math.floor(sec / 60); const s = sec % 60; return `${m}m ${s}s`; },
        enrollNow() { this.enrollment = { id: Math.floor(Math.random()*1000)+100, studentId: 0, courseId: this.course.id, status: 'active', progressPercent: 0, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() }; },
        async markDone(lesson) {
            if (!lesson || !lesson.id) return;
            
            // Show loading state
            const btn = event?.target;
            const originalText = btn?.textContent;
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Marking...';
            }
            
            try {
                const payload = { lessonId: lesson.id, courseId: this.course?.id };
                const res = await axios.post(
                    'http://localhost:5000/api/student/lesson-progress/complete',
                    payload,
                    { headers: this.authHeaders() }
                );
                const ok = res?.data?.success === true;
                if (ok) {
                    // Update lesson state locally (Vue 3 direct assignment)
                    lesson.completed = true;
                    lesson.completedAt = new Date().toISOString();
                    
                    // Update the lesson in sections array to trigger reactivity
                    const section = (this.sections || []).find(s => s.id === lesson.sectionId);
                    if (section && section.lessons) {
                        const lessonIndex = section.lessons.findIndex(l => l.id === lesson.id);
                        if (lessonIndex !== -1) {
                            section.lessons[lessonIndex] = { ...section.lessons[lessonIndex], completed: true, completedAt: new Date().toISOString() };
                        }
                        
                        // Recompute section progress
                        const total = section.lessons.length;
                        const done = section.lessons.filter(l => l.completed).length;
                        section.progressPercent = total ? Math.round((done / total) * 100) : 0;
                    }
                    
                    // Force re-render by updating activeLesson reference
                    if (this.activeLesson?.id === lesson.id) {
                        this.activeLesson = { ...this.activeLesson, completed: true, completedAt: new Date().toISOString() };
                    }
                    
                    // Show success message
                    alert('✅ Lesson marked as completed!');
                    
                    // The watcher will automatically handle course completion sync
                    
                    // Update button to show completion
                    if (btn) {
                        btn.textContent = '✓ Completed';
                        btn.classList.remove('btn-primary');
                        btn.classList.add('btn-success');
                    }
                } else {
                    console.warn('Complete lesson failed:', res?.data);
                    alert(res?.data?.message || res?.data?.error || 'Failed to mark as completed');
                    if (btn) {
                        btn.disabled = false;
                        btn.textContent = originalText;
                    }
                }
            } catch (e) {
                const msg = e?.response?.data?.message || e?.response?.data?.error || e?.message || 'Request error';
                console.error('markDone error:', msg);
                alert(`❌ Error: ${msg}`);
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = originalText;
                }
            }
        },
        toggleCourseComplete() {
            this.courseCompleted = !this.courseCompleted;
            if (!this.course?.id) return;
            if (this.courseCompleted) {
                addCompletedCourseId(this.course.id);
            } else {
                removeCompletedCourseId(this.course.id);
            }
        },
        syncCourseCompletion() {
            if (!this.course?.id) return;
            
            // First, check and update course completion based on actual lesson progress
            this.checkAndMarkCourseComplete();
            
            // Then sync the local state with updated localStorage
            this.courseCompleted = getCompletedCourseIds().has(this.course.id);
            console.log(`Course ${this.course.id} completion status synced: ${this.courseCompleted}`);
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
        
        checkAndMarkCourseComplete() {
            if (!this.course?.id || !this.sections?.length) return;
            
            // Count total lessons and completed lessons
            let totalLessons = 0;
            let completedLessons = 0;
            
            for (const section of this.sections) {
                if (section.lessons && Array.isArray(section.lessons)) {
                    totalLessons += section.lessons.length;
                    completedLessons += section.lessons.filter(lesson => lesson.completed).length;
                }
            }
            
            const courseId = this.course.id;
            const completedCourseIds = getCompletedCourseIds();
            const isCurrentlyMarkedComplete = completedCourseIds.has(courseId);
            
            console.log(`Course completion check: ${completedLessons}/${totalLessons} lessons completed`);
            console.log(`Currently marked as complete: ${isCurrentlyMarkedComplete}`);
            
            // Case 1: All lessons completed -> Mark course complete
            if (totalLessons > 0 && completedLessons === totalLessons) {
                if (!isCurrentlyMarkedComplete) {
                    addCompletedCourseId(courseId);
                    this.courseCompleted = true;
                    
                    // Emit event to update dashboard
                    window.dispatchEvent(new CustomEvent('courseCompletionChanged', { 
                        detail: { courseId, isCompleted: true, reason: 'all_lessons_completed' } 
                    }));
                    
                    // Show congratulations message
                    setTimeout(() => {
                        alert('🎉 Congratulations! You have completed this course!');
                    }, 500);
                    
                    console.log(`✅ Course ${courseId} marked as completed automatically`);
                }
            } 
            // Case 2: Not all lessons completed but course is marked complete -> Unmark course
            else if (isCurrentlyMarkedComplete && (totalLessons === 0 || completedLessons < totalLessons)) {
                removeCompletedCourseId(courseId);
                this.courseCompleted = false;
                
                // Emit event to update dashboard
                window.dispatchEvent(new CustomEvent('courseCompletionChanged', { 
                    detail: { courseId, isCompleted: false, reason: 'lessons_incomplete' } 
                }));
                
                console.log(`❌ Course ${courseId} unmarked as completed (${completedLessons}/${totalLessons} lessons done)`);
                
                // Show notification about course status change
                setTimeout(() => {
                    alert(`📚 Course status updated: ${completedLessons}/${totalLessons} lessons completed`);
                }, 300);
            }
        },

        // Phương thức đồng bộ chính xác trạng thái hoàn thành khóa học
        syncCourseCompletion() {
            if (!this.course?.id) return;
            
            const courseId = this.course.id;
            const totalLessons = this.totalLessonsCount;
            const completedLessons = this.completedLessonsCount;
            const isCurrentlyMarkedComplete = getCompletedCourseIds().has(courseId);
            
            console.log(`🔄 Syncing course completion for course ${courseId}:`);
            console.log(`   - Total lessons: ${totalLessons}`);
            console.log(`   - Completed lessons: ${completedLessons}`);
            console.log(`   - Currently marked complete: ${isCurrentlyMarkedComplete}`);
            
            // Determine what the completion status should be
            const shouldBeComplete = totalLessons > 0 && completedLessons === totalLessons;
            
            if (shouldBeComplete && !isCurrentlyMarkedComplete) {
                // Should be complete but isn't marked -> mark as complete
                addCompletedCourseId(courseId);
                this.courseCompleted = true;
                
                window.dispatchEvent(new CustomEvent('courseCompletionChanged', { 
                    detail: { courseId, isCompleted: true, reason: 'sync_completion' } 
                }));
                
                console.log(`✅ Course ${courseId} synchronized as completed`);
            } else if (!shouldBeComplete && isCurrentlyMarkedComplete) {
                // Should not be complete but is marked -> unmark
                removeCompletedCourseId(courseId);
                this.courseCompleted = false;
                
                window.dispatchEvent(new CustomEvent('courseCompletionChanged', { 
                    detail: { courseId, isCompleted: false, reason: 'sync_incomplete' } 
                }));
                
                console.log(`❌ Course ${courseId} synchronized as incomplete (${completedLessons}/${totalLessons})`);
            } else {
                // Status is already correct
                this.courseCompleted = shouldBeComplete;
                console.log(`✓ Course ${courseId} completion status is already correct: ${shouldBeComplete}`);
            }
        },

        handleCourseStructureChange(previousCount, newCount) {
            if (!this.course?.id) return;
            
            const courseId = this.course.id;
            const isMarkedComplete = getCompletedCourseIds().has(courseId);
            
            if (isMarkedComplete) {
                if (newCount > previousCount) {
                    // New lessons added - course should no longer be complete
                    removeCompletedCourseId(courseId);
                    this.courseCompleted = false;
                    
                    // Emit event to update dashboard
                    window.dispatchEvent(new CustomEvent('courseCompletionChanged', { 
                        detail: { courseId, isCompleted: false, reason: 'new_lessons_added' } 
                    }));
                    
                    setTimeout(() => {
                        alert(`📚 Course updated! ${newCount - previousCount} new lesson(s) added. Course completion reset.`);
                    }, 500);
                    
                    console.log(`🔄 Course ${courseId} unmarked due to new lessons: ${previousCount} → ${newCount}`);
                } else if (newCount < previousCount) {
                    // Lessons removed - need to recheck completion status
                    console.log(`📉 Lessons removed: ${previousCount} → ${newCount}. Rechecking completion...`);
                    
                    // Force a complete recheck of the course completion status
                    setTimeout(() => {
                        this.syncCourseCompletion();
                    }, 100);
                }
            } else if (newCount !== previousCount) {
                // Course not completed yet, but structure changed - just recheck completion
                console.log(`� Course structure changed (${previousCount} → ${newCount}), rechecking completion...`);
                setTimeout(() => {
                    this.syncCourseCompletion();
                }, 100);
            }
        },

        // SỬA: Hàm này giờ đây chỉ lấy lastScore (đã là hệ 10 từ backend) và nối thêm chuỗi "/10"
        formatLessonScore(lesson) {
            const test = lesson.tests && lesson.tests[0];
            if (!test || test.lastScore === undefined || test.lastScore === null) return '';
            
            // Backend đã trả về scale 10, hiển thị trực tiếp
            return `${test.lastScore}/10`;
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
.complete-btn--done {
    background: #94a3b8 !important;
    border-color: #94a3b8 !important;
    color: #fff !important;
}

.progress {
    border-radius: 10px;
    background-color: #e9ecef;
}

.progress-bar {
    border-radius: 10px;
    transition: width 0.5s ease-in-out;
}

.badge.bg-success {
    background-color: #198754 !important;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
</style>
