<template>
  <div class="admin-role-management">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">Role Management</h1>
          <p class="page-subtitle">Manage roles and permissions across the platform</p>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <i class="fas fa-search search-icon"></i>
            <input 
              v-model="searchQuery" 
              type="text" 
              class="search-input" 
              placeholder="Search roles..." 
            />
          </div>
          <button class="btn btn-primary btn-add-role" @click="openAdd">
            <i class="fas fa-plus-circle"></i>
            Add New Role
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="stats-overview">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total-roles">
            <i class="fas fa-user-tag"></i>
          </div>
          <div class="stat-content">
            <h3>{{ roles.length }}</h3>
            <p>Total Roles</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon admin-users">
            <i class="fas fa-user-shield"></i>
          </div>
          <div class="stat-content">
            <h3>{{ adminUsersCount }}</h3>
            <p>Admin Users</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon instructor-users">
            <i class="fas fa-chalkboard-teacher"></i>
          </div>
          <div class="stat-content">
            <h3>{{ instructorUsersCount }}</h3>
            <p>Instructors</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon student-users">
            <i class="fas fa-user-graduate"></i>
          </div>
          <div class="stat-content">
            <h3>{{ studentUsersCount }}</h3>
            <p>Students</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Roles Table -->
    <div class="table-container">
      <div class="table-card">
        <div class="table-header">
          <h3>Role List</h3>
          <div class="table-actions">
            <button class="btn btn-outline">
              <i class="fas fa-download"></i>
              Export
            </button>
          </div>
        </div>

        <div class="table-responsive">
          <table class="roles-table">
            <thead>
              <tr>
                <th class="role-id">ID</th>
                <th class="role-name">Role Name</th>
                <th class="role-description">Description</th>
                <th class="role-users">Users</th>
                <th class="role-permissions">Permissions</th>
                <th class="role-status">Status</th>
                <th class="role-actions">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="role in filteredRoles" :key="role.id" class="role-row">
                <td class="role-id">
                  <span class="role-badge">#{{ role.id }}</span>
                </td>
                <td class="role-name">
                  <div class="role-info">
                    <div class="role-avatar" :class="getRoleColor(role.name)">
                      <i :class="getRoleIcon(role.name)"></i>
                    </div>
                    <div class="role-details">
                      <span class="role-title">{{ role.name }}</span>
                      <span class="role-type">{{ role.type }}</span>
                    </div>
                  </div>
                </td>
                <td class="role-description">
                  <span class="description-text">{{ role.description }}</span>
                </td>
                <td class="role-users">
                  <div class="users-count">
                    <i class="fas fa-users"></i>
                    {{ role.users }}
                  </div>
                </td>
                <td class="role-permissions">
                  <div class="permissions-list">
                    <span class="permission-tag" v-for="perm in role.permissions.slice(0, 2)" :key="perm">
                      {{ perm }}
                    </span>
                    <span v-if="role.permissions.length > 2" class="permission-more">
                      +{{ role.permissions.length - 2 }} more
                    </span>
                  </div>
                </td>
                <td class="role-status">
                  <span class="status-badge" :class="role.status === 'Active' ? 'active' : 'inactive'">
                    <i :class="role.status === 'Active' ? 'fas fa-check-circle' : 'fas fa-pause-circle'"></i>
                    {{ role.status }}
                  </span>
                </td>
                <td class="role-actions">
                  <div class="action-buttons">
                    <button class="btn-action btn-edit" @click="editRole(role)" title="Edit Role">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action btn-view" @click="viewPermissions(role)" title="View Permissions">
                      <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-action btn-users" @click="manageUsers(role)" title="Manage Users">
                      <i class="fas fa-users"></i>
                    </button>
                    <button class="btn-action btn-delete" @click="deleteRole(role.id)" title="Delete Role">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="filteredRoles.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-user-tag"></i>
          </div>
          <h3>No roles found</h3>
          <p>Try adjusting your search criteria</p>
          <button class="btn btn-primary" @click="resetSearch">
            <i class="fas fa-refresh"></i>
            Reset Search
          </button>
        </div>

        <!-- Table Footer -->
        <div v-if="filteredRoles.length > 0" class="table-footer">
          <div class="pagination-info">
            Showing {{ filteredRoles.length }} of {{ roles.length }} roles
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Role Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Role' : 'Add New Role' }}</h3>
          <button class="modal-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Role Name</label>
            <input 
              v-model="form.name" 
              type="text" 
              class="form-input" 
              placeholder="Enter role name"
            />
          </div>
          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea 
              v-model="form.description" 
              class="form-textarea" 
              placeholder="Enter role description"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Role Type</label>
            <select v-model="form.type" class="form-select">
              <option value="System">System</option>
              <option value="Custom">Custom</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Permissions</label>
            <div class="permissions-grid">
              <label v-for="permission in availablePermissions" :key="permission" class="permission-checkbox">
                <input 
                  type="checkbox" 
                  :value="permission" 
                  v-model="form.permissions"
                />
                <span class="checkmark"></span>
                {{ permission }}
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" @click="saveRole">
            {{ isEditing ? 'Update Role' : 'Create Role' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import adminService from '@/services/adminService'

export default {
  name: 'RoleManagement',
  setup() {
    // Reactive data
    const roles = ref([])
    const summary = ref({ totalRoles: 0, adminUsers: 0, instructors: 0, students: 0 })

    const searchQuery = ref("")
    const showModal = ref(false)
    const isEditing = ref(false)
    const form = ref({
      id: null,
      name: "",
      description: "",
      type: "Custom",
      permissions: [],
      users: 0,
      status: "Active"
    })

    const availablePermissions = ref([
      "user_management",
      "course_management",
      "content_management",
      "settings_management",
      "analytics_view",
      "content_moderation",
      "user_moderation",
      "course_access",
      "content_view",
      "media_upload",
      "student_management"
    ])

    const loadRoles = async () => {
      try {
        const [rolesRes, summaryRes] = await Promise.all([
          adminService.getRoles(),
          adminService.getRoleSummary()
        ])
        roles.value = rolesRes.roles || []
        summary.value = {
          totalRoles: summaryRes.totalRoles || (rolesRes.roles ? rolesRes.roles.length : 0),
          adminUsers: summaryRes.adminUsers || 0,
          instructors: summaryRes.instructors || 0,
          students: summaryRes.students || 0
        }
      } catch (error) {
        console.error('Failed to load roles data', error)
      }
    }

    // Computed properties
    const filteredRoles = computed(() => {
      if (!searchQuery.value) {
        return roles.value
      }
      const query = searchQuery.value.toLowerCase()
      return roles.value.filter(role => 
        role.name.toLowerCase().includes(query) || 
        role.description.toLowerCase().includes(query) ||
        role.type.toLowerCase().includes(query)
      )
    })

    const adminUsersCount = computed(() => summary.value.adminUsers || 0)
    const instructorUsersCount = computed(() => summary.value.instructors || 0)
    const studentUsersCount = computed(() => summary.value.students || 0)

    // Methods
    const getRoleIcon = (roleName) => {
      const icons = {
        'Admin': 'fas fa-user-shield',
        'Instructor': 'fas fa-chalkboard-teacher',
        'Student': 'fas fa-user-graduate',
        'Content Manager': 'fas fa-file-alt',
        'Moderator': 'fas fa-gavel'
      }
      return icons[roleName] || 'fas fa-user-tag'
    }

    const getRoleColor = (roleName) => {
      const colors = {
        'Admin': 'role-admin',
        'Instructor': 'role-instructor',
        'Student': 'role-student',
        'Content Manager': 'role-content',
        'Moderator': 'role-moderator'
      }
      return colors[roleName] || 'role-default'
    }

    const openAdd = () => {
      isEditing.value = false
      form.value = {
        id: null,
        name: "",
        description: "",
        type: "Custom",
        permissions: [],
        users: 0,
        status: "Active"
      }
      showModal.value = true
    }

    const editRole = (role) => {
      isEditing.value = true
      form.value = { ...role }
      showModal.value = true
    }

    const saveRole = () => {
      if (isEditing.value) {
        const index = roles.value.findIndex(r => r.id === form.value.id)
        if (index !== -1) {
          roles.value[index] = { ...form.value }
        }
      } else {
        const newRole = {
          ...form.value,
          id: Math.max(...roles.value.map(r => r.id)) + 1
        }
        roles.value.push(newRole)
      }
      closeModal()
    }

    const deleteRole = (id) => {
      if (confirm("Are you sure you want to delete this role? This action cannot be undone.")) {
        roles.value = roles.value.filter(role => role.id !== id)
      }
    }

    const viewPermissions = (role) => {
      alert(`Viewing permissions for: ${role.name}\n\nPermissions: ${role.permissions.join(', ')}`)
    }

    const manageUsers = (role) => {
      alert(`Managing users for role: ${role.name}`)
    }

    const closeModal = () => {
      showModal.value = false
    }

    const resetSearch = () => {
      searchQuery.value = ""
    }

    onMounted(() => {
      loadRoles()
    })

    return {
      roles,
      searchQuery,
      filteredRoles,
      showModal,
      isEditing,
      form,
      availablePermissions,
      adminUsersCount,
      instructorUsersCount,
      studentUsersCount,
      openAdd,
      editRole,
      saveRole,
      deleteRole,
      viewPermissions,
      manageUsers,
      closeModal,
      resetSearch,
      getRoleIcon,
      getRoleColor
    }
  }
}
</script>

<style scoped>
.admin-role-management {
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

.btn-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #475569;
}

.btn-outline:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-secondary {
  background: #64748b;
  color: white;
}

.btn-secondary:hover {
  background: #475569;
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

.stat-icon.total-roles { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }
.stat-icon.admin-users { background: linear-gradient(135deg, #ef4444, #f87171); }
.stat-icon.instructor-users { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-icon.student-users { background: linear-gradient(135deg, #10b981, #34d399); }

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

.roles-table {
  width: 100%;
  border-collapse: collapse;
}

.roles-table th {
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

.roles-table td {
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
}

.role-row:hover {
  background: #f8fafc;
}

/* Role Info */
.role-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.role-admin { background: linear-gradient(135deg, #ef4444, #f87171); }
.role-instructor { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.role-student { background: linear-gradient(135deg, #10b981, #34d399); }
.role-content { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }
.role-moderator { background: linear-gradient(135deg, #06b6d4, #22d3ee); }
.role-default { background: linear-gradient(135deg, #64748b, #94a3b8); }

.role-details {
  display: flex;
  flex-direction: column;
}

.role-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.role-type {
  font-size: 12px;
  color: #64748b;
}

.role-badge {
  background: #f1f5f9;
  color: #475569;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

/* Permissions */
.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.permission-tag {
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.permission-more {
  color: #64748b;
  font-size: 11px;
  font-weight: 500;
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
.btn-users { background: #8b5cf6; }
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #475569;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 24px;
  border-top: 1px solid #f1f5f9;
}

/* Form Styles */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* Permissions Grid */
.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.permission-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.permission-checkbox input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s ease;
}

.permission-checkbox input[type="checkbox"]:checked + .checkmark {
  background: #3b82f6;
  border-color: #3b82f6;
}

.permission-checkbox input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-role-management {
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
  
  .table-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .roles-table {
    font-size: 14px;
  }
  
  .modal-content {
    margin: 20px;
    width: calc(100% - 40px);
  }
}
</style>
