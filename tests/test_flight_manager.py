import os
import unittest
from datetime import datetime, timedelta

from src.flight_manager import Flight, FlightService


class TestFlight(unittest.TestCase):

    def test_duration(self):
        flight = Flight("AC123", datetime(2022, 1, 1, 8, 0), datetime(2022, 1, 1, 10, 0), "SUCCESS")
        self.assertEqual(flight.duration, timedelta(hours=2))

    def test_repr(self):
        flight = Flight("AC123", datetime(2022, 1, 1, 8, 0), datetime(2022, 1, 1, 10, 0), "SUCCESS")
        self.assertEqual(str(flight), "<Flight AC123: 2022-01-01 08:00:00 to 2022-01-01 10:00:00>")


class TestFlightService(unittest.TestCase):
    def setUp(self):
        self.TEST_PATH = os.getcwd()
        self.flight_service = FlightService(rf'{self.TEST_PATH}\csv_files\flights.csv')
        self.invalid_csv_path = rf"{self.TEST_PATH}\csv_files\invalid_csv.csv"
        self.invalid_flight_id_csv_path = rf"{self.TEST_PATH}\csv_files\invalid_flight_id_format.csv"
        self.non_existent_csv_path = rf"{self.TEST_PATH}\csv_files\non_existent.csv"
        self.empty_file_path = rf"{self.TEST_PATH}\csv_files\empty_file.csv"
        self.txt_file_path = rf"{self.TEST_PATH}\csv_files\txt_file.txt"
        self.more_then_20_path = rf"{self.TEST_PATH}\csv_files\more_than_20_success.csv"
        self.updated_flights = rf"{self.TEST_PATH}\csv_files\updated_flights.csv"

    def test_get_flights(self):
        flights = self.flight_service.get_flights()
        self.assertEqual(len(flights), 23)
        self.assertEqual(flights[0].flight_id, "A12")
        self.assertEqual(flights[0].departure.strftime('%H:%M'), '09:00')
        self.assertEqual(flights[0].arrival.strftime('%H:%M'), '13:00')
        self.assertEqual(flights[0].success, "")
        self.assertEqual(flights[-1].flight_id, "C235")
        self.assertEqual(flights[-1].departure.strftime('%H:%M'), '08:00')
        self.assertEqual(flights[-1].arrival.strftime('%H:%M'), '22:00')
        self.assertEqual(flights[-1].success, "")

    def test_produce_success_flights(self):
        flights = self.flight_service.produce_success_flights()
        self.assertEqual(len(flights), 23)
        self.assertEqual(flights[0].success, "success")
        self.assertEqual(flights[-1].success, "success")

    def test_produce_more_then_20_success_flights(self):
        self.flight_service.csv_path = self.more_then_20_path
        flights = self.flight_service.produce_success_flights()
        self.assertEqual(len(flights), 31)
        self.assertEqual(flights[0].success, "success")
        self.assertEqual(flights[-1].success, "fail")
        self.assertEqual(flights[-2].success, "fail")
        self.assertEqual(flights[-3].success, "fail")

    def test_get_flights_invalid_csv(self):
        # check invalid format - such an extra column
        self.flight_service.csv_path = self.invalid_csv_path
        with self.assertRaises(ValueError):
            flights = self.flight_service.get_flights()

    def test_get_flights_empty_field_csv(self):
        # check invalid format - such an empty field column
        self.flight_service.csv_path = self.invalid_flight_id_csv_path
        flights = self.flight_service.get_flights()
        self.assertEqual(len(flights), 1)

    def test_get_flights_empty_file(self):
        self.flight_service.csv_path = self.empty_file_path
        with self.assertRaises(StopIteration):
            flights = self.flight_service.get_flights()

    def test_get_flights_file_not_found(self):
        self.flight_service.csv_path = self.non_existent_csv_path
        with self.assertRaises(FileNotFoundError):
            flights = self.flight_service.get_flights()

    def test_get_txt_file(self):
        self.flight_service.csv_path = self.txt_file_path
        with self.assertRaises(ValueError):
            flights = self.flight_service.get_flights()

    def test_get_flight_by_id(self):
        # existing flight
        flight_id = 'A12'
        flight = self.flight_service.get_flight_by_id(flight_id)
        self.assertEqual(flight.departure.strftime('%H:%M'), '09:00')
        self.assertEqual(flight.arrival.strftime('%H:%M'), '13:00')

        # non existing flight
        flight_id = 'NON_EXIST_ID'
        flight = self.flight_service.get_flight_by_id(flight_id)
        self.assertEqual(flight, None)

    def test_update_csv_flights(self):
        self.flight_service.csv_path = self.updated_flights
        update_test_flights = [
            Flight("FL001", "09:00", "13:00", ""),
            Flight("FL002", "12:00", "19:00", ""),
            Flight("FL003", "10:00", "13:00", ""),
        ]
        self.flight_service.update_csv_flights(update_test_flights)
        # Remove the created files
        os.remove(self.updated_flights)
