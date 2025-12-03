<template>
    <div class="instructor-management">
        <!-- Header -->
        <div class="page-header">
            <div class="header-content">
                <div class="title-section">
                    <h1 class="page-title">Instructor</h1>
                    <p class="page-subtitle">Manage instructors and their course assignments</p>
                </div>
                <div class="header-actions">
                    <div class="search-box">
                        <i class="fas fa-search search-icon"></i>
                        <input 
                            v-model="searchQuery" 
                            type="text" 
                            class="search-input" 
                            placeholder="Search instructors..." 
                        />
                    </div>
                    <button class="btn btn-primary btn-add-instructor" @click="showAddForm = true">
                        <i class="fas fa-user-plus"></i>
                        Add New Instructor
                    </button>
                </div>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-overview">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon total-instructors">
                        <i class="fas fa-chalkboard-teacher"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ instructors.length }}</h3>
                        <p>Total Instructors</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon active-instructors">
                        <i class="fas fa-user-check"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ activeInstructorsCount }}</h3>
                        <p>Active Instructors</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon total-courses">
                        <i class="fas fa-book-open"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ totalCoursesCount }}</h3>
                        <p>Total Courses</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon avg-rating">
                        <i class="fas fa-star"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ averageRating }}/5</h3>
                        <p>Avg. Rating</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add/Edit Form -->
        <div v-if="showAddForm || editingInstructor" class="form-section">
            <div class="form-card">
                <div class="form-header">
                    <h3>{{ editingInstructor ? "Edit Instructor" : "Add New Instructor" }}</h3>
                    <button class="btn-close" @click="cancelEdit">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form @submit.prevent="saveInstructor" class="instructor-form">
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
                            <label class="form-label">Expertise *</label>
                            <select v-model="form.expertise" class="form-control" required>
                                <option value="">Select Expertise</option>
                                <option v-for="expertise in availableExpertise" :key="expertise" :value="expertise">
                                    {{ expertise }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Phone</label>
                            <input v-model="form.phone" type="tel" class="form-control" />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Join Date</label>
                            <input v-model="form.joinDate" type="date" class="form-control" />
                        </div>
                        <div class="form-group">
                            <label class="form-label">Status</label>
                            <select v-model="form.status" class="form-control">
                                <option value="Active">Active</option>
                                <option value="Inactive">Inactive</option>
                                <option value="On Leave">On Leave</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label class="form-label">Bio</label>
                            <textarea v-model="form.bio" class="form-control" rows="3" placeholder="Brief introduction about the instructor..."></textarea>
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i>
                            {{ editingInstructor ? "Update Instructor" : "Add Instructor" }}
                        </button>
                        <button type="button" class="btn btn-secondary" @click="cancelEdit">
                            <i class="fas fa-times"></i>
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Instructors Table -->
        <div class="table-container">
            <div class="table-card">
                <div class="table-header">
                    <h3>Instructor List</h3>
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
                    <table v-else class="instructors-table">
                        <thead>
                            <tr>
                                <th class="instructor-info">Instructor</th>
                                <th class="expertise">Expertise</th>
                                <th class="courses">Courses</th>
                                <th class="rating">Rating</th>
                                <th class="students">Students</th>
                                <th class="status">Status</th>
                                <th class="actions">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="instructor in filteredInstructors" :key="instructor.id" class="instructor-row">
                                <td class="instructor-info">
                                    <div class="instructor-avatar">
                                        {{ getInitials(instructor.name) }}
                                    </div>
                                    <div class="instructor-details">
                                        <span class="instructor-name">{{ instructor.name }}</span>
                                        <span class="instructor-email">{{ instructor.email }}</span>
                                        <span class="instructor-phone" v-if="instructor.phone">
                                            <i class="fas fa-phone"></i> {{ instructor.phone }}
                                        </span>
                                    </div>
                                </td>
                                <td class="expertise">
                                    <span class="expertise-tag">{{ instructor.expertise }}</span>
                                    <div class="join-date" v-if="instructor.joinDate">
                                        Since {{ formatDate(instructor.joinDate) }}
                                    </div>
                                </td>
                                <td class="courses">
                                    <div class="courses-count">
                                        <i class="fas fa-book"></i>
                                        {{ instructor.courses }} courses
                                    </div>
                                    <div class="courses-progress">
                                        <div class="progress-bar">
                                            <div class="progress-fill" :style="{ width: instructor.courseProgress + '%' }"></div>
                                        </div>
                                    </div>
                                </td>
                                <td class="rating">
                                    <div class="rating-stars">
                                        <i class="fas fa-star" v-for="n in 5" :key="n" 
                                           :class="{ 'active': n <= Math.floor(instructor.rating), 'half': n === Math.ceil(instructor.rating) && !Number.isInteger(instructor.rating) }"></i>
                                    </div>
                                    <div class="rating-value">
                                        {{ instructor.rating }}/5 ({{ instructor.reviews }} reviews)
                                    </div>
                                </td>
                                <td class="students">
                                    <div class="students-count">
                                        <i class="fas fa-users"></i>
                                        {{ instructor.students.toLocaleString() }}
                                    </div>
                                    <div class="students-trend" :class="instructor.studentTrend >= 0 ? 'up' : 'down'">
                                        <i :class="instructor.studentTrend >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
                                        {{ Math.abs(instructor.studentTrend) }}%
                                    </div>
                                </td>
                                <td class="status">
                                    <span class="status-badge" :class="instructor.status.toLowerCase().replace(' ', '-')">
                                        <i :class="getStatusIcon(instructor.status)"></i>
                                        {{ instructor.status }}
                                    </span>
                                </td>
                                <td class="actions">
                                    <div class="action-buttons">
                                        <button class="btn-action btn-edit" @click="editInstructor(instructor)" title="Edit Instructor">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn-action btn-view" @click="viewInstructor(instructor)" title="View Profile">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn-action btn-courses" @click="manageCourses(instructor)" title="Manage Courses">
                                            <i class="fas fa-book"></i>
                                        </button>
                                        <button class="btn-action btn-delete" @click="deleteInstructor(instructor.id)" title="Delete Instructor">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Empty State -->
                <div v-if="filteredInstructors.length === 0" class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-chalkboard-teacher"></i>
                    </div>
                    <h3>No instructors found</h3>
                    <p>Try adjusting your search or add a new instructor</p>
                    <button class="btn btn-primary" @click="showAddForm = true">
                        <i class="fas fa-user-plus"></i>
                        Add First Instructor
                    </button>
                </div>

                <!-- Table Footer -->
                <div v-if="filteredInstructors.length > 0" class="table-footer">
                    <div class="pagination-info">
                        Showing {{ filteredInstructors.length }} of {{ instructors.length }} instructors
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
    name: "InstructorManagement",
    setup() {
        const instructors = ref([])
        const searchQuery = ref("")
        const showAddForm = ref(false)
        const editingInstructor = ref(null)
        const isLoading = ref(false)
        const errorMessage = ref("")
        const form = ref({
            id: null,
            name: "",
            email: "",
            expertise: "",
            phone: "",
            joinDate: new Date().toISOString().split('T')[0],
            status: "Active",
            bio: ""
        })

        const availableExpertise = ref([
            "Web Development",
            "Mobile Development",
            "Data Science",
            "Machine Learning",
            "Artificial Intelligence",
            "Cloud Computing",
            "DevOps",
            "UI/UX Design",
            "Cybersecurity",
            "Blockchain"
        ])

        const normalizeInstructor = (instructor) => {
            const courseCount = instructor.coursesCount || instructor.courses || 0
            const activeCourses = instructor.activeCourses || 0
            const rating = Math.round(Number(instructor.averageRating ?? instructor.rating ?? 0) * 10) / 10

            return {
                id: instructor.id,
                name: instructor.name || "",
                email: instructor.email || "",
                expertise: instructor.expertise || "N/A",
                phone: instructor.phone || "",
                joinDate: instructor.joinDate ? instructor.joinDate.slice(0, 10) : "",
                status: instructor.status || (instructor.isActive ? "Active" : "Inactive"),
                bio: instructor.biography || instructor.bio || "",
                courses: courseCount,
                courseProgress: courseCount ? Math.round((activeCourses / courseCount) * 100) : 0,
                rating,
                reviews: instructor.reviews || 0,
                students: instructor.students || 0,
                studentTrend: instructor.studentTrend || 0
            }
        }

        const loadInstructors = async () => {
            isLoading.value = true
            errorMessage.value = ""
            try {
                const res = await adminService.getInstructors()
                instructors.value = res.map(normalizeInstructor)
            } catch (error) {
                errorMessage.value = error.message || "Không thể tải danh sách giảng viên"
            } finally {
                isLoading.value = false
            }
        }

        const filteredInstructors = computed(() => {
            if (!searchQuery.value) {
                return instructors.value
            }
            const query = searchQuery.value.toLowerCase()
            return instructors.value.filter(instructor => 
                (instructor.name || "").toLowerCase().includes(query) || 
                (instructor.email || "").toLowerCase().includes(query) ||
                (instructor.expertise || "").toLowerCase().includes(query)
            )
        })

        const activeInstructorsCount = computed(() => {
            return instructors.value.filter(instructor => (instructor.status || "").toLowerCase() === "active").length
        })

        const totalCoursesCount = computed(() => {
            return instructors.value.reduce((sum, instructor) => sum + (instructor.courses || 0), 0)
        })

        const averageRating = computed(() => {
            if (instructors.value.length === 0) return 0
            const total = instructors.value.reduce((sum, instructor) => sum + (Number(instructor.rating) || 0), 0)
            return (total / instructors.value.length).toFixed(1)
        })

        const getInitials = (name = "") => {
            return name.split(' ').filter(Boolean).map(n => n[0]).join('').toUpperCase()
        }

        const getStatusIcon = (status) => {
            const icons = {
                'Active': 'fas fa-check-circle',
                'Inactive': 'fas fa-pause-circle',
                'On Leave': 'fas fa-umbrella-beach'
            }
            return icons[status] || 'fas fa-user'
        }

        const formatDate = (dateString) => {
            if (!dateString) return 'N/A'
            const options = { year: 'numeric', month: 'short' }
            return new Date(dateString).toLocaleDateString('en-US', options)
        }

        const saveInstructor = async () => {
            const payload = {
                name: form.value.name,
                email: form.value.email,
                expertise: form.value.expertise,
                biography: form.value.bio,
                isActive: form.value.status !== "Inactive"
            }

            try {
                if (editingInstructor.value) {
                    const updated = await adminService.updateInstructor(editingInstructor.value.id, payload)
                    const idx = instructors.value.findIndex(i => i.id === editingInstructor.value.id)
                    if (idx >= 0) {
                        instructors.value.splice(idx, 1, normalizeInstructor(updated))
                    }
                    editingInstructor.value = null
                } else {
                    const created = await adminService.createInstructor(payload)
                    instructors.value.unshift(normalizeInstructor(created))
                }
                resetForm()
            } catch (error) {
                alert(error.message || "Không thể lưu giảng viên")
            }
        }

        const editInstructor = (instructor) => {
            editingInstructor.value = instructor
            form.value = { 
                id: instructor.id,
                name: instructor.name,
                email: instructor.email,
                expertise: instructor.expertise,
                phone: instructor.phone,
                joinDate: instructor.joinDate || new Date().toISOString().split('T')[0],
                status: instructor.status || "Active",
                bio: instructor.bio || ""
            }
            showAddForm.value = true
        }

        const deleteInstructor = async (id) => {
            if (!confirm("Are you sure you want to delete this instructor? This action cannot be undone.")) {
                return
            }
            try {
                await adminService.deleteInstructor(id)
                instructors.value = instructors.value.filter(i => i.id !== id)
            } catch (error) {
                alert(error.message || "Không thể xóa giảng viên")
            }
        }

        const viewInstructor = (instructor) => {
            alert(`Viewing profile for: ${instructor.name}\n\nEmail: ${instructor.email}\nExpertise: ${instructor.expertise}\nBio: ${instructor.bio}`)
        }

        const manageCourses = (instructor) => {
            alert(`Managing courses for instructor: ${instructor.name}`)
        }

        const cancelEdit = () => {
            resetForm()
            editingInstructor.value = null
        }

        const resetForm = () => {
            showAddForm.value = false
            form.value = {
                id: null,
                name: "",
                email: "",
                expertise: "",
                phone: "",
                joinDate: new Date().toISOString().split('T')[0],
                status: "Active",
                bio: ""
            }
        }

        onMounted(() => {
            loadInstructors()
        })

        return {
            instructors,
            searchQuery,
            showAddForm,
            editingInstructor,
            form,
            availableExpertise,
            filteredInstructors,
            activeInstructorsCount,
            totalCoursesCount,
            averageRating,
            isLoading,
            errorMessage,
            saveInstructor,
            editInstructor,
            deleteInstructor,
            viewInstructor,
            manageCourses,
            cancelEdit,
            getInitials,
            getStatusIcon,
            formatDate
        }
    }
}
</script>

