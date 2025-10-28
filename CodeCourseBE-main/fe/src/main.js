import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import Admin from "./layout/wrapper/Admin/index.vue";
import Instructor from "./layout/wrapper/Instructor/index.vue";
import Student from "./layout/wrapper/Student/index.vue";
import User from "./layout/wrapper/User/index.vue";
const app = createApp(App);

app.use(router);
app.component("Admin-layout", Admin);
app.component("instructor-layout", Instructor);
app.component("student-layout", Student);
app.component("user-layout", User);

app.mount("#app");
