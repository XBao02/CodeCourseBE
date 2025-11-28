<template>
  <div class="home-page">
    <nav class="navbar navbar-expand-lg navbar-light bg-white py-3 fixed-top shadow-sm">
      <div class="container">
        <router-link to="/" class="navbar-brand fw-bold fs-3">
          <span class="text-gradient-primary">Code</span><span class="text-gradient-success">Course</span>
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav mx-auto">
            <li class="nav-item mx-2">
              <a class="nav-link fw-medium text-dark" href="#">Home</a>
            </li>
            <li class="nav-item mx-2">
              <a class="nav-link fw-medium text-dark" href="#courses">Courses</a>
            </li>
            <li class="nav-item mx-2">
              <a class="nav-link fw-medium text-dark" href="#instructors">Instructors</a>
            </li>
            <li class="nav-item mx-2">
              <a class="nav-link fw-medium text-dark" href="#students">Students</a>
            </li>
            <li class="nav-item mx-2">
              <a class="nav-link fw-medium text-dark" href="#contact">Contact</a>
            </li>
          </ul>
          
          <div class="d-flex flex-wrap gap-2 align-items-center justify-content-lg-end justify-content-center">
            <router-link to="/student" class="btn btn-outline-secondary px-3">
              Student Demo
            </router-link>
            <router-link to="/instructor" class="btn btn-outline-secondary px-3">
              Instructor Demo
            </router-link>
            <router-link to="/admin" class="btn btn-outline-secondary px-3">
              Admin Demo
            </router-link>
            <router-link to="/login" class="btn btn-outline-primary px-3">
              Sign In
            </router-link>
            <router-link to="/register" class="btn btn-primary px-4">
              Enroll
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <section class="hero-section py-5 mt-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <div class="hero-content">
              <h1 class="display-5 fw-bold mb-4 hero-title">
                Learn Programming Online
              </h1>
              
              <p class="lead text-muted mb-5">
                Online courses with expert instructors, updated content, and effective learning methods. 
                Start your coding journey today!
              </p>

              <div class="hero-actions d-flex flex-wrap gap-3 align-items-center mb-4">
                <router-link to="/courses" class="btn btn-primary btn-lg px-4 py-2 fw-semibold">
                  Get Started
                </router-link>
                
                <a href="#about" class="btn btn-outline-dark btn-lg px-4 py-2 fw-semibold">
                  Learn More
                </a>
              </div>

              <div class="stats d-flex align-items-center">
                <div class="stat-badge text-white rounded-pill px-3 py-2">
                  <span class="fw-bold">2,000+</span>
                  <span class="ms-1">Students</span>
                </div>
                <small class="text-muted ms-2">have joined our courses</small>
              </div>
            </div>
          </div>

          <div class="col-lg-6">
            <div class="code-example-card mt-5 mt-lg-0">
              <div class="card">
                <div class="card-header py-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="fw-medium">learnToCode.js</span>
                    <div class="code-actions">
                      <span class="dot bg-danger me-1"></span>
                      <span class="dot bg-warning me-1"></span>
                      <span class="dot bg-success"></span>
                    </div>
                  </div>
                </div>
                
                <div class="card-body p-4">
                  <pre class="mb-0"><code class="language-javascript">function learnToCode() {
  const skills = []
  const dedication = 100;
  let success = false;

  while (dedication > 0) {
    skills.push("New knowledge");
    if (skills.length > 50) {
      success = true;
      break;
    }
  }

  return {
    success,
    skills,
    message: "You are now a developer!"
  }
}</code></pre>
                </div>
              </div>

              <div class="feature-badge mt-4 p-3 bg-white rounded">
                <div class="d-flex align-items-center">
                  <div class="bg-gradient-primary rounded p-2 me-3">
                    <i class="bi bi-check-circle text-white"></i>
                  </div>
                  <div>
                    <h6 class="fw-bold mb-1 text-dark">Start from Basics</h6>
                    <p class="text-muted mb-0 small">Suitable for all levels</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="about" class="py-5 bg-light">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-bold mb-3 section-title">Why choose CodeCourse?</h2>
          <p class="text-muted lead fs-4">
            We provide a comprehensive learning platform to help you develop programming skills from beginner to advanced.
          </p>
        </div>

        <div class="row g-4">
          <div class="col-md-6 col-lg-4" v-for="(reason, index) in reasons" :key="index">
            <div class="reason-card h-100 p-4 bg-white rounded">
              <div class="reason-icon mb-3">
                <div class="icon-wrapper rounded-circle d-inline-flex align-items-center justify-content-center">
                  <img v-if="reason.iconSrc" :src="reason.iconSrc" :alt="reason.title" class="icon-img" />
                  <i v-else :class="reason.iconClass" class="fallback-icon"></i>
                </div>
              </div>
              <h5 class="fw-bold mb-3 text-dark">{{ reason.title }}</h5>
              <p class="text-muted mb-0">{{ reason.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="courses" class="py-5">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-bold mb-3 section-title">Featured Courses</h2>
          <p class="text-muted lead fs-4">
            Courses designed by top industry experts.
          </p>
        </div>

        <div class="row g-4">
          <div class="col-md-6 col-lg-4" v-for="(course, index) in featuredCourses" :key="index">
            <div class="course-card card h-100">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <span class="badge bg-primary bg-opacity-10 text-primary border-0 fw-semibold">{{ course.level }}</span>
                  <div class="rating text-warning">
                    <i class="bi bi-star-fill"></i>
                    <span class="ms-1 text-dark fw-semibold">{{ course.rating }}</span>
                  </div>
                </div>
                
                <h5 class="fw-bold mb-2 text-dark">{{ course.title }}</h5>
                <p class="text-muted small mb-3">{{ course.description }}</p>
                
                <div class="course-meta d-flex justify-content-between align-items-center mb-3">
                  <span class="text-muted small">
                    <i class="bi bi-people me-1"></i>
                    {{ course.students }} students
                  </span>
                </div>

                <div class="course-details border-top pt-3">
                  <div class="row text-center">
                    <div class="col-4">
                      <small class="text-muted d-block">{{ course.duration }}</small>
                      <small class="fw-semibold text-dark">Weeks</small>
                    </div>
                    <div class="col-4">
                      <small class="text-muted d-block">{{ course.lessons }}</small>
                      <small class="fw-semibold text-dark">Lessons</small>
                    </div>
                    <div class="col-4">
                      <small class="text-muted d-block">{{ course.hours }}</small>
                      <small class="fw-semibold text-dark">Hours</small>
                    </div>
                  </div>
                </div>

                <router-link to="/course-details" class="btn btn-outline-primary w-100 mt-3 fw-semibold">
                  Details
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <div class="text-center mt-5">
          <router-link to="/courses" class="btn btn-primary px-4 me-3 fw-semibold">
            Enroll
          </router-link>
          <router-link to="/courses" class="btn btn-outline-dark px-4 fw-semibold">
            View all courses 
          </router-link>
        </div>
      </div>
    </section>

    <section id="testimonials" class="py-5 bg-white">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-bold mb-3 section-title">What students say about us</h2>
          <p class="text-muted lead fs-4">
            Discover learning experiences from students who have joined CodeCourse.
          </p>
        </div>

        <div class="row g-4 justify-content-center">
          <div class="col-md-6 col-lg-4" v-for="(testimonial, index) in testimonials" :key="testimonial.name">
            <div class="testimonial-card card" :style="{ animationDelay: (index * 0.2) + 's' }">
              <div class="card-body p-5">
                <div class="text-center mb-4">
                  <div class="avatar mx-auto mb-3 d-flex align-items-center justify-content-center" :style="{ background: testimonial.gradient }">
                    <span class="avatar-initial">{{ testimonial.initials }}</span>
                  </div>
                  <h5 class="fw-bold mb-1 text-dark">{{ testimonial.name }}</h5>
                  <p class="text-muted mb-0">{{ testimonial.role }}</p>
                </div>
                <p class="lead text-center text-muted fst-italic">
                  "{{ testimonial.quote }}"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="demo-section py-4 text-white">
      <div class="container">
        <div class="text-center">
          <span class="me-3 fw-semibold">Quick Demo:</span>
          <router-link to="/student" class="text-white text-decoration-underline me-3 fw-semibold">Student</router-link>
          <router-link to="/instructor" class="text-white text-decoration-underline me-3 fw-semibold">Instructor</router-link>
          <router-link to="/admin" class="text-white text-decoration-underline fw-semibold">Admin</router-link>
        </div>
      </div>
    </section>

    <footer class="text-white py-5">
      <div class="container">
        <div class="row">
          <div class="col-lg-4 mb-4">
            <h5 class="fw-bold mb-3">
              <span class="text-primary">Code</span><span class="text-success">Course</span>
            </h5>
            <p class="text-light mb-4">
              Leading online programming platform with high-quality courses, experienced instructors, and a vibrant learner community.
            </p>
            <div class="contact-info">
              <p class="mb-2">
                <i class="bi bi-envelope me-2 text-primary"></i>Email: support@codecourse.dev
              </p>
              <p class="mb-2">
                <i class="bi bi-phone me-2 text-primary"></i>+84 123 456 789
              </p>
              <p class="mb-0">
                <i class="bi bi-geo-alt me-2 text-primary"></i>12th Ward, District 4, Ho Chi Minh City
              </p>
            </div>
          </div>

          <div class="col-lg-2 col-md-3 mb-4">
            <h6 class="fw-bold mb-3 text-light">Company</h6>
            <ul class="list-unstyled">
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">About Us</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Instructors</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Careers</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Partners</a></li>
            </ul>
          </div>

          <div class="col-lg-2 col-md-3 mb-4">
            <h6 class="fw-bold mb-3 text-light">Courses</h6>
            <ul class="list-unstyled">
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Web Development</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">React & Redux</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Node.js & Express</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Full-Stack Developer</a></li>
            </ul>
          </div>

          <div class="col-lg-2 col-md-3 mb-4">
            <h6 class="fw-bold mb-3 text-light">Resources</h6>
            <ul class="list-unstyled">
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Blog</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Docs</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Community</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">FAQ</a></li>
            </ul>
          </div>

          <div class="col-lg-2 col-md-3 mb-4">
            <h6 class="fw-bold mb-3 text-light">Legal</h6>
            <ul class="list-unstyled">
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Terms of Use</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Privacy Policy</a></li>
              <li class="mb-2"><a href="#" class="text-light text-decoration-none opacity-75 hover-opacity-100">Cookie Policy</a></li>
            </ul>
          </div>
        </div>

        <div class="border-top border-secondary pt-4 mt-4 text-center">
          <p class="text-light mb-0 opacity-75">© 2025 CodeCourse. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import reasonCode from '@/assets/images/reason-code.svg';
import reasonLaptop from '@/assets/images/reason-laptop.svg';
import reasonCommunity from '@/assets/images/reason-community.svg';
import reasonBook from '@/assets/images/reason-book.svg';
import reasonAward from '@/assets/images/reason-award.svg';
import reasonSupport from '@/assets/images/reason-support.svg';

export default {
  name: "HomePage",
  data() {
    return {
      reasons: [
        {
          iconSrc: reasonCode,
          iconClass: 'bi bi-briefcase-fill',
          title: "Practical programming",
          description: "Hands-on projects help learners apply knowledge immediately in real work."
        },
        {
          iconSrc: reasonLaptop,
          iconClass: 'bi bi-laptop',
          title: "Learn anytime, anywhere",
          description: "Online platform lets you learn anytime and anywhere on your own schedule."
        },
        {
          iconSrc: reasonCommunity,
          iconClass: 'bi bi-people-fill',
          title: "Supportive community",
          description: "Join a vibrant community of learners to solve problems and grow together."
        },
        {
          iconSrc: reasonBook,
          iconClass: 'bi bi-journal-code',
          title: "Updated materials",
          description: "Course content is regularly updated with the latest technologies and trends."
        },
        {
          iconSrc: reasonAward,
          iconClass: 'bi bi-award-fill',
          title: "Recognized certificates",
          description: "Receive certificates upon completion to strengthen your resume."
        },
        {
          iconSrc: reasonSupport,
          iconClass: 'bi bi-headset',
          title: "24/7 support",
          description: "Our support team is always ready to answer any questions during learning."
        }
      ],
      featuredCourses: [
        {
          level: "Beginner",
          rating: "4.9",
          title: "Basic Web Development",
          description: "Learn HTML, CSS, and JavaScript from scratch. Build modern websites...",
          students: "1245",
          duration: "10",
          lessons: "45",
          hours: "30"
        },
        {
          level: "Intermediate",
          rating: "4.8",
          title: "React & Redux Mastery",
          description: "Master React, Redux and build high-performance modern web apps...",
          students: "985",
          duration: "12",
          lessons: "52",
          hours: "40"
        },
        {
          level: "Intermediate",
          rating: "4.7",
          title: "Node.js & Express Backend",
          description: "Build robust backends with Node.js, Express and MongoDB. RESTful APIs...",
          students: "856",
          duration: "14",
          lessons: "48",
          hours: "35"
        },
        {
          level: "Advanced",
          rating: "4.9",
          title: "Full-Stack Developer",
          description: "Become a full-stack developer with the MERN stack. From frontend to backend...",
          students: "642",
          duration: "16",
          lessons: "60",
          hours: "50"
        }
      ],
      testimonials: [
        {
          name: "An Nguyen",
          role: "Frontend Developer at Tech Solutions",
          quote: "The courses helped me go from zero to a professional frontend developer. Instructors are enthusiastic and the content is frequently updated.",
          initials: "AN",
          gradient: "linear-gradient(135deg, #1d4ed8, #38bdf8)"
        },
        {
          name: "Bach Tran",
          role: "Backend Developer at NextGen Labs",
          quote: "Thanks to a clear roadmap and supportive community, I confidently built complex APIs within weeks. The lecture quality exceeded expectations.",
          initials: "BT",
          gradient: "linear-gradient(135deg, #0ea5e9, #38bdf8)"
        },
        {
          name: "Quan Pham",
          role: "Full-Stack Developer at Aurora Tech",
          quote: "Real-world exercises and detailed feedback helped me improve quickly. After the course, I got my first full-time job.",
          initials: "QP",
          gradient: "linear-gradient(135deg, #22d3ee, #2563eb)"
        }
      ]
    }
  },
  mounted() {
    this.highlightCode();
  },
  methods: {
    highlightCode() {
      const codeBlock = this.$el.querySelector('.language-javascript');
      if (codeBlock) {
        codeBlock.classList.add('highlighted-code');
      }
    }
  }
}
</script>

<style scoped>
.home-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #0f172a;
  background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-light: #dbeafe;
  --accent: #38bdf8;
  --accent-dark: #0ea5e9;
  --teal: #14b8a6;
  --dark: #0f172a;
  --light: #f8fafc;
}

.text-gradient-primary {
  background: linear-gradient(135deg, var(--accent-dark), var(--primary));
  background-clip: text;
  color: transparent;
}

.text-gradient-success {
  background: linear-gradient(135deg, var(--teal), var(--accent));
  background-clip: text;
  color: transparent;
}

.section-title {
  color: #2563eb;   /* xanh dương */
  font-weight: 800;
  text-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}


.bg-gradient-primary {
  background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
}

.bg-gradient-success {
  background: linear-gradient(135deg, var(--teal), var(--accent)) !important;
}

.navbar {
  backdrop-filter: blur(18px);
  background: rgba(248, 250, 252, 0.92) !important;
  border-bottom: 1px solid rgba(37, 99, 235, 0.08);
  transition: background 0.3s ease, border-color 0.3s ease;
}

.nav-link {
  color: #1f2937 !important;
  position: relative;
  padding-bottom: 4px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(135deg, var(--accent), var(--primary));
  transition: width 0.3s ease;
}

.nav-link:hover {
  color: var(--primary-dark) !important;
}

.nav-link:hover::after {
  width: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent), var(--primary));
  border: none;
  font-weight: 600;
  border-radius: 999px;
  box-shadow: 0 18px 36px rgba(37, 99, 235, 0.25);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  color: #050101 !important;
}

