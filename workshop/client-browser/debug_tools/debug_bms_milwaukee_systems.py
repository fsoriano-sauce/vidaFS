from google.cloud import bigquery
import os

client = bigquery.Client(project="xano-fivetran-bq")

query = """
    SELECT
        c.full_name,
        sa.name as system_name,
        sa.link,
        l._fivetran_deleted as login_deleted,
        sa._fivetran_deleted as system_deleted,
        c.suspended,
        c._fivetran_deleted as client_deleted
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    LEFT JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l ON c.id = l.client_id
    LEFT JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access` sa ON l.system_access_id = sa.id
    WHERE
        c.id = 457
"""

results = client.query(query).result()

print(f"{'Client':<25} | {'System':<20} | {'Link':<30} | {'L Del':<5} | {'S Del':<5} | {'Susp':<5}")
print("-" * 100)
for row in results:
    link = str(row.link)[:30]
    print(f"{row.full_name[:25]:<25} | {str(row.system_name)[:20]:<20} | {link:<30} | {str(row.login_deleted):<5} | {str(row.system_deleted):<5} | {str(row.suspended):<5}")




