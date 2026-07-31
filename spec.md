# AI SPEC — Tính năng AI Nhận diện Ngữ cảnh Slide (Contextual AI Tutor)
Hướng: [x] A — VLearn (Trợ lý Học viên)  [ ] B — Trợ lý Giảng viên  [ ] C — Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job
- **Job executor + workflow:** Học viên đang tự học (self-learning) thông qua tài liệu slide dài trên hệ thống. Workflow: Cuộn đọc slide -> Gặp đoạn khó / dài -> Hỏi AI Tutor.
- **Core JTBD:** "Tôi muốn hiểu nhanh và duy trì mạch đọc liên tục, thay vì phải dừng lại, thoát ra hoặc copy/bôi đen văn bản để hỏi."
- **Problem statement:** Với lượng slide dài, học viên cần duy trì mạch đọc. Tuy nhiên, AI tutor hiện tại "mù" với trang slide học viên đang xem. Việc AI không thể tự động tổng hợp hoặc trích xuất nội dung khiến quá trình học bị đứt đoạn, học viên mất thời gian quay lại tìm kiến thức ở các slide trước hoặc phải bôi đen thủ công rất phiền phức.
- **Evidence (chuẩn B - Mining Data từ 2.522 dòng chatlog):**
  - **Phương pháp đếm:** Lọc file `chat_history_anonymized_for_hackathon.csv` với các từ khoá: *"trang", "slide", "đoạn này", "không có thông tin"*.
  - **Số liệu đếm được:** Có **145 lần** học viên hỏi AI về một trang slide cụ thể, và **100% (145/145)** trường hợp AI trả lời thất bại (do không có ngữ cảnh).
  - **≥5 ví dụ nguyên văn (Quotes):**
    1. *U-102:* "Giải thích cho mình đoạn 2 trang 36 nhé" -> *AI:* "Rất tiếc, tài liệu bài học ngày hôm nay không có thông tin tại trang 36..."
    2. *U-405:* "Slide này thầy viết tắt chữ JTBD là gì vậy?" -> *AI:* "Bạn có thể nói rõ hơn bạn đang xem slide nào không?"
    3. *U-211:* "Ở đây ghi là 3 loại, sao tôi tra google ra 5?" -> *AI:* "Xin lỗi, tôi không rõ 'ở đây' là phần nào trong bài giảng."
    4. *U-089:* "Tóm tắt trang hiện tại" -> *AI:* "Vui lòng copy hoặc gõ lại nội dung bạn cần tóm tắt để tôi hỗ trợ nhé."
    5. *U-332:* "Dòng thứ 2 trang 12 có nghĩa là gì?" -> *AI:* "Hệ thống của tôi không thể xem trực tiếp trang 12..."

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên:**
  | Ứng viên (Giải pháp) | Bao nhiêu người gặp | Tần suất | Mỗi lần tốn gì | Build nổi không | Chọn? |
  |---|---|---|---|---|---|
  | **1. AI tự động đọc ngầm trang slide hiện tại (Context Injection)** | Đa số học viên đọc slide dài | Cao (mỗi trang) | Tốn 0s (liên tục) | Có (Working) | **Chọn** |
  | **2. Bôi đen text để gọi AI giải thích** | Một bộ phận học viên | Vừa | Tốn 5-10s thao tác | Rất dễ | Loại |
  | **3. AI tự sinh câu hỏi Quiz sau mỗi slide** | Mọi học viên | Dày đặc | Tốn 2-3 phút làm quiz | Có thể | Loại |

- **Ứng viên ĐÃ LOẠI + vì sao:** 
  - *Bôi đen text (2):* Giải pháp này giải quyết được vấn đề truyền input cho AI, nhưng UX quá thủ công, làm đứt đoạn mạch đọc (friction cao).
  - *AI sinh Quiz (3):* Đi lệch khỏi JTBD "đọc nhanh không đứt đoạn", tạo thêm việc cho học viên.
- **Ứng viên CHỌN + vì sao:** Chọn (1) vì nó giải quyết triệt để nỗi đau đứt đoạn. AI tự làm ngầm việc đọc text slide, học viên chỉ việc gõ "Tóm tắt" là AI tự hiểu "Tóm tắt cái đang xem ở đây".

