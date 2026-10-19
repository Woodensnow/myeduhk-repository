"""Meeting scheduling boundaries and state consistency."""
import copy
import unittest
from problem4 import MeetingRoom

class TestMeetingRoom(unittest.TestCase):
    def setUp(self):
        self.room = MeetingRoom('Conference-A', 10)

    def assert_schedule(self, ids, hours, slots):
        self.assertEqual([b['booking_id'] for b in self.room.bookings], ids)
        self.assertEqual(self.room.total_hours_booked, hours)
        self.assertEqual(self.room.get_utilization_rate(), round(hours / 10, 2))
        self.assertEqual(self.room.get_free_slots(), slots)

    def test_initial_state_multi_attributes(self):
        self.assertEqual(self.room.room_id, 'Conference-A')
        self.assertEqual(self.room.capacity, 10)
        self.assertFalse(self.room.is_maintenance)
        self.assert_schedule([], 0, [(8, 18)])

    def test_single_booking_multi_attributes(self):
        self.assertTrue(self.room.book('B01', 'Planning', 10, 12, 5))
        self.assertEqual(self.room.bookings[0], dict(
            booking_id='B01', title='Planning', start_time=10, end_time=12, attendees=5))
        self.assert_schedule(['B01'], 2, [(8, 10), (12, 18)])

    def test_back_to_back_meetings_allowed(self):
        self.room.book('B01', 'First', 9, 10, 10)
        self.assertTrue(self.room.book('B02', 'Next', 10, 12, 5))
        self.assertTrue(self.room.book('B00', 'Earlier', 8, 9, 1))
        self.assert_schedule(['B00', 'B01', 'B02'], 4, [(12, 18)])

    def test_overlapping_booking_rejected(self):
        self.room.book('B01', 'Existing', 9, 12, 5)
        before = copy.deepcopy(self.room.__dict__)
        for start, end in ((8, 10), (10, 13), (10, 11), (8, 13), (9, 12)):
            with self.subTest(start=start, end=end):
                with self.assertRaises(ValueError):
                    self.room.book('new', 'Conflict', start, end, 1)
                self.assertEqual(self.room.__dict__, before)
        self.assert_schedule(['B01'], 3, [(8, 9), (12, 18)])

    def test_cancel_booking_updates_all_attributes(self):
        self.room.book('B02', 'Later', 14, 16, 5)
        self.room.book('B01', 'Earlier', 9, 11, 5)
        self.assert_schedule(['B01', 'B02'], 4, [(8, 9), (11, 14), (16, 18)])
        self.assertTrue(self.room.cancel('B01'))
        self.assert_schedule(['B02'], 2, [(8, 14), (16, 18)])
        self.room.cancel('B02')
        self.assert_schedule([], 0, [(8, 18)])

    def test_capacity_and_validation_exceptions(self):
        for capacity in (0, -1):
            with self.assertRaises(ValueError):
                MeetingRoom('bad', capacity)
        for start, end, attendees in ((-1, 2, 1), (10, 10, 1), (11, 10, 1),
                                      (9, 10, 0), (9, 10, -1), (9, 10, 11)):
            with self.assertRaises(ValueError):
                self.room.book('bad', 'Invalid', start, end, attendees)
            self.assert_schedule([], 0, [(8, 18)])
        self.room.book('B01', 'Valid', 9, 10, 10)
        before = copy.deepcopy(self.room.__dict__)
        with self.assertRaises(ValueError):
            self.room.book('B01', 'Duplicate', 12, 13, 1)
        with self.assertRaises(KeyError):
            self.room.cancel('missing')
        self.assertEqual(self.room.__dict__, before)
        self.room.is_maintenance = True
        with self.assertRaises(RuntimeError):
            self.room.book('B02', 'Maintenance', 12, 13, 1)
        self.assertTrue(self.room.is_maintenance)
        self.assert_schedule(['B01'], 1, [(8, 9), (10, 18)])
        for start, end in ((8, 8), (18, 8)):
            with self.assertRaises(ValueError):
                self.room.get_free_slots(start, end)
        for hours in (0, -1):
            with self.assertRaises(ValueError):
                self.room.get_utilization_rate(hours)

    def test_free_slots_clip_bookings_to_requested_window(self):
        for bid, start, end in (('early', 0, 2), ('left', 6, 9),
                                ('right', 17, 20), ('late', 21, 23)):
            self.room.book(bid, bid, start, end, 1)
        self.assert_schedule(['early', 'left', 'right', 'late'], 10, [(9, 17)])
        self.assertEqual(self.room.get_free_slots(10, 12), [(10, 12)])
        self.assertEqual(self.room.get_free_slots(7, 8), [])
        self.assertEqual(self.room.get_utilization_rate(20), 0.5)

if __name__ == '__main__':
    unittest.main()
