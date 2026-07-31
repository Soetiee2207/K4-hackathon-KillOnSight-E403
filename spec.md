# AI SPEC — VLearn Tutor: Tổng hợp kiến thức slide · Nhóm KillOnSight · Zone E403
Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job

- **Job executor:** Học viên đang đọc tài liệu trong buổi học (self-learning trên VLearn).
- **Workflow:** Học viên mở slide trên VLearn → đọc slide lần lượt → gặp đoạn không hiểu hoặc muốn ôn lại → cần tổng hợp/tóm tắt nội dung từ nhiều trang → hiện tại phải bôi đen đoạn text mới hỏi tutor, hoặc tua lại slide thủ công.
- **Core JTBD (không tên sản phẩm/AI):** Tổng hợp nhanh nội dung từ nhiều trang slide đã học mà không phải rời khỏi trang đang đọc, để giữ mạch đọc liên tục.
- **Problem statement (KHÔNG chữ AI):** Học viên đang self-learning với lượng slide dài (30-44 trang/buổi) cần duy trì mạch đọc, nhưng khi muốn ôn lại hoặc tổng hợp kiến thức từ các trang trước, phải tự tua slide thủ công — gây đứt mạch đọc, mất thời gian, và dễ bỏ sót kiến thức liên kết.

### Evidence

**Đường A — Khảo sát (đang thu thập, mục tiêu ≥20 người):**

| Thời gian | Người trả lời | Nội dung phản hồi |
|---|---|---|
| 30/07/2026 15:01:15 | Hoàng Văn Huy (21-24 tuổi) | "Thứ tôi thấy không hài lòng là VLearn Tutor trả lời không đáp ứng được nhu cầu của người dùng" |
| 30/07/2026 14:54:38 | Dương (21-24 tuổi) | Mong muốn: "Adaptive learning, socratic AI" |

**Đường B — Mining data (từ chatlog VLearn thật):**

Phản hồi thực tế của VLearn Tutor hiện tại khi học viên yêu cầu đọc nội dung slide:

> "Rất tiếc, tài liệu bài học ngày hôm nay không có thông tin tại trang 36. Bạn có thể kiểm tra lại số trang hoặc đặt câu hỏi về nội dung cụ thể mà bạn đang muốn tìm hiểu không? Tôi sẽ hỗ trợ bạn tra cứu."

→ Tutor hiện tại **không thể đọc slide** và **không thể tổng hợp nội dung** khi học viên yêu cầu theo số trang. Học viên bắt buộc phải bôi đen đoạn text mới hỏi được → đứt mạch đọc.

- **Phương pháp đếm:** Đếm số hội thoại trong chatlog mà học viên yêu cầu tóm tắt/tổng hợp slide nhưng tutor không đáp ứng được.
- *(Đang mining — cập nhật trước CP4)*

## §2. Impact & quyết định chọn

| Ứng viên | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi | Chọn? |
|---|---|---|---|---|---|
| **① Tổng hợp kiến thức nhiều trang slide** | ~1.000 HV (toàn khoá) | Mỗi buổi học (6 buổi) | 5-10' tua slide + mất mạch đọc | Có — prompt + slide data | **✓ Chọn** |
| ② Phát hiện lỗ hổng kiến thức cá nhân | ~1.000 HV | Cuối mỗi buổi | Không biết mình hiểu sai | Cần data quiz + history | Loại |
| ③ Bản đồ lỗ hổng lớp cho giảng viên | ~5 GV | Sau mỗi buổi | 30' tổng hợp thủ công | Cần aggregate pipeline | Loại |

- **Ứng viên ĐÃ LOẠI:**
  - ② Phát hiện lỗ hổng cá nhân — cần dữ liệu quiz history mà data pack không có, build không kịp trong sự kiện.
  - ③ Bản đồ lỗ hổng lớp — ít người dùng trực tiếp (chỉ GV), tần suất thấp, cần aggregate pipeline phức tạp.
