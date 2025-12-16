from google.cloud import bigquery
import os

client = bigquery.Client(project="xano-fivetran-bq")

query = """
    SELECT
        c.full_name,
        c.subscription_id
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    WHERE
        c.full_name LIKE '%Panda%'
"""

results = client.query(query).result()

for row in results:
    print(f"Client: {row.full_name}, Subscription ID: {row.subscription_id}")


