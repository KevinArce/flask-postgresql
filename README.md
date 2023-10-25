# Flask PostgreSQL Backend

This is a Flask backend project that connects to a PostgreSQL database. It provides API endpoints to retrieve cumulative data. 

## Prerequisites

Before you begin, make sure you have the following prerequisites installed on your system:

- [Python](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [pip](https://pip.pypa.io/en/stable/installing/)

## Setup

1. Clone this repository to your local machine:

   ```shell
   git clone https://github.com/KevinArce/flask-postgresql.git
   cd flask-postgresql
   ```

2. Create a virtual environment for the project. You can use the built-in venv module in Python:

   ```shell
   python -m virtualenv .
   .\scripts\activate
   ```
3. Install the project dependencies:

   ```shell
   pip install -r requirements.txt
   ```
4. Create a .env file in the root directory of the project and add the following environment variables:

   ```shell
   DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
   ```

5. Run the backend server:

   ```shell
   flask run
   ```

6. Endpoints, you'll see a Postman Collection with the endpoints in the root directory of the project:

7. Shutdown the server:

   ```shell
   CTRL + C
   ```

8. Deactivate the virtual environment:

   ```shell
    .\scripts\deactivate
    ```