.btn-primary:hover {
  background: #1f2937;   /* Đổi khi hover để giống nút "Tìm hiểu thêm" */
  color: #fff !important;
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(15, 23, 42, 0.2);
}

.btn-outline-primary {
  color: var(--primary);
  border-color: var(--primary);
  font-weight: 600;
  border-radius: 999px;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  background: var(--primary);
  border-color: var(--primary);
  color: #523ad6;
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(37, 99, 235, 0.2);
}

.btn-outline-dark {
  color: #1f2937;
  border-color: rgba(31, 41, 55, 0.6);
  font-weight: 600;
  border-radius: 999px;
  transition: all 0.3s ease;
}

.btn-outline-dark:hover {
  background: #1f2937;
  color: #fff;
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(15, 23, 42, 0.2);
}

.hero-section {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.95) 0%, rgba(191, 219, 254, 0.95) 100%);
  padding-top: 120px;
  padding-bottom: 100px;
  border-radius: 32px;
  box-shadow: 0 32px 80px rgba(37, 99, 235, 0.12);
}

.hero-section::before,
.hero-section::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  opacity: 0.45;
}

.hero-section::before {
  width: 420px;
  height: 420px;
  top: -160px;
  right: -140px;
  background: radial-gradient(circle at center, rgba(56, 189, 248, 0.35), transparent 65%);
}

