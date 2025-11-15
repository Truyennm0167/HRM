# main.py

import os
from pprint import pprint

# Import các class từ các module khác
from config import GEMINI_API_KEY
from cv_parser import CVProcessor
from cv_scorer import ScoringModule

def main():
    """
    Hàm chính điều phối toàn bộ quy trình xử lý và chấm điểm CV.
    """
    # --- BƯỚC 1: KIỂM TRA CẤU HÌNH ---
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("LỖI: Bạn chưa cấu hình GEMINI_API_KEY trong file 'config.py'.")
        print("Hãy lấy API key từ Google AI Studio và dán vào file config.")
        return

    # --- BƯỚC 2: PARSE JOB DESCRIPTION VÀ ĐỊNH NGHĨA TRỌNG SỐ ---
    from jd_parser import parse_jd_from_file
    
    JOB_DESCRIPTION = parse_jd_from_file("JD.txt")
    if "error" in JOB_DESCRIPTION:
        print(f"\nLỖI: {JOB_DESCRIPTION['error']}")
        return

    print("\n--- THÔNG TIN JOB DESCRIPTION ---")
    print("Kỹ năng bắt buộc:", JOB_DESCRIPTION["required_skills"])
    print("Kỹ năng ưu tiên:", JOB_DESCRIPTION["nice_to_have_skills"])
    print("Số năm kinh nghiệm yêu cầu:", JOB_DESCRIPTION["required_years_experience"])
    print("Bằng cấp yêu cầu:", JOB_DESCRIPTION["required_degrees"])

    SCORING_WEIGHTS = {
        "skills": 0.5,
        "experience": 0.3,
        "education": 0.2
    }

    # --- BƯỚC 3: CHỌN FILE CV ĐỂ XỬ LÝ ---
    #!!! QUAN TRỌNG: Thay đổi tên file này thành tên file CV bạn muốn test
    # File này phải nằm trong thư mục `cvs/`
    cv_filename = "HuongHuynh.pdf" 
    cv_filepath = os.path.join("cvs", cv_filename)

    if not os.path.exists(cv_filepath):
        print(f"LỖI: Không tìm thấy file CV tại '{cv_filepath}'.")
        print("Hãy chắc chắn rằng bạn đã đặt file CV vào thư mục 'cvs'.")
        return

    # --- BƯỚC 4: KHỞI TẠO VÀ CHẠY QUY TRÌNH ---
    print("="*50)
    print(f"BẮT ĐẦU XỬ LÝ CV: {cv_filename}")
    print("="*50)

    processor = CVProcessor()
    scorer = ScoringModule(job_description=JOB_DESCRIPTION, weights=SCORING_WEIGHTS)

    structured_cv_data = processor.process_cv(cv_filepath)

    print("\n--- KẾT QUẢ PARSING (DỮ LIỆU CÓ CẤU TRÚC) ---")
    pprint(structured_cv_data)

    if structured_cv_data and "error" not in structured_cv_data:
        final_scores = scorer.calculate_total_score(structured_cv_data)
        print("\n--- KẾT QUẢ CHẤM ĐIỂM ---")
        pprint(final_scores)
    else:
        print("\nKhông thể chấm điểm do có lỗi trong quá trình parsing.")
    
    print("\n" + "="*50)
    print("KẾT THÚC QUY TRÌNH")
    print("="*50)

if __name__ == '__main__':
    main()