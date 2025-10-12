# Content Creator - Hướng dẫn sử dụng

## Tổng quan
Content Creator là module cho phép instructor tạo và quản lý nội dung khóa học, bao gồm:
- Câu hỏi trắc nghiệm
- Bài tập lập trình
- Ngân hàng câu hỏi
- Môi trường chạy code online

## Các thành phần chính

### 1. ContentCreator.vue
Component chính chứa 4 tab:
- **Câu hỏi trắc nghiệm**: Tạo và quản lý câu hỏi multiple choice
- **Bài tập Code**: Tạo và quản lý bài tập lập trình
- **Ngân hàng câu hỏi**: Quản lý tập trung tất cả câu hỏi
- **Code Runner**: Môi trường test code online

### 2. QuestionBank.vue
Quản lý ngân hàng câu hỏi với các tính năng:
- Lọc câu hỏi theo khóa học, chương, độ khó
- Tìm kiếm câu hỏi
- Import/Export Excel
- Chế độ xem Grid/List
- Phân trang
- Chọn multiple để xóa

### 3. CodeRunner.vue
Môi trường chạy code online:
- Hỗ trợ JavaScript, Python, Java, C++
- Editor code với syntax highlighting
- Chạy code với input tùy chỉnh
- Chạy test cases tự động
- Hiển thị kết quả chi tiết

### 4. Services

#### contentService.js
Quản lý API calls cho:
- CRUD operations cho questions và coding exercises
- Import/Export functionality
- Validation logic

#### codeExecutionService.js
Xử lý việc chạy code:
- Execute code với các ngôn ngữ khác nhau
- Run test cases
- Format output và error handling

## Hướng dẫn cài đặt

### 1. Thêm routes
Trong `router/index.js`:
```javascript
{
  path: "content-creator",
  name: "InstructorContentCreator",
  component: () => import("../components/Instructor/ContentCreator.vue"),
},
{
  path: "question-bank",
  name: "InstructorQuestionBank",
  component: () => import("../components/Instructor/QuestionBank.vue"),
}
```

### 2. Cập nhật menu
Trong `MenuInstructor.vue`:
```html
<li class="nav-item">
    <router-link to="/instructor/content-creator" class="nav-link">
        ✍️ Content Creator
    </router-link>
</li>
<li class="nav-item">
    <router-link to="/instructor/question-bank" class="nav-link">
        🏦 Question Bank
    </router-link>
</li>
```

### 3. Cài đặt Toast notifications
Trong `main.js`:
```javascript
import ToastPlugin from './plugins/toast.js'
import ToastContainer from './components/common/ToastContainer.vue'

app.use(ToastPlugin)
app.component('ToastContainer', ToastContainer)
```

## Cách sử dụng

### Tạo câu hỏi trắc nghiệm
1. Vào tab "Câu hỏi trắc nghiệm"
2. Click "Thêm câu hỏi mới"
3. Điền thông tin:
   - Chọn khóa học và chương
   - Loại câu hỏi (một/nhiều đáp án)
   - Độ khó
   - Tiêu đề và nội dung
   - Các đáp án (tối thiểu 2, tối đa 6)
   - Giải thích (tùy chọn)
4. Click "Tạo câu hỏi"

### Tạo bài tập code
1. Vào tab "Bài tập Code"
2. Click "Tạo bài tập mới"
3. Điền thông tin:
   - Chọn khóa học và chương
   - Ngôn ngữ lập trình
   - Độ khó
   - Tiêu đề và mô tả
   - Template code cho học sinh
   - Solution code (đáp án)
   - Test cases (ít nhất 1)
   - Gợi ý (tùy chọn)
4. Click "Tạo bài tập"

### Sử dụng Code Runner
1. Vào tab "Code Runner"
2. Chọn ngôn ngữ lập trình
3. Viết code trong editor
4. Chạy code với "Chạy" để test
5. Submit với "Submit" để chạy tất cả test cases

