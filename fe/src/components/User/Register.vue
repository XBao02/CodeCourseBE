<template>
  <div class="page-wrapper">
    <!-- Di chuyển @import link Boxicons vào <style> -->

    <div class="container"> 
      
      <!-- FORM ĐĂNG KÝ (Ở BÊN PHẢI) -->
      <div class="form-box register">
        <form @submit.prevent="register">
          <h1>Registration</h1>
          
          <!-- Full Name Input -->
          <div class="input-box">
            <input type="text" placeholder="Full Name" v-model="fullName" required>
            <i class='bx bxs-id-card'></i>
          </div>

          <!-- Email Input -->
          <div class="input-box">
            <input type="email" placeholder="Email" v-model="email" required>
            <i class='bx bxs-envelope'></i>
          </div>
          
          <!-- Password Input -->
          <div class="input-box">
            <input type="password" placeholder="Password" v-model="password" required>
            <i class='bx bxs-lock-alt'></i>
          </div>

          <!-- Role Selection (Radio Buttons) -->
          <div class="role-selection">
            <label>Register as:</label>
            <div class="radio-group">
              <label>
                <input type="radio" value="student" v-model="role" required> Student
              </label>
              <label>
                <input type="radio" value="instructor" v-model="role"> Instructor
              </label>
            </div>
          </div>
          
          <!-- Message Display Area -->
          <div v-if="message.text" :class="['api-message', message.type]">
            {{ message.text }}
          </div>

          <button type="submit" class="btn" :disabled="isLoading">
              <span v-if="isLoading">Đang đăng ký...</span>
              <span v-else>Register</span>
          </button>
          
          <p>or register with social platforms</p>
          <div class="social-icons">
            <a href="#"><i class='bx bxl-google'></i></a>
            <a href="#"><i class='bx bxl-facebook'></i></a>
            <a href="#"><i class='bx bxl-github'></i></a>
            <a href="#"><i class='bx bxl-linkedin'></i></a>
          </div>
        </form>
      </div>

      <!-- TOGGLE PANEL (Ở BÊN TRÁI) -->
      <div class="toggle-box">
        <div class="toggle-panel toggle-left">
          <h1>Hello, Welcome!</h1>
          <p>Already have an account?</p>
          
          <!-- NÚT CHUYỂN HƯỚNG VỀ LOGIN -->
          <button class="btn login-btn" @click="goToLogin">Login</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Không cần import axios nếu dùng fetch API
export default {
  name: 'RegisterForm', 
  data() {
    return {
      fullName: '', // Khớp với template
      email: '',
      password: '',
      role: 'student', // Mặc định là student
      isLoading: false,
      message: { text: '', type: '' }
    };
  },
  methods: {
    // Phương thức xử lý đăng ký (Asynchronous)
    async register() {
      this.isLoading = true;
      this.message = { text: '', type: '' }; // Xóa thông báo cũ

      // Dùng tên biến 'username' nếu backend Flask yêu cầu, nếu không hãy dùng 'fullName'
      const url = 'http://localhost:5000/register'; 
      
      try {
        // Thực hiện fetch (sử dụng fetch như trong file Register.vue gốc của bạn)
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            // Giả sử backend Flask chấp nhận cả fullName, email, password, và role
            fullName: this.fullName,
            email: this.email,
            password: this.password,
            role: this.role
          })
        });

        const data = await response.json();

        if (response.ok) { 
          // Đăng ký thành công
          const userRole = data.user?.Role || this.role; // Lấy role từ response hoặc từ v-model
          // Cập nhật thông báo chuyển hướng về trang đăng nhập
          this.message = { text: `Đăng ký tài khoản ${userRole} thành công! Vui lòng đăng nhập.`, type: 'success' };
          
          // Không lưu thông tin vào localStorage ở đây nữa nếu chuyển hướng về login
          // (Chức năng lưu localStorage thường được thực hiện trong hàm đăng nhập)
          if (data.user) {
              // Vẫn giữ việc lưu dữ liệu, nhưng logic đăng nhập mới sử dụng nó.
              localStorage.setItem('user', JSON.stringify(data.user)); 
          }

          // Chuyển hướng sau 1.5 giây
          setTimeout(() => {
            // Luôn chuyển hướng đến trang Đăng nhập
            this.goToLogin();
          }, 1500);

        } else {
          // Xử lý lỗi từ server
          this.message = { text: data.message || 'Đăng ký thất bại. Vui lòng thử lại.', type: 'error' };
        }
      } catch (error) {
        // Xử lý lỗi mạng hoặc lỗi không kết nối được
        console.error('Lỗi mạng/Kết nối:', error);
        this.message = { text: 'Lỗi kết nối server. Vui lòng đảm bảo Backend Flask đang chạy tại http://localhost:5000.', type: 'error' };
      } finally {
        this.isLoading = false;
      }
    },

    // Phương thức để chuyển hướng đến trang đăng nhập
    goToLogin() {
      if (this.$router) {
        this.$router.push('/login'); 
      } else {
        console.warn("Vue Router không khả dụng. Bạn cần định nghĩa router để chuyển hướng.");
      }
    }
  }
};
</script>

