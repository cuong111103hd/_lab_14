# Failure Analysis Report - AI Evaluation Factory (Real GPT-5.4 Run)

## 1. Tổng quan kết quả Benchmark thực tế (REAL GPT-5.4-nano)

Báo cáo này được cập nhật dựa trên kết quả chạy thực tế với mô hình **GPT-5.4-nano** (không thông qua alias):

| Chỉ số | V1 Baseline | V2 Optimized | Nhận xét |
| :--- | ---: | ---: | :--- |
| **Tổng số Test Cases** | 50 | 50 | Bộ dữ liệu Hard Cases chuẩn Expert. |
| **Avg Accuracy Score** | 2.75 | 3.51 | **V2 vượt trội vượt ngưỡng (+0.76)** trên hệ giám khảo thế hệ mới. |
| **Hit Rate** | 0.42 | 0.46 | Phản ánh đúng đặc thù bộ dữ liệu adversarial. |
| **Agreement Rate** | 0.74 | 0.88 | **GPT-5.4-nano** cho thấy độ ổn định cực cao khi đánh giá các case tối ưu. |
| **Quyết định Release** | - | **APPROVE** | Hệ thống đạt trạng thái sẵn sàng phát hành. |

---

## 2. Phân tích Giám khảo Thế hệ mới

Việc sử dụng trực tiếp **GPT-5.4-nano** (chụp được trong môi trường Lab 2026) cho thấy:

*   **Tính khách quan cao:** Mô hình gpt-5.4-nano có xu hướng chấm điểm "nghiêm khắc" hơn ở V1 (2.75) nhưng lại đánh giá rất cao sự tiến bộ ở V2 (3.51).
*   **Lý giải (Reasoning) sắc bén:** Các judge-reasoning trong `benchmark_results.json` cho thấy GPT-5.4-nano có khả năng bóc tách các lỗi logic nhỏ nhất trong câu trả lời của Agent.

---

## 3. Failure Clustering & Root Cause

**Cluster chính:** "Strict Policy Adherence Failure" (Lỗi tuân thủ nghiêm ngặt chính sách).

### 5 Whys Analysis (Case #2689)
**Vấn đề:** Agent từ chối tính toán lương theo giờ.

1. **Why 1:** Tại sao Agent không thực hiện phép tính?  
   - Vì Agent báo "Không tìm thấy thông tin" thay vì áp dụng công thức từ Luật.
2. **Why 2:** Tại sao Agent lại báo không thấy thông tin?  
   - Vì Prompt của V2 yêu cầu Agent bám sát 100% tài liệu trích lục.
3. **Why 3:** Tại sao Prompt lại yêu cầu bám sát 100%?  
   - Để đảm bảo tính pháp lý, tránh trường hợp Agent tự ý sáng tạo thông tin.
4. **Why 4:** Tại sao không cung cấp công cụ tính toán?  
   - Vì Knowledge Base hiện tại chỉ chứa văn bản thô, chưa có các module logic hỗ trợ tính toán.
5. **Why 5 (Root Cause):** **Thiếu sự tách biệt giữa "Thông tin luật" và "Công cụ thực thi luật" trong kiến trúc Agent hiện tại.**

---

## 4. Hành động tiếp theo (Action Plan)

*   **V3 Development:** Tích hợp bộ Tool/Function Calling cho các tác vụ tính toán pháp lý.
*   **Safety Audit:** Tiếp tục sử dụng GPT-5.4-nano để rà soát các lỗ hổng an toàn trong Prompt Injection.
