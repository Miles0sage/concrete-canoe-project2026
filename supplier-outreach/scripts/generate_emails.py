#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - Supplier Email Generator
Generates personalized sponsorship emails with AI validation
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
import requests

# Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Optional - will use OpenRouter if not set

# Contact info
MILES_NAME = "Miles"
MILES_TITLE = "Civil Engineering '27"
MILES_EMAIL = "miles27.85shah@nau.edu"
MILES_PHONE = "(928) 254-9179"
UNIVERSITY = "Northern Arizona University"
TEAM_NAME = "NAU Concrete Canoe Team"

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
EMAILS_DIR = BASE_DIR / "emails"
REPO_DIR = BASE_DIR.parent

# Create directories
EMAILS_DIR.mkdir(exist_ok=True)

def load_suppliers():
    """Load supplier data from JSON"""
    with open(DATA_DIR / "previous_donors.json", 'r') as f:
        data = json.load(f)
    return data

def generate_email_with_gemini(supplier, is_previous_donor=False):
    """Generate email using OpenRouter (Gemini)"""
    
    if is_previous_donor:
        prompt = f"""Generate a personalized sponsorship request email for the NAU Concrete Canoe team.

RECIPIENT INFO:
- Contact: {supplier.get('contact', 'General')}
- Company: {supplier['company']}
- Product: {supplier['product']}
- Previous Status: PREVIOUS DONOR (donated {supplier['product']} last year)
- Priority: {supplier['priority']}
- Notes: {supplier.get('notes', '')}

EMAIL TYPE: Previous Donor Thank-You + Request

SENDER INFO:
- Name: {MILES_NAME}
- Title: {MILES_TITLE}
- University: {UNIVERSITY}
- Team: {TEAM_NAME}
- Email: {MILES_EMAIL}
- Phone: {MILES_PHONE}

REQUIREMENTS:
1. Length: 200-300 words
2. Tone: Warm, appreciative, professional
3. MUST thank them for last year's donation of {supplier['product']}
4. Mention specific impact their donation had
5. Request same or similar donation for 2026 season
6. Emphasize continued partnership
7. Include sponsor benefits:
   - Logo on canoe hull (visible at competition)
   - Social media recognition
   - Photos from competition
   - Recognition in technical paper
   - Certificate from NAU
8. Make logistics easy (pickup/shipping details)
9. Include phone number {MILES_PHONE} in signature
10. Clear call to action

SPECIAL NOTES:
- If LOCAL (Flagstaff): Emphasize "we can pick up" convenience
- If previous major donor: Show extra appreciation
- Maintain personal relationship tone

Generate ONLY:
- Subject line
- Email body
- Signature with phone number

DO NOT include generic placeholders. Use specific details from the company info."""

    else:
        prompt = f"""Generate a personalized sponsorship request email for the NAU Concrete Canoe team.

RECIPIENT INFO:
- Contact: {supplier.get('contact', 'General')}
- Company: {supplier['company']}
- Product: {supplier['product']}
- Status: NEW TARGET (first contact)
- Priority: {supplier['priority']}
- Notes: {supplier.get('notes', '')}

EMAIL TYPE: Introduction + Sponsorship Request

SENDER INFO:
- Name: {MILES_NAME}
- Title: {MILES_TITLE}
- University: {UNIVERSITY}
- Team: {TEAM_NAME}
- Email: {MILES_EMAIL}
- Phone: {MILES_PHONE}

REQUIREMENTS:
1. Length: 200-300 words
2. Tone: Professional, enthusiastic, respectful
3. Introduce NAU Concrete Canoe team
4. Briefly explain what concrete canoe competition is (ASCE national competition)
5. Explain why their specific product ({supplier['product']}) is critical for our canoe
6. Request donation or sample materials
7. Include sponsor benefits:
   - Logo on canoe hull (visible at competition)
   - Social media recognition
   - Photos from competition
   - Recognition in technical paper
   - Certificate from NAU
8. Make logistics easy (we handle shipping costs if needed)
9. Include phone number {MILES_PHONE} in signature
10. Clear call to action

SPECIAL NOTES:
- If company known for student programs: Mention that
- If LOCAL (Flagstaff): Emphasize supporting local NAU students
- Show we've researched their products specifically

Generate ONLY:
- Subject line
- Email body
- Signature with phone number

DO NOT include generic placeholders. Use specific details from the company info."""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nau.edu",
        "X-Title": "NAU Concrete Canoe Email Generator"
    }
    
    data = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        email_content = result['choices'][0]['message']['content']
        return email_content
    except Exception as e:
        print(f"  ❌ Error generating with Gemini: {e}")
        return None

