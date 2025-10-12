# 📊 Admin Reports - Báo cáo và Thống kê Hệ thống

## Tổng quan

Trang Admin Reports cung cấp các báo cáo và thống kê chi tiết về hoạt động của hệ thống học trực tuyến, bao gồm:

- 📈 **Thống kê tổng quan**: Người dùng, khóa học, doanh thu
- 📚 **Báo cáo khóa học**: Tỉ lệ hoàn thành, đánh giá, top khóa học
- 💰 **Báo cáo doanh thu**: Theo tháng/quý/năm với export Excel/PDF

## Cấu trúc Files

```
fe/src/
├── components/Admin/Reports.vue          # Component chính
├── services/reportService.js             # Service xử lý API
└── ADMIN_REPORTS_README.md              # File này
```

## Chi tiết các Tab

### 1. Tab Tổng quan 📊

**Thống kê tổng quan:**
- 👥 Tổng số người dùng
- 📚 Tổng số khóa học
- 💰 Tổng doanh thu
- 📊 Tỉ lệ hoàn thành trung bình

**Biểu đồ:**
- Số lượng học viên đăng ký theo tháng (Bar Chart)
- Tỷ lệ Học viên / Giảng viên (Pie Chart)

### 2. Tab Khóa học 📚

**Thống kê khóa học:**
- 📚 Tổng số khóa học
- ✅ Số khóa học hoàn thành
- ⭐ Đánh giá trung bình

**Biểu đồ:**
- Tỉ lệ hoàn thành khóa học (Doughnut Chart)
- Phân bố đánh giá theo sao (Bar Chart)

**Bảng dữ liệu:**
- 🏆 Top khóa học được đánh giá cao nhất
- Thông tin: Tên khóa học, giảng viên, đánh giá, số học viên, tỉ lệ hoàn thành

### 3. Tab Doanh thu 💰

**Tính năng chính:**
- Bộ lọc theo thời gian: Tháng, Quý, Năm
- Export báo cáo Excel/PDF
- Tổng doanh thu theo kỳ đã chọn

**Biểu đồ:**
- Biểu đồ đường doanh thu theo thời gian

**Bảng dữ liệu:**
- Chi tiết doanh thu theo kỳ
- Số đơn hàng, trung bình/đơn, tỷ lệ tăng trưởng

## Sử dụng ReportService

### Import Service

```javascript
import reportService from '@/services/reportService';
```

### Các API Methods

```javascript
// Lấy thống kê tổng quan
const overview = await reportService.getOverviewStats();

// Lấy thống kê khóa học
const courseStats = await reportService.getCourseStats();

// Lấy top khóa học được đánh giá cao
const topCourses = await reportService.getTopRatedCourses(5);

// Lấy dữ liệu doanh thu
const revenueData = await reportService.getRevenueData('monthly');

// Export báo cáo
const exportResult = await reportService.exportReport('excel', 'monthly');
```

### Utility Functions

```javascript
// Format tiền tệ
const formatted = reportService.formatCurrency(1000000);
// => "1.000.000 ₫"

// Tính tăng trưởng
const growth = reportService.calculateGrowth(1200, 1000);
// => "20.0"

// Lấy màu cho biểu đồ
const colors = reportService.getChartColors();
```

## Tính năng Loading & Error Handling

- ⏳ Loading states cho từng tab
- 🔄 Auto-refresh khi chuyển tab
- ❌ Error handling với fallback data
- 📊 Chart destruction và recreation

## Tính năng Export

### Export Excel
```javascript
await reportService.exportReport('excel', 'monthly');
```

### Export PDF
```javascript
await reportService.exportReport('pdf', 'quarterly');
```

## Responsive Design

- 📱 Responsive trên mobile, tablet, desktop
- 📊 Charts tự động điều chỉnh kích thước
- 📋 Tables responsive với horizontal scroll

## Customization

### Thêm biểu đồ mới

1. Thêm canvas element vào template
2. Tạo chart trong `initCharts()` function
3. Add destroy logic cho cleanup

### Thêm thống kê mới

1. Cập nhật mock data trong `reportService.js`
2. Thêm API method mới
3. Update component để hiển thị data

### Thêm export format mới

1. Cập nhật `exportReport()` method
2. Add button trong template
3. Handle download logic

## Mock Data Structure

Service sử dụng mock data với cấu trúc:

```javascript
const mockData = {
  overview: { totalUsers, totalCourses, totalRevenue, averageCompletion },
  courseStats: { total, completed, averageRating, completionRate },
  topRatedCourses: [{ id, name, instructor, rating, students, completion }],
  revenue: {
    monthly: { labels, data, orders, details },
    quarterly: { labels, data, orders, details },
    yearly: { labels, data, orders, details }
  }
};
```

## Performance

- ⚡ Lazy loading cho charts
- 🔄 Chart caching và reuse
- 📊 Data caching trong component
- 🚀 Async data loading với Promise.all

## Browser Support

- ✅ Chrome, Firefox, Safari, Edge (modern versions)
- 📊 Chart.js support cho older browsers
- 🎨 Bootstrap 5 styling compatibility

## Troubleshooting

### Charts không hiển thị
- Kiểm tra canvas elements có tồn tại
- Verify Chart.js đã được import
- Check console cho errors

### Data không load
- Kiểm tra reportService import
- Verify mock data structure
- Check network/async errors

### Export không hoạt động
- Kiểm tra browser download permissions
- Verify blob URL generation
- Check file size limits
