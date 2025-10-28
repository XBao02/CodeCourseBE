<template>
    <div class="instructor-courses">
        <div class="courses-header">
            <h1>Quản lý Khóa học</h1>
            <button @click="createNewCourse" class="btn-create">
                <i class="fas fa-plus"></i>
                Tạo khóa học mới
            </button>
        </div>

        <div class="courses-filter">
            <div class="filter-group">
                <label>Trạng thái:</label>
                <select v-model="filterStatus" @change="filterCourses">
                    <option value="all">Tất cả</option>
                    <option value="active">Đang hoạt động</option>
                    <option value="draft">Bản nháp</option>
                    <option value="archived">Đã lưu trữ</option>
                </select>
            </div>

            <div class="search-group">
                <input type="text" v-model="searchQuery" placeholder="Tìm kiếm khóa học..." @input="searchCourses">
                <i class="fas fa-search"></i>
            </div>
        </div>

        <div class="courses-list">
            <div v-if="loading" class="loading">Đang tải...</div>

            <div v-else-if="filteredCourses.length === 0" class="no-courses">
                <p>Không có khóa học nào được tìm thấy.</p>
            </div>

            <div v-else class="courses-grid">
                <div v-for="course in filteredCourses" :key="course.id" class="course-card">
                    <div class="course-image">
                        <img :src="course.thumbnail" :alt="course.title" />
                        <div class="course-status" :class="course.status">
                            {{ getStatusText(course.status) }}
                        </div>
                    </div>

                    <div class="course-content">
                        <h3>{{ course.title }}</h3>
                        <p class="course-description">{{ course.description }}</p>

                        <div class="course-stats">
                            <span><i class="fas fa-users"></i> {{ course.students }} học viên</span>
                            <span><i class="fas fa-star"></i> {{ course.rating }}</span>
                            <span><i class="fas fa-dollar-sign"></i> {{ Number(course.price).toLocaleString('vi-VN') }}</span>
                        </div>

                        <div class="course-meta">
                            <span>Cập nhật: {{ formatDate(course.updatedAt) }}</span>
                        </div>
                    </div>

                    <div class="course-actions">
                        <button @click="editCourse(course.id)" class="btn-edit">
                            <i class="fas fa-edit"></i> Sửa
                        </button>
                        <button @click="goLessons(course.id)" class="btn-content">
                            <i class="fas fa-pen-nib"></i> Soạn nội dung
                        </button>
                        <button @click="viewCourse(course.id)" class="btn-view">
                            <i class="fas fa-eye"></i> Xem
                        </button>
                        <button @click="manageStudents(course.id)" class="btn-students">
                            <i class="fas fa-users"></i> Học viên
                        </button>
                        <button @click="toggleArchive(course.id, course.status)"
                            :class="['btn-archive', course.status === 'archived' ? 'btn-unarchive' : '']">
                            <i :class="course.status === 'archived' ? 'fas fa-box-open' : 'fas fa-archive'"></i>
                            {{ course.status === 'archived' ? 'Bỏ lưu trữ' : 'Lưu trữ' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="showCourseModal" class="modal-overlay">
            <div class="modal-content">
                <h2>{{ editingCourse ? 'Sửa khóa học' : 'Tạo khóa học mới' }}</h2>

                <form @submit.prevent="saveCourse">
                    <div class="form-group">
                        <label>Tiêu đề khóa học:</label>
                        <input type="text" v-model="courseForm.title" required>
                    </div>

                    <div class="form-group">
                        <label>Mô tả:</label>
                        <textarea v-model="courseForm.description" rows="4"></textarea>
                    </div>

                    <div class="form-group">
                        <label>Giá (VND):</label>
                        <input type="number" v-model="courseForm.price" min="0">
                    </div>

                    <div class="form-group">
                        <label>Ảnh thumbnail URL:</label>
                        <input type="url" v-model="courseForm.thumbnail">
                    </div>

                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-cancel">Hủy</button>
                        <button type="submit" class="btn-save">{{ editingCourse ? 'Cập nhật' : 'Tạo' }}</button>
                    </div>
                </form>
            </div>
        </div>

        <div v-if="showContentModal" class="modal-overlay content-modal">
            <div class="modal-content content-modal-content">
                <div class="modal-header">
                    <h2>Soạn nội dung khóa học: {{ selectedCourse?.title }}</h2>
                    <button @click="closeContentModal" class="btn-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <ContentCreator 
                        v-if="selectedCourse" 
                        :course="selectedCourse"
                        @close="closeContentModal"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import ContentCreator from './ContentCreator.vue'

export default {
    name: 'InstructorCourses',
    components: {
        ContentCreator
    },
    data() {
        return {
            courses: [],
            filteredCourses: [],
            loading: true,
            filterStatus: 'all',
            searchQuery: '',
            showCourseModal: false,
            showContentModal: false,
            editingCourse: null,
            selectedCourse: null,
            courseForm: {
                title: '',
                description: '',
                price: 0,
                thumbnail: ''
            }
        }
    },
    mounted() {
        // GỌI CHỨC NĂNG LOAD KHI COMPONENT ĐƯỢC TẠO
        this.loadCourses()
    },
    methods: {
        async loadCourses() {
            this.loading = true
            this.courses = []
            this.filteredCourses = []
            try {
                // ĐÃ XÁC NHẬN URL VÀ ENDPOINT HOẠT ĐỘNG
                const res = await fetch('http://localhost:5000/api/courses?instructor_id=2') 
                
                if (!res.ok) {
                    const errorData = await res.json()
                    throw new Error(errorData.message || `Lỗi HTTP: ${res.status}`)
                }
                
                const data = await res.json()
                
                // CẬP NHẬT DỮ LIỆU
                this.courses = data
                this.filteredCourses = data
                console.log('Khóa học đã tải:', this.courses)
            } catch (error) {
                console.error('Lỗi khi tải khóa học:', error)
                // Thông báo lỗi nếu cần
                // alert(`Không thể tải khóa học. Chi tiết: ${error.message}`) 
            }
            this.loading = false
        },

        filterCourses() {
            // Logic lọc (đã đúng)
            if (this.filterStatus === 'all') {
                this.filteredCourses = this.courses
            } else {
                this.filteredCourses = this.courses.filter(course =>
                    course.status === this.filterStatus
                )
            }
        },

        searchCourses() {
            // Logic tìm kiếm (đã đúng)
            const query = this.searchQuery.toLowerCase()
            this.filteredCourses = this.courses.filter(course =>
                course.title.toLowerCase().includes(query) ||
                course.description.toLowerCase().includes(query)
            )
        },

        getStatusText(status) {
            // Logic map status (đã đúng)
            const statusMap = {
                active: 'Đang hoạt động',
                draft: 'Bản nháp',
                archived: 'Đã lưu trữ'
            }
            return statusMap[status] || status
        },

        formatDate(date) {
            // Logic format ngày (đã sửa lỗi format trước đó)
            if (!date) return 'N/A'
            const d = new Date(date);
            if (isNaN(d.getTime())) {
                return 'Ngày không hợp lệ';
            }
            return d.toLocaleDateString('vi-VN')
        },

        createNewCourse() {
            this.editingCourse = null
            this.courseForm = {
                title: '',
                description: '',
                price: 0,
                thumbnail: ''
            }
            this.showCourseModal = true
        },

        editCourse(courseId) {
            const course = this.courses.find(c => c.id === courseId)
            if (course) {
                this.editingCourse = courseId
                this.courseForm = { ...course }
                this.showCourseModal = true
            }
        },

        viewCourse(courseId) {
            this.$router.push(`/instructor/courses/${courseId}`)
        },

        manageStudents(courseId) {
            this.$router.push(`/instructor/courses/${courseId}/students`)
        },

        async toggleArchive(courseId, currentStatus) {
            try {
                const isArchived = currentStatus === 'archived'
                const res = await fetch(`http://localhost:5000/api/courses/${courseId}/archive`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ is_archived: !isArchived })
                })
                const data = await res.json()
                if (!res.ok) throw new Error(data.message || 'Không thể cập nhật trạng thái')

                // cập nhật lại danh sách từ server để đồng bộ
                await this.loadCourses()
                alert('Đã cập nhật trạng thái khóa học')
            } catch (error) {
                console.error('Lỗi khi cập nhật trạng thái:', error)
                alert(`Lỗi: ${error.message}`)
            }
        },

        async saveCourse() {
            // Xác định Instructor ID. Giả định ID là 2 như trong các yêu cầu trước.
            // Trong ứng dụng thực tế, ID này sẽ được lấy từ state/token đăng nhập.
            const instructorId = 2; 

            // Chuẩn bị payload data từ form
            const payload = {
                ...this.courseForm,
                price: Number(this.courseForm.price), // Đảm bảo giá là số
                instructor_id: instructorId,
                // Giả định khóa học mới mặc định là bản nháp
                status: 'draft', 
                // Có thể thêm level, currency nếu form có field đó
                level: 'beginner',
                currency: 'VND'
            };

            try {
                const url = 'http://localhost:5000/api/courses';
                let res;
                let data;

                if (this.editingCourse) {
                    // --- CHỨC NĂNG CẬP NHẬT (PUT) ---
                    // Cần có endpoint PUT /api/courses/{id} và xử lý logic backend tương ứng
                    const updateUrl = `${url}/${this.editingCourse}`;
                    res = await fetch(updateUrl, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                } else {
                    // --- CHỨC NĂNG TẠO MỚI (POST) ---
                    res = await fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                }

                data = await res.json();

                if (!res.ok) {
                    // Xử lý lỗi trả về từ backend (400, 500)
                    throw new Error(data.message || `Lỗi khi lưu khóa học (HTTP ${res.status})`);
                }

                // --- Cập nhật UI sau khi Backend thành công ---
                this.closeModal();
                // Tải lại toàn bộ danh sách khóa học để hiển thị khóa học mới
                await this.loadCourses(); 
                
                alert(`Khóa học "${data.title}" đã được ${this.editingCourse ? 'cập nhật' : 'tạo'} thành công!`);

            } catch (error) {
                console.error('Lỗi khi lưu khóa học:', error);
                alert(`Lỗi: ${error.message}`);
            }
        },

        goLessons(courseId) {
            this.$router.push(`/instructor/courses/${courseId}/lessons`)
        },

        createContent(course) {
            // deprecated in favor of goLessons route
            this.$router.push(`/instructor/courses/${course.id}/lessons`)
        },

        closeContentModal() {
            this.showContentModal = false
            this.selectedCourse = null
        },

        closeModal() {
            this.showCourseModal = false
            this.editingCourse = null
        }
    }
}
</script>

