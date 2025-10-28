<template>
    <div class="course-detail">
        <div class="detail-header">
            <button @click="goBack" class="btn-back">
                <i class="fas fa-arrow-left"></i> Quay lại
            </button>
            <div class="header-actions">
                <button @click="editCourse" class="btn-edit">
                    <i class="fas fa-edit"></i> Sửa
                </button>
                <button @click="createContent" class="btn-content">
                    <i class="fas fa-pen-nib"></i> Soạn nội dung
                </button>
            </div>
        </div>

        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Đang tải thông tin khóa học...</p>
        </div>

        <div v-else-if="course" class="course-container">
            <!-- Banner -->
            <div class="course-banner">
                <img :src="course.thumbnail" :alt="course.title" class="banner-image">
                <div class="banner-overlay">
                    <h1>{{ course.title }}</h1>
                    <div class="course-meta-info">
                        <span class="badge" :class="course.status">
                            {{ getStatusText(course.status) }}
                        </span>
                        <span class="rating">
                            <i class="fas fa-star"></i> {{ course.rating }}
                        </span>
                        <span class="students">
                            <i class="fas fa-users"></i> {{ course.students }} học viên
                        </span>
                    </div>
                </div>
            </div>

            <!-- Content -->
            <div class="course-content-wrapper">
                <div class="main-content">
                    <!-- Description -->
                    <section class="section">
                        <h2>Mô tả khóa học</h2>
                        <p>{{ course.description }}</p>
                    </section>

                    <!-- Course Info -->
                    <section class="section">
                        <h2>Thông tin khóa học</h2>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Giá khóa học:</label>
                                <p>{{ Number(course.price).toLocaleString('vi-VN') }} VND</p>
                            </div>
                            <div class="info-item">
                                <label>Ngày tạo:</label>
                                <p>{{ formatDate(course.createdAt) }}</p>
                            </div>
                            <div class="info-item">
                                <label>Lần cập nhật cuối:</label>
                                <p>{{ formatDate(course.updatedAt) }}</p>
                            </div>
                            <div class="info-item">
                                <label>Trạng thái:</label>
                                <p>{{ getStatusText(course.status) }}</p>
                            </div>
                        </div>
                    </section>

                    <!-- Course Statistics -->
                    <section class="section">
                        <h2>Thống kê khóa học</h2>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-users"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>{{ course.students }}</h3>
                                    <p>Học viên</p>
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-star"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>{{ course.rating }}</h3>
                                    <p>Đánh giá trung bình</p>
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-book"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>{{ course.lessons || 0 }}</h3>
                                    <p>Bài học</p>
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-clock"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>{{ course.duration || '0' }}h</h3>
                                    <p>Thời lượng</p>
                                </div>
                            </div>
                        </div>
                    </section>

                    <!-- Actions -->
                    <section class="section">
                        <h2>Thao tác</h2>
                        <div class="action-buttons">
                            <button @click="editCourse" class="btn-primary">
                                <i class="fas fa-edit"></i> Chỉnh sửa khóa học
                            </button>
                            <button @click="createContent" class="btn-primary">
                                <i class="fas fa-pen-nib"></i> Soạn nội dung
                            </button>
                            <button @click="manageStudents" class="btn-primary">
                                <i class="fas fa-users"></i> Quản lý học viên
                            </button>
                            <button @click="toggleArchive" class="btn-warning">
                                <i :class="course.status === 'archived' ? 'fas fa-box-open' : 'fas fa-archive'"></i>
                                {{ course.status === 'archived' ? 'Bỏ lưu trữ' : 'Lưu trữ' }}
                            </button>
                            <button @click="deleteCourse" class="btn-danger">
                                <i class="fas fa-trash"></i> Xóa khóa học
                            </button>
                        </div>
                    </section>
                </div>

                <!-- Sidebar -->
                <aside class="sidebar">
                    <div class="sidebar-card">
                        <h3>Hành động nhanh</h3>
                        <button @click="editCourse" class="btn-block">
                            <i class="fas fa-edit"></i> Sửa
                        </button>
                        <button @click="createContent" class="btn-block">
                            <i class="fas fa-pen-nib"></i> Soạn nội dung
                        </button>
                        <button @click="manageStudents" class="btn-block">
                            <i class="fas fa-users"></i> Học viên
                        </button>
                    </div>

                    <div class="sidebar-card">
                        <h3>Giá</h3>
                        <p class="price">{{ Number(course.price).toLocaleString('vi-VN') }} VND</p>
                    </div>

                    <div class="sidebar-card">
                        <h3>Đánh giá</h3>
                        <div class="rating-display">
                            <div class="stars">
                                <i v-for="i in 5" :key="i" class="fas fa-star" :class="{ filled: i <= Math.floor(course.rating) }"></i>
                            </div>
                            <p>{{ course.rating }} / 5</p>
                        </div>
                    </div>
                </aside>
            </div>
        </div>

        <div v-else class="not-found">
            <p>Không tìm thấy khóa học này.</p>
            <button @click="goBack" class="btn-primary">Quay lại</button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CourseDetail',
    data() {
        return {
            course: null,
            loading: true
        }
    },
    mounted() {
        this.loadCourse()
    },
    methods: {
        async loadCourse() {
            this.loading = true
            try {
                const courseId = this.$route.params.id
                // Mock data - thay bằng API call thực
                const mockCourse = {
                    id: parseInt(courseId),
                    title: 'JavaScript Fundamentals',
                    description: 'Học JavaScript từ cơ bản đến nâng cao với các ví dụ thực tế và best practices',
                    price: 299000,
                    thumbnail: 'https://via.placeholder.com/1200x300/3498db/ffffff?text=JavaScript+Course',
                    students: 145,
                    rating: 4.5,
                    status: 'active',
                    lessons: 24,
                    duration: 18,
                    createdAt: new Date('2024-01-01'),
                    updatedAt: new Date('2024-01-20')
                }
                
                this.course = mockCourse
                console.log('Khóa học đã tải:', this.course)
            } catch (error) {
                console.error('Lỗi khi tải khóa học:', error)
            }
            this.loading = false
        },

        formatDate(date) {
            if (!date) return 'N/A'
            return new Date(date).toLocaleDateString('vi-VN')
        },

        getStatusText(status) {
            const map = {
                active: 'Đang hoạt động',
                draft: 'Bản nháp',
                archived: 'Đã lưu trữ'
            }
            return map[status] || status
        },

        goBack() {
            this.$router.back()
        },

        editCourse() {
            this.$router.push(`/instructor/courses/${this.course.id}/edit`)
        },

        createContent() {
            this.$router.push(`/instructor/courses/${this.course.id}`)
        },

        manageStudents() {
            this.$router.push(`/instructor/courses/${this.course.id}/students`)
        },

        async toggleArchive() {
            if (confirm(`Bạn có chắc muốn ${this.course.status === 'archived' ? 'bỏ lưu trữ' : 'lưu trữ'} khóa học này?`)) {
                try {
                    this.course.status = this.course.status === 'archived' ? 'active' : 'archived'
                    // API call to update
                    this.$toast.success('Đã cập nhật trạng thái khóa học')
                } catch (error) {
                    console.error('Lỗi:', error)
                }
            }
        },

        async deleteCourse() {
            if (confirm('Bạn có chắc muốn xóa khóa học này? Hành động này không thể hoàn tác.')) {
                try {
                    // API call to delete
                    this.$toast.success('Đã xóa khóa học')
                    this.$router.push('/instructor/courses')
                } catch (error) {
                    console.error('Lỗi:', error)
                }
            }
        }
    }
}
</script>

