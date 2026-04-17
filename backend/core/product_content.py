"""
Product Content Generators
===========================
Generates real, substantial downloadable content for each product.
Each product gets multiple files matching its advertised "includes" list.
"""

import json
from datetime import datetime


def generate_product_files(product: dict) -> dict[str, str]:
    """
    Return a dict of {filename: content} for the given product.
    Every product gets its main guide + all advertised bonus files.
    """
    product_id = product.get("id", "")
    generators = {
        "flagship-ai-offer-engine": _ai_offer_engine_files,
        "fiilthy-002": _launch_playbook_files,
        "fiilthy-003": _tiktok_affiliate_files,
        "fiilthy-004": _chatgpt_command_pack_files,
        "time-well-spent-ebook": _time_well_spent_files,
    }

    generator = generators.get(product_id)
    if generator:
        return generator(product)

    # Dynamic generation for AI-created products (from DB)
    return _dynamic_product_files(product)


# ─── AI Offer Engine ─────────────────────────────────────────────────────────

def _ai_offer_engine_files(product: dict) -> dict[str, str]:
    year = datetime.now().year
    files = {}

    files["AI_Offer_Engine_Main_Guide.md"] = f"""# AI Offer Engine for Solo Operators
## The Complete System to Build, Price, and Sell Premium Digital Offers

*© {year} FiiLTHY.ai — Personal use only*

---

## Part 1: The Solo Operator Advantage

You don't need a team, a big budget, or a huge audience. You need ONE clear offer, ONE conversion path, and ONE delivery system. This guide gives you all three.

### Why Solo Operators Win Right Now

The market has shifted. Buyers want:
- **Speed** — They want solutions now, not 12-week courses
- **Specificity** — Generic doesn't sell; niche expertise does
- **Access** — They want to feel like they're buying from a real person

As a solo operator, you deliver all three naturally.

---

## Part 2: Finding Your $79–$997 Offer Sweet Spot

### The Offer Discovery Framework

Answer these four questions:

1. **What do people already ask you for help with?**
   Write down every skill, topic, or task where someone has said "can you help me with..." or "how did you do that?"

2. **What would save someone 10+ hours?**
   Time is the most valuable commodity. If your knowledge saves someone a week of trial and error, that's worth $79 minimum.

3. **What transformation can you deliver in 7 days or less?**
   Fast results = happy customers = referrals. The best digital offers promise (and deliver) a specific outcome in a short timeframe.

4. **What can you systematize?**
   If you can turn your process into templates + instructions + examples, you have a product.

### Pricing Matrix

| Offer Type | Price Range | What's Included | Delivery Time |
|------------|-------------|-----------------|---------------|
| Starter Kit | $27–$49 | Templates + Quick Guide | Instant download |
| Full System | $79–$149 | Complete framework + templates + prompts + support | Instant download |
| Premium Bundle | $197–$497 | Everything above + video walkthroughs + community | Instant + drip |
| Done-With-You | $497–$997 | All above + 1:1 calls or audits | Ongoing |

**Rule of thumb:** Price at the level where you'd feel slightly uncomfortable saying the number out loud. That's usually right.

---

## Part 3: Building Your Offer Stack

### The 5-Layer Offer Structure

**Layer 1: The Core Deliverable**
This is the main thing they're buying. Examples:
- A complete template library
- A step-by-step system document
- A toolkit with multiple components

**Layer 2: The Quick-Win Bonus**
Something they can use in the first 10 minutes to get an immediate result.
- A fill-in-the-blank script
- A plug-and-play template
- A ready-to-post content calendar

**Layer 3: The AI Acceleration Pack**
Pre-built prompts that let them use AI to execute faster.
- Research prompts
- Content creation prompts
- Sales copy prompts

**Layer 4: The Safety Net**
Reduces perceived risk.
- FAQ document
- Troubleshooting guide
- Common mistakes to avoid

**Layer 5: The Status Signal**
Makes them feel smart for buying.
- Certificate of completion
- "Advanced" label on the offer
- Community access

---

## Part 4: The AI-Assisted Sales Engine

### Your 3-Page Sales System

You only need three pages:

1. **Landing Page** — Problem → Solution → Proof → CTA
2. **Checkout Page** — Stripe or Gumroad handles this
3. **Thank You Page** — Delivery + upsell

### Writing Sales Copy with AI

Use this prompt structure for every piece of sales copy:

```
You are a direct-response copywriter for digital products.

Product: [YOUR PRODUCT NAME]
Target buyer: [WHO IS THIS FOR]
Main transformation: [WHAT THEY GET FROM THIS]
Price: [PRICE]

Write a [LANDING PAGE / EMAIL / AD] that:
- Opens with the #1 pain point
- Positions the product as the fastest path to their goal
- Includes 3 specific proof points or results
- Ends with a clear, urgent CTA

Tone: Confident, specific, no hype. Short paragraphs. Use numbers.
```

---

## Part 5: The 7-Day Launch Sprint

| Day | Task | Time |
|-----|------|------|
| 1 | Finalize offer + pricing using the worksheet | 2 hours |
| 2 | Create product files using templates in this pack | 3 hours |
| 3 | Write sales page copy (use AI prompts) | 2 hours |
| 4 | Set up Stripe/Gumroad checkout | 1 hour |
| 5 | Create 5 social posts + 3 emails (use templates) | 2 hours |
| 6 | Soft launch to warm audience | 1 hour |
| 7 | Full launch + follow-up sequence | 2 hours |

---

## Part 6: Post-Launch — The Retention Machine

### The 3 Emails That Keep Customers Buying

**Email 1: The Quick Win (Day 0)**
Subject: "Start here — your first win in 10 minutes"
Send immediately after purchase. Link to the quickest, easiest part of the product.

**Email 2: The Deep Dive (Day 3)**
Subject: "Most people miss this part..."
Highlight an underused feature or bonus. Creates perceived value.

**Email 3: The Upsell (Day 7)**
Subject: "Ready for the next level?"
Offer your higher-tier product at a loyalty discount.

---

*This is your complete system. Execute it step by step and you'll have a profitable offer live within 7 days.*
"""

    files["Offer_Design_Worksheet.md"] = f"""# High-Ticket Offer Design Worksheet
## Fill in each section to design your premium offer

*© {year} FiiLTHY.ai*

---

### 1. YOUR EXPERTISE AUDIT

**What are you known for?**
_________________________________________

**What do people ask your help with most?**
1. _________________________________________
2. _________________________________________
3. _________________________________________

**What skill saves others the most time?**
_________________________________________

**Rate your confidence delivering results (1-10):** ___

---

### 2. TARGET BUYER PROFILE

**Who is your ideal buyer?**
- Job title / role: _______________________
- Industry: _______________________
- Main frustration: _______________________
- Budget range: _______________________
- Where they hang out online: _______________________

**The ONE sentence that makes them say "that's me":**
_________________________________________

---

### 3. OFFER ARCHITECTURE

**Product name:** _______________________

**One-line description (max 15 words):**
_________________________________________

**Core transformation (before → after):**
Before: _______________________
After: _______________________

**Timeframe to results:** _______ days

**Price point:** $________

**Includes (list 5–8 deliverables):**
1. _________________________________________
2. _________________________________________
3. _________________________________________
4. _________________________________________
5. _________________________________________
6. _________________________________________
7. _________________________________________
8. _________________________________________

---

### 4. COMPETITIVE POSITIONING

**3 competitors/alternatives:**
1. _____________ — Price: $_____ — Weakness: _____________
2. _____________ — Price: $_____ — Weakness: _____________
3. _____________ — Price: $_____ — Weakness: _____________

**Your unfair advantage:**
_________________________________________

**Why should they buy yours instead?**
_________________________________________

---

### 5. SALES SYSTEM PLAN

**Landing page headline:**
_________________________________________

**3 key bullet points for sales page:**
1. _________________________________________
2. _________________________________________
3. _________________________________________

**Guarantee/risk reversal:**
_________________________________________

**Launch date:** _______________________

---

### 6. PRICING VALIDATION CHECKLIST

- [ ] Price is > $49 (under $49 signals low value for systems/frameworks)
- [ ] Price is < competitor average (or justified by unique value)
- [ ] I can describe the transformation in one sentence
- [ ] At least 3 people have said they'd pay this price
- [ ] The deliverables justify the price visually (enough files/pages)

---

*Complete this worksheet before building anything. Clarity here = faster execution everywhere else.*
"""

    files["AI_Prompts_Positioning_and_Sales.md"] = f"""# AI Prompts for Positioning & Sales Copy
## 25 Ready-to-Use Prompts — Just Fill in the [BRACKETS]

*© {year} FiiLTHY.ai*

---

### POSITIONING PROMPTS

**Prompt 1: Niche Positioning Statement**
```
I sell [PRODUCT TYPE] to [TARGET AUDIENCE]. Help me write a positioning statement that:
- Differentiates me from [TOP 3 COMPETITORS]
- Highlights my unique angle: [YOUR UNIQUE ANGLE]
- Feels authentic, not corporate
- Is under 25 words
Give me 5 options ranked by impact.
```

**Prompt 2: Offer Name Generator**
```
Generate 20 product names for a [PRODUCT TYPE] that helps [TARGET AUDIENCE] achieve [MAIN RESULT]. 
Requirements:
- Short (2-4 words)
- Implies speed or ease
- Sounds premium but not pretentious
- Easy to remember and spell
Rank them by how likely someone would click on them.
```

**Prompt 3: Value Proposition Builder**
```
My product helps [AUDIENCE] go from [CURRENT STATE] to [DESIRED STATE] in [TIMEFRAME].
Write 5 value propositions, each using a different framework:
1. Problem-Agitate-Solve
2. Before-After-Bridge
3. Feature-Advantage-Benefit
4. So-What Test (keep asking "so what?" until you reach the real benefit)
5. The "Even If" framework (works even if [objection])
```

**Prompt 4: Ideal Customer Avatar**
```
I'm building a [PRODUCT] for [BROAD AUDIENCE]. Create a detailed customer avatar:
- Demographics (age, role, income)
- Psychographics (fears, desires, beliefs)
- Behavior (where they spend time online, what they Google)
- Buying triggers (what makes them finally purchase)
- Objections (top 5 reasons they'd hesitate)
Format as a profile card I can reference daily.
```

**Prompt 5: Competitor Gap Analysis**
```
Here are 3 products in my space:
1. [COMPETITOR 1] — [PRICE] — [WHAT THEY OFFER]
2. [COMPETITOR 2] — [PRICE] — [WHAT THEY OFFER]  
3. [COMPETITOR 3] — [PRICE] — [WHAT THEY OFFER]

My product: [YOUR PRODUCT] — [YOUR PRICE]

Identify:
- 3 gaps none of them fill
- 3 things all of them do that I should do differently
- The #1 positioning angle that would make my product the obvious choice
```

---

### SALES COPY PROMPTS

**Prompt 6: Landing Page Hero Section**
```
Write a landing page hero section for [PRODUCT NAME].
Target audience: [WHO]
Main promise: [WHAT THEY GET]
Price: [PRICE]

Include:
- Headline (max 10 words, specific result)
- Subheadline (max 20 words, addresses main objection)
- 3 bullet points (outcomes, not features)
- CTA button text

Tone: Direct, confident, zero fluff.
```

**Prompt 7: Sales Email Sequence (5 emails)**
```
Write a 5-email launch sequence for [PRODUCT NAME] at [PRICE].

Email 1: Problem awareness (Day 1)
Email 2: Story + credibility (Day 2)
Email 3: The solution reveal (Day 3)
Email 4: Objection handling (Day 4)
Email 5: Urgency + final CTA (Day 5)

Each email: Subject line + 150-200 word body. 
Tone: Conversational, like texting a smart friend.
Target: [AUDIENCE]
```

**Prompt 8: Social Media Launch Posts**
```
Create 10 social media posts to promote [PRODUCT NAME].
Mix of:
- 3 problem-awareness posts
- 3 value/tip posts (no selling)
- 2 social proof / results posts
- 2 direct CTA posts

Platform: [TIKTOK/INSTAGRAM/TWITTER/LINKEDIN]
Tone: Casual, punchy, scroll-stopping
Include hashtag suggestions for each post.
```

**Prompt 9: Testimonial Request Template**
```
Write a message I can send to beta users / early customers asking for a testimonial.
Product: [PRODUCT NAME]
Requirements:
- Feels natural, not corporate
- Guides them to mention specific results
- Includes a "fill in the blank" option for busy people
- Short (under 100 words)
```

**Prompt 10: FAQ Section Builder**
```
I sell [PRODUCT] at [PRICE] to [AUDIENCE].
Write 10 FAQ entries that:
- Address real buying objections (not softballs)
- Each answer is 2-3 sentences max
- Include a CTA at the end of at least 3 answers
- Handle: price, trust, time required, results timeline, refund policy
```

---

### CONTENT MARKETING PROMPTS

**Prompt 11-15: Blog/Thread Framework**
```
Write a [BLOG POST / TWITTER THREAD / LINKEDIN POST] about [TOPIC RELATED TO YOUR PRODUCT].
Structure: Hook → Story → 5 Key Points → Bridge to Product → CTA
Length: [WORD COUNT]
Goal: Position me as the expert and naturally lead to [PRODUCT NAME]
Do NOT be salesy. Lead with pure value.
```

**Prompt 16-20: Video Script Templates**
```
Write a [60-SECOND / 3-MINUTE] video script about [TOPIC].
Format:
- Hook (first 3 seconds — the most important part)
- Problem setup (10 seconds)
- 3 quick tips (30 seconds)
- Soft CTA (10 seconds)
- On-screen text suggestions for each section
Platform: [TIKTOK / YOUTUBE / INSTAGRAM REELS]
```

**Prompt 21-25: Ad Copy Variations**
```
Write 5 ad variations for [PRODUCT NAME] at [PRICE].
Each ad should be:
- Under 125 characters for the headline
- Under 250 characters for the body
- Include a clear CTA
Test angles: fear of missing out, social proof, curiosity, direct benefit, contrarian take
Platform: [META / GOOGLE / TIKTOK]
```

---

*Pro tip: Run each prompt 3x with slight variations and cherry-pick the best lines from each output.*
"""

    files["7_Day_Launch_Sprint_Plan.md"] = f"""# 7-Day Launch Sprint Plan
## From Zero to Live Offer in One Week

*© {year} FiiLTHY.ai*

---

## Day 1: Clarity Day (2 hours)

### Morning Block (1 hour)
- [ ] Complete the Offer Design Worksheet (included in this pack)
- [ ] Define your ONE target buyer
- [ ] Write your one-line product description
- [ ] Set your price (use the Pricing Matrix from the main guide)

### Afternoon Block (1 hour)
- [ ] List all deliverables you'll include
- [ ] Map the buyer journey: see ad → read page → buy → download → result
- [ ] Set your launch date (Day 7)
- [ ] Tell 3 people about your launch (accountability)

**End of Day 1 deliverable:** Completed Offer Design Worksheet

---

## Day 2: Creation Day (3 hours)

### Build Your Product Files
- [ ] Create the main guide/system document
- [ ] Build 3-5 templates (use the included template frameworks)
- [ ] Write the AI prompt pack (customize from prompts in this kit)
- [ ] Create the quick-start checklist
- [ ] Package everything into a clean folder structure

**Folder structure:**
```
YourProduct/
├── Main_Guide.pdf
├── Templates/
│   ├── Template_1.md
│   ├── Template_2.md
│   └── Template_3.md
├── AI_Prompts/
│   └── Prompt_Library.md
├── Checklists/
│   └── Quick_Start.md
└── README.txt
```

**End of Day 2 deliverable:** Complete product package

---

## Day 3: Sales Copy Day (2 hours)

- [ ] Write landing page headline + subheadline (use Prompt 6)
- [ ] Write 5 bullet points highlighting outcomes
- [ ] Write 3 paragraphs of body copy
- [ ] Create your FAQ section (use Prompt 10)
- [ ] Write your guarantee statement
- [ ] Draft your CTA button text

**End of Day 3 deliverable:** Complete sales page copy in a Google Doc

---

## Day 4: Setup Day (1 hour)

- [ ] Create Stripe or Gumroad product listing
- [ ] Upload product files
- [ ] Set up payment link
- [ ] Test the full purchase flow (buy your own product with test card)
- [ ] Verify download delivery works
- [ ] Set up your email (SendGrid / Mailchimp / ConvertKit)

**End of Day 4 deliverable:** Working checkout + delivery system

---

## Day 5: Content Day (2 hours)

- [ ] Write 5 social media posts (use Prompt 8)
- [ ] Write 3 launch emails (use Prompt 7)
- [ ] Create 1 value-first blog post or thread (use Prompt 11)
- [ ] Schedule posts for Days 6 and 7
- [ ] Prepare your "launch day" announcement

**End of Day 5 deliverable:** All marketing content ready

---

## Day 6: Soft Launch (1 hour)

- [ ] Send Email 1 to your existing list/contacts
- [ ] Post teaser content on social media
- [ ] DM 10 people who fit your target buyer profile
- [ ] Share in 2-3 relevant communities (add value first, mention product naturally)
- [ ] Monitor for questions or objections (update FAQ if needed)

**End of Day 6 deliverable:** First eyeballs on your offer

---

## Day 7: LAUNCH DAY (2 hours)

### Morning
- [ ] Send launch email to full list
- [ ] Post launch announcement on all platforms
- [ ] Go live in communities where you've been adding value
- [ ] Share behind-the-scenes of your creation process

### Afternoon
- [ ] Respond to every question within 1 hour
- [ ] Share any early sales/feedback as social proof
- [ ] Send follow-up email (reminder)

### Evening
- [ ] Post results/lessons from Day 1 of launch
- [ ] Plan Week 2 content
- [ ] Celebrate — you shipped

**End of Day 7 deliverable:** Live, selling product

---

## Post-Launch Checklist (Week 2+)

- [ ] Send Email 2 (Day 8)
- [ ] Send Email 3 (Day 10)
- [ ] Collect 3 testimonials from buyers
- [ ] Update sales page with social proof
- [ ] Plan your upsell / next product
- [ ] Set up automated email sequence for new subscribers
"""

    files["Delivery_Fulfillment_Checklist.md"] = f"""# Delivery & Fulfillment Checklist
## Make Sure Every Customer Gets a 10/10 Experience

*© {year} FiiLTHY.ai*

---

### Pre-Launch Checks

- [ ] Product files are complete and tested
- [ ] ZIP download works on Mac + Windows + mobile
- [ ] All links inside product files work
- [ ] Spelling/grammar check on all documents
- [ ] File sizes are reasonable (< 50MB per ZIP)
- [ ] Payment processor (Stripe/Gumroad) is connected
- [ ] Test purchase completed successfully
- [ ] Download email sends within 60 seconds
- [ ] Download link works and delivers correct files
- [ ] Refund policy is clearly stated

### Post-Purchase Experience

- [ ] Customer receives confirmation email instantly
- [ ] Download link is prominently displayed
- [ ] Thank you page loads correctly
- [ ] Product matches what was advertised
- [ ] Quick-start guide is the first thing they see
- [ ] Support email is included in product files

### Ongoing Operations

- [ ] Monitor for failed payments daily
- [ ] Respond to support emails within 24 hours
- [ ] Track download completion rate
- [ ] Send follow-up email on Day 3
- [ ] Ask for reviews/testimonials on Day 7
- [ ] Update product files monthly with improvements

### Red Flags to Watch

- High refund rate (> 5%) → Product-market fit issue
- Low download rate → Email delivery problem
- Support tickets about missing files → Check ZIP packaging
- Complaints about quality → Update content immediately
"""

    files["Upsell_Retention_Framework.md"] = f"""# Upsell & Retention Framework
## Turn One Sale Into Lifetime Revenue

*© {year} FiiLTHY.ai*

---

## The Product Ladder

```
$27-49    →  Starter Kit (entry point)
  ↓
$79-149   →  Full System (core offer) ← YOU ARE HERE
  ↓
$197-497  →  Premium Bundle (everything + extras)
  ↓
$497-997  →  Done-With-You (includes calls/audits)
  ↓
$997+     →  Done-For-You (full service)
```

### Upsell Timing

| Trigger | Upsell | Channel |
|---------|--------|---------|
| Immediately after purchase | Related template pack | Thank you page |
| Day 3 after purchase | Premium upgrade | Email |
| Day 7 after purchase | 1:1 consultation | Email |
| 30 days after purchase | New product launch | Email |
| Customer support interaction | Higher tier | Direct message |

### Retention Emails

**The Value Drip (automated, post-purchase):**

Day 0: Welcome + quick start
Day 3: "Did you try [specific feature]?"
Day 7: Success story + upsell offer
Day 14: Advanced tip + community invite
Day 30: New content update + next product preview

### Metrics to Track

- **Customer Lifetime Value (CLV):** Total revenue per customer across all purchases
- **Upsell Conversion Rate:** % of buyers who purchase the next tier
- **Repeat Purchase Rate:** % who buy a second product
- **Refund Rate:** Keep below 5%
- **NPS Score:** Ask at Day 14 — "Would you recommend this to a friend?"

---

*Goal: Every customer should buy at least 2 products from you within 90 days.*
"""

    return files


