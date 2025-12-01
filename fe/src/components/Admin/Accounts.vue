<template>
    <div class="student-management">
        <!-- Header -->
        <div class="page-header">
            <div class="header-content">
                <div class="title-section">
                    <h1 class="page-title">🎓 Student Management</h1>
                    <p class="page-subtitle">Manage student information and enrollment details</p>
                </div>
                <div class="header-actions">
                    <div class="search-box">
                        <i class="fas fa-search search-icon"></i>
                        <input 
                            v-model="searchQuery" 
                            type="text" 
                            class="search-input" 
                            placeholder="Search students..." 
                        />
                    </div>
                    <button class="btn btn-primary btn-add-student" @click="showAddForm = true">
                        <i class="fas fa-user-plus"></i>
                        Add New Student
                    </button>
                </div>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-overview">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon total-students">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ students.length }}</h3>
                        <p>Total Students</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon active-students">
                        <i class="fas fa-user-check"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ activeStudentsCount }}</h3>
                        <p>Active Students</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon courses">
                        <i class="fas fa-book-open"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ uniqueCoursesCount }}</h3>
                        <p>Active Courses</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon completion">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ averageProgress }}%</h3>
                        <p>Avg. Progress</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add/Edit Form -->
        <div v-if="showAddForm || editingStudent" class="form-section">
            <div class="form-card">
                <div class="form-header">
                    <h3>{{ editingStudent ? "Edit Student" : "Add New Student" }}</h3>
                    <button class="btn-close" @click="cancelEdit">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form @submit.prevent="saveStudent" class="student-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Full Name *</label>
                            <input v-model="form.name" type="text" class="form-control" required />
                        </div>
                        <div class="form-group">
                            <label class="form-label">Email *</label>
                            <input v-model="form.email" type="email" class="form-control" required />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Course *</label>
                            <select v-model="form.courseId" class="form-control" required>
                                <option value="">Select Course</option>
                                <option v-for="course in availableCourses" :key="course.id" :value="course.id">
                                    {{ course.name }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Phone *</label>
                            <input v-model="form.phone" type="tel" class="form-control" required />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label class="form-label">Address *</label>
                            <input v-model="form.address" type="text" class="form-control" required />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Enrollment Date</label>
                            <input v-model="form.enrollmentDate" type="date" class="form-control" />
                        </div>
                        <div class="form-group">
                            <label class="form-label">Status</label>
                            <select v-model="form.status" class="form-control">
                                <option value="Active">Active</option>
                                <option value="Inactive">Inactive</option>
                                <option value="Completed">Completed</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i>
                            {{ editingStudent ? "Update Student" : "Add Student" }}
                        </button>
                        <button type="button" class="btn btn-secondary" @click="cancelEdit">
                            <i class="fas fa-times"></i>
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Students Table -->
        <div class="table-container">
            <div class="table-card">
                <div class="table-header">
                    <h3>Student List</h3>
                    <div class="table-actions">
                        <button class="btn btn-outline">
                            <i class="fas fa-download"></i>
                            Export
                        </button>
                        <button class="btn btn-outline">
                            <i class="fas fa-filter"></i>
                            Filter
                        </button>
                    </div>
                </div>

                <div class="table-responsive">
                    <div v-if="errorMessage" class="alert alert-warning" role="alert">
                        {{ errorMessage }}
                    </div>
                    <div v-if="isLoading" class="loading-state">Loading data...</div>
                    <table v-else class="students-table">
                        <thead>
                            <tr>
                                <th class="student-info">Student Info</th>
                                <th class="course">Course</th>
                                <th class="contact">Contact</th>
                                <th class="progress">Progress</th>
                                <th class="status">Status</th>
                                <th class="actions">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="student in filteredStudents" :key="student.id" class="student-row">
                                <td class="student-info">
                                    <div class="student-avatar">
                                        {{ getInitials(student.name) }}
                                    </div>
                                    <div class="student-details">
                                        <span class="student-name">{{ student.name }}</span>
                                        <span class="student-email">{{ student.email }}</span>
                                        <span class="student-id">ID: {{ student.id }}</span>
                                    </div>
                                </td>
                                <td class="course">
                                    <div class="course-info">
                                        <div class="course-icon">
                                            <i class="fas fa-book"></i>
                                        </div>
                                        <span class="course-name">{{ getCourseName(student.courseId) || student.course }}</span>
                                    </div>
                                    <div class="enrollment-date">
                                        {{ formatDate(student.enrollmentDate) }}
                                    </div>
                                </td>
                                <td class="contact">
                                    <div class="contact-info">
                                        <div class="phone">
                                            <i class="fas fa-phone"></i>
                                            {{ student.phone }}
                                        </div>
                                        <div class="address">
                                            <i class="fas fa-map-marker-alt"></i>
                                            {{ student.address }}
                                        </div>
                                    </div>
                                </td>
                                <td class="progress">
                                    <div class="progress-container">
                                        <div class="progress-bar">
                                            <div class="progress-fill" :style="{ width: student.progress + '%' }"></div>
                                        </div>
                                        <span class="progress-text">{{ student.progress }}%</span>
                                    </div>
                                </td>
                                <td class="status">
                                    <span class="status-badge" :class="student.status.toLowerCase()">
                                        <i :class="getStatusIcon(student.status)"></i>
                                        {{ student.status }}
                                    </span>
                                </td>
                                <td class="actions">
                                    <div class="action-buttons">
                                        <button class="btn-action btn-edit" @click="editStudent(student)" title="Edit Student">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn-action btn-view" @click="viewStudent(student)" title="View Details">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn-action btn-delete" @click="deleteStudent(student.id)" title="Delete Student">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Empty State -->
                <div v-if="filteredStudents.length === 0" class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-user-graduate"></i>
                    </div>
                    <h3>No students found</h3>
                    <p>Try adjusting your search or add a new student</p>
                    <button class="btn btn-primary" @click="showAddForm = true">
                        <i class="fas fa-user-plus"></i>
                        Add First Student
                    </button>
                </div>

                <!-- Table Footer -->
                <div v-if="filteredStudents.length > 0" class="table-footer">
                    <div class="pagination-info">
                        Showing {{ filteredStudents.length }} of {{ students.length }} students
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import adminService from '@/services/adminService'

export default {
    name: "StudentManagement",
    setup() {
        const students = ref([])
        const availableCourses = ref([])
        const searchQuery = ref("")
        const showAddForm = ref(false)
        const editingStudent = ref(null)
        const isLoading = ref(false)
        const errorMessage = ref("")
        const form = ref({
            id: null,
            name: "",
            email: "",
            courseId: "",
            phone: "",
            address: "",
            enrollmentDate: new Date().toISOString().split('T')[0],
            status: "Active",
            progress: 0
        })

        const courseLookup = computed(() => {
            const map = new Map()
            availableCourses.value.forEach((c) => map.set(c.id, c.name || c.title || c.id))
            return map
        })

        const normalizeStudent = (student) => ({
            id: student.id,
            name: student.name || "",
            email: student.email || "",
            courseId: student.courseId || student.course_id || null,
            course: student.course || "",
            phone: student.phone || "",
            address: student.address || "",
            enrollmentDate: student.enrollmentDate ? student.enrollmentDate.slice(0, 10) : "",
            status: student.status ? student.status.charAt(0).toUpperCase() + student.status.slice(1) : (student.isActive ? "Active" : "Inactive"),
            progress: Number(student.progress ?? 0),
            isActive: student.isActive ?? true
        })

        const loadCourses = async () => {
            const res = await adminService.getCourses()
            availableCourses.value = res.map((course) => ({
                id: course.id,
                name: course.title
            }))
        }

        const loadStudents = async () => {
            const res = await adminService.getStudents()
            students.value = res.map(normalizeStudent)
        }

        const loadData = async () => {
            isLoading.value = true
            errorMessage.value = ""
            try {
                try {
                    await loadCourses()
                } catch (error) {
                    errorMessage.value = error.message || "Không thể tải danh sách khóa học"
                }
                await loadStudents()
            } catch (error) {
                errorMessage.value = error.message || "Không thể tải danh sách học viên"
            } finally {
                isLoading.value = false
            }
        }

        const filteredStudents = computed(() => {
            const list = students.value
            if (!searchQuery.value) {
                return list
            }
            const query = searchQuery.value.toLowerCase()
            return list.filter(student => 
                (student.name || "").toLowerCase().includes(query) || 
                (student.email || "").toLowerCase().includes(query) ||
                (student.course || "").toLowerCase().includes(query) ||
                (student.phone || "").includes(query)
            )
        })

        const activeStudentsCount = computed(() => {
            return students.value.filter(student => (student.status || "").toLowerCase() === "active" || student.isActive).length
        })

        const uniqueCoursesCount = computed(() => {
            const courses = new Set(students.value.map(student => student.courseId || student.course).filter(Boolean))
            return courses.size
        })

        const averageProgress = computed(() => {
            if (students.value.length === 0) return 0
            const total = students.value.reduce((sum, student) => sum + (Number(student.progress) || 0), 0)
            return Math.round(total / students.value.length)
        })

        const getInitials = (name = "") => {
            return name.split(' ').filter(Boolean).map(n => n[0]).join('').toUpperCase()
        }

        const getStatusIcon = (status) => {
            const normalized = (status || "").toLowerCase()
            if (normalized === "active") return "fas fa-check-circle"
            if (normalized === "completed") return "fas fa-trophy"
            if (normalized === "inactive") return "fas fa-pause-circle"
            return "fas fa-user"
        }

        const formatDate = (dateString) => {
            if (!dateString) return 'N/A'
            const options = { year: 'numeric', month: 'short', day: 'numeric' }
            return new Date(dateString).toLocaleDateString('en-US', options)
        }

        const getCourseName = (courseId) => {
            if (!courseId) return ""
            return courseLookup.value.get(courseId) || ""
        }

        const saveStudent = async () => {
            const payload = {
                name: form.value.name,
                email: form.value.email,
                phone: form.value.phone,
                address: form.value.address,
                courseId: form.value.courseId || null,
                status: form.value.status,
                progress: Number(form.value.progress) || 0,
                isActive: form.value.status !== "Inactive"
            }

            try {
                if (editingStudent.value) {
                    const updated = await adminService.updateStudent(editingStudent.value.id, payload)
                    const idx = students.value.findIndex(s => s.id === editingStudent.value.id)
                    if (idx >= 0) {
                        students.value.splice(idx, 1, normalizeStudent(updated))
                    }
                    editingStudent.value = null
                } else {
                    const created = await adminService.createStudent(payload)
                    students.value.unshift(normalizeStudent(created))
                }
                resetForm()
            } catch (error) {
                alert(error.message || "Không thể lưu học viên")
            }
        }

        const editStudent = (student) => {
            editingStudent.value = student
            form.value = {
                id: student.id,
                name: student.name,
                email: student.email,
                courseId: student.courseId || "",
                phone: student.phone,
                address: student.address,
                enrollmentDate: student.enrollmentDate || new Date().toISOString().split('T')[0],
                status: student.status || "Active",
                progress: student.progress || 0
            }
            showAddForm.value = true
        }

        const deleteStudent = async (id) => {
            if (!confirm("Are you sure you want to delete this student? This action cannot be undone.")) {
                return
            }
            try {
                await adminService.deleteStudent(id)
                students.value = students.value.filter(s => s.id !== id)
            } catch (error) {
                alert(error.message || "Không thể xóa học viên")
            }
        }

        const viewStudent = (student) => {
            alert(`Viewing details for: ${student.name}\n\nEmail: ${student.email}\nCourse: ${getCourseName(student.courseId) || student.course}\nProgress: ${student.progress}%`)
        }

        const cancelEdit = () => {
            resetForm()
            editingStudent.value = null
        }

        const resetForm = () => {
            showAddForm.value = false
            form.value = {
                id: null,
                name: "",
                email: "",
                courseId: "",
                phone: "",
                address: "",
                enrollmentDate: new Date().toISOString().split('T')[0],
                status: "Active",
                progress: 0
            }
        }

        onMounted(() => {
            loadData()
        })

        return {
            students,
            searchQuery,
            showAddForm,
            editingStudent,
            form,
            availableCourses,
            filteredStudents,
            activeStudentsCount,
            uniqueCoursesCount,
            averageProgress,
            isLoading,
            errorMessage,
            saveStudent,
            editStudent,
            deleteStudent,
            viewStudent,
            cancelEdit,
            getInitials,
            getStatusIcon,
            formatDate,
            getCourseName
        }
    }
}
</script>

<style scoped>
.student-management {
    padding: 24px;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    min-height: 100vh;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header Styles */
.page-header {
    margin-bottom: 32px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
}

.title-section .page-title {
    font-size: 32px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px 0;
    letter-spacing: -0.025em;
}

.title-section .page-subtitle {
    color: #64748b;
    font-size: 16px;
    margin: 0;
}

.header-actions {
    display: flex;
    gap: 16px;
    align-items: center;
}

.search-box {
    position: relative;
    min-width: 300px;
}

.search-input {
    width: 100%;
    padding: 12px 16px 12px 44px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: white;
    font-size: 14px;
    transition: all 0.2s ease;
}

.search-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    outline: none;
}

.btn-primary {
    background: #3b82f6;
    color: white;
    box-shadow: 0 1px 3px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
    background: #64748b;
    color: white;
}

.btn-secondary:hover {
    background: #475569;
}

.btn-outline {
    background: transparent;
    border: 1px solid #e2e8f0;
    color: #475569;
}

.btn-outline:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
}

