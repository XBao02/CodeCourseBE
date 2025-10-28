<template>
    <div class="question-bank">
        <div class="bank-header">
            <h1>Ngân hàng Câu hỏi</h1>
            <div class="header-actions">
                <button @click="exportQuestions" class="btn-export">
                    <i class="fas fa-download"></i>
                    Xuất Excel
                </button>
                <button @click="importQuestions" class="btn-import">
                    <i class="fas fa-upload"></i>
                    Nhập từ Excel
                </button>
                <button @click="showQuestionModal = true" class="btn-primary">
                    <i class="fas fa-plus"></i>
                    Thêm câu hỏi
                </button>
            </div>
        </div>

        <!-- Statistics -->
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-icon easy">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-info">
                    <h3>{{ stats.easy }}</h3>
                    <p>Câu hỏi dễ</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon medium">
                    <i class="fas fa-exclamation-circle"></i>
                </div>
                <div class="stat-info">
                    <h3>{{ stats.medium }}</h3>
                    <p>Câu hỏi trung bình</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon hard">
                    <i class="fas fa-times-circle"></i>
                </div>
                <div class="stat-info">
                    <h3>{{ stats.hard }}</h3>
                    <p>Câu hỏi khó</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon total">
                    <i class="fas fa-list"></i>
                </div>
                <div class="stat-info">
                    <h3>{{ stats.total }}</h3>
                    <p>Tổng câu hỏi</p>
                </div>
            </div>
        </div>

        <!-- Filters and Search -->
        <div class="bank-filters">
            <div class="filter-row">
                <div class="filter-group">
                    <label>Khóa học:</label>
                    <select v-model="filters.courseId" @change="applyFilters">
                        <option value="">Tất cả khóa học</option>
                        <option v-for="course in courses" :key="course.id" :value="course.id">
                            {{ course.title }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Chương:</label>
                    <select v-model="filters.chapterId" @change="applyFilters">
                        <option value="">Tất cả chương</option>
                        <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
                            {{ chapter.title }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Độ khó:</label>
                    <select v-model="filters.difficulty" @change="applyFilters">
                        <option value="">Tất cả</option>
                        <option value="easy">Dễ</option>
                        <option value="medium">Trung bình</option>
                        <option value="hard">Khó</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Loại câu hỏi:</label>
                    <select v-model="filters.type" @change="applyFilters">
                        <option value="">Tất cả loại</option>
                        <option value="single">Một đáp án</option>
                        <option value="multiple">Nhiều đáp án</option>
                    </select>
                </div>
            </div>
            
            <div class="search-row">
                <div class="search-group">
                    <input 
                        type="text" 
                        v-model="searchQuery" 
                        placeholder="Tìm kiếm theo tiêu đề, nội dung..."
                        @input="applyFilters"
                    >
                    <i class="fas fa-search"></i>
                </div>
                
                <div class="view-options">
                    <button 
                        @click="viewMode = 'grid'" 
                        :class="['view-btn', { active: viewMode === 'grid' }]"
                    >
                        <i class="fas fa-th"></i>
                    </button>
                    <button 
                        @click="viewMode = 'list'" 
                        :class="['view-btn', { active: viewMode === 'list' }]"
                    >
                        <i class="fas fa-list"></i>
                    </button>
                </div>
                
                <div class="bulk-actions">
                    <button 
                        @click="selectAll" 
                        class="btn-select-all"
                        v-if="filteredQuestions.length > 0"
                    >
                        {{ selectedQuestions.length === filteredQuestions.length ? 'Bỏ chọn tất cả' : 'Chọn tất cả' }}
                    </button>
                    <button 
                        @click="bulkDelete" 
                        class="btn-bulk-delete"
                        v-if="selectedQuestions.length > 0"
                    >
                        <i class="fas fa-trash"></i>
                        Xóa ({{ selectedQuestions.length }})
                    </button>
                </div>
            </div>
        </div>

        <!-- Questions List -->
        <div class="questions-container">
            <div v-if="loading" class="loading">
                <div class="spinner"></div>
                <p>Đang tải câu hỏi...</p>
            </div>
            
            <div v-else-if="filteredQuestions.length === 0" class="no-questions">
                <div class="empty-icon">
                    <i class="fas fa-question-circle"></i>
                </div>
                <h3>Không có câu hỏi nào</h3>
                <p>{{ searchQuery ? 'Không tìm thấy câu hỏi phù hợp với từ khóa tìm kiếm.' : 'Hãy thêm câu hỏi đầu tiên của bạn!' }}</p>
                <button @click="showQuestionModal = true" class="btn-primary">
                    <i class="fas fa-plus"></i>
                    Thêm câu hỏi đầu tiên
                </button>
            </div>
            
            <div v-else>
                <!-- Grid View -->
                <div v-if="viewMode === 'grid'" class="questions-grid">
                    <div 
                        v-for="question in paginatedQuestions" 
                        :key="question.id" 
                        class="question-card"
                        :class="{ selected: selectedQuestions.includes(question.id) }"
                    >
                        <div class="card-header">
                            <label class="checkbox-container">
                                <input 
                                    type="checkbox" 
                                    :checked="selectedQuestions.includes(question.id)"
                                    @change="toggleQuestion(question.id)"
                                >
                                <span class="checkmark"></span>
                            </label>
                            
                            <div class="question-badges">
                                <span class="type-badge" :class="question.type">
                                    {{ question.type === 'single' ? 'Một đáp án' : 'Nhiều đáp án' }}
                                </span>
                                <span class="difficulty-badge" :class="question.difficulty">
                                    {{ getDifficultyText(question.difficulty) }}
                                </span>
                            </div>
                            
                            <div class="card-actions">
                                <button @click="previewQuestion(question)" class="action-btn preview">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button @click="editQuestion(question)" class="action-btn edit">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button @click="duplicateQuestion(question)" class="action-btn duplicate">
                                    <i class="fas fa-copy"></i>
                                </button>
                                <button @click="deleteQuestion(question.id)" class="action-btn delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        
                        <div class="card-content">
                            <h4 class="question-title">{{ question.title }}</h4>
                            <div class="question-content" v-html="question.content"></div>
                            
                            <div class="answers-preview">
                                <div 
                                    v-for="(answer, index) in question.answers.slice(0, 2)" 
                                    :key="index"
                                    class="answer-preview"
                                    :class="{ correct: answer.isCorrect }"
                                >
                                    <span class="answer-label">{{ String.fromCharCode(65 + index) }}.</span>
                                    {{ answer.text }}
                                    <i v-if="answer.isCorrect" class="fas fa-check"></i>
                                </div>
                                <div v-if="question.answers.length > 2" class="more-answers">
                                    +{{ question.answers.length - 2 }} đáp án khác
                                </div>
                            </div>
                        </div>
                        
                        <div class="card-footer">
                            <span class="course-info">{{ question.course }} - {{ question.chapter }}</span>
                            <span class="date-info">{{ formatDate(question.createdAt) }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- List View -->
                <div v-else class="questions-list">
                    <div class="list-header">
                        <div class="col-select">
                            <label class="checkbox-container">
                                <input 
                                    type="checkbox" 
                                    :checked="selectedQuestions.length === filteredQuestions.length"
                                    @change="selectAll"
                                >
                                <span class="checkmark"></span>
                            </label>
                        </div>
                        <div class="col-title">Câu hỏi</div>
                        <div class="col-course">Khóa học</div>
                        <div class="col-difficulty">Độ khó</div>
                        <div class="col-type">Loại</div>
                        <div class="col-date">Ngày tạo</div>
                        <div class="col-actions">Thao tác</div>
                    </div>
                    
                    <div 
                        v-for="question in paginatedQuestions" 
                        :key="question.id"
                        class="list-item"
                        :class="{ selected: selectedQuestions.includes(question.id) }"
                    >
                        <div class="col-select">
                            <label class="checkbox-container">
                                <input 
                                    type="checkbox" 
                                    :checked="selectedQuestions.includes(question.id)"
                                    @change="toggleQuestion(question.id)"
                                >
                                <span class="checkmark"></span>
                            </label>
                        </div>
                        <div class="col-title">
                            <h5>{{ question.title }}</h5>
                            <p>{{ question.content.substring(0, 100) }}...</p>
                        </div>
                        <div class="col-course">{{ question.course }}</div>
                        <div class="col-difficulty">
                            <span class="difficulty-badge" :class="question.difficulty">
                                {{ getDifficultyText(question.difficulty) }}
                            </span>
                        </div>
                        <div class="col-type">
                            <span class="type-badge" :class="question.type">
                                {{ question.type === 'single' ? 'Một đáp án' : 'Nhiều đáp án' }}
                            </span>
                        </div>
                        <div class="col-date">{{ formatDate(question.createdAt) }}</div>
                        <div class="col-actions">
                            <button @click="previewQuestion(question)" class="action-btn preview">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button @click="editQuestion(question)" class="action-btn edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button @click="duplicateQuestion(question)" class="action-btn duplicate">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button @click="deleteQuestion(question.id)" class="action-btn delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Pagination -->
                <div class="pagination-container" v-if="totalPages > 1">
                    <div class="pagination-info">
                        Hiển thị {{ ((currentPage - 1) * itemsPerPage) + 1 }} - 
                        {{ Math.min(currentPage * itemsPerPage, filteredQuestions.length) }} 
                        trong tổng số {{ filteredQuestions.length }} câu hỏi
                    </div>
                    
                    <div class="pagination">
                        <button 
                            @click="currentPage = 1" 
                            :disabled="currentPage === 1"
                            class="page-btn"
                        >
                            <i class="fas fa-angle-double-left"></i>
                        </button>
                        <button 
                            @click="currentPage--" 
                            :disabled="currentPage === 1"
                            class="page-btn"
                        >
                            <i class="fas fa-angle-left"></i>
                        </button>
                        
                        <span class="page-numbers">
                            <button 
                                v-for="page in visiblePages" 
                                :key="page"
                                @click="currentPage = page"
                                :class="['page-number', { active: page === currentPage }]"
                            >
                                {{ page }}
                            </button>
                        </span>
                        
                        <button 
                            @click="currentPage++" 
                            :disabled="currentPage === totalPages"
                            class="page-btn"
                        >
                            <i class="fas fa-angle-right"></i>
                        </button>
                        <button 
                            @click="currentPage = totalPages" 
                            :disabled="currentPage === totalPages"
                            class="page-btn"
                        >
                            <i class="fas fa-angle-double-right"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Question Preview Modal -->
        <div v-if="showPreviewModal" class="modal-overlay">
            <div class="modal-content preview-modal">
                <div class="modal-header">
                    <h3>Xem trước câu hỏi</h3>
                    <button @click="closePreviewModal" class="btn-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="preview-content" v-if="previewQuestion">
                    <div class="preview-header">
                        <div class="question-info">
                            <span class="type-badge" :class="previewQuestion.type">
                                {{ previewQuestion.type === 'single' ? 'Một đáp án đúng' : 'Nhiều đáp án đúng' }}
                            </span>
                            <span class="difficulty-badge" :class="previewQuestion.difficulty">
                                {{ getDifficultyText(previewQuestion.difficulty) }}
                            </span>
                        </div>
                        <div class="course-path">
                            {{ previewQuestion.course }} → {{ previewQuestion.chapter }}
                        </div>
                    </div>
                    
                    <div class="question-display">
                        <h4>{{ previewQuestion.title }}</h4>
                        <div class="question-content" v-html="previewQuestion.content"></div>
                        
                        <div class="answers-display">
                            <div 
                                v-for="(answer, index) in previewQuestion.answers" 
                                :key="index"
                                class="answer-option"
                                :class="{ correct: answer.isCorrect }"
                            >
                                <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                                <span class="option-text">{{ answer.text }}</span>
                                <i v-if="answer.isCorrect" class="fas fa-check correct-mark"></i>
                            </div>
                        </div>
                        
                        <div v-if="previewQuestion.explanation" class="explanation">
                            <h5>Giải thích:</h5>
                            <p>{{ previewQuestion.explanation }}</p>
                        </div>
                    </div>
                </div>
                
                <div class="modal-actions">
                    <button @click="editQuestion(previewQuestion)" class="btn-primary">
                        <i class="fas fa-edit"></i>
                        Chỉnh sửa
                    </button>
                    <button @click="closePreviewModal" class="btn-secondary">
                        Đóng
                    </button>
                </div>
            </div>
        </div>

        <!-- Import Modal -->
        <div v-if="showImportModal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Nhập câu hỏi từ Excel</h3>
                    <button @click="closeImportModal" class="btn-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="import-content">
                    <div class="import-instructions">
                        <h4>Hướng dẫn:</h4>
                        <ol>
                            <li>Tải file mẫu Excel để xem định dạng</li>
                            <li>Điền thông tin câu hỏi vào file Excel</li>
                            <li>Tải file lên để import</li>
                        </ol>
                        
                        <button @click="downloadTemplate" class="btn-template">
                            <i class="fas fa-download"></i>
                            Tải file mẫu
                        </button>
                    </div>
                    
                    <div class="file-upload">
                        <input 
                            type="file" 
                            ref="fileInput"
                            @change="handleFileUpload"
                            accept=".xlsx,.xls"
                            style="display: none"
                        >
                        
                        <div class="upload-area" @click="$refs.fileInput.click()">
                            <i class="fas fa-cloud-upload-alt"></i>
                            <p>Click để chọn file Excel</p>
                            <span>Chỉ hỗ trợ file .xlsx, .xls</span>
                        </div>
                        
                        <div v-if="uploadedFile" class="uploaded-file">
                            <i class="fas fa-file-excel"></i>
                            <span>{{ uploadedFile.name }}</span>
                            <button @click="removeFile" class="btn-remove">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="modal-actions">
                    <button @click="closeImportModal" class="btn-secondary">Hủy</button>
                    <button 
                        @click="processImport" 
                        class="btn-primary"
                        :disabled="!uploadedFile"
                    >
                        <i class="fas fa-upload"></i>
                        Import
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'QuestionBank',
    data() {
        return {
            loading: false,
            questions: [],
            filteredQuestions: [],
            selectedQuestions: [],
            courses: [],
            chapters: [],
            
            // Filters
            filters: {
                courseId: '',
                chapterId: '',
                difficulty: '',
                type: ''
            },
            searchQuery: '',
            
            // View options
            viewMode: 'grid', // 'grid' or 'list'
            
            // Pagination
            currentPage: 1,
            itemsPerPage: 12,
            
            // Modals
            showQuestionModal: false,
            showPreviewModal: false,
            showImportModal: false,
            previewedQuestion: null,
            
            // Import
            uploadedFile: null,
            
            // Stats
            stats: {
                easy: 0,
                medium: 0,
                hard: 0,
                total: 0
            }
        }
    },
    computed: {
        filteredChapters() {
            if (!this.filters.courseId) return this.chapters
            return this.chapters.filter(c => c.courseId == this.filters.courseId)
        },
        
        paginatedQuestions() {
            const start = (this.currentPage - 1) * this.itemsPerPage
            const end = start + this.itemsPerPage
            return this.filteredQuestions.slice(start, end)
        },
        
        totalPages() {
            return Math.ceil(this.filteredQuestions.length / this.itemsPerPage)
        },
        
        visiblePages() {
            const total = this.totalPages
            const current = this.currentPage
            const delta = 2
            
            let start = Math.max(1, current - delta)
            let end = Math.min(total, current + delta)
            
            if (current - delta > 1) {
                start = Math.max(1, current - delta)
            }
            if (current + delta < total) {
                end = Math.min(total, current + delta)
            }
            
            const pages = []
            for (let i = start; i <= end; i++) {
                pages.push(i)
            }
            return pages
        }
    },
    mounted() {
        this.loadData()
    },
    methods: {
        async loadData() {
            this.loading = true
            try {
                await Promise.all([
                    this.loadCourses(),
                    this.loadQuestions()
                ])
                this.calculateStats()
            } catch (error) {
                console.error('Lỗi khi tải dữ liệu:', error)
            } finally {
                this.loading = false
            }
        },
        
        async loadCourses() {
            // Mock data - thay bằng API call thực
            this.courses = [
                { id: 1, title: 'JavaScript Fundamentals' },
                { id: 2, title: 'Vue.js Complete Guide' },
                { id: 3, title: 'Python for Beginners' }
            ]
            
            this.chapters = [
                { id: 1, title: 'Variables and Data Types', courseId: 1 },
                { id: 2, title: 'Functions and Scope', courseId: 1 },
                { id: 3, title: 'Vue Components', courseId: 2 },
                { id: 4, title: 'Vue Router', courseId: 2 }
            ]
        },
        
        async loadQuestions() {
            // Mock data - thay bằng API call thực
            this.questions = [
                {
                    id: 1,
                    title: 'JavaScript Variables',
                    content: 'Cách khai báo biến trong JavaScript là gì?',
                    type: 'single',
                    difficulty: 'easy',
                    course: 'JavaScript Fundamentals',
                    chapter: 'Variables and Data Types',
                    courseId: 1,
                    chapterId: 1,
                    answers: [
                        { text: 'var name = "John"', isCorrect: true },
                        { text: 'variable name = "John"', isCorrect: false },
                        { text: 'string name = "John"', isCorrect: false },
                        { text: 'declare name = "John"', isCorrect: false }
                    ],
                    explanation: 'Trong JavaScript, ta sử dụng từ khóa var, let hoặc const để khai báo biến.',
                    createdAt: new Date('2024-01-15')
                },
                {
                    id: 2,
                    title: 'Vue.js Components',
                    content: 'Cách tạo component trong Vue.js?',
                    type: 'multiple',
                    difficulty: 'medium',
                    course: 'Vue.js Complete Guide',
                    chapter: 'Vue Components',
                    courseId: 2,
                    chapterId: 3,
                    answers: [
                        { text: 'Vue.component()', isCorrect: true },
                        { text: 'app.component()', isCorrect: true },
                        { text: 'new Vue()', isCorrect: false },
                        { text: 'createComponent()', isCorrect: false }
                    ],
                    explanation: 'Vue.js cung cấp nhiều cách để tạo component.',
                    createdAt: new Date('2024-01-16')
                }
            ]
            
            this.applyFilters()
        },
        
        calculateStats() {
            this.stats = {
                easy: this.questions.filter(q => q.difficulty === 'easy').length,
                medium: this.questions.filter(q => q.difficulty === 'medium').length,
                hard: this.questions.filter(q => q.difficulty === 'hard').length,
                total: this.questions.length
            }
        },
        
        applyFilters() {
            let filtered = [...this.questions]
            
            // Filter by course
            if (this.filters.courseId) {
                filtered = filtered.filter(q => q.courseId == this.filters.courseId)
            }
            
            // Filter by chapter
            if (this.filters.chapterId) {
                filtered = filtered.filter(q => q.chapterId == this.filters.chapterId)
            }
            
            // Filter by difficulty
            if (this.filters.difficulty) {
                filtered = filtered.filter(q => q.difficulty === this.filters.difficulty)
            }
            
            // Filter by type
            if (this.filters.type) {
                filtered = filtered.filter(q => q.type === this.filters.type)
            }
            
            // Search filter
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                filtered = filtered.filter(q => 
                    q.title.toLowerCase().includes(query) ||
                    q.content.toLowerCase().includes(query)
                )
            }
            
            this.filteredQuestions = filtered
            this.currentPage = 1
        },
        
        toggleQuestion(questionId) {
            const index = this.selectedQuestions.indexOf(questionId)
            if (index > -1) {
                this.selectedQuestions.splice(index, 1)
            } else {
                this.selectedQuestions.push(questionId)
            }
        },
        
        selectAll() {
            if (this.selectedQuestions.length === this.filteredQuestions.length) {
                this.selectedQuestions = []
            } else {
                this.selectedQuestions = this.filteredQuestions.map(q => q.id)
            }
        },
        
        previewQuestion(question) {
            this.previewedQuestion = question
            this.showPreviewModal = true
        },
        
        closePreviewModal() {
            this.showPreviewModal = false
            this.previewedQuestion = null
        },
        
        editQuestion(question) {
            // Emit event to parent or navigate to edit page
            this.$emit('edit-question', question)
        },
        
        duplicateQuestion(question) {
            // Create duplicate
            this.$emit('duplicate-question', question)
        },
        
        async deleteQuestion(questionId) {
            if (confirm('Bạn có chắc muốn xóa câu hỏi này?')) {
                try {
                    // API call to delete
                    this.questions = this.questions.filter(q => q.id !== questionId)
                    this.applyFilters()
                    this.calculateStats()
                    this.$toast.success('Đã xóa câu hỏi')
                } catch (error) {
                    console.error('Lỗi khi xóa câu hỏi:', error)
                }
            }
        },
        
        async bulkDelete() {
            if (confirm(`Bạn có chắc muốn xóa ${this.selectedQuestions.length} câu hỏi đã chọn?`)) {
                try {
                    // API call to bulk delete
                    this.questions = this.questions.filter(q => !this.selectedQuestions.includes(q.id))
                    this.selectedQuestions = []
                    this.applyFilters()
                    this.calculateStats()
                    this.$toast.success('Đã xóa các câu hỏi đã chọn')
                } catch (error) {
                    console.error('Lỗi khi xóa câu hỏi:', error)
                }
            }
        },
        
        exportQuestions() {
            // Export to Excel
            console.log('Exporting questions to Excel...')
        },
        
        importQuestions() {
            this.showImportModal = true
        },
        
        closeImportModal() {
            this.showImportModal = false
            this.uploadedFile = null
        },
        
        downloadTemplate() {
            // Download Excel template
            console.log('Downloading template...')
        },
        
        handleFileUpload(event) {
            const file = event.target.files[0]
            if (file) {
                this.uploadedFile = file
            }
        },
        
        removeFile() {
            this.uploadedFile = null
            this.$refs.fileInput.value = ''
        },
        
        async processImport() {
            if (!this.uploadedFile) return
            
            try {
                // Process Excel file
                console.log('Processing import...', this.uploadedFile)
                this.closeImportModal()
                this.$toast.success('Import thành công!')
                this.loadQuestions()
            } catch (error) {
                console.error('Lỗi khi import:', error)
                this.$toast.error('Lỗi khi import file')
            }
        },
        
        getDifficultyText(difficulty) {
            const map = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' }
            return map[difficulty] || difficulty
        },
        
        formatDate(date) {
            return new Date(date).toLocaleDateString('vi-VN')
        }
    }
}
</script>

<style scoped>
.question-bank {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.bank-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #eee;
}

.bank-header h1 {
    color: #2c3e50;
    margin: 0;
}

.header-actions {
    display: flex;
    gap: 12px;
}

.btn-export, .btn-import {
    padding: 10px 20px;
    border: 2px solid #27ae60;
    background: white;
    color: #27ae60;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s;
}

.btn-export:hover, .btn-import:hover {
    background: #27ae60;
    color: white;
}

.btn-primary {
    background: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

.btn-primary i, .btn-export i, .btn-import i {
    margin-right: 8px;
}

/* Statistics */
.stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: white;
}

.stat-icon.easy { background: #27ae60; }
.stat-icon.medium { background: #f39c12; }
.stat-icon.hard { background: #e74c3c; }
.stat-icon.total { background: #3498db; }

.stat-info h3 {
    margin: 0;
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
}

.stat-info p {
    margin: 0;
    color: #7f8c8d;
    font-size: 14px;
}

/* Filters */
.bank-filters {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.filter-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.filter-group label {
    font-weight: 500;
    color: #555;
    font-size: 14px;
}

.filter-group select {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    font-size: 14px;
}

.search-row {
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
}

.search-group {
    position: relative;
    flex: 1;
    min-width: 300px;
}

.search-group input {
    width: 100%;
    padding: 12px 40px 12px 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
}

.search-group i {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #999;
}

.view-options {
    display: flex;
    gap: 4px;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
}

.view-btn {
    padding: 10px 12px;
    border: none;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.3s;
}

.view-btn:hover, .view-btn.active {
    background: #3498db;
    color: white;
}

.bulk-actions {
    display: flex;
    gap: 8px;
}

.btn-select-all, .btn-bulk-delete {
    padding: 8px 16px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s;
}

.btn-select-all:hover {
    background: #f8f9fa;
}

.btn-bulk-delete {
    background: #e74c3c;
    color: white;
    border-color: #e74c3c;
}

.btn-bulk-delete:hover {
    background: #c0392b;
}

/* Loading */
.loading {
    text-align: center;
    padding: 60px;
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

/* Empty state */
.no-questions {
    text-align: center;
    padding: 80px 20px;
}

.empty-icon {
    font-size: 64px;
    color: #bdc3c7;
    margin-bottom: 20px;
}

.no-questions h3 {
    color: #2c3e50;
    margin-bottom: 10px;
}

.no-questions p {
    color: #7f8c8d;
    margin-bottom: 30px;
}

/* Questions Grid */
.questions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}

.question-card {
    background: white;
    border-radius: 12px;
    border: 2px solid #eee;
    overflow: hidden;
    transition: all 0.3s;
}

.question-card:hover {
    border-color: #3498db;
    box-shadow: 0 4px 20px rgba(52, 152, 219, 0.1);
    transform: translateY(-2px);
}

.question-card.selected {
    border-color: #3498db;
    background: #f8fcff;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: #f8f9fa;
}

.checkbox-container {
    position: relative;
    cursor: pointer;
}

.checkbox-container input {
    opacity: 0;
    position: absolute;
}

.checkmark {
    width: 18px;
    height: 18px;
    border: 2px solid #ddd;
    border-radius: 3px;
    display: inline-block;
    position: relative;
    transition: all 0.3s;
}

.checkbox-container input:checked + .checkmark {
    background: #3498db;
    border-color: #3498db;
}

.checkbox-container input:checked + .checkmark::after {
    content: '✓';
    position: absolute;
    top: -2px;
    left: 2px;
    color: white;
    font-size: 12px;
}

.question-badges {
    display: flex;
    gap: 8px;
}

.type-badge, .difficulty-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
}

.type-badge.single { background: #e3f2fd; color: #1976d2; }
.type-badge.multiple { background: #f3e5f5; color: #7b1fa2; }

.difficulty-badge.easy { background: #e8f5e8; color: #388e3c; }
.difficulty-badge.medium { background: #fff3e0; color: #f57c00; }
.difficulty-badge.hard { background: #ffebee; color: #d32f2f; }

.card-actions {
    display: flex;
    gap: 4px;
}

.action-btn {
    width: 28px;
    height: 28px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    transition: all 0.3s;
}

.action-btn.preview { background: #e3f2fd; color: #1976d2; }
.action-btn.edit { background: #fff3e0; color: #f57c00; }
.action-btn.duplicate { background: #f3e5f5; color: #7b1fa2; }
.action-btn.delete { background: #ffebee; color: #d32f2f; }

.action-btn:hover {
    transform: scale(1.1);
}

.card-content {
    padding: 16px;
}

.question-title {
    color: #2c3e50;
    margin-bottom: 12px;
    font-size: 16px;
    line-height: 1.4;
}

.question-content {
    color: #555;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 16px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.answers-preview {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px;
}

.answer-preview {
    display: flex;
    align-items: center;
    padding: 6px 0;
    font-size: 13px;
    border-bottom: 1px solid #eee;
}

.answer-preview:last-child {
    border-bottom: none;
}

.answer-preview.correct {
    color: #27ae60;
    font-weight: 500;
}

.answer-label {
    margin-right: 8px;
    font-weight: 500;
    min-width: 20px;
}

.answer-preview i {
    margin-left: auto;
}

.more-answers {
    text-align: center;
    color: #999;
    font-size: 12px;
    padding: 8px 0 4px;
}

.card-footer {
    padding: 12px 16px;
    background: #f8f9fa;
    font-size: 12px;
    color: #666;
    display: flex;
    justify-content: space-between;
}

/* Questions List */
.questions-list {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.list-header, .list-item {
    display: grid;
    grid-template-columns: 40px 2fr 1fr 100px 100px 120px 120px;
    gap: 16px;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #eee;
}

.list-header {
    background: #f8f9fa;
    font-weight: 600;
    color: #555;
    font-size: 14px;
}

.list-item:hover {
    background: #f8f9fa;
}

.list-item.selected {
    background: #f8fcff;
}

.col-title h5 {
    margin: 0 0 4px;
    color: #2c3e50;
    font-size: 14px;
}

.col-title p {
    margin: 0;
    color: #666;
    font-size: 12px;
    line-height: 1.4;
}

/* Pagination */
.pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 30px;
    padding: 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.pagination-info {
    color: #666;
    font-size: 14px;
}

.pagination {
    display: flex;
    align-items: center;
    gap: 8px;
}

.page-btn, .page-number {
    padding: 8px 12px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s;
}

.page-btn:hover, .page-number:hover {
    background: #f8f9fa;
}

.page-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.page-number.active {
    background: #3498db;
    color: white;
    border-color: #3498db;
}

.page-numbers {
    display: flex;
    gap: 4px;
}

/* Modal styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 12px;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
}

.preview-modal {
    max-width: 1000px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #eee;
}

.modal-header h3 {
    margin: 0;
    color: #2c3e50;
}

.btn-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #999;
    padding: 4px;
}

.btn-close:hover {
    color: #333;
}

/* Preview Modal */
.preview-content {
    padding: 24px;
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
}

.question-info {
    display: flex;
    gap: 12px;
}

.course-path {
    color: #666;
    font-size: 14px;
}

.question-display h4 {
    color: #2c3e50;
    margin-bottom: 16px;
    font-size: 20px;
}

.question-display .question-content {
    color: #555;
    line-height: 1.6;
    margin-bottom: 24px;
    font-size: 16px;
}

.answers-display {
    margin-bottom: 24px;
}

.answer-option {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    margin-bottom: 8px;
    border: 2px solid #eee;
    border-radius: 8px;
    transition: all 0.3s;
}

.answer-option.correct {
    border-color: #27ae60;
    background: #f8fff8;
}

.option-label {
    font-weight: 600;
    margin-right: 12px;
    min-width: 24px;
}

.option-text {
    flex: 1;
}

.correct-mark {
    color: #27ae60;
    font-size: 16px;
}

.explanation {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #3498db;
}

.explanation h5 {
    margin: 0 0 8px;
    color: #2c3e50;
}

.explanation p {
    margin: 0;
    color: #555;
    line-height: 1.6;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px 24px;
    border-top: 1px solid #eee;
}

.btn-secondary {
    background: #f8f9fa;
    color: #666;
    border: 1px solid #ddd;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
}

.btn-secondary:hover {
    background: #e9ecef;
}

/* Import Modal */
.import-content {
    padding: 24px;
}

.import-instructions {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 24px;
}

.import-instructions h4 {
    margin-bottom: 12px;
    color: #2c3e50;
}

.import-instructions ol {
    margin-bottom: 16px;
    color: #555;
}

.btn-template {
    background: #27ae60;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}

.btn-template:hover {
    background: #229954;
}

.file-upload {
    margin-bottom: 24px;
}

.upload-area {
    border: 2px dashed #ddd;
    border-radius: 8px;
    padding: 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
}

.upload-area:hover {
    border-color: #3498db;
    background: #f8fcff;
}

.upload-area i {
    font-size: 48px;
    color: #bdc3c7;
    margin-bottom: 16px;
}

.upload-area p {
    margin: 0 0 8px;
    font-size: 16px;
    color: #2c3e50;
}

.upload-area span {
    font-size: 14px;
    color: #7f8c8d;
}

.uploaded-file {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-top: 16px;
}

.uploaded-file i {
    color: #27ae60;
    font-size: 20px;
}

.btn-remove {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    cursor: pointer;
    margin-left: auto;
}

/* Responsive */
@media (max-width: 768px) {
    .bank-header {
        flex-direction: column;
        gap: 16px;
        align-items: stretch;
    }
    
    .header-actions {
        flex-wrap: wrap;
    }
    
    .stats-container {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .filter-row {
        grid-template-columns: 1fr;
    }
    
    .search-row {
        flex-direction: column;
        align-items: stretch;
    }
    
    .search-group {
        min-width: auto;
    }
    
    .questions-grid {
        grid-template-columns: 1fr;
    }
    
    .list-header, .list-item {
        grid-template-columns: 40px 1fr 80px 100px;
        gap: 8px;
    }
    
    .col-course, .col-type, .col-date {
        display: none;
    }
    
    .pagination-container {
        flex-direction: column;
        gap: 16px;
    }
}
</style>
