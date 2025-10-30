<script setup>
import { ref, computed } from 'vue';

// --- Mock Course Data ---
const courses = ref([
  { id: 1, name: "Advanced React Programming", category: "Programming", instructor: "Nguyễn Văn An", students: 245, duration: "12 weeks", status: "Active", created: "2024-01-15" },
  { id: 2, name: "Basic to Advanced UI/UX Design", category: "Design", instructor: "Trần Thị Bích", students: 189, duration: "10 weeks", status: "Active", created: "2024-02-20" },
  { id: 3, name: "Digital Marketing in the 4.0 Era", category: "Marketing", instructor: "Unassigned", students: 0, duration: "8 weeks", status: "Draft", created: "2024-03-10" },
  { id: 4, name: "Python for Data Science", category: "Programming", instructor: "Lê Minh Tuấn", students: 312, duration: "14 weeks", status: "Active", created: "2024-01-05" },
  { id: 5, name: "Agile & Scrum Project Management", category: "Management", instructor: "Phạm Thu Hà", students: 156, duration: "6 weeks", status: "Completed", created: "2023-11-20" },
  { id: 6, name: "NodeJS and MongoDB", category: "Programming", instructor: "Unassigned", students: 0, duration: "10 weeks", status: "Draft", created: "2024-03-25" },
  { id: 7, name: "Professional Photoshop", category: "Design", instructor: "Đỗ Văn Cường", students: 203, duration: "8 weeks", status: "Active", created: "2024-02-01" },
  { id: 8, name: "SEO & Content Marketing", category: "Marketing", instructor: "Hoàng Thị Lan", students: 178, duration: "7 weeks", status: "Active", created: "2024-01-28" },
]);

// --- Mock Instructor Data (for Modal) ---
const instructors = ref([
  { id: 1, name: 'Nguyễn Văn An', specialty: 'React, JavaScript' },
  { id: 2, name: 'Trần Thị Bích', specialty: 'UI/UX Design' },
  { id: 3, name: 'Lê Minh Tuấn', specialty: 'Python, Data Science' },
  { id: 4, name: 'Phạm Thu Hà', specialty: 'Agile, Project Management' },
  { id: 5, name: 'Đỗ Văn Cường', specialty: 'Graphic Design' },
  { id: 6, name: 'Hoàng Thị Lan', specialty: 'Digital Marketing' },
  { id: 7, name: 'Võ Minh Khoa', specialty: 'Backend Development' },
  { id: 8, name: 'Ngô Thu Trang', specialty: 'Mobile Development' }
]);

// --- Modal State ---
const isModalVisible = ref(false);
const selectedCourseToAssign = ref(null);
const selectedCourseName = ref('');
const selectedInstructorId = ref(null); // Selected instructor ID in the modal

const searchQuery = ref('');

// --- Computed Properties (Stats and Filtering) ---
const totalCourses = computed(() => courses.value.length);
const activeCourses = computed(() => courses.value.filter(c => c.status === 'Active').length);
const needInstructorCourses = computed(() => courses.value.filter(c => c.instructor === 'Unassigned').length);

const filteredCourses = computed(() => {
  if (!searchQuery.value) return courses.value;
  const query = searchQuery.value.toLowerCase();
  return courses.value.filter(course =>
    course.name.toLowerCase().includes(query) ||
    course.instructor.toLowerCase().includes(query)
  );
});

// --- Table Actions ---
const editCourse = (id) => {
  const course = courses.value.find(c => c.id === id);
  if (course) {
    // Reset selection and set course info
    selectedInstructorId.value = null;
    selectedCourseToAssign.value = id;
    selectedCourseName.value = course.name;
    isModalVisible.value = true; // Open modal
  }
};

const deleteCourse = (id) => {
  if (confirm('Are you sure you want to delete this course?')) {
    courses.value = courses.value.filter(c => c.id !== id);
  }
};

const getStatusClass = (status) => {
  switch (status) {
    case 'Active': return 'status-active';
    case 'Draft': return 'status-draft';
    case 'Completed': return 'status-completed';
    default: return '';
  }
};

