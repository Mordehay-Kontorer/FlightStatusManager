import unittest
import json
import os
from src.flight_manager import Flight

from src.routes import app


class FlightEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Flight):
            return {
                'flight_id': obj.flight_id,
                'departure': obj.departure,
                'arrival': obj.arrival,
                'success': obj.success
                }

        return super().default(obj)

class TestFlights(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.FILE_PATH = rf'{os.getcwd()}\tests\csv_files\flights.csv'

    def test_get_flight(self):

        # Test with an existing flight ID
        response = self.app.get('/flight/A12')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['flight_id'], 'A12')
        self.assertEqual(data['departure'], '09:00')
        self.assertEqual(data['arrival'], '13:00')
        self.assertEqual(data['success'], '')

        # Test with a non-existent flight ID
        response = self.app.get('/flight/XYZ')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['ERROR'], 'Flight with ID XYZ not found')


    def test_update_flights(self):

        # Test successful request
        data = [
            Flight("FL001", "09:00", "13:00", ""),
            Flight("FL002", "12:00", "19:00", ""),
            Flight("FL003", "10:00", "13:00", ""),
        ]
        response = self.app.post('/flights', data=json.dumps(data, cls=FlightEncoder), content_type='application/json')
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'CSV file updated successfully', response.data)

        # Test request with empty data
        data = []
        response = self.app.post('/flights', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Request body is empty', response.data)


if __name__ == '__main__':
    unittest.main()