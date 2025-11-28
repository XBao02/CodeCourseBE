<template>
<div class="course-lessons">
    <div class="header">
      <h1>Course Content Management</h1>
      <div class="actions">
        <button class="btn" @click="goBack">Back</button>
        <button class="btn primary" @click="promptAddSection">Add Section</button>
      </div>
    </div>

    <!-- Add Section Inline Card -->
    <div v-if="addingSection" class="add-card">
      <div class="add-card-title">Add New Section</div>
      <div class="form-row">
        <div class="form-group">
          <label>Section Title</label>
          <input v-model.trim="newSectionTitle" type="text" placeholder="e.g., Introduction, Variables & Data Types..." />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn" @click="cancelAddSection">Cancel</button>
        <button class="btn primary" :disabled="!newSectionTitle" @click="saveNewSection">Save Section</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading curriculum...</div>
    <div v-else>
      <div v-if="sections.length === 0" class="empty">No sections yet. Add your first section.</div>

      <div v-for="section in sections" :key="section.id" class="section">
        <div class="section-header">
          <input v-model="section.editTitle" class="section-title-input" />
          <div class="section-actions">
            <button class="btn" @click="saveSection(section)">Save</button>
            <button class="btn danger" @click="deleteSection(section)">Delete</button>
            <button class="btn" @click="promptAddLesson(section)">Add Lesson</button>
          </div>
        </div>

        <!-- Add Lesson Inline Card -->
        <div v-if="section.addingLesson" class="add-card lesson">
          <div class="add-card-title">Add Lesson to: {{ section.editTitle || section.title }}</div>
          <div class="form-row">
            <div class="form-group">
              <label>Lesson Title</label>
              <input v-model.trim="section.newLesson.title" type="text" placeholder="e.g., Environment Setup, For Loops..." />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Lesson Type</label>
              <select v-model="section.newLesson.type">
                <option value="video">Video</option>
                <option value="quiz">Quiz</option>
              </select>
            </div>
            <div class="form-group align-end">
              <label class="checkbox"><input type="checkbox" v-model="section.newLesson.isPreview" /> Allow Preview</label>
            </div>
          </div>
          <div class="form-row" v-if="section.newLesson.type === 'video'">
            <div class="form-group">
              <label>Video URL</label>
              <input v-model.trim="section.newLesson.videoUrl" type="text" placeholder="https://..." />
            </div>
            <!-- Upload to Drive -->
            <div class="form-group">
              <label>Or upload a video</label>
              <input type="file" accept="video/*" @change="onUploadNewVideo(section, $event)" :disabled="newVideoUploadingSectionId===section.id" />
              <small v-if="newVideoUploadingSectionId===section.id">Uploading to Google Drive...</small>
            </div>
          </div>
          <div v-if="section.newLesson.videoUrl" class="form-row">
            <div class="form-group full">
              <label>Preview</label>
              <video :src="section.newLesson.videoUrl" controls style="max-width:100%;border-radius:8px;" />
            </div>
          </div>
          <div class="form-actions">
            <button class="btn" @click="cancelAddLesson(section)">Cancel</button>
            <button class="btn primary" :disabled="!section.newLesson.title" @click="saveNewLesson(section)">Save Lesson</button>
          </div>
        </div>

        <div class="lessons">
          <div v-if="(lessonsBySection[section.id] || []).length === 0" class="empty small">No lessons yet</div>
          <div v-for="lesson in lessonsBySection[section.id] || []" :key="lesson.id" class="lesson">
            <!-- Compact lesson header -->
            <div class="lesson-top">
              <button class="btn icon" @click="lesson.expanded = !lesson.expanded" :title="lesson.expanded ? 'Collapse' : 'Expand'">
                <i :class="lesson.expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                <span class="btn-text">{{ lesson.expanded ? 'Collapse' : 'Expand' }}</span>
              </button>
              <div class="lesson-title-display">{{ lesson.editTitle || lesson.title }}</div>
              <span class="type-pill">{{ lesson.editType || lesson.type }}</span>
              <span v-if="lesson.editPreview || lesson.isPreview" class="pill preview-pill">Preview</span>
              <div class="spacer"></div>
              <button class="btn danger" @click="deleteLesson(lesson)">Delete</button>
            </div>

            <!-- Editable details -->
            <div v-if="lesson.expanded" class="lesson-edit">
              <div class="lesson-edit-header">
                <div class="lesson-edit-title">Edit Lesson</div>
                <button class="btn icon" @click="lesson.expanded = false" title="Close editor">
                  <i class="fas fa-times"></i>
                  <span class="btn-text">Close</span>
                </button>
              </div>
              <div class="lesson-left">
                <div class="field">
                  <div class="mini-label">Title</div>
                  <input v-model="lesson.editTitle" class="lesson-title-input" />
                </div>
                <div class="field">
                  <div class="mini-label">Type</div>
                  <select v-model="lesson.editType" class="lesson-type">
                    <option value="video">Video</option>
                    <option value="quiz">Quiz</option>
                  </select>
                </div>
                <div class="field">
                  <div class="mini-label">Preview</div>
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
                    <label>Or upload a video</label>
                    <input type="file" accept="video/*" @change="onUploadLessonVideo(lesson, $event)" :disabled="!!videoUploading[lesson.id]" />
                    <small v-if="videoUploading[lesson.id]">Uploading to Google Drive...</small>
                  </div>
                </div>
                <div v-if="lesson.editVideoUrl" class="form-row">
                  <div class="form-group full">
                    <label>Preview</label>
                    <video :src="lesson.editVideoUrl" controls style="max-width:100%;border-radius:8px;" />
                  </div>
                </div>
              </div>
              <div class="lesson-actions">
                <button class="btn" @click="saveLesson(lesson)">Save</button>
              </div>
            </div>

            <!-- Tests block -->
            <div v-if="lesson.expanded" class="tests">
              <div class="tests-header">
                <div class="tests-title">Tests ({{ (testsByLesson[lesson.id] || []).length }})</div>
                <div class="tests-actions">
                  <button class="btn small" @click="lesson.testsExpanded = !lesson.testsExpanded" :title="lesson.testsExpanded ? 'Collapse tests' : 'Expand tests'">
                    <i :class="lesson.testsExpanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                    {{ lesson.testsExpanded ? 'Collapse' : 'Expand' }}
                  </button>
                  <button class="btn small" v-if="lesson.testsExpanded" @click="toggleAddTest(lesson)">Add Test</button>
                  <button class="btn small ai-btn" v-if="lesson.testsExpanded" @click="openAIQuizGenerator(lesson)" :disabled="aiGenerating" :title="aiGenerating ? 'Generating questions...' : 'Generate with AI'">
                    <i :class="aiGenerating ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i> {{ aiGenerating ? 'Generating...' : 'Generate with AI' }}
                  </button>
                </div>
              </div>

              <div v-if="lesson.testsExpanded">
                <div v-if="lesson.addingTest" class="add-card test">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Test Title</label>
                      <input v-model.trim="lesson.newTest.title" type="text" placeholder="e.g., Chapter 1 Quiz" />
                    </div>
                    <div class="form-group">
                      <label>Time Limit (minutes)</label>
                      <input v-model.number="lesson.newTest.timeLimitMinutes" type="number" min="0" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Attempts Allowed</label>
                      <input v-model.number="lesson.newTest.attemptsAllowed" type="number" min="1" />
                    </div>
                    <div class="form-group align-end">
                      <label class="checkbox"><input type="checkbox" v-model="lesson.newTest.isPlacement" /> Placement test</label>
                    </div>
                  </div>
                  <div class="form-actions">
                    <button class="btn" @click="cancelAddTest(lesson)">Cancel</button>
                    <button class="btn primary" :disabled="!lesson.newTest.title" @click="saveNewTest(lesson)">Save Test</button>
                  </div>
                </div>

                <div v-if="(testsByLesson[lesson.id] || []).length === 0" class="empty tiny">No tests yet</div>
                <div v-for="t in testsByLesson[lesson.id] || []" :key="t.id" class="test-item">
                  <div class="test-row">
                    <div class="field" style="flex:1">
                      <div class="mini-label">Test Title</div>
                      <input v-model="t.editTitle" class="test-title-input" />
                    </div>
                    <div class="field small">
                      <div class="mini-label">Minutes</div>
                      <input v-model.number="t.editTime" class="test-number-input" type="number" min="0" title="Minutes" />
                    </div>
                    <div class="field small">
                      <div class="mini-label">Attempts</div>
                      <input v-model.number="t.editAttempts" class="test-number-input" type="number" min="1" title="Attempts allowed" />
                    </div>
                    <div class="field">
                      <div class="mini-label">Placement</div>
                      <label class="checkbox"><input type="checkbox" v-model="t.editPlacement" /> Placement</label>
                    </div>
                    <div class="field qcount">
                      <div class="mini-label">Questions</div>
                      <div class="pill">{{ t.questionCount || 0 }}</div>
                    </div>
                    <button class="btn" @click="saveTest(t)">Save</button>
                    <button class="btn danger" @click="deleteTest(t)">Delete</button>
                    <button class="btn" @click="openTestEditor(t)">Open Editor</button>
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
          <h3>Generate Questions with AI</h3>
          <button class="ai-close-btn" @click="closeAIQuizModal"><i class="fas fa-times"></i></button>
        </div>

        <div class="ai-modal-body">
          <!-- Config Section -->
          <div v-if="!aiQuizGenerated" class="ai-config">
            <div class="form-group">
              <label>Lesson Title</label>
              <input v-model="aiQuizConfig.lesson_title" type="text" placeholder="e.g., For Loops in Python" readonly />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Number of Questions</label>
                <input v-model.number="aiQuizConfig.num_questions" type="number" min="1" max="20" />
              </div>
              <div class="form-group">
                <label>Difficulty</label>
                <select v-model="aiQuizConfig.difficulty">
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn" @click="closeAIQuizModal">Cancel</button>
              <button class="btn primary ai-generate-btn" @click="generateAIQuestions" :disabled="aiGenerating">
                <i :class="aiGenerating ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i>
                {{ aiGenerating ? 'Generating...' : 'Generate Questions' }}
              </button>
            </div>
          </div>

          <!-- Generated Questions Section -->
          <div v-else class="ai-questions">
            <div class="ai-success-message">
              <i class="fas fa-check-circle"></i> Generated {{ generatedQuestions.length }} questions!
            </div>

            <div v-for="(q, qIndex) in generatedQuestions" :key="qIndex" class="ai-question-card">
              <div class="ai-question-header">
                <span class="q-number">Question {{ qIndex + 1 }}</span>
                <button class="btn-small" @click="toggleQuestionPreview(qIndex)" :title="expandedQuestions.includes(qIndex) ? 'Collapse' : 'Expand'">
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
                  <strong>Explanation:</strong> {{ q.explanation }}
                </div>

                <div class="q-actions">
                  <button class="btn-small danger" @click="removeQuestion(qIndex)">
                    <i class="fas fa-trash"></i> Delete
                  </button>
                  <button class="btn-small" @click="regenerateQuestion(qIndex)" :disabled="aiGenerating">
                    <i class="fas fa-redo"></i> Regenerate
                  </button>
                </div>
              </div>
            </div>

            <div class="ai-final-actions">
              <button class="btn" @click="resetAIQuizModal">Reset</button>
              <button class="btn danger" @click="closeAIQuizModal">Cancel</button>
              <button class="btn primary" @click="saveGeneratedQuestions" :disabled="generatedQuestions.length === 0">
                <i class="fas fa-save"></i> Save Questions
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
      newVideoUploadingSectionId: null,
      videoUploading: {},
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
        console.log("Saving section:", section.id, payload);
        
        const res = await fetch(
          `http://localhost:5000/api/sections/${section.id}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );
        
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.message || `Failed to update section (${res.status})`);
        }
        
        const data = await res.json();
        console.log("Section saved successfully:", data);
        alert("✅ Section updated successfully!");
        await this.fetchCurriculum();
      } catch (e) {
        console.error("Error saving section:", e);
        alert(`❌ Error: ${e.message}\n\nPlease make sure the backend is running on http://localhost:5000`);
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
    async uploadToDrive(file) {
      const form = new FormData();
      form.append('file', file);
      // Optional: form.append('folder_id', '<YOUR_FOLDER_ID>')
      const res = await fetch('http://localhost:5000/api/upload/video', {
        method: 'POST',
        body: form,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.message || `Upload failed (HTTP ${res.status})`);
      // Prefer direct downloadable URL for video src
      return data.downloadUrl || data.viewUrl;
    },
    async onUploadNewVideo(section, evt) {
      const file = evt.target.files && evt.target.files[0];
      if (!file) return;
      try {
        this.newVideoUploadingSectionId = section.id;
        const url = await this.uploadToDrive(file);
        section.newLesson.videoUrl = url;
        this.$toast?.success('Uploaded video');
      } catch (e) {
        console.error(e);
        this.$toast?.error(e.message || 'Upload failed');
        alert(e.message || 'Upload failed');
      } finally {
        this.newVideoUploadingSectionId = null;
        evt.target.value = '';
      }
    },
    async onUploadLessonVideo(lesson, evt) {
      const file = evt.target.files && evt.target.files[0];
      if (!file) return;
      try {
        this.$set ? this.$set(this.videoUploading, lesson.id, true) : (this.videoUploading = { ...this.videoUploading, [lesson.id]: true });
        const url = await this.uploadToDrive(file);
        lesson.editVideoUrl = url;
        this.$toast?.success('Uploaded video');
      } catch (e) {
        console.error(e);
        this.$toast?.error(e.message || 'Upload failed');
        alert(e.message || 'Upload failed');
      } finally {
        if (this.$delete) this.$delete(this.videoUploading, lesson.id); else { const { [lesson.id]:_, ...rest } = this.videoUploading; this.videoUploading = rest; }
        evt.target.value = '';
      }
    },
  }
}
</script>

