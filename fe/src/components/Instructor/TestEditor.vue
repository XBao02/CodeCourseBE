<template>
  <div class="test-editor test-editor-light">
    <div class="editor-shell">
      <div class="panel header-panel">
        <div class="top-bar">
          <button class="btn-ghost" @click="goBack">← Back to course</button>
          <h2 class="panel-title">Test Questions</h2>
        </div>
      </div>
      <div class="panel questions-panel">
        <div class="panel-header">
          <h3 class="panel-title">Questions <span class="count">({{ questions.length }})</span></h3>
          <div class="bulk-tools">
            <label class="select-all">
              <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" /> Select all
            </label>
            <button class="danger-btn" v-if="selectedCount" @click="deleteSelectedQuestions">Delete Selected ({{ selectedCount }})</button>
          </div>
          <div class="actions">
            <button class="soft-btn" @click="toggleAddQuestion"><i class="fas fa-plus"></i> Add Question</button>
            <button class="primary-outline-btn" @click="toggleAISettings" :disabled="aiGenerating">
              <i :class="aiGenerating ? 'fas fa-spinner fa-spin' : 'fas fa-robot'" />
              {{ showAISettings ? 'Close AI Settings' : (aiGenerating ? 'Generating...' : 'AI Generator') }}
            </button>
          </div>
        </div>
        <transition name="fade">
          <div v-if="showAISettings" class="editor-card ai-settings-card">
            <div class="editor-card-header">AI Generation Settings</div>
            <div class="form-grid">
              <div>
                <label class="meta-label">Number of Questions</label>
                <input type="number" min="1" max="50" v-model.number="aiConfig.num_questions" class="form-input" />
              </div>
              <div>
                <label class="meta-label">Difficulty</label>
                <select v-model="aiConfig.difficulty" class="form-input">
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>
            <div class="card-actions">
              <button class="soft-btn" @click="showAISettings=false">Cancel</button>
              <button class="primary-btn" :disabled="aiGenerating" @click="generateWithAI">
                <i :class="aiGenerating ? 'fas fa-spinner fa-spin' : 'fas fa-magic'" />
                {{ aiGenerating ? 'Generating...' : 'Generate' }}
              </button>
            </div>
          </div>
        </transition>
        <transition name="fade">
          <div v-if="addingQuestion" class="editor-card add-question-card">
            <div class="editor-card-header">Add Question</div>
            <div class="add-q-block">
              <label class="meta-label block-label">Question Content</label>
              <textarea v-model="newQ.content" rows="3" class="form-input stretched"></textarea>
            </div>
            <div class="add-q-row">
              <div class="field-inline">
                <label class="meta-label">Points</label>
                <input type="number" min="0" v-model.number="newQ.points" class="form-input" />
              </div>
              <div class="field-inline">
                <label class="meta-label">Difficulty</label>
                <select v-model="newQ.difficulty" class="form-input">
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
              <div class="choices-inline-action">
                <button class="soft-btn small" @click="addChoice(newQ)"><i class="fas fa-plus"></i> Add choice</button>
              </div>
            </div>
            <div class="choices-section">
              <div class="sub-title">Choices</div>
              <div v-if="!newQ.choices.length" class="empty tiny">No choices</div>
              <div v-for="(c, idx) in newQ.choices" :key="idx" class="choice-row">
                <input v-model="c.text" class="form-input" placeholder="Choice text" />
                <label class="checkbox"><input type="checkbox" v-model="c.isCorrect" /> Correct</label>
                <button class="danger-btn small" @click="removeChoice(newQ, idx)">Delete</button>
              </div>
            </div>
            <div class="card-actions">
              <button class="soft-btn" @click="cancelAddQuestion">Cancel</button>
              <button class="primary-btn" @click="saveNewQuestion">Save</button>
            </div>
          </div>
        </transition>
        <div v-if="!questions.length && !addingQuestion" class="empty">No questions</div>
        <div class="question-list">
          <div v-for="q in questions" :key="q.id" class="question-row" :class="{ expanded: q.expanded }">
            <div class="q-head" @click="q.expanded = !q.expanded">
              <input type="checkbox" class="q-select" v-model="q.selected" @click.stop />
              <span class="badge">#{{ q.id }}</span>
              <div class="q-text">{{ q.content }}</div>
              <div class="q-meta">{{ q.points }} pts • {{ labelDifficulty(q.difficulty) }}</div>
              <div class="spacer"></div>
              <button class="toggle-btn" :title="q.expanded ? 'Collapse' : 'Expand'">
                <i :class="q.expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
              <button class="danger-btn small" @click.stop="deleteQuestion(q)">Delete</button>
            </div>
            <transition name="slide">
              <div v-if="q.expanded" class="q-edit">
                <div class="form-grid">
                  <div class="col-span-3">
                    <label class="meta-label">Question Content</label>
                    <textarea v-model="q.editContent" rows="2" class="form-input"></textarea>
                  </div>
                  <div>
                    <label class="meta-label">Points</label>
                    <input type="number" min="0" v-model.number="q.editPoints" class="form-input" />
                  </div>
                  <div>
                    <label class="meta-label">Difficulty</label>
                    <select v-model="q.editDifficulty" class="form-input">
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>
                </div>
                <div class="choices-section">
                  <div class="choices-bar">
                    <div class="sub-title">Choices</div>
                    <button class="soft-btn small" @click="addChoice(q)"><i class="fas fa-plus"></i> Add choice</button>
                  </div>
                  <div v-if="!q.editChoices.length" class="empty tiny">No choices</div>
                  <div v-for="(c, idx) in q.editChoices" :key="idx" class="choice-row">
                    <input v-model="c.text" class="form-input" placeholder="Choice text" />
                    <label class="checkbox"><input type="checkbox" v-model="c.isCorrect" /> Correct</label>
                    <button class="danger-btn small" @click="removeChoice(q, idx)">Delete</button>
                  </div>
                </div>
                <div class="card-actions">
                  <button class="soft-btn" @click="q.expanded = false">Close</button>
                  <button class="primary-btn" @click="saveQuestion(q)">Save</button>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getStoredSession } from "../../services/authService";
