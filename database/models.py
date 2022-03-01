# coding: utf-8
from sqlalchemy import Boolean, Column, DECIMAL, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base


########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
from safrs import SAFRSBase

import safrs

Base = declarative_base()
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.mysql import *
########################################################################################################################



class Customer(SAFRSBase, Base):
    __tablename__ = 'Customer'

    Id = Column(String(8000), primary_key=True)
    CompanyName = Column(String(8000))
    Balance = Column(DECIMAL)
    CreditLimit = Column(DECIMAL)
    allow_client_generated_ids = True

    OrderList = relationship('Order', cascade_backrefs=True, backref='Customer')
    PaymentList = relationship('Payment', cascade_backrefs=True, backref='Customer')


t_sqlite_sequence = Table(
    'sqlite_sequence', metadata,
    Column('name', NullType),
    Column('seq', NullType)
)


class Order(SAFRSBase, Base):
    __tablename__ = 'Order'

    Id = Column(Integer, primary_key=True)
    CustomerId = Column(ForeignKey('Customer.Id'))
    OrderDate = Column(String(8000))
    AmountTotal = Column(DECIMAL(10, 2))
    AmountPaid = Column(DECIMAL(10, 2), server_default=text("0"), nullable=False)
    AmountOwed = Column(DECIMAL(10, 2), server_default=text("0"), nullable=False)

    # see backref on parent: Customer = relationship('Customer', cascade_backrefs=True, backref='OrderList')

    PaymentAllocationList = relationship('PaymentAllocation', cascade_backrefs=True, backref='Order')


class Payment(SAFRSBase, Base):
    __tablename__ = 'Payment'

    Id = Column(Integer, primary_key=True)
    Amount = Column(DECIMAL)
    AmountUnAllocated = Column(DECIMAL)
    CustomerId = Column(ForeignKey('Customer.Id'))
    CreatedOn = Column(String(80))

    # see backref on parent: Customer = relationship('Customer', cascade_backrefs=True, backref='PaymentList')

    PaymentAllocationList = relationship('PaymentAllocation', cascade_backrefs=True, backref='Payment')


class PaymentAllocation(SAFRSBase, Base):
    __tablename__ = 'PaymentAllocation'

    Id = Column(Integer, primary_key=True)
    AmountAllocated = Column(DECIMAL, server_default=text("0"))
    OrderId = Column(ForeignKey('Order.Id'))
    PaymentId = Column(ForeignKey('Payment.Id'))

    # see backref on parent: Order = relationship('Order', cascade_backrefs=True, backref='PaymentAllocationList')
    # see backref on parent: Payment = relationship('Payment', cascade_backrefs=True, backref='PaymentAllocationList')


from database import customize_models
