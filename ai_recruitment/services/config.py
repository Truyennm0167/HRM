# config.py

#!!! QUAN TRỌNG: Hãy thay thế chuỗi "YOUR_GEMINI_API_KEY" bằng API Key thật của bạn.
# Lấy key tại: https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyCvZjuwI13EzSUErd-ddjBu2nK4PWAhKdM"

# Sử dụng model 'flash' để tối ưu tốc độ và chi phí
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Đường dẫn đến thư mục cache để lưu kết quả parsing
CACHE_DIR = "cache"