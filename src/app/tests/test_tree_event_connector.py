import sys
sys.path.insert(1,"src")


import unittest
import src.app.tree_event_connector as tec
import src.controls.tree_editor as tree_editor
import src.core.tree_templates as tmpl
import src.app.past_and_future as pf
import src.core.tree as treemod


class Test_Creating_Events_When_Creating_New_Tree_Item(unittest.TestCase):

    def test_creating_new_tree_item_with_date_attribute_produces_new_event_in_the_event_manager(self)->None:
        app_template = tmpl.AppTemplate(locale_code='en_us',name_attr="name")
        app_template.add(
            tmpl.NewTemplate("Logbook", {"name":"New Logbook"}, children=("Transaction",)),
            tmpl.NewTemplate("Transaction", {"name":"New transaction", "date":"2001-12-25"}, children=()),
        )

        editor = tree_editor.TreeEditor(app_template)
        event_manager = pf.Event_Manager()

        connector = tec.TreeEventConnector(editor, event_manager, ("date",))

        logbook = treemod.Tree("Logbook", "Logbook", app_template)
        editor.load_tree(logbook)

        logbook.new("Transaction 1", tag="Transaction")
        transaction_date = logbook._children[-1].attributes["date"]

        self.assertEqual(len(event_manager.realized), 1)


if __name__=="__main__":
    unittest.main()