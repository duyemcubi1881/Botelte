# Telegram Auto-Join & Delete Service Messages Userbot

Userbot Telegram viết bằng Python (sử dụng thư viện **Telethon**) giúp tự động tham gia nhóm qua link được gửi trong chat riêng tư và tự động xóa các tin nhắn hệ thống (ví dụ: *"Username joined the group"*, *"Username left the group"*).

---

## 🛠️ Hướng dẫn thiết lập & Vận hành

### Bước 1: Lấy API_ID và API_HASH từ Telegram
Do Userbot hoạt động dưới quyền một tài khoản cá nhân thực tế (không phải bot chính thức), bạn cần lấy thông tin API của tài khoản đó:
1. Truy cập trang web chính thức của Telegram: [my.telegram.org](https://my.telegram.org) và đăng nhập bằng số điện thoại của bạn.
2. Chọn mục **API development tools**.
3. Điền các thông tin cơ bản để tạo ứng dụng mới (ví dụ: đặt tên App title và Short name bất kỳ).
4. Sau khi tạo xong, bạn sẽ thấy thông tin **App api_id** (ví dụ: `12345678`) và **App api_hash** (ví dụ: `abcdef0123456789abcdef0123456789`). Hãy lưu lại hai thông tin này.

---

### Bước 2: Chạy thử và đăng nhập lần đầu (ở Local)
Vì lần đầu chạy cần phải đăng nhập bằng cách nhập Số điện thoại và Mã OTP gửi về Telegram, bạn **nên chạy trên máy tính cá nhân trước** để tạo tệp Session (được lưu tự động thành `delete_join_userbot.session` trong thư mục dự án).

1. Cài đặt thư viện yêu cầu:
   ```bash
   pip install -r requirements.txt
   ```
2. Chạy ứng dụng:
   ```bash
   python bot.py
   ```
3. Lúc này, do chưa cấu hình biến môi trường, chương trình sẽ hỏi bạn:
   - `Nhập API_ID của bạn (từ my.telegram.org):` -> Dán API_ID của bạn vào và nhấn Enter.
   - `Nhập API_HASH của bạn (từ my.telegram.org):` -> Dán API_HASH của bạn vào và nhấn Enter.
   - Tiếp tục nhập số điện thoại đăng nhập của bạn (định dạng quốc tế, ví dụ: `+84912345678`).
   - Nhập mã xác thực (OTP) gửi về ứng dụng Telegram của bạn.
   - Nếu tài khoản của bạn bật xác minh 2 bước, hãy nhập thêm mật khẩu 2 lớp.
4. Khi thấy thông báo thành công: `🎉 Đã khởi chạy Userbot thành công!...`, tài khoản của bạn đã sẵn sàng hoạt động.

---

## 🚀 Cách sử dụng

### 1. Tự động tham gia nhóm qua link
* Vào Telegram của bạn, gửi link nhóm (ví dụ: `https://t.me/ten_nhom`, `https://t.me/joinchat/xxxxx`, hoặc `@ten_nhom`) cho chính tài khoản Userbot của bạn (hoặc tài khoản Userbot tự gửi cho chính nó trong phần **Saved Messages**).
* Userbot sẽ tự động nhận diện liên kết và tham gia vào nhóm đó ngay lập tức.

### 2. Tự động xóa thông báo Join / Leave
* Để Userbot có thể dọn dẹp các tin nhắn hệ thống, bạn cần:
  1. Thêm tài khoản Userbot vào nhóm (nếu chưa có).
  2. Nâng cấp tài khoản Userbot lên làm **Admin (Quản trị viên)** của nhóm.
  3. Cấp quyền **Xóa tin nhắn (Delete messages)** cho tài khoản Userbot.
* Kể từ lúc này, mọi thông báo thành viên mới vào nhóm hay rời nhóm đều sẽ bị Userbot xóa ngay lập tức!

---

## 🚀 Hướng dẫn Deploy lên Render (Hoạt động 24/7 Miễn phí)

Do ổ đĩa của Render Free Tier là tạm thời (sẽ bị xóa sạch khi ứng dụng khởi động lại), việc dùng file `.session` thông thường sẽ khiến bot bị mất đăng nhập mỗi ngày. 

Để khắc phục hoàn hảo lỗi này, chúng ta sử dụng phương pháp **String Session** (lưu toàn bộ khóa đăng nhập thành 1 chuỗi văn bản dài cấu hình trong biến môi trường).

### Bước 1: Tạo String Session ở máy cá nhân (Local)
1. Trong terminal tại máy tính của bạn, hãy chạy lệnh sau:
   ```bash
   python generate_string_session.py
   ```
2. Nhập `API_ID`, `API_HASH` và số điện thoại của bạn, sau đó nhập mã OTP đăng nhập.
3. Khi đăng nhập thành công, chương trình sẽ hiển thị một chuỗi ký tự dài (ví dụ: `1ApW...`). Hãy **sao chép toàn bộ chuỗi này**.

---

### Bước 2: Đưa mã nguồn lên GitHub
1. Tạo một repository mới trên GitHub (khuyên dùng chế độ **Private** để bảo mật code).
2. Commit và push toàn bộ các file trong thư mục này lên GitHub (`bot.py`, `generate_string_session.py`, `requirements.txt`, `README.md`).

---

### Bước 3: Cấu hình trên Render
1. Truy cập [Render](https://render.com/) và đăng ký/đăng nhập.
2. Nhấp chọn **New +** -> **Web Service**.
3. Kết nối với tài khoản GitHub của bạn và chọn repository chứa bot vừa upload.
4. Cấu hình dịch vụ với các thông số sau:
   *   **Name:** Đặt tên tùy chọn (ví dụ: `telegram-delete-join-userbot`).
   *   **Region:** Chọn vùng gần bạn (ví dụ: `Singapore` hoặc `Oregon`).
   *   **Branch:** `main` (hoặc branch chính của bạn).
   *   **Runtime:** `Python`.
   *   **Build Command:** `pip install -r requirements.txt`
   *   **Start Command:** `python bot.py` (Chương trình đã tích hợp sẵn một Flask Web Server phụ chạy ngầm để qua môn kiểm tra Port của Render).
   *   **Instance Type:** `Free`.
5. Thêm các biến môi trường (Environment Variables):
   * Chuyển sang tab **Environment**, chọn **Add Environment Variable** và thêm các biến sau:
     *   `API_ID` : *Nhập API_ID của bạn*
     *   `API_HASH` : *Nhập API_HASH của bạn*
     *   `STRING_SESSION` : *Dán toàn bộ chuỗi String Session bạn đã copy ở Bước 1 vào đây*
6. Nhấp **Save Changes**.

Chờ Render build khoảng 1-2 phút. Khi log báo `Userbot is running perfectly!` và `🎉 Đã khởi chạy Userbot thành công!`, bot của bạn sẽ hoạt động trực tuyến 24/7 hoàn toàn miễn phí và không bao giờ lo bị mất đăng nhập nữa!

---

## ⚡ Giữ cho Render Web Service không bị "Ngủ"
Render Free Tier sẽ tự động tắt dịch vụ nếu không có ai truy cập web sau 15 phút. Để giữ cho bot luôn thức:
1. Copy đường link Web Service mà Render cấp cho bạn (dạng `https://ten-app.onrender.com`).
2. Truy cập trang web miễn phí [UptimeRobot](https://uptimerobot.com/) hoặc [Cron-Job.org](https://cron-job.org/).
3. Tạo một Monitor dạng `HTTP(s)` trỏ tới đường link đó, chọn chu kỳ ping là mỗi `5 minutes` hoặc `10 minutes`. Dịch vụ này sẽ ping liên tục giữ Render Web Service luôn hoạt động 24/7.

---

## ⚙️ Chạy bằng biến môi trường (Khuyên dùng khi deploy lâu dài)
Nếu bạn chạy trên VPS, Docker hoặc các nền tảng đám mây khác, bạn có thể thiết lập các biến môi trường sau để Userbot tự động đăng nhập từ file Session hiện có mà không cần nhập lại thông tin:
* `API_ID`: App api_id của bạn.
* `API_HASH`: App api_hash của bạn.
* `SESSION_NAME`: Tên file session (mặc định là `delete_join_userbot`).

Ví dụ thiết lập nhanh trên Windows bằng cmd:
```cmd
set API_ID=12345678
set API_HASH=abcdef0123456789abcdef0123456789
python bot.py
```
Hoặc PowerShell:
```powershell
$env:API_ID="12345678"
$env:API_HASH="abcdef0123456789abcdef0123456789"
python bot.py
```
