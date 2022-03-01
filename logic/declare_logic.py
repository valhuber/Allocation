import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import logging


def allocate_payment(row: models.Payment, old_row: models.Payment, logic_row: LogicRow):
    """ get unpaid orders (recipient), invoke allocation """
    customer_of_payment = row.Customer
    unpaid_orders = logic_row.session.query(Order)\
        .filter(Order.AmountOwed > 0, Order.CustomerId == customer_of_payment.Id)\
        .order_by(Order.OrderDate).all()
    row.AmountUnAllocated = row.Amount
    Allocate(from_provider_row=logic_row,  # uses default while_calling_allocator
             to_recipients=unpaid_orders,
             creating_allocation=PaymentAllocation).execute()


def declare_logic():

    Rule.sum(derive=models.Customer.Balance, as_sum_of=models.Order.AmountOwed)

    Rule.formula(derive=models.Order.AmountOwed, as_expression=lambda row: row.AmountTotal - row.AmountPaid)
    Rule.sum(derive=models.Order.AmountPaid, as_sum_of=models.PaymentAllocation.AmountAllocated)

    Rule.formula(derive=models.PaymentAllocation.AmountAllocated, as_expression=lambda row:
        min(Decimal(row.Payment.AmountUnAllocated), Decimal(row.Order.AmountOwed)))

    Rule.early_row_event(on_class=models.Payment, calling=allocate_payment)
