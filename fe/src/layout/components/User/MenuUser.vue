<template>
    <!-- Hero Section -->
    <section class="container text-center py-5">

        <!-- Logo + Tên -->
        <div class="d-flex justify-content-center align-items-center mb-3">
            <div class="d-flex align-items-center justify-content-center bg-success text-white fw-bold rounded me-2"
                style="width:40px; height:40px;">CC</div>
            <h2 class="fw-bold mb-0">
                <span class="text-success">Code</span><span class="text-primary">Class</span>
                <div class="fs-6 fw-normal text-muted">Manager</div>
            </h2>
        </div>

        <!-- Tagline -->
        <h1 class="fw-bold mb-3">
            AI-Powered Programming <br>
            <span class="text-success">Education</span> <span class="text-primary">Platform</span>
        </h1>

        <!-- Mô tả -->
        <p class="text-muted mb-4 fs-5">
            Master programming with personalized AI assistance, interactive coding environments, <br>
            and comprehensive progress tracking. Built for students, instructors, and administrators.
        </p>

        <!-- Nút hành động -->
        <div class="d-flex justify-content-center gap-3 mb-4">
            <!-- Login -->
            <router-link to="/login" class="btn btn-success btn-lg d-flex align-items-center gap-2 px-4">
                <i class="bi bi-mortarboard-fill"></i> Login <i class="bi bi-arrow-right"></i>
            </router-link>

            <!-- Register -->
            <router-link to="/register" class="btn btn-light btn-lg shadow-sm d-flex align-items-center gap-2 px-4">
                <i class="bi bi-person-video3"></i> Register
            </router-link>
        </div>

        <!-- Link demo -->
        <div class="text-muted">
            Quick Demo:
            <router-link to="/student" class="text-success text-decoration-none">Student</router-link> •
            <router-link to="/instructor" class="text-success text-decoration-none">Instructor</router-link> •
            <router-link to="/admin" class="text-success text-decoration-none">Admin</router-link>
        </div>

    </section>

    <section class="container py-5 text-center">
        <!-- Tiêu đề -->
        <h2 class="fw-bold mb-2">Everything You Need to Excel</h2>
        <p class="text-muted mb-5">Comprehensive tools and features designed to enhance programming education</p>

        <!-- Hàng 1 -->
        <div class="row g-4 mb-4">
            <!-- Card 1 -->
            <div class="col-md-4">
                <div class="card h-100 shadow-sm border-0 text-start p-3">
                    <div class="d-flex align-items-center mb-2">
                        <span class="fs-3 me-2">🤖</span>
                        <h5 class="fw-bold mb-0">AI-Powered Assistant</h5>
                    </div>
                    <span class="badge bg-success bg-opacity-25 text-success mb-2">Smart Learning</span>
                    <p class="text-muted">Get instant help with coding problems, explanations, and personalized learning
                        recommendations powered by advanced AI.</p>
                </div>
            </div>

            <!-- Card 2 -->
            <div class="col-md-4">
                <div class="card h-100 shadow-sm border-0 text-start p-3">
                    <div class="d-flex align-items-center mb-2">
                        <span class="fs-3 me-2">💻</span>
                        <h5 class="fw-bold mb-0">Interactive Code Lab</h5>
                    </div>
                    <span class="badge bg-success bg-opacity-25 text-success mb-2">Multi-Language</span>
                    <p class="text-muted">Practice coding in 10+ programming languages with real-time feedback and
                        automated testing.</p>
                </div>
            </div>

            <!-- Card 3 -->
            <div class="col-md-4">
                <div class="card h-100 shadow-sm border-0 text-start p-3">
                    <div class="d-flex align-items-center mb-2">
                        <span class="fs-3 me-2">📊</span>
                        <h5 class="fw-bold mb-0">Progress Tracking</h5>
                    </div>
                    <span class="badge bg-success bg-opacity-25 text-success mb-2">Data Driven</span>
                    <p class="text-muted">Comprehensive analytics and insights to track learning progress and identify
                        areas for improvement.</p>
                </div>
            </div>
        </div>

        <!-- Hàng 2 -->
        <div class="row g-4">
            <!-- Card 4 -->
            <div class="col-md-4">
                <div class="card h-100 shadow-sm border-0 text-start p-3">
                    <div class="d-flex align-items-center mb-2">
                        <span class="fs-3 me-2">📚</span>
                        <h5 class="fw-bold mb-0">Course Management</h5>
                    </div>
                    <span class="badge bg-success bg-opacity-25 text-success mb-2">Structured Learning</span>
                    <p class="text-muted">Create, manage, and deliver programming courses with structured curriculum and
                        assignments.</p>
                </div>
            </div>

            <!-- Card 5 -->
            <div class="col-md-4">
                <div class="card h-100 shadow-sm border-0 text-start p-3">
                    <div class="d-flex align-items-center mb-2">
                        <span class="fs-3 me-2">👥</span>
                        <h5 class="fw-bold mb-0">Multi-Role Support</h5>
                    </div>
                    <span class="badge bg-success bg-opacity-25 text-success mb-2">Role-Based</span>
                    <p class="text-muted">Purpose-built interfaces for students, instructors, and administrators with
                        role-specific features.</p>
                </div>
            </div>

            <!-- Card 6 -->
            <div class="col-md-4">
                <div class="card h-100 shadow-sm border-0 text-start p-3">
                    <div class="d-flex align-items-center mb-2">
                        <span class="fs-3 me-2">🔄</span>
                        <h5 class="fw-bold mb-0">Real-time Collaboration</h5>
                    </div>
                    <span class="badge bg-success bg-opacity-25 text-success mb-2">Team Work</span>
                    <p class="text-muted">Work together on coding projects with live code sharing and collaborative
                        debugging.</p>
                </div>
            </div>
        </div>
    </section>
</template>

<script>
export default {
    name: "MenuUser",
};
</script>
<style></style>