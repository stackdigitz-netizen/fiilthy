"""
Adaptive Learning Engine
Machine learning and continuous improvement system for the digital product factory
"""
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import random
import json
import os
from collections import defaultdict
import openai
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class LearningEngine:
    """
    Adaptive learning system that evolves product generation strategies
    based on performance data and market feedback
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client
        self.learning_collection = self.db.learning_data
        self.performance_collection = self.db.product_performance
        openai.api_key = os.environ.get('OPENAI_API_KEY')

    async def record_product_performance(self, product_id: str, metrics: Dict[str, Any]):
        """
        Record product performance metrics for learning

        Args:
            product_id: Unique product identifier
            metrics: Performance data (sales, engagement, reviews, etc.)
        """
        performance_data = {
            "product_id": product_id,
            "timestamp": datetime.now(timezone.utc),
            "metrics": metrics,
            "features": await self._extract_product_features(product_id)
        }

        await self.performance_collection.insert_one(performance_data)

        # Trigger learning update
        await self._update_learning_model()

    async def get_optimal_product_strategy(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the optimal product generation strategy based on learned patterns

        Args:
            opportunity: Market opportunity data

        Returns:
            Optimized product strategy
        """
        # Get historical performance data
        historical_data = await self._get_historical_performance()

        # Analyze successful patterns
        successful_patterns = await self._analyze_success_patterns(historical_data)

        # Generate strategy using AI
        strategy = await self._generate_adaptive_strategy(opportunity, successful_patterns)

        return strategy

    async def run_ab_test(self, product_variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run A/B testing on product variants to determine optimal approach

        Args:
            product_variants: List of product variations to test

        Returns:
            Test results and winner
        """
        test_id = f"ab_test_{datetime.now(timezone.utc).timestamp()}"

        # Distribute variants
        test_groups = self._create_test_groups(product_variants)

        # Store test configuration
        test_config = {
            "test_id": test_id,
            "variants": product_variants,
            "groups": test_groups,
            "start_time": datetime.now(timezone.utc),
            "status": "running"
        }

        await self.learning_collection.insert_one(test_config)

        return {
            "test_id": test_id,
            "groups": test_groups,
            "expected_completion": datetime.now(timezone.utc) + timedelta(days=7)
        }

    async def analyze_ab_results(self, test_id: str) -> Dict[str, Any]:
        """
        Analyze A/B test results and determine winner

        Args:
            test_id: A/B test identifier

        Returns:
            Analysis results
        """
        # Get test configuration
        test_config = await self.learning_collection.find_one({"test_id": test_id})
        if not test_config:
            raise ValueError(f"Test {test_id} not found")

        # Get performance data for each variant
        results = {}
        for variant in test_config["variants"]:
            variant_id = variant.get("variant_id")
            performance = await self._get_variant_performance(variant_id, test_config["start_time"])

            results[variant_id] = {
                "variant": variant,
                "performance": performance,
                "score": self._calculate_variant_score(performance)
            }

        # Determine winner
        winner = max(results.items(), key=lambda x: x[1]["score"])

        # Update learning model
        await self._learn_from_ab_test(results)

        return {
            "test_id": test_id,
            "results": results,
            "winner": winner[0],
            "confidence": self._calculate_confidence(results),
            "recommendations": await self._generate_test_insights(results)
        }

    async def predict_product_success(self, product_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict product success probability using learned model

        Args:
            product_features: Product characteristics

        Returns:
            Success prediction
        """
        # Get historical data for similar products
        similar_products = await self._find_similar_products(product_features)

        # Calculate success probability
        success_prob = await self._calculate_success_probability(product_features, similar_products)

        # Generate improvement suggestions
        suggestions = await self._generate_improvement_suggestions(product_features, success_prob)

        return {
            "success_probability": success_prob,
            "confidence": self._calculate_prediction_confidence(similar_products),
            "similar_products": len(similar_products),
            "improvement_suggestions": suggestions
        }

    async def _extract_product_features(self, product_id: str) -> Dict[str, Any]:
        """Extract features from a product for learning"""
        # This would extract title, description, price, category, etc.
        # For now, return placeholder
        return {
            "product_id": product_id,
            "features_extracted": True,
            "timestamp": datetime.now(timezone.utc)
        }

    async def _update_learning_model(self):
        """Update the learning model with new performance data"""
        # This would retrain ML models, update weights, etc.
        # For now, just log that learning occurred
        learning_update = {
            "timestamp": datetime.now(timezone.utc),
            "type": "model_update",
            "status": "completed"
        }

        await self.learning_collection.insert_one(learning_update)

    async def _get_historical_performance(self) -> List[Dict[str, Any]]:
        """Get historical product performance data"""
        return await self.performance_collection.find().to_list(length=None)

    async def _analyze_success_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in successful products"""
        if not historical_data:
            return {"patterns": [], "insights": "No historical data available"}

        # Group by success metrics
        successful_products = [p for p in historical_data if p.get("metrics", {}).get("revenue", 0) > 10]

        patterns = {
            "avg_price_successful": sum(p["metrics"].get("price", 0) for p in successful_products) / len(successful_products) if successful_products else 0,
            "common_categories": self._find_common_categories(successful_products),
            "successful_word_count": self._analyze_content_length(successful_products),
            "peak_performance_times": self._analyze_timing_patterns(successful_products)
        }

        return patterns

    async def _generate_adaptive_strategy(self, opportunity: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptive product strategy using AI"""
        try:
            prompt = f"""
            Based on successful product patterns and market opportunity, generate an optimal product strategy.

            Market Opportunity:
            {json.dumps(opportunity, indent=2)}

            Success Patterns:
            {json.dumps(patterns, indent=2)}

            Generate a strategy that includes:
            1. Product type recommendation
            2. Pricing strategy
            3. Content approach
            4. Marketing angle
            5. Risk assessment
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )

            strategy_text = response.choices[0].message.content

            # Parse strategy into structured format
            return {
                "strategy": strategy_text,
                "confidence": 0.85,
                "generated_at": datetime.now(timezone.utc),
                "based_on_patterns": len(patterns.get("patterns", []))
            }

        except Exception as e:
            return {
                "strategy": "Fallback strategy: Create comprehensive course with practical examples",
                "error": str(e),
                "confidence": 0.5
            }

    def _create_test_groups(self, variants: List[Dict[str, Any]]) -> Dict[str, List]:
        """Create A/B test groups"""
        groups = {}
        for i, variant in enumerate(variants):
            variant_id = variant.get("variant_id", f"variant_{i}")
            groups[variant_id] = {
                "variant": variant,
                "traffic_percentage": 100 / len(variants),
                "current_traffic": 0
            }
        return groups

    async def _get_variant_performance(self, variant_id: str, start_time: datetime) -> Dict[str, Any]:
        """Get performance metrics for a test variant"""
        # Placeholder - would query actual performance data
        return {
            "impressions": random.randint(100, 1000),
            "clicks": random.randint(10, 100),
            "conversions": random.randint(1, 20),
            "revenue": random.randint(50, 500)
        }

    def _calculate_variant_score(self, performance: Dict[str, Any]) -> float:
        """Calculate overall score for a variant"""
        revenue = performance.get("revenue", 0)
        conversions = performance.get("conversions", 0)
        clicks = performance.get("clicks", 0)

        # Weighted score
        return (revenue * 0.5) + (conversions * 0.3) + (clicks * 0.2)

    async def _learn_from_ab_test(self, results: Dict[str, Any]):
        """Learn from A/B test results"""
        learning_data = {
            "type": "ab_test_learning",
            "timestamp": datetime.now(timezone.utc),
            "results": results,
            "insights": "Winner identified and patterns stored"
        }

        await self.learning_collection.insert_one(learning_data)

    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate confidence in test results"""
        scores = [variant_data["score"] for variant_data in results.values()]
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        return min(1.0, (max_score - avg_score) / avg_score) if avg_score > 0 else 0.5

    async def _generate_test_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights from A/B test results"""
        insights = []

        # Find best performing variant
        best_variant = max(results.items(), key=lambda x: x[1]["score"])

        insights.append(f"Variant {best_variant[0]} performed best with score {best_variant[1]['score']:.2f}")

        # Analyze differences
        scores = [(vid, data["score"]) for vid, data in results.items()]
        scores.sort(key=lambda x: x[1], reverse=True)

        if len(scores) > 1:
            improvement = ((scores[0][1] - scores[1][1]) / scores[1][1]) * 100
            insights.append(f"Winner outperformed second best by {improvement:.1f}%")

        return insights

    async def _find_similar_products(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find products similar to the given features"""
        # Placeholder - would use similarity algorithms
        return await self.performance_collection.find().limit(10).to_list(length=None)

    async def _calculate_success_probability(self, features: Dict[str, Any], similar_products: List[Dict[str, Any]]) -> float:
        """Calculate success probability for a product"""
        if not similar_products:
            return 0.5

        # Simple average of similar products' success rates
        success_rates = []
        for product in similar_products:
            metrics = product.get("metrics", {})
            revenue = metrics.get("revenue", 0)
            # Consider successful if revenue > $10
            success_rates.append(1.0 if revenue > 10 else 0.0)

        return sum(success_rates) / len(success_rates) if success_rates else 0.5

    def _calculate_prediction_confidence(self, similar_products: List[Dict[str, Any]]) -> float:
        """Calculate confidence in prediction"""
        return min(1.0, len(similar_products) / 20)  # More similar products = higher confidence

    async def _generate_improvement_suggestions(self, features: Dict[str, Any], success_prob: float) -> List[str]:
        """Generate suggestions to improve product success"""
        suggestions = []

        if success_prob < 0.3:
            suggestions.extend([
                "Consider lowering price point to increase conversions",
                "Add more practical examples and case studies",
                "Improve product title for better click-through rates"
            ])
        elif success_prob < 0.7:
            suggestions.extend([
                "Product has moderate potential - consider A/B testing different titles",
                "Add bonus materials to increase perceived value",
                "Optimize product description for better SEO"
            ])
        else:
            suggestions.extend([
                "High success potential - focus on marketing and distribution",
                "Consider creating a product series or upsells",
                "Leverage social proof and testimonials"
            ])

        return suggestions

    def _find_common_categories(self, products: List[Dict[str, Any]]) -> List[str]:
        """Find most common categories in successful products"""
        categories = defaultdict(int)
        for product in products:
            category = product.get("metrics", {}).get("category", "unknown")
            categories[category] += 1

        return sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]

    def _analyze_content_length(self, products: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze content length patterns in successful products"""
        lengths = [len(product.get("metrics", {}).get("description", "")) for product in products]
        return {
            "average_length": sum(lengths) // len(lengths) if lengths else 0,
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0
        }

    def _analyze_timing_patterns(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze when products perform best"""
        # Placeholder - would analyze timestamps
        return {
            "best_day": "Wednesday",
            "best_hour": 14,
            "seasonal_trends": "Q4 performs best"
        }