/* Stats Overview */
.stats-overview {
    margin-bottom: 32px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
}

.stat-card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
}

.stat-icon.total-students { background: linear-gradient(135deg, #3b82f6, #60a5fa); }
.stat-icon.active-students { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-icon.courses { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-icon.completion { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }

.stat-content h3 {
    font-size: 28px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 4px 0;
}

.stat-content p {
    color: #64748b;
    font-size: 14px;
    margin: 0;
    font-weight: 500;
}

/* Form Section */
.form-section {
    margin-bottom: 32px;
}

.form-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #f1f5f9;
    overflow: hidden;
}

.form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    border-bottom: 1px solid #f1f5f9;
}

.form-header h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
}

.btn-close {
    background: none;
    border: none;
    font-size: 18px;
    color: #64748b;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
}

.btn-close:hover {
    background: #f1f5f9;
    color: #475569;
}

.student-form {
    padding: 24px;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

.form-row .full-width {
    grid-column: 1 / -1;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-label {
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 6px;
}

.form-control {
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.2s ease;
}

.form-control:focus {
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

/* Table Styles */
.table-container {
    margin-bottom: 32px;
}

.table-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #f1f5f9;
    overflow: hidden;
}

.table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    border-bottom: 1px solid #f1f5f9;
}

.table-header h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
}

.students-table {
    width: 100%;
    border-collapse: collapse;
}

.students-table th {
    background: #f8fafc;
    padding: 16px 20px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid #e2e8f0;
}

.students-table td {
    padding: 20px;
    border-bottom: 1px solid #f1f5f9;
}

.student-row:hover {
    background: #f8fafc;
}

/* Student Info */
.student-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.student-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #60a5fa);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 14px;
}

