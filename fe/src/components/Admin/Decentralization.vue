<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Role Management</h2>
        <p class="text-muted mb-0">Manage roles and permissions easily</p>
      </div>
      <div class="d-flex gap-2 mt-3 mt-md-0">
        <input v-model="searchQuery" type="text" class="form-control form-control-sm" placeholder="Search..." />
        <button class="btn btn-sm btn-primary text-nowrap" @click="openAdd">
          Add Role
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Role Name</th>
              <th>Description</th>
              <th class="text-center">Users</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="role in filteredRoles" :key="role.id">
              <td>{{ role.id }}</td>
              <td class="fw-semibold text-primary">{{ role.name }}</td>
              <td>{{ role.description }}</td>
              <td class="text-center">{{ role.users }}</td>
              <td class="text-center">
                <button class="btn btn-sm btn-outline-secondary me-1" @click="editRole(role)">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button class="btn btn-sm btn-outline-success me-1" @click="editRole(role)">
                  <i class="fa-solid fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteRole(role.id)">
                  <i class="fa-solid fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="filteredRoles.length === 0">
              <td colspan="5" class="text-center text-muted py-3">No roles found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Add/Edit -->
    <div class="modal fade" id="roleModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? "Edit Role" : "Add Role" }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Role Name</label>
              <input v-model="form.name" type="text" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea v-model="form.description" class="form-control"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button class="btn btn-primary" @click="saveRole" data-bs-dismiss="modal">
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";

export default {
  name: "RoleManagement",
  setup() {
    const roles = ref([
      { id: 1, name: "Admin", description: "Full access", users: 5 },
      { id: 2, name: "Instructor", description: "Can create courses", users: 12 },
      { id: 3, name: "Student", description: "Can enroll in courses", users: 200 },
    ]);
    const searchQuery = ref("");
    const form = ref({ id: null, name: "", description: "" });
    const isEditing = ref(false);

    const filteredRoles = computed(() =>
      roles.value.filter((r) =>
        r.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    );

    const openAdd = () => {
      isEditing.value = false;
      form.value = { id: null, name: "", description: "" };
      new bootstrap.Modal(document.getElementById("roleModal")).show();
    };

    const editRole = (role) => {
      isEditing.value = true;
      form.value = { ...role };
      new bootstrap.Modal(document.getElementById("roleModal")).show();
    };

    const saveRole = () => {
      if (isEditing.value) {
        const idx = roles.value.findIndex((r) => r.id === form.value.id);
        if (idx !== -1) roles.value[idx] = { ...form.value };
      } else {
        roles.value.push({
          id: roles.value.length + 1,
          ...form.value,
          users: 0,
        });
      }
    };

    const deleteRole = (id) => {
      roles.value = roles.value.filter((r) => r.id !== id);
    };

    return { roles, searchQuery, filteredRoles, form, isEditing, openAdd, editRole, saveRole, deleteRole };
  },
};
</script>
