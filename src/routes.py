import logging
from typing import Tuple
import os

from flask import Flask, jsonify, request, Response

from src.flight_manager import FlightService, Flight

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)

UPDATE_CSV_PATH = rf'{os.getcwd()}\csv_files\update.csv'
CSV_PATH = rf'{os.getcwd()}\csv_files\flights.csv'

# Endpoint to get information about a flight
@app.route('/flight/<flight_id>', methods=['GET'])
def get_flight(flight_id: str) -> tuple[Response, Flight]:

    try:
        flight_service = FlightService(CSV_PATH)
        flight = flight_service.get_flight_by_id(flight_id)
        if flight:
            return jsonify(flight.to_dict()), 200
    except FileNotFoundError as e:
        logger.error(str(e))
        return jsonify(
            {
                'ERROR': str(e),
                'Message': 'The file does not exist.'
            }
        ), 500
    except Exception as e:
        logger.error(str(e))
        return jsonify(
            {
                'ERROR': str(e),
                'Message': 'There is an error reading the file.'
            }
        ), 500
    # If the flight is not in the list, return 404 error
    return jsonify({"ERROR": f"Flight with ID {flight_id} not found"}), 404


# Endpoint to update the CSV file with flights
@app.route('/flights', methods=['POST'])
def update_flights() -> Tuple[str, int]:
    """
    This function updates flights in a CSV file with the data provided in the request body.
    The data should be in JSON format and should contain information about flights such as the flight ID,
    arrival, and departure time. The CSV file should have the following columns: flight ID, arrival,
    departure, and success. The function returns a JSON response with a message indicating whether
    the flights were added successfully or not.
    """
    # Read the flights from the request body
    flights_data = request.json
    flights = [Flight(**flight) for flight in flights_data]

    # Check if the request body is empty
    if not flights:
        logger.error('Request body is empty.')
        return jsonify({'ERROR': 'Request body is empty'}), 400
    # Update the flights CSV
    try:
        flight_service = FlightService(UPDATE_CSV_PATH)
        flight_service.update_csv_flights(flights)
    except ValueError as e:
        # Return error response if the data in the request body is not in the expected format
        logger.error(str(e))
        return jsonify(
            {
                'ERROR': str(e),
                'Message': 'Error: Invalid data in request body',
            }
        ), 400
    return jsonify({'message': 'CSV file updated successfully'}), 201



if __name__ == "__main__":
    app.run(debug=True, port=8080)
