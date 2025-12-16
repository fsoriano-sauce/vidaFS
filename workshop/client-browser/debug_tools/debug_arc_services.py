from google.cloud import bigquery
import os

client = bigquery.Client(project="xano-fivetran-bq")

query = """
    SELECT
        c.full_name,
        sa.name as system_name,
        sa.link,
        l.custom_link
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l ON c.id = l.client_id
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access` sa ON l.system_access_id = sa.id
    WHERE
        c.full_name LIKE '%ARC Services%'
        AND l._fivetran_deleted = false
        AND sa._fivetran_deleted = false
"""

results = client.query(query).result()

print(f"{'Client':<20} | {'System':<20} | {'Link':<40} | {'Custom':<40}")
print("-" * 120)
for row in results:
    link = str(row.link)[:40]
    custom = str(row.custom_link)[:40] if row.custom_link else "None"
    print(f"{row.full_name[:20]:<20} | {row.system_name[:20]:<20} | {link:<40} | {custom:<40}")


