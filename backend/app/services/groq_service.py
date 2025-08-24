import os
import json
from groq import Groq

class GroqService:
    def __init__(self):
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            print("Warning: GROQ_API_KEY not found. Using mock responses.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
    
    def generate_proposal_template(self, project_description):
        """
        Generate a proposal JSON template using GROQ API
        """
        try:
            if not self.client:
                return self._get_mock_proposal_template(project_description)
            
            prompt = f"""
            Generate a structured JSON template for an Upwork proposal based on this project description:
            {project_description}
            
            The JSON should include sections for:
            - introduction: A compelling opening paragraph
            - understanding: Your understanding of the project requirements
            - proposed_solution: Detailed solution approach with steps
            - timeline: Estimated timeline with phases
            - budget: Budget breakdown with justification
            - why_choose_us: Why you're the best choice for this project
            - portfolio_examples: Relevant experience or examples
            - questions: Any clarifying questions for the client
            
            Return only valid JSON without any additional text or markdown formatting.
            Make it professional and tailored to the specific project description.
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=2048
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            # Parse JSON
            proposal_json = json.loads(content)
            return proposal_json
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._get_mock_proposal_template(project_description)
        except Exception as e:
            print(f"GROQ API Error: {e}")
            return self._get_mock_proposal_template(project_description)
    
    def regenerate_proposal(self, current_json, admin_recommendations, bd_recommendations):
        """
        Regenerate proposal JSON with admin recommendations and BD input
        """
        try:
            if not self.client:
                return self._get_improved_mock_proposal(current_json, admin_recommendations, bd_recommendations)
            
            prompt = f"""
            Based on the current proposal JSON: {json.dumps(current_json, indent=2)}
            
            Admin recommendations: {admin_recommendations}
            Business Developer recommendations: {bd_recommendations}
            
            Please regenerate the proposal JSON incorporating these recommendations.
            Maintain the same JSON structure but improve the content based on feedback.
            Make sure to address all points mentioned in the recommendations.
            
            Return only valid JSON without any additional text or markdown formatting.
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=2048
            )
            
            # Extract and parse JSON
            content = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            improved_json = json.loads(content)
            return improved_json
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error during regeneration: {e}")
            return self._get_improved_mock_proposal(current_json, admin_recommendations, bd_recommendations)
        except Exception as e:
            print(f"GROQ API Error during regeneration: {e}")
            return self._get_improved_mock_proposal(current_json, admin_recommendations, bd_recommendations)
    
    def _get_mock_proposal_template(self, project_description):
        """Fallback mock template when GROQ API is unavailable"""
        return {
            "introduction": f"Thank you for posting this project. I've carefully reviewed your requirements and I'm excited to help you achieve your goals. With my expertise and experience, I'm confident I can deliver exactly what you're looking for.",
            "understanding": f"Based on your description: '{project_description[:100]}...', I understand you need a comprehensive solution that addresses your specific requirements. I've worked on similar projects and understand the challenges involved.",
            "proposed_solution": {
                "approach": "I will follow a systematic approach to ensure quality delivery",
                "phases": [
                    "Initial consultation and requirement analysis",
                    "Planning and design phase",
                    "Implementation and development",
                    "Testing and quality assurance",
                    "Delivery and post-project support"
                ]
            },
            "timeline": {
                "analysis": "1-2 days",
                "development": "7-10 days",
                "testing": "2-3 days",
                "delivery": "1 day",
                "total_duration": "2-3 weeks"
            },
            "budget": {
                "total": "To be discussed based on scope",
                "payment_terms": "Milestone-based payments preferred",
                "includes": "All development, testing, and basic support"
            },
            "why_choose_us": "With extensive experience in similar projects, I guarantee quality work delivered on time. I maintain clear communication throughout the project and provide ongoing support.",
            "portfolio_examples": "I have successfully completed similar projects with 100% client satisfaction. Happy to share relevant examples upon request.",
            "questions": "I'd love to discuss your specific requirements in more detail. Are there any particular features or constraints I should be aware of?"
        }
    
    def _get_improved_mock_proposal(self, current_json, admin_recommendations, bd_recommendations):
        """Fallback improved mock proposal"""
        improved_json = current_json.copy()
        improved_json['revision_notes'] = f"Enhanced based on admin feedback: {admin_recommendations[:100]}... and BD input: {bd_recommendations[:100]}..."
        
        # Add improvement indicators
        if 'introduction' in improved_json:
            improved_json['introduction'] = improved_json['introduction'] + " [REVISED BASED ON FEEDBACK]"
        
        return improved_json