<style scoped>
.course-detail {
    min-height: 100vh;
    background: #f8f9fa;
}

.detail-header {
    background: white;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-back {
    background: none;
    border: none;
    color: #3498db;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-back:hover {
    color: #2980b9;
}

.header-actions {
    display: flex;
    gap: 12px;
}

.btn-edit, .btn-content {
    background: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-content {
    background: #9b59b6;
}

.btn-edit:hover {
    background: #2980b9;
}

.btn-content:hover {
    background: #8e44ad;
}

.loading {
    text-align: center;
    padding: 60px 20px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.course-container {
    max-width: 1200px;
    margin: 0 auto;
}

.course-banner {
    position: relative;
    height: 300px;
    overflow: hidden;
    background: #2c3e50;
}

.banner-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.banner-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
    padding: 40px 20px 20px;
    color: white;
}

.banner-overlay h1 {
    margin: 0 0 20px;
    font-size: 32px;
}

.course-meta-info {
    display: flex;
    gap: 20px;
    align-items: center;
}

.badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}

.badge.active {
    background: #27ae60;
}

.badge.draft {
    background: #f39c12;
}

.badge.archived {
    background: #95a5a6;
}

.rating, .students {
    display: flex;
    align-items: center;
    gap: 6px;
}

.course-content-wrapper {
    display: grid;
    grid-template-columns: 1fr 350px;
    gap: 30px;
    padding: 30px 20px;
}

.main-content {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.section {
    margin-bottom: 40px;
    padding-bottom: 40px;
    border-bottom: 1px solid #eee;
}

.section:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

.section h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 22px;
}

.section p {
    color: #555;
    line-height: 1.6;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.info-item {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
}

.info-item label {
    display: block;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
}

.info-item p {
    color: #555;
    margin: 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.stat-card {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 20px;
}

.stat-icon {
    font-size: 32px;
    opacity: 0.8;
}

.stat-content h3 {
    margin: 0;
    font-size: 24px;
}

.stat-content p {
    margin: 4px 0 0;
    opacity: 0.9;
}

.action-buttons {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.btn-primary, .btn-warning, .btn-danger {
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

.btn-warning {
    background: #f39c12;
    color: white;
}

.btn-warning:hover {
    background: #e67e22;
}

.btn-danger {
    background: #e74c3c;
    color: white;
}

.btn-danger:hover {
    background: #c0392b;
}

.sidebar {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.sidebar-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.sidebar-card h3 {
    margin: 0 0 16px;
    color: #2c3e50;
    font-size: 16px;
}

.btn-block {
    width: 100%;
    background: #3498db;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.3s;
}

.btn-block:last-child {
    margin-bottom: 0;
}

.btn-block:hover {
    background: #2980b9;
}

.price {
    font-size: 24px;
    font-weight: bold;
    color: #27ae60;
    margin: 0;
}

.rating-display {
    text-align: center;
}

.stars {
    margin-bottom: 12px;
    font-size: 20px;
}

.stars i {
    color: #ddd;
    margin: 0 4px;
}

.stars i.filled {
    color: #f39c12;
}

.rating-display p {
    margin: 0;
    color: #555;
}

.not-found {
    text-align: center;
    padding: 60px 20px;
    background: white;
    margin: 20px;
    border-radius: 12px;
}

@media (max-width: 768px) {
    .course-content-wrapper {
        grid-template-columns: 1fr;
    }

    .banner-overlay h1 {
        font-size: 24px;
    }

    .course-meta-info {
        flex-wrap: wrap;
    }

    .info-grid {
        grid-template-columns: 1fr;
    }

    .action-buttons {
        flex-direction: column;
    }

    .action-buttons button {
        width: 100%;
        justify-content: center;
    }
}
</style>
