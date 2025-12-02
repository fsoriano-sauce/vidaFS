import os
import json
import time
from google.cloud import bigquery
import google.generativeai as genai
from datetime import datetime

# Configuration
API_KEY = "AIzaSyD7PpOBoHEGIiBBqL3Hco43BMeSEnmyVAc"
PROJECT_ID = "xano-fivetran-bq"
DATASET_ID = "slack_wescope"
SOURCE_VIEW = f"{PROJECT_ID}.{DATASET_ID}.rpt_employee_daily_summary"
DEST_TABLE = f"{PROJECT_ID}.{DATASET_ID}.compliance_flags"

# Initialize Clients
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
bq_client = bigquery.Client(project=PROJECT_ID)

def get_compliance_prompt(employee_name, date, transcript):
    return f"""
**ROLE**
You are the **Senior Compliance & Human Capital Analyst** for a corporation.

**OBJECTIVE**
Analyze the provided conversation logs and flag specific exchanges that indicate:
1.  **Explicit Policy Violations:** Harassment, discrimination, fraud, data security breaches.
2.  **Implicit Non-Performance:** Patterns indicating disengagement or refusal to work.
3.  **Toxic Workplace Dynamics:** Bullying, gaslighting, or conflicts.

**CRITICAL INSTRUCTION: REPORTER VS OFFENDER**
*   **Distinguish between a user REPORTING a violation and COMMITTING one.**
*   If {employee_name} says "Bob made a racist joke", DO NOT flag {employee_name} for harassment. Flag it only if {employee_name} is the one making the joke.
*   If {employee_name} is discussing a compliance issue as part of their job (e.g. HR, Legal, Manager), do not flag them unless they are mishandling it.

**INPUT DATA**
Employee: {employee_name}
Date: {date}
Transcript:
{transcript}

**OUTPUT FORMAT**
Return a JSON object with a key "flags" containing a list of objects. If no flags, return empty list.
Example format:
{{
  "flags": [
    {{
      "risk_level": "High",
      "category": "Harassment",
      "quote": "exact text",
      "context": "explanation",
      "confidence_score": 0.95
    }}
  ]
}}

**GUARDRAILS**
*   Ignore harmless banter.
*   Do not flag protected concerted activity (union discussions).
*   Only flag items with >70% confidence unless safety risk.
"""

def run_analysis():
    print("Fetching data from BigQuery...")
    # Ensure we cover the full 90 days
    query = f"""
        SELECT *
        FROM `{SOURCE_VIEW}`
        WHERE activity_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    """
    query_job = bq_client.query(query)
    rows = list(query_job.result())
    print(f"Found {len(rows)} daily records to analyze.")

    flags_to_insert = []

    for i, row in enumerate(rows):
        print(f"[{i+1}/{len(rows)}] Analyzing {row.employee_name} for {row.activity_date}...")
        
        # Rate Limiting: Sleep to avoid 429 errors (15 RPM limit = 4s per request)
        time.sleep(4)
        
        prompt = get_compliance_prompt(row.employee_name, row.activity_date, row.daily_transcript)
        
        try:
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            result = json.loads(response.text)
            
            if "flags" in result and result["flags"]:
                print(f"  -> Found {len(result['flags'])} flags.")
                for flag in result["flags"]:
                    flags_to_insert.append({
                        "flag_id": f"{row.user_id}_{row.activity_date}_{int(time.time())}",
                        "activity_date": row.activity_date.isoformat(),
                        "user_id": row.user_id,
                        "employee_email": row.employee_email,
                        "risk_level": flag.get("risk_level"),
                        "category": flag.get("category"),
                        "quote": flag.get("quote"),
                        "context": flag.get("context"),
                        "confidence_score": flag.get("confidence_score"),
                        "analysis_ts": datetime.utcnow().isoformat()
                    })
            else:
                print("  -> No flags found.")
                
        except Exception as e:
            print(f"  -> Error analyzing row: {e}")
            # Continue to next row
            continue

    if flags_to_insert:
        print(f"Inserting {len(flags_to_insert)} flags into BigQuery...")
        errors = bq_client.insert_rows_json(DEST_TABLE, flags_to_insert)
        if errors:
            print(f"Encountered errors while inserting rows: {errors}")
        else:
            print("Successfully inserted flags.")
    else:
        print("No flags to insert.")

if __name__ == "__main__":
    run_analysis()