.student-details {
    display: flex;
    flex-direction: column;
}

.student-name {
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 2px;
}

.student-email {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 2px;
}

.student-id {
    font-size: 12px;
    color: #94a3b8;
}

/* Course Info */
.course-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}

.course-icon {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: #f1f5f9;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    font-size: 12px;
}

.course-name {
    font-weight: 500;
    color: #1e293b;
}

.enrollment-date {
    font-size: 12px;
    color: #64748b;
}

/* Contact Info */
.contact-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.phone, .address {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #64748b;
}

.phone i, .address i {
    width: 14px;
    color: #94a3b8;
}

/* Progress */
.progress-container {
    display: flex;
    align-items: center;
    gap: 12px;
}

.progress-bar {
    flex: 1;
    height: 6px;
    background: #f1f5f9;
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981, #34d399);
    border-radius: 3px;
    transition: width 0.3s ease;
}

.progress-text {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    min-width: 35px;
}

/* Status Badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-badge.active {
    background: #d1fae5;
    color: #065f46;
}

.status-badge.inactive {
    background: #fef3c7;
    color: #92400e;
}

.status-badge.completed {
    background: #e0f2fe;
    color: #0369a1;
}

/* Action Buttons */
.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
}

.btn-action {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 12px;
    color: white;
}

