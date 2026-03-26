# CEO AI v4 - Complete Usage Examples

## 📚 Full Integration Examples

### Example 1: Dashboard Integration (React)

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api/v4';

function MyDashboard() {
  const [demoMode, setDemoMode] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch dashboard data
  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/dashboard/overview`);
      
      if (response.data.success) {
        setDashboard(response.data.data);
        setError(null);
      }
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  // Toggle demo mode
  const toggleDemoMode = async () => {
    try {
      await axios.post(
        `${API_URL}/demo-mode/toggle`,
        null,
        { params: { enable_demo: !demoMode } }
      );
      setDemoMode(!demoMode);
      fetchDashboard();
    } catch (err) {
      console.error('Failed to toggle demo mode:', err);
    }
  };

  // Run autonomous cycle
  const runCycle = async () => {
    try {
      setLoading(true);
      await axios.post(`${API_URL}/autonomous/run-cycle`);
      await new Promise(r => setTimeout(r, 2000));
      fetchDashboard();
    } catch (err) {
      console.error('Failed to run cycle:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="dashboard">
      <button onClick={toggleDemoMode}>
        {demoMode ? 'Demo Mode' : 'Production Mode'}
      </button>
      <button onClick={runCycle}>Run AI Cycle</button>

      <div className="stats">
        <div>Products: {dashboard?.stats?.total_products}</div>
        <div>Revenue: ${dashboard?.stats?.total_revenue}</div>
        <div>Opportunities: {dashboard?.stats?.opportunities_found}</div>
      </div>

      <div className="products">
        <h3>Recent Products</h3>
        {dashboard?.products?.map(product => (
          <div key={product.id}>
            <h4>{product.title}</h4>
            <p>${product.price}</p>
            <span>{product.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MyDashboard;
```

---

### Example 2: Backend Integration (FastAPI)

```python
from fastapi import FastAPI
from config.demo_config import demo_config
from config.demo_data import DemoData, DemoDataGenerator
import httpx

app = FastAPI()

@app.get("/my-endpoint")
async def my_endpoint():
    """Custom endpoint using demo data"""
    
    # Check if demo mode
    if demo_config.is_demo:
        # Use simulated data
        product = DemoData.generate_product()
        opportunities = [DemoData.generate_opportunity() for _ in range(5)]
        revenue = DemoData.generate_revenue_data(30)
        
        return {
            "mode": "demo",
            "product": product,
            "opportunities": opportunities,
            "revenue": revenue,
        }
    else:
        # Use real data from your APIs
        # Connect to databases, call real APIs
        return {
            "mode": "production",
            "data": "from_real_systems"
        }

@app.post("/run-my-workflow")
async def run_workflow():
    """Run a complete workflow"""
    
    from config.error_handler import ErrorResponse
    
    try:
        # Your business logic here
        products = [DemoData.generate_product() for _ in range(10)]
        revenue = sum(p.get('revenue', 0) for p in products)
        
        return ErrorResponse.format_success(
            data={
                "products_created": len(products),
                "total_revenue": revenue,
            },
            message="Workflow completed successfully"
        )
    except Exception as e:
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Workflow failed"
        )
```

---

### Example 3: Command Line Usage

```bash
#!/bin/bash

# Configuration
API="http://localhost:8000/api/v4"
AUTH_HEADER="Content-Type: application/json"

# ============================================================================
# Health Checks
# ============================================================================

health() {
  curl -s "$API/health" | jq '.data.status'
}

demo_status() {
  curl -s "$API/demo-mode/status" | jq '.data'
}

# ============================================================================
# Toggle Modes
# ============================================================================

enable_demo() {
  curl -s -X POST "$API/demo-mode/toggle?enable_demo=true" | jq
}

enable_production() {
  curl -s -X POST "$API/demo-mode/toggle?enable_demo=false" | jq
}

# ============================================================================
# Dashboard Operations
# ============================================================================

get_dashboard() {
  curl -s "$API/dashboard/overview" | jq '.data'
}

get_stats() {
  days=${1:-30}
  curl -s "$API/dashboard/stats?days=$days" | jq '.data'
}

# ============================================================================
# Product Operations
# ============================================================================

list_products() {
  limit=${1:-10}
  curl -s "$API/products?limit=$limit" | jq '.data.products'
}

create_product() {
  title=$1
  niche=${2:-"AI"}
  price=${3:-47.00}
  
  curl -s -X POST "$API/products/create" \
    -H "$AUTH_HEADER" \
    -d "{
      \"title\": \"$title\",
      \"niche\": \"$niche\",
      \"price\": $price
    }" | jq '.data'
}

# ============================================================================
# Analytics Operations
# ============================================================================

get_revenue() {
  days=${1:-30}
  curl -s "$API/analytics/revenue?days=$days" | jq '.data'
}

get_analytics() {
  curl -s "$API/analytics/full" | jq '.data'
}

# ============================================================================
# Marketing Operations
# ============================================================================

get_social_posts() {
  count=${1:-10}
  curl -s "$API/marketing/social-posts?count=$count" | jq '.data.posts'
}

generate_social_campaign() {
  niche=$1
  days=${2:-30}
  
  curl -s -X POST "$API/marketing/generate-social-campaign" \
    -H "$AUTH_HEADER" \
    -d "{
      \"niche\": \"$niche\",
      \"campaign_days\": $days
    }" | jq '.data'
}

get_emails() {
  count=${1:-5}
  curl -s "$API/marketing/email-sequences?count=$count" | jq '.data.sequences'
}

# ============================================================================
# Autonomous System Operations
# ============================================================================

run_cycle() {
  curl -s -X POST "$API/autonomous/run-cycle" \
    -H "$AUTH_HEADER" \
    -d '{
      "enable_publishing": true,
      "enable_marketing": true
    }' | jq '.data'
}

run_parallel() {
  projects=${1:-10}
  curl -s -X POST "$API/scaling/run-parallel?num_projects=$projects" \
    -H "$AUTH_HEADER" | jq '.data'
}

get_status() {
  curl -s "$API/autonomous/status" | jq '.data'
}

# ============================================================================
# Usage Examples
# ============================================================================

if [ $# -eq 0 ]; then
  echo "CEO AI v4 - CLI Usage"
  echo ""
  echo "Health: health"
  echo "Status: demo_status"
  echo "Toggle: enable_demo | enable_production"
  echo ""
  echo "Dashboard: get_dashboard | get_stats [days]"
  echo ""
  echo "Products: list_products [limit] | create_product <title> [niche] [price]"
  echo ""
  echo "Analytics: get_revenue [days] | get_analytics"
  echo ""
  echo "Marketing: get_social_posts [count]"
  echo "           generate_social_campaign <niche> [days]"
  echo "           get_emails [count]"
  echo ""
  echo "Cycles: run_cycle | run_parallel [projects] | get_status"
else
  $@
fi
```

Usage:
```bash
chmod +x ceo-cli.sh

# Health check
./ceo-cli.sh health

# Get dashboard
./ceo-cli.sh get_dashboard

# Create product
./ceo-cli.sh create_product "AI Product" "Automation" 67.00

# Generate social campaign
./ceo-cli.sh generate_social_campaign "Digital Marketing" 30

# Run cycles
./ceo-cli.sh run_cycle
./ceo-cli.sh run_parallel 25
```

---

### Example 4: Python Integration

```python
#!/usr/bin/env python3
"""
CEO AI v4 Python Integration
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime

class CEOAIClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_version: str = "v4"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/{api_version}"
        self.session = requests.Session()
    
    # ========================================================================
    # System Operations
    # ========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        response = self.session.get(f"{self.api_url}/health")
        return response.json()
    
    def toggle_demo_mode(self, enable: bool) -> Dict[str, Any]:
        """Toggle between demo and production mode"""
        response = self.session.post(
            f"{self.api_url}/demo-mode/toggle",
            params={"enable_demo": enable}
        )
        return response.json()
    
    def get_demo_status(self) -> Dict[str, Any]:
        """Get current demo mode status"""
        response = self.session.get(f"{self.api_url}/demo-mode/status")
        return response.json()
    
    # ========================================================================
    # Dashboard Operations
    # ========================================================================
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard overview"""
        response = self.session.get(f"{self.api_url}/dashboard/overview")
        return response.json()
    
    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get dashboard statistics"""
        response = self.session.get(
            f"{self.api_url}/dashboard/stats",
            params={"days": days}
        )
        return response.json()
    
    # ========================================================================
    # Product Operations
    # ========================================================================
    
    def list_products(self, limit: int = 10, status: str = None) -> Dict[str, Any]:
        """List products"""
        params = {"limit": limit}
        if status:
            params["status"] = status
        response = self.session.get(f"{self.api_url}/products", params=params)
        return response.json()
    
    def create_product(
        self,
        title: str,
        niche: str = None,
        product_type: str = "ebook",
        price: float = 27.0
    ) -> Dict[str, Any]:
        """Create a new product"""
        response = self.session.post(
            f"{self.api_url}/products/create",
            params={
                "title": title,
                "niche": niche,
                "product_type": product_type,
                "price": price
            }
        )
        return response.json()
    
    # ========================================================================
    # Analytics Operations
    # ========================================================================
    
    def get_revenue(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue analytics"""
        response = self.session.get(
            f"{self.api_url}/analytics/revenue",
            params={"days": days}
        )
        return response.json()
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get full analytics"""
        response = self.session.get(f"{self.api_url}/analytics/full")
        return response.json()
    
    # ========================================================================
    # Marketing Operations
    # ========================================================================
    
    def get_social_posts(self, count: int = 10) -> Dict[str, Any]:
        """Get social media posts"""
        response = self.session.get(
            f"{self.api_url}/marketing/social-posts",
            params={"count": count}
        )
        return response.json()
    
    def generate_social_campaign(
        self,
        niche: str,
        campaign_days: int = 30
    ) -> Dict[str, Any]:
        """Generate social media campaign"""
        response = self.session.post(
            f"{self.api_url}/marketing/generate-social-campaign",
            params={
                "niche": niche,
                "campaign_days": campaign_days
            }
        )
        return response.json()
    
    def get_email_sequences(self, count: int = 5) -> Dict[str, Any]:
        """Get email sequences"""
        response = self.session.get(
            f"{self.api_url}/marketing/email-sequences",
            params={"count": count}
        )
        return response.json()
    
    # ========================================================================
    # Autonomous Operations
    # ========================================================================
    
    def run_cycle(self, enable_publishing: bool = True) -> Dict[str, Any]:
        """Run autonomous cycle"""
        response = self.session.post(
            f"{self.api_url}/autonomous/run-cycle",
            params={
                "enable_publishing": enable_publishing,
                "enable_marketing": True
            }
        )
        return response.json()
    
    def run_parallel(self, num_projects: int = 10) -> Dict[str, Any]:
        """Run parallel cycles"""
        response = self.session.post(
            f"{self.api_url}/scaling/run-parallel",
            params={"num_projects": num_projects}
        )
        return response.json()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get autonomous system status"""
        response = self.session.get(f"{self.api_url}/autonomous/status")
        return response.json()


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    # Initialize client
    client = CEOAIClient()
    
    # 1. Health check
    print("1. Health Check")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # 2. Get dashboard
    print("\n2. Dashboard Overview")
    dashboard = client.get_dashboard()
    print(f"Total products: {dashboard['data']['stats']['total_products']}")
    print(f"Total revenue: ${dashboard['data']['stats']['total_revenue']}")
    
    # 3. Create product
    print("\n3. Create Product")
    product = client.create_product(
        title="My Awesome Product",
        niche="AI & Automation",
        price=97.00
    )
    print(f"Created: {product['data']['title']}")
    
    # 4. Get revenue
    print("\n4. Revenue Analytics")
    revenue = client.get_revenue(30)
    print(f"Total revenue (30d): ${revenue['data']['total_revenue']}")
    
    # 5. Generate campaign
    print("\n5. Generate Social Campaign")
    campaign = client.generate_social_campaign(
        niche="Digital Marketing",
        campaign_days=30
    )
    print(f"Campaign ID: {campaign['data']['campaign_id']}")
    print(f"Total posts: {campaign['data']['total_posts']}")
    
    # 6. Run cycle
    print("\n6. Run Autonomous Cycle")
    cycle = client.run_cycle()
    print(f"Products created: {cycle['data']['products_created']}")
    print(f"Revenue potential: ${cycle['data']['revenue_potential']}")
    
    # 7. Run parallel
    print("\n7. Run Parallel Cycles (25 projects)")
    parallel = client.run_parallel(25)
    print(f"Total products created: {parallel['data']['total_products_created']}")
    print(f"Total revenue potential: ${parallel['data']['total_revenue_potential']}")
```

Usage:
```bash
python ceo_client.py

# Output shows all operations working with demo data
```

---

### Example 5: Error Handling

```python
from config.error_handler import ErrorResponse, ErrorHandler, logger

# Format success response
success_response = ErrorResponse.format_success(
    data={"products": 10, "revenue": 5000},
    message="Data retrieved successfully",
    metadata={"cached": False}
)

# Format error response
error_response = ErrorResponse.format_error(
    ValueError("Invalid input"),
    status_code=400,
    message="Validation failed"
)

# Use in endpoint
@router.get("/my-endpoint")
@ErrorHandler.handle_endpoint
async def my_endpoint():
    # Automatically catches errors and returns consistent format
    products = await fetch_products()
    return products

# Manual logging
logger.info("Product created", product_id="prod_123", revenue=47.00)
logger.error("API call failed", error=exception, endpoint="/api/products")
```

---

### Example 6: Data Generation

```python
from config.demo_data import DemoData, DemoDataGenerator

# Generate individual items
product = DemoData.generate_product("ebook")
opportunity = DemoData.generate_opportunity()
revenue = DemoData.generate_revenue_data(30)
posts = DemoData.generate_social_posts(20)
emails = DemoData.generate_email_sequence()
analytics = DemoData.generate_analytics()

# Generate complete snapshot (async)
async def get_demo_data():
    snapshot = await DemoDataGenerator.generate_dashboard_snapshot()
    return snapshot

# All data is realistic
print(product['title'])  # "Ultimate AI Productivity Bundle - Digital Marketing"
print(product['price'])   # 67.00
print(product['sales'])   # 42
print(product['revenue']) # 2814.00
```

---

## 🎯 Next: Choose Your Integration

1. **React Dashboard**: Use `App_v4_production.js`
2. **FastAPI Endpoints**: Use `routes_v4_production.py`
3. **Command Line**: Use provided bash scripts
4. **Python Client**: Use `CEOAIClient` class
5. **Direct HTTP**: Use cURL examples

All support demo mode instantly! 🚀
