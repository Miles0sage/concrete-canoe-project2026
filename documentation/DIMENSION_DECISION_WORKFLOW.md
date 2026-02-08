# Hull Dimension Decision Workflow

**Goal:** Pick final hull dimensions (length × beam × depth) and target weight for NAU Canoe 2026.

---

## Step 1: Run Analysis on VPS (Terminal Only)

```bash
# SSH to VPS
ssh user@YOUR_VPS_IP

# Go to project
cd ~/nau-concrete-canoe-2026   # or your clone path
source venv/bin/activate

# Run comparison
python3 scripts/run_hull_analysis.py
```

**Output:** Table of Freeboard, GM, Safety Factor for each variant. All should Pass.

---

## Step 2: Generate Visual Report (for viewing later)

```bash
python3 scripts/generate_visualization.py
```

Creates `reports/figures/report.html` with charts.

---

## Step 3: Download Report to Your Mac

From your **Mac terminal** (not VPS):

```bash
# Download the HTML report
scp user@YOUR_VPS_IP:~/nau-concrete-canoe-2026/reports/figures/report.html ~/Desktop/

# Open in browser
open ~/Desktop/report.html
```

You’ll see bar charts (freeboard, GM, weight vs freeboard) and a comparison table.

---

## Step 4: Use the Results to Decide

| Criterion      | Canoe 1         | Canoe 2         | Canoe 3         |
|----------------|-----------------|-----------------|-----------------|
| Length         | 18'             | 18'             | 16'             |
| Beam           | 30"             | 36"             | 42"             |
| Weight         | 276 lbs         | 300 lbs         | 320 lbs         |

- **Racing / speed:** Smaller beam, lighter → Canoe 1  
- **Stability / endurance:** Wider beam → Canoe 2 or 3  
- **Storage / transport:** Shorter length → Canoe 3  

---

## Step 5: Document and Lock In

1. Record your choice in `documentation/NAU_Hull_Design_Plan_2026.md`  
2. Update `scripts/run_hull_analysis.py` if you add custom variants  
3. Use these dimensions in CAD and mold design  

---

## Optional: Add Custom Variants

Edit `scripts/run_hull_analysis.py` and add to `VARIANTS`:

```python
VARIANTS = [
    ("Canoe 1", 18 * 12, 30, 18, 276),
    ("Canoe 4", 17 * 12, 32, 18, 285),   # Custom
]
```

Re-run the scripts and compare.

---

## Using Qwen on VPS for Analysis Help

If Qwen (or another LLM) is running on your VPS:

```bash
# Example: ask Qwen to suggest variants based on your constraints
ollama run qwen2.5-coder "Given hull length 18ft beam 30in depth 18in weight 276lbs, what beam would give 8in freeboard?"
```

(Requires Ollama + Qwen installed on the VPS.)
