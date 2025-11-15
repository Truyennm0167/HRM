from django.conf import settings
from .cv_parser import CVProcessor
from .cv_scorer import ScoringModule

class ResumeService:
    def __init__(self):
        self.cv_processor = CVProcessor()

    def process_resume(self, resume, job_description=None):
        """Process a resume and optionally score it against a job description."""
        try:
            # Parse the CV
            parsed_data = self.cv_processor.process_cv(resume.file.path)
            resume.parsed_data = parsed_data
            
            # If job description is provided, score the CV
            if job_description and "error" not in parsed_data:
                jd_data = {
                    'required_skills': job_description.required_skills,
                    'nice_to_have_skills': job_description.nice_to_have_skills,
                    'required_years_experience': job_description.required_years_experience,
                    'required_degrees': job_description.required_degrees
                }
                
                weights = {
                    'skills': 0.5,
                    'experience': 0.3,
                    'education': 0.2
                }
                
                scorer = ScoringModule(jd_data, weights)
                scores = scorer.calculate_total_score(parsed_data)
                resume.scores = scores
            
            resume.save()
            return True

        except Exception as e:
            print(f"Error processing resume: {e}")
            return False