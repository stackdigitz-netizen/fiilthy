"""
Project File Manager
Organizes all products/projects in a clean file system
Allows download, copy, and management of all AI-generated content
"""
import os
import json
import zipfile
import io
import base64
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

class ProjectFileManager:
    """Manages all projects and products in an organized file system"""
    
    def __init__(self, db=None):
        self.db = db
        self.base_path = "/tmp/projects" if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) else "/app/projects"
        os.makedirs(self.base_path, exist_ok=True)
    
    async def create_project(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project folder for a product"""
        project_id = product.get("id", f"proj-{uuid.uuid4().hex[:8]}")
        project_path = os.path.join(self.base_path, project_id)
        os.makedirs(project_path, exist_ok=True)
        
        # Create project structure
        folders = ["content", "assets", "marketing", "analytics", "exports"]
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Save product data
        product_file = os.path.join(project_path, "product.json")
        with open(product_file, "w") as f:
            json.dump(product, f, indent=2, default=str)
        
        # Save content
        if product.get("content"):
            content_file = os.path.join(project_path, "content", "main_content.md")
            with open(content_file, "w") as f:
                f.write(product.get("content", ""))
        
        # Create README
        readme = self._generate_readme(product)
        readme_file = os.path.join(project_path, "README.md")
        with open(readme_file, "w") as f:
            f.write(readme)

        # Save reusable AI video prompts for this project.
        prompt_pack = self._build_video_prompt_pack(product)
        self._write_video_prompt_files(project_path, prompt_pack)
        
        # Save to database
        project_doc = {
            "id": project_id,
            "product_id": product.get("id"),
            "title": product.get("title"),
            "type": product.get("product_type", "ebook"),
            "path": project_path,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": self._list_project_files(project_path)
        }
        
        if self.db is not None:
            await self.db.projects.update_one(
                {"id": project_id},
                {"$set": project_doc},
                upsert=True
            )
        
        return {
            "success": True,
            "project": project_doc
        }

    def _build_video_prompt_pack(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reusable set of project-specific prompts for video generation tools."""
        title = (product.get("title") or "Untitled Product").strip()
        product_type = (product.get("product_type") or "digital product").replace("_", " ")
        description = (product.get("description") or product.get("content") or "").strip()
        short_description = " ".join(description.split())[:420] or f"A premium {product_type} called {title}."
        price = product.get("price")
        offer = f"priced at ${price}" if price not in (None, "") else "ready for launch"
        audience = product.get("target_audience") or product.get("audience") or "online buyers looking for a fast result"

        prompts = [
            {
                "id": "hero-launch",
                "title": "Hero Launch Ad",
                "goal": "Create a cinematic reveal for the project offer",
                "platform": "TikTok / Reels / Shorts",
                "duration_seconds": 20,
                "aspect_ratio": "9:16",
                "prompt": (
                    f"Create a polished vertical launch ad for {title}, a {product_type} {offer}. "
                    f"Show bold kinetic typography, premium product mockups, dramatic lighting, fast punch-in camera moves, "
                    f"clean studio background, luxury digital brand feel, persuasive pacing, and a strong final call to action. "
                    f"The audience is {audience}. Highlight this offer: {short_description}"
                ),
                "voiceover": (
                    f"Meet {title}. This {product_type} is built for {audience}. "
                    f"If you want a faster path to results, this is the offer to watch."
                ),
                "cta": f"Get {title} now.",
            },
            {
                "id": "problem-solution",
                "title": "Problem To Solution",
                "goal": "Frame the project as the answer to a painful problem",
                "platform": "TikTok / Reels / Shorts",
                "duration_seconds": 25,
                "aspect_ratio": "9:16",
                "prompt": (
                    f"Generate a short-form problem-solution video for {title}. Open with frustration and chaos, then transition "
                    f"into clarity and momentum once the {product_type} appears. Use split screens, animated captions, mobile-first framing, "
                    f"high-energy motion graphics, before-and-after storytelling, and clear benefit-driven visuals. Base the message on: {short_description}"
                ),
                "voiceover": (
                    f"Still stuck trying to solve this the hard way? {title} turns the mess into a step-by-step system you can actually use."
                ),
                "cta": "See how the system works.",
            },
            {
                "id": "demo-walkthrough",
                "title": "Feature Demo Walkthrough",
                "goal": "Show what the project includes and how it feels to use",
                "platform": "Product Demo / Sales Page Video",
                "duration_seconds": 35,
                "aspect_ratio": "16:9",
                "prompt": (
                    f"Create a clean demo video for {title}. Show close-up interface or product shots, scrolling pages, zoom-ins on key sections, "
                    f"highlight callouts, minimal premium UI overlays, subtle camera drift, soft editorial lighting, and smooth transitions. "
                    f"Make the viewer feel the value of this {product_type}. Include these details naturally: {short_description}"
                ),
                "voiceover": (
                    f"Inside {title}, you get a focused {product_type} designed to help {audience}. Here is what makes it worth having."
                ),
                "cta": "Watch the full breakdown and download.",
            },
            {
                "id": "ugc-style",
                "title": "UGC Testimonial Style",
                "goal": "Make the project feel socially proven and relatable",
                "platform": "TikTok / Instagram Reels",
                "duration_seconds": 18,
                "aspect_ratio": "9:16",
                "prompt": (
                    f"Produce a realistic UGC-style promo for {title}. Use handheld phone framing, authentic creator energy, quick jump cuts, "
                    f"caption overlays, natural room lighting, excited reactions, and direct-to-camera delivery. The creator should explain why "
                    f"this {product_type} stands out for {audience}. Reference this core offer: {short_description}"
                ),
                "voiceover": (
                    f"I was not expecting {title} to be this useful. If you want something practical, fast, and actually clear, this is it."
                ),
                "cta": f"Try {title} today.",
            },
            {
                "id": "launch-countdown",
                "title": "Offer Countdown Push",
                "goal": "Drive urgency for launch or promotion windows",
                "platform": "Ads / Retargeting Video",
                "duration_seconds": 15,
                "aspect_ratio": "9:16",
                "prompt": (
                    f"Create a punchy countdown-style ad for {title}. Use large countdown numerals, urgent text animation, product beauty shots, "
                    f"motion blur transitions, energetic soundtrack cues, and a final urgency card. Sell the value of the {product_type} while pushing action. "
                    f"Center the message around: {short_description}"
                ),
                "voiceover": (
                    f"If {title} is on your list, do not wait. This is your moment to grab the {product_type} and move now."
                ),
                "cta": "Buy before the offer closes.",
            },
        ]

        return {
            "project_title": title,
            "product_type": product_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "prompts": prompts,
        }

    def _write_video_prompt_files(self, project_path: str, prompt_pack: Dict[str, Any]) -> None:
        """Persist prompt packs inside the project so they ship with the ZIP export."""
        marketing_path = os.path.join(project_path, "marketing")
        os.makedirs(marketing_path, exist_ok=True)

        json_path = os.path.join(marketing_path, "video_prompts.json")
        with open(json_path, "w") as f:
            json.dump(prompt_pack, f, indent=2)

        lines = [
            f"# Video Prompt Pack: {prompt_pack.get('project_title', 'Project')}",
            "",
            f"Generated: {prompt_pack.get('generated_at', '')}",
            "",
        ]
        for index, prompt in enumerate(prompt_pack.get("prompts", []), start=1):
            lines.extend([
                f"## {index}. {prompt.get('title', 'Prompt')}",
                f"- Goal: {prompt.get('goal', '')}",
                f"- Platform: {prompt.get('platform', '')}",
                f"- Duration: {prompt.get('duration_seconds', '')} seconds",
                f"- Aspect Ratio: {prompt.get('aspect_ratio', '')}",
                "",
                "### Prompt",
                prompt.get("prompt", ""),
                "",
                "### Voiceover",
                prompt.get("voiceover", ""),
                "",
                "### CTA",
                prompt.get("cta", ""),
                "",
            ])

        markdown_path = os.path.join(marketing_path, "video_prompts.md")
        with open(markdown_path, "w") as f:
            f.write("\n".join(lines))

    async def _sync_project_files(self, project_id: str, project_path: str) -> None:
        if self.db is not None:
            await self.db.projects.update_one(
                {"id": project_id},
                {"$set": {"files": self._list_project_files(project_path)}},
            )
    
    def _generate_readme(self, product: Dict) -> str:
        """Generate a README for the project"""
        return f"""# {product.get('title', 'Untitled Project')}

## Product Information
- **Type:** {product.get('product_type', 'Digital Product')}
- **Price:** ${product.get('price', 0)}
- **Status:** {product.get('status', 'draft')}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Description
{product.get('description', 'No description available.')}

## Folder Structure
```
├── content/          # Main product content
├── assets/           # Images, covers, graphics
├── marketing/        # Social posts, ad copy
├── analytics/        # Performance data
└── exports/          # Downloadable files (PDF, ZIP)
```

## Publishing Status
- [ ] Gumroad
- [ ] Amazon KDP
- [ ] Teachable
- [ ] Shopify

## Notes
Generated by CEO AI System
"""
    
    def _list_project_files(self, path: str) -> List[Dict]:
        """List all files in a project"""
        files = []
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, path)
                files.append({
                    "name": filename,
                    "path": rel_path,
                    "size": os.path.getsize(filepath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        return files
    
    async def list_projects(self, status: str = None) -> List[Dict]:
        """List all projects"""
        if self.db is None:
            # Fallback to filesystem
            projects = []
            if os.path.exists(self.base_path):
                for name in os.listdir(self.base_path):
                    path = os.path.join(self.base_path, name)
                    if os.path.isdir(path):
                        product_file = os.path.join(path, "product.json")
                        if os.path.exists(product_file):
                            with open(product_file) as f:
                                product = json.load(f)
                            projects.append({
                                "id": name,
                                "title": product.get("title", name),
                                "type": product.get("product_type", "unknown"),
                                "path": path,
                                "files": self._list_project_files(path)
                            })
            return projects
        
        query = {}
        if status:
            query["status"] = status
        
        projects = await self.db.projects.find(query, {"_id": 0}).to_list(100)
        return projects
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project with all details"""
        project_path = os.path.join(self.base_path, project_id)
        
        if not os.path.exists(project_path):
            return {"success": False, "error": "Project not found"}
        
        # Load product data
        product_file = os.path.join(project_path, "product.json")
        product = {}
        if os.path.exists(product_file):
            with open(product_file) as f:
                product = json.load(f)
        
        # Get files
        files = self._list_project_files(project_path)
        
        return {
            "success": True,
            "project": {
                "id": project_id,
                "title": product.get("title", project_id),
                "product": product,
                "path": project_path,
                "files": files
            }
        }

    async def get_video_prompts(self, project_id: str) -> Dict[str, Any]:
        """Load or generate video prompts for a project."""
        project_path = os.path.join(self.base_path, project_id)
        if not os.path.exists(project_path):
            return {"success": False, "error": "Project not found"}

        prompt_file = os.path.join(project_path, "marketing", "video_prompts.json")
        if os.path.exists(prompt_file):
            with open(prompt_file) as f:
                return {"success": True, "video_prompts": json.load(f)}

        product_file = os.path.join(project_path, "product.json")
        if not os.path.exists(product_file):
            return {"success": False, "error": "Project data missing"}

        with open(product_file) as f:
            product = json.load(f)

        prompt_pack = self._build_video_prompt_pack(product)
        self._write_video_prompt_files(project_path, prompt_pack)
        await self._sync_project_files(project_id, project_path)
        return {"success": True, "video_prompts": prompt_pack}
    
    async def download_project(self, project_id: str) -> Dict[str, Any]:
        """Create a downloadable ZIP of the project"""
        project_path = os.path.join(self.base_path, project_id)
        
        if not os.path.exists(project_path):
            return {"success": False, "error": "Project not found"}
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, project_path)
                    zipf.write(filepath, arcname)
        
        zip_buffer.seek(0)
        zip_base64 = base64.b64encode(zip_buffer.read()).decode()
        
        return {
            "success": True,
            "filename": f"{project_id}.zip",
            "content": zip_base64,
            "size": len(zip_base64)
        }
    
    async def add_file_to_project(self, project_id: str, folder: str, filename: str, content: str) -> Dict:
        """Add a file to a project"""
        project_path = os.path.join(self.base_path, project_id, folder)
        os.makedirs(project_path, exist_ok=True)
        
        filepath = os.path.join(project_path, filename)
        with open(filepath, "w") as f:
            f.write(content)
        
        return {
            "success": True,
            "path": os.path.relpath(filepath, self.base_path)
        }
    
    async def get_file_content(self, project_id: str, file_path: str) -> Dict:
        """Get content of a specific file"""
        full_path = os.path.join(self.base_path, project_id, file_path)
        
        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}
        
        try:
            with open(full_path, "r") as f:
                content = f.read()
            return {"success": True, "content": content, "path": file_path}
        except:
            # Binary file
            with open(full_path, "rb") as f:
                content = base64.b64encode(f.read()).decode()
            return {"success": True, "content": content, "is_binary": True, "path": file_path}
    
    async def delete_project(self, project_id: str) -> Dict:
        """Delete a project"""
        import shutil
        project_path = os.path.join(self.base_path, project_id)
        
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        
        if self.db is not None:
            await self.db.projects.delete_one({"id": project_id})
        
        return {"success": True, "deleted": project_id}


class PublishingGuide:
    """
    Tells users where they can publish products and whether it's automated or manual.
    Respects platform rules and TOS.
    """
    
    PLATFORMS = {
        # === AUTOMATED (API Available) ===
        "gumroad": {
            "name": "Gumroad",
            "automated": False,  # API doesn't support product creation
            "manual_required": True,
            "instructions": "Go to gumroad.com/products/new → Upload your product → Set price → Publish",
            "product_types": ["ebook", "course", "template", "software", "music"],
            "fees": "10% + payment processing",
            "time_to_publish": "5 minutes",
            "url": "https://gumroad.com/products/new"
        },
        "amazon_kdp": {
            "name": "Amazon KDP",
            "automated": False,
            "manual_required": True,
            "instructions": "Go to kdp.amazon.com → Create New Title → Upload manuscript & cover → Set pricing → Publish",
            "product_types": ["ebook", "paperback", "hardcover"],
            "fees": "30-65% royalty (you keep)",
            "time_to_publish": "24-72 hours review",
            "url": "https://kdp.amazon.com"
        },
        "teachable": {
            "name": "Teachable",
            "automated": False,
            "manual_required": True,
            "instructions": "Create school → Add course → Upload videos/content → Set pricing → Publish",
            "product_types": ["course", "coaching", "membership"],
            "fees": "0-10% depending on plan",
            "time_to_publish": "1-2 hours",
            "url": "https://teachable.com"
        },
        "udemy": {
            "name": "Udemy",
            "automated": False,
            "manual_required": True,
            "instructions": "Apply as instructor → Create course → Upload content → Submit for review",
            "product_types": ["course"],
            "fees": "37-97% (Udemy takes large cut on their sales)",
            "time_to_publish": "2-5 days review",
            "url": "https://www.udemy.com/teaching/"
        },
        "etsy": {
            "name": "Etsy",
            "automated": False,
            "manual_required": True,
            "instructions": "Open shop → Create listing → Upload files → Set pricing → Publish",
            "product_types": ["template", "printable", "planner", "digital_art"],
            "fees": "$0.20 listing + 6.5% transaction",
            "time_to_publish": "10 minutes",
            "url": "https://www.etsy.com/sell"
        },
        "shopify": {
            "name": "Shopify",
            "automated": True,  # API supports product creation
            "manual_required": False,
            "instructions": "We can automatically create products in your Shopify store!",
            "product_types": ["ebook", "course", "template", "software", "physical"],
            "fees": "$29+/month + 2.9% payment",
            "time_to_publish": "Instant",
            "url": "https://shopify.com"
        },
        "payhip": {
            "name": "Payhip",
            "automated": False,
            "manual_required": True,
            "instructions": "Create account → Add product → Upload file → Set price → Share link",
            "product_types": ["ebook", "course", "software", "membership"],
            "fees": "5% transaction (free plan)",
            "time_to_publish": "5 minutes",
            "url": "https://payhip.com"
        },
        "ko_fi": {
            "name": "Ko-fi",
            "automated": False,
            "manual_required": True,
            "instructions": "Create page → Go to Shop → Add product → Upload → Publish",
            "product_types": ["ebook", "template", "art", "commissions"],
            "fees": "0% (Ko-fi Gold: $6/month)",
            "time_to_publish": "5 minutes",
            "url": "https://ko-fi.com"
        },
        
        # === SOCIAL MEDIA (Posting) ===
        "twitter": {
            "name": "Twitter/X",
            "automated": True,
            "manual_required": False,
            "instructions": "We can auto-post promotional tweets with your product links!",
            "product_types": ["all"],
            "fees": "Free",
            "time_to_publish": "Instant",
            "notes": "Best for: Announcements, threads, engagement"
        },
        "instagram": {
            "name": "Instagram",
            "automated": False,  # API limited for regular posts
            "manual_required": True,
            "instructions": "Create post/reel → Add product images → Write caption → Add link in bio",
            "product_types": ["all"],
            "fees": "Free",
            "time_to_publish": "5 minutes",
            "notes": "We generate captions & hashtags for you!"
        },
        "tiktok": {
            "name": "TikTok",
            "automated": False,
            "manual_required": True,
            "instructions": "Record/upload video → Add caption → Link in bio",
            "product_types": ["all"],
            "fees": "Free",
            "time_to_publish": "5 minutes",
            "notes": "We generate video scripts for you!"
        },
        "youtube": {
            "name": "YouTube",
            "automated": True,  # API supports uploads
            "manual_required": False,
            "instructions": "We can upload videos directly to your channel!",
            "product_types": ["all"],
            "fees": "Free",
            "time_to_publish": "Processing time varies",
            "notes": "Great for: Tutorials, promos, shorts"
        },
        "linkedin": {
            "name": "LinkedIn",
            "automated": True,
            "manual_required": False,
            "instructions": "We can auto-post to your LinkedIn profile/page!",
            "product_types": ["course", "ebook", "consulting"],
            "fees": "Free",
            "time_to_publish": "Instant",
            "notes": "Best for: B2B, professional courses"
        },
        "facebook": {
            "name": "Facebook",
            "automated": True,
            "manual_required": False,
            "instructions": "We can post to your Facebook page!",
            "product_types": ["all"],
            "fees": "Free",
            "time_to_publish": "Instant"
        },
        "pinterest": {
            "name": "Pinterest",
            "automated": True,
            "manual_required": False,
            "instructions": "We can create pins linking to your products!",
            "product_types": ["template", "printable", "ebook", "course"],
            "fees": "Free",
            "time_to_publish": "Instant",
            "notes": "Great for visual products, long-term traffic"
        },
        
        # === EMAIL ===
        "email_list": {
            "name": "Email List",
            "automated": True,
            "manual_required": False,
            "instructions": "We can send product announcements to your email list!",
            "product_types": ["all"],
            "fees": "Depends on email provider",
            "time_to_publish": "Instant",
            "notes": "Highest conversion rate!"
        }
    }
    
    def get_publishing_options(self, product_type: str) -> Dict[str, Any]:
        """Get all publishing options for a product type"""
        automated = []
        manual = []
        
        for platform_id, platform in self.PLATFORMS.items():
            if product_type in platform.get("product_types", []) or "all" in platform.get("product_types", []):
                info = {
                    "id": platform_id,
                    "name": platform["name"],
                    "fees": platform.get("fees", "Varies"),
                    "time": platform.get("time_to_publish", "Varies"),
                    "url": platform.get("url", ""),
                    "instructions": platform["instructions"],
                    "notes": platform.get("notes", "")
                }
                
                if platform.get("automated") and not platform.get("manual_required"):
                    automated.append(info)
                else:
                    manual.append(info)
        
        return {
            "automated": automated,
            "manual": manual,
            "total_options": len(automated) + len(manual)
        }
    
    def get_platform_guide(self, platform_id: str) -> Dict[str, Any]:
        """Get detailed guide for a specific platform"""
        platform = self.PLATFORMS.get(platform_id)
        if not platform:
            return {"error": "Platform not found"}
        
        return {
            "id": platform_id,
            **platform
        }
    
    def get_all_platforms(self) -> List[Dict]:
        """Get all platforms with their status"""
        return [
            {"id": pid, **pdata}
            for pid, pdata in self.PLATFORMS.items()
        ]
