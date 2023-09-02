from typing import Literal

import src.core.tree as treemod
from src.core.tree import NewTemplate
from decimal import Decimal
import src.lang.lang as lang


import src.core.currency as cur
from src.events.past_and_future import Event, Event_Manager
from src.core.tree_templates import User_Defined_Command


from src.core.dates import default_date


_Status_Label = Literal['planned','realized','requires_confirmation']


from PIL import Image, ImageTk
def photo_icon(rel_path:str)->ImageTk.PhotoImage:
    return ImageTk.PhotoImage(Image.open(rel_path))


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
    DATE = tvoc("date")
    DESCRIPTION = tvoc("description")
    STATUS = tvoc("status")
    LAST_STATUS = tvoc("last_status")

    PLANNED = vocabulary("Status","Planned")
    REALIZED = vocabulary("Status","Realized")
    REQUIRES_CONFIRMATION = vocabulary("Status","Requires_Confirmation")

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
                s += child._attributes[AMOUNT].value
            elif child.tag==ITEM:
                s += Decimal(extract_money_amount(child.dependent_attributes[EXPENSES].value))
        return cur.CURRY_FORMATS[item.its_tree._attributes[CURRENCY].value].present(s,locale_code)

    def status(item:treemod.TreeItem)->str:
        if "event" not in item.data: 
            item.data["event"] = Event(item._attributes[DATE]._value)
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
            if last_status.value not in states.values():
                if event.realized: last_status.set(REALIZED)
                elif event.confirmation_required: last_status.set(REQUIRES_CONFIRMATION)
                else: last_status.set(PLANNED)
                return last_status.value
            state_keys = {state:key for key,state in states.items()}
            new_status_label:_Status_Label = _updated_status(state_keys[last_status.value],event)
            last_status.set(states[new_status_label])
            return last_status.value
                
    def default_amount_by_tree(item:treemod.TreeItem)->str:
        return "1" + cur.CURRY_FORMATS[item.its_tree._attributes[CURRENCY].value].symbol
    
    def confirm_realization(item:treemod.TreeItem)->None:
        item.data["event"].confirm_realization()
        item._attributes[LAST_STATUS].set(REALIZED)

    def confirmation_required(item:treemod.TreeItem)->bool:
        return item.data["event"].confirmation_required

    app_template.add(
        NewTemplate(
            SCENARIO,
            {
                CURRENCY:({code:code for code in cur.CURRY_CODES}, cur.DEFAULT_CURRENCY_CODE),
                INCOMES: sum_incomes,
                EXPENSES: sum_expenses
            },
            children=(INCOME, EXPENSE, ITEM, DEBT, NONFINANCIAL_DEBT),
            icon_file=photo_icon("src/_icons/scenario.png"),
        ),
        NewTemplate(
            INCOME,
            { 
                AMOUNT: "1 Kč", 
                DATE: default_date(app_template.locale_code),
                STATUS: status,
                LAST_STATUS: "unknown"
            },
            children=(),
            icon_file=photo_icon("src/_icons/income.png"),
            variable_defaults={AMOUNT: default_amount_by_tree},
            user_def_cmds=[
                User_Defined_Command(
                    label="Confirm", 
                    condition=confirmation_required,
                    command=confirm_realization
                )
            ],
        ),
        NewTemplate(
            EXPENSE,
            {
                AMOUNT: "1 Kč", 
                DATE: default_date(app_template.locale_code),
                STATUS: status,
                LAST_STATUS: "unknown"
            },
            children=(),
            icon_file=photo_icon("src/_icons/expense.png"),
            variable_defaults={AMOUNT: default_amount_by_tree},
        ),
        NewTemplate(
            ITEM,
            {INCOMES: sum_incomes, EXPENSES: sum_expenses},
            children=(INCOME,EXPENSE,ITEM),
            icon_file=photo_icon("src/_icons/item.png")
        ),
        NewTemplate(
            DEBT,
            {
                AMOUNT:"1 Kč", 
                DATE: default_date(app_template.locale_code)
            },
            children=(),
            icon_file=photo_icon("src/_icons/debt.png"),
            variable_defaults={AMOUNT: default_amount_by_tree}
        ),
        NewTemplate(
            NONFINANCIAL_DEBT,
            {
                DESCRIPTION:"...", 
                DATE: default_date(app_template.locale_code)
            },
            children=(),
            icon_file=photo_icon("src/_icons/nonmonetary_debt.png")
        ),
    )


def _updated_status(last_status:_Status_Label, event:Event)->_Status_Label:
    if event.confirmation_required: return 'requires_confirmation'
    elif event.planned: return 'planned'
    else: 
        if last_status=='realized': return 'realized'
        else: return 'requires_confirmation'
