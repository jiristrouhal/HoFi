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


