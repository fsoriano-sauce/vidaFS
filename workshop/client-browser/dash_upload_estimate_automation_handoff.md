# DASH Upload Estimate — Automation Handoff

This document compiles the research, wiring analysis, and hand-off protocol for automating the "Upload Estimate" popup in DASH NextGear. 

---

## 1. Using the Prompt

Provide the following prompt to the IDE Agent (or Human Developer) that is tasked with translating your human-sequence for estimate delivery into code. 

### IDE Agent Prompt

```markdown
You possess the documented human sequence for delivering an estimate in DASH NextGear. I need you to translate that human workflow into a highly specific "**Delivery Protocol**" document. This protocol will be handed off to our head developer to implement via browser automation (specifically using Chrome Content Scripts and/or Playwright).

We have established a specific architecture and coding pattern for DASH automation in our `request-extension` repository. DASH is a legacy ASP.NET WebForms application, so our automation must handle dynamic IDs, `__doPostBack` AJAX requests, Telerik controls, and iframe popups carefully.

Your task is to convert every human step you know into a technical Step Definition following the template below.

### Translation Rules:
1. **Selectors over Descriptions:** Whenever a human clicks a button or fills a field, hypothesize the required CSS selectors. Provide an *array* of fallbacks (e.g., `#btnSubmit`, `input[value="Save"]`, `.rgSave`).
2. **Handle Iframes Explicitly:** If a step opens a modal or popup in DASH (like the Upload Estimate window), explicitly define a step to "Switch to Iframe Context" (e.g., `iframe[name*="RadWindow"]`).
3. **Handle Telerik Controls:** If a field uses Telerik (often indicated by `riTextBox` or hidden `_ClientState` fields), specify that the developer must use the Telerik `$find('ElementId').set_value()` API or Playwright's native `.fill()` to bypass client state issues.
4. **Explicit Waits:** Translate human waiting (e.g., "wait for the page to load") into explicit wait conditions (e.g., "Wait for `__doPostBack` to complete," "Wait for network idle," or "Explicit sleep for 3000ms").
5. **No Vague Actions:** Replace "Click the next button" with Action: `Click()` and the corresponding selectors. 

### Format Requirement
Output the entire translated workflow wrapping it in the following markdown structure exactly:

# 📋 Protocol: [Name of the Workflow]

### 1. Pre-requisite State
*Define what must be true before this sequence begins (Target URL, Authentication state, Required Payload Data).*

### 2. Sequence & Actions Definition
*(For every step in your human workflow, generate a block like this:)*

#### Step [X]: [Name of Step]
- **Human Action:** [Brief description of what the human does]
- **Target Element Description:** [What the element is physically]
- **Recommended Selectors:** 
  - `[Selector 1]`
  - `[Selector 2]`
- **Action:** [e.g., `Click()`, `Type("payload")`, `Select("option")`]
- **Underlying Architecture Requirement:** [Any specific DASH quirks like Telerik, Iframes, or Postbacks if applicable. Otherwise "None."]
- **Wait Condition:** [e.g., Wait 3s for iframe to load, Wait for network idle]

### 3. Verification & Validation
*How do we programmatically verify the sequence succeeded without human eyes?*
- **Success Criteria 1:** [e.g., Modal closes]
- **Success Criteria 2:** [e.g., Specific HTTP request fires]
- **Success Criteria 3:** [e.g., DOM element X appears on page Y]

Please execute this translation now based on the human sequence you have documented.
```

---

## 2. Example Structure: Upload Estimate Delivery

When the IDE agent successfully interprets your prompt, it should output a protocol matching the structure below. This is based on examining the target `UploadEstimate.aspx` page inside DASH.

# 📋 Protocol Template Example: "Upload Estimate Delivery"

### 1. Pre-requisite State
*What must be true before this sequence begins?*
- **URL Location:** `https://dash-ngs.net/NextGear/Enterprise/Module/Job/jJobSlideBoard.aspx?JobNumber={number}`
- **Authentication:** User must be logged into DASH.
- **Required Data:** `JobId`, `JobNumber`, File to upload, Scope Note text.

### 2. Sequence & Actions Definition

#### Step 1: Open the Upload Dialog
- **Target Element Description:** The "Upload Estimate" button in the Accounting Information section.
- **Recommended Selectors:** 
  - `img[alt="Upload Estimate"]`
  - `.imgAccountingHeaderStyle`
