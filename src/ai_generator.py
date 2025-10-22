"""
ai_generator.py - Pembangkit profil pekerjaan AI melalui Groq
"""
from groq import Groq
from config import Config
import json

client = Groq(api_key=Config.GROQ_API_KEY)

def generate_job_profile(role_name: str, role_purpose: str, job_level: str, benchmark_summary: str = None):
    """Membangkitkan profil pekerjaan menggunakan API Groq"""
    
    prompt = f"""Anda adalah mitra bisnis HR ahli. Buat profil pekerjaan komprehensif dalam format JSON.

    Peran: {role_name}
    Level: {job_level}
    Tujuan: {role_purpose}
    Ringkasan Benchmark: {benchmark_summary if benchmark_summary else "Tidak disediakan"}

    Kembalikan JSON valid dengan kunci-kunci ini:
    1. "job_description": 2-3 kalimat yang mendeskripsikan peran
    2. "responsibilities": Daftar 5-7 tanggung jawab utama
    3. "qualifications": Daftar 3-5 kualifikasi minimum
    4. "key_competencies": Daftar 3-5 keterampilan lunak kritis

    Jagalah agar ringkas dan profesional."""

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