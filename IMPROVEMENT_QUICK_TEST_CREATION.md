# Improvement: Tạo Test Nhanh Với Tên Mặc Định

## 📝 Mô Tả
Cải thiện UX cho việc tạo test: Khi nhấn nút **"Add Test"**, hệ thống sẽ **tạo test ngay lập tức** với tên mặc định là **"Test"** thay vì hiển thị form nhập liệu.

## ❌ Trước Đây
Khi nhấn "Add Test":
1. Hiển thị form với 4 fields:
   - Test Title (required)
   - Time Limit (minutes)
   - Attempts Allowed
   - Placement test (checkbox)
2. User phải nhập tên test
3. Click "Save Test" để tạo
4. Click "Cancel" để hủy

**Nhược điểm**:
- Nhiều bước
- Phải nhập thông tin
- Mất thời gian

## ✅ Sau Khi Sửa
Khi nhấn "Add Test":
1. ✅ Test được tạo ngay lập tức
2. ✅ Tên mặc định: **"Test"**
3. ✅ Time limit: **0** (không giới hạn)
4. ✅ Attempts: **1**
5. ✅ Not a placement test
6. ✅ Có thể edit sau

**Ưu điểm**:
- Nhanh chóng (1 click)
- Không cần nhập thông tin
- Edit sau nếu cần

## 🔧 Changes Made

### File: `fe/src/components/Instructor/CourseLessons.vue`

#### 1. Xóa Form Thêm Test
**Trước:**
```vue
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
```

**Sau:**
```vue
<!-- Form đã được xóa hoàn toàn -->
```

#### 2. Đổi Button Handler
**Trước:**
```vue
<button class="btn small" @click="toggleAddTest(lesson)">Add Test</button>
```

**Sau:**
```vue
<button class="btn small" @click="createTestDirectly(lesson)">Add Test</button>
```

#### 3. Thêm Hàm Tạo Test Trực Tiếp
**Trước:** (3 hàm phức tạp)
```javascript
async saveNewTest(lesson) {
  // Validate input
  // Send request with user input
  // Close form
  // Reload tests
}

toggleAddTest(lesson) {
  // Toggle form visibility
  // Initialize newTest object
}

cancelAddTest(lesson) {
  // Hide form
}
```