export default {
  name: 'TestEditor',
  data() {
    return {
      courseId: null,
      testId: null,
      loading: true,
      meta: {
        title: '',
        timeLimitMinutes: 0,
        attemptsAllowed: 1,
        isPlacement: false,
      },
      questions: [],
      addingQuestion: false,
      newQ: {
        content: '',
        points: 1,
        difficulty: 'medium',
        choices: [],
      },
      aiGenerating: false,
      aiError: null,
      aiConfig: { num_questions: 10, difficulty: 'medium' },
      showAISettings: false,
    }
  },
  computed: {
    selectedCount() { return this.questions.filter(q => q.selected).length },
    allSelected() { return this.questions.length > 0 && this.selectedCount === this.questions.length }
  },
  async mounted() {
    this.testId = Number(this.$route.params.id)
    this.courseId = Number(this.$route.query.courseId || 0)
    await this.fetchTest()
  },
  methods: {
    authHeaders(extra = {}) {
      const session = getStoredSession();
      const token = session?.access_token;
      return {
        ...(extra || {}),
        Authorization: token ? `Bearer ${token}` : "",
      };
    },
    goBack() {
      if (this.courseId) {
        this.$router.push({ name: 'InstructorCourseLessons', params: { id: this.courseId }})
      } else {
        this.$router.back()
      }
    },
    labelDifficulty(d) {
      return d === 'easy' ? 'Easy' : d === 'hard' ? 'Hard' : 'Medium'
    },
    async fetchTest() {
      this.loading = true
      try {
        const res = await fetch(`http://localhost:5000/api/tests/${this.testId}`, {
          headers: this.authHeaders(),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Cannot load test')
        // map meta
        this.meta = {
          title: data.title || '',
          timeLimitMinutes: data.timeLimitMinutes || 0,
          attemptsAllowed: data.attemptsAllowed || 1,
          isPlacement: !!data.isPlacement,
        }
        // map questions
        this.questions = (data.questions || []).map(q => ({
          ...q,
          expanded: false,
          editContent: q.content,
          editPoints: q.points || 1,
          editDifficulty: q.difficulty || 'medium',
          editChoices: (q.choices || []).map(c => ({ text: c.text, isCorrect: !!c.isCorrect })),
          selected: false, // add selected flag
        }))
      } catch (e) {
        alert(e.message)
      } finally {
        this.loading = false
      }
    },
    toggleAddQuestion() {
      this.addingQuestion = !this.addingQuestion
      if (this.addingQuestion) {
        this.newQ = { content: '', points: 1, difficulty: 'medium', choices: [] }
      }
    },
    addChoice(target) {
      target.choices = target.choices || target.editChoices || []
      if (target === this.newQ) {
        this.newQ.choices.push({ text: '', isCorrect: false })
      } else {
        target.editChoices.push({ text: '', isCorrect: false })
      }
    },
    removeChoice(target, idx) {
      if (target === this.newQ) {
        this.newQ.choices.splice(idx, 1)
      } else {
        target.editChoices.splice(idx, 1)
      }
    },
    cancelAddQuestion() {
      this.addingQuestion = false
    },
    async saveNewQuestion() {
      try {
        const payload = {
          content: this.newQ.content,
          points: this.newQ.points,
          difficulty: this.newQ.difficulty,
          choices: this.newQ.choices
        }
        const res = await fetch(`http://localhost:5000/api/tests/${this.testId}/questions`, {
          method: 'POST',
          headers: this.authHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Cannot create question')
        this.addingQuestion = false
        await this.fetchTest()
      } catch (e) {
        alert(e.message)
      }
    },
    async saveQuestion(q) {
      try {
        const payload = {
          content: q.editContent,
          points: q.editPoints,
          difficulty: q.editDifficulty,
          choices: q.editChoices
        }
        const res = await fetch(`http://localhost:5000/api/questions/${q.id}`, {
          method: 'PUT',
          headers: this.authHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Cannot update question')
        q.expanded = false
        await this.fetchTest()
      } catch (e) {
        alert(e.message)
      }
    },
    async deleteQuestion(q) {
      if (!confirm('Delete this question?')) return
      try {
        const res = await fetch(`http://localhost:5000/api/questions/${q.id}`, {
          method: 'DELETE',
          headers: this.authHeaders(),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Cannot delete question')
        await this.fetchTest()
      } catch (e) {
        alert(e.message)
      }
    },
    toggleAISettings() { this.showAISettings = !this.showAISettings },
    async openAIGenerator() {
      this.aiError = null
      this.aiGenerating = true
      try {
        const payload = {
          lesson_title: this.meta.title || 'Lesson Quiz',
          num_questions: this.aiConfig.num_questions,
          difficulty: this.aiConfig.difficulty,
        }
        const res = await fetch('http://localhost:5000/api/ai/quiz/generate', {
          method: 'POST',
          headers: this.authHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (!res.ok || !data.questions) throw new Error(data.error || 'Error generating questions')
        // append into current test
        for (const q of data.questions) {
          const choices = q.options.map((opt, idx) => ({ text: opt, isCorrect: q.correctAnswer === idx }))
          const qPayload = { content: q.question, points: 1, difficulty: this.aiConfig.difficulty, choices }
          const qRes = await fetch(`http://localhost:5000/api/tests/${this.testId}/questions`, {
            method: 'POST',
            headers: this.authHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify(qPayload)
          })
          const qData = await qRes.json().catch(() => ({}))
          if (!qRes.ok) throw new Error(qData.message || 'Error saving question')
        }
        await this.fetchTest()
      } catch (e) {
        this.aiError = e.message || 'Error creating AI questions'
        alert(this.aiError)
      } finally {
        this.aiGenerating = false
      }
    },
    generateWithAI() { this.openAIGenerator() },
    toggleSelectAll() { const target = !this.allSelected; this.questions.forEach(q => q.selected = target) },
    async deleteSelectedQuestions() {
      const targets = this.questions.filter(q => q.selected)
      if (!targets.length) return
      if (!confirm(`Delete ${targets.length} selected question(s)?`)) return
      try {
        for (const q of targets) {
          const res = await fetch(`http://localhost:5000/api/questions/${q.id}`, { method: 'DELETE', headers: this.authHeaders() })
          const data = await res.json().catch(()=>({}))
          if (!res.ok) throw new Error(data.message || 'Failed to delete one question')
        }
        await this.fetchTest()
      } catch (e) { alert(e.message) }
    },
  }
}
</script>

<style scoped>
/* Light theme (white background, slightly darker accents) */
.test-editor-light { background: #ffffff; min-height: 100vh; padding: 40px 26px; }
.editor-shell { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 32px; }
.panel { background: #ffffff; border: 1px solid #dbe1e8; border-radius: 12px; padding: 24px 28px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }
.header-panel { display: flex; flex-direction: column; gap: 20px; }
.top-bar { display: flex; align-items: center; gap: 12px; }
.meta-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(220px,1fr)); gap: 18px; }
.title-block { grid-column: 1 / -1; }
.meta-label { font-size: 12px; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: #64748b; margin-bottom: 6px; }
.form-input { background: #f1f5f9; border: 1px solid #cbd5e1; color: #1f2937; border-radius: 6px; padding: 10px 12px; font-size: 14px; transition: border-color .2s, background .2s, box-shadow .2s; }
.form-input.large { font-size: 15px; }
.form-input:focus { outline: none; background: #ffffff; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.2); }
.checkbox.inline { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.checkbox input { width:20px; height:20px; accent-color:#2563eb; }

/* Buttons */
.primary-btn, .primary-outline-btn, .soft-btn, .btn-ghost, .danger-btn, .toggle-btn { border-radius:6px; }
.primary-btn { background: linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%); color:#fff; border:none; padding:9px 16px; font-weight:600; font-size:14px; box-shadow:0 4px 16px -2px rgba(37,99,235,.35); cursor:pointer; transition:.25s; }
.primary-btn:hover:not(:disabled) { transform:translateY(-2px); box-shadow:0 8px 22px -4px rgba(37,99,235,.45); }
.primary-btn:disabled { opacity:.5; cursor:not-allowed; }
.primary-outline-btn { background:#ffffff; color:#2563eb; border:1px solid #cbd5e1; padding:9px 16px; font-weight:600; font-size:14px; cursor:pointer; transition:.25s; }
.primary-outline-btn:hover:not(:disabled){ border-color:#2563eb; color:#1d4ed8; box-shadow:0 2px 8px rgba(0,0,0,.06); }
.soft-btn { background:#f1f5f9; color:#1f2937; border:1px solid #cbd5e1; padding:9px 14px; font-size:14px; font-weight:500; cursor:pointer; transition:.2s; }
.soft-btn.small { padding:5px 8px; font-size:12px; }
.soft-btn:hover { background:#e2e8f0; border-color:#94a3b8; }
.btn-ghost { background:#f1f5f9; color:#1f2937; border:1px solid #cbd5e1; padding:9px 14px; cursor:pointer; font-weight:500; }
.btn-ghost:hover { background:#e2e8f0; border-color:#94a3b8; }
.danger-btn { background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; padding:6px 10px; cursor:pointer; font-size:12px; font-weight:600; transition:.2s; }
.danger-btn.small { padding:5px 8px; }
.danger-btn:hover { background:#fecaca; }
.toggle-btn { background:#f1f5f9; color:#475569; padding:5px 8px; cursor:pointer; font-size:12px; transition:.2s; }
.toggle-btn:hover { background:#e2e8f0; color:#1f2937; }

/* Questions */
.questions-panel { display:flex; flex-direction:column; gap:32px; }
.panel-header { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom: 8px; }
.panel-title { margin:0; font-size:18px; font-weight:700; color:#1f2937; display:flex; align-items:center; gap:6px; }
.panel-title .count { font-size:14px; font-weight:500; color:#64748b; }
.actions { display:flex; gap:16px; }
.editor-card { background:#ffffff; border:1px solid #dbe1e8; border-radius:12px; padding:22px 24px; display:flex; flex-direction:column; gap:20px; box-shadow:0 4px 14px -2px rgba(0,0,0,.08); }
.editor-card + .editor-card { margin-top: 20px; }
.editor-card-header { font-weight:600; font-size:15px; color:#1f2937; }
.form-grid { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:18px; }
.col-span-3 { grid-column:1 / -1; }
.choices-section { display:flex; flex-direction:column; gap:18px; }
.choices-bar { display:flex; justify-content:space-between; align-items:center; }
.sub-title { font-weight:600; font-size:13px; color:#64748b; letter-spacing:.5px; text-transform:uppercase; }
.choice-row { display:grid; grid-template-columns: 1fr auto auto; gap:12px; align-items:center; background:#f8fafc; padding:10px 12px; border-radius:8px; border:1px solid #e2e8f0; }
.choice-row + .choice-row { margin-top:8px; }
.card-actions { display:flex; justify-content:flex-end; gap:14px; margin-top: 8px; }
.question-list { display:flex; flex-direction:column; gap:16px; }
.question-row { background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; transition: border-color .25s, box-shadow .25s; }
.question-row.expanded { box-shadow:0 6px 24px -4px rgba(0,0,0,.12); border-color:#2563eb; }
.q-head { display:flex; align-items:center; gap:16px; padding:16px 20px; cursor:pointer; }
.badge { background:#2563eb; color:#fff; border-radius:5px; padding:3px 6px; font-size:12px; font-weight:600; letter-spacing:.5px; }
.q-text { flex:1; color:#1f2937; font-weight:500; }
.q-meta { color:#64748b; font-size:12px; font-weight:500; }
.q-edit { padding:0 20px 20px; display:flex; flex-direction:column; gap:20px; }
.empty { text-align:center; padding:32px 18px; font-size:14px; color:#64748b; border:1px dashed #cbd5e1; border-radius:14px; background:#f8fafc; margin-top: 4px; }
.empty.tiny { padding:8px 10px; font-size:12px; }

/* Animations */
.fade-enter-active, .fade-leave-active { transition:opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity:0; }
.slide-enter-active { transition:max-height .35s ease, opacity .35s ease; }
.slide-enter-from { max-height:0; opacity:0; }
.slide-enter-to { max-height:1000px; opacity:1; }
.slide-leave-active { transition:max-height .25s ease, opacity .25s ease; }
.slide-leave-to { max-height:0; opacity:0; }

.ai-settings-card { border-color:#cbd5e1; margin-top: 4px; }
.ai-settings-card .editor-card-header { display:flex; align-items:center; gap:6px; }
.ai-settings-card .editor-card-header:before { content:'🤖'; font-size:16px; }

.bulk-tools { display:flex; align-items:center; gap:16px; flex-wrap:wrap; }
.select-all { display:flex; align-items:center; gap:6px; font-size:12px; font-weight:500; color:#475569; }
.select-all input { width:20px; height:20px; accent-color:#2563eb; cursor:pointer; }
.q-select { width:20px; height:20px; accent-color:#2563eb; cursor:pointer; margin-right:6px; }

@media (max-width: 900px) {
  .meta-grid { grid-template-columns: 1fr 1fr; }
  .editor-shell { gap: 28px; }
  .questions-panel { gap: 28px; }
  .form-grid { grid-template-columns: 1fr 1fr; gap:14px; }
  .col-span-3 { grid-column:1 / -1; }
  .actions { width:100%; justify-content:flex-start; }
  .q-head { padding:14px 16px; gap: 12px; }
}
</style>
