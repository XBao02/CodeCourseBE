<template>
    <div class="content-creator">
        <div class="creator-header">
            <h1>Soạn Nội Dung Khóa Học: {{ course?.title || 'Chưa chọn khóa học' }}</h1>
            <div class="creator-nav">
                <button 
                    @click="activeTab = 'questions'" 
                    :class="['nav-btn', { active: activeTab === 'questions' }]"
                >
                    <i class="fas fa-question-circle"></i>
                    Câu hỏi trắc nghiệm
                </button>
                <button 
                    @click="activeTab = 'coding'" 
                    :class="['nav-btn', { active: activeTab === 'coding' }]"
                >
                    <i class="fas fa-code"></i>
                    Bài tập Code
                </button>
            </div>
        </div>

        <!-- Tab Câu hỏi trắc nghiệm -->
        <div v-if="activeTab === 'questions'" class="tab-content">
            <div class="content-section">
                <div class="section-header">
                    <h2>Quản lý Câu hỏi Trắc nghiệm</h2>
                    <button @click="showQuestionModal = true" class="btn-primary">
                        <i class="fas fa-plus"></i>
                        Thêm câu hỏi mới
                    </button>
                </div>

                <div class="questions-filter">
                    <div class="filter-group">
                        <label>Khóa học:</label>
                        <select v-model="selectedCourse" @change="loadQuestions">
                            <option value="">Chọn khóa học</option>
                            <option v-for="course in courses" :key="course.id" :value="course.id">
                                {{ course.title }}
                            </option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Chương:</label>
                        <div class="chapter-select-wrapper">
                            <select v-model="selectedChapter" @change="loadQuestions">
                                <option value="">Tất cả chương</option>
                                <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                                    {{ chapter.title }}
                                </option>
                            </select>
                            <button @click="addChapterPrompt" class="btn-add-chapter">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="filter-group">
                        <label>Độ khó:</label>
                        <select v-model="selectedDifficulty" @change="loadQuestions">
                            <option value="">Tất cả</option>
                            <option value="easy">Dễ</option>
                            <option value="medium">Trung bình</option>
                            <option value="hard">Khó</option>
                        </select>
                    </div>
                </div>

                <div class="questions-list">
                    <div v-if="questionsLoading" class="loading">Đang tải câu hỏi...</div>
                    
                    <div v-else-if="questions.length === 0" class="no-content">
                        <p>Chưa có câu hỏi nào. Hãy thêm câu hỏi đầu tiên!</p>
                    </div>

                    <div v-else class="questions-grid">
                        <div v-for="question in questions" :key="question.id" class="question-card">
                            <div class="question-header">
                                <span class="question-type">{{ getQuestionTypeText(question.type) }}</span>
                                <span :class="['difficulty-badge', question.difficulty]">
                                    {{ getDifficultyText(question.difficulty) }}
                                </span>
                            </div>
                            
                            <div class="question-content">
                                <h4>{{ question.title }}</h4>
                                <div class="question-text" v-html="question.content"></div>
                                
                                <div class="answers-preview">
                                    <div v-for="(answer, index) in question.answers" :key="index" 
                                         :class="['answer-item', { correct: answer.isCorrect }]">
                                        <span class="answer-label">{{ String.fromCharCode(65 + index) }}.</span>
                                        {{ answer.text }}
                                        <i v-if="answer.isCorrect" class="fas fa-check correct-icon"></i>
                                    </div>
                                </div>
                            </div>

                            <div class="question-meta">
                                <span>{{ question.course }} - {{ question.chapter }}</span>
                                <span>Tạo: {{ formatDate(question.createdAt) }}</span>
                            </div>

                            <div class="question-actions">
                                <button @click="editQuestion(question)" class="btn-edit">
                                    <i class="fas fa-edit"></i> Sửa
                                </button>
                                <button @click="duplicateQuestion(question)" class="btn-duplicate">
                                    <i class="fas fa-copy"></i> Sao chép
                                </button>
                                <button @click="deleteQuestion(question.id)" class="btn-delete">
                                    <i class="fas fa-trash"></i> Xóa
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab Bài tập Code -->
        <div v-if="activeTab === 'coding'" class="tab-content">
            <div class="content-section">
                <div class="section-header">
                    <h2>Quản lý Bài tập Code</h2>
                    <button @click="showCodingModal = true" class="btn-primary">
                        <i class="fas fa-plus"></i>
                        Tạo bài tập mới
                    </button>
                </div>

                <div class="coding-filter">
                    <div class="filter-group">
                        <label>Khóa học:</label>
                        <select v-model="selectedCodingCourse" @change="loadCodingExercises">
                            <option value="">Chọn khóa học</option>
                            <option v-for="course in courses" :key="course.id" :value="course.id">
                                {{ course.title }}
                            </option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Ngôn ngữ:</label>
                        <select v-model="selectedLanguage" @change="loadCodingExercises">
                            <option value="">Tất cả</option>
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="java">Java</option>
                            <option value="cpp">C++</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Độ khó:</label>
                        <select v-model="selectedCodingDifficulty" @change="loadCodingExercises">
                            <option value="">Tất cả</option>
                            <option value="easy">Dễ</option>
                            <option value="medium">Trung bình</option>
                            <option value="hard">Khó</option>
                        </select>
                    </div>
                </div>

                <div class="coding-list">
                    <div v-if="codingLoading" class="loading">Đang tải bài tập...</div>
                    
                    <div v-else-if="codingExercises.length === 0" class="no-content">
                        <p>Chưa có bài tập code nào. Hãy tạo bài tập đầu tiên!</p>
                    </div>

                    <div v-else class="coding-grid">
                        <div v-for="exercise in codingExercises" :key="exercise.id" class="coding-card">
                            <div class="coding-header">
                                <span class="language-badge" :class="exercise.language">
                                    {{ getLanguageText(exercise.language) }}
                                </span>
                                <span :class="['difficulty-badge', exercise.difficulty]">
                                    {{ getDifficultyText(exercise.difficulty) }}
                                </span>
                            </div>
                            
                            <div class="coding-content">
                                <h4>{{ exercise.title }}</h4>
                                <div class="coding-description" v-html="exercise.description"></div>
                                
                                <div class="coding-preview">
                                    <div class="code-section">
                                        <h5>Template Code:</h5>
                                        <pre><code>{{ exercise.templateCode.substring(0, 100) }}...</code></pre>
                                    </div>
                                    
                                    <div class="test-cases">
                                        <h5>Test Cases: {{ exercise.testCases.length }}</h5>
                                        <div class="test-case-preview">
                                            <span>Input: {{ exercise.testCases[0]?.input }}</span>
                                            <span>Output: {{ exercise.testCases[0]?.expectedOutput }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="coding-meta">
                                <span>{{ exercise.course }} - {{ exercise.chapter }}</span>
                                <span>Tạo: {{ formatDate(exercise.createdAt) }}</span>
                            </div>

                            <div class="coding-actions">
                                <button @click="editCodingExercise(exercise)" class="btn-edit">
                                    <i class="fas fa-edit"></i> Sửa
                                </button>
                                <button @click="testCodingExercise(exercise)" class="btn-test">
                                    <i class="fas fa-play"></i> Test
                                </button>
                                <button @click="duplicateCodingExercise(exercise)" class="btn-duplicate">
                                    <i class="fas fa-copy"></i> Sao chép
                                </button>
                                <button @click="deleteCodingExercise(exercise.id)" class="btn-delete">
                                    <i class="fas fa-trash"></i> Xóa
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal tạo/sửa câu hỏi -->
        <div v-if="showQuestionModal" class="modal-overlay">
            <div class="modal-content large-modal">
                <div class="modal-header">
                    <h3>{{ editingQuestion ? 'Sửa câu hỏi' : 'Tạo câu hỏi mới' }}</h3>
                    <button @click="closeQuestionModal" class="btn-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <form @submit.prevent="saveQuestion" class="question-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Khóa học:</label>
                            <select v-model="questionForm.courseId" required>
                                <option value="">Chọn khóa học</option>
                                <option v-for="course in courses" :key="course.id" :value="course.id">
                                    {{ course.title }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Chương:</label>
                            <select v-model="questionForm.chapterId" required>
                                <option value="">Chọn chương</option>
                                <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                                    {{ chapter.title }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Loại câu hỏi:</label>
                            <select v-model="questionForm.type" required>
                                <option value="single">Một đáp án đúng</option>
                                <option value="multiple">Nhiều đáp án đúng</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Độ khó:</label>
                            <select v-model="questionForm.difficulty" required>
                                <option value="easy">Dễ</option>
                                <option value="medium">Trung bình</option>
                                <option value="hard">Khó</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Tiêu đề câu hỏi:</label>
                        <input type="text" v-model="questionForm.title" required>
                    </div>

                    <div class="form-group">
                        <label>Nội dung câu hỏi:</label>
                        <div class="editor-container">
                            <div class="editor-toolbar">
                                <button type="button" @click="insertCode" class="editor-btn">
                                    <i class="fas fa-code"></i> Code
                                </button>
                                <button type="button" @click="insertImage" class="editor-btn">
                                    <i class="fas fa-image"></i> Hình ảnh
                                </button>
                            </div>
                            <textarea 
                                v-model="questionForm.content" 
                                rows="4" 
                                placeholder="Nhập nội dung câu hỏi..."
                                required
                            ></textarea>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Đáp án:</label>
                        <div class="answers-container">
                            <div v-for="(answer, index) in questionForm.answers" :key="index" class="answer-item">
                                <div class="answer-input">
                                    <span class="answer-label">{{ String.fromCharCode(65 + index) }}.</span>
                                    <input 
                                        type="text" 
                                        v-model="answer.text" 
                                        :placeholder="`Đáp án ${String.fromCharCode(65 + index)}`"
                                        required
                                    >
                                    <label class="correct-checkbox">
                                        <input 
                                            type="checkbox" 
                                            v-model="answer.isCorrect"
                                            @change="validateAnswers"
                                        >
                                        <span class="checkmark"></span>
                                        Đúng
                                    </label>
                                    <button 
                                        type="button" 
                                        @click="removeAnswer(index)" 
                                        class="btn-remove"
                                        v-if="questionForm.answers.length > 2"
                                    >
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                            
                            <button 
                                type="button" 
                                @click="addAnswer" 
                                class="btn-add-answer"
                                v-if="questionForm.answers.length < 6"
                            >
                                <i class="fas fa-plus"></i> Thêm đáp án
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Giải thích (tùy chọn):</label>
                        <textarea 
                            v-model="questionForm.explanation" 
                            rows="3"
                            placeholder="Giải thích tại sao đáp án này đúng..."
                        ></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="button" @click="closeQuestionModal" class="btn-secondary">Hủy</button>
                        <button type="submit" class="btn-primary">
                            {{ editingQuestion ? 'Cập nhật' : 'Tạo câu hỏi' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal tạo/sửa bài tập code -->
        <div v-if="showCodingModal" class="modal-overlay">
            <div class="modal-content extra-large-modal">
                <div class="modal-header">
                    <h3>{{ editingCoding ? 'Sửa bài tập' : 'Tạo bài tập code mới' }}</h3>
                    <button @click="closeCodingModal" class="btn-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <form @submit.prevent="saveCodingExercise" class="coding-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Khóa học:</label>
                            <select v-model="codingForm.courseId" required>
                                <option value="">Chọn khóa học</option>
                                <option v-for="course in courses" :key="course.id" :value="course.id">
                                    {{ course.title }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Chương:</label>
                            <select v-model="codingForm.chapterId" required>
                                <option value="">Chọn chương</option>
                                <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                                    {{ chapter.title }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Ngôn ngữ lập trình:</label>
                            <select v-model="codingForm.language" required>
                                <option value="javascript">JavaScript</option>
                                <option value="python">Python</option>
                                <option value="java">Java</option>
                                <option value="cpp">C++</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Độ khó:</label>
                            <select v-model="codingForm.difficulty" required>
                                <option value="easy">Dễ</option>
                                <option value="medium">Trung bình</option>
                                <option value="hard">Khó</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Tiêu đề bài tập:</label>
                        <input type="text" v-model="codingForm.title" required>
                    </div>

                    <div class="form-group">
                        <label>Mô tả bài tập:</label>
                        <textarea 
                            v-model="codingForm.description" 
                            rows="4"
                            placeholder="Mô tả chi tiết bài tập, yêu cầu, ví dụ..."
                            required
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label>Template Code:</label>
                        <div class="code-editor">
                            <textarea 
                                v-model="codingForm.templateCode" 
                                rows="8"
                                placeholder="// Template code cho học sinh..."
                                class="code-textarea"
                                required
                            ></textarea>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Solution Code:</label>
                        <div class="code-editor">
                            <textarea 
                                v-model="codingForm.solutionCode" 
                                rows="8"
                                placeholder="// Đáp án mẫu..."
                                class="code-textarea"
                                required
                            ></textarea>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Test Cases:</label>
                        <div class="test-cases-container">
                            <div v-for="(testCase, index) in codingForm.testCases" :key="index" class="test-case-item">
                                <div class="test-case-header">
                                    <h5>Test Case {{ index + 1 }}</h5>
                                    <button 
                                        type="button" 
                                        @click="removeTestCase(index)" 
                                        class="btn-remove"
                                        v-if="codingForm.testCases.length > 1"
                                    >
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                                
                                <div class="test-case-inputs">
                                    <div class="input-group">
                                        <label>Input:</label>
                                        <textarea 
                                            v-model="testCase.input" 
                                            rows="2"
                                            placeholder="Input cho test case..."
                                            required
                                        ></textarea>
                                    </div>
                                    
                                    <div class="input-group">
                                        <label>Expected Output:</label>
                                        <textarea 
                                            v-model="testCase.expectedOutput" 
                                            rows="2"
                                            placeholder="Output mong đợi..."
                                            required
                                        ></textarea>
                                    </div>
                                </div>
                                
                                <div class="test-case-options">
                                    <label class="checkbox-label">
                                        <input type="checkbox" v-model="testCase.isHidden">
                                        Test case ẩn (học sinh không thấy)
                                    </label>
                                </div>
                            </div>
                            
                            <button type="button" @click="addTestCase" class="btn-add-test">
                                <i class="fas fa-plus"></i> Thêm Test Case
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Gợi ý (tùy chọn):</label>
                        <textarea 
                            v-model="codingForm.hints" 
                            rows="3"
                            placeholder="Gợi ý giúp học sinh giải bài..."
                        ></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="button" @click="closeCodingModal" class="btn-secondary">Hủy</button>
                        <button type="button" @click="testCodingSolution" class="btn-test">
                            <i class="fas fa-play"></i> Test Solution
                        </button>
                        <button type="submit" class="btn-primary">
                            {{ editingCoding ? 'Cập nhật' : 'Tạo bài tập' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import QuestionBank from './QuestionBank.vue'

export default {
    name: 'ContentCreator',
    components: {
        QuestionBank
    },
    props: {
        course: {
            type: Object,
            default: null
        }
    },
    emits: ['close'],
    data() {
        return {
            activeTab: 'questions',
            
            // Courses and chapters
            courses: [],
            chapters: [],
            
            // Questions tab
            questions: [],
            questionsLoading: false,
            selectedCourse: '',
            selectedChapter: '',
            selectedDifficulty: '',
            showQuestionModal: false,
            editingQuestion: null,
            questionForm: {
                courseId: '',
                chapterId: '',
                type: 'single',
                difficulty: 'easy',
                title: '',
                content: '',
                answers: [
                    { text: '', isCorrect: false },
                    { text: '', isCorrect: false }
                ],
                explanation: ''
            },
            
            // Coding tab
            codingExercises: [],
            codingLoading: false,
            selectedCodingCourse: '',
            selectedLanguage: '',
            selectedCodingDifficulty: '',
            showCodingModal: false,
            editingCoding: null,
            codingForm: {
                courseId: '',
                chapterId: '',
                language: 'javascript',
                difficulty: 'easy',
                title: '',
                description: '',
                templateCode: '',
                solutionCode: '',
                testCases: [
                    { input: '', expectedOutput: '', isHidden: false }
                ],
                hints: ''
            },
            
            // Curriculum state
            curriculumLoading: false,
            sections: [],
            lessonsBySection: {}
        }
    },
    mounted() {
        this.loadCourses()
        this.loadQuestions()
        this.loadCodingExercises()
        if (this.course?.id) {
            this.selectedCourse = this.course.id
            this.fetchCurriculum(this.course.id)
        }
    },
    methods: {
        // Common methods
        async loadCourses() {
            try {
                // Lấy courses thật cho instructor id=2
                const res = await fetch('http://localhost:5000/api/courses?instructor_id=2')
                if (!res.ok) throw new Error('Không thể tải khóa học')
                const data = await res.json()
                this.courses = data
                // Khởi tạo chapters từ sections của khóa học hiện tại (sau khi fetchCurriculum)
            } catch (e) {
                console.error('Lỗi khi tải khóa học:', e)
            }
        },

        async fetchCurriculum(courseId) {
            this.curriculumLoading = true
            try {
                const res = await fetch(`http://localhost:5000/api/courses/${courseId}/curriculum`)
                if (!res.ok) throw new Error('Không thể tải curriculum')
                const sections = await res.json()
                this.sections = sections
                // Map chapters for select boxes
                this.chapters = sections.map(s => ({ id: s.id, title: s.title, courseId }))
                // Build lessonsBySection
                const map = {}
                sections.forEach(s => { map[s.id] = s.lessons || [] })
                this.lessonsBySection = map
            } catch (e) {
                console.error('Lỗi khi tải curriculum:', e)
            } finally {
                this.curriculumLoading = false
            }
        },

        formatDate(date) {
            return new Date(date).toLocaleDateString('vi-VN')
        },

        // Questions methods
        async loadQuestions() {
            this.questionsLoading = true
            try {
                // Mock data - thay bằng API call thực
                setTimeout(() => {
                    this.questions = [
                        {
                            id: 1,
                            title: 'JavaScript Variables',
                            content: 'Cách khai báo biến trong JavaScript là gì?',
                            type: 'single',
                            difficulty: 'easy',
                            course: 'JavaScript Fundamentals',
                            chapter: 'Variables and Data Types',
                            answers: [
                                { text: 'var name = "John"', isCorrect: true },
                                { text: 'variable name = "John"', isCorrect: false },
                                { text: 'string name = "John"', isCorrect: false },
                                { text: 'declare name = "John"', isCorrect: false }
                            ],
                            createdAt: new Date()
                        }
                    ]
                    this.questionsLoading = false
                }, 1000)
            } catch (error) {
                console.error('Lỗi khi tải câu hỏi:', error)
                this.questionsLoading = false
            }
        },

        getQuestionTypeText(type) {
            return type === 'single' ? 'Một đáp án' : 'Nhiều đáp án'
        },

        getDifficultyText(difficulty) {
            const map = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' }
            return map[difficulty] || difficulty
        },

        editQuestion(question) {
            this.editingQuestion = question
            this.questionForm = { ...question }
            this.showQuestionModal = true
        },

        duplicateQuestion(question) {
            const duplicate = { ...question }
            delete duplicate.id
            duplicate.title = `Copy of ${duplicate.title}`
            this.editingQuestion = null
            this.questionForm = duplicate
            this.showQuestionModal = true
        },

        async deleteQuestion(id) {
            if (confirm('Bạn có chắc muốn xóa câu hỏi này?')) {
                try {
                    // API call to delete
                    this.questions = this.questions.filter(q => q.id !== id)
                    this.$toast.success('Đã xóa câu hỏi')
                } catch (error) {
                    console.error('Lỗi khi xóa câu hỏi:', error)
                }
            }
        },

        closeQuestionModal() {
            this.showQuestionModal = false
            this.editingQuestion = null
            this.resetQuestionForm()
        },

        resetQuestionForm() {
            this.questionForm = {
                courseId: '',
                chapterId: '',
                type: 'single',
                difficulty: 'easy',
                title: '',
                content: '',
                answers: [
                    { text: '', isCorrect: false },
                    { text: '', isCorrect: false }
                ],
                explanation: ''
            }
        },

        addAnswer() {
            this.questionForm.answers.push({ text: '', isCorrect: false })
        },

        removeAnswer(index) {
            this.questionForm.answers.splice(index, 1)
        },

        validateAnswers() {
            // Đảm bảo có ít nhất một đáp án đúng
        },

        insertCode() {
            const code = prompt('Nhập code:')
            if (code) {
                this.questionForm.content += `\n\`\`\`\n${code}\n\`\`\`\n`
            }
        },

        insertImage() {
            const url = prompt('Nhập URL hình ảnh:')
            if (url) {
                this.questionForm.content += `\n![Image](${url})\n`
            }
        },

        async saveQuestion() {
            try {
                if (this.editingQuestion) {
                    // Update existing question
                    console.log('Updating question:', this.questionForm)
                } else {
                    // Create new question
                    console.log('Creating question:', this.questionForm)
                }
                
                this.closeQuestionModal()
                this.loadQuestions()
                this.$toast.success('Đã lưu câu hỏi')
            } catch (error) {
                console.error('Lỗi khi lưu câu hỏi:', error)
            }
        },

        // Coding methods
        async loadCodingExercises() {
            this.codingLoading = true
            try {
                // Mock data - thay bằng API call thực
                setTimeout(() => {
                    this.codingExercises = [
                        {
                            id: 1,
                            title: 'Sum Two Numbers',
                            description: 'Write a function that returns the sum of two numbers',
                            language: 'javascript',
                            difficulty: 'easy',
                            course: 'JavaScript Fundamentals',
                            chapter: 'Functions and Scope',
                            templateCode: 'function sum(a, b) {\n  // Your code here\n}',
                            testCases: [
                                { input: '1, 2', expectedOutput: '3' },
                                { input: '5, 10', expectedOutput: '15' }
                            ],
                            createdAt: new Date()
                        }
                    ]
                    this.codingLoading = false
                }, 1000)
            } catch (error) {
                console.error('Lỗi khi tải bài tập code:', error)
                this.codingLoading = false
            }
        },

        getLanguageText(language) {
            const map = {
                javascript: 'JavaScript',
                python: 'Python',
                java: 'Java',
                cpp: 'C++'
            }
            return map[language] || language
        },

        editCodingExercise(exercise) {
            this.editingCoding = exercise
            this.codingForm = { ...exercise }
            this.showCodingModal = true
        },

        duplicateCodingExercise(exercise) {
            const duplicate = { ...exercise }
            delete duplicate.id
            duplicate.title = `Copy of ${duplicate.title}`
            this.editingCoding = null
            this.codingForm = duplicate
            this.showCodingModal = true
        },

        async deleteCodingExercise(id) {
            if (confirm('Bạn có chắc muốn xóa bài tập này?')) {
                try {
                    // API call to delete
                    this.codingExercises = this.codingExercises.filter(e => e.id !== id)
                    this.$toast.success('Đã xóa bài tập')
                } catch (error) {
                    console.error('Lỗi khi xóa bài tập:', error)
                }
            }
        },

        testCodingExercise(exercise) {
            // Open test runner modal
            console.log('Testing exercise:', exercise)
        },

        closeCodingModal() {
            this.showCodingModal = false
            this.editingCoding = null
            this.resetCodingForm()
        },

        resetCodingForm() {
            this.codingForm = {
                courseId: '',
                chapterId: '',
                language: 'javascript',
                difficulty: 'easy',
                title: '',
                description: '',
                templateCode: '',
                solutionCode: '',
                testCases: [
                    { input: '', expectedOutput: '', isHidden: false }
                ],
                hints: ''
            }
        },

        addTestCase() {
            this.codingForm.testCases.push({
                input: '',
                expectedOutput: '',
                isHidden: false
            })
        },

        removeTestCase(index) {
            this.codingForm.testCases.splice(index, 1)
        },

        testCodingSolution() {
            // Test the solution code with test cases
            console.log('Testing solution with test cases')
        },

        async saveCodingExercise() {
            try {
                if (this.editingCoding) {
                    // Update existing exercise
                    console.log('Updating exercise:', this.codingForm)
                } else {
                    // Create new exercise
                    console.log('Creating exercise:', this.codingForm)
                }
                
                this.closeCodingModal()
                this.loadCodingExercises()
                this.$toast.success('Đã lưu bài tập')
            } catch (error) {
                console.error('Lỗi khi lưu bài tập:', error)
            }
        },

        // Methods for handling events from child components
        editQuestionFromBank(question) {
            this.activeTab = 'questions'
            this.editQuestion(question)
        },

        duplicateQuestionFromBank(question) {
            this.activeTab = 'questions'
            this.duplicateQuestion(question)
        },

        async addChapterPrompt() {
            if (!this.selectedCourse) return alert('Chưa chọn khóa học')
            const title = prompt('Nhập tiêu đề chương mới:')
            if (!title) return
            await this.createSection(title)
            // chọn chương vừa tạo nếu có
            const created = this.chapters.find(c => c.title === title)
            if (created) this.selectedChapter = created.id
        },
        async addLessonPrompt() {
            if (!this.selectedChapter) return alert('Chưa chọn chương')
            const title = prompt('Nhập tiêu đề bài học mới:')
            if (!title) return
            await this.createLesson(this.selectedChapter, { title, type: 'video', sortOrder: 0 })
        },
    }
}
</script>

<style scoped>
.content-creator {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.creator-header {
    margin-bottom: 30px;
    border-bottom: 1px solid #eee;
    padding-bottom: 20px;
}

.creator-header h1 {
    color: #2c3e50;
    margin-bottom: 20px;
}

.creator-nav {
    display: flex;
    gap: 10px;
}

.nav-btn {
    padding: 12px 24px;
    border: 2px solid #3498db;
    background: white;
    color: #3498db;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
}

.nav-btn:hover {
    background: #3498db;
    color: white;
}

.nav-btn.active {
    background: #3498db;
    color: white;
}

.nav-btn i {
    margin-right: 8px;
}

.content-section {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.section-header {
    display: flex;
    justify-content: between;
    align-items: center;
    margin-bottom: 24px;
}

.section-header h2 {
    color: #2c3e50;
    margin: 0;
}

.btn-primary {
    background: #3498db;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

.btn-primary i {
    margin-right: 8px;
}

/* Filter sections */
.questions-filter, .coding-filter {
    display: flex;
    gap: 20px;
    margin-bottom: 24px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 200px;
}

.filter-group label {
    font-weight: 500;
    color: #555;
}

.filter-group select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: white;
}

/* Loading and empty states */
.loading {
    text-align: center;
    padding: 40px;
    color: #666;
}

.no-content {
    text-align: center;
    padding: 60px;
    color: #999;
}

.no-content p {
    font-size: 18px;
}

/* Questions grid */
.questions-grid, .coding-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 20px;
}

.question-card, .coding-card {
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 20px;
    background: white;
    transition: all 0.3s;
}

.question-card:hover, .coding-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.question-header, .coding-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.question-type, .language-badge {
    background: #e3f2fd;
    color: #1976d2;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

.language-badge.javascript { background: #fff3e0; color: #f57c00; }
.language-badge.python { background: #e8f5e8; color: #388e3c; }
.language-badge.java { background: #fce4ec; color: #c2185b; }
.language-badge.cpp { background: #f3e5f5; color: #7b1fa2; }

.difficulty-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

.difficulty-badge.easy { background: #e8f5e8; color: #388e3c; }
.difficulty-badge.medium { background: #fff3e0; color: #f57c00; }
.difficulty-badge.hard { background: #ffebee; color: #d32f2f; }

.question-content, .coding-content {
    margin-bottom: 16px;
}

.question-content h4, .coding-content h4 {
    color: #2c3e50;
    margin-bottom: 12px;
}

.question-text, .coding-description {
    color: #555;
    line-height: 1.6;
    margin-bottom: 16px;
}

.answers-preview {
    background: #f8f9fa;
    padding: 12px;
    border-radius: 8px;
}

.answer-item {
    display: flex;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.answer-item:last-child {
    border-bottom: none;
}

.answer-item.correct {
    background: #e8f5e8;
    color: #388e3c;
    padding: 8px 12px;
    border-radius: 6px;
    margin: 4px 0;
}

.answer-label {
    font-weight: 500;
    margin-right: 8px;
    min-width: 20px;
}

.correct-icon {
    margin-left: auto;
    color: #388e3c;
}

.coding-preview {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.code-section, .test-cases {
    background: #f8f9fa;
    padding: 12px;
    border-radius: 8px;
}

.code-section h5, .test-cases h5 {
    margin-bottom: 8px;
    color: #555;
}

.code-section pre {
    background: #2d3748;
    color: #e2e8f0;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
    overflow: hidden;
}

.test-case-preview {
    font-size: 12px;
    color: #666;
}

.test-case-preview span {
    display: block;
    margin-bottom: 4px;
}

.question-meta, .coding-meta {
    font-size: 12px;
    color: #999;
    margin-bottom: 16px;
    border-top: 1px solid #eee;
    padding-top: 12px;
}

.question-meta span, .coding-meta span {
    display: block;
    margin-bottom: 4px;
}

.question-actions, .coding-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.btn-edit, .btn-view, .btn-duplicate, .btn-delete, .btn-test {
    padding: 6px 12px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s;
}

.btn-edit {
    background: #fff3e0;
    color: #f57c00;
}

.btn-edit:hover {
    background: #f57c00;
    color: white;
}

.btn-duplicate {
    background: #e3f2fd;
    color: #1976d2;
}

.btn-duplicate:hover {
    background: #1976d2;
    color: white;
}

.btn-test {
    background: #e8f5e8;
    color: #388e3c;
}

.btn-test:hover {
    background: #388e3c;
    color: white;
}

.btn-delete {
    background: #ffebee;
    color: #d32f2f;
}

.btn-delete:hover {
    background: #d32f2f;
    color: white;
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

.large-modal {
    max-width: 1000px;
}

.extra-large-modal {
    max-width: 1200px;
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

/* Form styles */
.question-form, .coding-form {
    padding: 24px;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.editor-container {
    position: relative;
}

.editor-toolbar {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
}

.editor-btn {
    padding: 6px 12px;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}

.editor-btn:hover {
    background: #e9ecef;
}

.answers-container {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 16px;
    background: #f8f9fa;
}

.answer-item {
    margin-bottom: 12px;
}

.answer-input {
    display: flex;
    align-items: center;
    gap: 12px;
}

.answer-input .answer-label {
    font-weight: 500;
    min-width: 20px;
}

.answer-input input[type="text"] {
    flex: 1;
    margin-bottom: 0;
}

.correct-checkbox {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    white-space: nowrap;
}

.correct-checkbox input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.checkmark {
    font-size: 12px;
    color: #666;
}

.btn-remove {
    background: #ffebee;
    color: #d32f2f;
    border: none;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
}

.btn-remove:hover {
    background: #d32f2f;
    color: white;
}

.btn-add-answer, .btn-add-test {
    background: #e8f5e8;
    color: #388e3c;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
}

.btn-add-answer:hover, .btn-add-test:hover {
    background: #388e3c;
    color: white;
}

.code-editor {
    position: relative;
}

.code-textarea {
    font-family: 'Courier New', monospace;
    background: #2d3748;
    color: #e2e8f0;
    border: none;
    resize: vertical;
}

.test-cases-container {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 16px;
    background: #f8f9fa;
}

.test-case-item {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
}

.test-case-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.test-case-header h5 {
    margin: 0;
    color: #555;
}

.test-case-inputs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 12px;
}

.input-group label {
    margin-bottom: 4px;
    font-size: 12px;
    font-weight: 500;
    color: #666;
}

.test-case-options {
    border-top: 1px solid #eee;
    padding-top: 12px;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 14px;
}

.checkbox-label input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.btn-secondary {
    background: #f8f9fa;
    color: #666;
    border: 1px solid #ddd;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
}

.btn-secondary:hover {
    background: #e9ecef;
}

/* Responsive */
@media (max-width: 768px) {
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .questions-grid, .coding-grid {
        grid-template-columns: 1fr;
    }
    
    .questions-filter, .coding-filter {
        flex-direction: column;
    }
    
    .test-case-inputs {
        grid-template-columns: 1fr;
    }
    
    .coding-preview {
        grid-template-columns: 1fr;
    }
}
</style>
