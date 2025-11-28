<template>
    <div class="course-edit">
        <div class="edit-header">
            <button @click="goBack" class="btn-back">
                <i class="fas fa-arrow-left"></i> Back
            </button>
            <h1>{{ isEdit ? 'Edit Course' : 'Create New Course' }}</h1>
        </div>

        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>

        <div v-else class="edit-container">
            <form @submit.prevent="saveCourse" class="edit-form">
                <!-- Basic Info -->
                <section class="form-section">
                    <h2>Basic Information</h2>
                    
                    <div class="form-group">
                        <label>Course Title *</label>
                        <input 
                            type="text" 
                            v-model="form.title" 
                            required
                            placeholder="Enter course title"
                        >
                    </div>

                    <div class="form-group">
                        <label>Course Description *</label>
                        <textarea 
                            v-model="form.description" 
                            rows="4"
                            required
                            placeholder="Enter a detailed description of the course"
                        ></textarea>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Price (VND) *</label>
                            <input 
                                type="number" 
                                v-model.number="form.price" 
                                min="0"
                                required
                                placeholder="0"
                            >
                        </div>
                        <div class="form-group">
                            <label>Status *</label>
                            <select v-model="form.status" required>
                                <option value="draft">Draft</option>
                                <option value="active">Active</option>
                                <option value="archived">Archived</option>
                            </select>
                        </div>
                    </div>
                </section>

                <!-- Images -->
                <section class="form-section">
                    <h2>Images</h2>
                    
                    <div class="form-group">
                        <label>Thumbnail URL *</label>
                        <input 
                            type="url" 
                            v-model="form.thumbnail"
                            required
                            placeholder="https://example.com/image.jpg"
                        >
                    </div>

                    <div v-if="form.thumbnail" class="thumbnail-preview">
                        <p>Preview:</p>
                        <img :src="form.thumbnail" :alt="form.title" @error="onImageError">
                    </div>
                </section>

                <!-- Form Actions -->
                <section class="form-actions">
                    <button type="button" @click="goBack" class="btn-secondary">
                        Cancel
                    </button>
                    <button type="submit" class="btn-primary">
                        {{ isEdit ? 'Update' : 'Create Course' }}
                    </button>
                </section>
            </form>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CourseEdit',
    data() {
        return {
            isEdit: false,
            loading: true,
            form: {
                title: '',
                description: '',
                price: 0,
                thumbnail: '',
                status: 'draft',
            }
        }
    },
    mounted() {
        this.loadCourse()
    },
    methods: {
        async loadCourse() {
            this.loading = true
            try {
                const courseId = this.$route.params.id
                if (courseId) {
                    this.isEdit = true
                    // Fetch real course data from backend
                    const res = await fetch(`http://localhost:5000/api/courses/${courseId}`)
                    if (!res.ok) {
                        const err = await res.json().catch(() => ({}))
                        throw new Error(err.message || `Failed to load course (HTTP ${res.status})`)
                    }
                    const course = await res.json()
                    // Map to form fields (assuming backend returns basic fields)
                    this.form = {
                        title: course.title || '',
                        description: course.description || '',
                        price: Number(course.price) || 0,
                        thumbnail: course.thumbnail || '',
                        status: course.status || 'draft',
                    }
                } else {
                    this.isEdit = false
                }
            } catch (error) {
                console.error('Error loading course:', error)
                this.$toast?.error(error.message || 'Failed to load course')
            }
            this.loading = false
        },

        async saveCourse() {
            try {
                const baseUrl = 'http://localhost:5000/api/courses'
                const instructorId = 2 // TODO: use auth state/token
                const payload = {
                    title: this.form.title,
                    description: this.form.description,
                    price: Number(this.form.price),
                    thumbnail: this.form.thumbnail,
                    status: this.form.status,
                    instructor_id: instructorId,
                }

                let res
                if (this.isEdit) {
                    const id = this.$route.params.id
                    res = await fetch(`${baseUrl}/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                    })
                } else {
                    res = await fetch(baseUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                    })
                }

                const data = await res.json().catch(() => ({}))
                if (!res.ok) {
                    throw new Error(data.message || `Failed to save course (HTTP ${res.status})`)
                }

                this.$toast?.success(this.isEdit ? 'Course updated' : 'Course created')
                this.$router.push('/instructor/courses')
            } catch (error) {
                console.error('Error saving course:', error)
                this.$toast?.error(error.message || 'Failed to save course')
            }
        },

        onImageError() {
            console.error('Failed to load image')
        },

        goBack() {
            this.$router.back()
        }
    }
}
</script>

<style scoped>
.course-edit {
    min-height: 100vh;
    background: #f8f9fa;
}

.edit-header {
    background: white;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    border-bottom: 1px solid #eee;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-back {
    background: none;
    border: none;
    color: #3498db;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-back:hover {
    color: #2980b9;
}

.edit-header h1 {
    margin: 0;
    color: #2c3e50;
    font-size: 24px;
}

.loading {
    text-align: center;
    padding: 60px 20px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.edit-container {
    max-width: 900px;
    margin: 30px auto;
    padding: 0 20px;
}

.edit-form {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.form-section {
    padding: 30px;
    border-bottom: 1px solid #eee;
}

.form-section:last-of-type {
    border-bottom: none;
}

.form-section h2 {
    color: #2c3e50;
    margin: 0 0 20px;
    font-size: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group:last-child {
    margin-bottom: 0;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.thumbnail-preview {
    margin-top: 20px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 6px;
}

.thumbnail-preview p {
    margin: 0 0 12px;
    color: #555;
    font-weight: 500;
}

.thumbnail-preview img {
    max-width: 100%;
    max-height: 300px;
    border-radius: 6px;
}

.form-actions {
    padding: 30px;
    background: #f8f9fa;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.btn-primary, .btn-secondary {
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

.btn-secondary {
    background: #ecf0f1;
    color: #555;
}

.btn-secondary:hover {
    background: #dfe6e9;
}

@media (max-width: 768px) {
    .edit-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .form-actions {
        flex-direction: column;
    }

    .form-actions button {
        width: 100%;
    }
}
</style>
