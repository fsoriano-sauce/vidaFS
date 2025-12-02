# Sample Analysis & Proposed Workflow

## 1. Sample Analysis Result
**Employee:** Logan Deyo
**Date:** 2025-11-05
**Transcript:**
> On 16:59 in #client-cancellations: Construemax shows canceled, so I would assume canceled. Phillip Edward canceled, and then opted not to cancel, so David reactivated.
> On 19:36 in #client-cancellations: They'll also post here automatically moving forward FYI. I reactivated same time I added you, Olivia.

**AI Analysis Output:**
> **No Flags Detected.**
> *   **Context:** Employee is discussing client account status and system updates with colleagues.
> *   **Tone:** Professional and informative.

---

## 2. Proposed Workflow for Full Analysis

To analyze the entire 3-month history for all employees, we recommend the following automated workflow:

### Step 1: Data Extraction
Use the `rpt_employee_daily_summary` view to fetch daily transcripts.
```sql
SELECT * FROM `slack_wescope.rpt_employee_daily_summary`
WHERE activity_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) -- Process weekly batches
```

### Step 2: AI Processing (Python Script)
We can create a Python script that:
1.  Iterates through each row of the query result.
2.  Constructs a prompt using the **Compliance Analyst** template.
3.  Sends the prompt to an LLM API (e.g., OpenAI GPT-4 or Vertex AI).
4.  Parses the JSON response to extract flags.

### Step 3: Reporting
Store the flagged results in a new BigQuery table `slack_wescope.compliance_flags` for review by HR/Compliance.

### Requirements
To proceed with building this automation, we need:
1.  **LLM API Access:** An API key or credentials for the preferred LLM provider.
2.  **Approval:** Confirmation to create the Python script and the results table.
