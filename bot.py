import os
import re
import logging
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import MessageActionChatAddUser, MessageActionChatJoinedByLink, MessageActionChatDeleteUser
from telethon.errors import (
    UserAlreadyParticipantError,
    InviteHashExpiredError,
    InviteHashInvalidError,
    ChannelPrivateError,
    ChatAdminRequiredError
)

# Cấu hình Logging để theo dõi hoạt động và lỗi dễ dàng
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Đọc thông số cấu hình từ biến môi trường (Environment Variables) hoặc chỉnh sửa trực tiếp dưới đây
# Bạn có thể lấy API_ID và API_HASH bằng cách truy cập: https://my.telegram.org/
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_NAME = os.environ.get("SESSION_NAME", "delete_join_userbot")

# Kiểm tra cấu hình bắt buộc trước khi khởi chạy
if not API_ID or not API_HASH:
    logger.warning("CẢNH BÁO: Chưa cấu hình API_ID hoặc API_HASH trong biến môi trường.")
    logger.info("Chương trình sẽ yêu cầu bạn nhập thủ công từ bàn phím khi khởi chạy.")
    
    # Hỗ trợ nhập trực tiếp từ bàn phím nếu chạy local
    try:
        if not API_ID:
            API_ID = input("Nhập API_ID của bạn (từ my.telegram.org): ").strip()
        if not API_HASH:
            API_HASH = input("Nhập API_HASH của bạn (từ my.telegram.org): ").strip()
    except Exception as e:
        logger.error(f"Không thể nhận dữ liệu nhập từ bàn phím: {e}")
        exit(1)

# Chuyển đổi API_ID sang kiểu số nguyên
try:
    API_ID = int(API_ID)
except ValueError:
    logger.error("API_ID phải là một số nguyên hợp lệ!")
    exit(1)

# Hỗ trợ String Session khi deploy lên Render (để không bị mất đăng nhập khi Render khởi động lại)
STRING_SESSION = os.environ.get("STRING_SESSION")

# Khởi tạo Telegram Client (Userbot)
if STRING_SESSION:
    logger.info("Phát hiện STRING_SESSION. Đang khởi chạy Userbot bằng String Session...")
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
else:
    logger.info(f"Không tìm thấy STRING_SESSION. Chạy bằng session tệp cục bộ: {SESSION_NAME}.session")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Hàm phân tích liên kết Telegram để lấy Invite Hash hoặc Username của nhóm
def parse_telegram_link(link):
    link = link.strip()
    
    # Định dạng link invite private cũ hoặc mới (ví dụ: t.me/joinchat/ABCDEF hoặc t.me/+ABCDEF)
    private_pattern = r'(?:t\.me|telegram\.me|telegram\.dog)\/(?:joinchat\/|\+)([a-zA-Z0-9_-]+)'
    private_match = re.search(private_pattern, link, re.IGNORECASE)
    if private_match:
        return "private", private_match.group(1)
        
    # Định dạng link group public (ví dụ: t.me/ten_nhom hoặc @ten_nhom)
    public_pattern = r'(?:t\.me|telegram\.me|telegram\.dog)\/([a-zA-Z0-9_]{5,})'
    public_match = re.search(public_pattern, link, re.IGNORECASE)
    if public_match:
        return "public", public_match.group(1)
        
    # Định dạng username dạng @username
    username_pattern = r'^@([a-zA-Z0-9_]{5,})$'
    username_match = re.match(username_pattern, link)
    if username_match:
        return "public", username_match.group(1)
        
    return None, None

