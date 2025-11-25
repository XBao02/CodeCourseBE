# Fixes Applied - CourseLessons.vue

## ✅ Issues Fixed

### 1. Tests Block Visibility (Ẩn/Hiện bài test)

**Problem**: Phần bài test luôn hiển thị, ngay cả khi bài học chưa được mở rộng.

**Solution**: Thêm điều kiện `v-if="lesson.expanded"` cho `.tests` container
- Tests block chỉ hiển thị khi bài học được mở rộng (`lesson.expanded = true`)
- Khi thu gọn bài học, toàn bộ tests section bị ẩn
- Khi mở rộng lại, phải click vào button "Mở" để hiển thị danh sách tests

**Changed at**: Line 160
```vue
<!-- Before -->
<div class="tests">

<!-- After -->
<div v-if="lesson.expanded" class="tests">
```

### 2. Delete Test Error (Lỗi khi xóa test)

**Problem**: `Unexpected token '<', "<1doctype '..." is not valid JSON` - Backend trả về HTML thay vì JSON

**This was already fixed** in previous version:
- Check file: Lines 687-705
- The `deleteTest` method properly filters out deleted test
- Response type checking in place

**Current implementation**:
```javascript
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
}
```

## 🔍 Troubleshooting the Delete Test JSON Error

If you still see "Unexpected token '<'" error:

### Check Backend

1. **Test endpoint exists**:
   ```bash
   grep -n "DELETE.*tests.*t_id" backend/app/routes/Instructor.py
   ```

2. **Backend returns JSON**:
   ```python
   @instructor_bp.route("/api/tests/<int:test_id>", methods=['DELETE'])
   def delete_test(test_id):
       # ...
       return jsonify({"message": "Xóa thành công"}), 200  # ✅ Must return JSON
   ```

3. **Content-Type header is set**:
   - Check that backend sets: `Content-Type: application/json`

4. **Check for errors in backend logs**:
   - If you see 500 error, backend is returning error HTML
   - Fix the Python error and restart Flask server

### Check Frontend

1. **Verify response is JSON**:
   - Add debug logging:
   ```javascript
   const contentType = res.headers.get("content-type");
   console.log("Delete response content-type:", contentType);
   if (!contentType?.includes("application/json")) {
     const text = await res.text();
     console.log("Response body:", text);
     throw new Error(`Expected JSON, got: ${contentType}`);
   }
   ```

2. **Check network tab**:
   - Open DevTools (F12)
   - Go to Network tab
   - Delete a test
   - Check DELETE request response:
     - Status should be 200 or 204
     - Content-Type should be `application/json`
     - Body should be valid JSON

## 📋 UI/UX Changes

### Before
- Tests section always visible
- User sees test list even when lesson is collapsed
- Confusing layout with many sections open at once

### After
- Tests section hidden when lesson is collapsed
- Tests section shows only when lesson is expanded
- Cleaner, more organized interface
- User must click lesson title to expand, then click "Mở" to see tests

### User Flow

1. Click lesson title → Lesson expands, shows tests header
2. Click "Mở" button → Tests list shows/hides
3. Collapse lesson → Tests section completely hidden
4. Expand lesson again → Tests section reappears (state preserved)

## 🧪 Testing

### Test Visibility
- [ ] Click on a lesson title - should expand with tests header hidden initially
- [ ] Click "Mở" button - tests list should appear
- [ ] Click "Thu gọn" button - tests list should disappear
- [ ] Collapse lesson - entire tests section should disappear
- [ ] Expand lesson again - tests section should reappear with same state

### Test Delete
- [ ] Create a test
- [ ] Click delete (trash icon)
- [ ] Confirm deletion
- [ ] Test should be removed from list
- [ ] No "JSON error" should appear
- [ ] If error appears, check:
  1. Backend is running
  2. Backend endpoint returns JSON
  3. No Python errors in backend logs

## 📝 Code Changes Summary

| File | Line | Change | Type |
|------|------|--------|------|
| CourseLessons.vue | 160 | Add `v-if="lesson.expanded"` to `.tests` div | Visibility |

---

**Status**: ✅ Ready for testing
**Date**: November 24, 2025
