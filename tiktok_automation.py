#!/usr/bin/env python3
"""
🚀 TikTok Traffic Automation Script

This script helps you:
1. Track posting progress
2. Generate posting schedules
3. Monitor sales from TikTok traffic
4. Create performance reports

Usage:
python tiktok_automation.py --action schedule
python tiktok_automation.py --action report
python tiktok_automation.py --action sales
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse

# Configuration
DATA_DIR = "tiktok_data"
POSTING_LOG = os.path.join(DATA_DIR, "posting_log.json")
SALES_LOG = os.path.join(DATA_DIR, "sales_log.json")
SCRIPTS_FILE = "VIRAL_TIKTOK_SCRIPTS.md"

class TikTokAutomation:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.posting_log = self.load_json(POSTING_LOG, [])
        self.sales_log = self.load_json(SALES_LOG, [])

    def load_json(self, filepath: str, default: Any = None) -> Any:
        """Load JSON file with fallback to default"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Ensure we return a list for logs
                if filepath in [POSTING_LOG, SALES_LOG]:
                    return data if isinstance(data, list) else []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return default or []

    def save_json(self, filepath: str, data: Any):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def generate_schedule(self, days: int = 7) -> List[Dict]:
        """Generate a posting schedule for the next N days"""
        schedule = []
        start_date = datetime.now()

        # Script rotation pattern
        script_rotation = [
            "AI Offer Engine", "Digital Launch", "TikTok Affiliate",
            "ChatGPT Business", "Mixed/Success Stories"
        ]

        for day in range(days):
            date = start_date + timedelta(days=day)
            day_name = date.strftime("%A")

            # 3 posts per day
            for post_num in range(1, 4):
                script_type = script_rotation[(day + post_num - 1) % len(script_rotation)]

                schedule.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "post_number": post_num,
                    "script_type": script_type,
                    "time_suggestion": self.get_posting_time(post_num),
                    "status": "pending",
                    "video_id": None,
                    "views": 0,
                    "engagement": 0,
                    "clicks": 0
                })

        return schedule

    def get_posting_time(self, post_num: int) -> str:
        """Get suggested posting time based on post number"""
        times = {
            1: "7:00 AM",
            2: "12:00 PM",
            3: "6:00 PM"
        }
        return times.get(post_num, "12:00 PM")

    def log_post(self, date: str, script_type: str, video_id: str = None):
        """Log a completed post"""
        post_entry = {
            "date": date,
            "script_type": script_type,
            "video_id": video_id,
            "posted_at": datetime.now().isoformat(),
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "saves": 0,
            "bio_clicks": 0
        }

        self.posting_log.append(post_entry)
        self.save_json(POSTING_LOG, self.posting_log)
        print(f"✅ Logged post: {script_type} on {date}")

    def log_sale(self, amount: float, product: str, source: str = "tiktok"):
        """Log a sale from TikTok"""
        sale_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "product": product,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }

        self.sales_log.append(sale_entry)
        self.save_json(SALES_LOG, self.sales_log)
        print(f"💰 Logged sale: ${amount} from {product}")

    def generate_report(self) -> Dict:
        """Generate performance report"""
        total_posts = len(self.posting_log)
        total_sales = len(self.sales_log)
        total_revenue = sum(sale.get("amount", 0) for sale in self.sales_log)

        # Calculate averages
        if total_posts > 0:
            avg_views = sum(p.get("views", 0) for p in self.posting_log) / total_posts
            avg_engagement = sum(p.get("likes", 0) + p.get("comments", 0) + p.get("shares", 0) + p.get("saves", 0) for p in self.posting_log) / total_posts
        else:
            avg_views = 0
            avg_engagement = 0

        # Revenue per post
        revenue_per_post = total_revenue / total_posts if total_posts > 0 else 0

        return {
            "total_posts": total_posts,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "avg_views_per_post": round(avg_views, 1),
            "avg_engagement_per_post": round(avg_engagement, 1),
            "revenue_per_post": round(revenue_per_post, 2),
            "conversion_rate": round((total_sales / total_posts * 100), 2) if total_posts > 0 else 0
        }

    def export_to_csv(self, filename: str = "tiktok_report.csv"):
        """Export posting log to CSV"""
        if not self.posting_log:
            print("No posting data to export")
            return

        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = self.posting_log[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.posting_log)

        print(f"📊 Exported to {filepath}")

def main():
    parser = argparse.ArgumentParser(description="TikTok Traffic Automation")
    parser.add_argument("--action", choices=["schedule", "report", "log_post", "log_sale", "export"],
                       required=True, help="Action to perform")
    parser.add_argument("--days", type=int, default=7, help="Number of days for schedule")
    parser.add_argument("--date", help="Date for logging (YYYY-MM-DD)")
    parser.add_argument("--script", help="Script type for logging")
    parser.add_argument("--video_id", help="Video ID for logging")
    parser.add_argument("--amount", type=float, help="Sale amount")
    parser.add_argument("--product", help="Product name")

    args = parser.parse_args()
    automation = TikTokAutomation()

    if args.action == "schedule":
        schedule = automation.generate_schedule(args.days)
        print("📅 7-Day TikTok Posting Schedule:")
        print("-" * 80)
        for item in schedule:
            print(f"{item['date']} ({item['day']}) - Post {item['post_number']}: {item['script_type']} @ {item['time_suggestion']}")

    elif args.action == "report":
        report = automation.generate_report()
        print("📊 TikTok Performance Report:")
        print("-" * 40)
        print(f"Total Posts: {report['total_posts']}")
        print(f"Total Sales: {report['total_sales']}")
        print(f"Total Revenue: ${report['total_revenue']:.2f}")
        print(f"Avg Views/Post: {report['avg_views_per_post']}")
        print(f"Avg Engagement/Post: {report['avg_engagement_per_post']}")
        print(f"Revenue/Post: ${report['revenue_per_post']}")
        print(f"Conversion Rate: {report['conversion_rate']}%")

    elif args.action == "log_post":
        if not args.date or not args.script:
            print("❌ Need --date and --script for logging post")
            return
        automation.log_post(args.date, args.script, args.video_id)

    elif args.action == "log_sale":
        if not args.amount or not args.product:
            print("❌ Need --amount and --product for logging sale")
            return
        automation.log_sale(args.amount, args.product)

    elif args.action == "export":
        automation.export_to_csv()

if __name__ == "__main__":
    main()