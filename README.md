# Padel Court Demand Analyzer in Playtomic

## Description

This project aims to analyze the demand for padel courts in clubs on the Playtomic platform. It uses Selenium to automate the collection of data regarding court availability, storing the information in a PostgreSQL database.

## Requirements

Before running the project, ensure you have the following components installed:

- Python 3.x
- PostgreSQL
- Chrome and ChromeDriver (compatible with the installed version of Chrome)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your_username/padel-court-demand-analyzer.git
   cd padel-court-demand-analyzer

2. **Clone the repository**:

    Install the necessary dependencies: Make sure you have selenium and psycopg2 installed. You can install them using pip:

    ```bash
    pip install selenium psycopg2

2. **Set up the database**:

    Create a PostgreSQL database named demanda_padel, and ensure you have the necessary tables (Club, pista, and Disponibilidad) configured according to your needs:

    ```bash
    pip install selenium psycopg2

## Usage

1. **Configure the Script**:
   - Adjust the path to `chromedriver` in the Python script. Locate the line:
     ```python
     chrome_driver_path = "C:\\chromedriver\\chromedriver.exe"
     ```
     Change it to the correct path where your `chromedriver.exe` is located.

   - Configure the database connection parameters in the script. Update the following values with your PostgreSQL credentials:
     ```python
     conn = psycopg2.connect(
         dbname='demanda_padel',
         user='your_username',
         password='your_password',
         host='localhost',
         port='5432'
     )
     ```

2. **Run the Script**:
   - Open your terminal or command prompt.
   - Navigate to the directory where the script is located.
   - Execute the script with the following command:
     ```bash
     python script.py
     ```
   - The script will start collecting data on court availability for the next 15 days for each club defined in your database. The results will be logged and stored in the PostgreSQL database.

3. **Check Logs**:
   - Logs of the script's execution will be stored in the `logs` directory specified in the script. Each log file will have a timestamp in its filename.
   - Review the log files to monitor the data collection process and any issues that may arise.

4. **Verify Database Entries**:
   - After running the script, check your PostgreSQL database to ensure that the availability data has been correctly inserted into the `Disponibilidad` table.
