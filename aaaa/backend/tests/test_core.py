"""
Integration tests for the core API endpoints.
Run with:  pytest tests/ -v
"""
import os
import sys
import pytest
import httpx

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token(base_url):
    """Sign up a disposable test user and return a JWT."""
    import time
    email = f"testuser_{int(time.time())}@test.local"
    password = "Test1234!@#"

    with httpx.Client(base_url=base_url, timeout=15) as c:
        # Try signup
        r = c.post("/api/auth/signup", json={"email": email, "password": password})
        if r.status_code in (200, 201):
            token = r.json().get("access_token") or r.json().get("token")
            if token:
                return token

        # Maybe user exists — try login
        r = c.post("/api/auth/login", json={"email": email, "password": password})
        if r.status_code == 200:
            return r.json().get("access_token") or r.json().get("token")

    pytest.skip("Could not obtain auth token — is the server running?")


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# ---------------------------------------------------------------------------
# Health & unauthenticated
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health(self, base_url):
        r = httpx.get(f"{base_url}/api/system/health", timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") in ("healthy", "ok", True)

    def test_docs(self, base_url):
        r = httpx.get(f"{base_url}/docs", timeout=10)
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class TestAuth:
    def test_login_bad_creds(self, base_url):
        r = httpx.post(
            f"{base_url}/api/auth/login",
            json={"email": "nobody@nowhere.fake", "password": "wrong"},
            timeout=10,
        )
        assert r.status_code in (401, 400, 404)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

class TestProducts:
    def test_list_products(self, base_url):
        r = httpx.get(f"{base_url}/api/products", timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, (list, dict))

    def test_generate_full_product(self, base_url, auth_headers):
        r = httpx.post(
            f"{base_url}/api/ai/generate-full-product",
            headers=auth_headers,
            json={
                "concept": "pytest smoke test product",
                "keywords": ["test", "automation"],
                "generate_image": False,
                "save_to_db": False,
            },
            timeout=60,
        )
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") == "success"
        assert body.get("product", {}).get("title")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboard:
    def test_dashboard_stats(self, base_url):
        r = httpx.get(f"{base_url}/api/dashboard/stats", timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "total_products" in body


# ---------------------------------------------------------------------------
# Gumroad (read-only — just verifies the endpoints exist)
# ---------------------------------------------------------------------------

class TestGumroad:
    def test_gumroad_products(self, base_url):
        r = httpx.get(f"{base_url}/api/gumroad/products", timeout=10)
        # 200 if token works, 400/500 if not — both are fine for a smoke test
        assert r.status_code in (200, 400, 500)

    def test_gumroad_sales(self, base_url):
        r = httpx.get(f"{base_url}/api/gumroad/sales", timeout=10)
        assert r.status_code in (200, 400, 500)


# ---------------------------------------------------------------------------
# Product cycle scheduler status
# ---------------------------------------------------------------------------

class TestScheduler:
    def test_scheduler_status(self, base_url, auth_headers):
        r = httpx.get(
            f"{base_url}/api/autonomous/status",
            headers=auth_headers,
            timeout=10,
        )
        # Endpoint may or may not exist — just check it doesn't 500
        assert r.status_code in (200, 404)


# ---------------------------------------------------------------------------
# QC Engine (unit-level, no network needed)
# ---------------------------------------------------------------------------

class TestQCEngine:
    def test_passing_product(self):
        from ai_services.product_quality_engine import ProductQualityEngine

        engine = ProductQualityEngine()
        product = {
            "id": "test-1",
            "title": "Master Your Morning Routine for Peak Productivity",
            "description": (
                "Transform your mornings and unlock peak performance with this step-by-step system. "
                "You will discover proven methods to build energy, focus, and momentum before 9 AM. "
                "This blueprint includes actionable checklists, a 30-day tracker, and specific "
                "habit-stacking techniques used by top performers. Whether you are a busy professional "
                "or a solopreneur, this guide gives you the complete framework to reclaim your mornings "
                "and achieve more in less time. Includes bonus templates and a quick-start planner."
            ),
            "product_type": "ebook",
            "price": 29.00,
            "chapters": ["Wake Up Protocol", "Energy Systems", "Focus Blocks",
                         "Habit Stacking", "Weekly Review", "Advanced Routines"],
            "pages": 45,
            "keywords": ["morning routine", "productivity", "habits", "focus", "time management"],
            "benefits": [
                "Build a rock-solid morning routine in 7 days",
                "Increase daily output by 30%+",
                "Eliminate decision fatigue with pre-built templates",
                "Track progress with the included 30-day journal",
            ],
            "target_audience": "Busy professionals and solopreneurs who want to start every day with energy and clarity",
            "image_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80",
        }
        report = engine.run(product)
        assert report.overall_score >= 80, f"Expected >=80, got {report.overall_score}"
        assert report.ready_for_sale

    def test_failing_product(self):
        from ai_services.product_quality_engine import ProductQualityEngine

        engine = ProductQualityEngine()
        product = {"id": "bad", "title": "ebook", "description": "short"}
        report = engine.run(product)
        assert report.overall_score < 80
        assert not report.ready_for_sale

    def test_rejects_known_boilerplate_description(self):
        from ai_services.product_quality_engine import ProductQualityEngine

        engine = ProductQualityEngine()
        product = {
            "id": "boilerplate-1",
            "title": "Korean Beauty Digital Lookbook Template Revenue System",
            "description": (
                "Korean Beauty Digital Lookbook Template Revenue System is built for founders, freelancers, and creators who want a cleaner path to revenue inside Korean beauty digital lookbook. "
                "It combines positioning guidance, concrete implementation steps, offer structure, and launch assets so buyers can move from idea to sellable offer without wasting weeks on scattered research. "
                "Instead of vague theory, this product focuses on execution, packaging, and conversion so it is ready to market and deliver immediately."
            ),
            "product_type": "template",
            "price": 39.0,
            "sections": ["Planning", "Execution", "Measurement"],
            "keywords": ["korean beauty", "lookbook", "template", "digital product", "brand assets"],
            "benefits": [
                "Launch a polished lookbook quickly",
                "Speed up product packaging",
                "Organize campaign visuals",
            ],
            "target_audience": "Beauty founders who want a premium digital lookbook workflow",
            "image_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80",
        }
        report = engine.run(product)
        assert not report.ready_for_sale
        assert any(check.name == "Uniqueness" and check.status.value == "fail" for check in report.checks)
