import os
import shutil
import subprocess

# Đường dẫn tới script và thư mục khởi động
file_path = os.path.abspath(__file__)
startup_folder = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')

# Sao chép script vào thư mục khởi động
print(f"Sao chép script từ {file_path} tới {startup_folder}")
shutil.copy(file_path, startup_folder)

def load_state():
    print("Đang tải trạng thái từ file state.txt")
    if os.path.exists('state.txt'):
        with open('state.txt', 'r') as f:
            return f.read().strip()
    return None

state = load_state()

if state == 'RESTARTED':
    print("Đoạn mã này chạy sau khi khởi động lại.")
else:
    print("Lưu trạng thái và khởi động lại máy tính")
    with open('state.txt', 'w') as f:
        f.write('RESTARTED')
    os.system("shutdown /r /t 1")
    exit()

if os.path.exists('state.txt'):
    os.remove('state.txt')

print("Script tiếp tục chạy sau khi khởi động lại máy tính.")
subprocess.Popen(['python', file_path])
