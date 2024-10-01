# HoFi
An abbreviation for home finance. It provides a way to write down expenses, incomes and debts, to plan them and to plan the repayment and the future transactions.

The following activities are of interest:
- storing information on various transactions and debts;
- planning the transaction and debt repayment;
- displaying the significance of individual transactions, debts and their groups.

The project is licensed under the [MIT License](https://opensource.org/license/mit/).


## How it works
The transactions are stored in a hierachical structure in an xml file. The xml schema defines several objects:
- debts,
- income,
- expense,
- object, that can be parent to other objects and to incomes and expenses.

The xml file should be edited via an user interface written in Python.


# Rebuild
At certain point, it was not anymore clear, how and when exactly are dependent attributes being updated, how to correctly implement undo and redo commands for editor actions and how to easily add checking various deadlines and how to handle changing the event (e.g., expense) dates. Another issue comes with the idea of using a whole scenario as an item in another, which appears to be a usefull option for first analysing a simple situation and then adding it to a more general scenario.
Other goals are:
- simplify defining the various objects occuring in the editor (scenario, income, ...)
- exporting only a single item into a file
- enable to connect a various kinds of visualisation tools (e.g., a graph displaying evolution of a quantity with respect to time)
