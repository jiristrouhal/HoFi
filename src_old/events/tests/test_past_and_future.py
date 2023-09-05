import sys
sys.path.insert(1,"src")


import unittest
import src.events.past_and_future as pf
from src.events.past_and_future import DismissedEvent


from datetime import date, timedelta


class Test_Setting_History_State(unittest.TestCase):

    def setUp(self) -> None:
        self.today = date.today()

    def test_events_created_in_the_past_are_considered_already_realized(self):
        yesterday = self.today - timedelta(days=1)
        event = pf.Event(date=yesterday)
        self.assertTrue(event.realized)

    def test_events_created_today_are_considered_already_realized(self):
        event = pf.Event(date=self.today)
        self.assertTrue(event.realized)

    def test_event_created_for_tomorrow_is_condireder_to_be_planned(self):
        tomorrow = self.today + timedelta(days=1)
        event = pf.Event(date=tomorrow)
        self.assertFalse(event.realized)
        self.assertTrue(event.planned)


class Test_Event_Realization_Confirmation(unittest.TestCase):

    def setUp(self) -> None:
        self.today = date.today()
        def today(): return self.today
        tomorrow = self.today + timedelta(days=1)
        self.event = pf.Event(date=tomorrow, _reference_date=today)
        self.today += timedelta(days=1)

    def test_event_created_for_tomorrow_will_require_confirmation_tomorrow(self):
        self.assertTrue(self.event.confirmation_required)

    def test_confirming_event_was_realized(self):
        self.event.confirm_realization()
        self.assertTrue(self.event.realized)
        self.assertFalse(self.event.planned)
        self.assertFalse(self.event.confirmation_required)
        #repeated confirmation should not occur, thus raise an exception, if it does so
        self.assertRaises(pf.AlreadyRealized, self.event.confirm_realization)

    def test_confirming_past_raises_error(self):
        yesterday = self.today - timedelta(days=1)
        some_realized_event = pf.Event(date=yesterday)
        self.assertFalse(some_realized_event.confirmation_required)
        self.assertRaises(pf.AlreadyRealized, some_realized_event.confirm_realization)

    def test_confirming_dismissed_event_raises_error(self):
        self.event.dismiss()
        self.assertRaises(pf.AlreadyDismissed, self.event.confirm_realization)
    
    def test_confirming_event_not_requiring_confirmation_raises_error(self):
        tomorrow = self.today + timedelta(days=1)
        future_event = pf.Event(date=tomorrow)
        self.assertFalse(future_event.confirmation_required)
        self.assertRaises(pf.ConfirmationNotRequired, future_event.confirm_realization)

    def test_dismissing_event(self):
        self.event.dismiss()

        self.assertTrue(self.event.dismissed)
        self.assertFalse(self.event.realized)
        self.assertFalse(self.event.planned)
        self.assertFalse(self.event.confirmation_required)
        #repeated dismissal should not occur, thus raise an exception, if it does so
        self.assertRaises(pf.AlreadyDismissed, self.event.dismiss)

    def test_dismissing_realized_event_raises_error(self):
        yesterday = self.today - timedelta(days=1)
        some_realized_event = pf.Event(date=yesterday)
        self.assertRaises(pf.AlreadyRealized, some_realized_event.dismiss)

    def test_dismissing_future_event_is_allowed(self):
        tomorrow = self.today+timedelta(days=1)
        some_event = pf.Event(date=tomorrow)
        self.assertTrue(some_event.planned)
        some_event.dismiss()
        self.assertTrue(some_event.dismissed)
        self.assertFalse(some_event.planned)

    def test_dismissed_event_cannot_be_confirmed(self):
        self.event.dismiss()
        self.assertTrue(self.event.dismissed)
        self.assertFalse(self.event.realized)
        self.assertFalse(self.event.planned)
        self.assertFalse(self.event.confirmation_required)
        #repeated dismissal should not occur, thus raise an exception, if it does so
        self.assertRaises(pf.AlreadyDismissed, self.event.dismiss)

    def test_running_action_on_dismissal(self):
        self.x = 0
        self.y = 0
        def action(): self.x += 1
        def other(): self.y += 5

        self.event.add_action('dismissed','owner', action)
        # repeatedly adding action under the same owner name is not allowed
        with self.assertRaises(KeyError):
            self.event.add_action('dismissed', 'owner', action)
        self.event.add_action('dismissed','other_owner', other)

        self.event.dismiss()
        self.assertEqual(self.x,1)
        self.assertEqual(self.y,5)

    def test_running_action_on_confirmation(self):
        self.x = 0
        self.y = 0
        def action(): self.x += 1
        def other(): self.y += 5

        self.event.add_action('confirmed','owner', action)
        # repeatedly adding action under the same owner name is not allowed
        with self.assertRaises(KeyError):
            self.event.add_action('confirmed', 'owner', action)
        self.event.add_action('confirmed','other_owner', other)

        self.event.confirm_realization()
        self.assertEqual(self.x,1)
        self.assertEqual(self.y,5)

    def test_trying_to_run_action_on_an_unknown_event_raises_key_error(self):
        def action(): pass
        self.assertRaises(KeyError, self.event.add_action,'nonexistent_event_type', 'owner', action)


