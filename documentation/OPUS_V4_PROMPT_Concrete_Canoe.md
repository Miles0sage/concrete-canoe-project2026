# OPUS V4 Prompt – NAU Concrete Canoe 2026

Use this prompt with Opus/Claude for AI-assisted hull and project planning.

---

## System Context

You are assisting the NAU Concrete Canoe 2026 team. Key constraints:

- **Competition:** ASCE ISWS, April 16–18, 2026  
- **Target hull:** 18' × 30" × 18", ~276 lbs  
- **Design phase:** Dimension finalization, hydrostatics, Op 4.6 evaluation  

## Available Data

- `calculations/concrete_canoe_calculator.py` – hydrostatics, stability, structural analysis  
- `data/spreadsheets/` – mixture design and reinforcement Excel files  
- `documentation/NAU_Hull_Design_Plan_2026.md` – design plan  
- `documentation/Hull_Design_Evaluation_Action_Plan.docx` – action items  

## Request Format

When asking Opus for help, include:

1. **Task:** e.g., "Compare Canoe 1 vs Canoe 2 stability"
2. **Constraints:** weight, freeboard, ASCE limits
3. **Output:** table, recommendations, code changes

## Example Prompts

- "Run hull analysis for 17' × 32" × 18" at 290 lbs and compare to Canoe 1"
- "Summarize ASCE 2026 mix design limits from our compliance checker"
- "Generate action items for Op 4.6 dimension finalization"
