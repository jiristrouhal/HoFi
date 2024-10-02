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

