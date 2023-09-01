from PIL import Image, ImageTk
from collections import OrderedDict
from typing import Literal, Dict

import src.core.tree as treemod
from decimal import Decimal
import src.lang.lang as lang


import src.core.currency as cur
from src.events.past_and_future import Event, Event_Manager
from src.core.tree_templates import User_Defined_Command


from src.core.dates import default_date



_Status_Label = Literal['planned','realized','requires_confirmation']



def main(vocabulary:lang.Vocabulary, app_template:treemod.AppTemplate, event_manager:Event_Manager):

    cur.set_localization(app_template.locale_code)
    tvoc = vocabulary.subvocabulary("Templates")
    SCENARIO = tvoc("Scenario")
    INCOME = tvoc("Income")
    EXPENSE = tvoc("Expense")
    ITEM = tvoc("Item")
    DEBT = tvoc("Debt")
    NONFINANCIAL_DEBT = tvoc("Non_Monetary_Debt")

    INCOMES = tvoc("incomes")
    EXPENSES = tvoc("expenses")
    CURRENCY = tvoc("currency")
    AMOUNT = tvoc("amount")
    NAME =  tvoc("name")
    DATE = tvoc("date")
    DESCRIPTION = tvoc("description")
    STATUS = tvoc("status")
    LAST_STATUS = tvoc("last_status")

    PLANNED = vocabulary("Status","Planned")
    REALIZED = vocabulary("Status","Realized")
    REQUIRES_CONFIRMATION = vocabulary("Status","Requires_Confirmation")

    income_icon = ImageTk.PhotoImage(Image.open("src/_icons/income.png"))
    expense_icon = ImageTk.PhotoImage(Image.open("src/_icons/expense.png"))
    item_icon = ImageTk.PhotoImage(Image.open("src/_icons/item.png"))
    debt_icon = ImageTk.PhotoImage(Image.open("src/_icons/debt.png"))
    nonmon_debt_icon = ImageTk.PhotoImage(Image.open("src/_icons/nonmonetary_debt.png"))

    locale_code = app_template.locale_code


    def extract_money_amount(assumed_money:str)->float:
        x = cur.convert_to_currency(assumed_money)
        if isinstance(x,tuple) and len(x)>0:
            return x[0]
        else:
            return 0

    def sum_incomes(item:treemod.TreeItem)->str:
        s = Decimal(0.0)
        for child in item._children:
            if child.tag==INCOME:
                s += child.attributes[AMOUNT].value
            elif child.tag==ITEM:
                s += Decimal(extract_money_amount(child.dependent_attributes[INCOMES].value))
        return cur.CURRY_FORMATS[item.its_tree.attributes[CURRENCY].value].present(s,locale_code)
    
    def sum_expenses(item:treemod.TreeItem)->str:
        s = Decimal(0.0)
        for child in item._children:
            if child.tag==EXPENSE:
                s += child.attributes[AMOUNT].value
            elif child.tag==ITEM:
                s += Decimal(extract_money_amount(child.dependent_attributes[EXPENSES].value))
        return cur.CURRY_FORMATS[item.its_tree.attributes[CURRENCY].value].present(s,locale_code)

    def status(item:treemod.TreeItem)->str:
        if DATE not in item._attributes: return ""
        if "event" not in item.data: 
            item.data["event"] = Event(item._attributes[DATE].value)
            event_manager.add(item.data["event"])
        if LAST_STATUS not in item._attributes: 
            return PLANNED if item.data["event"].planned else REALIZED
        else:
            last_status = item._attributes[LAST_STATUS]
            event:Event = item.data["event"]
            states = {
                'planned':PLANNED,
                'realized':REALIZED,
                'requires_confirmation':REQUIRES_CONFIRMATION
            }
            state_keys = {state:key for key,state in states.items()}
            new_status_label:_Status_Label = _updated_status(state_keys[last_status.value],event)
            last_status.set(states[new_status_label])
            return last_status.value
                


    def default_amount_by_tree(item:treemod.TreeItem)->str:
        return "1" + cur.CURRY_FORMATS[item.its_tree.attributes[CURRENCY].value].symbol
    
    def confirm_realization(item:treemod.TreeItem)->None:
        event:Event = item.data["event"]
        event.confirm_realization()

    def confirmation_required(item:treemod.TreeItem)->bool:
        event:Event = item.data["event"]
        return event.confirmation_required


    app_template.add(
        treemod.NewTemplate(
            SCENARIO,
            OrderedDict({
                NAME:SCENARIO,
                CURRENCY:({code:code for code in cur.CURRY_CODES}, cur.DEFAULT_CURRENCY_CODE),
                INCOMES: sum_incomes,
                EXPENSES: sum_expenses
            }),
            children=(INCOME, EXPENSE, ITEM, DEBT, NONFINANCIAL_DEBT)
        ),
        treemod.NewTemplate(
            INCOME,
            OrderedDict({
                NAME:INCOME, 
                AMOUNT: "1 Kč", 
                DATE: default_date(app_template.locale_code),
                STATUS: status,
                LAST_STATUS: "unknown"
            }),
            children=(),
            icon_file=income_icon,
            variable_defaults={AMOUNT: default_amount_by_tree},
            user_def_cmds=[
                User_Defined_Command(
                    label="Confirm", 
                    condition=confirmation_required,
                    command=confirm_realization
                )
            ],
        ),
        treemod.NewTemplate(
            EXPENSE,
            OrderedDict({
                NAME:EXPENSE,
                AMOUNT: "1 Kč", 
                DATE: default_date(app_template.locale_code),
                STATUS: status,
                LAST_STATUS: "unknown"
            }),
            children=(),
            icon_file=expense_icon,
            variable_defaults={AMOUNT: default_amount_by_tree},
        ),
        treemod.NewTemplate(
            ITEM,
            OrderedDict({
                NAME:ITEM,
                INCOMES: sum_incomes,
                EXPENSES: sum_expenses
            }),
            children=(INCOME,EXPENSE,ITEM),
            icon_file=item_icon
        ),

        treemod.NewTemplate(
            DEBT,
            OrderedDict({
                NAME:DEBT,
                AMOUNT:"1 Kč", 
                DATE: default_date(app_template.locale_code)
            }),
            children=(),
            icon_file=debt_icon,
            variable_defaults={AMOUNT: default_amount_by_tree}
        ),
        treemod.NewTemplate(
            NONFINANCIAL_DEBT,
            OrderedDict({
                NAME:NONFINANCIAL_DEBT,
                DESCRIPTION:"...", 
                DATE: default_date(app_template.locale_code)
            }),
            children=(),
            icon_file=nonmon_debt_icon
        ),
    )


def _updated_status(
    last_status:_Status_Label, 
    event:Event,
    )->_Status_Label:

    if last_status=='planned':
        if event.planned:
            if event.confirmation_required: 
                return 'requires_confirmation'
            else: 
                return 'planned'
        else:
            event.consider_as_planned()
            return 'requires_confirmation'

    elif last_status=='requires_confirmation':
        if event.realized or event.confirmation_required:
            event.consider_as_planned()
            return 'requires_confirmation'
        else:
            return 'planned'
    else: #last_status.value=='realized'
        if event.realized: 
            return 'realized'
        else: 
            if event.confirmation_required: 
                return 'requires_confirmation'
            else: 
                return 'planned'