**Sau:** (1 hàm đơn giản)
```javascript
async createTestDirectly(lesson) {
  try {
    const headers = this.getAuthHeaders()
    const payload = {
      title: "Test",                // Tên mặc định
      timeLimitMinutes: 0,          // Không giới hạn
      attemptsAllowed: 1,           // 1 lần
      isPlacement: false,           // Không phải placement test
    };
    const res = await fetch(
      `http://localhost:5000/api/lessons/${lesson.id}/tests`,
      {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      }
    );
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Không thể tạo test");
    await this.loadTestsForLesson(lesson.id);
  } catch (e) {
    alert(e.message);
  }
}
```

#### 4. Xóa State Không Cần Thiết
**Trước:**
```javascript
const lessons = (s.lessons || []).map((l) => ({
  ...l,
  expanded: false,
  testsExpanded: false,
  addingTest: false,           // ❌ Xóa
  newTest: {                   // ❌ Xóa
    title: "",
    timeLimitMinutes: 0,
    attemptsAllowed: 1,
    isPlacement: false,
  },
}));
```

**Sau:**
```javascript
const lessons = (s.lessons || []).map((l) => ({
  ...l,
  expanded: false,
  testsExpanded: false,
  // addingTest và newTest đã được xóa
}));
```

## 🎯 Workflow Mới

### Tạo Test
1. Click **"Add Test"** → Test được tạo ngay với tên "Test"
2. Test xuất hiện trong danh sách
3. Edit tên và các thông tin khác nếu cần

### Edit Test
Test vẫn có thể edit như trước:
- **Test Title**: Đổi tên
- **Time Limit**: Thêm giới hạn thời gian
- **Attempts**: Đổi số lần làm
- **Placement**: Đánh dấu là placement test

### Delete Test
Không thay đổi - vẫn có nút Delete

## 📊 So Sánh

| Feature | Trước | Sau |
|---------|-------|-----|
| **Số bước** | 3 bước | 1 bước |
| **Thời gian** | ~10-15s | ~1s |
| **Nhập liệu** | Bắt buộc | Không cần |
| **Form** | Hiển thị | Không có |
| **Tên mặc định** | Không | "Test" |
| **Có thể edit** | ✅ | ✅ |

## 🧪 Test Cases

### Test 1: Tạo Test Mới
**Steps:**
1. Expand một lesson
2. Click "Expand" trong Tests section
3. Click "Add Test"

**Expected:**
- ✅ Test mới xuất hiện ngay lập tức
- ✅ Tên: "Test"
- ✅ Time limit: 0
- ✅ Attempts: 1
- ✅ Không có form pop-up

### Test 2: Edit Test Sau Khi Tạo
**Steps:**
1. Tạo test theo Test 1
2. Edit tên test thành "Chapter 1 Quiz"
3. Đổi time limit = 30
4. Click "Save"

**Expected:**
- ✅ Test được update thành công
- ✅ Tên mới hiển thị đúng

### Test 3: Tạo Nhiều Tests (Nếu Cho Phép)
Hiện tại UI chỉ cho tạo 1 test per lesson (button chỉ hiện khi `length === 0`).

## 📝 Default Values

```javascript
{
  title: "Test",              // Tên test mặc định
  timeLimitMinutes: 0,        // 0 = không giới hạn thời gian
  attemptsAllowed: 1,         // Cho phép làm 1 lần
  isPlacement: false          // Không phải là placement test
}
```

## 💡 Future Improvements

### Option 1: Auto-Generate Sequential Names
```javascript
// Test 1, Test 2, Test 3...
const existingTests = testsByLesson[lesson.id] || [];
const nextNumber = existingTests.length + 1;
const defaultName = `Test ${nextNumber}`;
```

### Option 2: Use Lesson Title
```javascript
// "Python Basics Test", "Variables Test"...
const defaultName = `${lesson.title} Test`;
```

### Option 3: Add Timestamp
```javascript
// "Test (Dec 5, 2025)"
const defaultName = `Test (${new Date().toLocaleDateString()})`;
```

## 🎨 UI Impact

### Before
```
Tests (0)  [Collapse] [Add Test]

┌─────────────────────────────────────┐
│ Add Lesson to: Python Basics        │
├─────────────────────────────────────┤
│ Test Title: [________________]      │
│ Time Limit: [0]                     │
│ Attempts:   [1]                     │
│ ☐ Placement test                    │
│                                      │
│ [Cancel] [Save Test]                │
└─────────────────────────────────────┘

No tests yet
```

### After
```
Tests (0)  [Collapse] [Add Test]  ← Click once

Tests (1)  [Collapse]

┌──────────────────────────────────────────────────┐
│ Test Title: [Test]                               │
│ Minutes: [0]  Attempts: [1]  ☐ Placement         │
│ Questions: (0)                                    │
│ [Save] [Open Editor]                             │
└──────────────────────────────────────────────────┘
```

## ✅ Benefits

1. **⚡ Faster**: 1 click thay vì 3 bước
2. **🎯 Simple**: Không cần suy nghĩ về tên test lúc tạo
3. **✏️ Flexible**: Edit sau khi tạo
4. **🚀 Better UX**: Giảm friction, tăng tốc độ workflow
5. **📱 Mobile-friendly**: Ít tương tác hơn

## 🔧 Technical Details

### API Endpoint
```
POST /api/lessons/{lesson_id}/tests
```

### Request Payload
```json
{
  "title": "Test",
  "timeLimitMinutes": 0,
  "attemptsAllowed": 1,
  "isPlacement": false
}
```

### Response
```json
{
  "id": 123,
  "lessonId": 456,
  "title": "Test",
  "timeLimitMinutes": 0,
  "attemptsAllowed": 1,
  "isPlacement": false,
  "questionCount": 0,
  "createdAt": "2025-12-05T10:30:00Z",
  "updatedAt": "2025-12-05T10:30:00Z"
}
```

---

**Ngày**: 2025-12-05  
**Trạng thái**: ✅ **HOÀN THÀNH**  
**Impact**: UX Improvement  
**Files changed**: 1 (CourseLessons.vue)  
**Lines removed**: ~40 (form template + 3 functions)  
**Lines added**: ~18 (1 simple function)  
**Net change**: -22 lines (simpler code!)  
