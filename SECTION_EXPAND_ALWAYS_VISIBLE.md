# Section Expand - Always Visible Layout

## ✅ Changes Applied

### Section Expand Form - Always Visible

**Problem**: Phần chỉnh sửa chương bị ẩn, phải click mở rộng mới thấy

**Solution**: 
- Xóa điều kiện `v-if="section.expanded"` khỏi section-expand div
- Phần form chỉnh sửa chương (tiêu đề, thứ tự hiển thị) **luôn hiển thị suyên suốt**
- Xóa nút "Đóng" khỏi form (vì không cần nữa)
- Giữ lại nút "Lưu thay đổi"

### Expand Button - Purpose Changed

**From**: "Mở rộng/Thu gọn chương"  
**To**: "Mở rộng/Thu gọn danh sách bài học"

**Purpose**: 
- Mở rộng (`expanded = true`) → Hiển thị danh sách bài học
- Thu gọn (`expanded = false`) → Ẩn danh sách bài học (chỉ hiện tiêu đề bài học compactly)

## 📐 New Layout Structure

```
┌─────────────────────────────────────────┐
│ Section Header (Tiêu đề + buttons)      │
├─────────────────────────────────────────┤
│ Section Expand Form (LUÔN VISIBLE)      │
│ - Tiêu đề chương                        │
│ - Thứ tự hiển thị                       │
│ - Nút Lưu thay đổi                      │
├─────────────────────────────────────────┤
│ Add Lesson Card (if adding)             │
├─────────────────────────────────────────┤
│ Lessons List (if expanded)              │
│ - Lesson 1 header                       │
│ - Lesson 2 header                       │
│ - Lesson 3 header                       │
└─────────────────────────────────────────┘
```

## 🔄 User Flow

### Before
1. Click "Mở rộng chương" → Hiện form + danh sách bài học
2. Click "Thu gọn chương" → Ẩn form + danh sách bài học

### After
1. Form luôn hiển thị
2. Click "Mở rộng" → Hiện danh sách bài học
3. Click "Thu gọn" → Ẩn danh sách bài học
4. Dễ chỉnh sửa thông tin chương mà không cần expand

## 💡 Design Benefits

✅ **Tiếp cận dễ dàng**
- Form chỉnh sửa chương luôn visible
- Không cần tìm nút mở rộng

✅ **Giảm bước thao tác**
- Xem/sửa chương info ngay lập tức
- Chỉ expand khi muốn xem/quản lý bài học

✅ **Giao diện rõ ràng**
- Phân cấp thông tin rõ ràng
- Form + danh sách không trộn lẫn

## 📋 CSS Notes

Section-expand vẫn giữ nguyên CSS compact:
```css
.section-expand {
  padding: 16px;
  margin-top: 12px;
}

.section-expand .form-row {
  margin-bottom: 12px;
}

.section-expand .form-actions {
  margin-top: 12px;
  padding-top: 12px;
}
```

## 🧪 Testing Checklist

- [ ] Open courses page
- [ ] Navigate to lessons of any course
- [ ] Verify section header visible with title and buttons
- [ ] Verify section form (tiêu đề, thứ tự) visible below header
- [ ] Click "Mở rộng" → Lessons list appears
- [ ] Click "Thu gọn" → Lessons list disappears
- [ ] Form still visible when lessons collapsed
- [ ] Can edit section title/order without expanding lessons
- [ ] Verify "Lưu thay đổi" button saves changes

## 📝 Code Changes

| Part | Before | After |
|------|--------|-------|
| section-expand | `v-if="section.expanded"` | Always visible (no v-if) |
| Expand button | "Mở rộng chương" | "Mở rộng danh sách bài học" |
| Close button | Inside form | Removed |
| Form visibility | Only when expanded | Always visible |

---

**Status**: ✅ Ready to test
**Date**: November 24, 2025