async def cleanup_history(client_instance, chat_identifier, limit=1000):
    logger.info(f"Bắt đầu quét dọn lịch sử của nhóm '{chat_identifier}' (giới hạn {limit} tin nhắn)...")
    deleted_count = 0
    try:
        # Lấy thông tin nhóm/kênh để chắc chắn truy cập được
        entity = await client_instance.get_entity(chat_identifier)
        async for message in client_instance.iter_messages(entity, limit=limit):
            # Kiểm tra xem có phải là tin nhắn hệ thống (service message) về gia nhập/rời nhóm không
            if message.action and isinstance(message.action, (MessageActionChatAddUser, MessageActionChatJoinedByLink, MessageActionChatDeleteUser)):
                try:
                    await message.delete()
                    deleted_count += 1
                except Exception as delete_err:
                    logger.debug(f"Không thể xóa tin nhắn hệ thống {message.id}: {delete_err}")
        logger.info(f"Đã dọn dẹp xong lịch sử. Đã xóa {deleted_count} tin nhắn hệ thống.")
        return True, deleted_count
    except ChatAdminRequiredError:
        return False, "admin_required"
    except Exception as e:
        logger.error(f"Lỗi khi dọn dẹp lịch sử: {e}")
        return False, str(e)

# Sự kiện: Lắng nghe tin nhắn riêng tư gửi đến Userbot để tự động join nhóm
@client.on(events.NewMessage(func=lambda e: e.is_private))
async def handle_private_message(event):
    message_text = event.text
    sender = await event.get_sender()
    sender_username = sender.username or sender.first_name or "Người dùng"
    
    logger.info(f"Nhận được tin nhắn từ {sender_username}: {message_text}")
    
    # Tìm kiếm link Telegram trong nội dung tin nhắn
    link_type, identifier = parse_telegram_link(message_text)
    
    if not identifier:
        # Nếu tin nhắn không phải là link nhóm, gửi hướng dẫn cho người dùng
        help_text = (
            "👋 **Xin chào! Tôi là Userbot dọn dẹp tin nhắn hệ thống.**\n\n"
            "Hãy gửi cho tôi **liên kết nhóm (group link)** hoặc **username nhóm (@username)** của bạn.\n"
            "Tôi sẽ tự động tham gia vào nhóm đó.\n\n"
            "**⚠️ LƯU Ý QUAN TRỌNG:**\n"
            "Để tôi có thể xóa tin nhắn hệ thống (người mới vào/ra nhóm):\n"
            "1. Thêm tài khoản của tôi làm **Admin (Quản trị viên)** trong nhóm.\n"
            "2. Cấp quyền **Xóa tin nhắn (Delete messages)** cho tôi."
        )
        await event.reply(help_text)
        return
        
    await event.reply(f"🔄 Đang xử lý yêu cầu tham gia nhóm `{identifier}`...")
    
    try:
        if link_type == "private":
            logger.info(f"Đang tham gia nhóm private với hash: {identifier}")
            await client(ImportChatInviteRequest(identifier))
        else:
            logger.info(f"Đang tham gia nhóm public với username: {identifier}")
            await client(JoinChannelRequest(identifier))
            
        await event.reply(
            f"✅ **Đã tham gia/truy cập nhóm `{identifier}` thành công!**\n\n"
            f"🔄 Đang tự động quét dọn các tin nhắn thông báo cũ trong lịch sử nhóm..."
        )
        
        success, result = await cleanup_history(client, identifier)
        if success:
            await event.reply(f"✅ **Dọn dẹp lịch sử thành công!** Đã xóa **{result}** tin nhắn hệ thống cũ trong nhóm.")
        elif result == "admin_required":
            await event.reply(
                f"⚠️ **Lưu ý:** Tôi đã vào nhóm nhưng **không thể xóa** tin nhắn cũ.\n\n"
                f"**Lý do:** Tài khoản này chưa được cấp quyền **Xóa tin nhắn (Delete messages)** trong nhóm.\n"
                f"👉 Vui lòng đảm bảo tài khoản đã được cấp quyền, sau đó gửi lại link nhóm này để tôi dọn dẹp sạch sẽ nhé!"
            )
        else:
            await event.reply(f"ℹ️ Đã vào nhóm. Có vấn đề xảy ra khi quét dọn lịch sử: `{result}`")
    except UserAlreadyParticipantError:
        await event.reply("ℹ️ Tôi đã là thành viên trong nhóm này từ trước rồi! Đang bắt đầu quét và dọn dẹp lịch sử tin nhắn thông báo vào/ra nhóm...")
        success, result = await cleanup_history(client, identifier)
        if success:
            await event.reply(f"✅ **Dọn dẹp lịch sử thành công!** Đã xóa **{result}** tin nhắn hệ thống cũ trong nhóm.")
        elif result == "admin_required":
            await event.reply("⚠️ **Không thể dọn dẹp lịch sử:** Tôi chưa được cấp quyền Admin hoặc chưa được bật quyền **Xóa tin nhắn (Delete messages)** trong nhóm này. Vui lòng cấp quyền và gửi lại link để dọn dẹp nhé!")
        else:
            await event.reply(f"❌ Có lỗi xảy ra khi quét dọn lịch sử: `{result}`")
    except InviteHashExpiredError:
        await event.reply("❌ Lỗi: Liên kết mời đã hết hạn hoặc không còn hiệu lực.")
    except InviteHashInvalidError:
        await event.reply("❌ Lỗi: Liên kết mời không hợp lệ.")
    except ChannelPrivateError:
        await event.reply("❌ Lỗi: Nhóm này ở chế độ riêng tư và tôi không thể truy cập nếu không có link mời chính xác.")
    except Exception as e:
        logger.error(f"Lỗi khi tham gia nhóm: {e}")
        await event.reply(f"❌ Không thể tham gia nhóm. Lỗi: `{str(e)}`")