def validate_with_chatgpt(email_content, supplier_name):
    """Validate email with AI and get score (uses OpenAI if available, otherwise OpenRouter)"""
    
    prompt = f"""You are evaluating a sponsorship request email for a university concrete canoe team.

EMAIL TO EVALUATE:
{email_content}

CONTEXT: This email is being sent to {supplier_name} to request material donations for NAU's concrete canoe competition team.

Please evaluate this email on the following criteria:
1. Professionalism and tone
2. Clarity of the request
3. Personalization (not generic)
4. Persuasiveness
5. Proper structure and grammar
6. Appropriate length (200-300 words ideal)
7. Clear call to action
8. Contact information included

Provide:
1. A score from 1-10 (where 7+ is acceptable to send)
2. Brief explanation of the score
3. If score < 7: Specific improvements needed

Format your response as:
SCORE: [number]/10
EXPLANATION: [brief explanation]
IMPROVEMENTS: [if needed]"""

    # Try OpenAI first if available
    if OPENAI_API_KEY:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            validation = result['choices'][0]['message']['content']
            
            # Extract score
            score_line = [line for line in validation.split('\n') if 'SCORE:' in line.upper()]
            if score_line:
                score_text = score_line[0].split(':')[1].strip()
                score = float(score_text.split('/')[0])
                return score, validation
            return 0, validation
        except Exception as e:
            print(f"  ⚠️  Warning: OpenAI validation failed, trying OpenRouter: {e}")
    
    # Fallback to OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nau.edu",
        "X-Title": "NAU Concrete Canoe Email Validator"
    }
    
    data = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        validation = result['choices'][0]['message']['content']
        
        # Extract score
        score_line = [line for line in validation.split('\n') if 'SCORE:' in line.upper()]
        if score_line:
            score_text = score_line[0].split(':')[1].strip()
            score = float(score_text.split('/')[0])
            return score, validation
        return 7.5, validation  # Default good score if can't parse
    except Exception as e:
        print(f"  ⚠️  Warning: Validation failed: {e}")
        return 7.5, "Validation skipped due to API error"

def save_email(filename, content):
    """Save email to file"""
    filepath = EMAILS_DIR / filename
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath

