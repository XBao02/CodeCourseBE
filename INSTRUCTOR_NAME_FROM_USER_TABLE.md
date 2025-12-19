# Instructor Full Name Display - Implementation Summary

## Yêu Cầu
Tên của instructor phải được lấy từ trường `full_name` trong bảng `Users`, không phải từ bảng `Instructors`.

## Cấu Trúc Database

### Bảng Users
```python
class User(db.Model):
    __tablename__ = 'Users'
    
    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column('Email', db.String(190), unique=True, nullable=False)
    password_hash = db.Column('PasswordHash', db.String(255), nullable=False)
    full_name = db.Column('FullName', db.String(150), nullable=False)  # ⭐ Đây là trường chính
    role = db.Column('Role', db.String(50), nullable=False, default='student')
    avatar_url = db.Column('AvatarUrl', db.String(255))
    # ... các trường khác
    
    instructor = db.relationship('Instructor', backref='user', uselist=False)
```

### Bảng Instructors
```python
class Instructor(db.Model):
    __tablename__ = 'Instructors'
    
    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), unique=True, nullable=False)
    expertise = db.Column('Expertise', db.String(255))
    biography = db.Column('Biography', db.Text)
    years_experience = db.Column('YearsExperience', db.Integer, default=0)
    # Không có trường name/full_name
```

## Luồng Hoạt Động

### 1. 🔐 Login (Backend)
**File**: `backend/app/routes/Auth.py`

```python
@auth_bp.post("/login")
def login():
    # ... xác thực user
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": role,
            "full_name": user.full_name,  # ✅ Thêm full_name từ bảng Users
            "instructorId": instructor_id,
            "studentId": student_id,
        },
        "nextRoute": next_route,
    })
```

**Thay Đổi**: Thêm `"full_name": user.full_name` vào response của endpoint `/login`.

### 2. 💾 Lưu Session (Frontend)
**File**: `fe/src/services/authService.js`

Khi login thành công, response được lưu vào localStorage/sessionStorage:
```javascript
{
  "access_token": "eyJ...",
  "user": {
    "id": 1,
    "email": "instructor@example.com",
    "role": "instructor",
    "full_name": "Nguyễn Văn A",  // ⭐ full_name từ bảng Users
    "instructorId": 1
  },
  "nextRoute": "/instructor"
}
```

### 3. 🎨 Hiển Thị Tên (Frontend)
**File**: `fe/src/layout/components/Instructor/MenuInstructor.vue`

#### Method 1: Đọc từ Session (Ưu tiên)
```javascript
async loadUser() {
    const session = getStoredSession();
    console.log('🔍 MenuInstructor loading user from session:', session);
    
    const u = session?.user || {};
    const name = u.full_name || u.FullName || u.name || u.username || u.email?.split('@')[0];
    
    if (name) {
        this.instructorName = name;  // ✅ Lấy từ session.user.full_name
        console.log('✅ Got instructor name from session:', name);
    } else {
        // Fallback to backend profile
        await this.fetchProfile();
    }
}
```

#### Method 2: API Fallback (Nếu session không có)
```javascript
async fetchProfile() {
    const axios = (await import('axios')).default;
    const res = await axios.get('http://localhost:5000/api/instructor/profile', {
        headers: { Authorization: `Bearer ${session.access_token}` }
    });
    
    const instructor = res.data || {};
    const name = instructor.full_name || instructor.username || instructor.email?.split('@')[0] || '';
    if (name) {
        this.instructorName = name;  // ✅ Lấy từ API response
    }
}
```

### 4. 📡 API Profile Endpoint (Backend)
**File**: `backend/app/routes/Instructor.py`

