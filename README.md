# Telegram Join-Message Deleter Bot

Bot Telegram bằng Python được tối ưu hóa để deploy lên **Render** (Free Tier), có nhiệm vụ tự động xóa các tin nhắn hệ thống thông báo có người mới tham gia nhóm (ví dụ: *"Username joined the group"*).

---

## 🛠️ Hướng dẫn từng bước

### Bước 1: Tạo Telegram Bot mới
1. Mở Telegram, tìm kiếm bot chính thức của Telegram là **@BotFather**.
2. Nhấn `/start` và gửi lệnh `/newbot` để tạo bot mới.
3. Đặt tên hiển thị cho bot (ví dụ: `Join Deleter Bot`).
4. Đặt username cho bot (phải kết thúc bằng chữ `bot`, ví dụ: `xoa_tin_nhan_join_bot`).
5. **Sao chép mã API Token (BOT_TOKEN)** mà `@BotFather` gửi cho bạn (định dạng dạng `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

### Bước 2: Thêm Bot vào Nhóm và Phân Quyền
Bạn có hai cách để thêm bot vào nhóm của mình:
*   **Cách 1 (Nhanh nhất):** Chat riêng với Bot (gửi tin nhắn bất kỳ cho Bot). Bot sẽ phản hồi lại kèm theo một liên kết đặc biệt dạng `https://t.me/your_bot_username?startgroup=true`. Click vào đó, chọn nhóm của bạn là Bot sẽ được thêm vào ngay lập tức.
*   **Cách 2 (Thủ công):** Vào phần danh sách thành viên nhóm của bạn -> chọn **Add Member** -> tìm kiếm Username của bot -> nhấn thêm.

**Sau khi thêm, bạn cần:**
1. Chuyển bot sang vai trò **Quản trị viên (Administrator)**.
2. Cấp quyền **Xóa tin nhắn (Delete messages)** cho bot.
   > ⚠️ **Quan trọng:** Nếu không cấp quyền này, bot sẽ không thể xóa tin nhắn hệ thống khi có người tham gia và sẽ báo lỗi trong log.

### Bước 3: Deploy lên Render (Miễn phí)
1. **Đưa mã nguồn lên GitHub:**
   - Tạo một repository mới trên GitHub (ở chế độ Private hoặc Public đều được).
   - Commit và push toàn bộ các file trong thư mục này lên repository đó (`bot.py`, `requirements.txt`, `Procfile`, `README.md`).

2. **Tạo Web Service trên Render:**
   - Truy cập [Render](https://render.com/) và đăng nhập (bằng tài khoản GitHub của bạn).
   - Chọn **New +** -> **Web Service**.
   - Chọn repository GitHub chứa code bot của bạn.
   - Cấu hình các thông số sau:
     - **Name:** Đặt tên cho dịch vụ (ví dụ: `tele-join-delecer-bot`).
     - **Region:** Chọn khu vực gần bạn nhất (ví dụ: `Singapore` hoặc `Oregon`).
     - **Branch:** `main` (hoặc branch chính của bạn).
     - **Runtime:** `Python`.
     - **Build Command:** `pip install -r requirements.txt`.
     - **Start Command:** `gunicorn bot:server` (hoặc Render sẽ tự động đọc từ tệp `Procfile` đã có sẵn).
     - **Instance Type:** `Free`.

3. **Cấu hình Biến môi trường (Environment Variables):**
   - Chuyển sang tab **Environment** trong cấu hình Web Service trên Render.
   - Nhấp **Add Environment Variable** và thêm biến sau:
     - **Key:** `BOT_TOKEN`
     - **Value:** *Mã API Token bạn lấy được ở Bước 1*.
   - Nhấp **Save Changes**.

4. **Kích hoạt Webhook:**
   - Sau khi Render build và deploy thành công (chờ khoảng 1-3 phút), Render sẽ cung cấp cho bạn một đường dẫn URL công khai (dạng `https://ten-dich-vu-cua-ban.onrender.com`).
   - Hãy truy cập đường dẫn này một lần bằng trình duyệt web. Lúc này bot sẽ tự động đăng ký Webhook với Telegram. Bạn sẽ thấy thông báo: `Webhook is already active at...` hoặc `Webhook successfully updated to...` trên trình duyệt.

---

## ⚡ Giải pháp giữ cho Bot không bị "Ngủ" trên Render Free Tier

Trên gói **Render Free Tier**, Web Service của bạn sẽ tự động chuyển sang chế độ "ngủ" (Suspend) nếu không có yêu cầu HTTP (traffic) nào gửi tới trong vòng 15 phút. Điều này khiến bot bị phản hồi chậm hoặc không hoạt động khi có người mới join nhóm sau một thời gian dài không có ai tương tác.

Để khắc phục điều này hoàn toàn miễn phí:
1. Truy cập trang web [UptimeRobot](https://uptimerobot.com/) hoặc [Cron-Job.org](https://cron-job.org/) (đăng ký tài khoản miễn phí).
2. Tạo một Monitor mới:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Ping Tele Bot`
   - **URL (or IP):** *Đường dẫn URL Render của bạn* (ví dụ: `https://ten-dich-vu-cua-ban.onrender.com/`)
   - **Monitoring Interval:** Chọn `5 minutes` hoặc `10 minutes` (mỗi 5 hoặc 10 phút ping một lần).
3. Lưu lại. Hệ thống này sẽ liên tục gửi request HTTP giữ cho Render Web Service luôn thức và bot hoạt động 24/7.

---

## 💻 Hướng dẫn Chạy Thử ở Local (Máy tính cá nhân)

Nếu bạn muốn chạy thử bot trên máy tính cá nhân trước khi deploy:
1. Cài đặt các thư viện:
   ```bash
   pip install -r requirements.txt
   ```
2. Thiết lập biến môi trường và chạy file:
   - **Trên Windows (Command Prompt):**
     ```cmd
     set BOT_TOKEN=your_telegram_bot_token_here
     python bot.py
     ```
   - **Trên Windows (PowerShell):**
     ```powershell
     $env:BOT_TOKEN="your_telegram_bot_token_here"
     python bot.py
     ```
   - **Trên macOS / Linux:**
     ```bash
     export BOT_TOKEN="your_telegram_bot_token_here"
     python bot.py
     ```
3. Khi chạy ở Local, bot sẽ tự động nhận diện và chạy ở chế độ **Long Polling** (không cần Webhook) để bạn test trực tiếp vô cùng thuận tiện.
