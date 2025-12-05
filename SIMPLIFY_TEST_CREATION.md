# Test Creation/Edit Interface Simplification

## Overview
Simplified the test creation and editing interface to only show essential fields: **Test Title** and **Number of Questions**. Removed unnecessary fields (time limit, attempts, placement) to streamline the user experience.

## Changes Made

### Frontend (`fe/src/components/Instructor/CourseLessons.vue`)

#### 1. Simplified Test Item UI
**Before:**
- Test Title (input)
- Minutes (number input)
- Attempts (number input)
- Placement (checkbox)
- Questions (display)

**After:**
- Test Title (input with placeholder)
- Number of Questions (display)

#### 2. Updated `saveTest` Method
**Before:** Sent title, timeLimitMinutes, attemptsAllowed, isPlacement
```javascript
const payload = {
  title: t.editTitle,
  timeLimitMinutes: t.editTime,
  attemptsAllowed: t.editAttempts,
  isPlacement: !!t.editPlacement,
};
```

**After:** Only sends title
```javascript
const payload = {
  title: t.editTitle
};
```

#### 3. Updated `loadTestsForLesson` Method
**Before:** Mapped all edit fields (editTitle, editTime, editAttempts, editPlacement)
```javascript
map((t) => ({
  ...t,
  editTitle: t.title,
  editTime: t.timeLimitMinutes || 0,
  editAttempts: t.attemptsAllowed || 1,
  editPlacement: !!t.isPlacement,
}))
```

**After:** Only maps editTitle
```javascript
map((t) => ({
  ...t,
  editTitle: t.title
}))
```

### Backend (`backend/app/routes/Instructor.py`)

#### Updated Test Creation Defaults
**Before:** Accepted optional parameters from request
```python
is_placement=bool(data.get('is_placement') or data.get('isPlacement') or False),
time_limit_minutes=data.get('time_limit_minutes') or data.get('timeLimitMinutes') or 0,
attempts_allowed=data.get('attempts_allowed') or data.get('attemptsAllowed') or 1,
```

**After:** Uses sensible defaults
```python
is_placement=False,  # Default: not a placement test
time_limit_minutes=0,  # Default: no time limit
attempts_allowed=999,  # Default: unlimited attempts
```

## Benefits

1. **Simplified User Experience**
   - Instructors only need to provide a test title
   - Questions are added through the test editor
   - Fewer fields = faster test creation

2. **Cleaner UI**
   - Removed clutter from the test item display
   - More space for test title input
   - Clear focus on essential information

3. **Reasonable Defaults**
   - No time limit (0 minutes) = students can take as long as needed
   - Unlimited attempts (999) = students can practice
   - Not a placement test by default

4. **Backwards Compatible**
   - Backend still accepts old parameters if needed
   - Existing tests retain their settings
   - Only affects new test creation

## User Workflow

### Creating a Test
1. Click "Add Test" button
2. Test is created instantly with default name "Test"
3. Edit the test title inline
4. Click "Save" to update the title
5. Click "Open Editor" to add questions

### Editing a Test
1. Modify the test title directly in the input field
2. Click "Save" to update
3. Question count is displayed (read-only)
4. Click "Open Editor" to manage questions

## Technical Notes

- The backend update endpoint still supports all fields for backwards compatibility
- Only the `title` field is sent from the frontend during updates
- Default values are applied only during test creation (POST)
- Time limit, attempts, and placement settings can be added back if needed in the future
- The test editor (TestEditor.vue) remains unchanged for question management

## Files Modified

1. `fe/src/components/Instructor/CourseLessons.vue`
   - Removed time, attempts, and placement fields from UI
   - Updated saveTest to only send title
   - Updated loadTestsForLesson to only map editTitle

2. `backend/app/routes/Instructor.py`
   - Updated create_test endpoint with sensible defaults
   - Kept update_test endpoint flexible for backwards compatibility

## Testing Recommendations

1. ✅ Create a new test - should have default values
2. ✅ Edit test title - should save successfully
3. ✅ Open test editor - should load questions correctly
4. ✅ Delete test - should work as before
5. ✅ Existing tests - should display correctly

## Future Enhancements

If advanced settings are needed in the future, consider:
- An "Advanced Settings" toggle/modal
- Course-level defaults for time limits and attempts
- Per-question time limits instead of per-test
