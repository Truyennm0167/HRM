# cv_scorer.py

import re
from datetime import datetime
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta

class ScoringModule:
    """
    Class để chấm điểm CV đã được parse dựa trên một Job Description (JD).
    """
    def __init__(self, job_description, weights):
        self.jd = job_description
        self.weights = weights

    def _calculate_years_experience(self, experience_list: list) -> float:
        """
        Hàm nội bộ để tính tổng số năm kinh nghiệm từ danh sách kinh nghiệm.
        Hàm này đã được sửa lỗi để xử lý các định dạng ngày tháng và unpacking list.
        """
        if not isinstance(experience_list, list):
            return 0.0

        total_months = 0
        current_date = datetime.now()

        for exp in experience_list:
            duration_str = exp.get('duration')
            if not duration_str:
                continue
            
            # Chuẩn hóa chuỗi thời gian, loại bỏ các ký tự không mong muốn
            duration_str = duration_str.lower().replace('–', '-').replace('to', '-')
            duration_str = duration_str.replace('present', current_date.strftime('%b %Y'))
            duration_str = duration_str.replace('hiện tại', current_date.strftime('%b %Y'))
            duration_str = re.sub(r'\s+', ' ', duration_str).strip() # Loại bỏ khoảng trắng thừa

            try:
                parts = [p.strip() for p in duration_str.split('-') if p.strip()]
                if len(parts) == 2:
                    # === FIX: correct unpacking of the two parts ===
                    start_str, end_str = parts[0], parts[1]

                    # date_parse expects a string; parts[*] are strings after strip()
                    start_date = date_parse(start_str, fuzzy=True, default=datetime(1, 1, 1))
                    end_date = date_parse(end_str, fuzzy=True, default=current_date)
                    
                    if end_date > current_date: 
                        end_date = current_date
                    
                    delta = relativedelta(end_date, start_date)
                    total_months += delta.years * 12 + delta.months
            except Exception:
                # Xử lý dự phòng cho các định dạng chỉ có năm, ví dụ "2020 - 2024"
                years = re.findall(r'\b\d{4}\b', duration_str)
                if len(years) >= 2:
                    # === FIX: convert first and last year strings to int ===
                    start_year, end_year = int(years[0]), int(years[-1])
                    total_months += (end_year - start_year) * 12
                continue
        
        return round(total_months / 12.0, 1)

    def score_skills(self, cv_skills: list) -> float:
        """Chấm điểm kỹ năng dựa trên so khớp từ khóa (thang điểm 0-100)."""
        if not isinstance(cv_skills, list):
            return 0.0

        cv_skills_set = {skill.lower().strip() for skill in cv_skills}
        # Ensure defaults are lists so set comprehensions can iterate safely
        required_skills_set = {s.lower().strip() for s in self.jd.get('required_skills', [])}
        nice_to_have_set = {s.lower().strip() for s in self.jd.get('nice_to_have_skills', [])}

        required_matches = len(cv_skills_set.intersection(required_skills_set))
        nice_to_have_matches = len(cv_skills_set.intersection(nice_to_have_set))

        required_score = (required_matches / len(required_skills_set)) * 100 if required_skills_set else 100
        nice_to_have_bonus = min(nice_to_have_matches * 5, 25)

        return min(required_score + nice_to_have_bonus, 100.0)

    def score_experience(self, cv_experience: list) -> float:
        """Chấm điểm kinh nghiệm dựa trên số năm (thang điểm 0-100)."""
        total_years = self._calculate_years_experience(cv_experience)
        required_years = self.jd.get('required_years_experience', 0)

        if required_years == 0:
            return 100.0

        score = (total_years / required_years) * 100
        return min(score, 100.0)

    def score_education(self, cv_education: list) -> float:
        """Chấm điểm học vấn dựa trên việc có bằng cấp phù hợp (0 hoặc 100)."""
        if not isinstance(cv_education, list):
            return 0.0

        required_degrees = self.jd.get('required_degrees', [])
        if not required_degrees:
            return 100.0

        required_degrees_lower = [d.lower().strip() for d in required_degrees]

        for edu in cv_education:
            degree_str = edu.get('degree', '').lower()
            for req_degree in required_degrees_lower:
                if req_degree in degree_str:
                    return 100.0
        
        return 0.0

    def calculate_total_score(self, parsed_cv: dict) -> dict:
        """
        Tính toán điểm tổng thể có trọng số cho một CV đã được parse.
        """
        if "error" in parsed_cv:
            return {"error": parsed_cv["error"], "total_score": 0}

        skills_score = self.score_skills(parsed_cv.get('skills'))
        experience_score = self.score_experience(parsed_cv.get('experience'))
        education_score = self.score_education(parsed_cv.get('education'))

        total_score = (
            (skills_score * self.weights.get('skills', 0)) +
            (experience_score * self.weights.get('experience', 0)) +
            (education_score * self.weights.get('education', 0))
        )
        
        return {
            'skills_score': round(skills_score, 2),
            'experience_score': round(experience_score, 2),
            'education_score': round(education_score, 2),
            'total_score': round(total_score, 2)
        }