### Quản lý ngân hàng câu hỏi
1. Vào tab "Ngân hàng câu hỏi"
2. Sử dụng filters để lọc câu hỏi
3. Tìm kiếm bằng từ khóa
4. Chọn multiple questions để thực hiện bulk actions
5. Export ra Excel hoặc import từ Excel

## Tính năng nâng cao

### Import/Export Excel
- **Export**: Click "Xuất Excel" để tải file chứa tất cả câu hỏi
- **Import**: Click "Nhập từ Excel", tải template, điền dữ liệu, và upload

### Bulk Operations
- Chọn multiple câu hỏi bằng checkbox
- Click "Chọn tất cả" để chọn tất cả
- Click "Xóa (n)" để xóa các câu hỏi đã chọn

### Code Templates
Code Runner tự động cung cấp template phù hợp cho từng ngôn ngữ:
- **JavaScript**: Function-based template
- **Python**: Function với docstring
- **Java**: Class-based template
- **C++**: Với headers cần thiết

## API Endpoints cần implement

### Questions
```
GET    /api/questions          - Lấy danh sách câu hỏi
POST   /api/questions          - Tạo câu hỏi mới
PUT    /api/questions/:id      - Cập nhật câu hỏi
DELETE /api/questions/:id      - Xóa câu hỏi
POST   /api/questions/bulk-delete - Xóa multiple câu hỏi
GET    /api/questions/export   - Export Excel
POST   /api/questions/import   - Import từ Excel
GET    /api/questions/template - Download template Excel
```

### Coding Exercises
```
GET    /api/coding-exercises          - Lấy danh sách bài tập
POST   /api/coding-exercises          - Tạo bài tập mới
PUT    /api/coding-exercises/:id      - Cập nhật bài tập
DELETE /api/coding-exercises/:id      - Xóa bài tập
```

### Code Execution
```
POST   /api/code/execute       - Chạy code
POST   /api/code/test          - Chạy test cases
GET    /api/code/languages     - Lấy danh sách ngôn ngữ hỗ trợ
```

### Courses & Chapters
```
GET    /api/courses           - Lấy danh sách khóa học
GET    /api/chapters          - Lấy danh sách chương
```

## Troubleshooting

### Lỗi thường gặp

1. **Toast không hiển thị**
   - Kiểm tra ToastPlugin đã được install trong main.js
   - Kiểm tra ToastContainer đã được thêm vào App.vue

2. **Code không chạy được**
   - Kiểm tra API endpoint đã được setup
   - Kiểm tra token authentication
   - Fallback sẽ sử dụng mock data

3. **Import Excel bị lỗi**
   - Đảm bảo file đúng format (.xlsx, .xls)
   - Kiểm tra template có đúng columns không
   - File size không quá 5MB

### Performance Tips

1. **Lazy loading**: Components đã được setup với lazy loading
2. **Pagination**: Question Bank sử dụng pagination để tránh load quá nhiều data
3. **Debounce**: Search được debounce để tránh quá nhiều API calls
4. **Caching**: Service có thể implement caching cho courses/chapters

## Customization

### Thêm ngôn ngữ lập trình mới
1. Update `codeExecutionService.js`:
```javascript
getDefaultLanguages() {
    return [
        // existing languages...
        {
            id: 'go',
            name: 'Go',
            version: '1.19',
            extension: 'go',
            template: 'package main\n\nimport "fmt"\n\nfunc main() {\n    // Your code here\n}'
        }
    ];
}
```

2. Update CSS cho language badge:
```css
.language-badge.go { 
    background: #e0f7fa; 
    color: #00796b; 
}
```

### Tùy chỉnh theme
Các CSS variables có thể được override:
```css
:root {
    --primary-color: #3498db;
    --success-color: #27ae60;
    --error-color: #e74c3c;
    --warning-color: #f39c12;
}
```

## Support
Nếu có vấn đề, vui lòng tạo issue trong repository hoặc liên hệ team phát triển.
