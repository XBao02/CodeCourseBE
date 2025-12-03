<template>
  <div class="dashboard-page-wrapper">
    <div class="container-fluid py-5">
      <!-- Header Section -->
      <div class="dashboard-header mb-5">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h1 class="dashboard-title fw-bold mb-2">Course Management</h1>
            <p class="dashboard-subtitle text-muted">Manage and organize your course catalog efficiently</p>
          </div>
          <div class="col-md-6 text-md-end">
            <button class="btn btn-success btn-add-course" @click="openAddModal">
              <i class="bi bi-plus-circle me-2"></i>Add New Course
            </button>
          </div>
        </div>
      </div>

      <!-- Search and Filter Section -->
      <div class="search-filter-section mb-4">
      <div class="row g-3 align-items-end">
        <div class="col-md-4">
          <div class="search-box">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                  <i class="fa-solid fa-magnifying-glass text-muted"></i>
                </span>
                <input 
                  type="text" 
                  class="form-control border-start-0" 
                  placeholder="Search courses, instructors..." 
                  v-model="searchQuery"
                >
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">Status</label>
            <select class="form-select" v-model="statusFilter">
              <option value="all">All Status</option>
              <option value="Published">Published</option>
              <option value="Draft">Draft</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">Sort By</label>
            <select class="form-select" v-model="sortBy">
              <option value="name">Course Name</option>
              <option value="students">Students</option>
              <option value="instructor">Instructor</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="fa-solid fa-rotate-right me-2"></i>Reset
            </button>
          </div>
      </div>
    </div>

      <!-- Add Course Modal -->
      <div class="modal fade show" tabindex="-1" style="display: block;" v-if="showAddModal" role="dialog">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Add New Course</h5>
              <button type="button" class="btn-close" aria-label="Close" @click="closeAddModal"></button>
            </div>
            <div class="modal-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Title</label>
                  <input v-model="form.title" type="text" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Instructor ID</label>
                  <input v-model.number="form.instructorId" type="number" class="form-control" required />
                </div>
                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea v-model="form.description" class="form-control" rows="3"></textarea>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Level</label>
                  <select v-model="form.level" class="form-select">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Price</label>
                  <input v-model.number="form.price" type="number" min="0" step="0.01" class="form-control" />
                </div>
                <div class="col-md-4 d-flex align-items-center">
                  <div class="form-check mt-4">
                    <input class="form-check-input" type="checkbox" id="isPublic" v-model="form.isPublic">
                    <label class="form-check-label" for="isPublic">Published</label>
                  </div>
                </div>
              </div>
              <div class="alert alert-warning mt-3" v-if="errorMessage">{{ errorMessage }}</div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeAddModal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="submitCourse">Save</button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show" v-if="showAddModal"></div>

      <!-- Stats Cards -->
      <div class="stats-cards mb-4">
        <div class="row g-3">
          <div class="col-md-3">
            <div class="stat-card total-courses">
              <div class="stat-icon">
                <i class="fa-solid fa-book-open"></i>
              </div>
              <div class="stat-content">
                <h3>{{ courses.length }}</h3>
                <p>Total Courses</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card published-courses">
              <div class="stat-icon">
                <i class="fa-solid fa-check-circle"></i>
              </div>
              <div class="stat-content">
                <h3>{{ publishedCount }}</h3>
                <p>Published</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card draft-courses">
              <div class="stat-icon">
                <i class="fa-solid fa-edit"></i>
              </div>
              <div class="stat-content">
                <h3>{{ draftCount }}</h3>
                <p>In Draft</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card total-students">
              <div class="stat-icon">
                <i class="fa-solid fa-users"></i>
              </div>
              <div class="stat-content">
                <h3>{{ totalStudents }}</h3>
                <p>Total Students</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Courses Table -->
      <div class="card main-card rounded-3">
        <div class="card-header bg-transparent border-bottom-0 py-4">
          <div class="row align-items-center">
            <div class="col-md-6">
              <h5 class="card-title mb-0 fw-semibold">Course List</h5>
            </div>
            <div class="col-md-6 text-md-end">
              <div class="btn-group" role="group">
                <button class="btn btn-outline-primary btn-sm">
                  <i class="fa-solid fa-download me-2"></i>Export
                </button>
                <button class="btn btn-outline-secondary btn-sm">
                  <i class="fa-solid fa-filter me-2"></i>Filter
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="card-body p-0">
          <div class="table-responsive">
            <div v-if="errorMessage" class="alert alert-warning m-3" role="alert">
              {{ errorMessage }}
            </div>
            <div v-if="isLoading" class="text-center py-4">Loading courses...</div>
            <table v-else class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col" class="ps-4">Course Name</th>
                  <th scope="col">Instructor</th>
                  <th scope="col">Students</th>
                  <th scope="col">Enrollment</th>
                  <th scope="col">Status</th>
                  <th scope="col" class="text-center pe-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="course in filteredAndSortedCourses" :key="course.id" class="course-row">
                  <td class="ps-4">
                    <div class="d-flex align-items-center">
                      <div class="course-avatar me-3">
                        <i class="fa-solid fa-graduation-cap"></i>
                      </div>
                      <div>
                        <h6 class="mb-0 fw-semibold">{{ course.name }}</h6>
                        <small class="text-muted">{{ course.category }}</small>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="instructor-avatar me-2">
                        {{ getInitials(course.instructor) }}
                      </div>
                      <span>{{ course.instructor }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="fw-semibold">{{ course.students }}</span>
                  </td>
                  <td>
                    <div class="progress" style="height: 6px; width: 80px;">
                      <div class="progress-bar" :style="{ width: course.enrollmentRate + '%' }"></div>
                    </div>
                    <small class="text-muted">{{ course.enrollmentRate }}%</small>
                  </td>
                  <td>
                    <span class="badge" :class="getStatusClass(course.status)">
                      <i :class="getStatusIcon(course.status)" class="me-1"></i>
                      {{ course.status }}
                    </span>
                  </td>
                  <td class="text-center pe-4">
                    <div class="btn-group action-buttons" role="group">
                      <button class="btn btn-sm btn-outline-primary" @click="editCourse(course.id)" title="Edit Course">
                        <i class="fa-solid fa-edit"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-info" @click="assignInstructor(course.id)" title="Assign Instructor">
                        <i class="fa-solid fa-user-plus"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-success" @click="viewCourse(course.id)" title="View Details">
                        <i class="fa-solid fa-eye"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger" @click="deleteCourse(course.id)" title="Delete Course">
                        <i class="fa-solid fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty State -->
          <div v-if="filteredAndSortedCourses.length === 0" class="text-center py-5">
            <div class="empty-state-icon mb-3">
              <i class="fa-solid fa-book-open fa-3x text-muted"></i>
            </div>
            <h5 class="text-muted">No courses found</h5>
            <p class="text-muted mb-3">Try adjusting your search or filters</p>
            <button class="btn btn-primary" @click="resetFilters">
              <i class="fa-solid fa-rotate-right me-2"></i>Reset Filters
            </button>
          </div>
        </div>

        <!-- Table Footer -->
        <div v-if="filteredAndSortedCourses.length > 0" class="card-footer bg-transparent border-top-0 py-3">
          <div class="row align-items-center">
            <div class="col-md-6">
              <p class="mb-0 text-muted small">
                Showing {{ filteredAndSortedCourses.length }} of {{ courses.length }} courses
              </p>
            </div>
            <div class="col-md-6">
              <!-- Pagination can be added here -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/adminService'

export default {
  name: "AdminCourseManagement",
  data() {
    return {
      searchQuery: '',
      statusFilter: 'all',
      sortBy: 'name',
      isLoading: false,
      errorMessage: '',
      courses: [],
      showAddModal: false,
      form: {
        title: '',
        instructorId: '',
        description: '',
        level: 'beginner',
        price: 0,
        isPublic: false,
      }
    };
  },
  computed: {
    filteredAndSortedCourses() {
      let filtered = this.courses;

      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(course => 
          course.name.toLowerCase().includes(query) || 
          course.instructor.toLowerCase().includes(query) ||
          course.category.toLowerCase().includes(query)
        );
      }

      // Filter by status
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(course => course.status === this.statusFilter);
      }

      // Sort courses
      filtered = filtered.sort((a, b) => {
        if (this.sortBy === 'name') {
          return a.name.localeCompare(b.name);
        } else if (this.sortBy === 'students') {
          return b.students - a.students;
        } else if (this.sortBy === 'instructor') {
          return a.instructor.localeCompare(b.instructor);
        }
        return 0;
      });

      return filtered;
    },
    publishedCount() {
      return this.courses.filter(course => course.status === 'Published').length;
    },
    draftCount() {
      return this.courses.filter(course => course.status === 'Draft').length;
    },
    totalStudents() {
      return this.courses.reduce((sum, course) => sum + course.students, 0);
    }
  },
  methods: {
    normalizeCourse(course) {
      const status = (course.status || '').toLowerCase() === 'active' ? 'Published' : 'Draft';
      return {
        id: course.id,
        name: course.title || course.name || `Course #${course.id}`,
        instructor: course.instructor || 'N/A',
        students: course.students || 0,
        status,
        category: course.level || 'General',
        enrollmentRate: course.enrollmentRate ?? 0
      };
    },
    async fetchCourses() {
      this.isLoading = true;
      this.errorMessage = '';
      try {
        const res = await adminService.getCourses();
        this.courses = res.map((c) => this.normalizeCourse(c));
      } catch (error) {
        this.errorMessage = error.message || 'Không thể tải danh sách khóa học';
      } finally {
        this.isLoading = false;
      }
    },
    openAddModal() {
      this.errorMessage = '';
      this.showAddModal = true;
    },
    closeAddModal() {
      this.showAddModal = false;
      this.form = {
        title: '',
        instructorId: '',
        description: '',
        level: 'beginner',
        price: 0,
        isPublic: false,
      };
    },
    openAddModal() {
      this.errorMessage = '';
      this.showAddModal = true;
    },
    closeAddModal() {
      this.showAddModal = false;
      this.form = {
        title: '',
        instructorId: '',
        description: '',
        level: 'beginner',
        price: 0,
        isPublic: false,
      };
    },
    getInitials(name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase();
    },
    getStatusClass(status) {
      return {
        'Published': 'bg-success-soft text-success',
        'Draft': 'bg-warning-soft text-warning'
      }[status];
    },
    getStatusIcon(status) {
      return status === 'Published' ? 'fa-solid fa-check-circle' : 'fa-solid fa-edit';
    },
    async submitCourse() {
      if (!this.form.title || !this.form.instructorId) {
        this.errorMessage = 'Title và Instructor ID là bắt buộc';
        return;
      }
      try {
        const payload = {
          title: this.form.title,
          description: this.form.description,
          level: this.form.level,
          price: this.form.price,
          instructor_id: this.form.instructorId,
          is_public: this.form.isPublic
        };
        const created = await adminService.createCourse(payload);
        this.courses = [this.normalizeCourse(created), ...this.courses];
        this.closeAddModal();
      } catch (error) {
        this.errorMessage = error.message || 'Không thể tạo khóa học';
      }
    },
    async deleteCourse(courseId) {
      if (confirm("Are you sure you want to delete this course? This action cannot be undone.")) {
        try {
          await adminService.deleteCourse(courseId);
          this.courses = this.courses.filter(course => course.id !== courseId);
        } catch (error) {
          alert(error.message || "Không thể xóa khóa học");
        }
      }
    },
    assignInstructor(courseId) {
      const course = this.courses.find(c => c.id === courseId);
      console.log(`Assigning instructor for course: ${course.name}`);
      alert(`Assigning instructor functionality for "${course.name}"`);
    },
    editCourse(courseId) {
      const course = this.courses.find(c => c.id === courseId);
      console.log(`Editing course: ${course.name}`);
      alert(`Edit functionality for "${course.name}"`);
    },
    viewCourse(courseId) {
      const course = this.courses.find(c => c.id === courseId);
      console.log(`Viewing course: ${course.name}`);
      alert(`View details for "${course.name}"`);
    },
    resetFilters() {
      this.searchQuery = '';
      this.statusFilter = 'all';
      this.sortBy = 'name';
    }
  },
  mounted() {
    this.fetchCourses();
  }
};
</script>

