import csv
from google.cloud import bigquery

def run_query_and_print(project_id, query):
    """Runs a BigQuery query and prints the results."""
    try:
        client = bigquery.Client(project=project_id)
        print(f"Running query on project {project_id}...")
        query_job = client.query(query)  # Make an API request.
        
        rows = query_job.result() # Wait for the job to complete.
        
        # Print header
        print(",".join([field.name for field in rows.schema]))
        # Print rows
        for row in rows:
            print(",".join([str(item) for item in row]))
        
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    project_id = "xano-fivetran-bq"
    
    # Query for Stripe invoices
    stripe_query = """
    SELECT
      id,
      customer_id,
      subscription_id,
      status,
      amount_due,
      amount_paid,
      total,
      subtotal,
      tax,
      due_date,
      period_start,
      period_end,
      created,
      number,
      receipt_number
    FROM
      `xano-fivetran-bq.stripe.invoice`
    WHERE
      EXTRACT(YEAR FROM created) = 2025
      AND EXTRACT(MONTH FROM created) IN (9, 10)
    ORDER BY
      created DESC
    LIMIT 50;
    """
    print("\n--- Stripe Invoices ---")
    run_query_and_print(project_id, stripe_query)

    # Query for QuickBooks invoices
    qbo_query = """
    SELECT
      id,
      customer_id,
      total_amount,
      balance,
      transaction_date,
      due_date,
      doc_number
    FROM
      `xano-fivetran-bq.quickbooks.invoice`
    WHERE
      EXTRACT(YEAR FROM transaction_date) = 2025
      AND EXTRACT(MONTH FROM transaction_date) IN (9, 10)
    ORDER BY
      transaction_date DESC
    LIMIT 50;
    """
    print("\n--- QuickBooks Invoices ---")
    run_query_and_print(project_id, qbo_query)

if __name__ == "__main__":
    main()
