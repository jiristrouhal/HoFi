import sys

sys.path.insert(1, "src")


import src.app.set_templates as st
from src.events.past_and_future import Event
from datetime import date, timedelta
import unittest


class Test_Getting_Transaction_State(unittest.TestCase):

    def test_last_status_is_realized_and_event_is_in_future(self):
        last_status:st._Status_Label = 'realized'
        future_event = Event(date=date.today()+timedelta(days=1))
        self.assertEqual(st._updated_status(last_status, future_event), 'planned')

    def test_last_status_is_realized_and_event_is_realized(self):
        last_status:st._Status_Label = 'realized'
        realized_event = Event(date=date.today()-timedelta(days=1))
        self.assertEqual(st._updated_status(last_status, realized_event), 'realized')

    def test_last_status_is_realized_and_event_requires_confirmation(self):
        last_status:st._Status_Label = 'realized'
        planned_event = Event(date=date.today()-timedelta(days=1))
        planned_event.consider_as_planned()
        self.assertEqual(st._updated_status(last_status, planned_event), 'requires_confirmation')


    def test_last_status_is_requires_confirmation_and_event_is_in_future(self):
        last_status:st._Status_Label = 'requires_confirmation'
        planned_event = Event(date=date.today()+timedelta(days=1))
        self.assertEqual(st._updated_status(last_status, planned_event), 'planned')

    def test_last_status_is_requires_confirmation_and_event_is_realized(self):
        last_status:st._Status_Label = 'requires_confirmation'
        realized_event = Event(date=date.today()-timedelta(days=1))
        self.assertEqual(st._updated_status(last_status, realized_event), 'requires_confirmation')

    def test_last_status_is_requires_confirmation_and_event_requires_confirmation(self):
        last_status:st._Status_Label = 'requires_confirmation'
        event = Event(date=date.today()-timedelta(days=1))
        event.consider_as_planned()
        self.assertEqual(st._updated_status(last_status, event), 'requires_confirmation')


    def test_last_status_is_planned_and_event_is_planned(self):
        last_status:st._Status_Label = 'planned'
        planned_event = Event(date=date.today()+timedelta(days=1))
        self.assertEqual(st._updated_status(last_status, planned_event), 'planned')

    def test_last_status_is_planned_and_event_requires_confirmation(self):
        last_status:st._Status_Label = 'planned'
        event = Event(date=date.today()-timedelta(days=1))
        event.consider_as_planned()
        self.assertEqual(st._updated_status(last_status, event), 'requires_confirmation')

    def test_last_status_is_planned_and_event_is_realized(self):
        realized_event = Event(date=date.today()-timedelta(days=1))
        self.assertEqual(
            st._updated_status(last_status='planned',event=realized_event), 
        'requires_confirmation')





if __name__=="__main__": unittest.main()