<style scoped>
.instructor-management {
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

.stat-icon.total-instructors { background: linear-gradient(135deg, #3b82f6, #60a5fa); }
.stat-icon.active-instructors { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-icon.total-courses { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-icon.avg-rating { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }

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

.instructor-form {
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

.instructors-table {
    width: 100%;
    border-collapse: collapse;
}

.instructors-table th {
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

.instructors-table td {
    padding: 20px;
    border-bottom: 1px solid #f1f5f9;
}

.instructor-row:hover {
    background: #f8fafc;
}

/* Instructor Info */
.instructor-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.instructor-avatar {
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

.instructor-details {
    display: flex;
    flex-direction: column;
}

.instructor-name {
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 2px;
}

.instructor-email {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 2px;
}

.instructor-phone {
    font-size: 12px;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Expertise */
.expertise-tag {
    background: #e0f2fe;
    color: #0369a1;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    display: inline-block;
    margin-bottom: 4px;
}

.join-date {
    font-size: 11px;
    color: #94a3b8;
}

/* Courses */
.courses-count {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #64748b;
    margin-bottom: 6px;
}

.progress-bar {
    width: 100%;
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

/* Rating */
.rating-stars {
    display: flex;
    gap: 2px;
    margin-bottom: 4px;
}

.rating-stars .fa-star {
    color: #e5e7eb;
    font-size: 12px;
}

.rating-stars .fa-star.active {
    color: #fbbf24;
}

.rating-stars .fa-star.half {
    background: linear-gradient(90deg, #fbbf24 50%, #e5e7eb 50%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.rating-value {
    font-size: 11px;
    color: #64748b;
}

/* Students */
.students-count {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #64748b;
    margin-bottom: 4px;
}

.students-trend {
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 8px;
}

.students-trend.up {
    background: #d1fae5;
    color: #065f46;
}

.students-trend.down {
    background: #fee2e2;
    color: #dc2626;
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

.status-badge.on-leave {
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
.btn-courses { background: #8b5cf6; }
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
    .instructor-management {
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
    
    .instructors-table {
        font-size: 14px;
    }
    
    .instructor-info {
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