- **Action:** `Click()`
- **Wait Condition:** Wait 3 seconds for the Iframe popup `RadWindow_Common` to load.

#### Step 2: Switch to Iframe Context
- **Target Element Description:** The popup window containing the form.
- **Recommended Selectors:** `iframe[name*="RadWindow"]`
- **Action:** Switch execution context to `iframe.contentDocument` / `iframe.contentWindow`.

#### Step 3: Input Notes and Description
- **Target Element Description:** Notes and Description text areas.
- **Underlying Architecture Requirement:** These are Telerik RadInput controls. Ensure you use Telerik `$find()` logic if inside the browser, or raw selector `fill()` if using Playwright, to bypass the `_ClientState` hidden fields.
- **Element 1 (Notes):** `#Notes`, `textarea[name="Notes"]`
  - **Action:** `Type("Your structured delivery language here")`
- **Element 2 (Description):** `#TextBox1`, `textarea[name="TextBox1"]`
  - **Action:** `Type("Your structured description here")`

#### Step 4: Submit Protocol
- **Target Element Description:** The "Upload Estimate" submission button inside the iframe.
- **Recommended Selectors:**
  - `#btnUploadEstimate`
  - `input[value="Upload Estimate"]`
- **Action:** `Click()`
- **Wait Condition:** Wait for ASP.NET `__doPostBack` to complete (Wait for network idle or overlay disappearance). This POSTs to `UploadEstimate.aspx`.

### 3. Verification & Validation
- **Success Criteria 1:** The `RadWindow` iframe closes.
- **Success Criteria 2:** Navigating to `https://dash-ngs.net/NextGear/Enterprise/Module/Accounting/jEstimate.aspx?JobId={id}` shows the new estimate record in the `ctl00_ContentPlaceHolder1_gvInvoice_ctl00` grid.
- **Success Criteria 3:** The `Notes` column in that grid matches the payload provided in Step 3.

---

## 3. Underlying Technical Analysis (For the Developer)

The findings below outline exactly how the DASH "Upload Estimate" fields map mechanically, answering where the text goes upon form submission.

**Tested on:** Job 24-0481-REB (JobId: 9807532)  
**Page:** `UploadEstimate.aspx`

### Key Finding

The popup lives inside an **iframe**. The data POSTs to:
```
https://dash-ngs.net/NextGear/Enterprise/Module/Job/UploadEstimate.aspx?JobId=11275202&JobNumber=26-0079-REB&FromNewSlideBoard=true
```

> [!IMPORTANT]
> Both fields populate the **Estimate record** on the Estimates/Accounting grid (`jEstimate.aspx`), **NOT** the job-level Notes tab. 

### Verified Field Mapping

| Upload Estimate Field | Estimates Grid Column |
|---|---|
| `Notes` textarea | **Notes** |
| `TextBox1` textarea | **Description** |

**Estimates Grid URL:** `jEstimate.aspx?JobId={id}&JobNumber={num}`  
**Grid Table ID:** `ctl00_ContentPlaceHolder1_gvInvoice_ctl00`

### Field-Level Detail

**Notes (`id="Notes"`)**
- **DOM Element:** `<textarea id="Notes" name="Notes">`
- **Telerik Wrapper:** `RadTextBox` (via `$find('Notes')`)
- **Client State Field:** `Notes_ClientState` (Syncs validation text + valueAsString)

**Description (`id="TextBox1"`)**
- **DOM Element:** `<textarea id="TextBox1" name="TextBox1">`
- **Telerik Wrapper:** `RadTextBox` (via `$find('TextBox1')`)
- **Client State Field:** `TextBox1_ClientState` 

### Submission Mechanism

1. User clicks **Upload Estimate** button (`btnUploadEstimate`).
2. `ValidateFileType()` validates the attached file.
3. `WebForm_DoPostBackWithOptions()` fires a full form POST submitting all ~70 form fields to `UploadEstimate.aspx`.

### What This Means for Automation

Because it is an iframe, direct `.getElementById()` on the parent page will fail.

```javascript
// 1. Get the iframe
const iframe = document.querySelector('iframe[name*="RadWindow"]');
const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

// 2. Set values via Telerik API (critical for ClientState syncing)
const notesCtrl = iframe.contentWindow.$find('Notes');
notesCtrl.set_value('Your note text here');
```
