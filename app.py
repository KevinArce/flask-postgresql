import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request

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

load_dotenv()  # Loads variables from .env file into environment

app = Flask(__name__)
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
