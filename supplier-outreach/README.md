# NAU Concrete Canoe 2026 - Supplier Email Generator

**Mission**: Generate 15 personalized sponsorship emails for material suppliers  
**Deadline**: February 11, 2026 (Materials needed!)  
**Contact**: Miles - miles27.85shah@nau.edu - (928) 254-9179

---

## 🎯 Overview

This system automatically generates personalized sponsorship request emails for the NAU Concrete Canoe team using AI:

- **Previous Donors (8)**: Thank-you + renewal request emails
- **New Targets (7)**: Introduction + sponsorship request emails
- **AI-Powered**: Uses OpenRouter (Gemini) for generation + ChatGPT for validation
- **Quality Control**: Each email validated, minimum 7/10 score required
- **Git Integration**: Auto-commits each email as it's generated

---

## 📁 Project Structure

```
supplier-outreach/
├── data/
│   └── previous_donors.json       # Supplier database (8 donors + 7 targets)
├── scripts/
│   ├── generate_emails.py         # Main email generator
│   └── run_generation.sh          # Runner script
├── emails/                         # Generated emails (created when run)
│   ├── 01_simpson_strong_tie.txt
│   ├── 02_western_technologies.txt
│   └── ... (15 total)
├── TRACKING.md                     # Outreach tracking sheet (created when run)
└── validation_log.txt              # ChatGPT scores (created when run)
```

---

## 🚀 Quick Start

### 1. Set API Keys

```bash
export OPENROUTER_API_KEY='sk-or-v1-...'
export OPENAI_API_KEY='sk-...'
```

**Get API Keys:**
- OpenRouter: https://openrouter.ai/keys (Free tier available)
- OpenAI: https://platform.openai.com/api-keys (Costs ~$0.15 total)

### 2. Run Generator

```bash
cd /root/projects/concrete-canoe-2026/supplier-outreach/scripts
./run_generation.sh
```

### 3. Review & Send

```bash
# View all emails
ls -lh ../emails/

# Read first email (Simpson Strong-Tie - Previous Donor)
cat ../emails/01_simpson_strong_tie.txt

# View tracking sheet
cat ../TRACKING.md

# Check validation scores
cat ../validation_log.txt
```

---

## 📧 Email Categories

### Previous Donors (HIGH Priority!)
These companies donated last year - highest success rate!

1. **Simpson Strong-Tie** - Carbon fiber mesh
2. **Western Technologies (RMA)** - Testing services (LOCAL)
3. **Aero Aggregates** - Lightweight aggregate
4. **National Waste & Recycling** - Carbon carbonite
5. **Flagstaff Landscape Products** - Red sand (LOCAL)
6. **Salt River Materials** - Cement & fly ash (MAJOR DONOR)
7. **Loven Contracting** - Cash donation (LOCAL)
8. **Unknown Nevada Supplier** - Slag 120

### New Targets
Fresh contacts with high potential:

9. **Poraver North America** - Expanded glass aggregate (CRITICAL)
10. **CalPortland** - Portland cement
11. **Sika Corporation** - Admixtures
12. **CEMEX Arizona** - Portland cement
13. **Master Builders Solutions** - Superplasticizer
14. **Quikrete** - Backup cement source
15. **Home Depot Flagstaff** - Materials/gift card (LOCAL)

---

## 🎨 Email Structure

Each generated email includes:

1. **Personalized Subject Line**
2. **Opening** - Warm greeting, personalized to company
3. **Background**:
   - Previous donors: Thank you for last year
   - New targets: Introduction to NAU Concrete Canoe
4. **The Ask** - Specific product request with amount
5. **Sponsor Benefits**:
   - Logo on canoe hull (visible at competition)
   - Social media recognition
   - Competition photos
   - Recognition in technical paper
   - Certificate from NAU
6. **Logistics** - Easy pickup/shipping details
7. **Call to Action** - Clear next steps
8. **Signature** - Full contact info including phone

