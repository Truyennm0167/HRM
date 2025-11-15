"""
Module để parse nội dung JD từ file text thành cấu trúc dữ liệu.
"""
import re

def parse_jd_text(jd_data):
    """Parse JD data to extract structured fields."""
    try:
        return {
            'title': jd_data.get('title', ''),
            'required_skills': jd_data.get('required_skills', []),
            'nice_to_have_skills': jd_data.get('nice_to_have_skills', []),
            'required_years_experience': float(jd_data.get('required_years_experience', 0)),
            'required_degrees': jd_data.get('required_degrees', []),
            'description': jd_data.get('description', '')
        }
    except Exception as e:
        return {"error": f"Could not parse JD text: {e}"}

def parse_jd_from_file(file_path: str) -> dict:
    """
    Đọc và parse nội dung JD từ file text.
    Returns:
        dict: Cấu trúc dữ liệu chứa thông tin JD đã được parse
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tách các section chính
        must_have_section = re.search(r'Yêu cầu bắt buộc.*?(?=\n\n|\Z)', content, re.DOTALL)
        nice_to_have_section = re.search(r'Kỹ năng ưu tiên.*?(?=\n\n|\Z)', content, re.DOTALL)
        
        # Parse required skills
        required_skills = []
        if must_have_section:
            skills = re.findall(r'- (.+?)(?=\n|$)', must_have_section.group())
            for skill in skills:
                # Extract technical skills and keywords
                if any(keyword in skill.lower() for keyword in ['nắm vững', 'kinh nghiệm', 'thành thạo']):
                    # Extract specific technologies mentioned
                    techs = re.findall(r'(Dart|Flutter|Bloc|Provider|REST API|Git|Node\.js|Firebase|MongoDB|Kotlin|Swift)', skill)
                    required_skills.extend(techs)
                    # Add general concepts
                    if 'REST API' in skill:
                        required_skills.append('REST API')
                    if 'state' in skill.lower():
                        required_skills.extend(['Bloc', 'Provider'])

        # Parse nice to have skills
        nice_to_have_skills = []
        if nice_to_have_section:
            skills = re.findall(r'- (.+?)(?=\n|$)', nice_to_have_section.group())
            for skill in skills:
                # Extract technical skills
                techs = re.findall(r'(Node\.js|Firebase|MongoDB|Kotlin|Swift|CI/CD)', skill)
                nice_to_have_skills.extend(techs)

        # Extract required years
        years_match = re.search(r'(\d+)\s*năm', content)
        required_years = int(years_match.group(1)) if years_match else 0

        # Extract required degrees
        degrees = ["cử nhân", "kỹ sư", "bachelor", "engineer", "công nghệ thông tin", 
                  "khoa học máy tính", "information technology", "computer science"]

        # Remove duplicates and clean up
        required_skills = list(set(required_skills))
        nice_to_have_skills = [s for s in list(set(nice_to_have_skills)) 
                              if s not in required_skills]

        return {
            "required_skills": required_skills,
            "nice_to_have_skills": nice_to_have_skills,
            "required_years_experience": required_years,
            "required_degrees": degrees
        }
        
    except Exception as e:
        return {
            "error": f"Lỗi khi parse JD: {str(e)}",
            "required_skills": [],
            "nice_to_have_skills": [],
            "required_years_experience": 0,
            "required_degrees": []
        }