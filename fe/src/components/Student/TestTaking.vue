<template>
  <div class="test-taking">
    <div class="test-container">
      <!-- Header -->
      <div class="test-header">
        <button class="btn-back" @click="goBack">← Back to Course</button>
        <div class="test-info">
          <h2>{{ test.title }}</h2>
          <div class="test-meta">
            <span v-if="test.timeLimitMinutes > 0">
              ⏱️ Time: {{ formatTime(timeRemaining) }}
            </span>
            <span>📝 {{ questions.length }} Questions</span>
            <span>🎯 {{ calculateTotalPoints() }} Points</span>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading test...</p>
      </div>

      <!-- Test Content -->
      <div v-else-if="!submitted" class="test-content">
        <div class="questions-list">
          <div
            v-for="(question, index) in questions"
            :key="question.id"
            class="question-card"
          >
            <div class="question-header">
              <span class="question-number">Question {{ index + 1 }}</span>
              <span class="question-points">{{ question.points }} pts</span>
              <span class="difficulty-badge" :class="question.difficulty">
                {{ question.difficulty }}
              </span>
            </div>

            <div class="question-content">
              <p>{{ question.content }}</p>
            </div>

            <div class="choices-list">
              <div
                v-for="(choice, choiceIdx) in question.choices"
                :key="choice.id || choiceIdx"
                class="choice-item"
                @click="selectChoice(question, choice)"
              >
                <input
                  type="radio"
                  :name="'question-' + question.id"
                  :value="choice.id"
                  :checked="isChoiceSelected(question.id, choice.id)"
                  @change="selectChoice(question, choice)"
                />
                <label>{{ choice.text || choice.content }}</label>
              </div>
            </div>
          </div>
        </div>

        <div class="test-actions">
          <button class="btn-submit" @click="submitTest" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit Test' }}
          </button>
        </div>
      </div>

      <!-- Result Display -->
      <div v-else class="test-result">
        <div class="result-card">
          <div class="result-icon">
            <span v-if="result.passed">🎉</span>
            <span v-else>📊</span>
          </div>
          <h3>Test Completed!</h3>
          
          <div class="score-display">
            <div class="score-circle">
              <span class="score-value">{{ result.score }}</span>
              <span class="score-total">/ {{ result.totalScore }}</span>
            </div>
            <div class="score-percentage">
              {{ calculatePercentage(result.score, result.totalScore) }}%
            </div>
          </div>

          <div class="result-stats">
            <div class="stat-item">
              <span class="stat-label">Correct Answers</span>
              <span class="stat-value">{{ result.correctCount }} / {{ questions.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Status</span>
              <span class="stat-value" :class="result.passed ? 'passed' : 'failed'">
                {{ result.passed ? 'Passed' : 'Failed' }}
              </span>
            </div>
          </div>

          <div class="result-actions">
            <button class="btn-primary" @click="viewAnswers">View Answers</button>
            <button class="btn-secondary" @click="goBack">Back to Course</button>
          </div>
        </div>

        <!-- Detailed Answers (if viewing) -->
        <div v-if="showingAnswers" class="answers-review">
          <h3>Answer Review</h3>
          <div
            v-for="(question, index) in questions"
            :key="'review-' + question.id"
            class="review-question"
          >
            <div class="review-header">
              <span class="question-number">Question {{ index + 1 }}</span>
              <span class="review-status" :class="isQuestionCorrect(question) ? 'correct' : 'incorrect'">
                {{ isQuestionCorrect(question) ? '✓ Correct' : '✗ Incorrect' }}
              </span>
            </div>
            <p class="review-content">{{ question.content }}</p>
            
            <div class="review-choices">
              <div
                v-for="choice in question.choices"
                :key="'review-choice-' + choice.id"
                class="review-choice"
                :class="{
                  'correct-answer': choice.isCorrect,
                  'user-selected': isChoiceSelected(question.id, choice.id),
                  'wrong-selected': isChoiceSelected(question.id, choice.id) && !choice.isCorrect
                }"
              >
                <span class="choice-indicator">
                  <span v-if="choice.isCorrect">✓</span>
                  <span v-else-if="isChoiceSelected(question.id, choice.id)">✗</span>
                </span>
                <span>{{ choice.text || choice.content }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getStoredSession } from '../../services/authService'

export default {
  name: 'TestTaking',
  data() {
    return {
      testId: null,
      courseId: null,
      loading: true,
      submitting: false,
      submitted: false,
      showingAnswers: false,
      test: {
        title: '',
        timeLimitMinutes: 0,
        attemptsAllowed: 1,
      },
      questions: [],
      userAnswers: {}, // { questionId: choiceId }
      result: {
        score: 0,
        totalScore: 0,
        correctCount: 0,
        passed: false,
      },
      timeRemaining: 0,
      timerInterval: null,
    }
  },
  async mounted() {
    this.testId = Number(this.$route.params.testId)
    this.courseId = Number(this.$route.params.courseId)
    
    await this.loadTest()
    
    if (this.test.timeLimitMinutes > 0) {
      this.startTimer()
    }
  },
  methods: {
    getAuthHeaders() {
      const session = getStoredSession()
      if (!session?.access_token) {
        throw new Error('No authentication token found')
      }
      return {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json'
      }
    },
    
    async loadTest() {
      this.loading = true
      try {
        const headers = this.getAuthHeaders()
        const res = await fetch(`http://localhost:5000/api/student/tests/${this.testId}`, { headers })
        if (!res.ok) {
          const error = await res.json()
          throw new Error(error.message || 'Failed to load test')
        }
        const data = await res.json()
        this.test = {
          title: data.title || 'Test',
          timeLimitMinutes: data.timeLimitMinutes || data.time_limit_minutes || 0,
          attemptsAllowed: data.attemptsAllowed || data.attempts_allowed || 1,
        }
        // Map questions
        let mapped = (data.questions || []).map(q => ({
          id: q.id,
          content: q.content,
          points: q.points || 1,
            difficulty: q.difficulty || 'medium',
          choices: (q.choices || []).map(c => ({
            id: c.id,
            text: c.text || c.content,
            content: c.text || c.content,
            isCorrect: c.isCorrect || c.is_correct || false,
          }))
        }))
        // Shuffle questions
        for (let i = mapped.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1))
          ;[mapped[i], mapped[j]] = [mapped[j], mapped[i]]
        }
        // Limit to max 20
        if (mapped.length > 20) mapped = mapped.slice(0, 20)
        // Shuffle choices inside each question
        mapped.forEach(q => {
          for (let i = q.choices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1))
            ;[q.choices[i], q.choices[j]] = [q.choices[j], q.choices[i]]
          }
        })
        this.questions = mapped
        this.timeRemaining = this.test.timeLimitMinutes * 60
      } catch (error) {
        console.error('Error loading test:', error)
        alert('Failed to load test: ' + error.message)
        this.goBack()
      } finally {
        this.loading = false
      }
    },
    
    startTimer() {
      this.timerInterval = setInterval(() => {
        this.timeRemaining--
        if (this.timeRemaining <= 0) {
          this.timeUp()
        }
      }, 1000)
    },
    
    timeUp() {
      clearInterval(this.timerInterval)
      alert('Time is up! Submitting your test...')
      this.submitTest()
    },
    
    selectChoice(question, choice) {
      this.userAnswers[question.id] = choice.id
    },
    
    isChoiceSelected(questionId, choiceId) {
      return this.userAnswers[questionId] === choiceId
    },
    
    calculateTotalPoints() {
      return this.questions.reduce((sum, q) => sum + (q.points || 1), 0)
    },
    
    async submitTest() {
      if (this.submitting) return
      
      // Validate all questions are answered
      const unanswered = this.questions.filter(q => !this.userAnswers[q.id])
      if (unanswered.length > 0) {
        if (!confirm(`You have ${unanswered.length} unanswered question(s). Submit anyway?`)) {
          return
        }
      }
      
      this.submitting = true
      
      try {
        const headers = this.getAuthHeaders()
        
        // Format answers for submission
        const answers = this.questions.map(q => ({
          questionId: q.id,
          choiceId: this.userAnswers[q.id] || null
        }))
        
        const payload = {
          testId: this.testId,
          answers: answers
        }
        
        const res = await fetch(`http://localhost:5000/api/student/tests/${this.testId}/submit`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload)
        })
        
        if (!res.ok) {
          const error = await res.json()
          throw new Error(error.message || 'Failed to submit test')
        }
        
        const data = await res.json()
        
        this.result = {
          score: data.score || 0,
          totalScore: data.totalScore || data.total_score || this.calculateTotalPoints(),
          correctCount: data.correctCount || data.correct_count || 0,
          passed: data.passed || false,
        }
        
        this.submitted = true
        
        if (this.timerInterval) {
          clearInterval(this.timerInterval)
        }
        
      } catch (error) {
        console.error('Error submitting test:', error)
        alert('Failed to submit test: ' + error.message)
      } finally {
        this.submitting = false
      }
    },
    
    isQuestionCorrect(question) {
      const userChoiceId = this.userAnswers[question.id]
      if (!userChoiceId) return false
      
      const selectedChoice = question.choices.find(c => c.id === userChoiceId)
      return selectedChoice ? selectedChoice.isCorrect : false
    },
    
    viewAnswers() {
      this.showingAnswers = !this.showingAnswers
    },
    
    calculatePercentage(score, total) {
      if (total === 0) return 0
      return Math.round((score / total) * 100)
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    
    goBack() {
      this.$router.push({
        name: 'StudentCourseLesson',
        params: { courseId: this.courseId }
      })
    }
  },
  beforeUnmount() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval)
    }
  }
}
</script>

