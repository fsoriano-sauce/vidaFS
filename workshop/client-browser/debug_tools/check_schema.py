from google.cloud import bigquery

client = bigquery.Client(project="xano-fivetran-bq")

# Get table schema
table_id = "xano-fivetran-bq.staging_xano.ptl_client"
table = client.get_table(table_id)

print(f"Schema for {table_id}:")
for schema_field in table.schema:
    print(f"  {schema_field.name} ({schema_field.field_type})")




