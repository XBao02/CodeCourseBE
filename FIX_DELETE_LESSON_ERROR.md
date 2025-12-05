# Fix: Lỗi Xóa Bài Học (Delete Lesson Error)

## ❌ Vấn Đề
Khi nhấn nút **Delete** để xóa bài học, xuất hiện lỗi:
```
Unexpected token '<', "<!doctype "... is not valid JSON
```

## 🔍 Nguyên Nhân
- **Frontend** gọi: `DELETE /api/lessons/{lesson_id}`
- **Backend** chỉ có route: `DELETE /lessons/{lesson_id}` (thiếu prefix `/api/`)
- Kết quả: Backend trả về HTML error page 404, frontend cố parse như JSON → lỗi

## ✅ Giải Pháp
Thêm route `/api/lessons/<int:lesson_id>` cho endpoint DELETE trong backend.

### Backend Fix - Instructor.py

**File**: `backend/app/routes/Instructor.py`

**Trước:**
```python
@instructor_bp.route("/lessons/<int:lesson_id>", methods=['DELETE'])
@jwt_required()
def delete_lesson(lesson_id):
    # ...
```

**Sau:**
```python
@instructor_bp.route("/api/lessons/<int:lesson_id>", methods=['DELETE'])
@instructor_bp.route("/lessons/<int:lesson_id>", methods=['DELETE'])
@jwt_required()
def delete_lesson(lesson_id):
    # ...
```

## 📝 Chi Tiết Thay Đổi

### 1. Backend - Instructor.py (dòng 533-534)
Thêm route decorator với prefix `/api/` để hỗ trợ cả hai dạng URL:
- `/api/lessons/{id}` (được frontend sử dụng)
- `/lessons/{id}` (backward compatibility)

### 2. Không Cần Thay Đổi Frontend
Frontend đã gọi đúng endpoint `/api/lessons/{id}`, không cần sửa gì.

## 🧪 Cách Test

1. **Khởi động lại backend** (quan trọng!):
   ```powershell
   cd backend
   python app.py
   ```

2. Mở trình duyệt, vào **Course Content Management**

3. Expand một section có bài học

4. Click nút **Delete** trên một bài học

5. Xác nhận xóa

6. **Kết quả mong đợi**: 
   - Bài học được xóa thành công
   - Không có lỗi JSON
   - Danh sách bài học tự động refresh

## 🎯 Các Endpoint Liên Quan Đã Kiểm Tra

Các endpoint khác đều đã có đầy đủ cả hai route (`/api/...` và `/...`):

✅ `POST /api/sections/{id}/lessons` - Tạo lesson mới  
✅ `PUT /api/lessons/{id}` - Cập nhật lesson  
✅ `DELETE /api/lessons/{id}` - **ĐÃ SỬA** ✅  
✅ `POST /api/lessons/{id}/tests` - Tạo test  
✅ `PUT /api/tests/{id}` - Cập nhật test  
✅ `DELETE /api/tests/{id}` - Xóa test  

## 📌 Lưu Ý

- **Luôn khởi động lại backend** sau khi sửa code Python
- Route decorator trong Flask hỗ trợ nhiều URL cho cùng một function
- Nên giữ cả hai dạng route (`/api/...` và `/...`) để backward compatibility

## 🔧 Nếu Vẫn Lỗi

1. **Kiểm tra backend đang chạy**: 
   ```powershell
   curl http://localhost:5000/api/courses
   ```

2. **Xem log backend** khi click Delete để xác định endpoint được gọi

3. **Kiểm tra token**: Đảm bảo đã đăng nhập và có JWT token hợp lệ

4. **Clear browser cache** và refresh trang

---

**Ngày**: 2025-12-05  
**Trạng thái**: ✅ **ĐÃ SỬA**  
**Commit message**: `fix: add /api/ prefix to DELETE /lessons endpoint`