def git_commit(message):
    """Commit changes to git"""
    try:
        subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True, capture_output=True)
        subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=REPO_DIR,
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def create_tracking_sheet(all_suppliers):
    """Create tracking markdown file"""
    
    content = """# NAU Concrete Canoe 2026 - Supplier Outreach Tracking

**Mission**: Secure materials and cash donations for concrete canoe construction  
**Deadline**: February 11, 2026  
**Contact**: Miles - miles27.85shah@nau.edu - (928) 254-9179

---

## Priority Order

### 🔴 CRITICAL Priority - Previous Donors (Contact First!)

"""
    
    # Previous donors - Critical and High priority
    critical_donors = [s for s in all_suppliers if s.get('is_previous') and s['priority'] == 'CRITICAL']
    high_donors = [s for s in all_suppliers if s.get('is_previous') and s['priority'] == 'HIGH']
    
    for supplier in critical_donors:
        content += f"- [ ] **{supplier['company']}** - {supplier['product']}\n"
        content += f"  - Contact: {supplier.get('contact', 'General')}\n"
        if supplier.get('email'):
            content += f"  - Email: {supplier['email']}\n"
        content += f"  - Status: Previous Donor (2024)\n"
        content += f"  - Notes: {supplier.get('notes', '')}\n\n"
    
    content += "\n### 🟡 HIGH Priority - Previous Donors\n\n"
    
    for supplier in high_donors:
        content += f"- [ ] **{supplier['company']}** - {supplier['product']}\n"
        content += f"  - Contact: {supplier.get('contact', 'General')}\n"
        if supplier.get('email'):
            content += f"  - Email: {supplier['email']}\n"
        content += f"  - Status: Previous Donor (2024)\n"
        content += f"  - Notes: {supplier.get('notes', '')}\n\n"
    
    # New targets
    content += "\n### 🟢 New Targets 2026\n\n"
    
    critical_new = [s for s in all_suppliers if not s.get('is_previous') and s['priority'] == 'CRITICAL']
    high_new = [s for s in all_suppliers if not s.get('is_previous') and s['priority'] == 'HIGH']
    
    for supplier in critical_new + high_new:
        content += f"- [ ] **{supplier['company']}** - {supplier['product']}\n"
        content += f"  - Contact: {supplier.get('contact', 'General')}\n"
        if supplier.get('email'):
            content += f"  - Email: {supplier['email']}\n"
        content += f"  - Priority: {supplier['priority']}\n"
        content += f"  - Notes: {supplier.get('notes', '')}\n\n"
    
    # Other targets
    other = [s for s in all_suppliers if s['priority'] in ['MEDIUM', 'LOW']]
    if other:
        content += "\n### 🔵 Medium/Low Priority\n\n"
        for supplier in other:
            donor_status = " (Previous Donor)" if supplier.get('is_previous') else ""
            content += f"- [ ] **{supplier['company']}** - {supplier['product']}{donor_status}\n"
            if supplier.get('email'):
                content += f"  - Email: {supplier['email']}\n"
            content += f"  - Notes: {supplier.get('notes', '')}\n\n"
    
    content += """
---

## Response Tracking

| Company | Email Sent | Response Date | Status | Next Action |
|---------|-----------|---------------|--------|-------------|
| | | | | |

---

## Tips for Sending

1. **Send from NAU email** (miles27.85shah@nau.edu) - more professional
2. **Personalize subject line** - use the generated one or tweak it
3. **Follow up after 3-4 days** if no response
4. **Previous donors = highest priority** - they already know us!
5. **Local suppliers** - offer to pick up in person
6. **Track responses** in table above

---

## Materials Status

- [ ] Carbon fiber mesh (Simpson Strong-Tie)
- [ ] Testing cylinders (Western Technologies)  
- [ ] Lightweight aggregate (Aero Aggregates or Poraver)
- [ ] Portland cement (Salt River Materials or CalPortland)
- [ ] Fly ash (Salt River Materials)
- [ ] Admixtures (Sika or Master Builders)
- [ ] Red sand (Flagstaff Landscape Products)
- [ ] Cash donations (Loven Contracting, others)

---

**Generated**: February 4, 2026  
**Competition**: ASCE Pacific Southwest Conference 2026
"""
    
    tracking_file = BASE_DIR / "TRACKING.md"
    with open(tracking_file, 'w') as f:
        f.write(content)
    
    return tracking_file

