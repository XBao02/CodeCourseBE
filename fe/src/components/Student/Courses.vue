<template>
    <div class="p-4">
        <h1 class="text-center mb-5">Student Courses</h1>
        <div class="row justify-content-center">
            <div v-for="(course, index) in courses" :key="index" class="col-md-12 mb-4">
                <div class="card shadow-sm d-flex flex-row align-items-center">
                    <img :src="course.image" alt="Course Image" class="card-img-left"
                        style="width: 200px; height: 150px; object-fit: cover;">
                    <div class="card-body d-flex flex-column justify-content-between flex-grow-1">
                        <div>
                            <h2 class="card-title large-text course-title">{{ course.name }}</h2>
                            <p class="card-text large-text">Instructor: {{ course.instructor }}</p>
                            <div class="d-flex align-items-center mb-3">
                                <span class="me-2 large-text">Rating: {{ course.rating }}</span>
                                <div class="stars">
                                    <i v-for="star in 5" :key="star" class="fas fa-star"
                                        :class="{ 'text-warning': star <= Math.floor(course.rating), 'text-secondary': star > Math.ceil(course.rating) }"></i>
                                </div>
                            </div>
                            <div class="mb-3">
                                <h5>Sessions:</h5>
                                <div class="d-flex flex-wrap gap-2 mb-3">
                                    <button v-for="(session, sIndex) in course.sessions" :key="sIndex"
                                        class="btn btn-outline-primary rounded-circle session-btn"
                                        style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;"
                                        @click="toggleSession(index, sIndex)">
                                        {{ sIndex + 1 }}
                                    </button>
                                </div>
                                <div v-for="(session, sIndex) in course.sessions" :key="'details-' + sIndex"
                                    class="session-details" :class="{ 'active': course.activeSession === sIndex }">
                                    <h5>{{ session.name }}</h5>
                                    <p>{{ session.description }}</p>
                                    <button class="btn btn-primary mt-2" @click="startSession(course, sIndex)">Start
                                        Learning</button>
                                </div>
                            </div>
                        </div>
                        <div class="d-flex flex-column">
                            <div class="progress mb-3" style="height: 50px;">
                                <div class="progress-bar bg-success" :style="{ width: course.progress + '%' }">{{
                                    course.progress }}%</div>
                            </div>
                            <button class="btn btn-primary w-100" @click="goToCourse(course)">Go to course</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        >>>>>>> origin/tnqoc
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            courses: [
                {
                    name: 'Basic Java Programming',
                    instructor: 'Dr. Davis Marcos',
                    rating: 4.8,
                    image: 'public/download.jpg',
                    sessions: [
                        { name: 'Introduction to Java', description: 'Learn the basic concepts of the Java language.' },
                        { name: 'Variables and Data Types', description: 'Understand variables and data types in Java.' },
                        { name: 'Control Structures', description: 'Explore control structures like if, switch.' },
                        { name: 'Arrays and Strings', description: 'Work with arrays and strings in Java.' },
                        { name: 'Classes and Objects', description: 'Learn about object-oriented programming.' },
                        { name: 'Inheritance and Polymorphism', description: 'Discover inheritance and polymorphism.' },
                        { name: 'Exception Handling', description: 'Manage exceptions in Java.' },
                        { name: 'Files and I/O', description: 'Work with files and I/O.' }
                    ],
                    progress: 60,
                    activeSession: null
                },
                {
                    name: 'Python for Beginners',
                    instructor: 'Dr. Sophie Alden',
                    rating: 4.5,
                    image: 'public/python-co-ban_b80bca9b238b4615b94541de28af00ae.png',
                    sessions: [
                        { name: 'Installing Python', description: 'Guide to setting up the Python environment.' },
                        { name: 'Basic Syntax', description: 'Learn the basic syntax of Python.' },
                        { name: 'Functions and Modules', description: 'Use functions and modules in Python.' },
                        { name: 'Lists and Dictionaries', description: 'Work with lists and dictionaries.' },
                        { name: 'Object-Oriented Programming', description: 'Learn object-oriented programming with Python.' }
                    ],
                    progress: 40,
                    activeSession: null
                },
                {
                    name: 'Advanced JavaScript',
                    instructor: 'Dr. Paul William',
                    rating: 4.9,
                    image: 'public/images.png',
                    sessions: [
                        { name: 'ES6 Features', description: 'Explore new features of ES6.' },
                        { name: 'Asynchronous Programming', description: 'Work with asynchronous programming.' },
                        { name: 'DOM Manipulation', description: 'Manipulate the DOM in JavaScript.' },
                        { name: 'Fetch API', description: 'Use the Fetch API to call APIs.' },
                        { name: 'Modules and Bundling', description: 'Learn about modules and bundling.' },
                        { name: 'Error Handling', description: 'Manage errors in JavaScript.' },
                        { name: 'Testing with Jest', description: 'Perform testing with Jest.' }
                    ],
                    progress: 75,
                    activeSession: null
                }
            ]
        };
    },
    methods: {
        toggleSession(courseIndex, sessionIndex) {
            const course = this.courses[courseIndex];
            if (course.activeSession === sessionIndex) {
                course.activeSession = null; // Hide if already open
            } else {
                course.activeSession = sessionIndex; // Show selected session
            }
        },
        startSession(course, sessionIndex) {
            // Logic to start learning, e.g., redirect
            alert(`Start learning: ${course.sessions[sessionIndex].name}`);
            course.activeSession = null; // Hide after starting
        },
        goToCourse(course) {
            // Use router to navigate, assuming route /course/:name
            this.$router.push(`/course/${course.name.replace(/\s+/g, '-')}`);
        }
    }
};
</script>

<style scoped>
.card {
    border-radius: 10px;
    overflow: hidden;
}

.card-img-left {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}

.card-body {
    padding: 20px;
}

.stars .fas {
    font-size: 1.2rem;
}

.progress {
    border-radius: 10px;
}

.btn-primary {
    border-radius: 8px;
    padding: 10px 0;
}

.btn-outline-primary {
    border-width: 2px;
    /* Make button border bolder */
}

.session-details {
    display: none;
    margin-top: 30px;
    padding: 25px;
    background-color: #f8f9fa;
    border-radius: 5px;
}

.session-details.active {
    display: block;
}

.large-text {
    font-size: 1.25rem;
    /* Base size for Instructor and Rating, about 20px */
    font-weight: bold;
    /* Keep bold for emphasis */
}

.course-title {
    font-size: 1.75rem;
    /* Font size for course title, about 28px */
}
</style>
