// Content management service for questions and coding exercises
class ContentService {
    constructor() {
        this.apiUrl = 'http://localhost:8000/api';
    }

    // Question Management
    async getQuestions(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${this.apiUrl}/questions?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching questions:', error);
            return this.getMockQuestions();
        }
    }

    async createQuestion(questionData) {
        try {
            const response = await fetch(`${this.apiUrl}/questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(questionData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error creating question:', error);
            throw error;
        }
    }

    async updateQuestion(id, questionData) {
        try {
            const response = await fetch(`${this.apiUrl}/questions/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(questionData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error updating question:', error);
            throw error;
        }
    }

    async deleteQuestion(id) {
        try {
            const response = await fetch(`${this.apiUrl}/questions/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error deleting question:', error);
            throw error;
        }
    }

    async deleteMultipleQuestions(ids) {
        try {
            const response = await fetch(`${this.apiUrl}/questions/bulk-delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ ids })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error deleting questions:', error);
            throw error;
        }
    }

    // Coding Exercise Management
    async getCodingExercises(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${this.apiUrl}/coding-exercises?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching coding exercises:', error);
            return this.getMockCodingExercises();
        }
    }

    async createCodingExercise(exerciseData) {
        try {
            const response = await fetch(`${this.apiUrl}/coding-exercises`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(exerciseData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error creating coding exercise:', error);
            throw error;
        }
    }

    async updateCodingExercise(id, exerciseData) {
        try {
            const response = await fetch(`${this.apiUrl}/coding-exercises/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(exerciseData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error updating coding exercise:', error);
            throw error;
        }
    }

    async deleteCodingExercise(id) {
        try {
            const response = await fetch(`${this.apiUrl}/coding-exercises/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error deleting coding exercise:', error);
            throw error;
        }
    }

    // Course and Chapter Management
    async getCourses() {
        try {
            const response = await fetch(`${this.apiUrl}/courses`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching courses:', error);
            return this.getMockCourses();
        }
    }

    async getChapters(courseId = null) {
        try {
            const url = courseId 
                ? `${this.apiUrl}/chapters?courseId=${courseId}` 
                : `${this.apiUrl}/chapters`;
            
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching chapters:', error);
            return this.getMockChapters();
        }
    }

    // Import/Export functionality
    async exportQuestions(format = 'xlsx', filters = {}) {
        try {
            const params = new URLSearchParams({ ...filters, format });
            const response = await fetch(`${this.apiUrl}/questions/export?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `questions_export_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting questions:', error);
            throw error;
        }
    }

    async importQuestions(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.apiUrl}/questions/import`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error importing questions:', error);
            throw error;
        }
    }

    async downloadTemplate(type = 'questions') {
        try {
            const response = await fetch(`${this.apiUrl}/${type}/template`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}_template.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading template:', error);
            throw error;
        }
    }

    // Mock data methods (for development/testing)
    getMockQuestions() {
        return [
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
                createdAt: new Date('2024-01-15'),
                updatedAt: new Date('2024-01-15')
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
                createdAt: new Date('2024-01-16'),
                updatedAt: new Date('2024-01-16')
            }
        ];
    }

    getMockCodingExercises() {
        return [
            {
                id: 1,
                title: 'Two Sum',
                description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                language: 'javascript',
                difficulty: 'easy',
                course: 'Algorithm Fundamentals',
                chapter: 'Array Problems',
                courseId: 1,
                chapterId: 1,
                templateCode: `function twoSum(nums, target) {
    // Your code here
    
}

// Test
const nums = [2, 7, 11, 15];
const target = 9;
console.log(twoSum(nums, target));`,
                solutionCode: `function twoSum(nums, target) {
    const map = new Map();
    
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        
        if (map.has(complement)) {
            return [map.get(complement), i];
        }
        
        map.set(nums[i], i);
    }
    
    return [];
}`,
                testCases: [
                    { input: '[2,7,11,15]\n9', expectedOutput: '[0,1]', isHidden: false },
                    { input: '[3,2,4]\n6', expectedOutput: '[1,2]', isHidden: false },
                    { input: '[3,3]\n6', expectedOutput: '[0,1]', isHidden: true }
                ],
                hints: [
                    'Try using a hash map to store the numbers you have seen',
                    'For each number, check if target - number exists in the hash map'
                ],
                timeLimit: 1000,
                memoryLimit: 128,
                createdAt: new Date('2024-01-10'),
                updatedAt: new Date('2024-01-10')
            },
            {
                id: 2,
                title: 'Reverse String',
                description: 'Write a function that reverses a string. The input string is given as an array of characters s.',
                language: 'python',
                difficulty: 'easy',
                course: 'Python Basics',
                chapter: 'String Manipulation',
                courseId: 3,
                chapterId: 5,
                templateCode: `def reverse_string(s):
    """
    Do not return anything, modify s in-place instead.
    """
    # Your code here
    pass

# Test
s = ["h","e","l","l","o"]
reverse_string(s)
print(s)`,
                solutionCode: `def reverse_string(s):
    left, right = 0, len(s) - 1
    
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1`,
                testCases: [
                    { input: '["h","e","l","l","o"]', expectedOutput: '["o","l","l","e","h"]', isHidden: false },
                    { input: '["H","a","n","n","a","h"]', expectedOutput: '["h","a","n","n","a","H"]', isHidden: false }
                ],
                hints: [
                    'Use two pointers approach',
                    'Swap characters from both ends moving towards center'
                ],
                timeLimit: 1000,
                memoryLimit: 128,
                createdAt: new Date('2024-01-12'),
                updatedAt: new Date('2024-01-12')
            }
        ];
    }

    getMockCourses() {
        return [
            { id: 1, title: 'JavaScript Fundamentals', description: 'Learn JavaScript from scratch' },
            { id: 2, title: 'Vue.js Complete Guide', description: 'Master Vue.js framework' },
            { id: 3, title: 'Python for Beginners', description: 'Introduction to Python programming' },
            { id: 4, title: 'Algorithm Fundamentals', description: 'Essential algorithms and data structures' }
        ];
    }

    getMockChapters() {
        return [
            { id: 1, title: 'Variables and Data Types', courseId: 1, order: 1 },
            { id: 2, title: 'Functions and Scope', courseId: 1, order: 2 },
            { id: 3, title: 'Vue Components', courseId: 2, order: 1 },
            { id: 4, title: 'Vue Router', courseId: 2, order: 2 },
            { id: 5, title: 'String Manipulation', courseId: 3, order: 1 },
            { id: 6, title: 'Lists and Dictionaries', courseId: 3, order: 2 },
            { id: 7, title: 'Array Problems', courseId: 4, order: 1 },
            { id: 8, title: 'Tree Algorithms', courseId: 4, order: 2 }
        ];
    }

    // Utility methods
    validateQuestionData(questionData) {
        const errors = [];

        if (!questionData.title || questionData.title.trim().length === 0) {
            errors.push('Title is required');
        }

        if (!questionData.content || questionData.content.trim().length === 0) {
            errors.push('Content is required');
        }

        if (!questionData.courseId) {
            errors.push('Course is required');
        }

        if (!questionData.chapterId) {
            errors.push('Chapter is required');
        }

        if (!questionData.answers || questionData.answers.length < 2) {
            errors.push('At least 2 answers are required');
        }

        const correctAnswers = questionData.answers?.filter(a => a.isCorrect) || [];
        if (correctAnswers.length === 0) {
            errors.push('At least one correct answer is required');
        }

        if (questionData.type === 'single' && correctAnswers.length > 1) {
            errors.push('Single choice questions can have only one correct answer');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    validateCodingExerciseData(exerciseData) {
        const errors = [];

        if (!exerciseData.title || exerciseData.title.trim().length === 0) {
            errors.push('Title is required');
        }

        if (!exerciseData.description || exerciseData.description.trim().length === 0) {
            errors.push('Description is required');
        }

        if (!exerciseData.courseId) {
            errors.push('Course is required');
        }

        if (!exerciseData.chapterId) {
            errors.push('Chapter is required');
        }

        if (!exerciseData.language) {
            errors.push('Programming language is required');
        }

        if (!exerciseData.templateCode || exerciseData.templateCode.trim().length === 0) {
            errors.push('Template code is required');
        }

        if (!exerciseData.testCases || exerciseData.testCases.length === 0) {
            errors.push('At least one test case is required');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    formatDifficulty(difficulty) {
        const map = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' };
        return map[difficulty] || difficulty;
    }

    formatLanguage(language) {
        const map = {
            javascript: 'JavaScript',
            python: 'Python',
            java: 'Java',
            cpp: 'C++',
            csharp: 'C#',
            go: 'Go',
            rust: 'Rust'
        };
        return map[language] || language;
    }
}

// Create singleton instance
const contentService = new ContentService();

export default contentService;
