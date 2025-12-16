from google.cloud import bigquery
import os

client = bigquery.Client(project="xano-fivetran-bq")

query = """
    SELECT
        c.full_name,
        sa.link
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l ON c.id = l.client_id
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access` sa ON l.system_access_id = sa.id
    WHERE
        sa.link LIKE '%xactimate.com%'
"""

results = client.query(query).result()

print(f"{'Client':<30} | {'Link':<50}")
print("-" * 80)
for row in results:
    print(f"{row.full_name[:30]:<30} | {row.link[:50]:<50}")


