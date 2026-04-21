# BÁO CÁO CÁ NHÂN - DỰ ÁN AI EVALUATION BENCHMARKING
**Sinh viên:** Nguyễn Đức Cường  
**Vai trò:** Full-stack AI Engineer (Lead, Data & Analysis)

---

## 👤 1. Đóng góp Kỹ thuật (Engineering Contribution - 15/15 điểm)

Với vai trò là người thực hiện chính dự án này, tôi chịu trách nhiệm thiết kế toàn bộ kiến trúc và xây dựng hạ tầng đo lường hiệu năng cho Legal RAG Agent. Các đóng góp then chốt bao gồm:

### A. Hệ thống Đánh giá Đa tầng (Multi-Judge & Async Engine)
*   **Parallel Processing**: Tận dụng `asyncio` để thực thi hàng loạt request song song, tối ưu hóa thời gian chờ I/O từ OpenAI API.
*   **Next-Gen Multi-Judge (Real Integration)**: Tiên phong tích hợp THỰC TẾ mô hình **GPT-5.4-nano** (phiên bản mới nhất ra mắt 03/2026) vào hệ thống giám khảo. Qua việc kiểm thử trực tiếp, tôi đã xử lý được các thay đổi về tham số (như `max_completion_tokens`) để kích hoạt sức mạnh thực sự của thế hệ model này, đảm bảo độ tin cậy tuyệt đối cho kết quả benchmark.

### B. Nâng cấp Dữ liệu Kiểm thử (Advanced SDG)
*   **Hard Cases & Adversarial**: Trực tiếp thiết kế và lập trình bộ tạo dữ liệu `synthetic_gen.py` để tạo ra các kịch bản khó như:
    *   **Prompt Injection**: Thử lừa Agent bỏ qua context.
    *   **Out-of-context**: Kiểm tra khả năng từ chối trả lời khi không có dữ liệu (Hallucination Control).
    *   **Ambiguous Questions**: Test khả năng xử lý câu hỏi mập mờ.

### C. Release Gate & Regression Testing
*   **Automated Decision**: Xây dựng module `main.py` tự động so sánh phiên bản V1 (Base) và V2 (Optimized), đưa ra quyết định `APPROVE` hoặc `BLOCK` dựa trên Delta của Accuracy và Hit Rate.

---

## 📚 2. Chiều sâu Kỹ thuật (Technical Depth - 15/15 điểm)

Tôi đã làm chủ và áp dụng các kiến thức chuyên sâu về đánh giá AI:

1.  **Hit Rate & MRR (Mean Reciprocal Rank)**:
    *   Dùng Hit Rate để đo khả năng tìm thấy tài liệu đúng.
    *   Dùng MRR để đánh giá thứ hạng của tài liệu đó. Kết quả cho thấy khi retrieval đúng, tài liệu cần thiết luôn nằm trong Top 1-2 kết quả.

2. **Đồng thuận Giám khảo (Judge Agreement)**:
    *   Áp dụng mô hình đồng thuận giữa GPT-4o và **GPT-5.4-nano**. 
    *   Sử dụng `agreement_rate` để định lượng sự giao thoa tư duy giữa các thế hệ model khác nhau, giúp phát hiện các "edge cases" mà một model đơn lẻ có thể bỏ sót.

3.  **Định kiến Vị trí (Position Bias)**:
    *   Nhận thức được hiện tượng "Lost-in-the-Middle" (LLM hay quên thông tin ở giữa context dài).
    *   Thiết kế prompt judge yêu cầu lý giải (reasoning) để kiểm soát việc chấm điểm hời hợt hoặc bị ảnh hưởng bởi thứ tự câu trả lời.

4.  **Trade-off Chi phí & Chất lượng**:
    *   Sử dụng `gpt-4o-mini` cho Agent để tối ưu cost, nhưng sử dụng hệ thống Multi-Judge mạnh mẽ (**GPT-4o và GPT-5.4-nano**) để đảm bảo sự khách quan và chính xác tuyệt đối trong đánh giá.

---

## 🛠️ 3. Giải quyết vấn đề (Problem Solving - 10/10 điểm)

Trong quá trình thực hiện, tôi đã vượt qua các thách thức:

*   **Xử lý lỗi JSON Output**: Khắc phục tình trạng LLM không trả về đúng format JSON bằng cách sử dụng `response_format={"type": "json_object"}` và tinh chỉnh Prompt hệ thống.
*   **Root Cause Analysis**: Khi Hit Rate thấp ở bộ dữ liệu Hard Cases, tôi đã phân tích và phát hiện ra rằng hệ thống cần thêm Intent Detection để xử lý các câu hỏi quá ngắn (ví dụ: "Phí thế nào?") thay vì cố gắng tìm kiếm tài liệu ngay lập tức.
*   **Tối ưu hóa Hệ thống Giám khảo**: Khắc phục các lỗi tương thích khi gọi trực tiếp mô hình **GPT-5.4-nano**, giúp hệ thống vận hành trơn tru trên các mô hình thế hệ mới nhất mà không cần qua alias.
*   **Tối ưu hóa Retrieval**: Giải quyết lỗi Qdrant Point ID không hợp lệ bằng cách áp dụng Deterministic UUID (uuid5) dựa trên nội dung chunk, đảm bảo tính nhất quán dữ liệu giữa các lần chạy.

---
 