<style scoped>
/* Di chuyển link Boxicons vào style */
@import url('https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css');
@import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Poppins", sans-serif;
  text-decoration: none;
  list-style: none;
}

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

/* --- CẬP NHẬT CSS CHO REGISTER LAYOUT ---
*/

.form-box {
  position: absolute;
  /* Đặt form Register ở bên phải */
  left: 50%; 
  width: 50%;
  height: 100%;
  background: #fff;
  display: flex;
  flex-direction: column; 
  justify-content: center; 
  align-items: center;
  color: #333;
  text-align: center;
  padding: 40px;
  z-index: 1;
}

.input-box {
  position: relative;
  margin: 15px 0; /* Giảm margin để nhét thêm input */
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
  transition: all 0.3s ease;
}

.input-box input:focus {
    box-shadow: 0 0 5px rgba(116, 148, 236, 0.5);
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
  margin-top: 10px;
  transition: all 0.3s ease;
}

/* Style cho button bị disable */
.btn:disabled {
    background: #aab8d8; 
    cursor: not-allowed;
    opacity: 0.8;
}

.btn:hover:not(:disabled) {
    background: #5c7ac2;
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
  transition: all 0.3s ease;
}
.social-icons a:hover {
    border-color: #7494ec;
    color: #7494ec;
}

/* Role Selection Styling */
.role-selection {
    width: 100%;
    text-align: left;
    margin: 15px 0;
    color: #333;
}
.role-selection label {
    font-size: 15px;
    font-weight: 500;
    margin-bottom: 5px;
    display: block;
}
.radio-group {
    display: flex;
    gap: 20px;
    margin-top: 5px;
}
.radio-group label {
    display: flex;
    align-items: center;
    font-weight: 400;
    cursor: pointer;
}
.radio-group input[type="radio"] {
    margin-right: 5px;
    width: auto;
}

/* Style cho thông báo API */
.api-message {
    padding: 10px;
    margin-top: 5px;
    margin-bottom: 10px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    width: 100%;
    text-align: center;
}

.api-message.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.api-message.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}


.toggle-box {
  position: absolute;
  width: 100%;
  height: 100%;
}

.toggle-box::before {
  content: '';
  position: absolute;
  /* Đặt panel màu xanh ở bên trái */
  left: 0; 
  width: 50%; /* Chỉ bao phủ panel bên trái */
  height: 100%;
  background: #7494ec;
  border-radius: 30px 0 0 30px; /* Bo góc chỉ ở bên trái */
  z-index: 2;
}

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
}

.toggle-panel.toggle-left {
  left: 0; /* Đặt panel chữ ở bên trái */
}

.toggle-panel p {
  margin-bottom: 20px;
}

.toggle-panel .btn {
  width: 160px;
  height: 46px;
  background: transparent;
  border: 2px solid #fff;
  box-shadow: none;
  transition: all 0.3s ease;
}

.toggle-panel .btn:hover {
    background: #fff;
    color: #7494ec;
}


/* --- CẬP NHẬT MEDIA QUERIES cho mobile (Đảo ngược vị trí) --- */

@media screen and (max-width: 650px) {
  .container {
    height: calc(100vh - 40px);
  }

  .form-box {
    /* Đặt Register form ở phía dưới */
    top: 30%; 
    left: 0; /* Chiếm toàn bộ chiều ngang */
    width: 100%;
    height: 70%;
  }

  .toggle-box::before {
    /* Đặt gradient ở phía trên */
    top: 0; 
    left: 0; 
    width: 100%;
    height: 30%;
    border-radius: 30px 30px 0 0; /* Bo góc trên */
  }

  .toggle-panel {
    width: 100%;
    height: 30%;
  }

  .toggle-panel.toggle-left {
    left: 0; /* Đặt panel chữ ở phía trên */
    top: 0;
  }
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
