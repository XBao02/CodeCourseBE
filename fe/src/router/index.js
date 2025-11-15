import { createRouter, createWebHistory } from "vue-router"; // cài vue-router: npm install vue-router@next --save

const routes = [
  // ------------------ User ------------------
  {
    path: "/",
    component: () => import("../layout/wrapper/User/index.vue"),
    children: [
      {
        path: "",
        component: () => import("../layout/components/User/MenuUser.vue"),
      },
    ],
  },
  {
    path: "/login",
    component: () => import("../components/User/Login.vue"),
  },
  {
    path: "/register",
    component: () => import("../components/User/Register.vue"),
  },
  {
    path: "/profile",
    name: "UserProfile",
    component: () => import("../components/User/Profile.vue"),
  },
  {
    path: "/settings",
    name: "UserSettings",
    component: () => import("../components/User/Settings.vue"),
  },

  // ------------------ ADMIN ------------------
  {
    path: "/admin",
    component: () => import("../layout/wrapper/Admin/index.vue"),
    children: [
      {
        path: "",
        name: "AdminDashboard",
        component: () => import("../components/Admin/Dashboard.vue"), // Dashboard Admin
      },
      {
        path: "courses",
        name: "AdminCourses",
        component: () => import("../components/Admin/Courses.vue"),
      },
      {
        path: "instructors_manager",
        component: () => import("../components/Admin/Accounts_Instructor.vue"),
      },
      {
        path: "students_manager",
        component: () => import("../components/Admin/Accounts.vue"),
      },
      {
        path: "reports",
        name: "AdminReports",
        component: () => import("../components/Admin/Reports.vue"),
      },
      {
        path: "assistant",
        name: "AdminAssistant",
        component: () => import("../components/User/Assistant.vue"),
      },
      {
        path: "decentralization",
        name: "AdminDecentralization",
        component: () => import("../components/Admin/Decentralization.vue"),
      },
    ],
  },

  // ------------------ STUDENT ------------------
  {
    path: "/student",
    component: () => import("../layout/wrapper/Student/index.vue"),
    children: [
      {
        path: "",
        name: "StudentDashboard",
        component: () => import("../components/Student/Dashboard.vue"), // Dashboard Student
      },
      {
        path: "courses",
        name: "StudentCourses",
        component: () => import("../components/Student/Courses.vue"),
      },
      {
        path: "course/:courseId",
        name: "StudentCourseLesson",
        component: () =>
          import("../components/Student/Course_Section_Lesson.vue"),
      },
      {
        path: "minigames",
        name: "StudentMinigames",
        component: () => import("../components/Student/Minigames.vue"),
      },
      {
        path: "chat",
        name: "StudentChat",
        component: () => import("../components/Student/Chat.vue"),
      },
      {
        path: "profile",
        name: "StudentProfile",
        component: () => import("../components/Student/Profile.vue"),
      },
      {
        path: "assistant",
        name: "StudentAssistant",
        component: () => import("../components/User/Assistant.vue"),
      },
    ],
  },

  // ------------------ INSTRUCTOR ------------------
  {
    path: "/instructor",
    component: () => import("../layout/wrapper/Instructor/index.vue"),
    children: [
      {
        path: "",
        name: "InstructorDashboard",
        component: () => import("../components/Instructor/Dashboard.vue"), // Dashboard Instructor
      },
      {
        path: "courses",
        name: "InstructorCourses",
        component: () => import("../components/Instructor/Courses.vue"),
      },
      {
        path: "courses/:id",
        name: "InstructorCourseDetail",
        component: () => import("../components/Instructor/CourseDetail.vue"),
      },
      {
        path: "courses/:id/edit",
        name: "InstructorCourseEdit",
        component: () => import("../components/Instructor/CourseEdit.vue"),
      },
      {
        path: "courses/:id/lessons",
        name: "InstructorCourseLessons",
        component: () => import("../components/Instructor/CourseLessons.vue"),
      },
      {
        path: "courses/:id/students",
        name: "InstructorCourseStudents",
        component: () => import("../components/Instructor/CourseStudents.vue"),
      },
      {
        path: "tests/:id/edit",
        name: "InstructorTestEdit",
        component: () => import("../components/Instructor/TestEditor.vue"),
        props: true,
      },
      {
        path: "chat",
        name: "InstructorChat",
        component: () => import("../components/Instructor/Chat.vue"),
      },
      {
        path: "assistant",
        name: "InstructorAssistant",
        component: () => import("../components/User/Assistant.vue"),
      },
      {
        path: "reports",
        name: "InstructorReports",
        component: () => import("../components/Instructor/Reports.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
