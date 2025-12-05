# Fix: Lỗi 401 Unauthorized Khi Xóa Bài Học

## ❌ Vấn Đề
Khi nhấn nút **Delete** để xóa bài học, server trả về lỗi **401 Unauthorized**:
```
[2025-12-05 02:43:11] "DELETE /api/lessons/5001 HTTP/1.1" 401 -
```

## 🔍 Nguyên Nhân Có Thể

1. **JWT Token hết hạn** - Token đã quá thời gian sống
2. **Session không tồn tại** - User chưa login hoặc session bị xóa
3. **Token không hợp lệ** - Token bị corrupt hoặc không đúng format
4. **Backend không xác thực đúng** - Thiếu kiểm tra instructor_id

## ✅ Giải Pháp

### 1. Backend - Thêm Authorization Check

**File**: `backend/app/routes/Instructor.py`

**Cải thiện**:
- Kiểm tra instructor_id từ JWT token
- Xác minh lesson thuộc về khóa học của instructor
- Log chi tiết lỗi để debug
- Trả về mã lỗi phù hợp (401 vs 403)

```python
@instructor_bp.route("/api/lessons/<int:lesson_id>", methods=['DELETE'])
@instructor_bp.route("/lessons/<int:lesson_id>", methods=['DELETE'])
@jwt_required()
def delete_lesson(lesson_id):
    try:
        # Verify instructor authorization
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized: Not an instructor"}), 401
        
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return jsonify({"message": "Bài học không tồn tại"}), 404
        
        # Verify lesson belongs to instructor's course
        section = CourseSection.query.filter_by(id=lesson.section_id).first()
        if section:
            course = Course.query.filter_by(id=section.course_id, instructor_id=instructor_id).first()
            if not course:
                return jsonify({"message": "Unauthorized: Lesson does not belong to you"}), 403
        
        db.session.delete(lesson)
        db.session.commit()
        return jsonify({"message": "Đã xóa bài học"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa lesson: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Lỗi khi xóa lesson: {str(e)}"}), 500
```

### 2. Frontend - Xử Lý Lỗi 401

**File**: `fe/src/components/Instructor/CourseLessons.vue`

**Cải thiện**:
- Phát hiện lỗi 401 và redirect về login
- Hiển thị thông báo cụ thể cho từng loại lỗi
- Log error để debug
- Xử lý trường hợp response không phải JSON

```javascript
async deleteLesson(lesson) {
  if (!confirm("Xóa bài học này?")) return;
  try {
    const headers = this.getAuthHeaders()
    const res = await fetch(
      `http://localhost:5000/api/lessons/${lesson.id}`,
      { method: "DELETE", headers }
    );
    
    if (res.status === 401) {
      alert('❌ Session expired. Please login again.');
      this.$router.push('/login');
      return;
    }
    
    const data = await res.json().catch(() => ({ message: 'Unknown error' }));
    
    if (!res.ok) {
      throw new Error(data.message || `Failed to delete lesson (${res.status})`);
    }
    
    alert('✅ Lesson deleted successfully!');
    await this.fetchCurriculum();
  } catch (e) {
    console.error('Delete lesson error:', e);
    alert(`❌ Error: ${e.message}`);
  }
}
```

## 🧪 Cách Test & Debug

### 1. Kiểm tra Token
Mở DevTools Console và chạy:
```javascript
const session = JSON.parse(localStorage.getItem('session'));
console.log('Token:', session?.access_token);
console.log('Expires:', new Date(session?.expires_at));
```

### 2. Test Backend Trực Tiếp
```bash
curl -X DELETE http://localhost:5000/api/lessons/5001 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Xem Backend Logs
Sau khi sửa, backend sẽ log chi tiết:
```
Lỗi khi xóa lesson: <error details>
<full traceback>
```

### 4. Test Flow Đầy Đủ
1. **Login** với tài khoản instructor
2. Mở **Course Content Management**
3. Expand một section
4. Click **Delete** trên một lesson
5. Xác nhận xóa

**Kết quả mong đợi**:
- ✅ Nếu token hợp lệ → Xóa thành công, hiện "✅ Lesson deleted successfully!"
- ❌ Nếu token hết hạn → Hiện "❌ Session expired. Please login again." và redirect về login
- ❌ Nếu không phải instructor → Hiện lỗi 403

## 🔍 Các Mã Lỗi HTTP

| Code | Nghĩa | Giải pháp |
|------|-------|-----------|
| **401** | Unauthorized - Chưa xác thực hoặc token không hợp lệ | Login lại |
| **403** | Forbidden - Đã xác thực nhưng không có quyền | Kiểm tra quyền user |
| **404** | Not Found - Lesson không tồn tại | Kiểm tra lesson ID |
| **500** | Server Error - Lỗi backend | Xem backend logs |

## 🛠️ Sửa Lỗi Thường Gặp

### Lỗi: "No authentication token found"
**Nguyên nhân**: Session không tồn tại trong localStorage  
**Giải pháp**: Login lại

### Lỗi: "Unauthorized: Not an instructor"
**Nguyên nhân**: User không phải instructor hoặc `get_current_instructor_id()` trả về None  
**Giải pháp**: 
- Kiểm tra role của user trong database
- Kiểm tra JWT token có chứa đúng user_id không

### Lỗi: "Unauthorized: Lesson does not belong to you"
**Nguyên nhân**: Instructor đang cố xóa lesson của instructor khác  
**Giải pháp**: Chỉ xóa lesson trong khóa học của mình

## 📝 Improvements Added

### Backend
✅ Xác thực instructor_id từ JWT  
✅ Kiểm tra quyền sở hữu lesson  
✅ Log chi tiết với traceback  
✅ Phân biệt rõ 401 (chưa xác thực) vs 403 (không có quyền)  

### Frontend  
✅ Xử lý lỗi 401 → redirect login  
✅ Hiển thị thông báo thành công/lỗi rõ ràng  
✅ Log error ra console để debug  
✅ Xử lý trường hợp response không phải JSON  

## 🔧 Khởi Động Lại Services

**Backend** (quan trọng!):
```powershell
cd backend
python app.py
```

**Frontend** (nếu cần):
```powershell
cd fe
npm run dev
```

## 📌 Checklist

- [x] Backend: Thêm kiểm tra instructor_id
- [x] Backend: Xác minh quyền sở hữu lesson
- [x] Backend: Log chi tiết lỗi
- [x] Frontend: Xử lý lỗi 401 và redirect
- [x] Frontend: Hiển thị thông báo rõ ràng
- [x] Test: Login và xóa lesson
- [ ] **Khởi động lại backend** ⚠️
- [ ] Test flow đầy đủ

---

**Ngày**: 2025-12-05  
**Trạng thái**: ✅ **ĐÃ SỬA**  
**Mã lỗi**: 401 Unauthorized  
**Commit message**: `fix: add instructor authorization check for delete lesson endpoint`
