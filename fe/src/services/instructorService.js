/**
 * Dịch vụ API cho các chức năng Giảng viên
 * Xử lý tất cả các gọi API liên quan đến giảng viên
 */

const API_BASE_URL = 'http://localhost:5000/api'

class InstructorService {
  /**
   * Lấy thông tin dashboard giảng viên
   * @param {number} instructorId - ID của giảng viên
   * @returns {Promise<Object>} Dữ liệu dashboard
   */
  async getDashboard(instructorId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/instructor/dashboard?instructor_id=${instructorId}`
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching dashboard:', error)
      throw error
    }
  }

  /**
   * Lấy thống kê chi tiết của giảng viên
   * @param {number} instructorId - ID của giảng viên
   * @returns {Promise<Object>} Dữ liệu thống kê
   */
  async getStatistics(instructorId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/instructor/statistics?instructor_id=${instructorId}`
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching statistics:', error)
      throw error
    }
  }

  /**
   * Lấy danh sách khóa học của giảng viên
   * @param {number} instructorId - ID của giảng viên
   * @returns {Promise<Array>} Danh sách khóa học
   */
  async getCourses(instructorId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/courses?instructor_id=${instructorId}`
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching courses:', error)
      throw error
    }
  }

  /**
   * Tạo khóa học mới
   * @param {Object} courseData - Dữ liệu khóa học
   * @returns {Promise<Object>} Khóa học được tạo
   */
  async createCourse(courseData) {
    try {
      const response = await fetch(`${API_BASE_URL}/courses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(courseData)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error creating course:', error)
      throw error
    }
  }

  /**
   * Cập nhật khóa học
   * @param {number} courseId - ID khóa học
   * @param {Object} courseData - Dữ liệu cập nhật
   * @returns {Promise<Object>} Khóa học được cập nhật
   */
  async updateCourse(courseId, courseData) {
    try {
      const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(courseData)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error updating course:', error)
      throw error
    }
  }

  /**
   * Xóa khóa học
   * @param {number} courseId - ID khóa học
   * @returns {Promise<Object>} Kết quả xóa
   */
  async deleteCourse(courseId) {
    try {
      const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
        method: 'DELETE'
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error deleting course:', error)
      throw error
    }
  }

  /**
   * Lấy thông tin chi tiết khóa học
   * @param {number} courseId - ID khóa học
   * @returns {Promise<Object>} Thông tin khóa học
   */
  async getCourseDetails(courseId) {
    try {
      const response = await fetch(`${API_BASE_URL}/courses/${courseId}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching course details:', error)
      throw error
    }
  }

  /**
   * Lấy curriculum (chương - bài học) của khóa học
   * @param {number} courseId - ID khóa học
   * @returns {Promise<Array>} Danh sách chương
   */
  async getCurriculum(courseId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/courses/${courseId}/curriculum`
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching curriculum:', error)
      throw error
    }
  }

  /**
   * Tạo section mới
   * @param {number} courseId - ID khóa học
   * @param {Object} sectionData - Dữ liệu section
   * @returns {Promise<Object>} Section được tạo
   */
  async createSection(courseId, sectionData) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/courses/${courseId}/sections`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(sectionData)
        }
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error creating section:', error)
      throw error
    }
  }

  /**
   * Cập nhật section
   * @param {number} sectionId - ID section
   * @param {Object} sectionData - Dữ liệu cập nhật
   * @returns {Promise<Object>} Section được cập nhật
   */
  async updateSection(sectionId, sectionData) {
    try {
      const response = await fetch(`${API_BASE_URL}/sections/${sectionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(sectionData)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error updating section:', error)
      throw error
    }
  }

  /**
   * Xóa section
   * @param {number} sectionId - ID section
   * @returns {Promise<Object>} Kết quả xóa
   */
  async deleteSection(sectionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/sections/${sectionId}`, {
        method: 'DELETE'
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error deleting section:', error)
      throw error
    }
  }

  /**
   * Tạo lesson mới
   * @param {number} sectionId - ID section
   * @param {Object} lessonData - Dữ liệu lesson
   * @returns {Promise<Object>} Lesson được tạo
   */
  async createLesson(sectionId, lessonData) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/sections/${sectionId}/lessons`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(lessonData)
        }
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error creating lesson:', error)
      throw error
    }
  }

  /**
   * Cập nhật lesson
   * @param {number} lessonId - ID lesson
   * @param {Object} lessonData - Dữ liệu cập nhật
   * @returns {Promise<Object>} Lesson được cập nhật
   */
  async updateLesson(lessonId, lessonData) {
    try {
      const response = await fetch(`${API_BASE_URL}/lessons/${lessonId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(lessonData)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error updating lesson:', error)
      throw error
    }
  }

  /**
   * Xóa lesson
   * @param {number} lessonId - ID lesson
   * @returns {Promise<Object>} Kết quả xóa
   */
  async deleteLesson(lessonId) {
    try {
      const response = await fetch(`${API_BASE_URL}/lessons/${lessonId}`, {
        method: 'DELETE'
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error deleting lesson:', error)
      throw error
    }
  }

  /**
   * Lấy danh sách test của lesson
   * @param {number} lessonId - ID lesson
   * @returns {Promise<Array>} Danh sách test
   */
  async getTests(lessonId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/lessons/${lessonId}/tests`
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching tests:', error)
      throw error
    }
  }

  /**
   * Tạo test mới
   * @param {number} lessonId - ID lesson
   * @param {Object} testData - Dữ liệu test
   * @returns {Promise<Object>} Test được tạo
   */
  async createTest(lessonId, testData) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/lessons/${lessonId}/tests`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(testData)
        }
      )
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error creating test:', error)
      throw error
    }
  }

  /**
   * Cập nhật test
   * @param {number} testId - ID test
   * @param {Object} testData - Dữ liệu cập nhật
   * @returns {Promise<Object>} Test được cập nhật
   */
  async updateTest(testId, testData) {
    try {
      const response = await fetch(`${API_BASE_URL}/tests/${testId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error updating test:', error)
      throw error
    }
  }

  /**
   * Xóa test
   * @param {number} testId - ID test
   * @returns {Promise<Object>} Kết quả xóa
   */
  async deleteTest(testId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tests/${testId}`, {
        method: 'DELETE'
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error deleting test:', error)
      throw error
    }
  }

  /**
   * Lấy instructor ID từ local storage
   * @returns {number|null} ID của giảng viên
   */
  getInstructorId() {
    const instructorId = localStorage.getItem('instructorId') ||
                        sessionStorage.getItem('instructorId')
    
    if (!instructorId) {
      try {
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        return userInfo.instructorId || userInfo.id || null
      } catch (e) {
        return null
      }
    }
    
    return instructorId
  }

  /**
   * Format tiền tệ theo định dạng Việt Nam
   * @param {number} amount - Số tiền
   * @returns {string} Tiền đã format
   */
  formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      minimumFractionDigits: 0
    }).format(amount)
  }
}

export default new InstructorService()
