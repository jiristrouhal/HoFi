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

## How to use

### Requirements

- Python version 3.11.0 and newer

### Install dependencies

- create virtual environment: `python -m venv .venv`
- [activate](https://docs.python.org/3/library/venv.html#how-venvs-work),
- install dependencies: `pip install -r requirements.txt`.

### Configure the app

`localization` - locale code,
`allow_item_name_duplicates` - allow the items of the same name under a common parent item,
`currency` - currency code,
`editor_precision` - precision of decimal numbers shown in editor (except for currency),
`show_trailing_zeros` - display trailing zeros of all non-currency numbers,
`use_thousands_separator` - use thousands separator (given by the localization).

### Run the app

```bash
python3 -m hofi
```


