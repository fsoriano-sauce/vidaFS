from google.cloud import bigquery
import os

client = bigquery.Client(project="xano-fivetran-bq")

query = """
    SELECT
        id,
        full_name,
        subscription_id,
        child,
        isparent
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client`
    WHERE
        full_name LIKE '%BMS CAT - Milwaukee%'
"""

results = client.query(query).result()

print(f"{'ID':<5} | {'Client':<30} | {'Sub ID':<10} | {'Child':<5} | {'Parent':<5}")
print("-" * 80)
for row in results:
    print(f"{row.id:<5} | {row.full_name[:30]:<30} | {str(row.subscription_id):<10} | {str(row.child):<5} | {str(row.isparent):<5}")