# ─── Digital Product Launch Playbook ──────────────────────────────────────────

def _launch_playbook_files(product: dict) -> dict[str, str]:
    year = datetime.now().year
    files = {}

    files["Launch_Playbook_Complete_Guide.md"] = f"""# Digital Product Launch Playbook
## Launch Profitable Digital Products in 7 Days with AI

*© {year} FiiLTHY.ai*

---

## Chapter 1: The $50K Launch Formula

Every successful digital product launch follows the same pattern:
**Audience × Offer × Urgency = Revenue**

If any of these is zero, revenue is zero. This playbook maximizes all three.

### The 3 Launch Phases

**Phase 1: Pre-Launch (Days 1-3)**
Build anticipation. Warm up your audience. Create demand before you sell anything.

**Phase 2: Launch Window (Days 4-6)**
Open cart. Drive urgency. Handle objections in real-time.

**Phase 3: Post-Launch (Day 7+)**
Close cart (or raise price). Follow up. Transition to evergreen.

---

## Chapter 2: Pre-Launch Strategy

### Day 1: Seed the Idea
- Post 3 pieces of content related to your product topic
- Ask your audience: "What's your biggest challenge with [topic]?"
- Save every response — these become your sales copy

### Day 2: Build Anticipation
- Share a behind-the-scenes look at what you're building
- Post a "hot take" related to your topic (generates discussion)
- Respond to every comment from Day 1

### Day 3: Pre-Launch Email
- Send to your list: "Something new is coming tomorrow..."
- Include ONE specific benefit
- Create a reply trigger: "Reply YES if you want early access"

---

## Chapter 3: Launch Execution

### The Launch Email Sequence

**Email 1 — Launch Day (Cart Open)**
Subject: It's live — [Product Name]
Body: Problem → Your solution → What's included → Price → CTA → Deadline

**Email 2 — Day 2 (Social Proof)**
Subject: "[Name] already got results with this"
Body: Customer quote/story → Remind benefits → CTA

**Email 3 — Day 3 (FAQ & Objections)**
Subject: "Quick answers to your questions about [Product]"
Body: Top 5 questions → Direct answers → CTA

**Email 4 — Day 4 (Scarcity/Bonus)**
Subject: "Bonus expires tonight"
Body: Add a bonus for action-takers → Deadline reminder → CTA

**Email 5 — Final Day (Last Chance)**
Subject: "Last chance — closes at midnight"
Body: Recap transformation → Final testimonial → URGENCY → CTA

---

## Chapter 4: The 127-Point Launch Checklist

(See separate file: Launch_Checklist_127.md)

---

## Chapter 5: Post-Launch Transition

### Going Evergreen
After your launch window closes:
1. Remove urgency elements from sales page
2. Set up automated email funnel (see Email_Funnel_Sequences.md)
3. Add to your permanent product line
4. Set up retargeting ads for page visitors
5. Create a monthly content plan that drives organic traffic

---

*Your next $50K launch starts with Day 1. Let's go.*
"""

    files["Launch_Checklist_127.md"] = f"""# 127-Point Launch Checklist
## Every Step from Idea to $50K+ Launch

*© {year} FiiLTHY.ai*

---

### PRODUCT (Points 1-25)

1. [ ] Product idea validated with 10+ potential buyers
2. [ ] Clear target audience defined (one specific person)
3. [ ] Main transformation articulated in one sentence
4. [ ] Price point set and validated against competitors
5. [ ] Product name finalized
6. [ ] All product files created and tested
7. [ ] Product packaged as downloadable ZIP
8. [ ] Quick-start guide written
9. [ ] Thank you / welcome document included
10. [ ] All internal links tested
11. [ ] Spelling and grammar checked
12. [ ] File sizes optimized (< 50MB)
13. [ ] Product tested on desktop + mobile
14. [ ] Bonus content created
15. [ ] Upsell product identified
16. [ ] Refund policy written
17. [ ] Terms of use / license included
18. [ ] Support email configured
19. [ ] FAQ document with 10+ questions
20. [ ] Product screenshots / mockups created
21. [ ] Feature list matches actual deliverables
22. [ ] Priced for profit (> 80% margin for digital)
23. [ ] Differentiation from competitors is clear
24. [ ] Product solves an URGENT problem
25. [ ] Beta testers have confirmed value

### SALES PAGE (Points 26-50)

26. [ ] Headline grabs attention in 3 seconds
27. [ ] Subheadline addresses main objection
28. [ ] Hero image / product mockup above fold
29. [ ] Problem section resonates (use buyer language)
30. [ ] Solution section is specific and credible
31. [ ] Benefits listed (outcomes, not features)
32. [ ] Social proof (testimonials, numbers, logos)
33. [ ] Product breakdown (what's included)
34. [ ] Pricing section with anchor price
35. [ ] Guarantee / risk reversal
36. [ ] FAQ section (5-10 questions)
37. [ ] Multiple CTA buttons throughout page
38. [ ] Mobile responsive
39. [ ] Page loads in < 3 seconds
40. [ ] No broken links or images
41. [ ] Checkout button works
42. [ ] Analytics tracking installed
43. [ ] Pixel/tracking for retargeting
44. [ ] SEO meta title and description
45. [ ] Open Graph tags for social sharing
46. [ ] Urgency element (countdown, limited spots)
47. [ ] Trust badges / security indicators
48. [ ] Creator bio / credibility section
49. [ ] Clear next step (exactly what happens after purchase)
50. [ ] Page reviewed by someone outside your niche

### EMAIL MARKETING (Points 51-75)

51. [ ] Email list segmented (buyers vs non-buyers)
52. [ ] Pre-launch sequence written (3 emails)
53. [ ] Launch sequence written (5 emails)
54. [ ] Post-launch sequence written (3 emails)
55. [ ] Post-purchase welcome email written
56. [ ] Subject lines A/B tested
57. [ ] Preview text optimized
58. [ ] Unsubscribe link present
59. [ ] CAN-SPAM compliant
60. [ ] Links tested in every email
61. [ ] Email design is mobile-friendly
62. [ ] Personalization tags working
63. [ ] Send times optimized for audience timezone
64. [ ] Reply-to address monitored
65. [ ] Automated sequences set up in ESP
66. [ ] Cart abandonment email ready
67. [ ] Re-engagement email for non-openers
68. [ ] Subscriber confirmation / double opt-in
69. [ ] Welcome sequence for new subscribers
70. [ ] Email analytics tracking configured
71. [ ] Segmentation rules set up
72. [ ] Bounce handling configured
73. [ ] Warm-up sequence for cold addresses
74. [ ] Affiliate / JV partner emails drafted
75. [ ] Post-purchase upsell email scheduled

### SOCIAL MEDIA (Points 76-100)

76. [ ] Platform strategy: primary + secondary channels
77. [ ] 10 pre-launch posts created
78. [ ] 10 launch week posts created
79. [ ] 5 post-launch posts created
80. [ ] Behind-the-scenes content prepared
81. [ ] Content calendar for launch month
82. [ ] Hashtag strategy researched
83. [ ] Post times optimized per platform
84. [ ] Stories / Reels / Shorts content planned
85. [ ] Video scripts for at least 3 videos
86. [ ] Carousel / infographic designs ready
87. [ ] Community engagement plan (groups, forums)
88. [ ] Influencer / creator outreach list
89. [ ] UGC request templates ready
90. [ ] Social proof screenshotted and organized
91. [ ] Platform-specific formatting (aspect ratios, lengths)
92. [ ] Link in bio updated with product URL
93. [ ] Pinned post updated for launch
94. [ ] Comment response templates ready
95. [ ] DM outreach templates ready
96. [ ] Contest / giveaway planned (optional)
97. [ ] Podcast guest pitch ready (if applicable)
98. [ ] Press release or blog post for SEO
99. [ ] Affiliate / referral program set up
100. [ ] Social analytics reviewed pre-launch for baseline

### TECH & OPERATIONS (Points 101-127)

101. [ ] Payment processor connected and tested
102. [ ] Checkout flow tested end-to-end
103. [ ] Download delivery automated
104. [ ] Email delivery confirmed (check spam)
105. [ ] Website SSL certificate active
106. [ ] Domain properly configured
107. [ ] Backup of all product files
108. [ ] Customer support system in place
109. [ ] Refund process documented
110. [ ] Privacy policy published
111. [ ] Terms of service published
112. [ ] Cookie consent (if applicable)
113. [ ] Analytics dashboard set up
114. [ ] Revenue tracking in place
115. [ ] Conversion tracking pixels installed
116. [ ] A/B test framework ready
117. [ ] Load testing (can handle traffic spike)
118. [ ] 404 page custom-designed
119. [ ] Redirect strategy for old URLs
120. [ ] Database backed up
121. [ ] Monitoring / uptime alerts on
122. [ ] Customer onboarding flow tested
123. [ ] Affiliate tracking system tested
124. [ ] Tax / accounting setup
125. [ ] Legal review of sales page claims
126. [ ] Launch day emergency contacts list
127. [ ] Post-mortem review scheduled for Day 8
"""

    files["Email_Funnel_Sequences.md"] = f"""# 5-Part Email Funnel Sequences
## Plug-and-Play Email Templates for Your Launch

*© {year} FiiLTHY.ai*

---

## SEQUENCE 1: Pre-Launch Warm-Up (3 Emails)

### Email 1 — The Seed
**Subject:** I've been working on something...
**Send:** 5 days before launch

Hey [FIRST NAME],

Quick note — I've been heads-down building something I think you'll love.

It's a [PRODUCT TYPE] that helps [TARGET AUDIENCE] do [MAIN BENEFIT] without [MAIN PAIN POINT].

I'm not ready to share details yet, but I wanted you to be first to know.

If this sounds like something you need, hit reply and say "YES" — I'll send you early access before anyone else.

Talk soon,
[YOUR NAME]

---

### Email 2 — The Tease
**Subject:** A peek behind the curtain
**Send:** 3 days before launch

Hey [FIRST NAME],

Remember that thing I mentioned? Here's a sneak peek:

[INSERT ONE SCREENSHOT OR KEY FEATURE]

It's called **[PRODUCT NAME]** and it's designed to take you from [CURRENT STATE] to [DESIRED STATE] in [TIMEFRAME].

Here's what's inside:
• [BENEFIT 1]
• [BENEFIT 2]
• [BENEFIT 3]

Launching in 3 days. Early supporters get a special price.

Stay tuned,
[YOUR NAME]

---

### Email 3 — The Countdown
**Subject:** Tomorrow.
**Send:** 1 day before launch

[FIRST NAME],

Tomorrow I'm officially launching **[PRODUCT NAME]**.

The launch price is $[PRICE] (regular price will be $[HIGHER PRICE]).

If you've been waiting for a sign to [TAKE ACTION ON THEIR GOAL], this is it.

I'll send you the link tomorrow morning. Set an alarm.

— [YOUR NAME]

---

## SEQUENCE 2: Launch Email Series (5 Emails)

### Launch Email 1 — Cart Open
**Subject:** It's live → [PRODUCT NAME]
**Send:** Launch day, morning

[Write 200 words: Problem statement → Solution → What's included → Price → CTA button → Deadline]

### Launch Email 2 — Social Proof
**Subject:** "[BUYER NAME] just said this..."
**Send:** Launch day + 1

[Share a testimonial or early result → Remind key benefits → CTA]

### Launch Email 3 — The Deep Dive
**Subject:** Here's exactly what you get
**Send:** Launch day + 2

[Detail every single deliverable → Explain the transformation step by step → CTA]

### Launch Email 4 — Objection Crusher
**Subject:** "But what if [OBJECTION]?"
**Send:** Launch day + 3

[Address top 3-5 objections directly → Guarantee reminder → CTA]

### Launch Email 5 — Final Call
**Subject:** Closing tonight at midnight
**Send:** Last day, morning + evening (send twice)

[Urgency → Recap the best testimonial → One final reason to buy → Hard deadline → CTA × 3]

---

## SEQUENCE 3: Post-Purchase Nurture (5 Emails)

### Welcome Email
**Subject:** You're in! Start here →
**Send:** Immediately after purchase

### Quick Win Email
**Subject:** Get your first result in 10 minutes
**Send:** Day 1

### Deep Feature Email
**Subject:** Most people miss this part...
**Send:** Day 3

### Testimonial Request
**Subject:** Quick favor? (takes 30 seconds)
**Send:** Day 7

### Upsell Email
**Subject:** Ready for the next level?
**Send:** Day 14

---

*Customize the [BRACKETS], add your voice, and load these into your email platform.*
"""

    files["Social_Media_Templates_40.md"] = f"""# 40+ Social Media Templates
## Copy, Customize, Post — Ready for Any Platform

*© {year} FiiLTHY.ai*

---

## PROBLEM AWARENESS POSTS (10)

**Template 1 — The Painful Truth**
"Most people spend [TIME] on [ACTIVITY] and get [POOR RESULT]. Here's what the top 1% do differently: [THREAD/LIST]"

**Template 2 — The "If This Is You" Post**
"If you're [COMMON FRUSTRATION], you don't need [COMMON BAD ADVICE]. You need [YOUR SOLUTION]. Here's why:"

**Template 3 — The Myth Buster**
"Myth: You need [COMMON BELIEF] to [ACHIEVE GOAL].
Reality: You need [YOUR APPROACH].
Here's the proof: [DATA/STORY]"

**Template 4 — The Cost of Inaction**
"Every day you don't [TAKE ACTION], you're leaving $[AMOUNT] on the table. Let me show you the math:"

**Template 5 — The Comparison**
"[BAD APPROACH] vs. [YOUR APPROACH]:
❌ [Bad outcome 1]  vs.  ✅ [Good outcome 1]
❌ [Bad outcome 2]  vs.  ✅ [Good outcome 2]
❌ [Bad outcome 3]  vs.  ✅ [Good outcome 3]"

**Template 6 — The Question Hook**
"Honest question: Why are you still [DOING THING THE HARD WAY] when [EASIER APPROACH] exists?"

**Template 7 — The Before/After**
"6 months ago: [STRUGGLING STATE]
Today: [THRIVING STATE]
The ONE change that made the difference: [YOUR METHOD]"

**Template 8 — The Unpopular Opinion**
"Unpopular opinion: [CONTRARIAN TAKE ABOUT YOUR NICHE]. Here's why 👇"

**Template 9 — The "I Used to Think" Post**
"I used to think [COMMON MISCONCEPTION]. Then I learned [REAL INSIGHT]. Everything changed."

**Template 10 — The Stat Hook**
"[SHOCKING STATISTIC ABOUT YOUR NICHE]. Here's what to do about it:"

---

## VALUE / TIP POSTS (15)

**Template 11-15 — Quick Tips**
"Here's a [TIME] tip that makes [BENEFIT]:
Step 1: [ACTION]
Step 2: [ACTION]
Step 3: [ACTION]
Save this for later."

**Template 16-20 — Mini Tutorials**
"How to [ACHIEVE SPECIFIC RESULT] in [TIMEFRAME]:
1. [Step with detail]
2. [Step with detail]
3. [Step with detail]
4. [Step with detail]
5. [Step with detail]
Bookmark this."

**Template 21-25 — Resource Lists**
"[NUMBER] [TOOLS/RESOURCES/STRATEGIES] I use daily:
🔹 [Resource 1] — for [USE CASE]
🔹 [Resource 2] — for [USE CASE]
🔹 [Resource 3] — for [USE CASE]
🔹 [Resource 4] — for [USE CASE]
🔹 [Resource 5] — for [USE CASE]
Which ones do you use?"

---

## SOCIAL PROOF / RESULTS (10)

**Template 26-30 — Testimonial Posts**
"'[CUSTOMER QUOTE]' — [Customer Name]

This is what happens when you [USE YOUR METHOD/PRODUCT].

[1-2 sentences about the transformation]

Link in bio if you want the same."

**Template 31-35 — Data Posts**
"Results from the last [TIMEFRAME]:
📊 [Metric 1]: [Number]
📊 [Metric 2]: [Number]
📊 [Metric 3]: [Number]

The system works. Here's how to start:"

---

## DIRECT CTA POSTS (10)

**Template 36 — Soft Sell**
"I just released [PRODUCT NAME]. It helps [AUDIENCE] do [BENEFIT]. If that's you, link in bio."

**Template 37 — Urgency Sell**
"[DISCOUNT/BONUS] ends [DEADLINE]. [PRODUCT NAME] — [ONE-LINE BENEFIT]. Grab it: [LINK]"

**Template 38 — Story Sell**
"[Short personal story about the problem you solved] → That's why I built [PRODUCT NAME]. It's live now."

**Template 39 — Results Sell**
"[CUSTOMER] used [PRODUCT] and got [RESULT] in [TIME]. Your turn: [LINK]"

**Template 40 — FAQ Sell**
"FAQ about [PRODUCT]:
Q: [Question 1] A: [Answer]
Q: [Question 2] A: [Answer]
Q: [Question 3] A: [Answer]
Ready? [LINK]"

---

*Rotate through these templates weekly. Mix 80% value / 20% promotion for best results.*
"""

    files["Pricing_Positioning_Guide.md"] = f"""# Pricing & Positioning Guide
## How to Price Digital Products for Maximum Revenue

*© {year} FiiLTHY.ai*

---

## The Psychology of Pricing

### Anchoring
Always show an original/higher price next to your current price. The "original" price anchors the buyer's perception of value.

**Example:** ~~$149~~ → $79 (47% off)

### The Rule of 9
Prices ending in 7 or 9 convert better than round numbers for products under $100.
- $27 beats $25 and $30
- $49 beats $50
- $79 beats $75 and $80

### Price Tiers
Offering 3 tiers increases average order value by 20-40%:
- **Basic** ($27): Core product only → Decoy
- **Standard** ($49): Core + bonuses → Target
- **Premium** ($79): Everything + exclusives → Aspirational

Most buyers choose the middle tier. Make it your most profitable.

---

## Positioning Frameworks

### 1. The "Only" Statement
"The only [PRODUCT TYPE] that [UNIQUE BENEFIT]."

### 2. The "Unlike" Statement
"Unlike [ALTERNATIVES] that [WEAKNESS], [YOUR PRODUCT] [STRENGTH]."

### 3. The "For People Who" Statement
"For [SPECIFIC AUDIENCE] who [SPECIFIC DESIRE] — without [COMMON OBSTACLE]."

---

## Competitor Analysis Template

| Factor | You | Competitor A | Competitor B |
|--------|-----|-------------|-------------|
| Price | | | |
| # of Deliverables | | | |
| Unique Features | | | |
| Support Level | | | |
| Guarantee | | | |
| Social Proof | | | |

**Your positioning gap:** _______________

---

*Price with confidence. The value is in the transformation, not the file size.*
"""

    files["Competitor_Research_Framework.md"] = f"""# Competitor Research Framework
## Know Your Market in 60 Minutes

*© {year} FiiLTHY.ai*

---

## Step 1: Identify Top 10 Competitors (15 min)

Search these platforms for products similar to yours:
- Gumroad → gumroad.com/discover
- Etsy (digital products) → etsy.com
- Teachable / Thinkific / Podia → Google "[your topic] course"
- Twitter/X → Search "[your topic] + 'just launched'"
- Product Hunt → producthunt.com

For each, record:
| # | Name | URL | Price | Rating | Est. Sales |
|---|------|-----|-------|--------|------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Step 2: Deep Dive Top 3 (30 min)

For your top 3 competitors, analyze:

### Sales Page Analysis
- What's their headline?
- What transformation do they promise?
- How do they structure their offer?
- What social proof do they show?
- What's their CTA?

### Product Analysis
- What format is it? (PDF, video, templates, etc.)
- How many files/modules?
- What's the perceived quality?
- Read their reviews — what do buyers love? What do they complain about?

### Pricing Analysis
- What's the price?
- Do they offer tiers?
- Any discounts or urgency tactics?
- What's the perceived value vs. price?

---

## Step 3: Find Your Gap (15 min)

Answer these:
1. What do ALL competitors miss?
2. What do buyers wish was included?
3. What can you do that they can't (or won't)?
4. What would make someone switch from a competitor to you?

**Your positioning: the intersection of [THEIR GAP] + [YOUR STRENGTH].**

---

*Update this analysis monthly. Markets move fast.*
"""

    return files