```python
@instructor_bp.route("/api/instructor/profile", methods=['GET'])
@jwt_required()
def get_instructor_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    instructor = Instructor.query.filter_by(user_id=user_id).first()
    
    # ✅ Lấy full_name từ bảng Users
    full_name = getattr(user, 'full_name', None) or getattr(user, 'FullName', None)
    if not full_name:
        full_name = user.email.split('@')[0]
    
    result = {
        "id": instructor.id,
        "user_id": user.id,
        "username": full_name,
        "email": user.email,
        "full_name": full_name,  # ⭐ Từ bảng Users, không phải Instructors
        "biography": instructor.biography,
        "expertise": instructor.expertise,
        "years_experience": instructor.years_experience,
        "avatar_url": user.avatar_url,
    }
    
    return jsonify(result), 200
```

## Ưu Tiên Hiển Thị Tên

Thứ tự ưu tiên khi lấy tên instructor:

1. **session.user.full_name** (từ localStorage/sessionStorage) ⭐ Ưu tiên cao nhất
2. **session.user.FullName** (fallback cho case sensitivity)
3. **session.user.name** (fallback cũ)
4. **session.user.username** (fallback)
5. **API /api/instructor/profile → full_name** (nếu session không có)
6. **session.user.email.split('@')[0]** (fallback cuối cùng)

## Files Đã Sửa

### ✅ Backend
1. **backend/app/routes/Auth.py**
   - Thêm `"full_name": user.full_name` vào response của `/login` endpoint
   - Line: ~216

### ✅ Frontend  
1. **fe/src/layout/components/Instructor/MenuInstructor.vue**
   - Đã có logic đọc `session.user.full_name` (Line 158)
   - Đã có fallback đến API profile (Line 125-150)
   - Template hiển thị `{{ instructorName }}` (Line 41)

### ✅ Backend API
1. **backend/app/routes/Instructor.py**
   - Endpoint `/api/instructor/profile` đã trả về `full_name` từ `User` table (Line 61-66)

## Cách Test

### 1. Test Login
```bash
# Login với instructor account
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "instructor@example.com", "password": "password"}'

# Response phải có:
{
  "access_token": "...",
  "user": {
    "full_name": "Nguyễn Văn A"  # ✅ Phải có trường này
  }
}
```

### 2. Test Frontend
1. Login vào trang instructor
2. Mở DevTools → Application → Local Storage → Check `codecourse_auth`
3. Verify JSON có `user.full_name`
4. Navbar phải hiển thị tên đầy đủ từ `Users.FullName`

### 3. Test Profile API
```bash
# Get instructor profile
curl -X GET http://localhost:5000/api/instructor/profile \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response phải có:
{
  "full_name": "Nguyễn Văn A",  # ✅ Từ Users.FullName
  "email": "instructor@example.com"
}
```

## Console Logs để Debug

Khi navbar load, bạn sẽ thấy các logs:
```
🚀 MenuInstructor mounted
🔍 MenuInstructor loading user from session: {user: {full_name: "..."}}
✅ Got instructor name from session: Nguyễn Văn A
✅ MenuInstructor initialized
```

Nếu session không có name:
```
🚀 MenuInstructor mounted
🔍 MenuInstructor loading user from session: {user: {}}
📡 No name in session, fetching from backend...
📋 MenuInstructor profile response: {full_name: "..."}
✅ Updated instructorName to: Nguyễn Văn A
```

## Kết Luận

✅ **Tên instructor hiện được lấy từ `Users.FullName`**
- Login response có `user.full_name`
- Session lưu `user.full_name`
- Navbar hiển thị từ session hoặc API
- API profile trả về `full_name` từ `Users` table

✅ **Không lấy từ `Instructors` table**
- Bảng `Instructors` không có trường name
- Chỉ có `expertise`, `biography`, `years_experience`
- Tất cả thông tin cá nhân (name, email, avatar) đều từ `Users`

✅ **Relationship đúng**
```
User (1) ←→ (1) Instructor
  ↑
  └── full_name được lưu ở đây
```

---
**Status**: ✅ HOÀN THÀNH
**Updated**: December 20, 2025
