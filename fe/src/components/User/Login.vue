<template>
  <div class="page-wrapper">
    <!-- Đã xóa thẻ <link> Boxicons khỏi đây để tránh lỗi biên dịch Vue/Vite -->

    <div class="container"> 
      
      <div class="form-box login">
        <form @submit.prevent="login">
          <h1>Login</h1>
          <!-- Trường nhập Email -->
          <div class="input-box">
            <input type="email" placeholder="Email" v-model="email" required>
            <i class='bx bxs-user'></i>
          </div>
          <!-- Trường nhập Password -->
          <div class="input-box">
            <input type="password" placeholder="Password" v-model="password" required>
            <i class='bx bxs-lock-alt'></i>
          </div>

          <!-- Hiển thị thông báo lỗi/thành công -->
          <div v-if="message" :class="{'text-red-500': isError, 'text-green-500': !isError}" class="message-box">
            {{ message }}
          </div>

          <div class="forgot-link">
            <a href="#">Forgot Password?</a>
          </div>
          <button type="submit" class="btn">Login</button>
          <p>or login with social platforms</p>
          <div class="social-icons">
            <a href="#"><i class='bx bxl-google'></i></a>
            <a href="#"><i class='bx bxl-facebook'></i></a>
            <a href="#"><i class='bx bxl-github'></i></a>
            <a href="#"><i class='bx bxl-linkedin'></i></a>
          </div>
        </form>
      </div>

      <div class="toggle-box">
        <div class="toggle-panel toggle-right">
          <h1>Welcome Back!</h1>
          <p>Don't have an account?</p>
          <button class="btn register-btn" @click="goToRegister">Register</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

// Định nghĩa base URL của API
const API_BASE_URL = 'http://localhost:5000';

export default {
  name: 'LoginSignupForm', 
  data() {
    return {
      email: '',
      password: '',
      message: '',
      isError: false,
    };
  },
  methods: {
    async login() {
      this.message = ''; // Xóa thông báo cũ
      this.isError = false;

      // Dữ liệu gửi đi
      const loginData = {
        email: this.email,
        password: this.password
      };

      try {
        const response = await axios.post(`${API_BASE_URL}/login`, loginData);
        
        // --- LOGIC GHI NHỚ VÀ CHUYỂN HƯỚNG THEO ROLE (Đã cập nhật) ---
        if (response.data && response.data.user) {
          const user = response.data.user;
          const role = user.Role; // Lấy vai trò từ phản hồi
          
          // 1. Lưu thông tin người dùng vào localStorage (hoặc Vuex/Pinia)
          localStorage.setItem('user', JSON.stringify(user));
          
          this.message = response.data.message; // "Đăng nhập thành công!"
          
          // 2. Chuyển hướng dựa trên Role
          let targetPath = '/';

          if (role === 'student') {
            targetPath = '/student/dashboard';
          } else if (role === 'instructor') {
            targetPath = '/instructor/dashboard';
          } else {
            console.warn("Vai trò không xác định:", role);
          }
          
          // Thực hiện chuyển hướng
          if (this.$router) {
            console.log(`Đăng nhập thành công, cố gắng chuyển hướng đến: ${targetPath}`);
            // Sử dụng catch để bắt lỗi nếu route không tồn tại (như lỗi bạn đã báo cáo)
            this.$router.push(targetPath).catch(err => {
              // Cảnh báo nếu route không tìm thấy và chuyển hướng về trang gốc (/)
              if (err.name === 'NavigationDuplicated') {
                  // Bỏ qua lỗi NavigationDuplicated (thường xảy ra khi cố gắng điều hướng đến cùng 1 route)
                  return;
              }
              console.warn(`[CẢNH BÁO ROUTE]: Không tìm thấy route "${targetPath}". Vui lòng thêm route này vào file cấu hình Vue Router của bạn.`);
              this.$router.push('/'); // Chuyển hướng dự phòng
            });
          } else {
            console.error("Vue Router không khả dụng. Vui lòng đảm bảo nó đã được khởi tạo.");
          }
        }
        // -----------------------------------------------------------------

      } catch (error) {
        let errorMessage = 'Lỗi kết nối server.';
        
        if (error.response) {
          // Lỗi từ server (401, 400, 409, 500...)
          errorMessage = error.response.data.message || `Lỗi: ${error.response.status}`;
        } else if (error.request) {
          // Lỗi không có phản hồi (mất kết nối)
          errorMessage = 'Không thể kết nối đến Backend Flask (http://localhost:5000).';
        }

        this.message = errorMessage;
        this.isError = true;
        console.error("Lỗi đăng nhập:", error);
      }
    },
    
    goToRegister() {
      if (this.$router) {
        // Tạm thời chuyển hướng đến /register. Lỗi "No match found" cũng có thể xảy ra ở đây.
        this.$router.push('/register').catch(err => {
            if (err.name === 'NavigationDuplicated') {
                return;
            }
            console.warn(`[CẢNH BÁO ROUTE]: Không tìm thấy route "/register". Vui lòng thêm route này.`);
        });
      } else {
        console.error("Vue Router is not available. Please ensure it is initialized.");
      }
    }
  }
};
</script>

<style scoped>
/*
  --- CẬP NHẬT CSS ĐỂ CHỈ HIỂN THỊ FORM LOGIN VÀ PANEL BÊN CẠNH ---
*/

