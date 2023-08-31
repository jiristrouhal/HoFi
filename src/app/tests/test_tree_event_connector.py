import sys
sys.path.insert(1,"src")


import unittest
import src.app.tree_event_connector as tec
import src.controls.tree_editor as tree_editor
import src.core.tree_templates as tmpl
import src.app.past_and_future as pf
import src.core.tree as treemod


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
            transaction_date.value
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


if __name__=="__main__": # pragma: no cover
    unittest.main()