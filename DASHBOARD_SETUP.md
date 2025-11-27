# Hướng Dẫn Hoàn Thiện Dashboard Giảng Viên

## Tổng Quan

Dashboard giảng viên đã được hoàn thiện với liên kết đầy đủ giữa frontend và backend. Giáo viên có thể xem thống kê khóa học, học viên, đánh giá và doanh thu một cách thời gian thực.

## API Endpoints Mới

### 1. Dashboard Giảng Viên
```
GET /api/instructor/dashboard?instructor_id=X

Response:
{
  "instructor": {
    "id": 1,
    "name": "Nguyễn Văn A",
    "email": "instructor@example.com",
    "avatar": "https://...",
    "expertise": "Web Development",
    "yearsExperience": 5
  },
  "stats": {
    "totalCourses": 5,
    "totalStudents": 124,
    "averageRating": 4.8,
    "totalRevenue": 12500000
  },
  "recentCourses": [
    {
      "id": 1,
      "title": "Lập trình Vue.js cơ bản",
      "description": "...",
      "level": "beginner",
      "price": 299000,
      "students": 45,
      "status": "active",
      "createdAt": "2025-01-15T10:30:00",
      "updatedAt": "2025-01-20T15:45:00"
    }
  ]
}
```

### 2. Thống Kê Chi Tiết
```
GET /api/instructor/statistics?instructor_id=X

Response:
{
  "coursesByLevel": {
    "beginner": 2,
    "intermediate": 2,
    "advanced": 1
  },
  "coursesByStatus": {
    "active": 4,
    "draft": 1
  },
  "studentsByStatus": {
    "enrolled": 100,
    "completed": 20,
    "dropped": 4
  },
  "averageStudentsPerCourse": 24.8,
  "totalLessons": 45,
  "totalTests": 12
}
```

## Frontend Components

### Dashboard.vue
Thành phần chính hiển thị:
- **Thống kê nhanh**: Khóa học, học viên, đánh giá, doanh thu
- **Danh sách khóa học gần đây**: 5 khóa học mới nhất
- **Thao tác nhanh**: Tạo khóa học, xem báo cáo, tin nhắn, quản lý khóa học

### instructorService.js
Dịch vụ API giúp:
- Gọi API dashboard và thống kê
- Quản lý khóa học (tạo, cập nhật, xóa)
- Quản lý sections và lessons
- Quản lý tests
- Format dữ liệu và tiền tệ

## Cách Sử Dụng

### Trong Component Vue

```vue
import instructorService from '@/services/instructorService'

export default {
  methods: {
    async loadData() {
      const instructorId = instructorService.getInstructorId()
      const dashboard = await instructorService.getDashboard(instructorId)
      const statistics = await instructorService.getStatistics(instructorId)
    },
    
    async createCourse(courseData) {
      const result = await instructorService.createCourse(courseData)
    },
    
    async updateCourse(courseId, courseData) {
      const result = await instructorService.updateCourse(courseId, courseData)
    }
  }
}
```

## Lưu Trữ Instructor ID

Khi người dùng đăng nhập, hãy lưu instructor ID:

```javascript
// Trong Auth.vue hoặc login handler
localStorage.setItem('instructorId', user.instructorId)
localStorage.setItem('userInfo', JSON.stringify({
  id: user.id,
  instructorId: user.instructorId,
  email: user.email,
  name: user.name,
  role: user.role
}))
```

## Ghi Chú Quan Trọng

1. **API Base URL**: Hiện tại là `http://localhost:5000/api`
   - Có thể thay đổi trong `instructorService.js` dòng 3
   - Cần cập nhật khi deploy lên production

2. **Thống Kê Doanh Thu**: 
   - Hiện tại tính dựa trên `price * số học viên hoàn thành`
   - Trong tương lai có thể dùng bảng `Invoices` để tính chính xác hơn

3. **Đánh Giá Trung Bình**:
   - Hiện tại là giá trị cố định 4.5
   - Cần thêm bảng `Ratings` để lưu đánh giá từ học viên

4. **Empty State**:
   - Khi không có khóa học, sẽ hiển thị message "Chưa có khóa học nào"

5. **Error Handling**:
   - Tất cả lỗi API đều được log console và hiển thị default data
   - Có thể thêm toast notification nếu cần

## Testing

### Test Dashboard Load
```bash
curl "http://localhost:5000/api/instructor/dashboard?instructor_id=1"
```

### Test Statistics
```bash
curl "http://localhost:5000/api/instructor/statistics?instructor_id=1"
```

### Test Courses List
```bash
curl "http://localhost:5000/api/courses?instructor_id=1"
```

## Các Feature Tiếp Theo

1. **Real-time Updates**: Dùng WebSocket để cập nhật dữ liệu thời gian thực
2. **Advanced Statistics**: Biểu đồ chi tiết về tiến độ học viên
3. **Student Analytics**: Phân tích hiệu suất từng học viên
4. **Revenue Tracking**: Theo dõi chi tiết doanh thu
5. **Notifications**: Thông báo về sinh viên mới, hoàn thành khóa học, v.v.

## Troubleshooting

### Dashboard không load dữ liệu
- Kiểm tra console xem có lỗi không
- Xác minh instructorId được lưu đúng
- Kiểm tra backend API có chạy không

### API trả về 404
- Kiểm tra instructor_id có tồn tại không
- Xác minh database có dữ liệu không

### Tiền tệ không format đúng
- Kiểm tra `instructorService.formatCurrency()`
- Có thể cần cập nhật locale theo từng khu vực

## Liên Hệ Backend API

**Instructor.py** routes mới:
- `/api/instructor/dashboard` - Lấy dashboard
- `/api/instructor/statistics` - Lấy thống kê

Tất cả routes khác đã tồn tại như:
- `/api/courses` - Quản lý khóa học
- `/api/sections` - Quản lý chapters
- `/api/lessons` - Quản lý bài học
- `/api/tests` - Quản lý tests