<style scoped>
.dashboard-page-wrapper {
  background: linear-gradient(135deg, #f9fafb, #f1f5f9);
  min-height: 100vh;
  padding: 20px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

/* Header */
.dashboard-header {
  background: transparent;
}

.dashboard-title {
  color: #222;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.dashboard-subtitle {
  font-size: 1rem;
}

.btn-add-course {
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
}

/* Search and Filter */
.search-filter-section {
  background: transparent;
}

.search-box .input-group {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-box .input-group-text {
  border-radius: 8px 0 0 8px;
  border: 1px solid #ddd;
  border-right: none;
}

.search-box .form-control {
  border-radius: 0 8px 8px 0;
  border: 1px solid #ddd;
  border-left: none;
}

.form-select {
  border-radius: 8px;
  border: 1px solid #ddd;
}

/* Stats Cards */
.stats-cards .stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 15px;
}

.stats-cards .stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: white;
}

.total-courses .stat-icon { background: linear-gradient(135deg, #4f46e5, #6366f1); }
.published-courses .stat-icon { background: linear-gradient(135deg, #10b981, #34d399); }
.draft-courses .stat-icon { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.total-students .stat-icon { background: linear-gradient(135deg, #ef4444, #f87171); }

.stat-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.2rem;
  color: #222;
}

.stat-content p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Main Card */
.main-card {
  border-radius: 14px;
  border: none;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  overflow: hidden;
}

.main-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  background: transparent !important;
}

.card-title {
  color: #222;
  font-size: 1.2rem;
}

/* Table */
.table {
  color: #333;
  font-size: 0.95rem;
  margin: 0;
}

.table thead th {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #666;
  border-bottom: 1px solid #e9ecef;
  padding: 15px 12px;
}

.table tbody td {
  padding: 15px 12px;
  vertical-align: middle;
  border-bottom: 1px solid #f8f9fa;
}

.course-row:hover {
  background-color: #f8f9fa;
}

/* Course Avatar */
.course-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
}

/* Instructor Avatar */
.instructor-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
  color: #666;
}

/* Progress Bar */
.progress {
  background: #f1f5f9;
  border-radius: 10px;
}

.progress-bar {
  background: linear-gradient(135deg, #10b981, #34d399);
  border-radius: 10px;
}

/* Badge */
.badge {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.35em 0.75em;
  border-radius: 12px;
}

.bg-warning-soft {
  background-color: #fff3cd;
  color: #856404;
}

.bg-success-soft {
  background-color: #d4edda;
  color: #155724;
}

/* Action Buttons */
.action-buttons .btn {
  border-radius: 6px;
  padding: 6px 10px;
  margin: 0 2px;
  border: 1px solid #dee2e6;
  transition: all 0.2s ease;
}

.action-buttons .btn:hover {
  transform: translateY(-1px);
}

.btn-outline-primary:hover { background: #0d6efd; color: white; }
.btn-outline-info:hover { background: #0dcaf0; color: white; }
.btn-outline-success:hover { background: #198754; color: white; }
.btn-outline-danger:hover { background: #dc3545; color: white; }

/* Empty State */
.empty-state-icon {
  opacity: 0.5;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-page-wrapper {
    padding: 15px;
  }
  
  .stats-cards .row {
    margin: 0 -10px;
  }
  
  .stats-cards .col-md-3 {
    padding: 0 10px;
    margin-bottom: 15px;
  }
  
  .action-buttons .btn {
    padding: 4px 8px;
    margin: 1px;
  }
  
  .table-responsive {
    font-size: 0.9rem;
  }
}
</style>