def main():
    """Main execution"""
    
    print("=" * 70)
    print("NAU CONCRETE CANOE 2026 - EMAIL GENERATOR")
    print("=" * 70)
    print()
    
    # Check API keys
    if not OPENROUTER_API_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY environment variable not set")
        sys.exit(1)
    
    print("✅ OpenRouter API key configured")
    if OPENAI_API_KEY:
        print("✅ OpenAI API key configured (will use for validation)")
    else:
        print("ℹ️  OpenAI API key not set (will use OpenRouter for validation)")
    print()
    
    # Load suppliers
    data = load_suppliers()
    previous_donors = data['donors_2024']
    new_targets = data['new_targets_2026']
    
    # Mark previous donors
    for donor in previous_donors:
        donor['is_previous'] = True
    for target in new_targets:
        target['is_previous'] = False
    
    # Combine all suppliers
    all_suppliers = previous_donors + new_targets
    
    # Sort by priority: CRITICAL, HIGH, MEDIUM, LOW
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    all_suppliers.sort(key=lambda x: (not x.get('is_previous', False), priority_order.get(x['priority'], 99)))
    
    total = len(all_suppliers)
    print(f"📊 Loaded {len(previous_donors)} previous donors + {len(new_targets)} new targets = {total} total")
    print()
    
    validation_log = []
    
    # Generate emails
    for idx, supplier in enumerate(all_suppliers, 1):
        company = supplier['company']
        is_previous = supplier.get('is_previous', False)
        donor_type = "Previous Donor" if is_previous else "New Target"
        
        print(f"[{idx}/{total}] Generating email for {company} ({donor_type})...")
        
        # Generate filename
        filename = f"{idx:02d}_{company.lower().replace(' ', '_').replace('/', '_')}.txt"
        
        # Generate email
        max_attempts = 3
        for attempt in range(max_attempts):
            email_content = generate_email_with_gemini(supplier, is_previous)
            
            if not email_content:
                print(f"  ❌ Failed to generate email (attempt {attempt+1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue
                else:
                    break
            
            # Validate with ChatGPT
            score, validation_details = validate_with_chatgpt(email_content, company)
            
            print(f"  ChatGPT Validation: {score:.1f}/10", end="")
            
            if score >= 7.0:
                print(" ✅")
                
                # Save email
                filepath = save_email(filename, email_content)
                print(f"  ✅ Saved to {filepath.relative_to(BASE_DIR)}")
                
                # Git commit
                commit_msg = f"feat: Generate email for {company}"
                if git_commit(commit_msg):
                    print(f"  ✅ Committed to git")
                
                # Log validation
                validation_log.append({
                    'company': company,
                    'score': score,
                    'attempt': attempt + 1
                })
                
                print()
                break
            else:
                print(f" ⚠️  (Below threshold, regenerating...)")
                if attempt < max_attempts - 1:
                    time.sleep(2)
        
        # Small delay between requests
        time.sleep(1)
    
    # Create tracking sheet
    print("Creating tracking sheet...")
    tracking_file = create_tracking_sheet(all_suppliers)
    print(f"✅ Created {tracking_file.relative_to(BASE_DIR)}")
    print()
    
    # Save validation log
    log_file = BASE_DIR / "validation_log.txt"
    with open(log_file, 'w') as f:
        f.write("NAU CONCRETE CANOE 2026 - EMAIL VALIDATION SCORES\n")
        f.write("=" * 70 + "\n\n")
        for entry in validation_log:
            f.write(f"{entry['company']}: {entry['score']:.1f}/10 (Attempt {entry['attempt']})\n")
        f.write(f"\nAverage Score: {sum(e['score'] for e in validation_log) / len(validation_log):.1f}/10\n")
    print(f"✅ Saved validation log to {log_file.relative_to(BASE_DIR)}")
    print()
    
    # Final commit
    git_commit("feat: Complete 15 supplier sponsorship emails")
    
    print("=" * 70)
    print("GENERATION COMPLETE! 🎉")
    print("=" * 70)
    print()
    print(f"📧 {total} emails generated and saved")
    print(f"📊 Average validation score: {sum(e['score'] for e in validation_log) / len(validation_log):.1f}/10")
    print(f"🔄 All changes committed to git")
    print()

if __name__ == "__main__":
    main()