@import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0-800;0,900&display=swap');
/* Thêm Boxicons @import vào đây để thay thế thẻ <link> bị lỗi */
@import url('https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css'); 


* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Poppins", sans-serif;
  text-decoration: none;
  list-style: none;
}

/* Thêm Tailwind-like class cho thông báo lỗi */
.text-red-500 { color: #ef4444; font-weight: 500; }
.text-green-500 { color: #10b981; font-weight: 500; }
.message-box { margin-bottom: 15px; font-size: 14px; }


/* Thay thế body bằng .page-wrapper để căn giữa toàn bộ nội dung */
.page-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(90deg, #e2e2e2, #c9d6ff);
}

.container {
  position: relative;
  width: 850px;
  height: 550px;
  background: #fff;
  margin: 20px;
  border-radius: 30px;
  box-shadow: 0 0 30px rgba(0, 0, 0, .2);
  overflow: hidden;
  /* Đã bỏ transition của .container active */
}

.container h1 {
  font-size: 36px;
  margin: -10px 0;
}

.container p {
  font-size: 14.5px;
  margin: 15px 0;
}

form {
  width: 100%;
}

.form-box {
  position: absolute;
  /* Đặt form Login luôn ở bên trái */
  left: 0; 
  width: 50%;
  height: 100%;
  background: #fff;
  display: flex;
  flex-direction: column; /* Thêm để căn giữa form-box */
  justify-content: center; /* Căn giữa theo chiều dọc */
  align-items: center;
  color: #333;
  text-align: center;
  padding: 40px;
  z-index: 1;
  /* Bỏ transition và chỉ để lại các rule cơ bản */
}

/* Xóa các rule .container.active .form-box, .form-box.register, .container.active .form-box.register */

.input-box {
  position: relative;
  margin: 30px 0;
  width: 100%; /* Đảm bảo input-box chiếm toàn bộ chiều rộng form */
}

.input-box input {
  width: 100%;
  padding: 13px 50px 13px 20px;
  background: #eee;
  border-radius: 8px;
  border: none;
  outline: none;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.input-box input::placeholder {
  color: #888;
  font-weight: 400;
}

.input-box i {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
}

.forgot-link {
  margin: -15px 0 15px;
  width: 100%; /* Căn chỉnh */
  text-align: right;
}

.forgot-link a {
  font-size: 14.5px;
  color: #333;
}

.btn {
  width: 100%;
  height: 48px;
  background: #7494ec;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, .1);
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #fff;
  font-weight: 600;
  transition: background 0.3s;
}

.btn:hover {
  background: #5a7cce;
}

.social-icons {
  display: flex;
  justify-content: center;
}

.social-icons a {
  display: inline-flex;
  padding: 10px;
  border: 2px solid #ccc;
  border-radius: 8px;
  font-size: 24px;
  color: #333;
  margin: 0 8px;
  transition: all 0.3s;
}

.social-icons a:hover {
  background: #f0f0f0;
  border-color: #7494ec;
}

.toggle-box {
  position: absolute;
  width: 100%;
  height: 100%;
}

.toggle-box::before {
  content: '';
  position: absolute;
  /* Giữ panel ở bên phải */
  left: 50%; 
  width: 50%; /* Chỉ bao phủ panel bên phải */
  height: 100%;
  background: #7494ec;
  border-radius: 0 30px 30px 0; /* Bo góc chỉ ở bên phải */
  z-index: 2;
  /* Xóa transition của left */
}

/* Xóa .container.active .toggle-box::before */

.toggle-panel {
  position: absolute;
  width: 50%;
  height: 100%;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 2;
  /* Xóa transition */
}

/* Xóa .toggle-panel.toggle-left và các rule liên quan đến active */

.toggle-panel.toggle-right {
  right: 0;
  /* Xóa transition-delay */
}

/* Xóa .container.active .toggle-panel.toggle-right */

.toggle-panel p {
  margin-bottom: 20px;
}

.toggle-panel .btn {
  width: 160px;
  height: 46px;
  background: transparent;
  border: 2px solid #fff;
  box-shadow: none;
  transition: background 0.3s, color 0.3s;
}

.toggle-panel .btn:hover {
  background: #fff;
  color: #7494ec;
}

/* --- CẬP NHẬT MEDIA QUERIES cho mobile --- */

@media screen and (max-width: 650px) {
  .container {
    width: 90%;
    height: 600px;
  }

  .form-box {
    top: 30%; /* Đặt Login form ở phía dưới */
    width: 100%;
    height: 70%;
    left: 0; /* Luôn ở 0 */
  }

  /* Xóa các rule active */

  .toggle-box::before {
    top: 0; /* Đặt gradient ở phía trên */
    left: 0; 
    width: 100%;
    height: 30%;
    border-radius: 30px 30px 0 0; /* Bo góc trên */
  }

  /* Xóa .container.active .toggle-box::before */

  .toggle-panel {
    width: 100%;
    height: 30%;
  }

  /* Xóa .container.active .toggle-panel.toggle-left */

  .toggle-panel.toggle-right {
    right: 0;
    top: 0;
    /* Bỏ bottom: -30% */
  }

  /* Xóa .container.active .toggle-panel.toggle-right */
}

@media screen and (max-width: 400px) {
  .form-box {
    padding: 20px;
  }

  .toggle-panel h1 {
    font-size: 30px;
  }
}
</style>
