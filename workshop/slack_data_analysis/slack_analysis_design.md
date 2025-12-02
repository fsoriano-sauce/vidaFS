# Slack Conversation Analysis Design

## Goal
Create a BigQuery dataset/view to organize Slack conversations by employee for the last 3 months, enabling downstream AI analysis to flag potential issues.

## Data Source
- **Source**: Slack API via Fivetran.
- **Destination**: BigQuery.

## Assumed Fivetran Schema
Based on standard Fivetran Slack schemas, we expect the following core tables:

1.  **`users`**
    *   `id` (STRING): Slack User ID (e.g., `U0123456`).
    *   `name` (STRING): Username.
    *   `real_name` (STRING): Full name.
    *   `email` (STRING): Email address.
    *   `is_bot` (BOOLEAN): Filter out bots.
    *   `deleted` (BOOLEAN): Filter out deleted users (optional).

2.  **`channels`** (or `conversations`)
    *   `id` (STRING): Channel ID.
    *   `name` (STRING): Channel name.
    *   `is_private` (BOOLEAN): To distinguish public/private channels.

3.  **`messages`**
    *   `ts` (TIMESTAMP/STRING): Message timestamp (unique ID).
    *   `user_id` (STRING): Foreign key to `users`.
    *   `channel_id` (STRING): Foreign key to `channels`.
    *   `text` (STRING): The message content.
    *   `thread_ts` (STRING): Parent message timestamp (if part of a thread).

## Proposed Data Model

We need to organize data "by employee". This can be interpreted in two ways for AI analysis:
1.  **Employee Output**: What the employee wrote.
2.  **Employee Context**: The conversations the employee participated in (including what others said to them).

For "flagging potential problems" (e.g., HR, compliance, sentiment), **Context** is usually critical. However, to start simple, we will build a foundation that allows both.

### 1. Base View: `stg_recent_employee_messages`
*Filters for the last 3 months and enriches messages with user/channel details.*

```sql
SELECT
  m.ts AS message_ts,
  m.channel_id,
  c.name AS channel_name,
  m.user_id,
  u.real_name AS employee_name,
  u.email AS employee_email,
  m.text AS message_text,
  m.thread_ts,
  -- Determine if this is a thread start or reply
  COALESCE(m.thread_ts, m.ts) AS conversation_root_id
FROM `source_dataset.messages` m
JOIN `source_dataset.users` u ON m.user_id = u.id
LEFT JOIN `source_dataset.channels` c ON m.channel_id = c.id
WHERE
  -- Filter for last 3 months
  CAST(TIMESTAMP_SECONDS(CAST(m.ts AS INT64)) AS DATE) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
  AND u.is_bot IS FALSE
```

### 2. AI Analysis View: `rpt_employee_daily_summary`
*Aggregates messages by employee and day to create "documents" for the AI to process. This reduces the number of API calls to the LLM.*

```sql
SELECT
  DATE(TIMESTAMP_SECONDS(CAST(ts AS INT64))) AS activity_date,
  user_id,
  employee_name,
  employee_email,
  -- Concatenate all messages for the day into a single text block for analysis
  STRING_AGG(
    FORMAT("On %s in #%s: %s", FORMAT_TIMESTAMP("%H:%M", TIMESTAMP_SECONDS(CAST(ts AS INT64))), channel_name, message_text),
    "\n" ORDER BY ts
  ) AS daily_transcript
FROM `stg_recent_employee_messages`
GROUP BY 1, 2, 3, 4
```

## AI Prompt Preparation (Preview)
When we run this against the AI, the prompt structure would look like:

> **Context**: You are analyzing the communication history of employee {employee_name}.
> **Data**: The following is a transcript of their messages from {activity_date}:
> {daily_transcript}
> **Task**: Identify any messages that indicate [potential problem criteria, e.g., conflict, security risk, burnout].

## Next Steps
1.  Confirm the exact dataset name in BigQuery.
2.  Create the `stg_recent_employee_messages` view.
3.  Create the `rpt_employee_daily_summary` table/view.