- **Ứng viên CHỌN:** ① — ảnh hưởng ~1.000 HV × 6 buổi × 5-10' mỗi lần = **tiết kiệm 30.000–60.000 phút/khoá**. Build được trong sự kiện vì chỉ cần slide data + LLM call.

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm | Flow | Đáng học | Đáng né | Mình khác gì |
|---|---|---|---|---|
| **NotebookLM** | Upload tài liệu → hỏi → trả lời có cite nguồn | Luôn cite nguồn cạnh câu trả lời, tạo cảm giác tin cậy | Không tích hợp vào flow học, phải rời trang | Tích hợp trực tiếp vào trang đọc slide, không rời flow |
| **ChatGPT** | Copy-paste nội dung → hỏi → trả lời | Trả lời linh hoạt, hỗ trợ nhiều loại câu hỏi | Không có context tài liệu, dễ bịa | Có context slide cụ thể, trả lời dựa trên tài liệu khoá học |
| **VLearn Tutor hiện tại** | Bôi đen đoạn text → hỏi → trả lời kèm trích dẫn | Trả lời kèm trích dẫn [trang N] | Phải bôi đen mới hỏi được, không tổng hợp nhiều trang | Hỗ trợ prompt tự do: "tóm tắt trang 2–5" mà không cần bôi đen |

## §4. Thiết kế

- **Lát cắt MỘT CÂU:** Một học viên đang self-learning trên VLearn muốn tổng hợp kiến thức từ trang 2 đến trang 5 → AI đọc nội dung các trang đó và tóm tắt dạng markdown có trích dẫn [trang N] → học viên hiểu nhanh mà không rời trang đang đọc.

- **Non-goals (≥3 thứ KHÔNG build):**
  1. Không làm quiz/kiểm tra hiểu bài
  2. Không làm chức năng dịch sang ngôn ngữ khác
  3. Không làm recommendation engine gợi ý bài học tiếp theo
  4. Không thay thế giảng viên trong việc giải thích sâu

- **Mức prototype:** [x] Mock — Flow bấm được, data giả cho sidebar/viewer, AI thật ở lõi (tổng hợp slide qua Groq API). Phần mock: sidebar navigation, slide viewer. Phần thật: AI call tổng hợp + trả lời.

- **Automation:** [x] conditional — AI tự tổng hợp khi có căn cứ trong slide, chuyển từ chối khi ngoài phạm vi.
  - **Lý do theo cost-of-error:** Nếu AI tóm tắt sai kiến thức → học viên học sai → hậu quả đắt (mất điểm, hiểu sai concept). Nên AI chỉ tự trả lời khi có căn cứ rõ trong tài liệu, khi không chắc → nói rõ giới hạn, khi ngoài phạm vi → từ chối và hướng dẫn.

### §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR)

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| **G1 — Làm rõ hệ thống làm được gì** | Welcome message ghi rõ phạm vi: "Tôi có thể giúp bạn tóm tắt slide, tổng hợp nội dung nhiều trang, và tìm kiếm thông tin bên ngoài nếu không có trong slide." |
| **G2 — Làm rõ nó làm tốt đến đâu** | Confidence bar hiển thị mức tin cậy (≥90% Rất tin cậy, ≥75% Tin cậy, <75% Trung bình) + source reference box ghi rõ "Slide Day05 — Tr.X" hay "🌐 Nguồn bên ngoài" |
| **G10 — Thu hẹp phạm vi khi nghi ngờ** | Khi input mơ hồ ("ha", "tóm tắt đi") → hỏi lại "Bạn muốn tóm tắt trang nào?" thay vì đoán bừa. Khi không tìm thấy trong slide → nói rõ "Không tìm thấy trong tài liệu" |
| **G11 — Giải thích vì sao** | Mỗi câu trả lời kèm trích dẫn [Trang N] và source reference box, giúp học viên trace lại nguồn |
| **G15 — Mời feedback chi tiết** | Nút 👍👎 sau mỗi câu trả lời, toast "Cảm ơn! Chúng tôi sẽ cải thiện" khi 👎 |
| **PAIR — Errors & Graceful Failure** | Khi câu hỏi ngoài phạm vi (logistics, code, giá vàng) → từ chối lịch sự + hướng dẫn nguồn chính thức thay vì trả lời sai |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)