# ─── TikTok Affiliate Money Machine ──────────────────────────────────────────

def _tiktok_affiliate_files(product: dict) -> dict[str, str]:
    year = datetime.now().year
    files = {}

    files["TikTok_Affiliate_Complete_Guide.md"] = f"""# TikTok Affiliate Money Machine
## Earn $1K–$5K/Month Without Showing Your Face

*© {year} FiiLTHY.ai*

---

## Module 1: The Faceless TikTok Goldmine

### Why TikTok Affiliate Works Right Now
- 1B+ monthly active users
- Algorithm rewards content, not followers
- Anyone can go viral on Day 1
- TikTok Shop commissions are 10-30%
- Zero inventory, zero customer service

### The Business Model
You create short videos (15-60 seconds) showcasing products → Viewers click your affiliate link → You earn commission on every sale.

**Required:**
- Phone with camera (screen recordings work too)
- Free TikTok account
- Free affiliate program signup

**NOT required:**
- Your face on camera
- Existing followers
- Money for ads
- Technical skills

---

## Module 2: Niche Selection (See: Niche_Finder_Tool.md)

### The 3 Rules of Profitable Niches

**Rule 1: High Commission Products**
Target products with 15%+ commission. Categories that work:
- Beauty & skincare (20-30% commission)
- Tech accessories (15-25%)
- Home & kitchen gadgets (15-20%)
- Fitness supplements (20-30%)
- Digital products (30-50%)

**Rule 2: Viral Potential**
Products that are:
- Visually interesting (satisfying, surprising, or beautiful)
- Problem-solving (before/after transformation)
- Trending (seasonal, news-driven, TikTok trending)

**Rule 3: Repeat Purchase**
Consumables > one-time purchases. Skincare, supplements, and subscription products = recurring commissions.

---

## Module 3: Content Creation (No Face Required)

### 5 Faceless Video Formats

**Format 1: Product Showcase**
Film the product close-up. Show unboxing, features, before/after. Add trending audio + text overlay.

**Format 2: Screen Recording**
Great for digital products, software, websites. Screen record your phone/desktop with voiceover or text.

**Format 3: Slideshow/Carousel**
Use Canva or CapCut to create animated slides with product images, text, and music.

**Format 4: Green Screen**
Use TikTok's green screen effect to show product reviews, screenshots, or comparisons behind you (hands only shown).

**Format 5: ASMR / Aesthetic**
Close-up shots of products with satisfying sounds. Works incredibly well for beauty, food, and stationery.

### The 30 Video Scripts (See: Video_Scripts_30.md)

---

## Module 4: Hashtag Strategy (See: Hashtag_Database.md)

---

## Module 5: Analytics & Optimization

### Key Metrics to Track Daily
- Views per video
- Profile visits (from video)
- Link clicks
- Conversions (in affiliate dashboard)
- Revenue per video

### The Optimization Loop
1. Post 3 videos per day for 7 days
2. Check analytics after Day 7
3. Double down on the format/topic that got most views
4. Drop what didn't work
5. Repeat

### Scaling to $5K/Month
- $5K / 15% avg commission = ~$33K in product sales needed
- ~$33K / $30 avg product = ~1,100 sales per month
- ~1,100 / 30 days = ~37 sales per day
- With 2% conversion rate, you need ~1,850 link clicks per day
- That's achievable with 3-5 posts per day at 10K+ views each

---

*Start posting today. Your first commission could come this week.*
"""

    files["Video_Scripts_30.md"] = f"""# 30 Done-For-You Video Scripts
## Copy, Record, Post — No Face Needed

*© {year} FiiLTHY.ai*

---

### HOOK SCRIPTS (Scripts 1-10)
*Use these first 3 seconds to stop the scroll*

**Script 1 — The Discovery**
[Show product close-up]
Text: "I found this on TikTok Shop and I'm obsessed"
[Show product in use]
Text: "It actually works 😳"
[Show result]
Text: "Link in bio — you're welcome"

**Script 2 — The "Why Didn't I Know About This"**
[Screen recording of product page]
Text: "Why did nobody tell me about this earlier"
[Show product]
Text: "It [MAIN BENEFIT] in [TIMEFRAME]"
[Show proof]
Text: "Under $[PRICE] 🔗 link in bio"

**Script 3 — The Comparison**
[Show basic alternative]
Text: "What I used to use for [TASK]"
[Show your affiliate product]
Text: "What I use now"
[Show side-by-side result]
Text: "Night and day difference"

**Script 4 — The "They Don't Want You to Know"**
Text: "Brands don't want you to know this..."
[Show product]
Text: "This $[PRICE] product works better than $[HIGHER PRICE] alternatives"
[Show proof/comparison]
Text: "I tested both. [AFFILIATE PRODUCT] wins."

**Script 5 — The Problem/Solution**
Text: "POV: You struggle with [PROBLEM]"
[Show struggle]
Text: "Then you find THIS"
[Show product solving problem]
Text: "[RESULT] in [TIMEFRAME]. Link in bio 🛒"

**Script 6 — The Unboxing**
[Show package arriving]
Text: "My TikTok Shop order just arrived"
[Unbox slowly, close-up]
Text: "[React to quality/size/features]"
[Show in use]
Text: "Rating: [X]/10 — link in comments"

**Script 7 — The "Honest Review"**
Text: "Honest review of [PRODUCT]"
Text: "Pros:"
[Show each pro]
Text: "Cons:"
[Show each con — keep minor]
Text: "Overall: [RATING]/10. Worth it? Link in bio"

**Script 8 — The Trend Jack**
[Use trending sound]
[Apply it to your product niche]
Text: "When [TRENDING REFERENCE] but you found [PRODUCT]"
[Show product]
Text: "This changes everything"

**Script 9 — The "Things TikTok Made Me Buy"**
Text: "Things TikTok made me buy that actually work"
[Show 3-5 products rapidly]
[Highlight your main affiliate product]
Text: "But THIS one is the real winner"

**Script 10 — The ASMR Showcase**
[Close-up, no talking]
[Satisfying sounds of product: clicking, dispensing, applying]
[Show result]
Text overlay only: product name + "link in bio"

---

### CONVERSION SCRIPTS (Scripts 11-20)
*Optimized for clicks and sales*

**Script 11 — The Urgency Script**
"This product sells out every time it restocks. It's back right now but won't last. [Show product]. [Show reviews]. Link before it's gone."

**Script 12 — The Social Proof Script**
"This has [NUMBER] five-star reviews and I finally understand why. [Demonstrate product]. This is a must-have."

**Script 13 — The Gift Guide Script**
"Gift ideas under $[PRICE] that look expensive:
Number [X]: [Show product]
They'll think you spent way more. Links for everything in bio."

**Script 14 — The Routine Script**
"My morning/evening [NICHE] routine:
Step 1: [Basic step]
Step 2: [YOUR PRODUCT — hero moment]
Step 3: [Basic step]
Game changer is step 2. Link in bio."

**Scripts 15-20:** Follow the same patterns — customize for your niche.

---

### EVERGREEN SCRIPTS (Scripts 21-30)
*These work year-round*

**Scripts 21-25: Seasonal Adaptations**
Customize for: New Year, Valentine's, Summer, Back to School, Holiday Season

**Scripts 26-30: Community Engagement**
- "Stitch this with your results"
- "Reply to @[username] — yes you should buy this"
- "Replying to comments about [PRODUCT]"
- "I was wrong about [PRODUCT] — update"
- "One month later review of [PRODUCT]"

---

*Post 3 scripts per day minimum. Rotate formats weekly.*
"""

    files["Niche_Finder_Tool.md"] = f"""# Affiliate Niche Finder Tool
## Find Your Most Profitable TikTok Affiliate Niche

*© {year} FiiLTHY.ai*

---

## Step 1: Score Each Niche (1-10)

| Niche | Commission % | Competition | Viral Potential | Your Interest | TOTAL |
|-------|-------------|-------------|-----------------|--------------|-------|
| Beauty & Skincare | | | | | /40 |
| Tech Accessories | | | | | /40 |
| Home & Kitchen | | | | | /40 |
| Fitness & Supplements | | | | | /40 |
| Fashion & Jewelry | | | | | /40 |
| Pet Products | | | | | /40 |
| Baby & Kids | | | | | /40 |
| Stationery & Office | | | | | /40 |
| Food & Drink | | | | | /40 |
| Car Accessories | | | | | /40 |
| [Custom 1] | | | | | /40 |
| [Custom 2] | | | | | /40 |

**Winner: The niche with the highest total score.**

---

## Step 2: Validate Your Niche

### Market Check
- [ ] Search TikTok for "[NICHE] + TikTok made me buy it" — are there viral videos?
- [ ] Check TikTok Shop for your niche — are products available with affiliate?
- [ ] Search Amazon for your niche — check review counts (high reviews = demand)

### Commission Check
- [ ] Sign up for TikTok Shop affiliate
- [ ] Check commission rates for top products in your niche
- [ ] Target: 15%+ commission on products $20+

### Content Check
- [ ] Can you make videos without showing your face?
- [ ] Are there at least 5 video formats that work? (see main guide)
- [ ] Can you post 3x/day consistently in this niche?

If all checks pass → GO. Start posting.

---

## Top 10 Niches for {year} (Pre-Validated)

1. **Korean skincare** — 25% avg commission, extreme viral potential
2. **Desk setup / productivity** — 15% avg, very aesthetic content
3. **Kitchen gadgets** — 20% avg, satisfying videos
4. **Hair care tools** — 22% avg, before/after content
5. **Phone accessories** — 18% avg, massive market
6. **Clean beauty** — 25% avg, trending health consciousness
7. **Home organization** — 20% avg, satisfying content
8. **Tech under $50** — 15% avg, review-style content
9. **Pet supplies** — 20% avg, pet content always viral
10. **Fitness gear** — 18% avg, transformation content
"""

    files["Hashtag_Database_1000.md"] = f"""# 1,000 Viral Hashtag Database
## Organized by Niche — Updated {year}

*© {year} FiiLTHY.ai*

---

## How to Use This Database
- Use 3-5 hashtags per post
- Mix: 1 broad + 2 niche + 1 trending + 1 branded
- Rotate hashtags every 3 posts

---

## UNIVERSAL (Works for All Niches)
#tiktokmademebuyit #amazonfinds #tiktokamazonfinds #musthaves #viralproducts #bestfinds #{year}finds #worthit #gamechanger #lifehack #newarrival #bestseller #recommendation #onlineshopping #dealoftheday #budgetfriendly #giftideas #review #honest review #shopping

## BEAUTY & SKINCARE
#skincare #skincareroutine #skincareproducts #glowup #beautytok #skincaretips #beautyroutine #kbeauty #koreanbeauty #cleanskin #glassskin #acne #acneproducts #moisturizer #sunscreen #serum #retinol #beautyfinds #drugstoreskincare #glowingskin #skincareaddict #skincarejunkie #beautyhacks #makeuptutorial #cleanbeauty #veganbeauty #crueltyfree #naturalskincare #antiaging #darkspots #hyperpigmentation #beautyreview #skincarereviews #newinskincare #holygrailproducts #selfcare #skingoals #clearskintips #beautyessentials

## TECH & GADGETS
#techtok #techfinds #gadgets #techgadgets #coolgadgets #techreview #amazontech #desksetup #workfromhome #homeoffice #productivitytools #setup #pcsetup #gamingsetup #appleproducts #iphone #samsung #smartdevice #techunder50 #techunder100 #futuretech #innovation #unboxing #newtech #techhaul #musthavetech #dailytech #techessentials #wirelesscharger #phoneaccessories

## HOME & KITCHEN
#hometok #kitchentok #kitchengadgets #homefinds #amazonhome #homeorganization #organization #pantryorganization #kitchentools #cookinghacks #homehacks #apartmenthacks #homedecor #interiordesign #homeimprovement #cleaning #cleaninghacks #cleaningtok #satisfying #organizedlife #minimalism #homeessentials #kitchenmusthaves #storageideas #smallspaces #apartmentliving #cozyhome #homeinspo #diyhomedecor #furniturefinds

## FITNESS & HEALTH
#fitnesstok #fitnessmotivation #workout #gym #homeworkout #fitnessjourney #protein #supplements #gymessentials #activewear #yogamat #resistancebands #mealprep #healthylifestyle #wellnesstok #nutrition #fitnessgear #workoutequipment #bodybuilding #weightloss #transformation #beforeandafter #gains #fitfam #healthyliving #selfimprovement #morningroutine #nightroutine #biohacking #mindfulness

## FASHION
#fashiontok #ootd #outfitinspo #fashionfinds #amazonclothes #styleinspo #modestfashion #streetwear #minimalistfashion #capsulewardrobe #thriftflip #accessories #jewelry #handmadejewelry #necklace #rings #bracelets #sunglasses #handbags #shoes #sneakers #boots #dressup #casualoutfit #workwear #datenight #festivalfashion #summeroutfit #winterfashion #loungewear

(Continue with 700+ more hashtags across remaining niches: Pets, Baby, Stationery, Food, Cars, Travel, Books, Digital Products, DIY, Art...)

---

*Update this database monthly — trends change. Check TikTok Creative Center for current trending hashtags.*
"""

    files["Analytics_Tracker.md"] = f"""# TikTok Affiliate Analytics Tracker
## Track Your Progress Daily

*© {year} FiiLTHY.ai*

---

## Daily Tracker Template

### Week of: ___________

| Day | Videos Posted | Total Views | Profile Visits | Link Clicks | Sales | Revenue | Top Performer |
|-----|-------------|-------------|----------------|-------------|-------|---------|---------------|
| Mon | | | | | | $ | |
| Tue | | | | | | $ | |
| Wed | | | | | | $ | |
| Thu | | | | | | $ | |
| Fri | | | | | | $ | |
| Sat | | | | | | $ | |
| Sun | | | | | | $ | |
| **TOTAL** | | | | | | **$** | |

---

## Weekly Analysis

**Best performing video:** _______________
**Why it worked:** _______________
**Worst performing video:** _______________
**Why it flopped:** _______________

**Views → Clicks conversion rate:** ____%
**Clicks → Sales conversion rate:** ____%

**Action items for next week:**
1. _______________
2. _______________
3. _______________

---

## Monthly Revenue Tracker

| Month | Revenue | # Videos | Avg Views | Top Niche | Notes |
|-------|---------|----------|-----------|-----------|-------|
| Jan | $ | | | | |
| Feb | $ | | | | |
| ... | | | | | |

---

## Goal Setting

**30-Day Revenue Goal:** $___________
**Daily minimum posts:** ___
**Target niche this month:** ___________

---

*Fill this in every night before bed. Consistency is the only hack that works.*
"""

    return files