.hero-section::after {
  width: 360px;
  height: 360px;
  bottom: -150px;
  left: -120px;
  background: radial-gradient(circle at center, rgba(37, 99, 235, 0.35), transparent 70%);
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 800;
  background: linear-gradient(90deg, #2563eb, #38bdf8, #0ea5e9, #14b8a6);
  background-size: 300% 300%;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;

  /* Hiệu ứng kết hợp */
  animation: gradientFlow 6s linear infinite, bounce 2.5s ease-in-out infinite;

  /* Bóng mờ dưới chữ */
  text-shadow: 0 6px 14px rgba(37, 99, 235, 0.35);
}

@keyframes gradientFlow {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}


@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  100% {
    background-position: 100% 50%;
  }
}

.hero-content .lead {
  color: #4b5563;
}

.stats small {
  color: #6b7280;
}

.stat-badge {
  background: linear-gradient(135deg, var(--primary-dark), var(--accent));
  border: none;
  font-weight: 600;
  box-shadow: 0 18px 36px rgba(37, 99, 235, 0.25);
  animation: pulseGlow 3s ease-in-out infinite;
  color: #000 !important;
}

.code-example-card {
  transform: perspective(1100px) rotateY(-4deg) rotateX(6deg);
  transition: transform 0.5s ease;
  filter: drop-shadow(0 24px 48px rgba(15, 23, 42, 0.2));
}

