import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

/* ==================================== */
/* 1. IMPORT FONT AWESOME CORE COMPONENTS */
/* Lỗi ban đầu: thiếu 2 dòng import này */
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
/* ==================================== */

// Import các layout components
import Admin from "./layout/wrapper/Admin/index.vue";
import Instructor from "./layout/wrapper/Instructor/index.vue";
import Student from "./layout/wrapper/Student/index.vue";
import User from "./layout/wrapper/User/index.vue";

// Import icon Home
import { faBell, faBook, faChalkboardTeacher, faChartLine, faGamepad, faHouse, faMessage, faProjectDiagram, faRobot, faUser, faUserGraduate } from '@fortawesome/free-solid-svg-icons' 

// Thêm icon vào thư viện (để có thể sử dụng)
library.add(faHouse)
library.add(faBook)
library.add(faGamepad)
library.add(faMessage)
library.add(faUser)
library.add(faRobot)
library.add(faBell)
library.add(faChartLine)
library.add(faUserGraduate)
library.add(faChalkboardTeacher)
library.add(faProjectDiagram)

// Tạo instance app
const app = createApp(App);

// 2. Đăng ký component Font Awesome TOÀN CỤC
app.component('font-awesome-icon', FontAwesomeIcon);

// 3. Sử dụng Router
app.use(router);

// 4. Đăng ký các Layout Components
app.component("Admin-layout", Admin);
app.component("instructor-layout", Instructor);
app.component("student-layout", Student);
app.component("user-layout", User);

// 5. Gắn app vào DOM
app.mount("#app");
