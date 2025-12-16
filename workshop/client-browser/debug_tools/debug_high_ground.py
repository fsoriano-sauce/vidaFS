from google.cloud import bigquery
import os

client = bigquery.Client(project="xano-fivetran-bq")

query = """
    SELECT
        c.id,
        c.full_name,
        c.suspended,
        c._fivetran_deleted as client_deleted,
        c.subscription_id,
        sa.name as system_name,
        sa.link,
        l.custom_link
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    LEFT JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l
    ON
        c.id = l.client_id
    LEFT JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access` sa
    ON
        l.system_access_id = sa.id
    WHERE
        LOWER(c.full_name) LIKE '%high%' OR LOWER(c.full_name) LIKE '%ground%'
"""

results = client.query(query).result()

print(f"{'ID':<5} | {'Client':<30} | {'Sub':<5} | {'System':<20} | {'Link':<40}")
print("-" * 100)
for row in results:
    link = str(row.custom_link if row.custom_link else row.link)[:40]
    print(f"{row.id:<5} | {row.full_name[:30]:<30} | {str(row.subscription_id):<5} | {str(row.system_name)[:20]:<20} | {link:<40}")


