<template>
    <div class="adm container mt-5">
        <div class="card shadow-lg rounded-3">
            <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                <h4 class="mb-0">👨‍🏫 Instructor Management</h4>
                <button class="btn btn-light btn-sm" @click="showAddForm = true">
                    + Add Instructor
                </button>
            </div>

            <div class="card-body">
                <!-- Add/Edit Form -->
                <div v-if="showAddForm || editingInstructor" class="mb-4">
                    <h5 class="text-secondary mb-3">
                        {{ editingInstructor ? "Edit Instructor" : "Add New Instructor" }}
                    </h5>
                    <form @submit.prevent="saveInstructor" class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label">Full Name</label>
                            <input v-model="form.name" type="text" class="form-control" required />
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Email</label>
                            <input v-model="form.email" type="email" class="form-control" required />
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Expertise</label>
                            <input v-model="form.expertise" type="text" class="form-control" required />
                        </div>
                        <div class="col-12">
                            <button type="submit" class="btn btn-success me-2">Save</button>
                            <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
                        </div>
                    </form>
                    <hr />
                </div>

                <!-- Instructors Table -->
                <table class="table table-bordered table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>#</th>
                            <th>Full Name</th>
                            <th>Email</th>
                            <th>Expertise</th>
                            <th class="text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(instructor, index) in instructors" :key="instructor.id">
                            <td>{{ index + 1 }}</td>
                            <td>{{ instructor.name }}</td>
                            <td>{{ instructor.email }}</td>
                            <td>{{ instructor.expertise }}</td>
                            <td class="text-center">
                                <button class="btn btn-warning btn-sm me-2"
                                    @click="editInstructor(instructor)">Edit</button>
                                <button class="btn btn-danger btn-sm"
                                    @click="deleteInstructor(instructor.id)">Delete</button>
                            </td>
                        </tr>
                        <tr v-if="instructors.length === 0">
                            <td colspan="5" class="text-center text-muted">No instructors available</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "InstructorManagement",
    data() {
        return {
            instructors: [
                { id: 1, name: "Dr. Emily Brown", email: "emily@mail.com", expertise: "Machine Learning" },
                { id: 2, name: "John Doe", email: "john@mail.com", expertise: "Web Development" }
            ],
            showAddForm: false,
            editingInstructor: null,
            form: { id: null, name: "", email: "", expertise: "" }
        };
    },
    methods: {
        saveInstructor() {
            if (this.editingInstructor) {
                Object.assign(this.editingInstructor, this.form);
                this.editingInstructor = null;
            } else {
                this.instructors.push({ ...this.form, id: Date.now() });
            }
            this.resetForm();
        },
        editInstructor(instructor) {
            this.editingInstructor = instructor;
            this.form = { ...instructor };
        },
        deleteInstructor(id) {
            this.instructors = this.instructors.filter(i => i.id !== id);
        },
        cancelEdit() {
            this.resetForm();
            this.editingInstructor = null;
        },
        resetForm() {
            this.showAddForm = false;
            this.form = { id: null, name: "", email: "", expertise: "" };
        }
    }
};
</script>
<style scoped>
.adm {
    max-width: 1200px;
    padding-top: 6rem;
}
</style>
