# Kết Quả Thực Tế

Thư mục này chứa các kết quả thực tế từ hệ thống khi đã chạy và truy vấn.

## File Trong Thư Mục

- **ACTUAL_RESULTS.md**: Kết quả thực tế - các câu hỏi và câu trả lời thực sự mà hệ thống đã tạo ra. Đây là kết quả thực tế từ hệ thống, không phải ví dụ giả định.

## Cách Xem Kết Quả Thực Tế

### 1. Xem Kết Quả Đã Chạy (Không Cần Chạy Code)

Đọc file `ACTUAL_RESULTS.md` để xem:
- Các câu hỏi và câu trả lời thực tế từ hệ thống
- Format của câu trả lời thực tế
- Thông tin về nguồn và trích dẫn thực tế
- Thống kê thực tế từ hệ thống

### 2. Chạy Ứng Dụng Web (Yêu Cầu Cài Đặt)

Nếu bạn đã có dữ liệu đã lập chỉ mục (đã chạy `COMPLETE_WORKFLOW.ipynb` phần 2), bạn có thể chạy ứng dụng web:

```bash
# Cài đặt dependencies (nếu chưa có)
poetry add streamlit pandas

# Chạy ứng dụng
streamlit run demo_app.py
```

Ứng dụng sẽ mở trong trình duyệt tại `http://localhost:8501` và bạn có thể đặt câu hỏi thực tế.

### 3. Xem Notebook

Mở file `../COMPLETE_WORKFLOW.ipynb` trong Jupyter Notebook để xem quy trình đầy đủ và chạy các truy vấn thực tế.

## Thêm Kết Quả Thực Tế

Nếu bạn muốn thêm kết quả thực tế vào `ACTUAL_RESULTS.md`, hãy:
1. Chạy một số câu hỏi trong notebook hoặc ứng dụng web
2. Sao chép câu hỏi và câu trả lời thực tế từ hệ thống
3. Thêm vào file `ACTUAL_RESULTS.md` để người khác có thể xem kết quả thực tế