<style scoped>
.instructor-courses {
    width: 100%;
    padding: 20px;
    margin: 0 auto;
}

.courses-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.btn-create {
    background: #3498db;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
}

.courses-filter {
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
    align-items: center;
}

.filter-group,
.search-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.filter-group label {
    font-weight: bold;
}

.filter-group select,
.search-group input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-group {
    position: relative;
}

.search-group input {
    padding-left: 35px;
    width: 250px;
}

.search-group i {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #7f8c8d;
}

.courses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}

.course-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.course-image {
    position: relative;
    height: 200px;
}

.course-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.course-status {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.course-status.active {
    background: #27ae60;
    color: white;
}

.course-status.draft {
    background: #f39c12;
    color: white;
}

.course-status.archived {
    background: #95a5a6;
    color: white;
}

.course-content {
    padding: 15px;
}

.course-content h3 {
    margin: 0 0 10px 0;
    color: #2c3e50;
}

.course-description {
    color: #7f8c8d;
    margin-bottom: 15px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.course-stats {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    font-size: 14px;
    color: #7f8c8d;
}

.course-stats span {
    display: flex;
    align-items: center;
    gap: 5px;
}

.course-meta {
    font-size: 12px;
    color: #bdc3c7;
}

.course-actions {
    padding: 15px;
    border-top: 1px solid #ecf0f1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.course-actions button {
    padding: 8px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    transition: all 0.3s;
}

.btn-edit {
    background: #3498db;
    color: white;
}

.btn-view {
    background: #2ecc71;
    color: white;
}

.btn-students {
    background: #9b59b6;
    color: white;
}

.btn-archive {
    background: #e74c3c;
    color: white;
}

.btn-unarchive {
    background: #f39c12;
}

.course-actions button:hover {
    opacity: 0.9;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 30px;
    border-radius: 10px;
    width: 90%;
    max-width: 500px;
}

.modal-content h2 {
    margin-bottom: 20px;
    color: #2c3e50;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
}

.form-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
}

.btn-cancel,
.btn-save {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-cancel {
    background: #95a5a6;
    color: white;
}

.btn-save {
    background: #3498db;
    color: white;
}

.btn-content {
    background: #9b59b6;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s;
}

.btn-content:hover {
    background: #8e44ad;
    transform: translateY(-2px);
}

/* Content Modal Styles */
.content-modal .modal-content {
    max-width: 95vw;
    width: 95vw;
    max-height: 95vh;
    height: 95vh;
    display: flex;
    flex-direction: column;
}

.content-modal-content {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.content-modal .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #eee;
    flex-shrink: 0;
}

.content-modal .modal-header h2 {
    margin: 0;
    color: #2c3e50;
    font-size: 20px;
}

.btn-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #999;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.3s;
}

.btn-close:hover {
    background: #f8f9fa;
    color: #333;
}

.content-modal .modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 0;
}

.loading,
.no-courses {
    text-align: center;
    padding: 40px;
    color: #7f8c8d;
}

@media (max-width: 768px) {
    .courses-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
    }

    .courses-filter {
        flex-direction: column;
        align-items: flex-start;
    }

    .search-group input {
        width: 100%;
    }

    .courses-grid {
        grid-template-columns: 1fr;
    }

    .course-actions {
        grid-template-columns: 1fr;
    }
}
</style>