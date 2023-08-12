# Treeview and XML connection

The xml structure is completely dictated by the application.
No schema is required. The initially created schema is used only as an auxiliary tool for defining the rules inside the app. 

## Displaying the XML content
The user opens the app and reads the file. The tree is displayed immediatelly. 

![Domain model](./out/uml/uml/domain_model.svg)


The structure for holding the displayed data loaded from xml looks like this

![Class diagram](./out/uml/uml/class_diagram.svg)


## Editing the tree object and its children

### Reporting errors
For example, when attempting to delete branch with some child branches, the branch should be left intact and the program should print an error message.

The rule of not deleting branch with child branches should be maintained by the branch itself.

The branch should basically call some methods for printing out the error message. The branch does not store the printed message neither take care of the particular content (the content is set by the displaying object).

The called methods are provided by the displayer/displayers. 


# The app
The app comprises the xml file handling and managing the tree object indirectly via UI. 

A GUI for the tree management (aside from the treeview) is created. 

The app defines the tree elements' templates (the tags and attributes) and passes them to the tree objects via the UI part responsible for the tree editing (Treeview).

Trees cannot be loaded or unloaded via the Treeview - it can only serve for their editing. That is the job for the TreeManager, which vice versa cannot modify the trees, it only enables to handle them as a whole, to load or save them or to create a new (empty) tree.

The basic structure of the app is shown below, including the Tree object, the App itself and TreeView and TreeToXml converter. The app controls the converted via the TreeManager. The Analyst conducts calculations and a displays the results.

![App class diagram](./out/uml/uml/app_class_diagram.svg)


## Where are the xml files?
Files are stored at custom locations. When saving or loading a tree, the user is prompted to specify the file via dialog window.

## Actions of the Tree Manager
- **save** the tree at specific location (the tree name is preserved, and user is prompted to choose a different name, if tree already exists)
- **update** an existing tree; if the xml file to be updated or the directory no longer exist, they are **created** anew and the user is **notified** of this
- **load** the tree from file specified by the user via **dialog window**
- **unload** the tree from the **tree list**


## Adding an item to the Named Items List
- Adding an item with already existing name will result in adding the new item, however under an adjusted name (e.g., if item is added under already taken name "Thing", it will be added as "Thing (1)").