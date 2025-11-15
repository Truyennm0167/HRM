# cv_parser.py

import fitz  # PyMuPDF
import docx
import re
import requests
import json
import os
import hashlib
from pprint import pprint

# Import cấu hình từ file config.py
from .config import GEMINI_API_URL, CACHE_DIR

class CVParser:
    """
    Class chỉ chịu trách nhiệm gọi Gemini API để phân tích nội dung text của CV.
    """
    def __init__(self, api_url):
        self.api_url = api_url

    def _build_prompt(self, cv_text: str) -> str:
        """Xây dựng prompt chi tiết để hướng dẫn Gemini."""
        return f"""
        You are an expert HR assistant. Your task is to analyze the following CV text and extract key information into a structured JSON format.

        **CV Text to Analyze:**
        ---
        {cv_text}
        ---

        **Instructions:**
        1.  Extract the following fields: 'name', 'email', 'phone', 'skills', 'experience', and 'education'.
        2.  For 'name', find the full name of the candidate.
        3.  For 'skills', create a list of all technical skills, programming languages, frameworks, and soft skills mentioned.
        4.  For 'experience', create a list of objects. Each object must contain 'position', 'company', and 'duration'.
        5.  For 'education', create a list of objects. Each object must contain 'university', 'degree', and 'duration'.
        6.  If a field is not found, return `null` for that field or an empty list `` for lists.
        7.  **CRITICAL:** Your final output must be ONLY a valid JSON object, with no other text before or after it. Start with `{{` and end with `}}`.
        """

    def parse_text(self, cv_text: str) -> dict:
        """Gửi text đến Gemini API và nhận về dữ liệu có cấu trúc."""
        if not cv_text:
            return {"error": "CV text is empty."}

        prompt = self._build_prompt(cv_text)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        
        headers = {"Content-Type": "application/json"}

        try:
            print("--> Đang gửi yêu cầu đến Gemini API (đây là bước có thể tốn phí)...")
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=90)
            response.raise_for_status()

            api_response = response.json()
            
            # SỬA LỖI: Truy cập đúng vào cấu trúc response của Gemini
            # 'candidates' là một list, ta cần lấy phần tử đầu tiên 
            json_text = api_response['candidates'][0]['content']['parts'][0]['text']
            
            structured_data = json.loads(json_text)
            return structured_data

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {e}"}
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Lỗi khi xử lý phản hồi từ API: {e}")
            print("Phản hồi gốc:", response.text if 'response' in locals() else "Không có phản hồi")
            return {"error": "Could not parse API response."}

class CVProcessor:
    """
    Pipeline hoàn chỉnh: Đọc file -> Trích xuất text -> Quản lý Cache -> Parse.
    """
    def __init__(self):
        self.parser = CVParser(api_url=GEMINI_API_URL)
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
            print(f"Đã tạo thư mục cache tại: {CACHE_DIR}")

    def _get_cache_path(self, file_path: str) -> str:
        """Tạo đường dẫn file cache dựa trên hash của file CV."""
        file_hash = self._hash_file(file_path)
        return os.path.join(CACHE_DIR, f"{file_hash}.json")

    def _hash_file(self, file_path: str) -> str:
        """Tạo một hash SHA256 duy nhất cho file để làm key cache."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def _extract_text_from_file(self, file_path: str) -> str:
        """Trích xuất text từ PDF hoặc DOCX."""
        text = ""
        try:
            if file_path.lower().endswith('.pdf'):
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text += page.get_text("text", flags=fitz.TEXTFLAGS_SEARCH) + "\n"
            elif file_path.lower().endswith('.docx'):
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
            
            return re.sub(r'(\n\s*){2,}', '\n\n', text).strip()
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path}: {e}")
            return ""

    def process_cv(self, file_path: str) -> dict:
        """
        Xử lý một file CV: kiểm tra cache trước, nếu không có thì mới gọi API.
        """
        cache_path = self._get_cache_path(file_path)

        if os.path.exists(cache_path):
            print(f"Đã tìm thấy kết quả parsing trong cache cho file: {os.path.basename(file_path)}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        print(f"Không tìm thấy cache. Bắt đầu xử lý mới file: {os.path.basename(file_path)}")
        
        cv_text = self._extract_text_from_file(file_path)
        if not cv_text:
            return {"error": f"Không thể trích xuất văn bản từ file: {file_path}"}
        
        structured_data = self.parser.parse_text(cv_text)

        if "error" not in structured_data:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, ensure_ascii=False, indent=4)
            print(f"Đã lưu kết quả parsing vào cache: {cache_path}")
        
        return structured_data