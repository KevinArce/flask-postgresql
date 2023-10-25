import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS

CUMULATIVE_WEEKLY_COUNTS = """SELECT
    EXTRACT(WEEK FROM MIN(c.date)) AS week,
    COUNT(DISTINCT ci.company_id) AS cumulative_count
FROM conversations c
JOIN company_identifiers ci ON c.account_id = ci.account_identifier
WHERE c.successful = true
AND c.date >= '2023-02-01'
AND c.date <= '2023-08-31'
GROUP BY EXTRACT(WEEK FROM c.date)
ORDER BY week;
"""

PERCENTAGE_OF_SUCESSFUL_COMPANIES_OVER_TIME = """SELECT 
  recent.month, 
  COUNT(CASE WHEN recent.total_conversations > 1500 THEN 1 END) * 100.0 / COUNT(*) as success_percentage
FROM 
  (
    SELECT 
      comp.id, 
      DATE_TRUNC('month', conv.date) as month, 
      SUM(conv.total) as total_conversations
    FROM 
      public.company comp
      JOIN public.company_identifiers ci ON comp.id = ci.company_id
      JOIN public.conversations conv ON ci.account_identifier = conv.account_id
    WHERE 
      conv.successful = TRUE AND
      comp.close_date BETWEEN '2023-01-01' AND '2023-08-31' -- Adjust this date range
    GROUP BY 
      comp.id, DATE_TRUNC('month', conv.date)
  ) AS recent 
GROUP BY 
  recent.month
ORDER BY 
  recent.month;
"""

COMPANIES_CLOSED_PER_MONTH = """WITH cohort_data AS (
  SELECT
    c.id AS company_id,
    DATE_TRUNC('month', c.close_date) AS cohort_month,
    ci.stripe_company_ids AS stripe_id
  FROM
    public.company c
    JOIN public.company_identifiers ci ON c.id = ci.company_id
),
invoice_data AS (
  SELECT
    si.company_id AS stripe_id,
    DATE_TRUNC('month', si.sent_date) AS invoice_month,
    si.amount
  FROM
    public.stripe_invoice si
),
cohort_revenue AS (
  SELECT
    cd.cohort_month,
    id.invoice_month,
    SUM(id.amount) AS revenue
  FROM
    cohort_data cd
    JOIN invoice_data id ON cd.stripe_id = id.stripe_id
  GROUP BY
    cd.cohort_month, id.invoice_month
)
SELECT
  cr.cohort_month,
  cr.invoice_month,
  cr.revenue
FROM
  cohort_revenue cr
ORDER BY
  cr.cohort_month, cr.invoice_month;
"""

load_dotenv()  # Loads variables from .env file into environment

app = Flask(__name__)
CORS(app)
url = os.environ.get("DATABASE_URL")  # Gets variables from environment
connection = psycopg2.connect(url)


@app.get("/")
def index():
    return "Hello, Daniel!"


@app.get("/api/cumulative")
def get_cumulative():
    # Create a new connection for this request
    new_connection = psycopg2.connect(url)

    try:
        with new_connection:
            with new_connection.cursor() as cursor:
                cursor.execute(CUMULATIVE_WEEKLY_COUNTS)
                result = cursor.fetchall()

        # Format the data into the desired format
        formatted_data = []
        for row in result:
            week, cumulative_count = row
            formatted_data.append(
                {
                    "Week": week,
                    "Cumulative Count": cumulative_count,
                }
            )

        return {"lineChartData": formatted_data}
    finally:
        # Close the connection after the request is processed
        new_connection.close()

@app.get("/api/success")
def get_success():
    # Create a new connection for this request
    new_connection = psycopg2.connect(url)

    try:
        with new_connection:
            with new_connection.cursor() as cursor:
                cursor.execute(PERCENTAGE_OF_SUCESSFUL_COMPANIES_OVER_TIME)
                result = cursor.fetchall()

        # Format the data into the desired format
        formatted_data = []
        for row in result:
            month, success_percentage = row
            # Convert month to a string with only the month and year
            formatted_month = month.strftime("%b, %Y")
            # Round the success percentage to 2 decimal places
            rounded_percentage = round(success_percentage, 2)
            formatted_data.append(
                {
                    "Month": formatted_month,
                    "Success Percentage": rounded_percentage,
                }
            )

        return {"lineChartData2": formatted_data}
    finally:
        # Close the connection after the request is processed
        new_connection.close()

@app.get("/api/stackedBarChartData")
def get_stackedBarChartData():
    # Create a new connection for this request
    new_connection = psycopg2.connect(url)

    try:
        with new_connection:
            with new_connection.cursor() as cursor:
                cursor.execute(COMPANIES_CLOSED_PER_MONTH)
                result = cursor.fetchall()

        # Format the data into the desired format
        formatted_data = []
        for row in result:
            cohort_month, invoice_month, revenue = row
            # Convert month to a string with only the month and year
            formatted_cohort_month = cohort_month.strftime("%b, %Y")
            formatted_invoice_month = invoice_month.strftime("%b, %Y")
            formatted_data.append(
                {
                    "Month": formatted_cohort_month,
                    "Invoice Month": formatted_invoice_month,
                    "Revenue": revenue,
                }
            )

        return {"stackedBarChartData": formatted_data}
    finally:
        # Close the connection after the request is processed
        new_connection.close()

