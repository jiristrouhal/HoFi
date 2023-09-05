import sys
sys.path.insert(1,"src")


import unittest
import src.app.tree_event_connector as tec
import src.controls.tree_editor as tree_editor
import src.core.tree_templates as tmpl
import src.events.past_and_future as pf
import src.core.tree as treemod


import datetime


class Test_Creating_Events_When_Creating_New_Tree_Item(unittest.TestCase):

    def setUp(self) -> None:
        self.app_template = tmpl.AppTemplate(locale_code='en_us',name_attr="name")
        self.app_template.add(
            tmpl.NewTemplate("Logbook", {"name":"New Logbook"}, children=("Transaction", "ItemWithoutDateAttribute")),
            tmpl.NewTemplate("Transaction", {"name":"New transaction", "date":"2001-12-25"}, children=()),
            tmpl.NewTemplate("ItemWithoutDateAttribute", {"name":"New item"}, children=()),
        )

        self.editor = tree_editor.TreeEditor(self.app_template)
        self.event_manager = pf.Event_Manager()
        self.connector = tec.TreeEventConnector(self.editor, self.event_manager, "date")
        self.logbook = treemod.Tree("Logbook", "Logbook", self.app_template)
        self.editor.load_tree(self.logbook)

    def test_creating_new_tree_item_with_date_attribute_produces_new_event_in_the_event_manager(self)->None:
        self.logbook.new("Transaction 1", tag="Transaction")
        transaction_date = self.logbook._children[-1].attributes["date"]
        self.assertEqual(len(self.event_manager.realized), 1)
        self.assertEqual(
            self.logbook._children[-1].data["event"].date, 
            transaction_date._value
        )

    def test_dismissing_event_when_item_is_removed(self)->None:
        self.logbook.new("Transaction 1", tag="Transaction")
        self.logbook.remove_child("Transaction 1")
        self.assertSetEqual(self.event_manager.planned, set())
        self.assertSetEqual(self.event_manager.realized, set())

    def test_creating_item_without_date_attribute_does_not_produce_any_event(self)->None:
        self.logbook.new("ItemWithoutDateAttribute", tag="ItemWithoutDateAttribute")
        self.assertSetEqual(self.event_manager.planned, set())
        self.assertSetEqual(self.event_manager.realized, set())

    def test_moving_item_date_further_to_past_just_replaces_the_corresponding_event_with_other_realized_event(self):
        self.logbook.new("RealizedTransaction", tag="Transaction")
        transaction = self.logbook._children[-1]

        old_date = transaction.attributes["date"]._value
        self.assertEqual(len(self.event_manager.realized), 1)
        self.assertSetEqual(self.event_manager.realized, {transaction.data["event"]})
        self.assertEqual(transaction.data["event"].date, old_date)

        transaction.attributes["date"].set(datetime.date.today()-datetime.timedelta(days=2))
        new_date = transaction.attributes["date"]._value

        self.assertEqual(len(self.event_manager.realized), 1)
        self.assertSetEqual(self.event_manager.realized, {transaction.data["event"]})
        self.assertEqual(transaction.data["event"].date, new_date)

    def test_moving_item_date_to_the_future_replaced_realized_event_with_planned_event_and_run_actions(self):
        # create and add an action that will be run when previously confirmed event is moved to future
        self.moved_to_future = False
        def action(): self.moved_to_future=True
        self.connector.add_action('realized_to_planned','x', action)
        
        self.logbook.new("RealizedTransaction", tag="Transaction")
        transaction = self.logbook._children[-1]
        date_attr:treemod.Date_Attr = transaction.attributes["date"]
        date_attr.set_from_date_obj(datetime.date.today()+datetime.timedelta(days=2))

        self.assertEqual(len(self.event_manager.realized), 0)
        self.assertEqual(len(self.event_manager.planned), 1)
        self.assertTrue(transaction.data["event"] in self.event_manager.planned)

        # check the action has been run
        self.assertTrue(self.moved_to_future)

    def test_moving_item_date_from_future_to_present(self):
        # create and add an action that will be run when planned event is moved to present (or past)
        self.moved_to_present = False
        def action(): self.moved_to_present=True
        self.connector.add_action('planned_to_realized','x', action)
        # move the transaction to the future
        self.logbook.new("PlannedTransaction", tag="Transaction")
        transaction = self.logbook._children[-1]
        date_attr:treemod.Date_Attr = transaction.attributes["date"]
        date_attr.set_from_date_obj(datetime.date.today()+datetime.timedelta(days=2))
        self.assertFalse(transaction.data["event"].confirmation_required)

        # move the event to present
        date_attr.set_from_date_obj(datetime.date.today())
        self.assertTrue(transaction.data["event"].confirmation_required)

    def test_moving_item_date_from_future_to_present_when_the_original_event_was_not_yet_confirmed(self):
        # create and add an action that will be run when event is moved in the past
        self.moved_to_present = False
        def action(): self.moved_to_present=True
        self.connector.add_action('planned_to_realized','x', action)
        
        self.logbook.new("PlannedTransaction", tag="Transaction")
        transaction = self.logbook._children[-1]
        transaction.data["event"].consider_as_planned()
        date_attr:treemod.Date_Attr = transaction.attributes["date"]

        self.assertTrue(transaction.data["event"].confirmation_required)

        # move the event further to past
        date_attr.set_from_date_obj(datetime.date.today()-datetime.timedelta(days=5))
        self.assertTrue(transaction.data["event"].confirmation_required)



if __name__=="__main__": # pragma: no cover
    unittest.main()