class Test_Adding_Event_To_Event_Manager(unittest.TestCase):

    def setUp(self) -> None:
        self.manager = pf.Event_Manager()
        self.today = date.today()

    def test_adding_realized_event_to_manager(self):
        yesterday = self.today - timedelta(days=1)
        event = pf.Event(date=yesterday)
        self.manager.add(event)
        self.assertTrue(event in self.manager.realized)
        self.assertFalse(event in self.manager.planned)

    def test_adding_planned_event_to_manager(self):
        tomorrow = self.today+timedelta(days=1)
        event = pf.Event(date=tomorrow)
        self.manager.add(event)
        self.assertTrue(event in self.manager.planned)
        self.assertFalse(event in self.manager.realized)

    def test_adding_dismissed_event_to_manager_raises_error(self):
        tomorrow = self.today+timedelta(days=1)
        event = pf.Event(date=tomorrow, _reference_date=lambda: self.today)
        self.assertTrue(event.planned)
        event.dismiss()
        self.assertTrue(event.dismissed)
        with self.assertRaises(DismissedEvent):
            self.manager.add(event)


class Test_Event_Informing_The_Event_Manager(unittest.TestCase):

    def setUp(self) -> None:
        self.today = date.today()
        def today(): return self.today
        self.manager = pf.Event_Manager()
        tomorrow = self.today + timedelta(days=1)
        self.event = pf.Event(date=tomorrow, _reference_date=today)
        self.manager.add(self.event)
        self.today += timedelta(3)

    def test_confirming_event_realization_moves_it_in_the_manager_from_planned_to_realized(self):
        self.event.confirm_realization()
        self.assertTrue(self.event in self.manager.realized)
        self.assertFalse(self.event in self.manager.planned)

    def test_dismissing_event_removes_it_from_planned_events(self):
        self.event.dismiss()
        self.assertFalse(self.event in self.manager.realized)
        self.assertFalse(self.event in self.manager.planned)


class Test_Event_Manager_Inspecting_Its_Events(unittest.TestCase):

    def test_manager_can_report_events_requiring_realization_confirmation(self):
        manager = pf.Event_Manager()
        self.today = date.today()
        def today(): return self.today

        day_1 = self.today + timedelta(days=1)
        day_2 = self.today + timedelta(days=2)
        day_3 = self.today + timedelta(days=3)
        day_4 = self.today + timedelta(days=4)

        event_A = pf.Event(day_1, today)
        event_B = pf.Event(day_2, today)
        event_C = pf.Event(day_3, today)
        event_D = pf.Event(day_4, today)

        manager.add(event_A)
        manager.add(event_B)
        manager.add(event_C)
        manager.add(event_D)

        self.today += timedelta(3)

        self.assertSetEqual(manager.waiting_for_confirmation, {event_A,event_B,event_C})
        self.assertSetEqual(manager.planned, {event_A,event_B,event_C,event_D})

        self.today += timedelta(1)
        self.assertSetEqual(manager.waiting_for_confirmation, {event_A,event_B,event_C,event_D})


if __name__=="__main__": unittest.main()