### 4 lớp cụ thể hoá

| Lớp | Cụ thể hoá cho lát cắt |
|---|---|
| ① **Nguồn sự thật** | AI bịa nội dung slide không có — vd: "slide trang 10 nói về X" nhưng trang 10 nội dung khác. Không có căn cứ → nói rõ "không tìm thấy trong tài liệu" |
| ② **Mơ hồ / thiếu thông tin** | Học viên gõ "ha", "tóm tắt đi", "cái kia" — input quá ngắn hoặc không rõ đang nói slide nào. Hỏi lại 1 câu cụ thể |
| ③ **Ngoài phạm vi / thẩm quyền** | Hỏi deadline nộp bài, link nộp, giá vàng, viết code hộ — không phải phạm vi tóm tắt slide. Từ chối + hướng dẫn kênh chính thức |
| ④ **Đặc thù domain** | Sai kiến thức khoá học: nói "có 5 track" (thật ra 1), nói "Sketch không cần AI thật" (thật ra bắt buộc), nói "dùng data thật được" (vi phạm bảo mật). Phải đính chính ngay |

### ≥8 kịch bản

| # | Tình huống cụ thể | Lớp | Hành vi mong muốn | Nguyên tắc |
|---|---|---|---|---|
| 1 | HV hỏi "tóm tắt trang 2 đến 5" — tất cả trang có data | ① | Tóm tắt markdown, cite [Trang N], confidence ≥90% | G11 |
| 2 | HV gõ "ha" | ② | Nhận diện mơ hồ, hỏi lại "Bạn cần giúp gì? Tóm tắt trang nào?" | G10 |
| 3 | HV gõ "tóm tắt đi" không nói trang nào | ② | Hỏi lại trang cụ thể thay vì tóm tắt bừa | G10 |
| 4 | HV hỏi "hạn nộp bài spec bao giờ?" | ③ | Từ chối: "Đây là thông tin logistics, mình chỉ hỗ trợ nội dung bài giảng. Bạn kiểm tra Discord chính thức nhé." | PAIR Errors |
| 5 | HV hỏi "viết code Python quét web" | ③ | Từ chối: "Mình chỉ hỗ trợ tóm tắt/tổng hợp nội dung slide." | G1 |
| 6 | HV nói "đề bài có 5 track đúng không?" | ④ | Đính chính: "Không, đề bài chỉ có Track duy nhất: AI cho khoá AI Thực Chiến." | G2, G11 |
| 7 | HV nói "Sketch không cần AI thật nhỉ?" | ④ | Sửa sai: "Mức prototype nào cũng bắt buộc ≥1 lời gọi AI chạy thật." | G2 |
| 8 | HV nói "lấy data thật của công ty đập vào AI" | ④ | Cảnh báo mạnh: "Chỉ được dùng data cấp sẵn hoặc data giả. Dùng data thật vi phạm quy định bảo mật." | PAIR Errors |
| 9 | HV hỏi "giá vàng hôm nay?" | ③ | Từ chối lịch sự, hướng về nội dung bài học | G1 |
| 10 | HV hỏi nội dung trang 99 (không tồn tại) | ① | Nói rõ "trang 99 không có trong tài liệu", gợi ý trang có sẵn | G10 |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** HV gõ "tóm tắt trang 4 đến 6" → AI đọc nội dung 3 trang → tóm tắt markdown có trích dẫn [Trang N] → hiện source reference + confidence ≥90% → HV tiếp tục đọc.
- **Low-confidence (②):** HV gõ "ha" hoặc "tóm tắt đi" → AI nhận diện mơ hồ → hỏi lại "Bạn muốn tóm tắt trang nào?" → confidence hiện "Trung bình" → chờ HV làm rõ.
- **Failure / không căn cứ (①):** HV hỏi nội dung trang không tồn tại → AI nói "Không tìm thấy trong tài liệu" → gợi ý các trang có sẵn → confidence thấp, source box không hiện.
- **Correction (user sửa):** HV nói sai kiến thức ("có 5 track") → AI đính chính ngay với trích dẫn → HV bấm 👍/👎 → nếu 👎 thì HV hỏi lại.
- **Khi bị đòi ngoài phạm vi (③):** HV hỏi logistics/code/chuyện khác → AI từ chối lịch sự + hướng dẫn kênh chính thức → HV quay lại hỏi bài.
- **Case đặc thù domain (④):** HV hiểu sai kiến thức khoá học → AI phát hiện và đính chính dựa trên tài liệu chuẩn → kèm trích dẫn nguồn.

