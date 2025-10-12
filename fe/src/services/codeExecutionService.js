// Code execution service for running user code
class CodeExecutionService {
    constructor() {
        this.apiUrl = 'http://localhost:8000/api'; // Backend API URL
    }

    /**
     * Execute code with given input
     * @param {string} code - User's source code
     * @param {string} language - Programming language (javascript, python, java, cpp)
     * @param {string} input - Input for the code
     * @param {number} timeLimit - Time limit in milliseconds
     * @param {number} memoryLimit - Memory limit in MB
     * @returns {Promise<Object>} Execution result
     */
    async executeCode(code, language, input = '', timeLimit = 5000, memoryLimit = 128) {
        try {
            const response = await fetch(`${this.apiUrl}/code/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    code,
                    language,
                    input,
                    timeLimit,
                    memoryLimit
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Code execution error:', error);
            throw error;
        }
    }

    /**
     * Run multiple test cases for a problem
     * @param {string} code - User's source code
     * @param {string} language - Programming language
     * @param {Array} testCases - Array of test cases with input and expected output
     * @returns {Promise<Array>} Array of test results
     */
    async runTestCases(code, language, testCases) {
        try {
            const response = await fetch(`${this.apiUrl}/code/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    code,
                    language,
                    testCases
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const results = await response.json();
            return results;
        } catch (error) {
            console.error('Test execution error:', error);
            throw error;
        }
    }

    /**
     * Submit solution for a problem
     * @param {number} problemId - Problem ID
     * @param {string} code - User's source code
     * @param {string} language - Programming language
     * @returns {Promise<Object>} Submission result
     */
    async submitSolution(problemId, code, language) {
        try {
            const response = await fetch(`${this.apiUrl}/submissions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    problemId,
                    code,
                    language
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Submission error:', error);
            throw error;
        }
    }

    /**
     * Get supported languages
     * @returns {Promise<Array>} Array of supported languages
     */
    async getSupportedLanguages() {
        try {
            const response = await fetch(`${this.apiUrl}/code/languages`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const languages = await response.json();
            return languages;
        } catch (error) {
            console.error('Error fetching languages:', error);
            return this.getDefaultLanguages();
        }
    }

    /**
     * Get default language configurations
     * @returns {Array} Default languages
     */
    getDefaultLanguages() {
        return [
            {
                id: 'javascript',
                name: 'JavaScript',
                version: 'Node.js 18',
                extension: 'js',
                template: 'function solution() {\n    // Your code here\n}\n\nconsole.log(solution());'
            },
            {
                id: 'python',
                name: 'Python',
                version: '3.9',
                extension: 'py',
                template: 'def solution():\n    # Your code here\n    pass\n\nprint(solution())'
            },
            {
                id: 'java',
                name: 'Java',
                version: '11',
                extension: 'java',
                template: 'public class Solution {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}'
            },
            {
                id: 'cpp',
                name: 'C++',
                version: '17',
                extension: 'cpp',
                template: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    return 0;\n}'
            }
        ];
    }

    /**
     * Format execution time
     * @param {number} timeMs - Time in milliseconds
     * @returns {string} Formatted time string
     */
    formatExecutionTime(timeMs) {
        if (timeMs < 1000) {
            return `${timeMs}ms`;
        } else {
            return `${(timeMs / 1000).toFixed(2)}s`;
        }
    }

    /**
     * Format memory usage
     * @param {number} memoryMB - Memory in MB
     * @returns {string} Formatted memory string
     */
    formatMemoryUsage(memoryMB) {
        if (memoryMB < 1) {
            return `${(memoryMB * 1024).toFixed(0)}KB`;
        } else {
            return `${memoryMB.toFixed(2)}MB`;
        }
    }

    /**
     * Check if code execution result indicates success
     * @param {Object} result - Execution result
     * @returns {boolean} True if successful
     */
    isExecutionSuccessful(result) {
        return result && !result.error && !result.stderr && result.stdout !== null;
    }

    /**
     * Compare outputs for test case validation
     * @param {string} actual - Actual output
     * @param {string} expected - Expected output
     * @param {boolean} strictMode - Whether to use strict comparison
     * @returns {boolean} True if outputs match
     */
    compareOutputs(actual, expected, strictMode = false) {
        if (!actual || !expected) return false;

        const normalizeOutput = (output) => {
            return output
                .toString()
                .trim()
                .replace(/\r\n/g, '\n')
                .replace(/\s+/g, ' ')
                .toLowerCase();
        };

        if (strictMode) {
            return actual.trim() === expected.trim();
        } else {
            return normalizeOutput(actual) === normalizeOutput(expected);
        }
    }

    /**
     * Get code templates for different problem types
     * @param {string} language - Programming language
     * @param {string} problemType - Type of problem (algorithm, data-structure, etc.)
     * @returns {string} Code template
     */
    getCodeTemplate(language, problemType = 'general') {
        const templates = {
            javascript: {
                general: '// Write your solution here\nfunction solution() {\n    // Your code here\n}\n\nconsole.log(solution());',
                array: '// Array manipulation problem\nfunction solution(arr) {\n    // Your code here\n    return arr;\n}',
                string: '// String manipulation problem\nfunction solution(str) {\n    // Your code here\n    return str;\n}',
                math: '// Math problem\nfunction solution(n) {\n    // Your code here\n    return n;\n}'
            },
            python: {
                general: '# Write your solution here\ndef solution():\n    # Your code here\n    pass\n\nprint(solution())',
                array: '# Array manipulation problem\ndef solution(arr):\n    # Your code here\n    return arr',
                string: '# String manipulation problem\ndef solution(s):\n    # Your code here\n    return s',
                math: '# Math problem\ndef solution(n):\n    # Your code here\n    return n'
            },
            java: {
                general: 'public class Solution {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}',
                array: 'public class Solution {\n    public int[] solution(int[] arr) {\n        // Your code here\n        return arr;\n    }\n}',
                string: 'public class Solution {\n    public String solution(String s) {\n        // Your code here\n        return s;\n    }\n}'
            },
            cpp: {
                general: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    return 0;\n}',
                array: '#include <vector>\n#include <iostream>\nusing namespace std;\n\nvector<int> solution(vector<int>& arr) {\n    // Your code here\n    return arr;\n}',
                string: '#include <string>\n#include <iostream>\nusing namespace std;\n\nstring solution(string s) {\n    // Your code here\n    return s;\n}'
            }
        };

        return templates[language]?.[problemType] || templates[language]?.general || '';
    }

    /**
     * Validate code syntax (basic check)
     * @param {string} code - Source code
     * @param {string} language - Programming language
     * @returns {Object} Validation result
     */
    validateCodeSyntax(code, language) {
        const result = { isValid: true, errors: [] };

        if (!code || code.trim().length === 0) {
            result.isValid = false;
            result.errors.push('Code cannot be empty');
            return result;
        }

        // Basic syntax checks based on language
        switch (language) {
            case 'javascript':
                // Check for basic JavaScript syntax
                if (!code.includes('{') || !code.includes('}')) {
                    result.errors.push('Missing curly braces');
                }
                break;
            case 'python':
                // Check for basic Python syntax
                if (code.includes('def ') && !code.includes(':')) {
                    result.errors.push('Missing colon after function definition');
                }
                break;
            case 'java':
                // Check for basic Java syntax
                if (!code.includes('class ')) {
                    result.errors.push('Missing class declaration');
                }
                break;
            case 'cpp':
                // Check for basic C++ syntax
                if (!code.includes('#include')) {
                    result.errors.push('Missing include statements');
                }
                break;
        }

        if (result.errors.length > 0) {
            result.isValid = false;
        }

        return result;
    }
}

// Create singleton instance
const codeExecutionService = new CodeExecutionService();

export default codeExecutionService;
