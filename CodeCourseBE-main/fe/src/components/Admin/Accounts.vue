<template>
    <div class="container mt-5">
        <div class="card shadow-lg rounded-3">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h4 class="mb-0">🎓 Student Management</h4>
                <button class="btn btn-light btn-sm" @click="showAddForm = true">
                    + Add Student
                </button>
            </div>

            <div class="card-body">
                <!-- them, chinh sua form -->
                <div v-if="showAddForm || editingStudent" class="mb-4">
                    <h5 class="text-secondary mb-3">
                        {{ editingStudent ? "Edit Student" : "Add New Student" }}
                    </h5>
                    <form @submit.prevent="saveStudent" class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label">Full Name</label>
                            <input v-model="form.name" type="text" class="form-control" required />
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Email</label>
                            <input v-model="form.email" type="email" class="form-control" required />
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Course</label>
                            <input v-model="form.course" type="text" class="form-control" required />
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Phone</label>
                            <input v-model="form.phone" type="text" class="form-control" required />
                        </div>
                        <div class="col-md-8">
                            <label class="form-label">Address</label>
                            <input v-model="form.address" type="text" class="form-control" required />
                        </div>
                        <div class="col-12">
                            <button type="submit" class="btn btn-success me-2">Save</button>
                            <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
                        </div>
                    </form>
                    <hr />
                </div>

                <!-- bang -->
                <div class="table-responsive">
                    <table class="table table-bordered table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>#</th>
                                <th>Full Name</th>
                                <th>Email</th>
                                <th>Course</th>
                                <th>Phone</th>
                                <th>Address</th>
                                <th class="text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(student, index) in students" :key="student.id">
                                <td>{{ index + 1 }}</td>
                                <td>{{ student.name }}</td>
                                <td>{{ student.email }}</td>
                                <td>{{ student.course }}</td>
                                <td>{{ student.phone }}</td>
                                <td>{{ student.address }}</td>
                                <td class="text-center">
                                    <button class="btn btn-warning btn-sm me-2"
                                        @click="editStudent(student)">Edit</button>
                                    <button class="btn btn-danger btn-sm"
                                        @click="deleteStudent(student.id)">Delete</button>
                                </td>
                            </tr>
                            <tr v-if="students.length === 0">
                                <td colspan="7" class="text-center text-muted">No students available</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "StudentManagement",
    data() {
        return {
            students: [
                {
                    id: 1,
                    name: "Nguyen Van A",
                    email: "nva@mail.com",
                    course: "Vue.js Basics",
                    phone: "0987654321",
                    address: "123 Hai Chau, Da Nang"
                },
                {
                    id: 1,
                    name: "Tran Van B",
                    email: "tvb@mail.com",
                    course: "C++",
                    phone: "0981234567",
                    address: "123 Quang Nam, Da Nang"
                }
            ],
            showAddForm: false,
            editingStudent: null,
            form: { id: null, name: "", email: "", course: "", phone: "", address: "" }
        };
    },
    methods: {
        saveStudent() {
            if (this.editingStudent) {
                Object.assign(this.editingStudent, this.form);
                this.editingStudent = null;
            } else {
                this.students.push({ ...this.form, id: Date.now() });
            }
            this.resetForm();
        },
        editStudent(student) {
            this.editingStudent = student;
            this.form = { ...student };
        },
        deleteStudent(id) {
            this.students = this.students.filter(s => s.id !== id);
        },
        cancelEdit() {
            this.resetForm();
            this.editingStudent = null;
        },
        resetForm() {
            this.showAddForm = false;
            this.form = { id: null, name: "", email: "", course: "", phone: "", address: "" };
        }
    }
};
</script>