<style scoped>
/* ==================== MODERN DESIGN SYSTEM ==================== */
.course-lessons {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
  background: #f8f9fa;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* ==================== HEADER DESIGN ==================== */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.5px;
  color: #1a1a1a;
}

.actions {
  display: flex;
  gap: 12px;
}

/* ==================== MODERN BUTTON SYSTEM ==================== */
.btn {
  padding: 10px 20px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
  background: white;
  color: #374151;
  text-decoration: none;
  user-select: none;
}

.btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.btn:active {
  transform: scale(0.98);
}

.btn.primary {
  background: #1f2937;
  color: white;
  border-color: #1f2937;
}

.btn.primary:hover {
  background: #111827;
  border-color: #111827;
}

.btn.danger {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

.btn.danger:hover {
  background: #dc2626;
  border-color: #dc2626;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f3f4f6;
}

.btn:disabled:hover {
  background: #f3f4f6;
  border-color: #e5e7eb;
}

/* ==================== STATUS STATES ==================== */
.loading,
.empty {
  text-align: center;
  padding: 40px 20px;
  color: #666;
  font-size: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin: 24px 0;
}

.empty {
  border: 2px dashed #d1d5db;
  background: #fafafa;
}

.empty.small {
  padding: 20px;
  font-size: 14px;
}

.empty.tiny {
  padding: 16px;
  font-size: 13px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.loading::before {
  content: '';
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #1f2937;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ==================== ADD CARD COMPONENTS ==================== */
.add-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
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
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 20px;
  font-size: 16px;
}

/* ==================== FORM SYSTEM ==================== */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: white;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1f2937;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
  line-height: 1.5;
}

.form-group.align-end {
  align-self: end;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #1f2937;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

/* ==================== SECTION COMPONENTS ==================== */
.section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.section-title-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-weight: 600;
  font-size: 16px;
  background: white;
  transition: all 0.2s ease;
}

.section-title-input:focus {
  outline: none;
  border-color: #1f2937;
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
  margin-top: 16px;
  padding-left: 16px;
  border-left: 3px solid #e5e7eb;
}

.lesson {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.lesson:hover {
  border-color: #d1d5db;
}

.lesson-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn.icon {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-radius: 6px;
  background: white;
  border: 1px solid #e5e7eb;
  color: #666;
  transition: all 0.2s ease;
  font-size: 14px;
}

.btn.icon .btn-text {
  display: inline;
  font-size: 13px;
  font-weight: 500;
}

.btn.icon:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.lesson-title-display {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 15px;
}

.type-pill {
  background: #f3f4f6;
  color: #666;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.pill.preview-pill {
  background: #fef3c7;
  color: #d97706;
}

.spacer {
  flex: 1;
}
/* ==================== LESSON EDIT INTERFACE ==================== */
.lesson-edit {
  margin: 16px 0;
  padding: 20px;
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
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

/* ==================== TEST SYSTEM (Simplified Orange Theme) ==================== */
.tests {
  margin-top: 24px;
  padding: 20px;
  background: #fffaf5; /* soft warm background */
  border: 1px solid #fcd9b6; /* light orange border */
  border-radius: 12px;
  position: relative;
}

.tests::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: #f59e0b; /* accent bar */
  border-radius: 12px 12px 0 0;
}

.tests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #fcd9b6;
}

.tests-title {
  font-weight: 600;
  color: #b45309; /* darker orange for text */
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.3px;
  text-transform: none;
}

/* remove emoji before */
.tests-title::before { content: none; }

.test-item {
  background: #ffffff;
  border: 1px solid #f5d2a8;
  border-radius: 10px;
  padding: 16px;
  margin-top: 12px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.test-item:hover {
  border-color: #f59e0b;
  background: #fff7ed; /* subtle highlight */
}

.test-title-input,
.test-number-input {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: none;
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 500;
  background: #ffffff;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.test-title-input:focus,
.test-number-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.25);
  transform: none;
}

.pill {
  background: #fff7ed;
  color: #b45309;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 12px;
  border: 1px solid #fdba74;
  letter-spacing: 0.3px;
  box-shadow: none;
  text-transform: uppercase;
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
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
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
  border-color: #1f2937;
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
  background: #1f2937;
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
  background: #1f2937;
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
