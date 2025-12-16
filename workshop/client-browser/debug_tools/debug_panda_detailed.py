from google.cloud import bigquery
import os

# Copying logic from client_browser_setup.py
BQ_QUERY = """
    SELECT
        c.full_name as client_name,
        COALESCE(NULLIF(l.custom_link, ''), sa.link) as login_url,
        sa.name as system_name,
        c.key_and_pro_account as is_key_account,
        c.subscription_id,
        s.subscription_name,
        l.api_key
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l ON c.id = l.client_id
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access` sa ON l.system_access_id = sa.id
    LEFT JOIN
        `xano-fivetran-bq.staging_xano.ptl_subscription` s ON c.subscription_id = s.id
    WHERE
        c.full_name LIKE '%Panda%'
        AND l._fivetran_deleted = false
        AND sa._fivetran_deleted = false
"""

client = bigquery.Client(project="xano-fivetran-bq")
results = client.query(BQ_QUERY).result()

print(f"{'Client':<20} | {'System':<20} | {'URL':<40} | {'API Key':<10}")
print("-" * 100)

for row in results:
    url = str(row.login_url)[:40]
    api_key = str(row.api_key)
    
    # Logic check
    status = "Included"
    if row.api_key:
        is_symbility = "symbility" in str(row.login_url).lower()
        if not is_symbility:
            status = "Excluded (API Key)"
            
    print(f"{row.client_name[:20]:<20} | {row.system_name[:20]:<20} | {url:<40} | {api_key:<10} | {status}")


