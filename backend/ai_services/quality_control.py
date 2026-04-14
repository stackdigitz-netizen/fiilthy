"""
Quality Control System - Strict validation for all generated content
Ensures products, videos, and content meet quality standards
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class QCLevel(str, Enum):
    CRITICAL = "critical"  # Blocks publishing
    HIGH = "high"           # Requires action
    MEDIUM = "medium"       # Warning
    LOW = "low"             # Info only


class QCIssue:
    """Represents a QC issue"""
    def __init__(self, level: QCLevel, category: str, message: str, fix_suggestion: str = ""):
        self.level = level
        self.category = category
        self.message = message
        self.fix_suggestion = fix_suggestion
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self):
        return {
            "level": self.level.value,
            "category": self.category,
            "message": self.message,
            "fix_suggestion": self.fix_suggestion,
            "timestamp": self.timestamp
        }


class ContentQualityControl:
    """Validates content quality"""
    
    # Minimum standards
    MIN_TITLE_LENGTH = 5
    MAX_TITLE_LENGTH = 200
    MIN_DESCRIPTION_LENGTH = 20
    MAX_DESCRIPTION_LENGTH = 5000
    MIN_PRICE = 4.99
    MAX_PRICE = 9999.99
    
    # Text quality rules
    PROFANITY_WORDS = {"bad", "worst", "terrible", "horrible"}  # Extend as needed
    MIN_UNIQUE_WORDS = 20
    
    @staticmethod
    def validate_product(product: Dict[str, Any]) -> Tuple[bool, List[QCIssue]]:
        """Validate product with standards"""
        issues = []
        
        # Title validation
        title = product.get("title", "").strip()
        if not title:
            issues.append(QCIssue(
                QCLevel.CRITICAL,
                "Title",
                "Product title is empty",
                "Add a clear, descriptive product title"
            ))
        elif len(title) < ContentQualityControl.MIN_TITLE_LENGTH:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Title",
                f"Title too short (min {ContentQualityControl.MIN_TITLE_LENGTH} chars)",
                f"Expand title to at least {ContentQualityControl.MIN_TITLE_LENGTH} characters"
            ))
        elif len(title) > ContentQualityControl.MAX_TITLE_LENGTH:
            issues.append(QCIssue(
                QCLevel.MEDIUM,
                "Title",
                f"Title too long (max {ContentQualityControl.MAX_TITLE_LENGTH} chars)",
                f"Shorten title to {ContentQualityControl.MAX_TITLE_LENGTH} characters"
            ))
        
        # Description validation
        desc = product.get("description", "").strip()
        if not desc:
            issues.append(QCIssue(
                QCLevel.CRITICAL,
                "Description",
                "Product description is empty",
                "Add detailed description of product benefits"
            ))
        elif len(desc) < ContentQualityControl.MIN_DESCRIPTION_LENGTH:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Description",
                f"Description too short (min {ContentQualityControl.MIN_DESCRIPTION_LENGTH} chars)",
                f"Expand description with more details"
            ))
        
        # Price validation
        price = product.get("price")
        if price is None:
            issues.append(QCIssue(
                QCLevel.CRITICAL,
                "Price",
                "No price set",
                "Set a competitive price between $4.99 and $9,999.99"
            ))
        elif not isinstance(price, (int, float)):
            issues.append(QCIssue(
                QCLevel.CRITICAL,
                "Price",
                "Price must be a number",
                "Enter valid price amount"
            ))
        elif price < ContentQualityControl.MIN_PRICE:
            issues.append(QCIssue(
                QCLevel.MEDIUM,
                "Price",
                f"Price too low (min ${ContentQualityControl.MIN_PRICE})",
                "Increase price to minimum $4.99 or validate pricing strategy"
            ))
        elif price > ContentQualityControl.MAX_PRICE:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Price",
                f"Price too high (max ${ContentQualityControl.MAX_PRICE})",
                "Reduce price or justify premium positioning"
            ))
        
        # Cover image
        if not product.get("cover"):
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Cover",
                "No cover image uploaded",
                "Upload professional cover image"
            ))
        
        # Check for low-quality language
        combined_text = f"{title} {desc}".lower()
        for word in ContentQualityControl.PROFANITY_WORDS:
            if word in combined_text:
                issues.append(QCIssue(
                    QCLevel.MEDIUM,
                    "Language",
                    f"Potentially harmful word detected: '{word}'",
                    "Use professional, positive language only"
                ))
        
        # Check unique words
        unique_words = len(set(combined_text.split()))
        if unique_words < ContentQualityControl.MIN_UNIQUE_WORDS:
            issues.append(QCIssue(
                QCLevel.MEDIUM,
                "Content",
                f"Limited vocabulary ({unique_words} unique words)",
                "Add more varied, descriptive language"
            ))
        
        # Tags validation
        tags = product.get("tags", [])
        if not tags or len(tags) < 3:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Tags",
                "Insufficient tags for discovery",
                "Add at least 5 relevant tags"
            ))
        
        has_critical = any(i.level == QCLevel.CRITICAL for i in issues)
        return (not has_critical, issues)
    
    @staticmethod
    def validate_video(video_data: Dict[str, Any]) -> Tuple[bool, List[QCIssue]]:
        """Validate video content"""
        issues = []
        
        # File validation
        file_path = video_data.get("file_path")
        if not file_path:
            issues.append(QCIssue(
                QCLevel.CRITICAL,
                "File",
                "No video file specified",
                "Provide valid video file path"
            ))
        
        # Duration validation
        duration = video_data.get("duration_seconds")
        if duration is None:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Duration",
                "Video duration not specified",
                "Ensure video duration is detected"
            ))
        elif duration < 10:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Duration",
                "Video too short (min 10 seconds)",
                "Lengthen video to minimum 10 seconds"
            ))
        elif duration > 600:
            issues.append(QCIssue(
                QCLevel.MEDIUM,
                "Duration",
                "Video may be too long (>10 min)",
                "Consider shorter format for social media"
            ))
        
        # Title validation
        video_title = video_data.get("title", "").strip()
        if not video_title:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Title",
                "Video has no title",
                "Add compelling video title"
            ))
        
        # Description/Script validation
        script = video_data.get("script", "").strip()
        if not script:
            issues.append(QCIssue(
                QCLevel.MEDIUM,
                "Script",
                "No voiceover script",
                "Add voiceover or script"
            ))
        elif len(script) < 30:
            issues.append(QCIssue(
                QCLevel.MEDIUM,
                "Script",
                "Script too short",
                "Expand script for better engagement"
            ))
        
        # Resolution validation
        resolution = video_data.get("resolution")
        if resolution:
            width, height = resolution.get("width", 0), resolution.get("height", 0)
            if width < 720 or height < 720:
                issues.append(QCIssue(
                    QCLevel.MEDIUM,
                    "Resolution",
                    "Low video resolution (min 720p)",
                    "Render at 1080p or higher"
                ))
        
        has_critical = any(i.level == QCLevel.CRITICAL for i in issues)
        return (not has_critical, issues)
    
    @staticmethod
    def validate_post(post: Dict[str, Any]) -> Tuple[bool, List[QCIssue]]:
        """Validate social media post"""
        issues = []
        
        # Content validation
        text = post.get("text", "").strip()
        if not text:
            issues.append(QCIssue(
                QCLevel.CRITICAL,
                "Text",
                "Post body is empty",
                "Add post text content"
            ))
        elif len(text) < 10:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Text",
                "Post too short (min 10 characters)",
                "Expand post with more content"
            ))
        
        # Media validation
        media = post.get("media_urls", [])
        if post.get("requires_media") and not media:
            issues.append(QCIssue(
                QCLevel.CRITICAL,
                "Media",
                "Post requires media but none provided",
                "Upload image or video"
            ))
        
        # Hashtag validation
        hashtags = post.get("hashtags", [])
        if not hashtags or len(hashtags) < 3:
            issues.append(QCIssue(
                QCLevel.MEDIUM,
                "Hashtags",
                "Insufficient hashtags for reach",
                "Add at least 5 relevant hashtags"
            ))
        
        # Platform-specific validation
        platform = post.get("platform", "").lower()
        if platform == "tiktok" and len(text) > 2200:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Platform",
                "TikTok caption too long (max 2200 chars)",
                "Shorten caption for TikTok"
            ))
        elif platform == "twitter" and len(text) > 280:
            issues.append(QCIssue(
                QCLevel.HIGH,
                "Platform",
                "Tweet too long (max 280 chars)",
                "Shorten to fit Twitter limit"
            ))
        
        has_critical = any(i.level == QCLevel.CRITICAL for i in issues)
        return (not has_critical, issues)


class QualityControlReport:
    """Generates QC report"""
    
    def __init__(self):
        self.checks = []
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def add_check(self, passed: bool, issues: List[QCIssue]):
        """Add validation results"""
        self.checks.append({
            "passed": passed,
            "issues": [i.to_dict() for i in issues]
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get QC summary"""
        all_issues = []
        for check in self.checks:
            all_issues.extend(check["issues"])
        
        critical = len([i for i in all_issues if i["level"] == "critical"])
        high = len([i for i in all_issues if i["level"] == "high"])
        medium = len([i for i in all_issues if i["level"] == "medium"])
        low = len([i for i in all_issues if i["level"] == "low"])
        
        is_publishable = critical == 0 and high == 0
        
        return {
            "timestamp": self.timestamp,
            "is_publishable": is_publishable,
            "quality_score": self._calculate_score(all_issues),
            "issue_counts": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "total": len(all_issues)
            },
            "issues": all_issues,
            "recommendations": self._get_recommendations(all_issues)
        }
    
    def _calculate_score(self, issues: List[Dict]) -> float:
        """Calculate quality score 0-100"""
        score = 100.0
        for issue in issues:
            if issue["level"] == "critical":
                score -= 25
            elif issue["level"] == "high":
                score -= 10
            elif issue["level"] == "medium":
                score -= 5
            elif issue["level"] == "low":
                score -= 1
        return max(0, min(100, score))
    
    def _get_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate recommendations"""
        recs = []
        for issue in issues:
            if issue["fix_suggestion"]:
                recs.append(issue["fix_suggestion"])
        return recs[:5]  # Top 5 recommendations


async def run_qc_check(content_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Run QC check on content"""
    report = QualityControlReport()
    
    if content_type == "product":
        passed, issues = ContentQualityControl.validate_product(data)
        report.add_check(passed, issues)
    elif content_type == "video":
        passed, issues = ContentQualityControl.validate_video(data)
        report.add_check(passed, issues)
    elif content_type == "post":
        passed, issues = ContentQualityControl.validate_post(data)
        report.add_check(passed, issues)
    
    return report.get_summary()
