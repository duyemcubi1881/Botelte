import os
import logging
from flask import Flask, request
import telebot

# Cấu hình logging để dễ dàng debug trên Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Token của Bot Telegram
BOT_TOKEN = "8146489062:AAGBGPJYAWHLgxMbpGyTOyO1WQF1IVrZqdE"

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

# Route nhận webhook từ Telegram
@server.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return "Error", 500

# Trình xử lý xóa tin nhắn khi có người mới vào nhóm
@bot.message_handler(content_types=['new_chat_members'])
def delete_join_message(message):
    try:
        logger.info(f"Phát hiện thành viên mới trong chat {message.chat.id}. Tiến hành xóa tin nhắn hệ thống {message.message_id}...")
        # Xóa tin nhắn hệ thống hiển thị "X joined the group"
        bot.delete_message(message.chat.id, message.message_id)
        logger.info(f"Đã xóa thành công tin nhắn hệ thống {message.message_id}.")
    except telebot.apihelper.ApiTelegramException as api_err:
        logger.error(
            f"Lỗi Telegram API: {api_err.description}. Code: {api_err.error_code}. "
            f"Vui lòng kiểm tra xem bot đã được thêm làm Admin của Group và được cấp quyền 'Delete messages' (Xóa tin nhắn) chưa."
        )
    except Exception as e:
        logger.error(f"Lỗi không xác định khi xóa tin nhắn: {e}")

# Lấy Username của Bot một cách an toàn
BOT_USERNAME = None
def get_bot_username():
    global BOT_USERNAME
    if BOT_USERNAME is None and BOT_TOKEN != "DUMMY_TOKEN":
        try:
            BOT_USERNAME = bot.get_me().username
        except Exception as e:
            logger.error(f"Lỗi khi lấy username bot: {e}")
    return BOT_USERNAME or "bot_username"

# Hỗ trợ thêm bot vào nhóm khi chat riêng tư (Private Chat)
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_message(message):
    username = get_bot_username()
    add_link = f"https://t.me/{username}?startgroup=true"
    
    response_text = (
        f"👋 <b>Xin chào!</b>\n\n"
        f"Do chính sách bảo mật của Telegram, Bot không thể tự động tự tham gia vào nhóm qua link.\n\n"
        f"Tuy nhiên, bạn có thể thêm tôi vào nhóm cực kỳ dễ dàng bằng cách click vào link dưới đây:\n"
        f"👉 <a href=\"{add_link}\">THÊM BOT VÀO NHÓM CỦA BẠN</a>\n\n"
        f"<b>Các bước cần làm sau đó:</b>\n"
        f"1. Chọn nhóm bạn muốn thêm Bot vào.\n"
        f"2. Nâng cấp Bot lên làm <b>Quản trị viên (Admin)</b> của nhóm.\n"
        f"3. Đảm bảo cấp quyền <b>Xóa tin nhắn (Delete messages)</b> để Bot hoạt động dọn dẹp tin nhắn hệ thống."
    )
    try:
        bot.reply_to(message, response_text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Lỗi khi gửi tin nhắn hỗ trợ trong chat riêng tư: {e}")

# Route trang chủ (dùng cho Health Check và tự động thiết lập Webhook)
@server.route('/')
def index():
    render_url = os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/')
    if render_url and BOT_TOKEN != "DUMMY_TOKEN":
        webhook_url = f"{render_url}/{BOT_TOKEN}"
        try:
            current_webhook = bot.get_webhook_info()
            if current_webhook.url != webhook_url:
                logger.info(f"Đang thiết lập webhook tới: {webhook_url}")
                bot.remove_webhook()
                bot.set_webhook(url=webhook_url)
                return f"Webhook set to: {webhook_url}", 200
            else:
                return f"Webhook is already active at: {webhook_url}", 200
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập webhook: {e}")
            return f"Error setting webhook: {e}", 500
    return "Bot đang chạy. (Nếu trên Render, vui lòng kiểm tra biến RENDER_EXTERNAL_URL)", 200

# Route kiểm tra trạng thái webhook hiện tại
@server.route('/status')
def status():
    if BOT_TOKEN == "DUMMY_TOKEN":
        return {"error": "BOT_TOKEN is not configured"}, 400
    try:
        info = bot.get_webhook_info()
        return {
            "url": info.url,
            "pending_update_count": info.pending_update_count,
            "ip_address": info.ip_address,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message
        }, 200
    except Exception as e:
        return {"error": str(e)}, 500

# Tự động cấu hình Webhook ngay khi ứng dụng khởi chạy nếu có RENDER_EXTERNAL_URL
if BOT_TOKEN != "DUMMY_TOKEN":
    render_url = os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/')
    if render_url:
        webhook_url = f"{render_url}/{BOT_TOKEN}"
        try:
            current_webhook = bot.get_webhook_info()
            if current_webhook.url != webhook_url:
                logger.info(f"Tự động thiết lập webhook tại startup tới: {webhook_url}")
                bot.remove_webhook()
                bot.set_webhook(url=webhook_url)
        except Exception as e:
            logger.error(f"Lỗi tự động thiết lập webhook tại startup: {e}")

if __name__ == "__main__":
    if not os.environ.get('RENDER_EXTERNAL_URL'):
        if BOT_TOKEN == "DUMMY_TOKEN":
            logger.warning("Vui lòng đặt biến môi trường BOT_TOKEN để bot hoạt động.")
        else:
            logger.info("Không tìm thấy RENDER_EXTERNAL_URL. Đang chạy Bot ở chế độ Long Polling để test...")
            bot.remove_webhook()
            bot.infinity_polling()
    else:
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Đang khởi chạy Flask server trên cổng {port}...")
        server.run(host="0.0.0.0", port=port)
