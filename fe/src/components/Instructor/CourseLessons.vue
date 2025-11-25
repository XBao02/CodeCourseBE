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
            <button class="btn" @click="saveSection(section)"><i class="fas fa-save"></i> Lưu</button>
            <button class="btn danger" @click="deleteSection(section)"><i class="fas fa-trash"></i> Xóa</button>
            <button class="btn" @click="promptAddLesson(section)"><i class="fas fa-plus"></i> Thêm bài học</button>
          </div>
        </div>

        <!-- Add Lesson Inline Card -->
        <div v-if="section.addingLesson" class="add-card lesson">
          <div class="add-card-title">Thêm bài học vào: {{ section.editTitle || section.title }}</div>
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
                <option value="quiz">Quiz</option>
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
              <button class="btn icon" @click="lesson.expanded = !lesson.expanded" :title="lesson.expanded ? 'Thu gọn bài học' : 'Mở rộng bài học'">
                <i :class="lesson.expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                <span class="btn-text">{{ lesson.expanded ? 'Thu gọn' : 'Mở rộng' }}</span>
              </button>
              <div class="lesson-title-display">{{ lesson.editTitle || lesson.title }}</div>
              <span class="type-pill">{{ lesson.editType || lesson.type }}</span>
              <span v-if="lesson.editPreview || lesson.isPreview" class="pill preview-pill">Preview</span>
              <div class="spacer"></div>
              <button class="btn danger" @click="deleteLesson(lesson)"><i class="fas fa-trash"></i></button>
            </div>

            <!-- Editable details -->
            <div v-if="lesson.expanded" class="lesson-edit">
              <div class="lesson-edit-header">
                <div class="lesson-edit-title"><i class="fas fa-edit"></i> Chỉnh sửa bài học</div>
                <button class="btn icon" @click="lesson.expanded = false" title="Đóng trình chỉnh sửa">
                  <i class="fas fa-times"></i>
                  <span class="btn-text">Đóng</span>
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
                    <option value="quiz">Quiz</option>
                  </select>
                </div>
                <div class="field">
                  <div class="mini-label">Xem trước</div>
                  <label class="preview"><input type="checkbox" v-model="lesson.editPreview" /> Preview</label>
                </div>
              </div>
              
              <!-- Video specific fields -->
              <div v-if="lesson.editType === 'video'" class="lesson-video-fields">
                <div class="form-row">
                  <div class="form-group">
                    <label>Video URL</label>
                    <input v-model="lesson.editVideoUrl" type="url" placeholder="https://..." />
                  </div>
                  <div class="form-group">
                    <label>Thời lượng (giây)</label>
                    <input v-model.number="lesson.editDurationSeconds" type="number" min="0" placeholder="600" />
                  </div>
                </div>
              </div>
              <div class="lesson-actions">
                <button class="btn" @click="saveLesson(lesson)"><i class="fas fa-save"></i> Lưu</button>
              </div>
            </div>

            <!-- Tests block -->
            <div v-if="lesson.expanded" class="tests">
              <div class="tests-header">
                <div class="tests-title">Bài test ({{ (testsByLesson[lesson.id] || []).length }})</div>
                <div class="tests-actions">
                  <button class="btn small" @click="lesson.testsExpanded = !lesson.testsExpanded" :title="lesson.testsExpanded ? 'Thu gọn danh sách bài test' : 'Mở rộng danh sách bài test'">
                    <i :class="lesson.testsExpanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                    {{ lesson.testsExpanded ? 'Thu gọn' : 'Mở' }}
                  </button>
                  <button class="btn small" v-if="lesson.testsExpanded" @click="toggleAddTest(lesson)"><i class="fas fa-plus"></i> Thêm test</button>
                  <button class="btn small ai-btn" v-if="lesson.testsExpanded" @click="openAIQuizGenerator(lesson)" :disabled="aiGenerating" :title="aiGenerating ? 'Đang tạo câu hỏi...' : 'Tạo câu hỏi bằng AI'">
                    <i :class="aiGenerating ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i> {{ aiGenerating ? 'Đang tạo...' : 'Tạo bằng AI' }}
                  </button>
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

    <!-- AI Quiz Generator Modal -->
    <div v-if="showAIQuizModal" class="ai-modal-overlay">
      <div class="ai-modal-content">
        <div class="ai-modal-header">
          <h3><i class="fas fa-magic"></i> Tạo Câu Hỏi Bằng AI</h3>
          <button class="ai-close-btn" @click="closeAIQuizModal"><i class="fas fa-times"></i></button>
        </div>

        <div class="ai-modal-body">
          <!-- Config Section -->
          <div v-if="!aiQuizGenerated" class="ai-config">
            <div class="form-group">
              <label>Tiêu đề bài học</label>
              <input v-model="aiQuizConfig.lesson_title" type="text" placeholder="VD: Vòng lặp for trong Python" readonly />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Số lượng câu hỏi</label>
                <input v-model.number="aiQuizConfig.num_questions" type="number" min="1" max="20" />
              </div>
              <div class="form-group">
                <label>Độ khó</label>
                <select v-model="aiQuizConfig.difficulty">
                  <option value="easy">Dễ</option>
                  <option value="medium">Trung bình</option>
                  <option value="hard">Khó</option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn" @click="closeAIQuizModal">Hủy</button>
              <button class="btn primary ai-generate-btn" @click="generateAIQuestions" :disabled="aiGenerating">
                <i :class="aiGenerating ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i>
                {{ aiGenerating ? 'Đang tạo...' : 'Tạo Câu Hỏi' }}
              </button>
            </div>
          </div>

          <!-- Generated Questions Section -->
          <div v-else class="ai-questions">
            <div class="ai-success-message">
              <i class="fas fa-check-circle"></i> Đã tạo {{ generatedQuestions.length }} câu hỏi!
            </div>

            <div v-for="(q, qIndex) in generatedQuestions" :key="qIndex" class="ai-question-card">
              <div class="ai-question-header">
                <span class="q-number">Câu {{ qIndex + 1 }}</span>
                <button class="btn-small" @click="toggleQuestionPreview(qIndex)" :title="expandedQuestions.includes(qIndex) ? 'Thu gọn' : 'Mở rộng'">
                  <i :class="expandedQuestions.includes(qIndex) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                </button>
              </div>

              <div v-if="expandedQuestions.includes(qIndex)" class="ai-question-details">
                <div class="q-text">{{ q.question }}</div>

                <div class="q-options">
                  <div v-for="(opt, optIndex) in q.options" :key="optIndex" class="q-option" :class="{ correct: q.correctAnswer === optIndex }">
                    <span class="option-letter">{{ String.fromCharCode(65 + optIndex) }}</span>
                    <span class="option-text">{{ opt }}</span>
                    <span v-if="q.correctAnswer === optIndex" class="correct-badge"><i class="fas fa-check"></i></span>
                  </div>
                </div>

                <div class="q-explanation">
                  <strong>Giải thích:</strong> {{ q.explanation }}
                </div>

                <div class="q-actions">
                  <button class="btn-small danger" @click="removeQuestion(qIndex)">
                    <i class="fas fa-trash"></i> Xóa
                  </button>
                  <button class="btn-small" @click="regenerateQuestion(qIndex)" :disabled="aiGenerating">
                    <i class="fas fa-redo"></i> Tạo lại
                  </button>
                </div>
              </div>
            </div>

            <div class="ai-final-actions">
              <button class="btn" @click="resetAIQuizModal">Tạo Lại</button>
              <button class="btn danger" @click="closeAIQuizModal">Hủy</button>
              <button class="btn primary" @click="saveGeneratedQuestions" :disabled="generatedQuestions.length === 0">
                <i class="fas fa-save"></i> Lưu Câu Hỏi
              </button>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="aiError" class="ai-error-message">
            <i class="fas fa-exclamation-circle"></i> {{ aiError }}
          </div>
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
      // AI Quiz states
      showAIQuizModal: false,
      aiGenerating: false,
      aiError: null,
      aiQuizGenerated: false,
      aiQuizConfig: {
        lesson_title: "",
        num_questions: 5,
        difficulty: "medium",
      },
      generatedQuestions: [],
      expandedQuestions: [],
      selectedLessonForAI: null,
    };
  },
  async mounted() {
    console.log('CourseLessons component mounted');
    console.log('Route params:', this.$route.params);
    this.courseId = Number(this.$route.params.id);
    console.log('Course ID:', this.courseId);
    if (!this.courseId || isNaN(this.courseId)) {
      console.error('Invalid course ID:', this.courseId);
      alert('ID khóa học không hợp lệ');
      this.$router.push('/instructor/courses');
      return;
    }
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
        const url = `http://localhost:5000/api/courses/${this.courseId}/curriculum`;
        console.log('Fetching curriculum from:', url);
        const res = await fetch(url);
        console.log('Response status:', res.status);
        const data = await res.json();
        console.log('Response data:', data);
        if (!res.ok)
          throw new Error(data.message || "Không thể tải curriculum");
        // clone and attach edit and add fields
        this.sections = (data || []).map((s) => ({
          ...s,
          editTitle: s.title,
          editOrder: s.sortOrder || 0,
          addingLesson: false,
          newLesson: {
            title: "",
            type: "video",
            isPreview: false,
            videoUrl: "",
            durationSeconds: null,
          },
        }));
        const map = {};
        this.sections.forEach((s) => {
          const lessons = (s.lessons || []).map((l) => ({
            ...l,
            editTitle: l.title,
            editType: l.type,
            editPreview: !!l.isPreview,
            editVideoUrl: l.videoUrl || '',
            editDurationSeconds: l.durationSeconds || null,
            expanded: false,
            testsExpanded: false,
            addingTest: false,
            newTest: {
              title: "",
              timeLimitMinutes: 0,
              attemptsAllowed: 1,
              isPlacement: false,
            },
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
        console.error('Error fetching curriculum:', e);
        alert(`Lỗi khi tải curriculum: ${e.message}`);
        // Set empty state so UI still shows
        this.sections = [];
        this.lessonsBySection = {};
        this.testsByLesson = {};
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
        
        // Add type-specific fields
        if (lesson.editType === 'video') {
          payload.videoUrl = lesson.editVideoUrl || undefined;
          payload.durationSeconds = lesson.editDurationSeconds || undefined;
        }
        
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
    // AI Quiz Methods
    openAIQuizGenerator(lesson) {
      this.selectedLessonForAI = lesson;
      this.aiQuizConfig = {
        lesson_title: lesson.editTitle || lesson.title,
        num_questions: 5,
        difficulty: "medium",
      };
      this.showAIQuizModal = true;
      this.aiQuizGenerated = false;
      this.generatedQuestions = [];
      this.expandedQuestions = [];
      this.aiError = null;
    },
    async generateAIQuestions() {
      if (!this.aiQuizConfig.lesson_title) {
        this.aiError = "Tiêu đề bài học không được để trống";
        return;
      }

      this.aiGenerating = true;
      this.aiError = null;

      try {
        const payload = {
          lesson_title: this.aiQuizConfig.lesson_title,
          num_questions: this.aiQuizConfig.num_questions,
          difficulty: this.aiQuizConfig.difficulty,
        };

        const res = await fetch("http://localhost:5000/api/ai/quiz/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (!res.ok || !data.questions) {
          throw new Error(data.error || "Lỗi khi tạo câu hỏi");
        }

        this.generatedQuestions = data.questions || [];
        this.aiQuizGenerated = true;
        
        // Tự động mở rộng tất cả câu hỏi
        this.expandedQuestions = this.generatedQuestions.map((_, i) => i);
      } catch (e) {
        console.error("Error generating AI questions:", e);
        this.aiError = e.message || "Lỗi không xác định khi tạo câu hỏi";
      } finally {
        this.aiGenerating = false;
      }
    },
    toggleQuestionPreview(qIndex) {
      const idx = this.expandedQuestions.indexOf(qIndex);
      if (idx > -1) {
        this.expandedQuestions.splice(idx, 1);
      } else {
        this.expandedQuestions.push(qIndex);
      }
    },
    removeQuestion(qIndex) {
      this.generatedQuestions.splice(qIndex, 1);
      this.expandedQuestions = this.expandedQuestions
        .filter(i => i !== qIndex)
        .map(i => i > qIndex ? i - 1 : i);
    },
    async regenerateQuestion(qIndex) {
      this.aiGenerating = true;
      this.aiError = null;

      try {
        const payload = {
          lesson_title: this.aiQuizConfig.lesson_title,
          num_questions: 1,
          difficulty: this.aiQuizConfig.difficulty,
        };

        const res = await fetch("http://localhost:5000/api/ai/quiz/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (!res.ok || !data.questions || data.questions.length === 0) {
          throw new Error(data.error || "Lỗi khi tạo lại câu hỏi");
        }

        this.generatedQuestions[qIndex] = data.questions[0];
      } catch (e) {
        console.error("Error regenerating question:", e);
        this.aiError = e.message || "Lỗi khi tạo lại câu hỏi";
      } finally {
        this.aiGenerating = false;
      }
    },
    resetAIQuizModal() {
      this.aiQuizGenerated = false;
      this.generatedQuestions = [];
      this.expandedQuestions = [];
      this.aiError = null;
    },
    closeAIQuizModal() {
      this.showAIQuizModal = false;
      this.resetAIQuizModal();
    },
    async saveGeneratedQuestions() {
      if (this.generatedQuestions.length === 0) {
        alert("Không có câu hỏi nào để lưu");
        return;
      }

      if (!this.selectedLessonForAI) {
        alert("Không có bài học được chọn");
        return;
      }

      // Tạo test từ câu hỏi được tạo
      const testTitle = `${this.aiQuizConfig.lesson_title} - Quiz (AI)`;
      const lesson = this.selectedLessonForAI;

      try {
        // Tạo test
        const testPayload = {
          title: testTitle,
          timeLimitMinutes: this.generatedQuestions.length * 3, // ~3 phút/câu
          attemptsAllowed: 1,
          isPlacement: false,
        };

        console.log("Creating test with payload:", testPayload);
        const testRes = await fetch(
          `http://localhost:5000/api/lessons/${lesson.id}/tests`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(testPayload),
          }
        );

        console.log("Test response status:", testRes.status);
        console.log("Test response headers:", testRes.headers);
        
        // Check if response is JSON
        const contentType = testRes.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          const text = await testRes.text();
          console.error("Invalid response type. Expected JSON, got:", contentType);
          console.error("Response body:", text);
          throw new Error(`Server returned invalid response: ${contentType}. Check backend logs.`);
        }

        const testData = await testRes.json();
        console.log("Test data:", testData);
        if (!testRes.ok) throw new Error(testData.message || "Không thể tạo test");

        const testId = testData.id;
        console.log("Created test with ID:", testId);

        // Lưu từng câu hỏi vào test
        for (const q of this.generatedQuestions) {
          // Build choices array với đáp án đúng được đánh dấu
          const choices = q.options.map((opt, idx) => ({
            content: opt,
            text: opt,
            is_correct: q.correctAnswer === idx,
            isCorrect: q.correctAnswer === idx,
            sort_order: idx,
          }));

          const qPayload = {
            type: 'single_choice',
            content: q.question,
            points: 1,
            choices: choices,
          };

          console.log("Creating question with payload:", qPayload);
          const qRes = await fetch(
            `http://localhost:5000/api/tests/${testId}/questions`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(qPayload),
            }
          );

          console.log("Question response status:", qRes.status);
          console.log("Question response headers:", qRes.headers);
          
          // Check if response is JSON
          const qContentType = qRes.headers.get("content-type");
          if (!qContentType || !qContentType.includes("application/json")) {
            const text = await qRes.text();
            console.error("Invalid question response type. Expected JSON, got:", qContentType);
            console.error("Response body:", text);
            throw new Error(`Server returned invalid response: ${qContentType}. Check backend logs.`);
          }
          
          if (!qRes.ok) {
            const errData = await qRes.json();
            console.error("Error saving question:", errData);
            throw new Error(errData.message || "Lỗi khi lưu câu hỏi");
          }
          console.log("Question saved successfully");
        }

        // Close modal immediately without showing alert
        this.closeAIQuizModal();
        await this.loadTestsForLesson(lesson.id);
      } catch (e) {
        alert(`Lỗi khi lưu câu hỏi: ${e.message}`);
      }
    },
  },
};
</script>

<style scoped>
/* ==================== MODERN DESIGN SYSTEM ==================== */
.course-lessons {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* Background pattern */
.course-lessons::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(120, 200, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}
/* ==================== HEADER DESIGN ==================== */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 32px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px;
  color: white;
  box-shadow: 
    0 20px 40px rgba(102, 126, 234, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(20px);
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 30% 40%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  letter-spacing: -0.5px;
  position: relative;
  z-index: 1;
  color: white;
}

.actions {
  display: flex;
  gap: 16px;
  position: relative;
  z-index: 1;
}

/* ==================== MODERN BUTTON SYSTEM ==================== */
.btn {
  padding: 14px 24px;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-height: 48px;
  text-decoration: none;
  user-select: none;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.btn:active {
  transform: translateY(-1px);
  transition: transform 0.1s;
}

.btn.primary {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.btn.primary:hover {
  background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
  box-shadow: 0 16px 40px rgba(79, 70, 229, 0.4);
  transform: translateY(-4px) scale(1.02);
}

.btn.danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.btn.danger:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  box-shadow: 0 16px 40px rgba(239, 68, 68, 0.4);
  transform: translateY(-4px) scale(1.02);
}

.btn:not(.primary):not(.danger) {
  background: rgba(255, 255, 255, 0.9);
  color: #374151;
  border: 2px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.btn:not(.primary):not(.danger):hover {
  background: rgba(255, 255, 255, 1);
  color: #1f2937;
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  filter: grayscale(100%);
}

.btn:disabled:hover {
  transform: none;
  box-shadow: none;
}
/* ==================== STATUS STATES ==================== */
.loading,
.empty {
  text-align: center;
  padding: 60px 40px;
  color: #6b7280;
  font-size: 18px;
  font-weight: 500;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  margin: 24px 0;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.empty {
  border: 3px dashed #cbd5e1;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.empty.small {
  padding: 24px 20px;
  font-size: 14px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: linear-gradient(135deg, #fefefe 0%, #f8fafc 100%);
}

.loading::before {
  content: '';
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ==================== ADD CARD COMPONENTS ==================== */
.add-card {
  background: white;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(20px);
}

.add-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #667eea;
}

.add-card:hover {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.add-card.lesson {
  background: linear-gradient(135deg, #fefcff 0%, #f8faff 100%);
  border-color: #e0e7ff;
}

.add-card.test {
  background: linear-gradient(135deg, #fffef7 0%, #fefce8 100%);
  border-color: #fef3c7;
}

.add-card-title {
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 24px;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.add-card-title::before {
  content: '✨';
  font-size: 24px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}
/* ==================== FORM SYSTEM ==================== */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 14px;
  color: #374151;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 16px 20px;
  border: 3px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s ease;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  font-weight: 500;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 
    0 0 0 4px rgba(79, 70, 229, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.form-group.align-end {
  align-self: end;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: #374151;
  font-weight: 600;
  padding: 12px 0;
}

.checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: #4f46e5;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px solid #f3f4f6;
}

/* ==================== SECTION COMPONENTS ==================== */
.section {
  background: white;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 24px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(20px);
}



.section:hover {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  transform: translateY(-6px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f1f5f9;
}

.section-title-input {
  flex: 1;
  padding: 16px 20px;
  border: 3px solid #e5e7eb;
  border-radius: 16px;
  font-weight: 700;
  font-size: 18px;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-title-input:focus {
  outline: none;
  border-color: #4f46e5;
  background: white;
  box-shadow: 
    0 0 0 4px rgba(79, 70, 229, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.section-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.section-expand {
  background: linear-gradient(135deg, #fefcff 0%, #f8faff 100%);
  border: 3px solid #e0e7ff;
  border-radius: 20px;
  padding: 16px;
  margin-top: 12px;
  animation: slideDown 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(79, 70, 229, 0.1);
}

@keyframes slideDown {
  from { 
    opacity: 0; 
    transform: translateY(-20px) scale(0.95); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0) scale(1); 
  }
}

.section-expand .form-row {
  margin-bottom: 12px;
}

.section-expand .form-actions {
  margin-top: 12px;
  padding-top: 12px;
}
/* ==================== LESSON COMPONENTS ==================== */
.lessons {
  margin-top: 24px;
  padding-left: 24px;
  border-left: 6px solid #e0e7ff;
  position: relative;
}

.lesson {
  background: white;
  border: 3px solid #f8fafc;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.lesson::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981, #06b6d4, #8b5cf6);
  opacity: 0;
  transition: all 0.3s ease;
}

.lesson:hover {
  border-color: #cbd5e1;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.lesson:hover::before {
  opacity: 1;
}

.lesson-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.btn.icon {
  padding: 12px 16px;
  min-width: 44px;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  color: #64748b;
  transition: all 0.3s ease;
  font-size: 16px;
}

.btn.icon .btn-text {
  display: inline;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.btn.icon:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border-color: #4f46e5;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3);
  transform: translateY(-2px) scale(1.05);
}

.lesson-title-display {
  font-weight: 700;
  color: #1f2937;
  font-size: 16px;
  letter-spacing: -0.2px;
}

.type-pill {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  padding: 6px 16px;
  border-radius: 25px;
  font-size: 13px;
  font-weight: 600;
  border: 2px solid #93c5fd;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
}

.pill.preview-pill {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  border: 2px solid #fbbf24;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.2);
}

.spacer {
  flex: 1;
}
/* ==================== LESSON EDIT INTERFACE ==================== */
.lesson-edit {
  margin: 24px 0;
  padding: 32px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 3px solid #e2e8f0;
  border-radius: 20px;
  animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.lesson-edit::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #4f46e5;
}

@keyframes slideIn {
  from { 
    opacity: 0; 
    transform: translateY(-20px) scale(0.98); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0) scale(1); 
  }
}

.lesson-edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 3px solid #e2e8f0;
}

.lesson-edit-title {
  font-weight: 800;
  color: #1e293b;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.lesson-edit-title i {
  color: #4f46e5;
  font-size: 22px;
}

.lesson-title-input,
.lesson-type {
  padding: 16px 20px;
  border: 3px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  background: white;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.lesson-title-input:focus,
.lesson-type:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 
    0 0 0 4px rgba(79, 70, 229, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.lesson-left {
  display: grid;
  grid-template-columns: 2fr 200px 140px;
  gap: 20px;
  align-items: end;
  margin-bottom: 24px;
}

.lesson-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 3px solid #e2e8f0;
}
/* ==================== LESSON CONTENT FIELDS ==================== */
.lesson-video-fields,
.lesson-article-fields {
  margin-top: 24px;
  padding: 24px;
  background: white;
  border: 3px solid #e0e7ff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(224, 231, 255, 0.3);
  position: relative;
}

.lesson-video-fields::before {
  content: '🎥';
  position: absolute;
  top: -12px;
  left: 20px;
  background: white;
  padding: 0 8px;
  font-size: 20px;
}

.lesson-article-fields::before {
  content: '📝';
  position: absolute;
  top: -12px;
  left: 20px;
  background: white;
  padding: 0 8px;
  font-size: 20px;
}

.lesson-video-fields .form-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 0;
}

.lesson-article-fields .form-group {
  margin-bottom: 0;
}

.lesson-article-fields textarea {
  width: 100%;
  padding: 16px 20px;
  border: 3px solid #e2e8f0;
  border-radius: 12px;
  resize: vertical;
  min-height: 140px;
  font-size: 15px;
  line-height: 1.6;
  background: white;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.lesson-article-fields textarea:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 
    0 0 0 4px rgba(79, 70, 229, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* ==================== FIELD LABELS ==================== */
.field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field.small {
  min-width: 160px;
}

.mini-label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 4px;
}

/* ==================== TEST SYSTEM ==================== */
.tests {
  margin-top: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
  border: 3px solid #fbbf24;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(251, 191, 36, 0.2);
  position: relative;
}

.tests::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #f59e0b;
  border-radius: 16px 16px 0 0;
}

.tests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #fbbf24;
}

.tests-title {
  font-weight: 800;
  color: #92400e;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tests-title::before {
  content: '📝';
  font-size: 22px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.test-item {
  background: white;
  border: 3px solid #fed7aa;
  border-radius: 16px;
  padding: 24px;
  margin-top: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative;
}

.test-item:hover {
  border-color: #fb923c;
  box-shadow: 0 12px 32px rgba(251, 146, 60, 0.2);
  transform: translateY(-2px);
}

.test-row {
  display: flex;
  gap: 20px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.test-title-input {
  flex: 1;
  padding: 14px 18px;
  border: 3px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  background: white;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.test-title-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 
    0 0 0 4px rgba(245, 158, 11, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.test-number-input {
  width: 140px;
  padding: 14px 18px;
  border: 3px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  background: white;
  transition: all 0.3s ease;
  font-weight: 600;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.test-number-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 
    0 0 0 4px rgba(245, 158, 11, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.pill {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  padding: 8px 16px;
  border-radius: 25px;
  font-weight: 700;
  font-size: 13px;
  display: inline-block;
  border: 2px solid #93c5fd;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
}

/* ==================== AI QUIZ STYLES ==================== */
.ai-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3) !important;
}

.ai-btn:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 24px rgba(102, 126, 234, 0.4) !important;
}

.ai-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.ai-modal-content {
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  max-width: 800px;
  width: 90%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-modal-header {
  padding: 24px;
  border-bottom: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 24px 24px 0 0;
}

.ai-modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s;
}

.ai-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.ai-modal-body {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.ai-config {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-config .form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.ai-config .form-group input,
.ai-config .form-group select {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s;
}

.ai-config .form-group input:focus,
.ai-config .form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.ai-config .form-group input:read-only {
  background: #f5f5f5;
  cursor: not-allowed;
}

.ai-config .form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

.ai-generate-btn {
  min-width: 180px;
}

.ai-success-message {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.ai-questions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-question-card {
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s;
}

.ai-question-card:hover {
  border-color: #667eea;
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.1);
}

.ai-question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.q-number {
  font-weight: 700;
  color: #667eea;
  font-size: 14px;
}

.btn-small {
  padding: 6px 12px;
  background: #e5e7eb;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.btn-small:hover {
  background: #d1d5db;
  transform: scale(1.05);
}

.btn-small.danger {
  background: #fee2e2;
  color: #dc2626;
}

.btn-small.danger:hover {
  background: #fecaca;
}

.ai-question-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.q-text {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  font-size: 15px;
  line-height: 1.5;
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.q-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  transition: all 0.3s;
}

.q-option:hover {
  border-color: #667eea;
}

.q-option.correct {
  background: #f0fdf4;
  border-color: #10b981;
}

.option-letter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #667eea;
  color: white;
  border-radius: 6px;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}

.q-option.correct .option-letter {
  background: #10b981;
}

.option-text {
  flex: 1;
  color: #374151;
  font-size: 14px;
}

.correct-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  flex-shrink: 0;
}

.q-explanation {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  color: #92400e;
  margin-bottom: 12px;
}

.q-explanation strong {
  color: #b45309;
}

.q-actions {
  display: flex;
  gap: 8px;
}

.ai-final-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

.ai-error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 16px 20px;
  border-radius: 12px;
  margin-top: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
   border: 2px solid #fca5a5;
}
</style>
