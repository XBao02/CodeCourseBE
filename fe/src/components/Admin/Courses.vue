<template>
  <div class="dashboard-page-wrapper">
    <div class="container-fluid py-5">
      <h1 class="dashboard-title fw-bold mb-4">Course Management</h1>

      <div class="d-flex justify-content-between align-items-center mb-4">
        <div class="input-group" style="max-width: 400px;">
          <input type="text" class="form-control" placeholder="Search for courses..." v-model="searchQuery">
          <button class="btn btn-primary" type="button"><i class="fa-solid fa-magnifying-glass"></i></button>
        </div>
        <button class="btn btn-success"><i class="bi bi-plus-circle me-2"></i>Add New Course</button>
      </div>

      <div class="card p-4 rounded-3">
        <div class="table-responsive">
          <table class="table table-borderless table-hover mb-0">
            <thead>
              <tr class="text-muted">
                <th scope="col">Course Name</th>
                <th scope="col">Instructor</th>
                <th scope="col">Students</th>
                <th scope="col">Status</th>
                <th scope="col" class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in filteredCourses" :key="course.id">
                <td class="fw-bold">{{ course.name }}</td>
                <td>{{ course.instructor }}</td>
                <td>{{ course.students }}</td>
                <td>
                  <span class="badge"
                    :class="{ 'bg-success-soft text-success': course.status === 'Published', 'bg-warning-soft text-warning': course.status === 'Draft' }">{{
                      course.status }}</span>
                </td>
                <td class="text-center">
                  <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-info" @click="assignInstructor(course.id)">
                      <i class="fas fa-user-plus"></i>

                    </button>
                    <button class="btn btn-sm btn-danger" @click="deleteCourse(course.id)">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="filteredCourses.length === 0" class="text-center text-muted py-5">
          No courses found.
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: "AdminCourseManagement",
  data() {
    return {
      searchQuery: '',
      courses: [
        { id: 1, name: "Advanced Web Programming", instructor: "Michael Brown", students: 45, status: "Published" },
        { id: 2, name: "Data Structures & Algorithms", instructor: "Jane Doe", students: 32, status: "Published" },
        { id: 3, name: "Mobile Development with React Native", instructor: "Emily White", students: 28, status: "Draft" },
        { id: 4, name: "Introduction to Python", instructor: "David Kim", students: 49, status: "Published" },
        { id: 5, name: "Machine Learning Fundamentals", instructor: "Sophia Chen", students: 15, status: "Draft" },
      ]
    };
  },
  computed: {
    filteredCourses() {
      if (!this.searchQuery) {
        return this.courses;
      }
      const query = this.searchQuery.toLowerCase();
      return this.courses.filter(course => {
        return course.name.toLowerCase().includes(query) || course.instructor.toLowerCase().includes(query);
      });
    }
  },
  methods: {
    deleteCourse(courseId) {
      if (confirm("Are you sure you want to delete this course?")) {
        // In a real application, you would make an API call here to delete the course
        console.log(`Deleting course with ID: ${courseId}`);
        this.courses = this.courses.filter(course => course.id !== courseId);
      }
    },
    assignInstructor(courseId) {
      // In a real application, this would open a modal to select a new instructor
      const course = this.courses.find(c => c.id === courseId);
      console.log(`Assigning instructor for course: ${course.name}`);
      alert(`Assigning instructor functionality for "${course.name}"`);
    }
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

/* Title */
.dashboard-title {
  color: #222;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

/* Search + Add */
.input-group input {
  border-radius: 8px 0 0 8px;
  border: 1px solid #ddd;
}

.input-group .btn {
  border-radius: 0 8px 8px 0;
}

.btn-success {
  border-radius: 8px;
  padding: 6px 14px;
  font-weight: 500;
}

/* Card */
.card {
  border-radius: 14px;
  border: none;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

/* Table */
.table {
  color: #333;
  font-size: 0.95rem;
}

.table thead th {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.table-hover tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.fw-bold {
  font-weight: 600;
}

/* Badge mềm */
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

/* Actions */
.btn-group .btn {
  border-radius: 6px;
  padding: 4px 8px;
}

.btn-info {
  background: #17a2b8;
  border: none;
}

.btn-info:hover {
  background: #138496;
}

.btn-danger {
  background: #dc3545;
  border: none;
}

.btn-danger:hover {
  background: #c82333;
}
</style>
