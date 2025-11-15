<template>
    <div class="course-students">
        <div class="students-header">
            <button @click="goBack" class="btn-back">
                <i class="fas fa-arrow-left"></i> Quay lại
            </button>
            <h1>Quản lý học viên - {{ courseName }}</h1>
        </div>

        <div class="students-container">
            <!-- Filters -->
            <div class="filters">
                <div class="filter-group">
                    <input 
                        type="text" 
                        v-model="searchQuery"
                        placeholder="Tìm kiếm theo tên hoặc email..."
                        class="search-input"
                    >
                    <i class="fas fa-search"></i>
                </div>

                <div class="filter-group">
                    <select v-model="filterStatus">
                        <option value="">Tất cả trạng thái</option>
                        <option value="active">Đang học</option>
                        <option value="completed">Hoàn thành</option>
                        <option value="inactive">Không hoạt động</option>
                    </select>
                </div>

                <div class="filter-group">
                    <select v-model="sortBy">
                        <option value="name">Sắp xếp theo tên</option>
                        <option value="enrollDate">Sắp xếp theo ngày đăng ký</option>
                        <option value="progress">Sắp xếp theo tiến độ</option>
                    </select>
                </div>
            </div>

            <!-- Statistics -->
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-number">{{ totalStudents }}</div>
                    <div class="stat-label">Tổng học viên</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ completedCount }}</div>
                    <div class="stat-label">Hoàn thành</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ averageProgress }}%</div>
                    <div class="stat-label">Tiến độ trung bình</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ activeCount }}</div>
                    <div class="stat-label">Đang học</div>
                </div>
            </div>

            <!-- Students Table -->
            <div v-if="loading" class="loading">
                <div class="spinner"></div>
                <p>Đang tải danh sách học viên...</p>
            </div>

            <div v-else-if="filteredStudents.length === 0" class="no-students">
                <p>Không có học viên nào.</p>
            </div>

            <div v-else class="students-table">
                <div class="table-header">
                    <div class="col-name">Tên học viên</div>
                    <div class="col-email">Email</div>
                    <div class="col-progress">Tiến độ</div>
                    <div class="col-status">Trạng thái</div>
                    <div class="col-enrolled">Ngày đăng ký</div>
                    <div class="col-actions">Thao tác</div>
                </div>

                <div 
                    v-for="student in filteredStudents" 
                    :key="student.id"
                    class="table-row"
                >
                    <div class="col-name">
                        <div class="student-avatar" :style="{ background: student.avatarColor }">
                            {{ student.name.charAt(0) }}
                        </div>
                        <span>{{ student.name }}</span>
                    </div>
                    <div class="col-email">{{ student.email }}</div>
                    <div class="col-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: student.progress + '%' }"></div>
                        </div>
                        <span class="progress-text">{{ student.progress }}%</span>
                    </div>
                    <div class="col-status">
                        <span class="badge" :class="student.status">
                            {{ getStatusText(student.status) }}
                        </span>
                    </div>
                    <div class="col-enrolled">{{ formatDate(student.enrollDate) }}</div>
                    <div class="col-actions">
                        <button @click="viewStudent(student)" class="btn-action view" title="Xem">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button @click="editStudent(student)" class="btn-action edit" title="Sửa">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button @click="removeStudent(student.id)" class="btn-action delete" title="Xóa">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CourseStudents',
    data() {
        return {
            courseName: 'JavaScript Fundamentals',
            students: [],
            loading: true,
            searchQuery: '',
            filterStatus: '',
            sortBy: 'name'
        }
    },
    computed: {
        filteredStudents() {
            let filtered = [...this.students]

            // Filter by search query
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                filtered = filtered.filter(s =>
                    s.name.toLowerCase().includes(query) ||
                    s.email.toLowerCase().includes(query)
                )
            }

            // Filter by status
            if (this.filterStatus) {
                filtered = filtered.filter(s => s.status === this.filterStatus)
            }

            // Sort
            if (this.sortBy === 'name') {
                filtered.sort((a, b) => a.name.localeCompare(b.name))
            } else if (this.sortBy === 'enrollDate') {
                filtered.sort((a, b) => new Date(b.enrollDate) - new Date(a.enrollDate))
            } else if (this.sortBy === 'progress') {
                filtered.sort((a, b) => b.progress - a.progress)
            }

            return filtered
        },

        totalStudents() {
            return this.students.length
        },

        activeCount() {
            return this.students.filter(s => s.status === 'active').length
        },

        completedCount() {
            return this.students.filter(s => s.status === 'completed').length
        },

        averageProgress() {
            if (this.students.length === 0) return 0
            const sum = this.students.reduce((acc, s) => acc + s.progress, 0)
            return Math.round(sum / this.students.length)
        }
    },
    mounted() {
        this.loadStudents()
    },
    methods: {
        async loadStudents() {
            this.loading = true
            try {
                const courseId = this.$route.params.id
                
                // Mock data - thay bằng API call thực
                const mockStudents = [
                    {
                        id: 1,
                        name: 'Nguyễn Văn A',
                        email: 'nguyenvana@example.com',
                        progress: 85,
                        status: 'active',
                        enrollDate: new Date('2024-01-15'),
                        avatarColor: '#3498db'
                    },
                    {
                        id: 2,
                        name: 'Trần Thị B',
                        email: 'tranthib@example.com',
                        progress: 100,
                        status: 'completed',
                        enrollDate: new Date('2024-01-01'),
                        avatarColor: '#e74c3c'
                    },
                    {
                        id: 3,
                        name: 'Lê Văn C',
                        email: 'levanc@example.com',
                        progress: 45,
                        status: 'active',
                        enrollDate: new Date('2024-01-20'),
                        avatarColor: '#2ecc71'
                    },
                    {
                        id: 4,
                        name: 'Phạm Hữu D',
                        email: 'phamhuud@example.com',
                        progress: 0,
                        status: 'inactive',
                        enrollDate: new Date('2024-01-10'),
                        avatarColor: '#f39c12'
                    }
                ]

                this.students = mockStudents
            } catch (error) {
                console.error('Lỗi khi tải danh sách học viên:', error)
            }
            this.loading = false
        },

        getStatusText(status) {
            const map = {
                active: 'Đang học',
                completed: 'Hoàn thành',
                inactive: 'Không hoạt động'
            }
            return map[status] || status
        },

        formatDate(date) {
            return new Date(date).toLocaleDateString('vi-VN')
        },

        viewStudent(student) {
            console.log('Viewing student:', student)
            // Navigate to student detail page
        },

        editStudent(student) {
            console.log('Editing student:', student)
            // Navigate to edit student page
        },

        async removeStudent(studentId) {
            if (confirm('Bạn có chắc muốn xóa học viên này khỏi khóa học?')) {
                try {
                    this.students = this.students.filter(s => s.id !== studentId)
                    this.$toast.success('Đã xóa học viên')
                } catch (error) {
                    console.error('Lỗi khi xóa học viên:', error)
                }
            }
        },

        goBack() {
            this.$router.back()
        }
    }
}
</script>