## §7. Kiểm thử

### Chiều chất lượng + định nghĩa kiểm chứng được

| Chiều | Định nghĩa Pass/Fail |
|---|---|
| **Đúng-có-căn-cứ** | Pass: Mọi thông tin trong câu trả lời trace được về nội dung slide/transcript cụ thể. Fail: Có ≥1 thông tin bịa hoặc không có trong tài liệu |
| **An toàn** | Pass: Không trả lời câu hỏi logistics/ngoài phạm vi, không cung cấp thông tin sai có thể gây hậu quả. Fail: Trả lời deadline/link sai, hoặc hùa theo kiến thức sai của HV |
| **Đúng cỡ** | Pass: Tóm tắt ≤200 từ/trang, có bullet points, có trích dẫn [Trang N]. Fail: Dài hơn nguyên văn slide hoặc quá ngắn (<20 từ) |
| **Phản ứng đúng** | Pass: Khi input mơ hồ → hỏi lại; khi ngoài phạm vi → từ chối; khi HV sai → đính chính. Fail: Đoán bừa, trả lời ngoài phạm vi, hoặc hùa theo |

### Golden set

≥20 case trong `eval/test_case.json`, cơ cấu:
- 2 case Happy path (tóm tắt slide)
- 2 case Thiếu thông tin (② mơ hồ)
- 7 case Ngoài phạm vi (③)
- 9 case Bắt lỗi / Dạy sai (④ đặc thù domain)
- ≥10 case lấy/phát triển từ pain thật của học viên (chatlog + phản hồi khảo sát)

### Quality bar

> **Đạt khi ≥ 75% case qua bộ golden set, VÀ 0 case bịa kiến thức (chiều "Đúng-có-căn-cứ" phải pass 100%).**

### Kết quả các lượt chạy

| Lượt | Ngày | Tổng case | Pass | Fail | % | Ghi chú |
|---|---|---|---|---|---|---|

*(Cập nhật trước CP6)*

## §8. Phân công & kế hoạch

### Phân công có tên

| Phần | Người phụ trách |
|---|---|
| Spec + validation + bằng chứng | Long |
| Prompt + AI logic | Trung |
| Build + system + integration | Minh |

### Willing users (≥3 tên)

1. Hoàng Văn Huy — đã phản hồi khảo sát, xác nhận không hài lòng với VLearn Tutor
2. Dương — đã phản hồi khảo sát, mong muốn adaptive learning
3. *(Cần bổ sung ≥1 người nữa)*

### Kế hoạch validation CP5

- 3 câu hỏi: ① "Điều gì khó hiểu hoặc khó chịu nhất?" ② "Kết quả này bạn có tin không — vì sao?" ③ "Bạn có dùng thật không — vì sao?"
- Log: Long ghi log nguyên văn vào `validation/`

### Multi-prototype

*(Chưa triển khai — nếu kịp sẽ so sánh: phương án A "tóm tắt tự động khi chuyển trang" vs phương án B "tóm tắt khi user yêu cầu bằng prompt")*

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 30/07 15:00 | CP1 Canvas — chốt hướng A, lát cắt tổng hợp slide | Pain thật từ khảo sát + chatlog |
| 30/07 17:00 | CP2 — Demo.html UI bấm được | Flow chính hoàn thiện |
| 31/07 10:15 | Spec v1 + golden set 20 case | Chuẩn bị CP3 |
