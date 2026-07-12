import os
from telethon import TelegramClient
from telethon.sessions import StringSession

print("=" * 60)
print("  TẠO STRING SESSION CHO TELEGRAM USERBOT (DEPLOY CLOUD/RENDER)")
print("=" * 60)

try:
    API_ID = input("Nhập API_ID của bạn (từ my.telegram.org): ").strip()
    API_HASH = input("Nhập API_HASH của bạn (từ my.telegram.org): ").strip()
    
    if not API_ID or not API_HASH:
        print("❌ Lỗi: Bạn phải nhập cả API_ID và API_HASH.")
        exit(1)
        
    API_ID = int(API_ID)
except ValueError:
    print("❌ Lỗi: API_ID phải là một số nguyên.")
    exit(1)
except KeyboardInterrupt:
    print("\nĐã hủy bỏ.")
    exit(0)

# Khởi tạo client với StringSession rỗng để tạo session mới
client = TelegramClient(StringSession(), API_ID, API_HASH)

async def main():
    await client.start()
    session_string = client.session.save()
    me = await client.get_me()
    
    print("\n" + "=" * 50)
    print("🎉 ĐĂNG NHẬP THÀNH CÔNG!")
    print(f"Tài khoản: {me.first_name} (@{me.username or 'Không có username'})")
    print("=" * 50)
    print("\nHÃY COPY TOÀN BỘ CHUỖI DƯỚI ĐÂY (STRING SESSION):")
    print("\n" + session_string + "\n")
    print("=" * 50)
    print("⚠️ CẢNH BÁO BẢO MẬT:")
    print("Giữ chuỗi này bí mật tuyệt đối! Bất kỳ ai có chuỗi này đều có quyền truy cập vào tài khoản Telegram của bạn.")
    print("=" * 50)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nĐã hủy.")