<style scoped>
.test-taking {
  background: #f8f9fa;
  min-height: 100vh;
  padding: 20px;
}

.test-container {
  max-width: 900px;
  margin: 0 auto;
}

.test-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.btn-back {
  background: #f1f5f9;
  color: #1f2937;
  border: 1px solid #cbd5e1;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #e2e8f0;
}

.test-info h2 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.test-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.question-number {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 16px;
}

.question-points {
  background: #e0e7ff;
  color: #3730a3;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.difficulty-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.difficulty-badge.easy { background: #d1fae5; color: #065f46; }
.difficulty-badge.medium { background: #fef3c7; color: #92400e; }
.difficulty-badge.hard { background: #fee2e2; color: #991b1b; }

.question-content {
  margin-bottom: 20px;
}

.question-content p {
  font-size: 16px;
  color: #1f2937;
  line-height: 1.6;
  margin: 0;
}

.choices-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.choice-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #f8f9fa;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.choice-item:hover {
  background: #e5e7eb;
  border-color: #3b82f6;
}

.choice-item input[type="radio"] {
  width: 20px;
  height: 20px;
  accent-color: #3b82f6;
}

.choice-item label {
  flex: 1;
  cursor: pointer;
  font-size: 15px;
  color: #1f2937;
}

.test-actions {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  justify-content: center;
}

.btn-submit {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.test-result {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  text-align: center;
}

.result-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.result-card h3 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 32px 0;
}

.score-display {
  margin-bottom: 32px;
}

.score-circle {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  margin-bottom: 16px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
}

.score-total {
  font-size: 24px;
  opacity: 0.9;
}

.score-percentage {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
}

.result-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.stat-value.passed { color: #059669; }
.stat-value.failed { color: #dc2626; }

.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
}

.btn-secondary {
  background: white;
  color: #1f2937;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #f8f9fa;
}

.answers-review {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.answers-review h3 {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 24px 0;
}

.review-question {
  padding: 20px 0;
  border-bottom: 1px solid #e5e7eb;
}

.review-question:last-child {
  border-bottom: none;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.review-status {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
}

.review-status.correct {
  background: #d1fae5;
  color: #065f46;
}

.review-status.incorrect {
  background: #fee2e2;
  color: #991b1b;
}

.review-content {
  font-size: 15px;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.review-choices {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.review-choice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  background: #f8f9fa;
  border: 2px solid transparent;
}

.review-choice.correct-answer {
  background: #d1fae5;
  border-color: #10b981;
}

.review-choice.wrong-selected {
  background: #fee2e2;
  border-color: #ef4444;
}

.choice-indicator {
  font-weight: 700;
  font-size: 16px;
}

.review-choice.correct-answer .choice-indicator {
  color: #059669;
}

.review-choice.wrong-selected .choice-indicator {
  color: #dc2626;
}

@media (max-width: 768px) {
  .test-taking {
    padding: 12px;
  }
  
  .test-header,
  .question-card,
  .test-actions,
  .result-card {
    padding: 20px;
  }
  
  .result-stats {
    grid-template-columns: 1fr;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>
