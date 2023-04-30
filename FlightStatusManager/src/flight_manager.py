import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

MAX_SUCCESS_COUNT = 20
TOTAL_MINUTES = 180
HEADER_SIZE = 4

class Flight:
    """
    Flight class represents a flight with its unique identifier, departure and arrival times, and its success status.

    Attributes:
    flight_id (str): A string that represents the unique identifier of the flight.
    departure (datetime): A datetime object that represents the departure time of the flight.
    arrival (datetime): A datetime object that represents the arrival time of the flight.
    success (str): A string that represents the success status of the flight, either "success" or "fail".

    Methods:
    - repr(self): Returns a string that represents the Flight object.
    - duration(self) -> timedelta: Returns a timedelta object that represents the duration of the flight.
    """
    def __init__(self, flight_id: str, departure: datetime, arrival: datetime, success: str):
        self.flight_id = flight_id
        self.departure = departure
        self.arrival = arrival
        self.success = success

    def to_dict(self):
        return {
            'flight_id': self.flight_id,
            'departure': self.departure.strftime("%H:%M"),
            'arrival': self.arrival.strftime("%H:%M"),
            'success': ""
        }
    def __repr__(self):
        return f"<Flight {self.flight_id}: {self.departure} to {self.arrival}>"

    @property
    def duration(self) -> timedelta:
        return self.arrival - self.departure

class FlightService:
    """
    FlightService - A class to handle flight data stored in a CSV file.

    Attributes:
    csv_path (str): The path to the CSV file that contains the flight data.

    Methods:
    - get_flights(): Retrieves all flights information from the CSV file and returns a sorted list of Flight objects.
    - produce_success_flights(): Analyzes the flight data stored in the CSV file and produces a list of flight dictionaries,
    with a new "success" key indicating whether each flight is a success or failure.
    - get_flight_by_id(flight_id: str): Returns a Flight object with a matching flight_id if it exists within the list of successful
    flights produced by calling produce_success_flights. If no matching flight_id is found, the method returns None.
    - update_csv_flights(flights: List[Flight]): Updates the CSV file with the provided list of Flight objects.
    """
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def get_flights(self) -> List[Flight]:
        """
        Retrieves all flights information from the CSV file.

        Returns:
            A list of Flight objects representing all flights in the CSV file, sorted by arrival time.
        """
        flights = []

        try:
            if os.path.splitext(self.csv_path)[1] != '.csv':
                raise ValueError(f"Invalid CSV format: File {self.csv_path} is not a CSV file")
            with open(self.csv_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                try:
                    header = next(reader)
                except StopIteration:
                    # handle empty file or missing header row
                    raise StopIteration("File is empty or missing header row")
                if len(header) != HEADER_SIZE or not header == ['Flight ID', 'Departure', 'Arrival', 'Success']:
                    raise ValueError("Invalid CSV format: The header should have 4 columns.\n"
                                     "The header should be in this format: ['Flight ID', 'Departure', 'Arrival', 'Success']")
                for idx, row in enumerate(reader):
                    flight_id, departure, arrival, success = row

                    if not flight_id or not departure or not arrival:
                        print(f'Invalid CSV format in line {idx} row {row}: \n'
                              f'Flight ID, Departure, and Arrival cannot be empty.')
                        continue
                    try:
                        departure_time = datetime.strptime(departure, "%H:%M")
                        arrival_time = datetime.strptime(arrival, "%H:%M")
                    except ValueError as e:
                        print(f'Invalid CSV format in line {idx} row {row}: '
                              'departure and arrival times should be in the format HH:MM')
                        continue
                    # Add flight to list
                    flights.append(Flight(flight_id, departure_time, arrival_time, success))
        except FileNotFoundError as e:
            print(f"File Not Found: The {self.csv_path} does not exist.")
            raise FileNotFoundError(f"File Not Found: The {self.csv_path} does not exist.")
        except ValueError as e:
            print(e)
            raise e
        except StopIteration as e:
            print(e)
            raise e
        except Exception as e:
            print(f"Unexpected ERROR: {e}")
            raise e
        flights.sort(key=lambda flight: flight.arrival)
        return flights

    def produce_success_flights(self) -> List[Dict[str, Any]]:
        """
        Analyzes the flight data stored in the CSV file and produces a list of flight dictionaries,
        with a new "success" key indicating whether each flight is a success or failure based on
        the criteria(no more than 20 success happens in a day and the difference between the
        arrival and departure is greater or equal than 180 minutes).

        Returns:
            A list of dictionaries representing each flight in the CSV file, with an additional
            "success" key indicating whether the flight is a success or failure.
        """
        flights = self.get_flights()
        count = 0
        for flight in sorted(flights, key=lambda f: f.arrival):
            if flight.duration >= timedelta(minutes=180) and count < 20:
                flight.success = "success"
                count += 1
            else:
                flight.success = "fail"
        return flights

    def get_flight_by_id(self, flight_id: str) -> Optional[Flight]:
        """
        Returns a `Flight` object with a matching `flight_id` if it exists within the list of successful flights produced by
        calling `produce_success_flights`. If no matching `flight_id` is found, the method returns `None`.

        Args:
        - flight_id (str): The ID of the flight to be returned

        Returns:
        - A `Flight` object if a matching `flight_id` is found, `None` otherwise
        """
        flights = self.produce_success_flights()
        for flight in flights:
            if flight.flight_id == flight_id:
                return flight
        return None

    def update_csv_flights(self, flights: List[Flight]) -> None:
        """
        Updates a CSV file with flight information.

        Args:
        flights (List[Flight]): A list of Flight objects to be written to the CSV file.

        Raises:
        TypeError: If the flights argument is not a list.
        ValueError: If any element of the flights list is not a Flight object.
        Exception: If there is an error updating the CSV file.

        Returns: None
        """
        if not isinstance(flights, list):
            raise TypeError("Flights must be a list")
        try:
            with open(self.csv_path, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Flight ID", "Departure", "Arrival", "Success"])
                for flight in flights:
                    if not isinstance(flight, Flight):
                        print("All elements of input list must be Flight objects.")
                        continue
                    writer.writerow(
                        [flight.flight_id, flight.departure, flight.arrival, flight.success]
                    )
        except Exception as e:
            print(f'Error updating CSV file: {e}')
        print(f'CSV file updated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')