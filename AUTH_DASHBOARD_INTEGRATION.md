# Hướng Dẫn Tích Hợp Auth với Dashboard

## Cập Nhật Auth Component

Khi người dùng đăng nhập thành công, hãy lưu instructor ID:

```vue
<!-- Auth.vue hoặc Login.vue -->
<script>
export default {
  methods: {
    async handleLogin() {
      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          // Lưu token
          localStorage.setItem('authToken', data.token)
          
          // Lưu instructor ID
          if (data.user.role === 'instructor' && data.user.instructorId) {
            localStorage.setItem('instructorId', data.user.instructorId)
          }
          
          // Lưu user info
          localStorage.setItem('userInfo', JSON.stringify(data.user))
          
          // Redirect tới dashboard
          this.$router.push('/instructor/dashboard')
        }
      } catch (error) {
        console.error('Login error:', error)
      }
    }
  }
}
</script>
```

## Backend Auth Response

Backend cần trả về user object có instructor ID:

```python
# auth/Instructor.py hoặc tương đương
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # ... validate email/password ...
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.role == 'instructor':
        instructor = Instructor.query.filter_by(user_id=user.id).first()
        
        response = {
            'token': generate_token(user.id),
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.full_name,
                'role': user.role,
                'instructorId': instructor.id if instructor else None,
                'avatar': user.avatar_url
            }
        }
        
        return jsonify(response), 200
```

## Update Backend Auth Endpoint

Hãy đảm bảo trả về instructorId trong response:

```python
from app.models.model import User, Instructor

# ... trong login route ...

if user and verify_password(data['password'], user.password_hash):
    # Lấy instructor info
    instructor = Instructor.query.filter_by(user_id=user.id).first()
    
    return jsonify({
        'success': True,
        'token': jwt_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'fullName': user.full_name,
            'role': user.role,
            'instructorId': instructor.id if instructor else None,
            'avatar': user.avatar_url
        }
    }), 200
```

## Logout Handler

Xóa instructor ID khi logout:

```javascript
// Store.js hoặc logout method
logout() {
  localStorage.removeItem('authToken')
  localStorage.removeItem('instructorId')
  localStorage.removeItem('userInfo')
  sessionStorage.removeItem('instructorId')
  
  this.$router.push('/login')
}
```

## Route Guards

Thêm guards để bảo vệ dashboard:

```javascript
// router/index.js

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('authToken')
  const instructorId = localStorage.getItem('instructorId')
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  
  // Nếu truy cập dashboard nhưng chưa login
  if (to.path.includes('/instructor') && !token) {
    next('/login')
    return
  }
  
  // Nếu truy cập dashboard nhưng không phải instructor
  if (to.path.includes('/instructor') && userInfo.role !== 'instructor') {
    next('/student/dashboard')
    return
  }
  
  next()
})
```

## Session Management

Quản lý session timeout:

```javascript
// Trong App.vue hoặc main.js

const SESSION_TIMEOUT = 30 * 60 * 1000 // 30 phút
let timeoutId

function resetSessionTimer() {
  if (timeoutId) clearTimeout(timeoutId)
  
  timeoutId = setTimeout(() => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('instructorId')
    localStorage.removeItem('userInfo')
    
    alert('Session hết hạn. Vui lòng đăng nhập lại.')
    router.push('/login')
  }, SESSION_TIMEOUT)
}

// Reset khi có hoạt động
document.addEventListener('mousedown', resetSessionTimer)
document.addEventListener('keydown', resetSessionTimer)

export { resetSessionTimer }
```

## Test Integration

### Test 1: Login và Load Dashboard
```bash
# 1. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"instructor@example.com","password":"password123"}'

# Response nên có instructorId
# {
#   "token": "...",
#   "user": {
#     "instructorId": 1,
#     ...
#   }
# }

# 2. Sử dụng instructorId để load dashboard
curl "http://localhost:5000/api/instructor/dashboard?instructor_id=1"
```

### Test 2: Invalid Instructor ID
```bash
curl "http://localhost:5000/api/instructor/dashboard?instructor_id=999"

# Response: 404 - Giảng viên không tồn tại
```

## Cấu Hình Environment

Thêm vào `.env`:

```env
# Backend
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DATABASE_URL=mysql://user:password@localhost/codecourse_db

# Auth
JWT_SECRET=your_secret_key
JWT_EXPIRATION_HOURS=24

# Frontend
VITE_API_BASE_URL=http://localhost:5000
```

## File Cần Cập Nhật

1. **Auth.vue** - Thêm lưu instructorId khi login
2. **Auth.py** (Backend) - Return instructorId trong response
3. **Router/index.js** - Thêm guards cho instructor routes
4. **App.vue** - Session timeout handler

## Checklist

- [ ] Auth component lưu instructorId
- [ ] Backend API trả về instructorId
- [ ] Route guards được thêm vào
- [ ] Session timeout được xử lý
- [ ] Logout xóa instructorId
- [ ] Dashboard load dữ liệu thành công
- [ ] Test login -> dashboard flow
- [ ] Test logout -> remove data

## Troubleshooting

### Dashboard trống sau khi login
- [ ] Kiểm tra instructorId được lưu trong localStorage
- [ ] Kiểm tra API dashboard trả về dữ liệu
- [ ] Kiểm trace console.log để debug

### Session expire quá nhanh
- [ ] Tăng SESSION_TIMEOUT
- [ ] Kiểm tra server JWT expiration

### 404 khi load dashboard
- [ ] Xác minh instructorId đúng
- [ ] Kiểm tra DB có giảng viên với ID đó
- [ ] Kiểm tra database connection
