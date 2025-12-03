import { getStoredSession } from "./authService";

const API_ROOT = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
const API_BASE_URL = `${API_ROOT}/admin`

const handleJson = async (res, context) => {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${context} (${res.status}): ${text || res.statusText}`)
  }
  return res.json()
}

class AdminService {
  authHeaders() {
    const session = getStoredSession()
    return session?.access_token
      ? { Authorization: `Bearer ${session.access_token}`, "Content-Type": "application/json" }
      : { "Content-Type": "application/json" }
  }

  async getDashboard() {
    const res = await fetch(`${API_BASE_URL}/dashboard/overview`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load admin dashboard')
  }

  async getCourses() {
    const res = await fetch(`${API_BASE_URL}/courses`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load courses')
  }

  async deleteCourse(courseId) {
    const res = await fetch(`${API_BASE_URL}/courses/${courseId}`, { method: 'DELETE', headers: this.authHeaders() })
    return handleJson(res, 'Failed to delete course')
  }

  async createCourse(payload) {
    const res = await fetch(`${API_BASE_URL}/courses`, {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify(payload),
    })
    return handleJson(res, 'Failed to create course')
  }

  async getStudents() {
    const res = await fetch(`${API_BASE_URL}/students`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load students')
  }

  async createStudent(payload) {
    const res = await fetch(`${API_BASE_URL}/students`, {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify(payload),
    })
    return handleJson(res, 'Failed to create student')
  }

  async updateStudent(studentId, payload) {
    const res = await fetch(`${API_BASE_URL}/students/${studentId}`, {
      method: 'PUT',
      headers: this.authHeaders(),
      body: JSON.stringify(payload),
    })
    return handleJson(res, 'Failed to update student')
  }

  async deleteStudent(studentId) {
    const res = await fetch(`${API_BASE_URL}/students/${studentId}`, { method: 'DELETE', headers: this.authHeaders() })
    return handleJson(res, 'Failed to delete student')
  }

  async getInstructors() {
    const res = await fetch(`${API_BASE_URL}/instructors`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load instructors')
  }

  async createInstructor(payload) {
    const res = await fetch(`${API_BASE_URL}/instructors`, {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify(payload),
    })
    return handleJson(res, 'Failed to create instructor')
  }

  async updateInstructor(instId, payload) {
    const res = await fetch(`${API_BASE_URL}/instructors/${instId}`, {
      method: 'PUT',
      headers: this.authHeaders(),
      body: JSON.stringify(payload),
    })
    return handleJson(res, 'Failed to update instructor')
  }

  async deleteInstructor(instId) {
    const res = await fetch(`${API_BASE_URL}/instructors/${instId}`, { method: 'DELETE', headers: this.authHeaders() })
    return handleJson(res, 'Failed to delete instructor')
  }

  async getDashboardAnalytics(year) {
    const res = await fetch(`${API_BASE_URL}/dashboard/analytics?year=${year}`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load dashboard analytics')
  }

  async getReportsSummary() {
    const res = await fetch(`${API_BASE_URL}/reports/summary`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load reports summary')
  }

  async getRoles() {
    const res = await fetch(`${API_BASE_URL}/roles`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load roles')
  }

  async getRoleSummary() {
    const res = await fetch(`${API_BASE_URL}/roles/summary`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load role summary')
  }

  // VietQR invoices
  async getPendingInvoices() {
    const res = await fetch(`${API_BASE_URL}/invoices/pending`, { headers: this.authHeaders() })
    return handleJson(res, 'Failed to load pending invoices')
  }

  async approveInvoice(invoiceNumber) {
    const res = await fetch(`${API_BASE_URL}/invoices/${invoiceNumber}/approve`, {
      method: 'POST',
      headers: this.authHeaders(),
    })
    return handleJson(res, 'Failed to approve invoice')
  }

  async rejectInvoice(invoiceNumber) {
    const res = await fetch(`${API_BASE_URL}/invoices/${invoiceNumber}/reject`, {
      method: 'POST',
      headers: this.authHeaders(),
    })
    return handleJson(res, 'Failed to reject invoice')
  }
}

export default new AdminService()
