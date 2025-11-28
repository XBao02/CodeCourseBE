<template>
    <div class="instructor-dashboard">
        <div class="dashboard-header">
            <h1>Dashboard</h1>
            <p>Welcome back, {{ instructorName }}!</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-content">
                    <p class="stat-label">Courses</p>
                    <h3>{{ totalCourses }}</h3>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-content">
                    <p class="stat-label">Students</p>
                    <h3>{{ totalStudents }}</h3>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-content">
                    <p class="stat-label">Average Rating</p>
                    <h3>{{ averageRating }} / 5</h3>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-content">
                    <p class="stat-label">Revenue</p>
                    <h3>{{ totalRevenue }}</h3>
                </div>
            </div>
        </div>

        <div class="dashboard-content">
            <div class="recent-courses">
                <h2>Recent Courses</h2>
                <div v-if="recentCourses.length === 0" class="empty-state">
                    <p>No courses yet</p>
                </div>
                <div v-else class="courses-list">
                    <div v-for="course in recentCourses" :key="course.id" class="course-item">
                        <div class="course-info">
                            <h4>{{ course.title }}</h4>
                            <p class="student-count">{{ course.students }} students</p>
                            <span class="status" :class="course.status">{{ course.status === 'active' ? 'Active' : 'Draft' }}</span>
                        </div>
                        <div class="course-actions">
                            <button @click="editCourse(course.id)" class="btn-edit">Edit</button>
                            <button @click="viewCourse(course.id)" class="btn-view">Content</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="quick-actions">
                <h2>Quick Actions</h2>
                <div class="action-buttons">
                    <button @click="createNewCourse" class="btn-primary">Create New Course</button>
                    <button @click="viewReports" class="btn-secondary">View Reports</button>
                    <button @click="goToChat" class="btn-secondary">Messages</button>
                    <button @click="goToCourses" class="btn-secondary">Manage Courses</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import instructorService from '../../services/instructorService'

export default {
    name: 'InstructorDashboard',
    data() {
        return {
            instructorName: 'Giảng viên',
            totalCourses: 0,
            totalStudents: 0,
            averageRating: '0.0',
            totalRevenue: '0đ',
            recentCourses: [],
            isLoading: false
        }
    },
    mounted() {
        this.loadDashboardData()
    },
    methods: {
        async loadDashboardData() {
            this.isLoading = true
            try {
                // Tạm thời hardcode instructor ID = 2 để test
                const instructorId = 2
                
                if (!instructorId) {
                    console.error('Không thể lấy instructor ID')
                    this.showErrorMessage()
                    return
                }
                
                // Gọi API dashboard từ service
                const data = await instructorService.getDashboard(instructorId)
                
                // Cập nhật dữ liệu
                this.instructorName = data.instructor.name
                this.totalCourses = data.stats.totalCourses
                this.totalStudents = data.stats.totalStudents
                this.averageRating = data.stats.averageRating.toFixed(1)
                this.totalRevenue = instructorService.formatCurrency(data.stats.totalRevenue)
                
                // Format lại dữ liệu khóa học
                this.recentCourses = data.recentCourses.map(course => ({
                    id: course.id,
                    title: course.title,
                    students: course.students,
                    status: course.status
                }))
                
            } catch (error) {
                console.error('Lỗi khi tải dữ liệu dashboard:', error)
                this.showErrorMessage()
            } finally {
                this.isLoading = false
            }
        },
        
        extractInstructorIdFromAuth() {
            // Thử lấy từ auth state hoặc user info
            try {
                const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
                return userInfo.instructorId || userInfo.id
            } catch (e) {
                return null
            }
        },
        
        formatCurrency(amount) {
            return instructorService.formatCurrency(amount)
        },
        
        showErrorMessage() {
            this.instructorName = 'Giảng viên'
            this.totalCourses = 0
            this.totalStudents = 0
            this.averageRating = '0.0'
            this.totalRevenue = '0đ'
            this.recentCourses = []
        },

        createNewCourse() {
            this.$router.push('/instructor/courses/create')
        },

        editCourse(courseId) {
            this.$router.push(`/instructor/courses/${courseId}/edit`)
        },

        viewCourse(courseId) {
            // Navigate directly to content management (lessons) instead of detail page
            this.$router.push(`/instructor/courses/${courseId}/lessons`)
        },

        viewReports() {
            this.$router.push('/instructor/reports')
        },

        goToChat() {
            this.$router.push('/instructor/chat')
        },
        
        goToCourses() {
            this.$router.push('/instructor/courses')
        }
    }
}
</script>

<style scoped>
.instructor-dashboard {
    width: 100%;
    padding: 40px;
    margin: 0;
    background: #f8f9fa;
    min-height: 100vh;
}

.dashboard-header {
    margin-bottom: 40px;
}

.dashboard-header h1 {
    font-size: 32px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}

.dashboard-header p {
    color: #666;
    font-size: 15px;
    margin: 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.stat-card {
    background: white;
    padding: 24px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    transition: all 0.3s ease;
    cursor: default;
}

.stat-card:hover {
    border-color: #d1d5db;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stat-content {
    text-align: left;
}

.stat-label {
    font-size: 13px;
    color: #666;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 8px 0;
}

.stat-content h3 {
    font-size: 28px;
    font-weight: 600;
    margin: 0;
    color: #1a1a1a;
}

.dashboard-content {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 30px;
}

.recent-courses,
.quick-actions {
    background: white;
    padding: 28px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}

.recent-courses h2,
.quick-actions h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 24px 0;
    padding-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;
}

.course-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 16px 0;
    border-bottom: 1px solid #f0f0f0;
    gap: 16px;
}

.course-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.course-info {
    flex: 1;
}

.course-info h4 {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 6px 0;
}

.student-count {
    font-size: 13px;
    color: #666;
    margin: 0 0 8px 0;
    display: block;
}

.status {
    display: inline-block;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 4px;
}

.status.active {
    color: #1f2937;
    background: #d1fae5;
}

.status.draft {
    color: #d97706;
    background: #fef3c7;
}

.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #999;
}

.empty-state p {
    font-size: 15px;
    margin: 0;
}

.course-actions {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
}

.btn-edit,
.btn-view {
    padding: 6px 14px;
    border: 1px solid #d1d5db;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    color: #374151;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.btn-edit:hover {
    background: #f9fafb;
    border-color: #9ca3af;
    color: #1f2937;
}

.btn-view:hover {
    background: #f9fafb;
    border-color: #9ca3af;
    color: #1f2937;
}

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.btn-primary,
.btn-secondary {
    padding: 12px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
    text-align: center;
    width: 100%;
}

.btn-primary {
    background: #1f2937;
    color: white;
    border: 1px solid #1f2937;
}

.btn-primary:hover {
    background: #111827;
    border-color: #111827;
}

.btn-secondary {
    background: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
}

.btn-secondary:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
    color: #1f2937;
}

@media (max-width: 768px) {
    .instructor-dashboard {
        padding: 20px;
    }

    .dashboard-content {
        grid-template-columns: 1fr;
    }

    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .course-item {
        flex-direction: column;
    }

    .course-actions {
        width: 100%;
    }

    .btn-edit,
    .btn-view {
        flex: 1;
    }
}
</style>