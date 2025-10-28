<template>
  <div class="test-editor">
    <div class="header">
      <button class="btn" @click="goBack">
        ← Quay lại khóa học
      </button>
      <div class="spacer" />
      <div class="test-title-area">
        <div class="mini-label">Tên bài kiểm tra</div>
        <input v-model="meta.title" class="title-input" />
      </div>
      <div class="meta-rows">
        <div class="field small">
          <div class="mini-label">Thời gian (phút)</div>
          <input type="number" min="0" v-model.number="meta.timeLimitMinutes" />
        </div>
        <div class="field small">
          <div class="mini-label">Số lần làm</div>
          <input type="number" min="1" v-model.number="meta.attemptsAllowed" />
        </div>
        <div class="field small">
          <div class="mini-label">Placement</div>
          <label class="checkbox"><input type="checkbox" v-model="meta.isPlacement" /> Placement</label>
        </div>
        <button class="btn primary" @click="saveMeta"><i class="fas fa-save" /> Lưu</button>
      </div>
    </div>

    <div class="questions">
      <div class="questions-header">
        <div class="questions-title">Câu hỏi ({{ questions.length }})</div>
        <button class="btn" @click="toggleAddQuestion">
          <i class="fas fa-plus" /> Thêm câu hỏi
        </button>
      </div>

      <div v-if="addingQuestion" class="add-card">
        <div class="add-card-title">Thêm câu hỏi</div>
        <div class="form-row">
          <div class="form-group full">
            <label>Nội dung câu hỏi</label>
            <textarea v-model="newQ.content" rows="2" />
          </div>
          <div class="form-group">
            <label>Điểm</label>
            <input type="number" min="0" v-model.number="newQ.points" />
          </div>
          <div class="form-group">
            <label>Độ khó</label>
            <select v-model="newQ.difficulty">
              <option value="easy">Dễ</option>
              <option value="medium">Trung bình</option>
              <option value="hard">Khó</option>
            </select>
          </div>
        </div>
        <div class="choices-edit">
          <div class="choices-header">
            <div class="title">Lựa chọn</div>
            <button class="btn small" @click="addChoice(newQ)"><i class="fas fa-plus"></i> Thêm lựa chọn</button>
          </div>
          <div v-if="!newQ.choices.length" class="empty tiny">Chưa có lựa chọn</div>
          <div v-for="(c, idx) in newQ.choices" :key="idx" class="choice-row">
            <input v-model="c.text" placeholder="Nội dung lựa chọn" />
            <label class="checkbox"><input type="checkbox" v-model="c.isCorrect" /> Đúng</label>
            <button class="btn danger small" @click="removeChoice(newQ, idx)">Xóa</button>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn" @click="cancelAddQuestion">Hủy</button>
          <button class="btn primary" @click="saveNewQuestion">Lưu</button>
        </div>
      </div>

      <div v-if="!questions.length && !addingQuestion" class="empty">Chưa có câu hỏi</div>

      <div v-for="q in questions" :key="q.id" class="question-item">
        <div class="question-row">
          <span class="badge">#{{ q.id }}</span>
          <div class="q-content">{{ q.content }}</div>
          <div class="q-meta">{{ q.points }}đ • {{ labelDifficulty(q.difficulty) }}</div>
          <div class="spacer" />
          <button class="btn small" @click="q.expanded = !q.expanded">
            <i class="fas" :class="q.expanded ? 'fa-chevron-up' : 'fa-chevron-down'" />
          </button>
          <button class="btn danger small" @click="deleteQuestion(q)">Xóa</button>
        </div>
        <div v-if="q.expanded" class="question-edit">
          <div class="form-row">
            <div class="form-group full">
              <label>Nội dung câu hỏi</label>
              <textarea v-model="q.editContent" rows="2" />
            </div>
            <div class="form-group">
              <label>Điểm</label>
              <input type="number" min="0" v-model.number="q.editPoints" />
            </div>
            <div class="form-group">
              <label>Độ khó</label>
              <select v-model="q.editDifficulty">
                <option value="easy">Dễ</option>
                <option value="medium">Trung bình</option>
                <option value="hard">Khó</option>
              </select>
            </div>
          </div>
          <div class="choices-edit">
            <div class="choices-header">
              <div class="title">Lựa chọn</div>
              <button class="btn small" @click="addChoice(q)"><i class="fas fa-plus"></i> Thêm lựa chọn</button>
            </div>
            <div v-if="!q.editChoices.length" class="empty tiny">Chưa có lựa chọn</div>
            <div v-for="(c, idx) in q.editChoices" :key="idx" class="choice-row">
              <input v-model="c.text" placeholder="Nội dung lựa chọn" />
              <label class="checkbox"><input type="checkbox" v-model="c.isCorrect" /> Đúng</label>
              <button class="btn danger small" @click="removeChoice(q, idx)">Xóa</button>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn" @click="q.expanded = false">Đóng</button>
            <button class="btn primary" @click="saveQuestion(q)">Lưu</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
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
    }
  },
  async mounted() {
    this.testId = Number(this.$route.params.id)
    this.courseId = Number(this.$route.query.courseId || 0)
    await this.fetchTest()
  },
  methods: {
    goBack() {
      if (this.courseId) {
        this.$router.push({ name: 'InstructorCourseLessons', params: { id: this.courseId }})
      } else {
        this.$router.back()
      }
    },
    labelDifficulty(d) {
      return d === 'easy' ? 'Dễ' : d === 'hard' ? 'Khó' : 'Trung bình'
    },
    async fetchTest() {
      this.loading = true
      try {
        const res = await fetch(`http://localhost:5000/api/tests/${this.testId}`)
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Không thể tải test')
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
          editChoices: (q.choices || []).map(c => ({ text: c.text, isCorrect: !!c.isCorrect }))
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
    async saveMeta() {
      try {
        const payload = { ...this.meta }
        const res = await fetch(`http://localhost:5000/api/tests/${this.testId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Không thể lưu meta')
        await this.fetchTest()
      } catch (e) {
        alert(e.message)
      }
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
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Không thể thêm câu hỏi')
        this.addingQuestion = false
        await this.fetchTest()
      } catch (e) {
        alert(e.message)
      }
    },
    cancelAddQuestion() {
      this.addingQuestion = false
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
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Không thể cập nhật câu hỏi')
        q.expanded = false
        await this.fetchTest()
      } catch (e) {
        alert(e.message)
      }
    },
    async deleteQuestion(q) {
      if (!confirm('Xóa câu hỏi này?')) return
      try {
        const res = await fetch(`http://localhost:5000/api/questions/${q.id}`, { method: 'DELETE' })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || 'Không thể xóa câu hỏi')
        await this.fetchTest()
      } catch (e) {
        alert(e.message)
      }
    }
  }
}
</script>

<style scoped>
.test-editor {
  padding: 20px;
  max-width: 1100px;
  margin: 0 auto;
}
.header {
  background: #ffffff;
  border: 1px solid #eaeaea;
  border-radius: 10px;
  padding: 12px;
  display: grid;
  grid-template-columns: 160px 1fr;
  align-items: end;
  gap: 12px 16px;
}
.spacer { flex: 1; }
.test-title-area { grid-column: 1 / -1; }
.title-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.meta-rows {
  display: flex;
  gap: 10px;
  align-items: end;
}
.mini-label {
  font-size: 11px;
  color: #8a8a8a;
  margin-bottom: 4px;
}
.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
}
.btn.primary {
  background: #3498db;
  color: #fff;
  border-color: #3498db;
}
.btn.danger {
  background: #ffebee;
  color: #d32f2f;
  border-color: #ffcdd2;
}
.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.field.small input,
.field.small select {
  width: 140px;
}

.questions {
  margin-top: 16px;
}
.questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.questions-title {
  font-weight: 600;
  color: #2c3e50;
}
.add-card {
  background: #ffffff;
  border: 1px solid #eaeaea;
  border-radius: 10px;
  padding: 16px;
  margin: 10px 0;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.add-card-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 160px 160px;
  gap: 12px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group.full { grid-column: 1 / -1; }
.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}

.question-item {
  background: #fff;
  border: 1px solid #eaeaea;
  border-radius: 10px;
  padding: 12px;
  margin-top: 10px;
}
.question-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.badge {
  background: #eef7ff;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}
.q-content { flex: 1; color: #34495e; }
.q-meta { color: #888; font-size: 12px; }
.question-edit { margin-top: 10px; }

.choices-edit {
  margin-top: 10px;
  background: #fafbff;
  border: 1px dashed #e5e7fb;
  border-radius: 10px;
  padding: 10px;
}
.choices-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.choice-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 6px;
}

.empty { color: #666; padding: 8px; text-align: center; }
.empty.tiny { color: #888; padding: 4px; font-size: 13px; text-align: left; }
.btn.small { padding: 5px 8px; font-size: 12px; }

@media (max-width: 768px) {
  .header { grid-template-columns: 1fr; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