# Sự kiện: Tự động xóa các tin nhắn hệ thống (Gia nhập, Rời nhóm, Thêm thành viên)
@client.on(events.ChatAction)
async def handle_chat_action(event):
    # Kiểm tra xem có phải là sự kiện liên quan đến tham gia hoặc rời nhóm không
    is_join = event.user_joined or event.user_added
    is_leave = event.user_left
    
    if is_join or is_leave:
        action_desc = "gia nhập" if is_join else "rời"
        logger.info(f"Phát hiện sự kiện {action_desc} nhóm trong chat {event.chat_id}.")
        
        try:
            # Xóa tin nhắn hệ thống sinh ra bởi sự kiện này
            await event.delete()
            logger.info(f"✅ Đã xóa thành công tin nhắn hệ thống {action_desc} nhóm.")
        except ChatAdminRequiredError:
            logger.warning(
                f"⚠️ KHÔNG THỂ XÓA: Thiếu quyền Admin trong chat {event.chat_id}. "
                "Vui lòng set tài khoản Userbot làm Admin và cấp quyền 'Delete messages'."
            )
        except Exception as e:
            logger.error(f"Lỗi khi xóa tin nhắn hệ thống: {e}")

async def main():
    # Bắt đầu client và thực hiện đăng nhập nếu cần
    await client.start()
    me = await client.get_me()
    logger.info(f"🎉 Đã khởi chạy Userbot thành công! Đang chạy dưới tài khoản: {me.first_name} (@{me.username or 'Không có username'})")
    
    # Giữ cho Userbot chạy liên tục để lắng nghe sự kiện
    await client.run_until_disconnected()

# Cấu hình Flask Web Server giả lập để deploy được trên Render Free Web Service (tránh lỗi Port Binding Timeout)
server = Flask(__name__)

@server.route('/')
def health_check():
    return "Userbot is running perfectly!", 200

def start_web_server():
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Khởi động Flask Web Server trên port {port}...")
    server.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    import asyncio
    
    # Khởi chạy Flask Web Server dưới dạng luồng phụ (daemon thread)
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    try:
        # Chạy vòng lặp sự kiện chính của asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Đã tắt Userbot theo yêu cầu người dùng.")
