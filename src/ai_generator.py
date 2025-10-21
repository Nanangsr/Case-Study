"""
ai_generator.py - AI job profile generation via Groq
"""
from groq import Groq
from config import Config
import json

client = Groq(api_key=Config.GROQ_API_KEY)

def generate_job_profile(role_name: str, role_purpose: str, job_level: str, benchmark_summary: str = None):
    """Generate job profile using Groq API"""
    
    prompt = f"""You are an expert HR business partner. Create a comprehensive job profile in JSON format.

Role: {role_name}
Level: {job_level}
Purpose: {role_purpose}
Benchmark Summary: {benchmark_summary if benchmark_summary else "Not provided"}

Return valid JSON with these keys:
1. "job_description": 2-3 sentences describing the role
2. "responsibilities": List of 5-7 key responsibilities
3. "qualifications": List of 3-5 minimum qualifications
4. "key_competencies": List of 3-5 critical soft skills

Keep it concise and professional."""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=Config.GROQ_MODEL,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response", "raw_response": content}
    except Exception as e:
        return {"error": f"AI generation failed: {str(e)}"}