"""
Course Creation AI
Creates video & text courses automatically
"""
import asyncio
from typing import Dict, Any, List
import random
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class CourseCreator:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def generate_course(self,
                            topic: str,
                            target_audience: str = "beginners",
                            duration_hours: int = 3,
                            learning_objectives: List[str] = None) -> Dict[str, Any]:
        """
        Generate a complete online course
        
        Args:
            topic: Course topic/subject
            target_audience: Target student level
            duration_hours: Desired course length in hours
            learning_objectives: What students will learn
            
        Returns:
            Dictionary with course structure, modules, content
        """
        
        # Initialize AI chat
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"course-creator-{datetime.now().timestamp()}",
            system_message="You are an expert instructional designer and online course creator. You create engaging, structured courses that deliver real learning outcomes."
        ).with_model("openai", "gpt-5.2")
        
        # Determine course structure
        num_modules = max(4, min(8, duration_hours))
        
        learning_obj_text = ""
        if learning_objectives:
            learning_obj_text = f"\nLearning Objectives: {', '.join(learning_objectives)}"
        
        # Generate course structure
        structure_prompt = f"""
Create a comprehensive online course structure for: {topic}

Target Audience: {target_audience}
Course Duration: {duration_hours} hours
Number of Modules: {num_modules}{learning_obj_text}

Provide:
1. Engaging course title
2. Compelling course description (2-3 sentences)
3. {num_modules} module titles with descriptions
4. 3-5 lessons per module with descriptions
5. Key skills students will gain
6. Assessment types for each module

Format as JSON:
{{
  "title": "Course Title",
  "description": "Course description",
  "modules": [
    {{
      "number": 1,
      "title": "Module Title",
      "description": "What this module covers",
      "duration_minutes": 45,
      "lessons": [
        {{"title": "Lesson Title", "type": "video", "duration_minutes": 15, "description": "Lesson content"}}
      ],
      "assessment": "Quiz/Assignment/Project"
    }}
  ],
  "skills_gained": ["Skill 1", "Skill 2"]
}}
"""
        
        try:
            # Generate structure
            structure_message = UserMessage(text=structure_prompt)
            structure_response = await chat.send_message(structure_message)
            
            import json
            structure_text = structure_response.strip()
            if "```json" in structure_text:
                structure_text = structure_text.split("```json")[1].split("```")[0].strip()
            elif "```" in structure_text:
                structure_text = structure_text.split("```")[1].split("```")[0].strip()
            
            course_structure = json.loads(structure_text)
            
            # Generate sample lesson content for first module
            first_module = course_structure['modules'][0]
            content_prompt = f"""
Write detailed content for the first lesson of this course module:

Module: {first_module['title']}
Lesson: {first_module['lessons'][0]['title']}
Description: {first_module['lessons'][0]['description']}

Provide:
1. Video script (engaging and instructional)
2. Key concepts to cover
3. Practical examples
4. Action items for students

Format as structured lesson content.
"""
            
            content_message = UserMessage(text=content_prompt)
            content_response = await chat.send_message(content_message)
            
            # Compile course data
            course_data = {
                "id": f"course-{random.randint(1000, 9999)}",
                "title": course_structure['title'],
                "description": course_structure['description'],
                "product_type": "course",
                "content": {
                    "structure": course_structure,
                    "sample_lesson": content_response
                },
                "status": "ready",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "topic": topic,
                    "target_audience": target_audience,
                    "duration_hours": duration_hours,
                    "num_modules": len(course_structure['modules']),
                    "total_lessons": sum(len(m.get('lessons', [])) for m in course_structure['modules']),
                    "skills_gained": course_structure.get('skills_gained', [])
                }
            }
            
            return course_data
            
        except Exception as e:
            print(f"Error generating course: {str(e)}")
            raise