// --- Modal Actions ---
const closeModal = () => {
  isModalVisible.value = false;
  selectedInstructorId.value = null;
};

const handleAssign = () => {
  if (selectedInstructorId.value === null) {
    alert('Please select an instructor to assign.');
    return;
  }
  
  const courseId = selectedCourseToAssign.value;
  const courseIndex = courses.value.findIndex(c => c.id === courseId);
  
  if (courseIndex !== -1) {
    const instructor = instructors.value.find(i => i.id === selectedInstructorId.value);
    
    // Update data
    courses.value[courseIndex].instructor = instructor ? instructor.name : 'Unknown Instructor';
    
    // If status was Draft, change it to Active upon assignment (Optional logic)
    if (courses.value[courseIndex].status === 'Draft') {
      courses.value[courseIndex].status = 'Active';
    }
  }

  closeModal();
};

</script>

<template>
  <div class="course-management">
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>

    <h1 class="page-title">Course Management</h1>
    <p class="page-subtitle">View, search, and manage all courses in the system</p>

    <div class="stats-cards">
      <div class="card">
        <div class="icon icon-total"><i class='bx bxs-book-bookmark'></i></div>
        <div class="info">
          <span class="label">Total Courses</span>
          <span class="value">{{ totalCourses }}</span>
        </div>
      </div>
      <div class="card">
        <div class="icon icon-active"><i class='bx bx-user-voice'></i></div>
        <div class="info">
          <span class="label">Active Courses</span>
          <span class="value">{{ activeCourses }}</span>
        </div>
      </div>
      <div class="card card-warning">
        <div class="icon icon-pending"><i class='bx bxs-time-five'></i></div>
        <div class="info">
          <span class="label">Unassigned Instructors</span>
          <span class="value">{{ needInstructorCourses }}</span>
        </div>
      </div>
    </div>

    <div class="search-bar">
      <i class='bx bx-search'></i>
      <input 
        type="text" 
        v-model="searchQuery"
        placeholder="Search by course name, category, or instructor..."
      >
    </div>

    <div class="course-table-wrapper">
      <table class="course-table">
        <thead>
          <tr>
            <th>Course Name</th>
            <th>Category</th>
            <th>Instructor</th>
            <th>Students</th>
            <th>Duration</th>
            <th>Status</th>
            <th>Created Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="course in filteredCourses" :key="course.id">
            <td class="course-name">{{ course.name }}</td>
            <td>{{ course.category }}</td>
            <td :class="{'no-instructor': course.instructor === 'Unassigned'}">{{ course.instructor }}</td>
            <td>{{ course.students }}</td>
            <td>{{ course.duration }}</td>
            <td>
              <span :class="['status-badge', getStatusClass(course.status)]">
                {{ course.status }}
              </span>
            </td>
            <td>{{ course.created }}</td>
            <td class="actions">
              <button @click="editCourse(course.id)" class="action-btn edit-btn">
                <i class='bx bxs-pencil'></i> Assign
              </button>
              <button @click="deleteCourse(course.id)" class="action-btn delete-btn">
                <i class='bx bxs-trash'></i>
              </button>
            </td>
          </tr>
          <tr v-if="filteredCourses.length === 0">
              <td colspan="8" class="no-results">No courses found matching your criteria.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <teleport to="body">
    <div v-if="isModalVisible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Assign Instructor</h2>
          <p>Course: <strong>{{ selectedCourseName }}</strong></p>
        </div>
        
        <div class="select-wrapper">
          <select v-model="selectedInstructorId" class="instructor-select">
            <option :value="null" disabled>Select Instructor</option>
            <option 
              v-for="instructor in instructors" 
              :key="instructor.id" 
              :value="instructor.id"
            >
              {{ instructor.name }} ({{ instructor.specialty }})
            </option>
          </select>
          <i class='bx bx-chevron-down select-icon'></i>
        </div>

        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeModal">Cancel</button>
          <button 
            class="btn btn-primary" 
            @click="handleAssign" 
            :disabled="selectedInstructorId === null"
          >
            Assign
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
/* Import font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
@import url('https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css');

.course-management {
  padding: 30px;
  background-color: #f4f7f9;
  min-height: 100vh;
  font-family: 'Poppins', sans-serif;
}

.page-title { font-size: 28px; font-weight: 600; color: #333; margin-bottom: 5px; }
.page-subtitle { font-size: 15px; color: #666; margin-bottom: 25px; }

/* --- 1. Stats Cards --- */
.stats-cards { display: flex; gap: 20px; margin-bottom: 30px; }
.card { display: flex; align-items: center; flex: 1; padding: 20px; background-color: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); }
.icon { display: flex; justify-content: center; align-items: center; width: 50px; height: 50px; border-radius: 10px; font-size: 24px; color: #fff; margin-right: 15px; }
.icon-total { background-color: #7494ec; }
.icon-active { background-color: #4CAF50; }
.icon-pending { background-color: #FF9800; }
.info { display: flex; flex-direction: column; }
.label { font-size: 14px; color: #666; font-weight: 500; }
.value { font-size: 24px; font-weight: 700; color: #333; }

/* --- 2. Search Bar --- */
.search-bar { display: flex; align-items: center; padding: 10px 15px; background-color: #fff; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03); }
.search-bar i { font-size: 20px; color: #999; margin-right: 10px; }
.search-bar input { flex-grow: 1; border: none; outline: none; font-size: 15px; color: #333; }

/* --- 3. Data Table --- */
.course-table-wrapper { background-color: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); overflow-x: auto; }
.course-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.course-table thead th { padding: 15px; text-align: left; font-size: 14px; font-weight: 600; color: #666; border-bottom: 1px solid #eee; background-color: #f8f9fa; }
.course-table tbody td { padding: 15px; font-size: 14px; color: #333; border-bottom: 1px solid #eee; vertical-align: middle; }
.course-name { font-weight: 500; color: #1a73e8; }
.no-instructor { color: #FF9800; font-style: italic; }
.status-badge { display: inline-block; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; text-align: center; min-width: 90px; }
.status-active { background-color: #e6f7ed; color: #38a169; }
.status-draft { background-color: #fff3e0; color: #ff9800; }
.status-completed { background-color: #e0f7fa; color: #00bcd4; }
.actions { display: flex; align-items: center; gap: 8px; min-width: 150px; }
.action-btn { padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; display: inline-flex; align-items: center; gap: 5px; transition: background-color 0.2s; }
.edit-btn { background-color: #e3f2fd; color: #1a73e8; }
.edit-btn:hover { background-color: #c6e3ff; }
.delete-btn { background-color: #ffebee; color: #f44336; padding: 8px; }
.delete-btn:hover { background-color: #ffcdd2; }
.no-results { text-align: center; padding: 30px !important; color: #999; font-style: italic; }

/* --- 4. STYLE MODAL --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 450px;
  max-width: 90%;
  padding: 20px 25px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header h2 { font-size: 20px; font-weight: 600; color: #333; margin-bottom: 5px; }
.modal-header p { font-size: 14px; color: #666; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid #eee; }

/* Dropdown */
.select-wrapper { position: relative; margin-bottom: 25px; }
.instructor-select {
  width: 100%;
  padding: 10px 40px 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-color: #f9f9f9;
  cursor: pointer;
}
.select-icon { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #999; font-size: 20px; }

/* Footer and Buttons */
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding-top: 15px; }
.btn { padding: 10px 18px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: background-color 0.2s; }
.btn-cancel { background-color: #f1f1f1; color: #666; }
.btn-cancel:hover { background-color: #e0e0e0; }
.btn-primary { background-color: #7494ec; color: #fff; }
.btn-primary:hover { background-color: #5d7ac9; }
.btn-primary:disabled { background-color: #a8b9e6; cursor: not-allowed; }
</style>
