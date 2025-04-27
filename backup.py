import os
import shutil
import smtplib
import schedule
import time
from email.message import EmailMessage
from dotenv import load_dotenv
import datetime

# Load thông tin từ file .env
load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Thư mục chứa database và thư mục lưu backup
DATABASE_FOLDER = 'database_folder'
BACKUP_FOLDER = 'backup_folder'

def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        
        # Thông báo khi gửi email thành công
        print("Đã hoàn tất gửi mail")
    
    except Exception as e:
        print(f"Failed to send email: {e}")

def backup_database():
    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)

        files = os.listdir(DATABASE_FOLDER)
        db_files = [f for f in files if f.endswith('.sql') or f.endswith('.sqlite3')]

        if not db_files:
            send_email("Sao lưu không thành công", "Không tìm thấy tệp cơ sở dữ liệu (.sql hoặc .sqlite3) để sao lưu.")
            return

        for file_name in db_files:
            src_path = os.path.join(DATABASE_FOLDER, file_name)
            dst_file_name = f"{date_str}_{file_name}"
            dst_path = os.path.join(BACKUP_FOLDER, dst_file_name)
            shutil.copy2(src_path, dst_path)

        send_email("Sao lưu thành công", f"Sao lưu hoàn tất thành công tại {now.strftime('%Y-%m-%d %H:%M:%S')}.")

    except Exception as e:
        send_email("Sao lưu không thành công", f"Sao lưu không thành công với lỗi: {str(e)}")

if __name__ == "__main__":
    # Lên lịch backup lúc 00:00 mỗi ngày
    schedule.every().day.at("00:00").do(backup_database)

    print("Backup Scheduler đang chạy... (Nhấn Ctrl+C để dừng)")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Kiểm tra lịch mỗi 60 giây