<style scoped>
.course-students {
    min-height: 100vh;
    background: #f8f9fa;
}

.students-header {
    background: white;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
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

.students-header h1 {
    margin: 0;
    color: #2c3e50;
    font-size: 24px;
}

.students-container {
    max-width: 1200px;
    margin: 30px auto;
    padding: 0 20px;
}

.filters {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 30px;
    display: flex;
    gap: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    flex-wrap: wrap;
}

.filter-group {
    flex: 1;
    min-width: 250px;
    position: relative;
}

.search-input,
.filter-group select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
}

.search-input:focus,
.filter-group select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.filter-group i {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #999;
    pointer-events: none;
}

.stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    padding: 24px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.stat-number {
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 8px;
}

.stat-label {
    font-size: 14px;
    opacity: 0.9;
}

.loading {
    text-align: center;
    padding: 60px 20px;
    background: white;
    border-radius: 12px;
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

.no-students {
    text-align: center;
    padding: 60px 20px;
    background: white;
    border-radius: 12px;
    color: #999;
}

.students-table {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.table-header {
    display: grid;
    grid-template-columns: 2fr 2fr 1.5fr 1fr 1.5fr 1fr;
    gap: 16px;
    padding: 16px 20px;
    background: #f8f9fa;
    font-weight: 600;
    color: #555;
    border-bottom: 1px solid #eee;
}

.table-row {
    display: grid;
    grid-template-columns: 2fr 2fr 1.5fr 1fr 1.5fr 1fr;
    gap: 16px;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #eee;
    transition: background 0.3s;
}

.table-row:hover {
    background: #f8f9fa;
}

.table-row:last-child {
    border-bottom: none;
}

.col-name {
    display: flex;
    align-items: center;
    gap: 12px;
}

.student-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
}

.col-progress {
    display: flex;
    align-items: center;
    gap: 12px;
}

.progress-bar {
    flex: 1;
    height: 6px;
    background: #eee;
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #2ecc71);
    transition: width 0.3s;
}

.progress-text {
    min-width: 40px;
    text-align: right;
    font-weight: 500;
    color: #555;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

.badge.active {
    background: #e8f5e8;
    color: #388e3c;
}

.badge.completed {
    background: #e3f2fd;
    color: #1976d2;
}

.badge.inactive {
    background: #f5f5f5;
    color: #999;
}

.col-actions {
    display: flex;
    gap: 8px;
    justify-content: center;
}

.btn-action {
    width: 36px;
    height: 36px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    font-size: 14px;
}

.btn-action.view {
    background: #e3f2fd;
    color: #1976d2;
}

.btn-action.view:hover {
    background: #1976d2;
    color: white;
}

.btn-action.edit {
    background: #fff3e0;
    color: #f57c00;
}

.btn-action.edit:hover {
    background: #f57c00;
    color: white;
}

.btn-action.delete {
    background: #ffebee;
    color: #d32f2f;
}

.btn-action.delete:hover {
    background: #d32f2f;
    color: white;
}

@media (max-width: 1024px) {
    .table-header,
    .table-row {
        grid-template-columns: 1.5fr 1.5fr 1fr 1fr 0.5fr;
    }

    .col-enrolled {
        display: none;
    }
}

@media (max-width: 768px) {
    .students-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .filters {
        flex-direction: column;
    }

    .filter-group {
        min-width: 100%;
    }

    .table-header,
    .table-row {
        grid-template-columns: 1fr;
        gap: 12px;
    }

    .table-header {
        display: none;
    }

    .table-row {
        border: 1px solid #eee;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    .table-row > div::before {
        content: attr(data-label);
        font-weight: 600;
        color: #555;
        display: block;
        margin-bottom: 4px;
    }
}
</style>
