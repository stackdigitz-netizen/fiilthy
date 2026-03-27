"""
Book Writing AI
Generates complete eBooks with AI-generated cover images
"""
import asyncio
from typing import Dict, Any, Optional, List
import random
from datetime import datetime, timezone
import os
import base64
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

load_dotenv()

class BookWriter:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def generate_book(self, 
                           niche: str,
                           keywords: List[str],
                           book_length: str = "medium",
                           target_audience: str = "general") -> Dict[str, Any]:
        """
        Generate a complete eBook
        
        Args:
            niche: The niche/topic for the book
            keywords: List of relevant keywords
            book_length: short/medium/long
            target_audience: Target reader demographic
            
        Returns:
            Dictionary with book content, metadata, and cover image
        """
        
        # Determine book specifications
        word_counts = {"short": "5,000", "medium": "10,000", "long": "20,000"}
        word_count = word_counts.get(book_length, "10,000")
        
        # Initialize AI chat for book writing
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"book-writer-{datetime.now().timestamp()}",
            system_message="You are a professional book author and content strategist. You create engaging, well-structured, and valuable eBooks that readers love."
        ).with_model("openai", "gpt-5.2")
        
        # Step 1: Generate book outline
        outline_prompt = f"""
Create a comprehensive outline for an eBook about: {niche}

Target Keywords: {', '.join(keywords)}
Target Audience: {target_audience}
Desired Length: ~{word_count} words

Provide:
1. An engaging book title
2. A compelling subtitle
3. 8-12 chapter titles with brief descriptions
4. Key takeaways for readers

Format as JSON:
{{
  "title": "Book Title",
  "subtitle": "Book Subtitle",
  "chapters": [
    {{"number": 1, "title": "Chapter Title", "description": "What this chapter covers"}}
  ],
  "key_takeaways": ["Takeaway 1", "Takeaway 2"]
}}
"""
        
        try:
            # Generate outline
            outline_message = UserMessage(text=outline_prompt)
            outline_response = await chat.send_message(outline_message)
            
            import json
            outline_text = outline_response.strip()
            if "```json" in outline_text:
                outline_text = outline_text.split("```json")[1].split("```")[0].strip()
            elif "```" in outline_text:
                outline_text = outline_text.split("```")[1].split("```")[0].strip()
            
            try:
                outline = json.loads(outline_text)
            except json.JSONDecodeError:
                # Fallback: generate a default outline if parsing fails
                outline = {
                    "title": f"The Ultimate Guide to {niche.title()}",
                    "subtitle": f"Master {niche} for {target_audience}",
                    "chapters": [
                        {"number": 1, "title": "Introduction", "description": f"Overview of {niche}"},
                        {"number": 2, "title": "Getting Started", "description": "First steps and basics"},
                        {"number": 3, "title": "Core Concepts", "description": "Key principles and ideas"},
                        {"number": 4, "title": "Practical Application", "description": "Hands-on techniques"},
                        {"number": 5, "title": "Advanced Strategies", "description": "Taking it to the next level"},
                        {"number": 6, "title": "Conclusion", "description": "Summary and next steps"}
                    ],
                    "key_takeaways": [
                        f"Understanding the fundamentals of {niche}",
                        f"Practical strategies for {target_audience}",
                        "Actionable steps you can implement today"
                    ]
                }
            
            # Ensure title exists
            if 'title' not in outline or not outline['title']:
                outline['title'] = f"The Ultimate Guide to {niche.title()}"
            if 'subtitle' not in outline:
                outline['subtitle'] = f"Master {niche} for {target_audience}"
            if 'chapters' not in outline:
                outline['chapters'] = [{"number": 1, "title": "Introduction", "description": f"Overview of {niche}"}]
            if 'key_takeaways' not in outline:
                outline['key_takeaways'] = [f"Understanding the fundamentals of {niche}"]
            
            # Step 2: Generate book content (abbreviated for MVP)
            content_prompt = f"""
Write the introduction and first 2 chapters for the eBook:

Title: {outline['title']}
Subtitle: {outline['subtitle']}

Chapters to write:
{chr(10).join([f"Chapter {ch['number']}: {ch['title']} - {ch['description']}" for ch in outline['chapters'][:2]])}

Make it engaging, informative, and valuable. Use clear structure with headings, subheadings, and actionable insights.
"""
            
            content_message = UserMessage(text=content_prompt)
            content_response = await chat.send_message(content_message)
            
            # Step 3: Generate cover image (optional, may timeout)
            try:
                cover_image_base64 = await asyncio.wait_for(
                    self._generate_cover_image(
                        title=outline['title'],
                        subtitle=outline.get('subtitle', ''),
                        niche=niche
                    ),
                    timeout=30.0  # 30 second timeout for image generation
                )
            except (asyncio.TimeoutError, Exception) as e:
                print(f"Cover image generation failed or timed out: {str(e)}")
                cover_image_base64 = None
            
            # Compile book data
            book_data = {
                "id": f"book-{random.randint(1000, 9999)}",
                "title": outline['title'],
                "subtitle": outline.get('subtitle', ''),
                "description": f"A comprehensive guide to {niche}. {' '.join(outline.get('key_takeaways', [])[:2])}",
                "product_type": "ebook",
                "content": content_response,
                "outline": outline,
                "cover_image": cover_image_base64,
                "status": "ready",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "niche": niche,
                    "keywords": keywords,
                    "word_count_estimate": word_count,
                    "chapters": len(outline.get('chapters', [])),
                    "target_audience": target_audience
                }
            }
            
            return book_data
            
        except Exception as e:
            print(f"Error generating book: {str(e)}")
            raise
    
    async def _generate_cover_image(self, title: str, subtitle: str, niche: str) -> Optional[str]:
        """Generate book cover image using AI"""
        try:
            image_gen = OpenAIImageGeneration(api_key=self.api_key)
            
            cover_prompt = f"""
Professional book cover design for: {title}
Subtitle: {subtitle}
Topic: {niche}

Style: Modern, clean, professional book cover with bold typography.
No people. Abstract or conceptual imagery related to {niche}.
Color scheme: Professional and eye-catching.
"""
            
            images = await image_gen.generate_images(
                prompt=cover_prompt,
                model="gpt-image-1",
                number_of_images=1
            )
            
            if images and len(images) > 0:
                image_base64 = base64.b64encode(images[0]).decode('utf-8')
                return f"data:image/png;base64,{image_base64}"
            
            return None
            
        except Exception as e:
            print(f"Error generating cover image: {str(e)}")
            return None
