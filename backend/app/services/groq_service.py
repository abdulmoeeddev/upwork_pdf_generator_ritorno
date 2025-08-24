import os
import json
from groq import Groq

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    
    def generate_proposal_template(self, project_description):
        """
        Generate a proposal JSON template using GROQ API
        """
        try:
            # Placeholder for GROQ API call - replace with actual implementation
            prompt = f"""
            Generate a structured JSON template for an Upwork proposal based on this project description:
            {project_description}
            
            The JSON should include sections for:
            - Introduction
            - Understanding of requirements
            - Proposed solution
            - Timeline
            - Budget
            - Why choose us
            
            Return only valid JSON without any additional text.
            """
            
            # Actual GROQ API call would go here
            # response = self.client.chat.completions.create(
            #     messages=[{"role": "user", "content": prompt}],
            #     model="llama3-70b-8192",
            #     temperature=0.7
            # )
            
            # For now, return a mock response
            mock_response = {
                "introduction": "Thank you for posting this project. I've carefully reviewed your requirements...",
                "understanding": "I understand you need a comprehensive solution that includes...",
                "proposed_solution": "My approach will involve the following steps: 1. Requirement analysis...",
                "timeline": {
                    "analysis": "2 days",
                    "development": "10 days",
                    "testing": "3 days",
                    "delivery": "1 day"
                },
                "budget": {
                    "total": "$1500",
                    "breakdown": {
                        "development": "$1200",
                        "testing": "$200",
                        "project_management": "$100"
                    }
                },
                "why_choose_us": "With 5+ years of experience in similar projects, I guarantee quality work..."
            }
            
            return mock_response
            
        except Exception as e:
            print(f"GROQ API Error: {e}")
            # Fallback to basic template
            return {
                "introduction": "",
                "understanding": "",
                "proposed_solution": "",
                "timeline": {},
                "budget": {},
                "why_choose_us": ""
            }
    
    def regenerate_proposal(self, current_json, admin_recommendations, bd_recommendations):
        """
        Regenerate proposal JSON with admin recommendations and BD input
        """
        try:
            # Placeholder for GROQ API call
            prompt = f"""
            Based on the current proposal JSON: {json.dumps(current_json)}
            
            Admin recommendations: {admin_recommendations}
            Business Developer recommendations: {bd_recommendations}
            
            Please regenerate the proposal JSON incorporating these recommendations.
            Maintain the same JSON structure but improve the content.
            
            Return only valid JSON without any additional text.
            """
            
            # Actual GROQ API call would go here
            # response = self.client.chat.completions.create(
            #     messages=[{"role": "user", "content": prompt}],
            #     model="llama3-70b-8192",
            #     temperature=0.7
            # )
            
            # For now, return the current JSON with a note about improvements
            improved_json = current_json.copy()
            improved_json['improvement_note'] = 'Enhanced based on recommendations'
            
            return improved_json
            
        except Exception as e:
            print(f"GROQ API Error: {e}")
            return current_json