## §3. Giải pháp tương tự đã nghiên cứu
- **ChatPDF / Notion AI:** 
  - *Đáng học:* Tốc độ phản hồi nhanh, trích xuất text PDF chuẩn xác.
  - *Đáng né:* Phải tải file PDF lên thủ công, không tích hợp sẵn vào mạch học tập của khoá học. 
  - *Mình khác gì:* AI của nhóm tích hợp thẳng vào màn hình VLearn, tracking chính xác `currentPage` bằng JavaScript (IntersectionObserver) để feed text ngầm, user không cần setup gì.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Khi học viên cuộn đến một trang slide bất kỳ và chat, AI sẽ tự động đọc toàn bộ chữ trên trang đó, ghép vào ngữ cảnh và tóm tắt/trả lời chuẩn xác dưới dạng markdown mà không cần học viên phải copy/bôi đen.
- **Non-goals (≥3 thứ KHÔNG build):** 
  - Không xây dựng AI tự động làm bài tập hộ học viên.
  - Không hỗ trợ đọc Context từ Video (chỉ hỗ trợ PDF/Slide).
  - Không có tính năng tự động chấm điểm (đó là tính năng của Hướng B/C).
- **Mức prototype nhắm tới:** `[x] Working` — Gọi API thật qua Groq (Llama-3), PDF.js render trực tiếp file thật, UI chat chạy thật.
- **Automation:** `[x] Augment` — AI chỉ hỗ trợ tổng hợp thông tin, quyết định học và tiếp thu vẫn thuộc về người dùng (giữ cost-of-error thấp).
- **§4b. Nguyên tắc đã áp dụng:**
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | HAX G2 (Make clear how well it can do) | Hiển thị % Confidence Score và dòng chữ báo "Đang đọc trang X..." |
  | HAX G4 (Show contextual information) | Báo rõ nguồn slide (VD: d1-slide-hackathon.pdf, Tr. 5) dưới câu trả lời |
  | PAIR (Privacy/Security) | System prompt nghiêm cấm lấy data thật của công ty |

## §5 & §6. Lỗi & Bốn đường đi của trải nghiệm
- **Happy path (②):** Học viên cuộn slide 5, chat "Tóm tắt". AI trả về tóm tắt 3 ý chính dạng markdown.
- **Thiếu thông tin (①):** User gõ "hả?". AI không bịa chuyện, lịch sự hỏi lại "Bạn cần hỗ trợ gì ở nội dung trang này?".
- **Ngoài phạm vi (③):** Học viên hỏi "Deadline nộp bài/ Link nộp bài". AI từ chối khéo, nhắc học viên check Discord của khoá học để đảm bảo thông tin logistic chính xác.
- **Case đặc thù domain (④):** Học viên mớm kiến thức sai (VD: "Đề bài có 5 Track đúng ko?"). AI đọc ngữ cảnh slide hiện tại, phát hiện sai và đính chính "Đề bài chỉ có 1 Track duy nhất".

## §7. Kiểm thử
- **Chiều chất lượng:** Độ chính xác ngữ cảnh (Context-awareness) & Tuân thủ luật System Prompt.
- **Golden set:** 20 case bao gồm Happy path, Ngoài lề, Bắt lỗi, Mơ hồ. (Bộ test lưu tại `test_case.json`).
- **Quality bar:** Đạt khi ≥ 90% qua bộ, và không có case nào vi phạm việc tuân thủ data ngoài lề (Leak logistic info).
- **Kết quả các lượt chạy:** Pass **20/20 (100%)**. 

> *(Bảng chi tiết 20 case đã được xuất tự động tại file `eval_results.md` đính kèm trong dự án).*

## §8. Phân công & kế hoạch
- **Phân công có tên:** 
  - **Long:** Làm Spec, Validation, thu thập bằng chứng.
  - **Trung:** Viết System Prompt, thiết kế AI Logic (Golden Set).
  - **Minh:** Build UI, thiết lập System, API Integration (PDF.js + Groq).
- **Willing users (kế hoạch CP5):** Mời 3 bạn (Hoàng Văn Huy, Dương, + 1 bạn cùng Lab) thử trải nghiệm bản Demo thực tế.
  - *Kế hoạch hỏi:* (1) Trải nghiệm cuộn và hỏi AI có mượt không? (2) AI tóm tắt có đúng ý bạn đang đọc không? (3) Mất bao lâu để bạn nắm được slide khó? (Long phụ trách log kết quả).

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 31/07 | Đổi từ HTML Mock tĩnh sang PDF.js render | Giám khảo yêu cầu dùng data thực tế thay vì hardcode. |
| 31/07 | Cập nhật System Prompt bắt chặt Rule | Khắc phục việc AI dễ bị đánh lừa khi user hỏi xin đáp án ngoài lề. |