.code-example-card:hover {
  transform: perspective(1100px) rotateY(0deg) rotateX(0deg) scale(1.02);
}

.code-example-card .card {
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  backdrop-filter: blur(12px);
}

.code-example-card .card-header {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.92));
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
  color: #f8fafc;
}

.code-example-card .card-body {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
  border: none;
  color: #e2e8f0;
}

.code-example-card pre {
  font-size: 0.9rem;
  line-height: 1.5;
  font-family: 'Fira Code', 'Monaco', 'Cascadia Code', monospace;
  margin: 0;
}

.highlighted-code {
  color: #c7d2fe;
  text-shadow: 0 0 22px rgba(56, 189, 248, 0.45);
}

.feature-badge {
  border: 1px solid rgba(37, 99, 235, 0.12);
  box-shadow: 0 16px 36px rgba(37, 99, 235, 0.12);
  border-radius: 18px;
  overflow: hidden;
}

.feature-badge .bg-gradient-primary {
  background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.35);
}

.reason-card {
  transition: transform 0.4s ease, box-shadow 0.4s ease, border-color 0.4s ease;
  border: 1px solid rgba(37, 99, 235, 0.12);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
  border-radius: 20px;
}

.reason-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 36px 70px rgba(37, 99, 235, 0.18);
  border-color: rgba(37, 99, 235, 0.4);
}

