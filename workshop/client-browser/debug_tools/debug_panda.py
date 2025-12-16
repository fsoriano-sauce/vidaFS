from google.cloud import bigquery
import os

client = bigquery.Client(project="xano-fivetran-bq")

query = """
    SELECT
        c.full_name,
        sa.name as system_name,
        sa.link,
        l.custom_link,
        l.api_key,
        l._fivetran_deleted,
        sa._fivetran_deleted as system_deleted
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l ON c.id = l.client_id
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access` sa ON l.system_access_id = sa.id
    WHERE
        c.full_name LIKE '%Panda%'
"""

results = client.query(query).result()

print(f"{'Client':<20} | {'System':<20} | {'Link':<40} | {'API Key':<10} | {'Deleted'}")
print("-" * 110)
for row in results:
    link = str(row.link)[:40]
    api_key = "YES" if row.api_key else "NO"
    deleted = f"L:{row._fivetran_deleted} S:{row.system_deleted}"
    print(f"{row.full_name[:20]:<20} | {row.system_name[:20]:<20} | {link:<40} | {api_key:<10} | {deleted}")


