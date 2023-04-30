# Flight Success Manager

## Description:
##### 
This is a simple Flask application with two endpoints: GET /flight/<flight_id> and POST /flights.

The GET /flight/<flight_id> endpoint takes a flight_id parameter in the URL and returns the flight information associated with that ID from a CSV file named flights.csv. If the flight is not found, it returns a 404 error.

The POST /flights endpoint expects a JSON payload in the request body with one or more flights to be added to the CSV file. It writes the flights to the CSV file and returns a success message with a 201 status code.

The CSV file should have columns with the following field names: 'flight ID', 'Arrival', 'Departure', 'success'.

Note that this code assumes the CSV file already exists and is located in the same directory. Also, it is using the csv module to read and write CSV files.