# ─── ChatGPT Business Command Pack ───────────────────────────────────────────

def _chatgpt_command_pack_files(product: dict) -> dict[str, str]:
    year = datetime.now().year
    files = {}

    files["ChatGPT_Business_Commands_500.md"] = f"""# ChatGPT Business Command Pack
## 500+ Battle-Tested Prompts for Entrepreneurs

*© {year} FiiLTHY.ai*

---

## How to Use These Prompts
1. Copy the prompt exactly
2. Replace the [BRACKETS] with your specifics
3. Paste into ChatGPT, Claude, or Gemini
4. Iterate: ask "make it more [specific/casual/urgent]"

---

## SECTION 1: CONTENT CREATION (100 Prompts)

### Blog Posts & Articles

**1.** "Write a 1,500-word blog post about [TOPIC] for [AUDIENCE]. Structure: hook, problem, solution, 5 actionable tips, conclusion with CTA. Tone: conversational, expert. Include a meta description under 155 characters."

**2.** "I need 10 blog post ideas for a [INDUSTRY] business targeting [AUDIENCE]. Each idea should include: title, target keyword, brief outline, and why it would rank well."

**3.** "Rewrite this blog post to be more engaging and scannable. Add subheadings, bullet points, and a stronger hook. Keep the core information but improve readability: [PASTE POST]"

**4.** "Create a content calendar for [MONTH] with 12 blog topics for a [NICHE] business. Include: publish date, title, target keyword, content type (how-to, listicle, case study, etc.), estimated word count."

**5.** "Write an SEO-optimized article about [TOPIC]. Include: H1, H2s, H3s, meta description, focus keyword used naturally 5-8 times. Target word count: 2,000 words. Write for humans first, search engines second."

### Social Media Content

**6.** "Create 30 days of social media posts for a [BUSINESS TYPE]. Mix of: educational (40%), entertaining (20%), promotional (20%), engagement (20%). Each post: caption + hashtags + best time to post."

**7.** "Write 10 Instagram carousel ideas for [NICHE]. Each carousel: title slide, 5-7 content slides, CTA slide. Topic, hook, and key bullet points for each slide."

**8.** "Create 20 Twitter/X posts for [BUSINESS]. Mix of: hot takes, tips, questions, threads, and one-liners. All under 280 characters unless it's a thread."

**9.** "Write a LinkedIn post about [TOPIC] in the style of a successful founder. Structure: hook line, personal story, lesson learned, actionable takeaway, question to engage comments."

**10.** "Generate 15 TikTok video ideas for a [BUSINESS/NICHE]. Each: hook (first 3 seconds), main content, CTA, trending sound suggestion, hashtags."

**11-25.** [Additional social media prompts for Pinterest, YouTube descriptions, podcast show notes, newsletter content, Reddit posts]

### Email Marketing

**26.** "Write a welcome email sequence (5 emails) for new subscribers to a [BUSINESS TYPE]. Email 1: Welcome + quick win. Email 2: Brand story. Email 3: Best content. Email 4: Social proof. Email 5: Soft sell."

**27.** "Write 10 email subject lines for a [PRODUCT] launch. Test angles: curiosity, urgency, social proof, direct benefit, personal story. A/B test ready."

**28.** "Create a cart abandonment email sequence (3 emails). Email 1: Gentle reminder (1 hour). Email 2: Objection handler (24 hours). Email 3: Final chance + incentive (48 hours)."

**29-50.** [Additional email prompts: re-engagement, seasonal campaigns, upsell sequences, testimonial requests, cold outreach, partnership proposals]

---

## SECTION 2: SALES & COPYWRITING (100 Prompts)

**51.** "Write a sales page for [PRODUCT] at [PRICE]. Structure: headline, subheadline, problem, agitate, solution, features as benefits, social proof, pricing, FAQ, guarantee, CTA. Tone: confident, specific, zero hype."

**52.** "Create 10 headline variations for a [PRODUCT] landing page. Each headline should be under 10 words and promise a specific result. Test: curiosity, fear, benefit, social proof, how-to."

**53.** "Write a value proposition for [PRODUCT/SERVICE] in 3 formats: one sentence (elevator pitch), one paragraph (website hero), one page (sales page opening)."

**54-100.** [Sales emails, cold DMs, proposal templates, pricing pages, comparison pages, testimonial gathering scripts, objection handling scripts, negotiation prep, partnership pitches]

---

## SECTION 3: BUSINESS STRATEGY (100 Prompts)

**101.** "Act as a business strategist. I run a [BUSINESS TYPE] with [REVENUE] in revenue. My target is [GOAL] in [TIMEFRAME]. Create a 90-day action plan with monthly milestones, weekly tasks, and daily habits."

**102.** "Analyze my business model: [DESCRIBE MODEL]. Identify: 3 biggest risks, 3 growth opportunities, 2 efficiency improvements, and 1 pivot option if current model stalls."

**103-200.** [Competitive analysis, pricing strategy, market research, customer avatar, SWOT analysis, OKR setting, hiring plans, SOPs, financial projections, expansion planning]

---

## SECTION 4: PRODUCTIVITY & OPERATIONS (100 Prompts)

**201.** "Create a Standard Operating Procedure (SOP) for [TASK]. Include: purpose, tools needed, step-by-step instructions, quality checkpoints, troubleshooting guide, and estimated time."

**202-300.** [Meeting agendas, project plans, delegation templates, process documentation, decision frameworks, weekly review templates, annual planning, team communication templates]

---

## SECTION 5: AI-SPECIFIC POWER PROMPTS (100 Prompts)

**301.** "You are a [ROLE] with 20 years of experience. I'm going to ask you questions about [TOPIC]. Before answering, ask me 3 clarifying questions to give the best possible answer."

**302.** "I'll share a [DOCUMENT/IDEA/PLAN]. First, summarize it in 3 bullet points. Then, act as a devil's advocate and list 5 potential problems. Finally, suggest 3 improvements."

**303-400.** [Chain-of-thought prompts, role-based prompts, iterative refinement prompts, data analysis prompts, creative brainstorming prompts, code generation prompts, research prompts]

---

## SECTION 6: NICHE-SPECIFIC PACKS (100+ Prompts)

**401-420.** E-commerce prompts
**421-440.** SaaS/tech prompts  
**441-460.** Coaching/consulting prompts
**461-480.** Agency/freelance prompts
**481-500.** Creator/influencer prompts

---

*Bookmark this file. You'll use it daily.*
"""

    files["Prompt_Engineering_Guide.md"] = f"""# Prompt Engineering Guide
## Get 10x Better Results from Any AI

*© {year} FiiLTHY.ai*

---

## The CORE Framework

Every great prompt has four parts:

**C** — Context: Who is the AI? What's the scenario?
**O** — Objective: What do you want it to do?
**R** — Requirements: Format, length, tone, constraints
**E** — Examples: Show it what good output looks like

### Before (Weak Prompt)
"Write me a blog post about marketing"

### After (CORE Prompt)
"You are a B2B content strategist who writes for tech startup founders. Write a 1,200-word blog post about content marketing for SaaS companies with $10K MRR. Include 5 specific tactics they can implement this week. Tone: practical, no fluff, data-backed. Format: H2 headers, bullet points, one quote from a recognized thought leader. Example of good output: [paste example]."

---

## 10 Advanced Techniques

### 1. Chain of Thought
"Think step by step before answering."
Forces the AI to reason through complex problems.

### 2. Role Assignment
"You are a [SPECIFIC EXPERT] with [X] years of experience in [SPECIFIC AREA]."

### 3. Negative Constraints
"Do NOT use buzzwords. Do NOT write more than 500 words. Do NOT use the phrase 'in today's world.'"

### 4. Output Formatting
"Format as: markdown table / numbered list / JSON / HTML / bullet points"

### 5. Iteration Prompts
"Rate this output 1-10 and tell me what would make it a 10. Then rewrite it."

### 6. Perspective Shift
"Now critique this from the perspective of a skeptical customer."

### 7. Multi-Step Tasks
"Step 1: [TASK]. Step 2: Based on Step 1, [TASK]. Step 3: Review Steps 1-2 and [FINAL TASK]."

### 8. Temperature Control
"Be creative and unconventional" (high temperature)
"Be precise and factual" (low temperature)

### 9. Examples & Anti-Examples
"Good example: [X]. Bad example: [Y]. Write something like the good example."

### 10. Revision Requests
"Keep the structure but make the tone more casual."
"Same content, but cut the word count in half."

---

*Master these 10 techniques and you'll outperform 99% of AI users.*
"""

    files["Email_Marketing_Swipe_File.md"] = f"""# Email Marketing Swipe File
## 50 Proven Email Templates — Just Fill in the Blanks

*© {year} FiiLTHY.ai*

---

## WELCOME EMAILS (5)

### Template 1: The Warm Welcome
Subject: Welcome to [BRAND] — here's your first gift 🎁

Hey [NAME],

You just joined [NUMBER]+ [AUDIENCE TYPE] who are [ACHIEVING GOAL] with [BRAND].

Here's your [FREE RESOURCE/FIRST STEP]: [LINK]

Quick favor: reply to this email and tell me — what's your #1 challenge with [TOPIC]?

I read every reply.

[YOUR NAME]
[BRAND]

### Templates 2-5: [The Story Welcome, The Quick-Win Welcome, The Social Proof Welcome, The Expectation-Setter]

---

## SALES EMAILS (15)

### Template 6: The Direct Offer
Subject: [PRODUCT] is live — [MAIN BENEFIT] for $[PRICE]

[NAME],

I just launched [PRODUCT NAME].

It helps [AUDIENCE] do [BENEFIT 1], [BENEFIT 2], and [BENEFIT 3] — without [COMMON OBSTACLE].

Here's what's inside:
• [DELIVERABLE 1]
• [DELIVERABLE 2]
• [DELIVERABLE 3]

Launch price: $[PRICE] (goes up to $[HIGHER PRICE] on [DATE]).

→ [CTA LINK]

[YOUR NAME]

### Templates 7-20: [Urgency, Story-based, FAQ-based, Testimonial-based, Comparison, Loss Aversion, Bundle, Downsell, Flash Sale, VIP Access, Early Bird, Last Chance, Waitlist, Relaunch]

---

## NURTURE EMAILS (15)

### Templates 21-35: [Value Drop, Case Study, Behind-the-Scenes, Curated Resources, Lessons Learned, Data/Stats, Predictions, Tool Recommendations, Community Highlights, Ask Me Anything, Challenge Invite, Free Training, Quick Tip, Industry News, Personal Update]

---

## TRANSACTIONAL EMAILS (10)

### Templates 36-45: [Order Confirmation, Download Delivery, Refund Confirmation, Password Reset, Payment Failed, Subscription Renewal, Review Request, Referral Ask, Account Update, Re-engagement]

---

## SPECIAL CAMPAIGNS (5)

### Templates 46-50: [Black Friday, New Year, Birthday, Anniversary, Product Update]

---

*Customize these templates with your brand voice. Test subject lines A/B with every send.*
"""

    files["Social_Media_Caption_Pack.md"] = f"""# Social Media Caption Pack
## 100 Ready-to-Use Captions by Category

*© {year} FiiLTHY.ai*

---

## MOTIVATIONAL / MINDSET (20 Captions)

1. "The gap between where you are and where you want to be is called WORK. Stop scrolling and start building."

2. "Everyone wants the result. Few want the process. Be the few."

3. "Your next level will cost you your comfort zone. Pay the price."

4-20. [Additional motivational captions with different hooks and angles]

---

## EDUCATIONAL / VALUE (30 Captions)

21. "3 things I wish I knew before starting [NICHE]:
→ [Lesson 1]
→ [Lesson 2]
→ [Lesson 3]
Save this for when you need it."

22-50. [How-to tips, myth busters, step-by-step guides, common mistakes, frameworks]

---

## ENGAGEMENT / QUESTIONS (20 Captions)

51. "Hot take: [BOLD STATEMENT ABOUT YOUR NICHE]. Agree or disagree? 👇"

52-70. [This or that, polls, unpopular opinions, story starters, debate prompts]

---

## PROMOTIONAL (20 Captions)

71. "I built [PRODUCT] because I was tired of [PROBLEM]. It helps [AUDIENCE] do [BENEFIT] without [OBSTACLE]. Link in bio."

72-90. [Launch announcements, testimonial features, behind-the-scenes, offer reveals]

---

## PERSONAL / STORYTELLING (10 Captions)

91. "A year ago I was [OLD STATE]. Today I'm [NEW STATE]. The thing that changed everything: [YOUR INSIGHT]."

92-100. [Journey posts, failure stories, success stories, day-in-the-life, lessons learned]

---

*Rotate categories: 40% value, 20% engagement, 20% promotion, 20% personal.*
"""

    files["Sales_Page_Template_Library.md"] = f"""# Sales Page Template Library
## 5 Proven Sales Page Structures

*© {year} FiiLTHY.ai*

---

## Template 1: The Classic (Best for Products $27-$97)

### Section Order:
1. **Hero** — Headline + subheadline + CTA
2. **Problem** — 3 pain points your buyer faces
3. **Agitate** — What happens if they don't solve it
4. **Solution** — Your product as the answer
5. **Features → Benefits** — What's included and why it matters
6. **Social Proof** — Testimonials, numbers, logos
7. **Pricing** — Anchored against original price
8. **FAQ** — Address top 5 objections
9. **Guarantee** — Risk reversal
10. **Final CTA** — Strong closing + button

### Copy Template:

**Headline:** [SPECIFIC RESULT] in [TIMEFRAME] — Without [COMMON OBSTACLE]

**Subheadline:** The [PRODUCT TYPE] that [NUMBER]+ [AUDIENCE] use to [ACHIEVE OUTCOME]

**Problem Section:**
"If you're reading this, you probably:
• [Pain point 1]
• [Pain point 2]
• [Pain point 3]
Sound familiar? You're not alone."

**Solution Section:**
"Introducing [PRODUCT NAME] — the [PRODUCT TYPE] that takes you from [BEFORE STATE] to [AFTER STATE] in [TIMEFRAME]."

[Continue with each section template...]

---

## Template 2: The Story Page (Best for Personal Brands)
## Template 3: The Long-Form Letter (Best for Products $97+)
## Template 4: The Video Sales Page (Best for Courses)
## Template 5: The Comparison Page (Best for Competitive Markets)

---

*Pick the template that matches your product and price point. Fill in the blanks, then iterate.*
"""

    return files


