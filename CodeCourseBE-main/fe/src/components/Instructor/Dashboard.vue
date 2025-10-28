<template>
    <div class="instructor-dashboard">
        <div class="dashboard-header">
            <h1>Bảng điều khiển Giảng viên</h1>
            <p>Chào mừng trở lại, {{ instructorName }}!</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-book"></i>
                </div>
                <div class="stat-content">
                    <h3>{{ totalCourses }}</h3>
                    <p>Khóa học của tôi</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-users"></i>
                </div>
                <div class="stat-content">
                    <h3>{{ totalStudents }}</h3>
                    <p>Học viên</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-star"></i>
                </div>
                <div class="stat-content">
                    <h3>{{ averageRating }}</h3>
                    <p>Đánh giá trung bình</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-dollar-sign"></i>
                </div>
                <div class="stat-content">
                    <h3>{{ totalRevenue }}</h3>
                    <p>Doanh thu</p>
                </div>
            </div>
        </div>

        <div class="dashboard-content">
            <div class="recent-courses">
                <h2>Khóa học gần đây</h2>
                <div class="courses-list">
                    <div v-for="course in recentCourses" :key="course.id" class="course-item">
                        <div class="course-info">
                            <h4>{{ course.title }}</h4>
                            <p>{{ course.students }} học viên</p>
                            <span class="status" :class="course.status">{{ course.status }}</span>
                        </div>
                        <div class="course-actions">
                            <button @click="editCourse(course.id)" class="btn-edit">Sửa</button>
                            <button @click="viewCourse(course.id)" class="btn-view">Xem</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="quick-actions">
                <h2>Thao tác nhanh</h2>
                <div class="action-buttons">
                    <button @click="createNewCourse" class="btn-primary">
                        <i class="fas fa-plus"></i>
                        Tạo khóa học mới
                    </button>
                    <button @click="viewReports" class="btn-secondary">
                        <i class="fas fa-chart-bar"></i>
                        Xem báo cáo
                    </button>
                    <button @click="goToChat" class="btn-secondary">
                        <i class="fas fa-comments"></i>
                        Tin nhắn
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'InstructorDashboard',
    data() {
        return {
            instructorName: 'Giảng viên',
            totalCourses: 0,
            totalStudents: 0,
            averageRating: '0.0',
            totalRevenue: '0đ',
            recentCourses: []
        }
    },
    mounted() {
        this.loadDashboardData()
    },
    methods: {
        async loadDashboardData() {
            // Giả lập API call
            try {
                // Trong thực tế, bạn sẽ gọi API ở đây
                this.instructorName = 'Nguyễn Văn A'
                this.totalCourses = 5
                this.totalStudents = 124
                this.averageRating = '4.8'
                this.totalRevenue = '12.500.000đ'

                this.recentCourses = [
                    { id: 1, title: 'Lập trình Vue.js cơ bản', students: 45, status: 'active' },
                    { id: 2, title: 'JavaScript nâng cao', students: 32, status: 'active' },
                    { id: 3, title: 'React Native từ zero', students: 28, status: 'draft' }
                ]
            } catch (error) {
                console.error('Lỗi khi tải dữ liệu dashboard:', error)
            }
        },

        createNewCourse() {
            this.$router.push('/instructor/courses/create')
        },

        editCourse(courseId) {
            this.$router.push(`/instructor/courses/edit/${courseId}`)
        },

        viewCourse(courseId) {
            this.$router.push(`/instructor/courses/${courseId}`)
        },

        viewReports() {
            this.$router.push('/instructor/reports')
        },

        goToChat() {
            this.$router.push('/instructor/chat')
        }
    }
}
</script>

<style scoped>
.instructor-dashboard {
    width: 100%;
    padding: 20px;
    margin: 0;
}

.dashboard-header {
    margin-bottom: 30px;
}

.dashboard-header h1 {
    color: #2c3e50;
    margin-bottom: 5px;
}

.dashboard-header p {
    color: #7f8c8d;
    font-size: 16px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 15px;
}

.stat-icon {
    background: #3498db;
    color: white;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.stat-content h3 {
    font-size: 24px;
    margin: 0;
    color: #2c3e50;
}

.stat-content p {
    margin: 5px 0 0 0;
    color: #7f8c8d;
}

.dashboard-content {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 30px;
}

.recent-courses,
.quick-actions {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.course-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid #ecf0f1;
}

.course-item:last-child {
    border-bottom: none;
}

.status.active {
    color: #27ae60;
    background: #d5f4e6;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status.draft {
    color: #f39c12;
    background: #fef5e7;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.course-actions {
    display: flex;
    gap: 10px;
}

.btn-edit,
.btn-view {
    padding: 5px 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-edit {
    background: #3498db;
    color: white;
}

.btn-view {
    background: #2ecc71;
    color: white;
}

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.btn-primary,
.btn-secondary {
    padding: 12px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    transition: all 0.3s;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-secondary {
    background: #ecf0f1;
    color: #2c3e50;
}

.btn-primary:hover {
    background: #2980b9;
}

.btn-secondary:hover {
    background: #bdc3c7;
}

@media (max-width: 768px) {
    .dashboard-content {
        grid-template-columns: 1fr;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }
}
</style>