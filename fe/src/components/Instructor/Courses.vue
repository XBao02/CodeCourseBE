<template>
    <div class="instructor-courses">
        <div class="courses-header">
            <h1>Manage Courses</h1>
            <button @click="createNewCourse" class="btn-create">
                Create New Course
            </button>
        </div>

        <div class="courses-filter">
            <div class="filter-group">
                <label>Status:</label>
                <select v-model="filterStatus" @change="filterCourses">
                    <option value="all">All</option>
                    <option value="active">Active</option>
                    <option value="draft">Draft</option>
                    <option value="archived">Archived</option>
                </select>
            </div>

            <div class="search-group">
                <input type="text" v-model="searchQuery" placeholder="Search courses..." @input="searchCourses">
            </div>
        </div>

        <div class="courses-list">
            <div v-if="loading" class="loading">Loading...</div>

            <div v-else-if="filteredCourses.length === 0" class="no-courses">
                <p>No courses found</p>
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
                            <span>{{ course.students }} Students</span>
                            <span>Rating: {{ course.rating }}</span>
                            <span>{{ Number(course.price).toLocaleString('vi-VN') }}đ</span>
                        </div>

                        <div class="course-meta">
                            <span>Updated: {{ formatDate(course.updatedAt) }}</span>
                        </div>
                    </div>

                    <div class="course-actions">
                        <button @click="editCourse(course.id)" class="btn-edit">Edit</button>
                        <button @click="goLessons(course.id)" class="btn-content">Content</button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="showCourseModal" class="modal-overlay">
            <div class="modal-content">
                <h2>{{ editingCourse ? 'Edit Course' : 'Create New Course' }}</h2>

                <form @submit.prevent="saveCourse">
                    <div class="form-group">
                        <label>Course Title:</label>
                        <input type="text" v-model="courseForm.title" required>
                    </div>

                    <div class="form-group">
                        <label>Description:</label>
                        <textarea v-model="courseForm.description" rows="4"></textarea>
                    </div>

                    <div class="form-group">
                        <label>Price (VND):</label>
                        <input type="number" v-model="courseForm.price" min="0">
                    </div>

                    <div class="form-group">
                        <label>Thumbnail URL:</label>
                        <input type="url" v-model="courseForm.thumbnail">
                    </div>

                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
                        <button type="submit" class="btn-save">{{ editingCourse ? 'Update' : 'Create' }}</button>
                    </div>
                </form>
            </div>
        </div>

        <div v-if="showContentModal" class="modal-overlay content-modal">
            <div class="modal-content content-modal-content">
                <div class="modal-header">
                    <h2>Create Course Content: {{ selectedCourse?.title }}</h2>
                    <button @click="closeContentModal" class="btn-close">✕</button>
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
import { getStoredSession } from '../../services/authService'

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
        this.loadCourses()
    },
    methods: {
        getAuthHeaders() {
            const session = getStoredSession()
            if (!session?.access_token) {
                throw new Error('No authentication token found')
            }
            return {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json'
            }
        },
        
        async loadCourses() {
            this.loading = true
            this.courses = []
            this.filteredCourses = []
            try {
                const headers = this.getAuthHeaders()
                // Backend now uses instructor ID from JWT token
                const res = await fetch('http://localhost:5000/api/courses', { headers }) 
                
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
            const statusMap = {
                active: 'Active',
                draft: 'Draft',
                archived: 'Archived'
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
            this.$router.push(`/instructor/courses/${courseId}/lessons`)
        },

        manageStudents(courseId) {
            this.$router.push(`/instructor/courses/${courseId}/students`)
        },

        async toggleArchive(courseId, currentStatus) {
            try {
                const headers = this.getAuthHeaders()
                const isArchived = currentStatus === 'archived'
                const res = await fetch(`http://localhost:5000/api/courses/${courseId}/archive`, {
                    method: 'PUT',
                    headers,
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
            try {
                const headers = this.getAuthHeaders()
                
                // Backend sẽ lấy instructor_id từ JWT token
                const payload = {
                    ...this.courseForm,
                    price: Number(this.courseForm.price),
                    status: this.courseForm.status || 'draft',
                    level: 'beginner',
                    currency: 'VND'
                };

                const url = 'http://localhost:5000/api/courses';
                let res;
                let data;

                if (this.editingCourse) {
                    // Cập nhật khóa học
                    const updateUrl = `${url}/${this.editingCourse}`;
                    res = await fetch(updateUrl, {
                        method: 'PUT',
                        headers,
                        body: JSON.stringify(payload)
                    });
                } else {
                    // Tạo khóa học mới
                    res = await fetch(url, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify(payload)
                    });
                }

                data = await res.json();

                if (!res.ok) {
                    throw new Error(data.message || `Lỗi khi lưu khóa học (HTTP ${res.status})`);
                }

                this.closeModal();
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

        manageStudents(courseId) {
            this.$router.push(`/instructor/courses/${courseId}/students`)
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
    padding: 40px;
    margin: 0 auto;
    background: #f8f9fa;
    min-height: 100vh;
}

.courses-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40px;
    flex-wrap: wrap;
    gap: 20px;
}

.courses-header h1 {
    font-size: 32px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
    letter-spacing: -0.5px;
}

.btn-create {
    background: #1f2937;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.btn-create:hover {
    background: #111827;
}

.courses-filter {
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
    align-items: center;
    flex-wrap: wrap;
}

.filter-group,
.search-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.filter-group label {
    font-weight: 500;
    color: #374151;
}

.filter-group select,
.search-group input {
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    background: white;
    color: #1f2937;
}

.search-group input {
    width: 250px;
}

.search-group input::placeholder {
    color: #9ca3af;
}

.courses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 24px;
}

.course-card {
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    overflow: hidden;
    transition: all 0.3s ease;
}

.course-card:hover {
    border-color: #d1d5db;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.course-image {
    position: relative;
    height: 180px;
    background: #f0f0f0;
}

.course-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.course-status {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.course-status.active {
    background: #d1fae5;
    color: #1f2937;
}

.course-status.draft {
    background: #fef3c7;
    color: #d97706;
}

.course-status.archived {
    background: #e5e7eb;
    color: #6b7280;
}

.course-content {
    padding: 20px;
}

.course-content h3 {
    margin: 0 0 12px 0;
    color: #1a1a1a;
    font-size: 16px;
    font-weight: 600;
}

.course-description {
    color: #666;
    margin-bottom: 14px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    font-size: 14px;
    line-height: 1.4;
}

.course-stats {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 13px;
    color: #666;
}

.course-meta {
    font-size: 12px;
    color: #999;
}

.course-actions {
    padding: 16px 20px;
    border-top: 1px solid #e5e7eb;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.course-actions button {
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    color: #374151;
    transition: all 0.2s ease;
}

.btn-edit {
    background: white;
    border: 1px solid #d1d5db;
    color: #1f2937;
}

.btn-edit:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

.btn-content {
    background: white;
    border: 1px solid #d1d5db;
    color: #1f2937;
}

.btn-content:hover {
    background: #f9fafb;
    border-color: #9ca3af;
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
    padding: 32px;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
}

.modal-content h2 {
    margin-bottom: 24px;
    color: #1a1a1a;
    font-size: 20px;
    font-weight: 600;
}

.form-group {
    margin-bottom: 18px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #374151;
    font-size: 14px;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    box-sizing: border-box;
    font-size: 14px;
    color: #1f2937;
    font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 24px;
}

.btn-cancel,
.btn-save {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.btn-cancel {
    background: #e5e7eb;
    color: #374151;
    border: 1px solid #d1d5db;
}

.btn-cancel:hover {
    background: #d1d5db;
}

.btn-save {
    background: #1f2937;
    color: white;
    border: 1px solid #1f2937;
}

.btn-save:hover {
    background: #111827;
}

/* Content Modal Styles */
.content-modal .modal-content {
    max-width: 95vw;
    width: 95vw;
    max-height: 95vh;
    height: 95vh;
    display: flex;
    flex-direction: column;
    padding: 0;
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
    padding: 24px;
    border-bottom: 1px solid #e5e7eb;
    flex-shrink: 0;
}

.content-modal .modal-header h2 {
    margin: 0;
    color: #1a1a1a;
    font-size: 18px;
    font-weight: 600;
}

.btn-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
}

.btn-close:hover {
    background: #f0f0f0;
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
    padding: 60px 20px;
    color: #999;
}

.loading {
    font-size: 16px;
}

.no-courses {
    font-size: 15px;
}

@media (max-width: 768px) {
    .instructor-courses {
        padding: 20px;
    }

    .courses-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .courses-filter {
        flex-direction: column;
        align-items: stretch;
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

    .modal-content {
        width: 95%;
        padding: 24px;
    }
}
</style>