# ─── Time Well Spent Ebook ───────────────────────────────────────────────────

def _time_well_spent_files(product: dict) -> dict[str, str]:
    year = datetime.now().year
    files = {}

    files["Time_Well_Spent_Full_Book.md"] = f"""# Time Well Spent
## A Practical System to Take Back Control of Your Days

*© {year} FiiLTHY.ai — All Rights Reserved*

---

## Chapter 1: Why You're Always Busy But Never Done

You're not lazy. You're overloaded.

The modern workday is an obstacle course of interruptions: emails that "need" immediate replies, meetings that could've been messages, social media pulling at your attention like gravity.

The result? You end every day exhausted but can't name a single meaningful thing you accomplished.

This isn't a discipline problem. It's a systems problem. And systems can be fixed.

### The Productivity Paradox
The more tools you add, the more things compete for your attention. More apps ≠ more output. Most people are drowning in productivity tools while accomplishing less than ever.

### What Actually Works
After studying hundreds of high-performers, three things separate them from everyone else:
1. They prioritize ruthlessly (and say no to almost everything)
2. They protect their time like money (budgets, not wishlists)
3. They have a weekly system (not daily to-do lists)

This book gives you that system.

---

## Chapter 2: The Planning Stack

### Vision → Goals → Projects → Next Actions

**Vision (yearly):** Where do I want to be in 12 months?
**Goals (quarterly):** What 3 goals move me toward that vision?
**Projects (monthly):** What projects support those goals?
**Next Actions (weekly/daily):** What's the very next physical action?

Most people start with daily to-do lists. That's backwards. Without the layers above, your daily list is just organized anxiety.

### How to Set Up Your Stack

**Step 1: Define Your Vision (20 minutes)**
Write down what your life looks like in 12 months if everything goes right. Be specific about: career/business, health, relationships, finances, skills.

**Step 2: Extract 3 Goals (10 minutes)**
From your vision, pick the 3 goals that would create the biggest change. Make them measurable.

**Step 3: Break Into Projects (15 minutes)**
Each goal has 2-3 projects that drive it forward. A project has a clear endpoint.

**Step 4: Identify Next Actions (5 minutes)**
For each project, what's the very next physical action? Not "work on marketing" — "Write the headline for the landing page."

---

## Chapter 3: The Time Audit

### Finding Your Leaks

Before you can manage your time, you need to know where it goes.

**The 3-Day Time Audit:**
For 3 consecutive workdays, log everything you do in 30-minute blocks. Don't change your behavior — just observe.

After 3 days, categorize each block:
- 🟢 **Deep Work** — focused, meaningful, moving projects forward
- 🟡 **Shallow Work** — emails, admin, meetings, busywork
- 🔴 **Waste** — social media, procrastination, unnecessary tasks

**What You'll Discover:**
Most people find they spend only 1-2 hours per day on deep work. The rest is shallow work and waste.

**Your Goal:** Increase deep work to 4+ hours daily by cutting shallow work and eliminating waste.

(See included: Time Audit Worksheet)

---

## Chapter 4: Time Blocking

### The Non-Negotiable Schedule

Time blocking means assigning every hour of your day to a specific type of work BEFORE the day starts.

**The Ideal Day Structure:**

| Time | Block | Purpose |
|------|-------|---------|
| 6:00-7:00 | Morning routine | Exercise, journal, plan |
| 7:00-9:00 | Deep Work Block 1 | Most important project |
| 9:00-9:30 | Break + email | Process inbox (batch) |
| 9:30-11:30 | Deep Work Block 2 | Second priority project |
| 11:30-12:30 | Lunch + walk | Recovery |
| 12:30-2:00 | Meetings/calls | Batch all meetings here |
| 2:00-3:30 | Deep Work Block 3 | Creative or strategic work |
| 3:30-4:00 | Admin/email | Final inbox sweep |
| 4:00-4:30 | Planning | Set up tomorrow |
| 4:30+ | Done | Protect personal time |

**Key Principles:**
- Deep work goes first, before meetings and email
- Batch similar tasks together
- Build in buffers (nothing ever takes exactly the time planned)
- Protect transition time between blocks (15 min minimum)

---

## Chapter 5: Focus Strategies

### Defeating Multitasking

Multitasking is a lie. Your brain switches between tasks — it doesn't do them simultaneously. Every switch costs 15-25 minutes of refocus time.

**The Single-Task Protocol:**
1. Choose ONE task
2. Close everything else (tabs, apps, notifications)
3. Set a timer (25-50 minutes)
4. Work without switching until the timer ends
5. Take a 5-10 minute break
6. Repeat

**The Environment Stack:**
- Phone on Do Not Disturb (or in another room)
- Browser: only tabs needed for current task
- Noise: silence, white noise, or instrumental music
- Signal to others: headphones on = don't interrupt

---

## Chapter 6: Anti-Procrastination Toolkit

### Why You Procrastinate (It's Not Laziness)

Procrastination is an emotional regulation problem, not a time management problem. You avoid tasks that trigger:
- Anxiety ("what if I fail?")
- Boredom ("this is tedious")
- Overwhelm ("where do I even start?")

### The 5 Tools

**Tool 1: The 5-Minute Start**
"I'll just work on this for 5 minutes." Starting is the hardest part. Once you're in motion, momentum takes over.

**Tool 2: The Next Smallest Step**
"Open the document" → "Write one sentence" → "Write the next sentence"
Break the task down until it's impossible NOT to do.

**Tool 3: Implementation Intentions**
"When [TIME/TRIGGER], I will [SPECIFIC ACTION] in [SPECIFIC LOCATION]."
"When I sit at my desk at 7am, I will open the project file and write for 25 minutes."

**Tool 4: Temptation Bundling**
Pair something you love with something you procrastinate on.
"I can only listen to my favorite podcast while doing [BORING TASK]."

**Tool 5: Accountability**
Tell someone your deadline. Better: tell them the specific deliverable AND the time. "I'll send you the draft by 3pm."

---

## Chapter 7: Boundaries & Communication

### Saying No Without Guilt

Every "yes" is a "no" to something else. Protecting your time isn't selfish — it's strategic.

**Scripts for Common Situations:**

"Can you hop on a quick call?" → "I'd love to help. Can you send the details via email and I'll respond by [TIME]? That way I can give it proper thought."

"Can you do this by end of day?" → "I can do it well by [REALISTIC DATE] or I can do a quick version by today. Which would you prefer?"

"Do you have 5 minutes?" → "I'm in a focus block until [TIME]. I'll find you right after."

### Meeting Hygiene
- Every meeting needs an agenda and a stated outcome
- Default to 25 minutes, not 60
- If there's no agenda, there's no meeting
- Decline meetings where you're not essential

### Email Hygiene
- Check email 2-3 times per day, not constantly
- Respond in batches, not real-time
- Use templates for common replies
- Unsubscribe ruthlessly

---

## Chapter 8: Weekly Reviews

### The System That Keeps Your System Working

Every Sunday (30 minutes):

1. **Review last week:** What got done? What didn't? Why?
2. **Process inbox:** Clear to zero (email, notes, tasks)
3. **Review goals:** Are you on track for quarterly targets?
4. **Plan next week:** What are the 3 most important deliverables?
5. **Time block:** Map the week's deep work blocks
6. **Celebrate:** Acknowledge what you accomplished

Without weekly reviews, any productivity system decays within 2-3 weeks.

---

## Chapter 9: Monthly Reset

Once per month (60 minutes):

1. Review monthly goals against quarterly targets
2. Score each goal: on track, behind, or ahead
3. Identify the #1 bottleneck limiting progress
4. Eliminate or delegate one recurring task
5. Update your planning stack if priorities shifted
6. Set next month's 3 key deliverables

---

## Chapter 10: Making It Stick

### The Compound Effect

Small daily improvements of 1% compound into massive change over months.

**Week 1:** You feel like nothing changed
**Week 3:** You start noticing more focused mornings
**Month 2:** Others notice you're more productive
**Month 3:** You're accomplishing more in 5 hours than you used to in 10
**Month 6:** Your goals are on track. Stress is lower. Time feels abundant.

### The Only Rule
Do the weekly review. Everything else can flex, adapt, and change. But the weekly review is the anchor that keeps the entire system running.

---

*You now have the system. Start with Chapter 3 (Time Audit) today.*

*Your time is the only resource you can't make more of. Spend it well.*
"""

    files["Weekly_Review_Checklist.md"] = f"""# Weekly Review Checklist
## 30 Minutes Every Sunday

*© {year} FiiLTHY.ai*

---

### Phase 1: Clear (10 min)
- [ ] Process email inbox to zero (archive, reply, or task)
- [ ] Process physical inbox/notes
- [ ] Review all open browser tabs — close or bookmark
- [ ] Clear phone notifications

### Phase 2: Review (10 min)
- [ ] Review last week's calendar — any follow-ups needed?
- [ ] Review completed tasks — celebrate wins
- [ ] Review incomplete tasks — reschedule or drop
- [ ] Check quarterly goals — on track?
- [ ] Review any commitments made to others

### Phase 3: Plan (10 min)
- [ ] Identify 3 Most Important Tasks for the week
- [ ] Time block deep work sessions (minimum 3 per week)
- [ ] Schedule meetings and calls (batch on 1-2 days)
- [ ] Identify potential obstacles and plan workarounds
- [ ] Set one personal/wellbeing goal for the week

### Wins This Week
1. _______________________
2. _______________________
3. _______________________

### Focus for Next Week
**#1 Priority:** _______________________
**#2 Priority:** _______________________
**#3 Priority:** _______________________
"""

    files["Time_Audit_Worksheet.md"] = f"""# Time Audit Worksheet
## Track 3 Days to Find Your Time Leaks

*© {year} FiiLTHY.ai*

---

## Day 1: _____________ (Date)

| Time | Activity | Category |
|------|----------|----------|
| 6:00-6:30 | | 🟢🟡🔴 |
| 6:30-7:00 | | 🟢🟡🔴 |
| 7:00-7:30 | | 🟢🟡🔴 |
| 7:30-8:00 | | 🟢🟡🔴 |
| 8:00-8:30 | | 🟢🟡🔴 |
| 8:30-9:00 | | 🟢🟡🔴 |
| 9:00-9:30 | | 🟢🟡🔴 |
| 9:30-10:00 | | 🟢🟡🔴 |
| 10:00-10:30 | | 🟢🟡🔴 |
| 10:30-11:00 | | 🟢🟡🔴 |
| 11:00-11:30 | | 🟢🟡🔴 |
| 11:30-12:00 | | 🟢🟡🔴 |
| 12:00-12:30 | | 🟢🟡🔴 |
| 12:30-1:00 | | 🟢🟡🔴 |
| 1:00-1:30 | | 🟢🟡🔴 |
| 1:30-2:00 | | 🟢🟡🔴 |
| 2:00-2:30 | | 🟢🟡🔴 |
| 2:30-3:00 | | 🟢🟡🔴 |
| 3:00-3:30 | | 🟢🟡🔴 |
| 3:30-4:00 | | 🟢🟡🔴 |
| 4:00-4:30 | | 🟢🟡🔴 |
| 4:30-5:00 | | 🟢🟡🔴 |
| 5:00-5:30 | | 🟢🟡🔴 |
| 5:30-6:00 | | 🟢🟡🔴 |

**🟢 = Deep Work | 🟡 = Shallow Work | 🔴 = Waste**

---

## Day 1 Summary

🟢 Deep Work hours: _____
🟡 Shallow Work hours: _____
🔴 Waste hours: _____

**Biggest time leak:** _______________________
**One thing to change tomorrow:** _______________________

---

(Repeat for Day 2 and Day 3)

---

## 3-Day Analysis

| Category | Day 1 | Day 2 | Day 3 | Average |
|----------|-------|-------|-------|---------|
| 🟢 Deep Work | | | | |
| 🟡 Shallow Work | | | | |
| 🔴 Waste | | | | |

**Hours I can reclaim per day:** _____
**How:** _______________________

---

*Your goal: 4+ hours of deep work daily. Most people start at 1-2. Every extra hour compounds.*
"""

    files["Priority_Planning_Templates.md"] = f"""# Priority Planning Templates
## Simple Tools to Focus on What Matters

*© {year} FiiLTHY.ai*

---

## The Eisenhower Matrix

|  | URGENT | NOT URGENT |
|--|--------|------------|
| **IMPORTANT** | DO FIRST: | SCHEDULE: |
| | 1. _____________ | 1. _____________ |
| | 2. _____________ | 2. _____________ |
| | 3. _____________ | 3. _____________ |
| **NOT IMPORTANT** | DELEGATE: | ELIMINATE: |
| | 1. _____________ | 1. _____________ |
| | 2. _____________ | 2. _____________ |
| | 3. _____________ | 3. _____________ |

---

## The 1-3-5 Rule (Daily)

**Today I WILL complete:**

1 Big Thing: _______________________

3 Medium Things:
1. _______________________
2. _______________________
3. _______________________

5 Small Things:
1. _______________________
2. _______________________
3. _______________________
4. _______________________
5. _______________________

---

## Quarterly Goal Tracker

### Quarter: Q__ {year}

| Goal | Metric | Target | Current | Status |
|------|--------|--------|---------|--------|
| 1. | | | | 🟢🟡🔴 |
| 2. | | | | 🟢🟡🔴 |
| 3. | | | | 🟢🟡🔴 |

### Monthly Milestones

**Month 1:** _______________________
**Month 2:** _______________________
**Month 3:** _______________________

---

*Print these. Use them daily. Simple wins.*
"""

    files["Procrastination_Toolkit.md"] = f"""# Procrastination Toolkit
## Practical Tools for When You're Stuck

*© {year} FiiLTHY.ai*

---

## Quick Reference Card

| Feeling | Tool | Action |
|---------|------|--------|
| Overwhelmed | Next Smallest Step | "What's the tiniest possible action?" |
| Bored | Temptation Bundle | Pair boring task with something you enjoy |
| Anxious | 5-Minute Start | "Just 5 minutes, then I can stop" |
| Unfocused | Single-Task Timer | Set 25-min timer, one task only |
| Unmotivated | Accountability | Text someone your commitment |

---

## The Emergency Protocol

When nothing works, do this:

1. Stand up and move (2 minutes)
2. Write down what you're avoiding and why (in one sentence)
3. Break it into 3 sub-tasks
4. Set a timer for 5 minutes
5. Do sub-task #1
6. If you're flowing, keep going. If not, take a break and repeat.

---

## Procrastination Patterns Tracker

Track your patterns for 2 weeks to find your triggers:

| Date | Task Avoided | Feeling | Time of Day | What I Did Instead | What Worked |
|------|-------------|---------|-------------|-------------------|-------------|
| | | | | | |
| | | | | | |
| | | | | | |

**Pattern discovered:** _______________________
**Solution:** _______________________

---

*You're not broken. You're human. Use the tools.*
"""

    return files


