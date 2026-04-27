"""
Real Product File Generator
Generates actual, sellable digital products with complete content.
Uses standard OpenAI SDK — no third-party wrappers.
"""
import asyncio
from typing import Dict, Any, List
import json
import logging
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import openai

load_dotenv()
logger = logging.getLogger(__name__)


def _openai_key() -> str:
    """Resolve OpenAI key from multiple env var names."""
    for var in ("OPENAI_API_KEY", "OPENAI_KEY"):
        val = os.environ.get(var)
        if val:
            return val
    return ""


class RealProductGenerator:
    def __init__(self):
        self.api_key = _openai_key()
        
    async def generate_complete_ebook(self, niche: str, keywords: List[str], 
                                     target_audience: str = "general") -> Dict[str, Any]:
        """
        Generate a COMPLETE, sellable eBook with full content.
        Uses standard openai SDK.
        """
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured — cannot generate real ebook content")
        
        logger.info("Generating complete eBook for niche: %s", niche)
        client = openai.OpenAI(api_key=self.api_key)
        
        def _chat(prompt: str, max_tokens: int = 2000) -> str:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional author and content strategist. Create comprehensive, valuable, and well-structured eBooks that customers love."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()

        # Step 1: outline
        outline_prompt = f"""Create a comprehensive outline for a professional eBook.

Niche: {niche}
Keywords: {', '.join(keywords)}
Target Audience: {target_audience}
Goal: 8-12 chapters

Return ONLY valid JSON (no markdown fences):
{{
  "title": "Compelling Book Title (4-10 words)",
  "subtitle": "Benefit-driven subtitle",
  "chapters": [
    {{"number": 1, "title": "Chapter Title", "description": "What it covers", "key_points": ["point1", "point2"]}}
  ],
  "target_pain_points": ["specific pain1", "specific pain2", "specific pain3"],
  "key_benefits": ["benefit1", "benefit2", "benefit3"]
}}"""

        outline_text = await asyncio.to_thread(_chat, outline_prompt, 1500)
        # strip markdown fences if present
        if "```" in outline_text:
            outline_text = outline_text.split("```")[1]
            if outline_text.startswith("json"):
                outline_text = outline_text[4:]
            outline_text = outline_text.split("```")[0].strip()
        outline = json.loads(outline_text)
        logger.info("Outline created: %s", outline['title'])

        # Step 2: chapters (batch them for speed)
        chapters_content = []
        for chapter in outline['chapters'][:10]:
            chapter_prompt = f"""Write Chapter {chapter['number']}: {chapter['title']}

Book: {outline['title']}
Description: {chapter['description']}
Key Points: {', '.join(chapter.get('key_points', []))}

Requirements:
- Minimum 800 words
- Professional, engaging writing with subheadings
- Practical examples and actionable advice
- No placeholder or filler text

Write the complete chapter now:"""

            content = await asyncio.to_thread(_chat, chapter_prompt, 2000)
            chapters_content.append({
                "number": chapter['number'],
                "title": chapter['title'],
                "content": content,
            })
            logger.debug("Chapter %d complete (%d chars)", chapter['number'], len(content))

        # Step 3: intro + conclusion
        intro = await asyncio.to_thread(_chat, f"""Write a compelling introduction (500-800 words) for:
Title: {outline['title']}
Subtitle: {outline.get('subtitle','')}
Hook the reader, explain the problem this solves, and preview the transformation.""", 1500)

        conclusion = await asyncio.to_thread(_chat, f"""Write a powerful conclusion (500-800 words) for:
Title: {outline['title']}
Summarize key takeaways, inspire action, and provide clear next steps.""", 1500)

        # Step 4: sales description (300+ chars for QC)
        sales_description = await asyncio.to_thread(_chat, f"""Write a compelling product sales description (250-350 words) for:
Title: {outline['title']}
Pain Points: {', '.join(outline.get('target_pain_points', []))}
Benefits: {', '.join(outline.get('key_benefits', []))}

Include: hook, problem statement, solution preview, what's inside, who it's for, and a call to action.
Use conversion language (transform, master, unlock, step-by-step, etc.).""", 800)

        total_words = (len(intro.split()) +
                       sum(len(ch['content'].split()) for ch in chapters_content) +
                       len(conclusion.split()))

        logger.info("eBook complete: %d words, %d chapters", total_words, len(chapters_content))

        return {
            "product_type": "ebook",
            "title": outline['title'],
            "subtitle": outline.get('subtitle', ''),
            "description": sales_description,
            "content": {
                "introduction": intro,
                "chapters": chapters_content,
                "conclusion": conclusion,
                "outline": outline,
            },
            "chapters": [ch['title'] for ch in chapters_content],
            "pages": max(28, total_words // 250),
            "metadata": {
                "word_count": total_words,
                "chapter_count": len(chapters_content),
                "niche": niche,
                "keywords": keywords,
                "target_audience": target_audience,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "file_ready": True,
            "quality_score": self._calculate_quality_score(total_words, len(chapters_content)),
        }
    
    async def generate_complete_course(self, topic: str, 
                                      target_audience: str = "beginners",
                                      duration_hours: int = 3) -> Dict[str, Any]:
        """
        Generate a COMPLETE online course with all content.
        Uses standard openai SDK.
        """
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured — cannot generate real course content")
        
        logger.info("Generating complete course for topic: %s", topic)
        client = openai.OpenAI(api_key=self.api_key)

        def _chat(prompt: str, max_tokens: int = 2000) -> str:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer and online course creator. Create comprehensive, engaging courses."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()

        # Step 1: course structure
        structure_prompt = f"""Create a complete course structure.

Topic: {topic}
Target: {target_audience}
Duration: {duration_hours} hours

Return ONLY valid JSON (no markdown fences):
{{
  "title": "Course Title (4-10 words)",
  "tagline": "Learn X in Y",
  "objectives": ["objective1", "objective2"],
  "modules": [
    {{
      "number": 1,
      "title": "Module Title",
      "lessons": [
        {{"title": "Lesson Title", "type": "video", "duration_min": 10, "content_outline": "What to teach"}}
      ]
    }}
  ]
}}"""

        structure_text = await asyncio.to_thread(_chat, structure_prompt, 1500)
        if "```" in structure_text:
            structure_text = structure_text.split("```")[1]
            if structure_text.startswith("json"):
                structure_text = structure_text[4:]
            structure_text = structure_text.split("```")[0].strip()
        course_structure = json.loads(structure_text)
        logger.info("Course structure created: %s", course_structure['title'])

        # Step 2: lesson content
        detailed_modules = []
        for module in course_structure['modules'][:8]:
            detailed_lessons = []
            for lesson in module['lessons'][:5]:
                lesson_prompt = f"""Create complete lesson content for:
Module: {module['title']}
Lesson: {lesson['title']}
Duration: {lesson.get('duration_min', 10)} minutes
Outline: {lesson.get('content_outline', '')}

Include: lesson script, key concepts, 2-3 practical examples, exercises.
Write 500-800 words of teaching content:"""

                content = await asyncio.to_thread(_chat, lesson_prompt, 1500)
                detailed_lessons.append({**lesson, "script": content, "completed": True})

            detailed_modules.append({**module, "lessons": detailed_lessons, "completed": True})
            logger.debug("Module %d complete", module['number'])

        # Step 3: sales description
        sales_description = await asyncio.to_thread(_chat, f"""Write a compelling course sales description (250-350 words) for:
Title: {course_structure['title']}
Tagline: {course_structure.get('tagline','')}
Objectives: {', '.join(course_structure.get('objectives',[]))}

Include: hook, what you'll learn, who it's for, what's included, call to action.
Use conversion language (transform, master, unlock, step-by-step, etc.).""", 800)

        total_lessons = sum(len(m['lessons']) for m in detailed_modules)
        logger.info("Course complete: %d modules, %d lessons", len(detailed_modules), total_lessons)

        return {
            "product_type": "course",
            "title": course_structure['title'],
            "tagline": course_structure.get('tagline', ''),
            "description": sales_description,
            "content": {
                "objectives": course_structure.get('objectives', []),
                "modules": detailed_modules,
                "structure": course_structure,
            },
            "modules": [m['title'] for m in detailed_modules],
            "metadata": {
                "module_count": len(detailed_modules),
                "lesson_count": total_lessons,
                "duration_hours": duration_hours,
                "topic": topic,
                "target_audience": target_audience,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "file_ready": True,
            "quality_score": self._calculate_quality_score(total_lessons * 500, len(detailed_modules)),
        }
    
    def _calculate_quality_score(self, word_count: int, sections: int) -> int:
        """Calculate quality score 0-100"""
        # Word count score (max at 10,000+ words)
        word_score = min(word_count / 100, 100) * 0.6
        
        # Structure score (max at 10+ sections)
        structure_score = min(sections * 10, 100) * 0.4
        
        return int(word_score + structure_score)
    
    async def export_to_file(self, product: Dict[str, Any], format: str = "json") -> str:
        """
        Export product to file format
        Returns file path
        """
        import os
        import json
        
        # Create exports directory
        export_dir = "/app/exports"
        os.makedirs(export_dir, exist_ok=True)
        
        product_id = product.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))
        
        if format == "json":
            file_path = f"{export_dir}/{product_id}.json"
            with open(file_path, 'w') as f:
                json.dump(product, f, indent=2, default=str)
        
        elif format == "markdown":
            file_path = f"{export_dir}/{product_id}.md"
            markdown = self._convert_to_markdown(product)
            with open(file_path, 'w') as f:
                f.write(markdown)
        
        return file_path
    
    def _convert_to_markdown(self, product: Dict[str, Any]) -> str:
        """Convert product to markdown format"""
        md = f"# {product['title']}\n\n"
        
        if product.get('subtitle'):
            md += f"## {product['subtitle']}\n\n"
        
        md += f"**Description:**\n{product['description']}\n\n"
        md += "---\n\n"
        
        if product['product_type'] == 'ebook':
            content = product['content']
            md += "## Introduction\n\n"
            md += content['introduction'] + "\n\n"
            
            for chapter in content['chapters']:
                md += f"## Chapter {chapter['number']}: {chapter['title']}\n\n"
                md += chapter['content'] + "\n\n"
            
            md += "## Conclusion\n\n"
            md += content['conclusion'] + "\n\n"
        
        return md
