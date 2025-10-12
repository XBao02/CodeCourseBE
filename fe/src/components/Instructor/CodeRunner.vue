<template>
    <div class="code-runner">
        <div class="runner-header">
            <h1>Code Runner - Test Environment</h1>
            <div class="header-info">
                <span class="language-tag" :class="selectedLanguage">
                    {{ getLanguageDisplay(selectedLanguage) }}
                </span>
                <div class="test-status" :class="testStatus">
                    <i :class="getStatusIcon()"></i>
                    {{ getStatusText() }}
                </div>
            </div>
        </div>

        <div class="runner-layout">
            <!-- Left Panel: Problem Description -->
            <div class="problem-panel">
                <div class="panel-header">
                    <h3>{{ problem.title }}</h3>
                    <div class="problem-meta">
                        <span class="difficulty" :class="problem.difficulty">
                            {{ getDifficultyText(problem.difficulty) }}
                        </span>
                        <span class="time-limit">Time: {{ problem.timeLimit || '1000ms' }}</span>
                        <span class="memory-limit">Memory: {{ problem.memoryLimit || '256MB' }}</span>
                    </div>
                </div>
                
                <div class="problem-content">
                    <div class="description">
                        <h4>Mô tả bài toán</h4>
                        <div v-html="problem.description"></div>
                    </div>
                    
                    <div class="input-output" v-if="problem.inputFormat || problem.outputFormat">
                        <div class="input-format" v-if="problem.inputFormat">
                            <h4>Input</h4>
                            <pre>{{ problem.inputFormat }}</pre>
                        </div>
                        
                        <div class="output-format" v-if="problem.outputFormat">
                            <h4>Output</h4>
                            <pre>{{ problem.outputFormat }}</pre>
                        </div>
                    </div>
                    
                    <div class="examples" v-if="problem.examples && problem.examples.length > 0">
                        <h4>Ví dụ</h4>
                        <div v-for="(example, index) in problem.examples" :key="index" class="example">
                            <div class="example-header">Ví dụ {{ index + 1 }}</div>
                            <div class="example-content">
                                <div class="example-input">
                                    <strong>Input:</strong>
                                    <pre>{{ example.input }}</pre>
                                </div>
                                <div class="example-output">
                                    <strong>Output:</strong>
                                    <pre>{{ example.output }}</pre>
                                </div>
                                <div v-if="example.explanation" class="example-explanation">
                                    <strong>Giải thích:</strong>
                                    <p>{{ example.explanation }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="constraints" v-if="problem.constraints">
                        <h4>Ràng buộc</h4>
                        <ul>
                            <li v-for="constraint in problem.constraints" :key="constraint">
                                {{ constraint }}
                            </li>
                        </ul>
                    </div>
                    
                    <div class="hints" v-if="problem.hints && showHints">
                        <h4>Gợi ý</h4>
                        <div v-for="(hint, index) in problem.hints" :key="index" class="hint">
                            <strong>Gợi ý {{ index + 1 }}:</strong> {{ hint }}
                        </div>
                    </div>
                    
                    <button v-if="problem.hints && !showHints" @click="showHints = true" class="btn-hints">
                        <i class="fas fa-lightbulb"></i>
                        Xem gợi ý
                    </button>
                </div>
            </div>

            <!-- Right Panel: Code Editor and Output -->
            <div class="editor-panel">
                <div class="editor-header">
                    <div class="language-selector">
                        <label>Ngôn ngữ:</label>
                        <select v-model="selectedLanguage" @change="changeLanguage">
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="java">Java</option>
                            <option value="cpp">C++</option>
                        </select>
                    </div>
                    
                    <div class="editor-actions">
                        <button @click="resetCode" class="btn-reset">
                            <i class="fas fa-undo"></i>
                            Reset
                        </button>
                        <button @click="runCode" class="btn-run" :disabled="isRunning">
                            <i class="fas fa-play"></i>
                            {{ isRunning ? 'Đang chạy...' : 'Chạy' }}
                        </button>
                        <button @click="submitCode" class="btn-submit" :disabled="isRunning">
                            <i class="fas fa-check"></i>
                            Submit
                        </button>
                    </div>
                </div>
                
                <div class="code-editor-container">
                    <textarea
                        ref="codeEditor"
                        v-model="userCode"
                        class="code-editor"
                        :placeholder="getCodePlaceholder()"
                        spellcheck="false"
                    ></textarea>
                </div>
                
                <div class="output-tabs">
                    <div class="tab-headers">
                        <button 
                            @click="activeTab = 'output'" 
                            :class="['tab-btn', { active: activeTab === 'output' }]"
                        >
                            <i class="fas fa-terminal"></i>
                            Output
                        </button>
                        <button 
                            @click="activeTab = 'testcases'" 
                            :class="['tab-btn', { active: activeTab === 'testcases' }]"
                        >
                            <i class="fas fa-flask"></i>
                            Test Cases ({{ testResults.length }})
                        </button>
                        <button 
                            @click="activeTab = 'console'" 
                            :class="['tab-btn', { active: activeTab === 'console' }]"
                        >
                            <i class="fas fa-bug"></i>
                            Console
                        </button>
                    </div>
                    
                    <div class="tab-content">
                        <!-- Output Tab -->
                        <div v-if="activeTab === 'output'" class="output-content">
                            <div v-if="!runOutput && !isRunning" class="empty-output">
                                <i class="fas fa-code"></i>
                                <p>Nhấn "Chạy" để xem kết quả</p>
                            </div>
                            
                            <div v-if="isRunning" class="running-output">
                                <div class="spinner"></div>
                                <p>Đang thực thi code...</p>
                            </div>
                            
                            <div v-if="runOutput" class="output-result">
                                <div class="output-header">
                                    <span class="execution-time">Thời gian: {{ runOutput.executionTime }}ms</span>
                                    <span class="memory-usage">Bộ nhớ: {{ runOutput.memoryUsage }}MB</span>
                                </div>
                                
                                <div class="output-body">
                                    <div v-if="runOutput.stdout" class="stdout">
                                        <h5>Output:</h5>
                                        <pre>{{ runOutput.stdout }}</pre>
                                    </div>
                                    
                                    <div v-if="runOutput.stderr" class="stderr">
                                        <h5>Error:</h5>
                                        <pre>{{ runOutput.stderr }}</pre>
                                    </div>
                                    
                                    <div v-if="runOutput.error" class="runtime-error">
                                        <h5>Runtime Error:</h5>
                                        <pre>{{ runOutput.error }}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Test Cases Tab -->
                        <div v-if="activeTab === 'testcases'" class="testcases-content">
                            <div v-if="testResults.length === 0" class="empty-tests">
                                <i class="fas fa-flask"></i>
                                <p>Nhấn "Submit" để chạy test cases</p>
                            </div>
                            
                            <div v-else class="test-results">
                                <div class="test-summary">
                                    <div class="summary-item">
                                        <span class="label">Passed:</span>
                                        <span class="value passed">{{ passedTests }}/{{ testResults.length }}</span>
                                    </div>
                                    <div class="summary-item">
                                        <span class="label">Accuracy:</span>
                                        <span class="value">{{ Math.round((passedTests / testResults.length) * 100) }}%</span>
                                    </div>
                                </div>
                                
                                <div class="test-list">
                                    <div 
                                        v-for="(result, index) in testResults" 
                                        :key="index"
                                        class="test-case"
                                        :class="{ passed: result.passed, failed: !result.passed }"
                                    >
                                        <div class="test-header">
                                            <span class="test-name">Test Case {{ index + 1 }}</span>
                                            <span class="test-status">
                                                <i :class="result.passed ? 'fas fa-check' : 'fas fa-times'"></i>
                                                {{ result.passed ? 'PASSED' : 'FAILED' }}
                                            </span>
                                        </div>
                                        
                                        <div class="test-details">
                                            <div class="test-input">
                                                <strong>Input:</strong>
                                                <pre>{{ result.input }}</pre>
                                            </div>
                                            
                                            <div class="test-expected">
                                                <strong>Expected:</strong>
                                                <pre>{{ result.expected }}</pre>
                                            </div>
                                            
                                            <div class="test-actual">
                                                <strong>Actual:</strong>
                                                <pre>{{ result.actual }}</pre>
                                            </div>
                                            
                                            <div v-if="result.error" class="test-error">
                                                <strong>Error:</strong>
                                                <pre>{{ result.error }}</pre>
                                            </div>
                                            
                                            <div class="test-meta">
                                                <span>Time: {{ result.executionTime }}ms</span>
                                                <span>Memory: {{ result.memoryUsage }}MB</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Console Tab -->
                        <div v-if="activeTab === 'console'" class="console-content">
                            <div class="console-input">
                                <label>Custom Input:</label>
                                <textarea 
                                    v-model="customInput" 
                                    placeholder="Nhập input tùy chỉnh..."
                                    rows="3"
                                ></textarea>
                                <button @click="runWithCustomInput" class="btn-run-custom">
                                    <i class="fas fa-play"></i>
                                    Run với Custom Input
                                </button>
                            </div>
                            
                            <div class="console-output">
                                <div v-for="(log, index) in consoleLogs" :key="index" class="console-log">
                                    <span class="log-time">{{ log.timestamp }}</span>
                                    <span class="log-type" :class="log.type">{{ log.type.toUpperCase() }}</span>
                                    <span class="log-message">{{ log.message }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results Modal -->
        <div v-if="showResultsModal" class="modal-overlay">
            <div class="modal-content results-modal">
                <div class="modal-header">
                    <h3>Kết quả Submit</h3>
                    <button @click="closeResultsModal" class="btn-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="results-content">
                    <div class="results-summary">
                        <div class="summary-card" :class="allTestsPassed ? 'success' : 'failure'">
                            <div class="summary-icon">
                                <i :class="allTestsPassed ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
                            </div>
                            <div class="summary-info">
                                <h4>{{ allTestsPassed ? 'Accepted' : 'Wrong Answer' }}</h4>
                                <p>{{ passedTests }}/{{ testResults.length }} test cases passed</p>
                            </div>
                            <div class="summary-score">
                                <span class="score">{{ Math.round((passedTests / testResults.length) * 100) }}%</span>
                            </div>
                        </div>
                        
                        <div class="performance-stats">
                            <div class="stat">
                                <span class="stat-label">Avg Time:</span>
                                <span class="stat-value">{{ averageTime }}ms</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Avg Memory:</span>
                                <span class="stat-value">{{ averageMemory }}MB</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Language:</span>
                                <span class="stat-value">{{ getLanguageDisplay(selectedLanguage) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="modal-actions">
                    <button @click="closeResultsModal" class="btn-secondary">Đóng</button>
                    <button v-if="!allTestsPassed" @click="tryAgain" class="btn-primary">Thử lại</button>
                    <button v-if="allTestsPassed" @click="nextProblem" class="btn-success">Bài tiếp theo</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import codeExecutionService from '../../services/codeExecutionService.js'

export default {
    name: 'CodeRunner',
    props: {
        problem: {
            type: Object,
            default: () => ({
                id: 1,
                title: 'Two Sum',
                difficulty: 'easy',
                description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                inputFormat: 'Line 1: Array of integers\nLine 2: Target integer',
                outputFormat: 'Array of two indices',
                examples: [
                    {
                        input: '[2,7,11,15]\n9',
                        output: '[0,1]',
                        explanation: 'nums[0] + nums[1] = 2 + 7 = 9'
                    }
                ],
                constraints: [
                    '2 ≤ nums.length ≤ 10^4',
                    '-10^9 ≤ nums[i] ≤ 10^9',
                    '-10^9 ≤ target ≤ 10^9'
                ],
                hints: [
                    'Try using a hash map to store the numbers you have seen',
                    'For each number, check if target - number exists in the hash map'
                ],
                testCases: [
                    { input: '[2,7,11,15]\n9', expected: '[0,1]', isHidden: false },
                    { input: '[3,2,4]\n6', expected: '[1,2]', isHidden: false },
                    { input: '[3,3]\n6', expected: '[0,1]', isHidden: true }
                ],
                templates: {
                    javascript: `function twoSum(nums, target) {
    // Your code here
    
}

// Test
const nums = JSON.parse(process.argv[2]);
const target = parseInt(process.argv[3]);
console.log(JSON.stringify(twoSum(nums, target)));`,
                    python: `def two_sum(nums, target):
    # Your code here
    pass

# Test
import sys
import json
nums = json.loads(sys.argv[1])
target = int(sys.argv[2])
print(json.dumps(two_sum(nums, target)))`,
                    java: `public class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Your code here
        return new int[]{};
    }
    
    public static void main(String[] args) {
        // Test code here
    }
}`,
                    cpp: `#include <vector>
#include <iostream>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Your code here
        return {};
    }
};

int main() {
    // Test code here
    return 0;
}`
                }
            })
        }
    },
    data() {
        return {
            selectedLanguage: 'javascript',
            userCode: '',
            isRunning: false,
            runOutput: null,
            testResults: [],
            activeTab: 'output',
            customInput: '',
            consoleLogs: [],
            showHints: false,
            showResultsModal: false,
            testStatus: 'idle' // idle, running, passed, failed
        }
    },
    computed: {
        passedTests() {
            return this.testResults.filter(t => t.passed).length
        },
        
        allTestsPassed() {
            return this.testResults.length > 0 && this.passedTests === this.testResults.length
        },
        
        averageTime() {
            if (this.testResults.length === 0) return 0
            const total = this.testResults.reduce((sum, t) => sum + (t.executionTime || 0), 0)
            return Math.round(total / this.testResults.length)
        },
        
        averageMemory() {
            if (this.testResults.length === 0) return 0
            const total = this.testResults.reduce((sum, t) => sum + (t.memoryUsage || 0), 0)
            return Math.round(total / this.testResults.length * 100) / 100
        }
    },
    mounted() {
        this.initializeCode()
        this.addToConsole('info', 'Code Runner initialized')
    },
    methods: {
        initializeCode() {
            this.userCode = this.problem.templates[this.selectedLanguage] || ''
        },
        
        changeLanguage() {
            this.userCode = this.problem.templates[this.selectedLanguage] || ''
            this.runOutput = null
            this.testResults = []
            this.addToConsole('info', `Switched to ${this.getLanguageDisplay(this.selectedLanguage)}`)
        },
        
        resetCode() {
            this.userCode = this.problem.templates[this.selectedLanguage] || ''
            this.runOutput = null
            this.testResults = []
            this.addToConsole('info', 'Code reset to template')
        },
        
        async runCode() {
            this.isRunning = true
            this.runOutput = null
            this.activeTab = 'output'
            
            try {
                this.addToConsole('info', 'Running code...')
                
                // Simulate API call to run code
                const result = await this.executeCode(this.userCode, this.customInput || '')
                
                this.runOutput = result
                this.addToConsole('success', `Code executed in ${result.executionTime}ms`)
                
            } catch (error) {
                this.runOutput = {
                    error: error.message,
                    executionTime: 0,
                    memoryUsage: 0
                }
                this.addToConsole('error', `Execution failed: ${error.message}`)
            } finally {
                this.isRunning = false
            }
        },
        
        async submitCode() {
            this.isRunning = true
            this.testResults = []
            this.testStatus = 'running'
            this.activeTab = 'testcases'
            
            try {
                this.addToConsole('info', 'Running test cases...')
                
                // Run all test cases
                for (let i = 0; i < this.problem.testCases.length; i++) {
                    const testCase = this.problem.testCases[i]
                    const result = await this.executeCode(this.userCode, testCase.input)
                    
                    const testResult = {
                        input: testCase.input,
                        expected: testCase.expected,
                        actual: result.stdout || result.error || '',
                        passed: this.compareOutputs(result.stdout, testCase.expected),
                        executionTime: result.executionTime,
                        memoryUsage: result.memoryUsage,
                        error: result.error
                    }
                    
                    this.testResults.push(testResult)
                }
                
                this.testStatus = this.allTestsPassed ? 'passed' : 'failed'
                this.addToConsole('info', `Test completed: ${this.passedTests}/${this.testResults.length} passed`)
                
                // Show results modal
                setTimeout(() => {
                    this.showResultsModal = true
                }, 500)
                
            } catch (error) {
                this.testStatus = 'failed'
                this.addToConsole('error', `Test execution failed: ${error.message}`)
            } finally {
                this.isRunning = false
            }
        },
        
        async runWithCustomInput() {
            this.activeTab = 'console'
            try {
                this.addToConsole('info', 'Running with custom input...')
                const result = await this.executeCode(this.userCode, this.customInput)
                
                this.addToConsole('output', `Output: ${result.stdout}`)
                if (result.stderr) {
                    this.addToConsole('error', `Error: ${result.stderr}`)
                }
                
            } catch (error) {
                this.addToConsole('error', `Execution failed: ${error.message}`)
            }
        },
        
        async executeCode(code, input) {
            try {
                // Use the code execution service
                const result = await codeExecutionService.executeCode(
                    code,
                    this.selectedLanguage,
                    input,
                    this.problem.timeLimit || 5000,
                    this.problem.memoryLimit || 128
                );
                
                return {
                    stdout: result.stdout || '',
                    stderr: result.stderr || '',
                    error: result.error || '',
                    executionTime: result.executionTime || 0,
                    memoryUsage: result.memoryUsage || 0
                };
            } catch (error) {
                // Fallback to mock execution for demo
                return this.mockExecuteCode(code, input);
            }
        },
        
        async mockExecuteCode(code, input) {
            // Simulate code execution - this is for demo purposes
            return new Promise((resolve) => {
                setTimeout(() => {
                    try {
                        // Mock execution result
                        const mockResult = {
                            stdout: this.mockExecute(code, input),
                            stderr: '',
                            error: '',
                            executionTime: Math.random() * 100 + 50,
                            memoryUsage: Math.random() * 10 + 5
                        }
                        resolve(mockResult)
                    } catch (error) {
                        resolve({
                            stdout: '',
                            stderr: '',
                            error: error.message,
                            executionTime: 0,
                            memoryUsage: 0
                        })
                    }
                }, 1000 + Math.random() * 1000)
            })
        },
        
        mockExecute(code, input) {
            // Simple mock execution for demo
            if (this.selectedLanguage === 'javascript' && input.includes('[2,7,11,15]')) {
                return '[0,1]'
            }
            if (this.selectedLanguage === 'javascript' && input.includes('[3,2,4]')) {
                return '[1,2]'
            }
            if (this.selectedLanguage === 'javascript' && input.includes('[3,3]')) {
                return '[0,1]'
            }
            return 'Mock output for: ' + input.substring(0, 20)
        },
        
        compareOutputs(actual, expected) {
            if (!actual || !expected) return false
            return actual.trim() === expected.trim()
        },
        
        addToConsole(type, message) {
            this.consoleLogs.push({
                type,
                message,
                timestamp: new Date().toLocaleTimeString()
            })
            
            // Keep only last 50 logs
            if (this.consoleLogs.length > 50) {
                this.consoleLogs = this.consoleLogs.slice(-50)
            }
        },
        
        closeResultsModal() {
            this.showResultsModal = false
        },
        
        tryAgain() {
            this.showResultsModal = false
            this.testResults = []
            this.testStatus = 'idle'
            this.activeTab = 'output'
        },
        
        nextProblem() {
            this.$emit('next-problem')
            this.showResultsModal = false
        },
        
        getLanguageDisplay(lang) {
            const map = {
                javascript: 'JavaScript',
                python: 'Python',
                java: 'Java',
                cpp: 'C++'
            }
            return map[lang] || lang
        },
        
        getDifficultyText(difficulty) {
            const map = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' }
            return map[difficulty] || difficulty
        },
        
        getCodePlaceholder() {
            return `Viết code ${this.getLanguageDisplay(this.selectedLanguage)} của bạn ở đây...`
        },
        
        getStatusIcon() {
            const icons = {
                idle: 'fas fa-clock',
                running: 'fas fa-spinner fa-spin',
                passed: 'fas fa-check-circle',
                failed: 'fas fa-times-circle'
            }
            return icons[this.testStatus] || icons.idle
        },
        
        getStatusText() {
            const texts = {
                idle: 'Chưa test',
                running: 'Đang test...',
                passed: 'Tất cả test passed',
                failed: 'Có test failed'
            }
            return texts[this.testStatus] || texts.idle
        }
    }
}
</script>

<style scoped>
.code-runner {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f5f5f5;
}

.runner-header {
    background: white;
    padding: 16px 24px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.runner-header h1 {
    margin: 0;
    color: #2c3e50;
    font-size: 24px;
}

.header-info {
    display: flex;
    align-items: center;
    gap: 16px;
}

.language-tag {
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
}

.language-tag.javascript { background: #fff3e0; color: #f57c00; }
.language-tag.python { background: #e8f5e8; color: #388e3c; }
.language-tag.java { background: #fce4ec; color: #c2185b; }
.language-tag.cpp { background: #f3e5f5; color: #7b1fa2; }

.test-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
}

.test-status.idle { background: #f5f5f5; color: #666; }
.test-status.running { background: #e3f2fd; color: #1976d2; }
.test-status.passed { background: #e8f5e8; color: #388e3c; }
.test-status.failed { background: #ffebee; color: #d32f2f; }

.runner-layout {
    display: grid;
    grid-template-columns: 400px 1fr;
    height: calc(100vh - 80px);
    gap: 1px;
    background: #e0e0e0;
}

/* Problem Panel */
.problem-panel {
    background: white;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.panel-header {
    padding: 20px;
    border-bottom: 1px solid #e0e0e0;
}

.panel-header h3 {
    margin: 0 0 12px;
    color: #2c3e50;
    font-size: 18px;
}

.problem-meta {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.problem-meta span {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
}

.difficulty.easy { background: #e8f5e8; color: #388e3c; }
.difficulty.medium { background: #fff3e0; color: #f57c00; }
.difficulty.hard { background: #ffebee; color: #d32f2f; }

.time-limit, .memory-limit {
    background: #f5f5f5;
    color: #666;
}

.problem-content {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.problem-content h4 {
    color: #2c3e50;
    margin: 0 0 12px;
    font-size: 16px;
}

.description {
    margin-bottom: 24px;
    line-height: 1.6;
    color: #555;
}

.input-output {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
}

.input-format, .output-format {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #3498db;
}

.examples {
    margin-bottom: 24px;
}

.example {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    border-left: 4px solid #27ae60;
}

.example-header {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 12px;
}

.example-content > div {
    margin-bottom: 12px;
}

.example-content pre {
    background: white;
    padding: 8px;
    border-radius: 4px;
    margin: 4px 0;
    font-size: 13px;
    border: 1px solid #e0e0e0;
}

.constraints ul {
    margin: 0;
    padding-left: 20px;
    color: #555;
}

.constraints li {
    margin-bottom: 8px;
}

.hints {
    background: #fff8e1;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
}

.hint {
    margin-bottom: 8px;
    color: #f57c00;
}

.btn-hints {
    background: #ffc107;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
}

.btn-hints:hover {
    background: #ffb300;
}

/* Editor Panel */
.editor-panel {
    background: white;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
}

.language-selector {
    display: flex;
    align-items: center;
    gap: 8px;
}

.language-selector label {
    font-weight: 500;
    color: #555;
}

.language-selector select {
    padding: 6px 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
}

.editor-actions {
    display: flex;
    gap: 8px;
}

.btn-reset, .btn-run, .btn-submit {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.3s;
}

.btn-reset {
    background: #f5f5f5;
    color: #666;
}

.btn-reset:hover {
    background: #eeeeee;
}

.btn-run {
    background: #4caf50;
    color: white;
}

.btn-run:hover:not(:disabled) {
    background: #45a049;
}

.btn-submit {
    background: #2196f3;
    color: white;
}

.btn-submit:hover:not(:disabled) {
    background: #1976d2;
}

.btn-run:disabled, .btn-submit:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.code-editor-container {
    flex: 1;
    position: relative;
    min-height: 300px;
}

.code-editor {
    width: 100%;
    height: 100%;
    border: none;
    padding: 20px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.5;
    background: #1e1e1e;
    color: #d4d4d4;
    resize: none;
    outline: none;
}

.code-editor::placeholder {
    color: #666;
}

.output-tabs {
    height: 300px;
    display: flex;
    flex-direction: column;
    border-top: 1px solid #e0e0e0;
}

.tab-headers {
    display: flex;
    background: #f8f9fa;
    border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
    padding: 12px 16px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-weight: 500;
    color: #666;
    transition: all 0.3s;
}

.tab-btn:hover {
    background: #e9ecef;
}

.tab-btn.active {
    background: white;
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
}

.tab-btn i {
    margin-right: 6px;
}

.tab-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

/* Output Content */
.empty-output, .running-output {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #999;
}

.empty-output i, .running-output i {
    font-size: 48px;
    margin-bottom: 16px;
}

.running-output .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.output-result {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
}

.output-header {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
    font-size: 12px;
    color: #666;
}

.execution-time, .memory-usage {
    background: white;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
}

.output-body h5 {
    margin: 0 0 8px;
    color: #2c3e50;
    font-size: 14px;
}

.stdout pre, .stderr pre, .runtime-error pre {
    background: #2d3748;
    color: #e2e8f0;
    padding: 12px;
    border-radius: 6px;
    margin: 0;
    font-size: 13px;
    line-height: 1.4;
    overflow-x: auto;
}

.stderr, .runtime-error {
    margin-top: 12px;
}

.stderr h5, .runtime-error h5 {
    color: #e74c3c;
}

/* Test Cases Content */
.empty-tests {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #999;
}

.empty-tests i {
    font-size: 48px;
    margin-bottom: 16px;
}

.test-summary {
    display: flex;
    gap: 24px;
    margin-bottom: 20px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
}

.summary-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.summary-item .label {
    font-size: 12px;
    color: #666;
    font-weight: 500;
}

.summary-item .value {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
}

.summary-item .value.passed {
    color: #27ae60;
}

.test-case {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    margin-bottom: 12px;
    overflow: hidden;
}

.test-case.passed {
    border-color: #27ae60;
}

.test-case.failed {
    border-color: #e74c3c;
}

.test-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #f8f9fa;
}

.test-case.passed .test-header {
    background: #f8fff8;
}

.test-case.failed .test-header {
    background: #fff8f8;
}

.test-name {
    font-weight: 600;
    color: #2c3e50;
}

.test-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
}

.test-case.passed .test-status {
    color: #27ae60;
}

.test-case.failed .test-status {
    color: #e74c3c;
}

.test-details {
    padding: 16px;
}

.test-details > div {
    margin-bottom: 12px;
}

.test-details strong {
    display: block;
    margin-bottom: 4px;
    color: #2c3e50;
    font-size: 14px;
}

.test-details pre {
    background: #f8f9fa;
    padding: 8px;
    border-radius: 4px;
    margin: 0;
    font-size: 13px;
    border: 1px solid #e0e0e0;
    overflow-x: auto;
}

.test-error pre {
    background: #fff5f5;
    border-color: #feb2b2;
    color: #c53030;
}

.test-meta {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: #666;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #e0e0e0;
}

/* Console Content */
.console-input {
    margin-bottom: 20px;
}

.console-input label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #555;
}

.console-input textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-family: monospace;
    font-size: 13px;
    resize: vertical;
}

.btn-run-custom {
    background: #ff9800;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    margin-top: 8px;
}

.btn-run-custom:hover {
    background: #f57c00;
}

.console-output {
    background: #1e1e1e;
    border-radius: 6px;
    padding: 12px;
    height: 200px;
    overflow-y: auto;
}

.console-log {
    display: flex;
    gap: 8px;
    margin-bottom: 4px;
    font-family: monospace;
    font-size: 12px;
    line-height: 1.4;
}

.log-time {
    color: #888;
    min-width: 60px;
}

.log-type {
    min-width: 50px;
    font-weight: 600;
}

.log-type.info { color: #3498db; }
.log-type.success { color: #27ae60; }
.log-type.error { color: #e74c3c; }
.log-type.output { color: #f39c12; }

.log-message {
    color: #e2e8f0;
    flex: 1;
}

/* Results Modal */
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
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
}

.results-modal {
    max-width: 700px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #e0e0e0;
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

.results-content {
    padding: 24px;
}

.summary-card {
    display: flex;
    align-items: center;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 24px;
}

.summary-card.success {
    background: linear-gradient(135deg, #e8f5e8 0%, #f8fff8 100%);
    border: 2px solid #27ae60;
}

.summary-card.failure {
    background: linear-gradient(135deg, #ffebee 0%, #fff8f8 100%);
    border: 2px solid #e74c3c;
}

.summary-icon {
    font-size: 48px;
    margin-right: 20px;
}

.summary-card.success .summary-icon {
    color: #27ae60;
}

.summary-card.failure .summary-icon {
    color: #e74c3c;
}

.summary-info {
    flex: 1;
}

.summary-info h4 {
    margin: 0 0 8px;
    font-size: 24px;
    color: #2c3e50;
}

.summary-info p {
    margin: 0;
    color: #666;
}

.summary-score {
    font-size: 32px;
    font-weight: bold;
    color: #2c3e50;
}

.performance-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
}

.stat {
    text-align: center;
}

.stat-label {
    display: block;
    font-size: 12px;
    color: #666;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px 24px;
    border-top: 1px solid #e0e0e0;
}

.btn-secondary, .btn-primary, .btn-success {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s;
}

.btn-secondary {
    background: #f5f5f5;
    color: #666;
}

.btn-secondary:hover {
    background: #eeeeee;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
}

.btn-success {
    background: #27ae60;
    color: white;
}

.btn-success:hover {
    background: #229954;
}

/* Responsive */
@media (max-width: 1024px) {
    .runner-layout {
        grid-template-columns: 1fr;
        grid-template-rows: 300px 1fr;
    }
    
    .problem-panel {
        overflow-y: auto;
    }
    
    .input-output {
        grid-template-columns: 1fr;
    }
    
    .performance-stats {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .runner-header {
        flex-direction: column;
        gap: 12px;
        align-items: stretch;
    }
    
    .editor-header {
        flex-direction: column;
        gap: 12px;
        align-items: stretch;
    }
    
    .editor-actions {
        justify-content: center;
    }
    
    .tab-headers {
        overflow-x: auto;
    }
    
    .test-summary {
        flex-direction: column;
        gap: 12px;
    }
    
    .summary-card {
        flex-direction: column;
        text-align: center;
    }
    
    .summary-icon {
        margin-right: 0;
        margin-bottom: 12px;
    }
}
</style>
