# PythonAnywhere MySQL Setup Guide

The error "Can't connect to MySQL server on 'localhost'" appears because PythonAnywhere requires specific database connection settings. Follow these steps to configure your database correctly:

## 1. Set Up a MySQL Database on PythonAnywhere

1. Log in to your PythonAnywhere account
2. Go to the Databases tab
3. Set a MySQL password if you haven't already
4. Note your database details:
   - Username: `mattan` (your PythonAnywhere username)
   - Database name: `mattan$blocks_game` (note the $ symbol is required)
   - Host: `mattan.mysql.pythonanywhere-services.com`

## 2. Update Environment Variables

1. Go to the Web tab in PythonAnywhere
2. Scroll down to "Environment variables"
3. Add the following variable:
   - Name: `DATABASE_URL`
   - Value: `mysql+pymysql://mattan:YourPassword@mattan.mysql.pythonanywhere-services.com/mattan$blocks_game`
   
   (Replace `YourPassword` with your actual MySQL password)

## 3. Create Required Tables

You can run the test script to verify the database connection and create tables:

1. Upload the `test_db_connection_pythonanywhere.py` file to your PythonAnywhere site
2. Edit the file to include your actual MySQL password
3. Run the script from the PythonAnywhere bash console:
   ```
   python test_db_connection_pythonanywhere.py
   ```

## 4. Restart Your Web App

1. Go to the Web tab
2. Click the "Reload" button next to your web app

Once these steps are completed, the database functionality (Save to DB and Load from DB) should work correctly.

## Troubleshooting

If you still experience issues:

1. Check MySQL error logs in the Databases tab
2. Verify your connection string format is correct
3. Make sure you've installed all required packages:
   ```
   pip install sqlalchemy pymysql
   ```
4. Test the connection with a simple script to isolate any issues 