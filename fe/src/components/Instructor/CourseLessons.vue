<template>
    <div class="course-lessons">
    <div class="header">
      <h1>Quản lý nội dung khóa học</h1>
      <div class="actions">
        <button class="btn" @click="goBack"><i class="fas fa-arrow-left"></i> Quay lại</button>
        <button class="btn primary" @click="promptAddSection"><i class="fas fa-plus"></i> Thêm chương</button>
      </div>
    </div>

    <!-- Add Section Inline Card -->
    <div v-if="addingSection" class="add-card">
      <div class="add-card-title">Thêm chương mới</div>
      <div class="form-row">
        <div class="form-group">
          <label>Tiêu đề chương</label>
          <input v-model.trim="newSectionTitle" type="text" placeholder="VD: Giới thiệu, Biến & Kiểu dữ liệu..." />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn" @click="cancelAddSection">Hủy</button>
        <button class="btn primary" :disabled="!newSectionTitle" @click="saveNewSection">Lưu chương</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Đang tải curriculum...</div>
    <div v-else>
      <div v-if="sections.length === 0" class="empty">Chưa có chương nào. Hãy thêm chương đầu tiên.</div>

      <div v-for="section in sections" :key="section.id" class="section">
        <div class="section-header">
          <input v-model="section.editTitle" class="section-title-input" />
          <div class="section-actions">
            <button class="btn" @click="section.expanded = !section.expanded">
              <i :class="section.expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              {{ section.expanded ? 'Thu gọn' : 'Mở rộng' }}
            </button>
            <button class="btn" @click="saveSection(section)"><i class="fas fa-save"></i> Lưu</button>
            <button class="btn danger" @click="deleteSection(section)"><i class="fas fa-trash"></i> Xóa</button>
            <button class="btn" @click="promptAddLesson(section)"><i class="fas fa-plus"></i> Thêm bài học</button>
          </div>
        </div>

        <!-- Expanded section config -->
        <div v-if="section.expanded" class="section-expand">
          <div class="form-row">
            <div class="form-group">
              <label>Tiêu đề chương</label>
              <input v-model.trim="section.editTitle" type="text" />
            </div>
            <div class="form-group">
              <label>Thứ tự hiển thị</label>
              <input v-model.number="section.editOrder" type="number" min="0" />
            </div>
          </div>
          <div class="form-actions">
            <button class="btn" @click="section.expanded = false">Đóng</button>
            <button class="btn primary" @click="saveSection(section)">Lưu thay đổi</button>
          </div>
        </div>

        <!-- Add Lesson Inline Card -->
        <div v-if="section.addingLesson" class="add-card lesson">
          <div class="add-card-title">Thêm bài học vào: {{ section.title }}</div>
          <div class="form-row">
            <div class="form-group">
              <label>Tiêu đề bài học</label>
              <input v-model.trim="section.newLesson.title" type="text" placeholder="VD: Cài đặt môi trường, Vòng lặp for..." />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Loại bài học</label>
              <select v-model="section.newLesson.type">
                <option value="video">Video</option>
                <option value="article">Bài viết</option>
                <option value="coding">Coding</option>
                <option value="quiz">Quiz</option>
                <option value="assignment">Assignment</option>
                <option value="live">Live</option>
              </select>
            </div>
            <div class="form-group align-end">
              <label class="checkbox"><input type="checkbox" v-model="section.newLesson.isPreview" /> Cho xem trước</label>
            </div>
          </div>
          <div class="form-row" v-if="section.newLesson.type === 'video'">
            <div class="form-group">
              <label>Video URL</label>
              <input v-model.trim="section.newLesson.videoUrl" type="text" placeholder="https://..." />
            </div>
            <div class="form-group">
              <label>Thời lượng (giây)</label>
              <input v-model.number="section.newLesson.durationSeconds" type="number" min="0" placeholder="600" />
            </div>
          </div>
          <div class="form-row" v-if="section.newLesson.type === 'article'">
            <div class="form-group full">
              <label>Nội dung bài viết</label>
              <textarea v-model="section.newLesson.content" rows="4" placeholder="Nhập nội dung bài viết..."></textarea>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn" @click="cancelAddLesson(section)">Hủy</button>
            <button class="btn primary" :disabled="!section.newLesson.title" @click="saveNewLesson(section)">Lưu bài học</button>
          </div>
        </div>

        <div class="lessons">
          <div v-if="(lessonsBySection[section.id] || []).length === 0" class="empty small">Chưa có bài học</div>
          <div v-for="lesson in lessonsBySection[section.id] || []" :key="lesson.id" class="lesson">
            <!-- Compact lesson header -->
            <div class="lesson-top">
              <button class="btn icon" @click="lesson.expanded = !lesson.expanded" :title="lesson.expanded ? 'Thu gọn' : 'Mở rộng'">
                <i :class="lesson.expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
              <div class="lesson-title-display">{{ lesson.editTitle }}</div>
              <span class="type-pill">{{ lesson.editType }}</span>
              <span v-if="lesson.editPreview" class="pill preview-pill">Preview</span>
              <div class="spacer"></div>
              <button class="btn danger" @click="deleteLesson(lesson)"><i class="fas fa-trash"></i></button>
            </div>

            <!-- Editable details -->
            <div v-if="lesson.expanded" class="lesson-edit">
              <div class="lesson-edit-header">
                <div class="lesson-edit-title"><i class="fas fa-edit"></i> Chỉnh sửa bài học</div>
                <button class="btn icon" @click="lesson.expanded = false" title="Đóng">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="lesson-left">
                <div class="field">
                  <div class="mini-label">Tiêu đề</div>
                  <input v-model="lesson.editTitle" class="lesson-title-input" />
                </div>
                <div class="field">
                  <div class="mini-label">Loại</div>
                  <select v-model="lesson.editType" class="lesson-type">
                    <option value="video">Video</option>
                    <option value="article">Bài viết</option>
                    <option value="coding">Coding</option>
                    <option value="quiz">Quiz</option>
                    <option value="assignment">Assignment</option>
                    <option value="live">Live</option>
                  </select>
                </div>
                <div class="field">
                  <div class="mini-label">Xem trước</div>
                  <label class="preview"><input type="checkbox" v-model="lesson.editPreview" /> Preview</label>
                </div>
              </div>
              <div class="lesson-actions">
                <button class="btn" @click="saveLesson(lesson)"><i class="fas fa-save"></i> Lưu</button>
              </div>
            </div>

            <!-- Tests block -->
            <div class="tests">
              <div class="tests-header">
                <div class="tests-title">Bài test ({{ (testsByLesson[lesson.id] || []).length }})</div>
                <div class="tests-actions">
                  <button class="btn small" @click="lesson.testsExpanded = !lesson.testsExpanded">
                    <i :class="lesson.testsExpanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                    {{ lesson.testsExpanded ? 'Thu gọn' : 'Mở' }}
                  </button>
                  <button class="btn small" v-if="lesson.testsExpanded" @click="toggleAddTest(lesson)"><i class="fas fa-plus"></i> Thêm test</button>
                </div>
              </div>

              <div v-if="lesson.testsExpanded">
                <div v-if="lesson.addingTest" class="add-card test">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Tiêu đề test</label>
                      <input v-model.trim="lesson.newTest.title" type="text" placeholder="VD: Quiz Chương 1" />
                    </div>
                    <div class="form-group">
                      <label>Thời gian (phút)</label>
                      <input v-model.number="lesson.newTest.timeLimitMinutes" type="number" min="0" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Số lần làm</label>
                      <input v-model.number="lesson.newTest.attemptsAllowed" type="number" min="1" />
                    </div>
                    <div class="form-group align-end">
                      <label class="checkbox"><input type="checkbox" v-model="lesson.newTest.isPlacement" /> Placement test</label>
                    </div>
                  </div>
                  <div class="form-actions">
                    <button class="btn" @click="cancelAddTest(lesson)">Hủy</button>
                    <button class="btn primary" :disabled="!lesson.newTest.title" @click="saveNewTest(lesson)">Lưu test</button>
                  </div>
                </div>

                <div v-if="(testsByLesson[lesson.id] || []).length === 0" class="empty tiny">Chưa có bài test</div>
                <div v-for="t in testsByLesson[lesson.id] || []" :key="t.id" class="test-item">
                  <div class="test-row">
                    <div class="field" style="flex:1">
                      <div class="mini-label">Tiêu đề test</div>
                      <input v-model="t.editTitle" class="test-title-input" />
                    </div>
                    <div class="field small">
                      <div class="mini-label">Phút</div>
                      <input v-model.number="t.editTime" class="test-number-input" type="number" min="0" title="Phút" />
                    </div>
                    <div class="field small">
                      <div class="mini-label">Số lần</div>
                      <input v-model.number="t.editAttempts" class="test-number-input" type="number" min="1" title="Số lần làm" />
                    </div>
                    <div class="field">
                      <div class="mini-label">Placement</div>
                      <label class="checkbox"><input type="checkbox" v-model="t.editPlacement" /> Placement</label>
                    </div>
                    <div class="field qcount">
                      <div class="mini-label">Số câu</div>
                      <div class="pill">{{ t.questionCount || 0 }}</div>
                    </div>
                    <button class="btn" @click="saveTest(t)"><i class="fas fa-save"></i></button>
                    <button class="btn danger" @click="deleteTest(t)"><i class="fas fa-trash"></i></button>
                    <button class="btn" @click="openTestEditor(t)"><i class="fas fa-external-link-alt"></i> Mở trình soạn thảo</button>
                  </div>
                </div>
              </div>
            </div>
            <!-- end tests block -->
          </div>
        </div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  name: "CourseLessons",
  data() {
    return {
      courseId: null,
      loading: true,
      sections: [],
      lessonsBySection: {},
      // New inline add states
      addingSection: false,
      newSectionTitle: "",
      testsByLesson: {},
    };
  },
  async mounted() {
    this.courseId = Number(this.$route.params.id);
    await this.fetchCurriculum();
  },
  methods: {
    goBack() {
      this.$router.push("/instructor/courses");
    },
    openTestEditor(t) {
      this.$router.push({
        name: "InstructorTestEdit",
        params: { id: t.id },
        query: { courseId: this.courseId },
      });
    },
    async fetchCurriculum() {
      this.loading = true;
      try {
        const res = await fetch(
          `http://localhost:5000/api/courses/${this.courseId}/curriculum`
        );
        const data = await res.json();
        if (!res.ok)
          throw new Error(data.message || "Không thể tải curriculum");
        // clone and attach edit and add fields
        this.sections = (data || []).map((s) => ({
          ...s,
          editTitle: s.title,
          editOrder: s.sortOrder || 0,
          expanded: false,
          addingLesson: false,
          newLesson: {
            title: "",
            type: "video",
            isPreview: false,
            videoUrl: "",
            durationSeconds: null,
            content: "",
          },
        }));
        const map = {};
        this.sections.forEach((s) => {
          const lessons = (s.lessons || []).map((l) => ({
            ...l,
            editTitle: l.title,
            editType: l.type,
            editPreview: !!l.isPreview,
            expanded: false,
            testsExpanded: false,
          }));
          map[s.id] = lessons;
        });
        this.lessonsBySection = map;
        // load tests per lesson
        await Promise.all(
          Object.values(this.lessonsBySection)
            .flat()
            .map(async (l) => {
              await this.loadTestsForLesson(l.id);
            })
        );
      } catch (e) {
        alert(e.message);
      } finally {
        this.loading = false;
      }
    },
    async loadTestsForLesson(lessonId) {
      try {
        const res = await fetch(
          `http://localhost:5000/api/lessons/${lessonId}/tests`
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể tải test");
        this.testsByLesson = {
          ...this.testsByLesson,
          [lessonId]: (data || []).map((t) => ({
            ...t,
            editTitle: t.title,
            editTime: t.timeLimitMinutes || 0,
            editAttempts: t.attemptsAllowed || 1,
            editPlacement: !!t.isPlacement,
          })),
        };
      } catch (e) {
        console.error(e);
      }
    },
    // Add Section UX
    promptAddSection() {
      this.addingSection = true;
      this.$nextTick(() => {
        // optional: focus first input
      });
    },
    cancelAddSection() {
      this.addingSection = false;
      this.newSectionTitle = "";
    },
    async saveNewSection() {
      if (!this.newSectionTitle) return;
      try {
        const res = await fetch(
          `http://localhost:5000/api/courses/${this.courseId}/sections`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: this.newSectionTitle }),
          }
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể tạo chương");
        this.cancelAddSection();
        await this.fetchCurriculum();
      } catch (e) {
        alert(e.message);
      }
    },
    async saveSection(section) {
      try {
        const payload = {
          title: section.editTitle,
          sort_order: section.editOrder,
        };
        const res = await fetch(
          `http://localhost:5000/api/sections/${section.id}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );
        const data = await res.json();
        if (!res.ok)
          throw new Error(data.message || "Không thể cập nhật chương");
        await this.fetchCurriculum();
      } catch (e) {
        alert(e.message);
      }
    },
    async deleteSection(section) {
      if (!confirm("Xóa chương này?")) return;
      try {
        const res = await fetch(
          `http://localhost:5000/api/sections/${section.id}`,
          { method: "DELETE" }
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể xóa chương");
        await this.fetchCurriculum();
      } catch (e) {
        alert(e.message);
      }
    },
    // Add Lesson UX
    promptAddLesson(section) {
      section.addingLesson = true;
      section.newLesson = {
        title: "",
        type: "video",
        isPreview: false,
        videoUrl: "",
        durationSeconds: null,
        content: "",
      };
    },
    cancelAddLesson(section) {
      section.addingLesson = false;
    },
    async saveNewLesson(section) {
      if (!section.newLesson.title) return;
      try {
        const payload = {
          title: section.newLesson.title,
          type: section.newLesson.type,
          isPreview: !!section.newLesson.isPreview,
          videoUrl: section.newLesson.videoUrl || undefined,
          durationSeconds: section.newLesson.durationSeconds || undefined,
          content:
            section.newLesson.type === "article"
              ? section.newLesson.content || ""
              : undefined,
        };
        const res = await fetch(
          `http://localhost:5000/api/sections/${section.id}/lessons`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể tạo bài học");
        section.addingLesson = false;
        await this.fetchCurriculum();
      } catch (e) {
        alert(e.message);
      }
    },
    async saveLesson(lesson) {
      try {
        const payload = {
          title: lesson.editTitle,
          type: lesson.editType,
          isPreview: !!lesson.editPreview,
        };
        const res = await fetch(
          `http://localhost:5000/api/lessons/${lesson.id}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );
        const data = await res.json();
        if (!res.ok)
          throw new Error(data.message || "Không thể cập nhật bài học");
        await this.fetchCurriculum();
      } catch (e) {
        alert(e.message);
      }
    },
    async deleteLesson(lesson) {
      if (!confirm("Xóa bài học này?")) return;
      try {
        const res = await fetch(
          `http://localhost:5000/api/lessons/${lesson.id}`,
          { method: "DELETE" }
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể xóa bài học");
        await this.fetchCurriculum();
      } catch (e) {
        alert(e.message);
      }
    },
    async saveNewTest(lesson) {
      try {
        const payload = {
          title: lesson.newTest.title,
          timeLimitMinutes: lesson.newTest.timeLimitMinutes || 0,
          attemptsAllowed: lesson.newTest.attemptsAllowed || 1,
          isPlacement: !!lesson.newTest.isPlacement,
        };
        const res = await fetch(
          `http://localhost:5000/api/lessons/${lesson.id}/tests`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể tạo test");
        lesson.addingTest = false;
        await this.loadTestsForLesson(lesson.id);
      } catch (e) {
        alert(e.message);
      }
    },
    toggleAddTest(lesson) {
      lesson.addingTest = !lesson.addingTest;
      if (lesson.addingTest) {
        lesson.newTest = {
          title: "",
          timeLimitMinutes: 0,
          attemptsAllowed: 1,
          isPlacement: false,
        };
      }
    },
    cancelAddTest(lesson) {
      lesson.addingTest = false;
    },
    async saveTest(t) {
      try {
        const payload = {
          title: t.editTitle,
          timeLimitMinutes: t.editTime,
          attemptsAllowed: t.editAttempts,
          isPlacement: !!t.editPlacement,
        };
        const res = await fetch(`http://localhost:5000/api/tests/${t.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể cập nhật test");
        // refresh tests in this lesson
        if (t.lessonId) await this.loadTestsForLesson(t.lessonId);
      } catch (e) {
        alert(e.message);
      }
    },
    async deleteTest(t) {
      if (!confirm("Xóa bài test này?")) return;
      try {
        const res = await fetch(`http://localhost:5000/api/tests/${t.id}`, {
          method: "DELETE",
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Không thể xóa test");
        Object.keys(this.testsByLesson).forEach((k) => {
          this.testsByLesson[k] = (this.testsByLesson[k] || []).filter(
            (x) => x.id !== t.id
          );
        });
      } catch (e) {
        alert(e.message);
      }
    },
  },
};
</script>

<style scoped>
.course-lessons {
  padding: 20px;
  max-width: 1100px;
  margin: 0 auto;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.actions {
  display: flex;
  gap: 10px;
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
.loading,
.empty {
  text-align: center;
  padding: 16px;
  color: #666;
}
.empty.small {
  padding: 8px;
}

/* Add cards */
.add-card {
  background: #ffffff;
  border: 1px solid #eaeaea;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
}
.add-card.lesson {
  background: #fcfcff;
}
.add-card-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group.full {
  grid-column: 1 / -1;
}
.form-group label {
  font-size: 13px;
  color: #666;
}
.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.form-group textarea {
  resize: vertical;
}
.form-group.align-end {
  align-self: end;
}
.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}

.section {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 16px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.section-title-input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-weight: 600;
}
.section-actions {
  display: flex;
  gap: 8px;
}
.section-expand {
  background: #fcfcff;
  border: 1px solid #eceefe;
  border-radius: 10px;
  padding: 12px;
  margin-top: 10px;
}
.lessons {
  margin-top: 10px;
  padding-left: 10px;
  border-left: 3px solid #f0f0f0;
}
.lesson {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border: 1px solid #f1f1f1;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #fff;
}
.lesson-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.btn.icon {
  padding: 6px;
  min-width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.lesson-title-display {
  font-weight: 600;
  color: #2c3e50;
}
.type-pill {
  background: #f4f6f8;
  color: #546e7a;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
}
.pill.preview-pill {
  background: #fff3e0;
  color: #ef6c00;
}
.spacer {
  flex: 1;
}
.lesson-edit {
  margin: 8px 0;
  padding: 12px;
  background: #fcfcff;
  border: 1px solid #eceefe;
  border-radius: 10px;
}
.lesson-edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.lesson-edit-title {
  font-weight: 600;
  color: #2c3e50;
}
.lesson-title-input,
.lesson-type {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
}
.lesson-left {
  display: grid;
  grid-template-columns: 1fr 200px 140px;
  gap: 12px;
  align-items: end;
}
.lesson-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

/* mini labels */
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field.small {
  min-width: 120px;
}
.mini-label {
  font-size: 11px;
  color: #8a8a8a;
}

/***** tests & questions *****/
.tests {
  margin-top: 8px;
  padding: 10px;
  background: #fafbff;
  border: 1px dashed #e5e7fb;
  border-radius: 10px;
}
.tests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.tests-title {
  font-weight: 600;
  color: #2c3e50;
}
.test-item {
  background: #fff;
  border: 1px solid #eceefe;
  border-radius: 10px;
  padding: 10px;
  margin-top: 8px;
}
.test-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
}
.test-title-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
}
.test-number-input {
  width: 110px;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
}
.pill {
  background: #eef7ff;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 12px;
  display: inline-block;
}
.qcount {
  display: flex;
  align-items: flex-end;
  gap: 6px;
}

.questions {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #eee;
}
.questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.questions-title {
  font-weight: 600;
  color: #2c3e50;
}
.question-item {
  border: 1px solid #f1f1f1;
  border-radius: 8px;
  padding: 8px;
  margin-top: 6px;
  background: #fff;
}
.question-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.badge {
  background: #eef7ff;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}
.q-content {
  flex: 1;
  color: #34495e;
}
.q-meta {
  color: #888;
  font-size: 12px;
}
.choices-list {
  margin: 6px 0 0 18px;
}
.choice {
  color: #555;
}
.choice.correct {
  color: #2e7d32;
  font-weight: 600;
}
.empty.tiny {
  padding: 6px;
  font-size: 13px;
  color: #888;
}
.btn.small {
  padding: 5px 8px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 768px) {
  .lesson-left {
    grid-template-columns: 1fr;
  }
}
</style>