.icon-wrapper {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  box-shadow: 0 15px 32px rgba(37, 99, 235, 0.18);
}

.icon-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.fallback-icon {
  font-size: 1.75rem;
  color: #2563eb;
}

.course-card {
  border: 1px solid rgba(37, 99, 235, 0.12);
  border-radius: 20px;
  transition: transform 0.4s ease, box-shadow 0.4s ease, border-color 0.4s ease;
  position: relative;
  overflow: hidden;
}

.course-card::before {
  content: '';
  position: absolute;
  top: -60px;
  right: -60px;
  width: 160px;
  height: 160px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.16), transparent 70%);
  transition: transform 0.4s ease;
}

.course-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 36px 70px rgba(37, 99, 235, 0.22);
  border-color: rgba(37, 99, 235, 0.45);
}

.course-card:hover::before {
  transform: scale(1.25);
}

.course-card .badge {
  background: rgba(37, 99, 235, 0.12) !important;
  color: var(--primary) !important;
}

.rating {
  color: #fbbf24;
}

.course-details {
  border-top: 1px solid rgba(37, 99, 235, 0.2);
}

.testimonial-card {
  border: none;
  border-radius: 24px;
  background: linear-gradient(135deg, #ffffff, #eff6ff);
  box-shadow: 0 28px 60px rgba(37, 99, 235, 0.16);
  opacity: 0;
  transform: translateY(24px);
  animation: fadeUp 0.9s ease forwards;
}

.testimonial-card .card-body {
  color: #1f2937;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  box-shadow: 0 18px 32px rgba(37, 99, 235, 0.3);
  color: #fff;
  font-weight: 700;
  font-size: 1.6rem;
  letter-spacing: 1px;
  animation: avatar-spin 12s linear infinite;
}

.avatar-initial {
  color: #fff;
  animation: avatar-spin-reverse 12s linear infinite;
  display: inline-block;
}

.demo-section {
  background: linear-gradient(135deg, var(--primary-dark), var(--accent));
  box-shadow: 0 24px 48px rgba(37, 99, 235, 0.22);
  border-radius: 18px;
}

.demo-section a {
  color: #fff;
  text-decoration: none;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.demo-section a:hover {
  opacity: 0.85;
  transform: translateY(-2px);
}

footer {
  background: linear-gradient(135deg, #0b1220, #1e293b);
  border-top: 4px solid rgba(56, 189, 248, 0.35);
  color: #e2e8f0;
}

footer a {
  transition: color 0.3s ease, opacity 0.3s ease;
}

footer a:hover {
  color: #bfdbfe !important;
  opacity: 1 !important;
}

@media (max-width: 992px) {
  .hero-section {
    border-radius: 24px;
  }
}

@media (max-width: 768px) {
  .hero-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats {
    margin-top: 1rem;
    margin-left: 0 !important;
  }

  .code-example-card {
    transform: none;
    margin-top: 2rem;
  }

  .hero-section {
    padding-top: 130px;
    border-radius: 20px;
  }
}

* {
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
@keyframes avatar-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes avatar-spin-reverse {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(-360deg);
  }
}


@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 18px 36px rgba(37, 99, 235, 0.25);
  }
  50% {
    box-shadow: 0 20px 42px rgba(56, 189, 248, 0.35);
  }
}

@keyframes fadeUp {
  0% {
    opacity: 0;
    transform: translateY(24px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