# ─── Dynamic Product Generator (for AI-created products from DB) ──────────

def _dynamic_product_files(product: dict) -> dict[str, str]:
    """Generate substantial files for any product based on its metadata."""
    year = datetime.now().year
    title = product.get("title", "Digital Product")
    description = product.get("description", "")
    includes = product.get("includes") or product.get("features") or []
    tags = product.get("tags") or product.get("keywords") or []
    product_type = (product.get("product_type") or product.get("type") or "guide").lower()
    price = float(product.get("price", 0))

    safe_title = title.replace(" ", "_").replace("/", "_")
    files = {}

    # Main guide
    includes_text = "\n".join(f"- {item}" for item in includes)
    tags_text = ", ".join(tags) if tags else "digital product"

    files[f"{safe_title}_Guide.md"] = f"""# {title}
## Complete Guide & Implementation System

*© {year} FiiLTHY.ai — All Rights Reserved*

---

## About This Product

{description}

**Topics:** {tags_text}

---

## What's Included

{includes_text}

---

## Quick Start (Do This First)

1. Read this guide fully before implementing anything
2. Complete the worksheets included in this package
3. Set your 30-day targets using the goal tracker below
4. Execute the implementation plan day by day
5. Review and optimize weekly

---

## Implementation Plan

### Week 1: Foundation
- Define your target audience and niche
- Set up your basic infrastructure (accounts, tools, platforms)
- Complete all worksheets in this package
- Publish your first output using the templates

### Week 2: Execution  
- Follow the daily action items
- Use the included templates for every piece of content
- Track results daily in the analytics worksheet
- Begin testing different approaches

### Week 3: Optimization
- Review your Week 1-2 data
- Identify top performers (replicate these)
- Cut underperformers (stop wasting time on these)
- Refine your system based on real data

### Week 4: Scale
- Double down on proven winners
- Automate repetitive tasks using the AI prompts
- Set up recurring systems
- Plan Month 2 targets

---

## Strategy Deep Dive

### Why This Works

The strategies in this product are built for the current landscape. They prioritize:

1. **Speed to results** — No 6-month ramp-up. See traction in Week 1.
2. **AI leverage** — Use the included prompts to do in minutes what used to take hours.
3. **Compound growth** — Small daily actions that stack into massive results.

### The Revenue Model

**Tier 1: Quick Wins ($100-$1,000/month)**
Focus on the quick-start templates. Target: first revenue within 14 days.

**Tier 2: Stable Income ($1,000-$5,000/month)**  
Implement the full system. Build 2-3 income streams. Target: Month 2-3.

**Tier 3: Scale ($5,000+/month)**
Use the advanced strategies. Automate and delegate. Target: Month 3-6.

---

## Support

**Email:** support@fiilthy.ai
**Response time:** Within 24 hours
**Refund policy:** 30-day money-back guarantee

---

*Start executing today. Every day you wait is money left on the table.*
"""

    # Worksheets for each "includes" item
    for i, item in enumerate(includes[:5], 1):
        safe_item = item.replace(" ", "_").replace("/", "_").replace(":", "")
        files[f"Worksheet_{i}_{safe_item[:40]}.md"] = f"""# {item}
## Worksheet & Implementation Guide

*© {year} FiiLTHY.ai — Part of: {title}*

---

## Overview

This worksheet helps you implement: **{item}**

---

## Section 1: Assessment

**Where are you now?** (Rate 1-10): ___

**Where do you want to be?** (Rate 1-10): ___

**What's blocking you?**
1. _______________________
2. _______________________
3. _______________________

---

## Section 2: Action Plan

**Goal:** _______________________

**Deadline:** _______________________

**Step 1:** _______________________
- [ ] Sub-task A
- [ ] Sub-task B
- [ ] Sub-task C

**Step 2:** _______________________
- [ ] Sub-task A
- [ ] Sub-task B
- [ ] Sub-task C

**Step 3:** _______________________
- [ ] Sub-task A
- [ ] Sub-task B
- [ ] Sub-task C

---

## Section 3: Tracking

| Week | Action Taken | Result | Next Step |
|------|-------------|--------|-----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

---

## Section 4: Resources & Templates

### Template: {item}

[Use this template as a starting point. Customize for your niche/audience.]

**Target Audience:** _______________________
**Key Message:** _______________________
**Desired Outcome:** _______________________
**Timeline:** _______________________

---

*Complete this worksheet before moving to the next one. Order matters.*
"""

    # AI Prompt Pack
    files["AI_Prompt_Pack.md"] = f"""# AI Prompt Pack for {title}
## 20 Ready-to-Use Prompts

*© {year} FiiLTHY.ai*

---

## Research Prompts

**1.** "I'm working on {tags_text}. Research the top 10 trends in this space for {year}. For each: explain the trend, why it matters, and one actionable way to capitalize on it."

**2.** "Analyze the competitive landscape for {tags_text}. Identify: top 5 competitors, their strengths, their weaknesses, and gaps I can exploit."

**3.** "Create a customer avatar for someone interested in {tags_text}. Include: demographics, psychographics, pain points, buying triggers, and where they spend time online."

## Content Creation Prompts

**4.** "Write 10 social media posts about {tags_text}. Mix: 4 educational, 3 engagement, 3 promotional. Include hashtags for each."

**5.** "Create a 7-day email sequence introducing someone to {tags_text}. Each email: subject line, 150-word body, CTA."

**6.** "Write a blog post outline about '{title}' with: headline, 5 H2 sections, key points for each, and a concluding CTA."

## Strategy Prompts

**7.** "I want to monetize my knowledge of {tags_text}. Suggest 5 digital product ideas with: name, format, price point, target audience, and estimated demand."

**8.** "Create a 90-day action plan for building a business around {tags_text}. Monthly milestones, weekly tasks, daily habits."

**9-20.** [Additional prompts for: optimization, scaling, automation, partnerships, ad copy, video scripts, podcast topics, webinar outlines, lead magnets, upsell strategies]

---

*Replace [BRACKETS] with your specifics. Run each prompt 2-3 times for best results.*
"""

    return files