.btn-edit { background: #3b82f6; }
.btn-view { background: #10b981; }
.btn-delete { background: #ef4444; }

.btn-action:hover {
    transform: translateY(-1px);
    opacity: 0.9;
}

/* Empty State */
.empty-state {
    padding: 60px 20px;
    text-align: center;
    color: #64748b;
}

.empty-icon {
    font-size: 48px;
    color: #cbd5e1;
    margin-bottom: 16px;
}

.empty-state h3 {
    color: #475569;
    margin-bottom: 8px;
}

.empty-state p {
    margin-bottom: 20px;
}

/* Table Footer */
.table-footer {
    padding: 20px 24px;
    border-top: 1px solid #f1f5f9;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.pagination-info {
    color: #64748b;
    font-size: 14px;
}

.loading-state {
    padding: 16px;
    color: #475569;
}

/* Responsive Design */
@media (max-width: 768px) {
    .student-management {
        padding: 16px;
    }
    
    .header-content {
        flex-direction: column;
        align-items: stretch;
    }
    
    .header-actions {
        flex-direction: column;
    }
    
    .search-box {
        min-width: auto;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .table-header {
        flex-direction: column;
        gap: 16px;
        align-items: stretch;
    }
    
    .students-table {
        font-size: 14px;
    }
    
    .student-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }
    
    .action-buttons {
        flex-wrap: wrap;
        justify-content: center;
    }
}
</style>