**Length**: 200-300 words  
**Tone**: Professional, enthusiastic, personalized  
**Phone**: (928) 254-9179 in EVERY email

---

## 🤖 AI System

### Generation (OpenRouter - Gemini 2.0 Flash)
- Model: `google/gemini-2.0-flash-exp:free`
- Cost: **$0** (free tier)
- Creates personalized emails based on supplier data

### Validation (OpenAI - ChatGPT)
- Model: `gpt-4o-mini`
- Cost: **~$0.01 per email** (~$0.15 total)
- Scores each email 1-10
- Minimum 7/10 to accept
- Auto-regenerates if below threshold (max 3 attempts)

---

## 📊 Output Files

### Generated Emails
```
emails/01_simpson_strong_tie.txt
emails/02_western_technologies_rma_company.txt
emails/03_aero_aggregates_of_north_america.txt
... (15 total)
```

### Tracking Sheet
`TRACKING.md` - Complete outreach tracking:
- All suppliers organized by priority
- Contact information
- Checkboxes for tracking
- Response tracking table
- Materials status checklist

### Validation Log
`validation_log.txt` - ChatGPT scores for each email

---

## 📈 Success Metrics

✅ **All 15 emails generated**  
✅ **ChatGPT validation scores ≥ 7/10**  
✅ **Phone number in every email**  
✅ **Previous donors thanked personally**  
✅ **Committed to git (16 commits)**  
✅ **Ready to copy & send**

---

## 🎯 Sending Strategy

### Priority Order:
1. **🔴 Previous Donors First** (Day 1-2)
   - They already know us
   - Highest success rate
   - Send ASAP!

2. **🟡 Critical New Targets** (Day 2-3)
   - Poraver (known concrete canoe supporter)
   - Local Flagstaff suppliers

3. **🟢 Other New Targets** (Day 3-5)
   - Regional suppliers
   - National companies

### Tips:
- **Use NAU email** (miles27.85shah@nau.edu) - more professional
- **Personalize subject lines** if desired
- **Follow up after 3-4 days** if no response
- **Local suppliers**: Mention easy pickup
- **Track responses** in TRACKING.md

---

## 🔧 Technical Details

### Requirements
- Python 3.6+
- `requests` library (auto-installed)
- Git
- Internet connection
- API keys (OpenRouter + OpenAI)

### Environment Variables
```bash
OPENROUTER_API_KEY  # Required
OPENAI_API_KEY      # Required
```

### Git Integration
- Each email committed separately as generated
- Commit format: `feat: Generate email for [Company Name]`
- Final commit: `feat: Complete 15 supplier sponsorship emails`
- Easy to track progress in git log

---

## 💰 Cost Estimate

| Service | Model | Cost | Purpose |
|---------|-------|------|---------|
| OpenRouter | Gemini 2.0 Flash | $0 | Email generation |
| OpenAI | GPT-4o-mini | ~$0.15 | Quality validation |
| **TOTAL** | | **~$0.15** | Complete system |

---

## 🐛 Troubleshooting

### "API key not set"
```bash
export OPENROUTER_API_KEY='your_key_here'
export OPENAI_API_KEY='your_key_here'
```

### "Validation score too low"
The system auto-regenerates (up to 3 attempts). If still failing, check:
- Is supplier data complete?
- Are there placeholder fields in JSON?

### "Git commit failed"
Ensure git is configured:
```bash
git config user.name "Miles"
git config user.email "miles27.85shah@nau.edu"
```

---

## 📞 Contact

**Miles**  
Civil Engineering '27  
Northern Arizona University  
miles27.85shah@nau.edu  
(928) 254-9179

---

## 🏆 Competition Info

**Event**: ASCE Pacific Southwest Conference 2026  
**Project**: Concrete Canoe  
**Challenge**: Build lightweight, strong concrete canoe  
**Materials Deadline**: February 11, 2026 (7 DAYS!)

---

**Let's get those donations! 🚣**
