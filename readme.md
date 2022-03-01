# Project Information

| About                    | Info                               |
|:-------------------------|:-----------------------------------|
| Created                  | February 28, 2022 19:09:37                      |
| API Logic Server Version | 4.02.08           |
| Created in directory     | Allocation |
| API Name                 | api          |


# Allocate Payment to Outstanding Orders

This project is to illustrate the use of [Allocation](https://github.com/valhuber/LogicBank/wiki/Sample-Project---Allocation).

Allocation is a pattern (more examples below), where:

> A ```Provider``` allocates to a list of ```Recipients```,
>creating ```Allocation``` rows.


For example, imagine a ```Customer``` has a set of outstanding
```Orders```, and pays all/several off with a periodic ```Payment```.

## Data Model

![Background](/images/db.png?raw=true "Optional Title")

## Requirements
When the ```Payment``` is inserted, our system must:
1. Allocate the ```Payment``` to ```Orders``` that have ```AmountOwed```, oldest first
1. Keep track of how the ```Payment``` is allocated, by creating 
a ```PaymentAllocation```
1. As the ```Payment``` is allocated,
   1. Update the ```Order.AmountOwed```, and
   1. Adjust the ```Customer.Balance```



&nbsp;&nbsp;


# Setup

The usual:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This should enable you to run launch configuration `ApiLogicServer`.

&nbsp;&nbsp;

# Walkthrough

The test illustrates allocation logic for our inserted payment,
which operates as follows:
1. The triggering event is the insertion of a ```Payment```, which triggers:
1. The ```allocate``` rule (line 28).  It performs the allocation:
   1. Obtains the list of recipient orders by calling the function```unpaid_orders``` (line 9)
   1. For each recipient (```Order```),
      1. Creates a ```PaymentAllocation```, links it to the ```Order``` and ```Payment```,
      1. Invokes ```while_calling_allocator```, which
           1. Reduces ```Payment.AmountUnAllocated```
           1. Inserts the ```PaymentAllocation```, which runs the following rules:
              * r1 ```PaymentAllocation.AmountAllocated``` is derived (formula, line 25); 
                 this triggers the next rule...
              * r2 ```Order.AmountPaid``` is adjusted (sum rule, line 23); that triggers... 
              * r3 ```Order.AmountOwed``` is derived (formula rule, line 22); that triggers
              * r4 ```Customer.Balance``` is adjusted (sum rule, line 20)
           1. Returns whether the```Payment.AmountUnAllocated``` has remaining value ( > 0 ).
        1. Tests the returned result
            1. If true (allocation remains), the loop continues for the next recipient
            1. Otherwise, the allocation loop is terminated
   
#### Default ```while_calling_allocator```
This example does not supply an optional argument:
```while_calling_allocator```.
The [`logic_bank/extensions/allocate.py`](../blob/main/logic_bank/extensions/allocate.py)
provides a default, called ```while_calling_allocator_default```.

This default presumes the attribute names shown in the code below.
If these do not match your attribute names, copy / alter this
implementation to your own, and specify it on the constructor
(line 15).

```python
    def while_calling_allocator_default(self, allocation_logic_row, provider_logic_row) -> bool:
        """
        Called for each created allocation, to
            * insert the created allocation (triggering rules that compute `Allocation.AmountAllocated`)
            * reduce Provider.AmountUnAllocated
            * return boolean indicating whether Provider.AmountUnAllocated > 0 (remains)

        This uses default names:
            * provider.Amount
            * provider.AmountUnallocated
            * allocation.AmountAllocated

        To use your names, copy this code and alter as as required

        :param allocation_logic_row: allocation row being created
        :param provider_logic_row: provider
        :return: provider has AmountUnAllocated remaining
        """

        if provider_logic_row.row.AmountUnAllocated is None:
            provider_logic_row.row.AmountUnAllocated = provider_logic_row.row.Amount  # initialization

        allocation_logic_row.insert(reason="Allocate " + provider_logic_row.name)  # triggers rules, eg AmountAllocated

        provider_logic_row.row.AmountUnAllocated = \
            provider_logic_row.row.AmountUnAllocated - allocation_logic_row.row.AmountAllocated

        return provider_logic_row.row.AmountUnAllocated > 0  # terminate allocation loop if none left
```

#### Log Output
Logic operation is visible in the log

> Note: the test program
[`examples/payment_allocation/tests/add_payment.py`](../blob/main/examples/banking/tests/transfer_funds.py)
shows some test data in comments at the end

```
Logic Phase:		BEFORE COMMIT          						 - 2020-12-23 05:56:45,682 - logic_logger - DEBUG
Logic Phase:		ROW LOGIC (sqlalchemy before_flush)			 - 2020-12-23 05:56:45,682 - logic_logger - DEBUG
..Customer[ALFKI] {Update - client} Id: ALFKI, CompanyName: Alfreds Futterkiste, Balance: 1016.00, CreditLimit: 2000.00  row@: 0x10abbea00 - 2020-12-23 05:56:45,682 - logic_logger - DEBUG
..Payment[None] {Insert - client} Id: None, Amount: 1000, AmountUnAllocated: None, CustomerId: None, CreatedOn: None  row@: 0x10970f610 - 2020-12-23 05:56:45,682 - logic_logger - DEBUG
..Payment[None] {BEGIN Allocate Rule, creating: PaymentAllocation} Id: None, Amount: 1000, AmountUnAllocated: None, CustomerId: None, CreatedOn: None  row@: 0x10970f610 - 2020-12-23 05:56:45,683 - logic_logger - DEBUG
....PaymentAllocation[None] {Insert - Allocate Payment} Id: None, AmountAllocated: None, OrderId: None, PaymentId: None  row@: 0x10abbe700 - 2020-12-23 05:56:45,684 - logic_logger - DEBUG
....PaymentAllocation[None] {Formula AmountAllocated} Id: None, AmountAllocated: 100.00, OrderId: None, PaymentId: None  row@: 0x10abbe700 - 2020-12-23 05:56:45,684 - logic_logger - DEBUG
......Order[10692] {Update - Adjusting Order} Id: 10692, CustomerId: ALFKI, OrderDate: 2013-10-03, AmountTotal: 878.00, AmountPaid:  [778.00-->] 878.00, AmountOwed: 100.00  row@: 0x10ac82370 - 2020-12-23 05:56:45,685 - logic_logger - DEBUG
......Order[10692] {Formula AmountOwed} Id: 10692, CustomerId: ALFKI, OrderDate: 2013-10-03, AmountTotal: 878.00, AmountPaid:  [778.00-->] 878.00, AmountOwed:  [100.00-->] 0.00  row@: 0x10ac82370 - 2020-12-23 05:56:45,685 - logic_logger - DEBUG
........Customer[ALFKI] {Update - Adjusting Customer} Id: ALFKI, CompanyName: Alfreds Futterkiste, Balance:  [1016.00-->] 916.00, CreditLimit: 2000.00  row@: 0x10abbea00 - 2020-12-23 05:56:45,685 - logic_logger - DEBUG
....PaymentAllocation[None] {Insert - Allocate Payment} Id: None, AmountAllocated: None, OrderId: None, PaymentId: None  row@: 0x10ac6a850 - 2020-12-23 05:56:45,686 - logic_logger - DEBUG
....PaymentAllocation[None] {Formula AmountAllocated} Id: None, AmountAllocated: 330.00, OrderId: None, PaymentId: None  row@: 0x10ac6a850 - 2020-12-23 05:56:45,686 - logic_logger - DEBUG
......Order[10702] {Update - Adjusting Order} Id: 10702, CustomerId: ALFKI, OrderDate: 2013-10-13, AmountTotal: 330.00, AmountPaid:  [0.00-->] 330.00, AmountOwed: 330.00  row@: 0x10ac824f0 - 2020-12-23 05:56:45,686 - logic_logger - DEBUG
......Order[10702] {Formula AmountOwed} Id: 10702, CustomerId: ALFKI, OrderDate: 2013-10-13, AmountTotal: 330.00, AmountPaid:  [0.00-->] 330.00, AmountOwed:  [330.00-->] 0.00  row@: 0x10ac824f0 - 2020-12-23 05:56:45,686 - logic_logger - DEBUG
........Customer[ALFKI] {Update - Adjusting Customer} Id: ALFKI, CompanyName: Alfreds Futterkiste, Balance:  [916.00-->] 586.00, CreditLimit: 2000.00  row@: 0x10abbea00 - 2020-12-23 05:56:45,686 - logic_logger - DEBUG
....PaymentAllocation[None] {Insert - Allocate Payment} Id: None, AmountAllocated: None, OrderId: None, PaymentId: None  row@: 0x10ac6a9d0 - 2020-12-23 05:56:45,687 - logic_logger - DEBUG
....PaymentAllocation[None] {Formula AmountAllocated} Id: None, AmountAllocated: 570.00, OrderId: None, PaymentId: None  row@: 0x10ac6a9d0 - 2020-12-23 05:56:45,687 - logic_logger - DEBUG
......Order[10835] {Update - Adjusting Order} Id: 10835, CustomerId: ALFKI, OrderDate: 2014-01-15, AmountTotal: 851.00, AmountPaid:  [0.00-->] 570.00, AmountOwed: 851.00  row@: 0x10ac82550 - 2020-12-23 05:56:45,688 - logic_logger - DEBUG
......Order[10835] {Formula AmountOwed} Id: 10835, CustomerId: ALFKI, OrderDate: 2014-01-15, AmountTotal: 851.00, AmountPaid:  [0.00-->] 570.00, AmountOwed:  [851.00-->] 281.00  row@: 0x10ac82550 - 2020-12-23 05:56:45,688 - logic_logger - DEBUG
........Customer[ALFKI] {Update - Adjusting Customer} Id: ALFKI, CompanyName: Alfreds Futterkiste, Balance:  [586.00-->] 16.00, CreditLimit: 2000.00  row@: 0x10abbea00 - 2020-12-23 05:56:45,688 - logic_logger - DEBUG
..Payment[None] {END Allocate Rule, creating: PaymentAllocation} Id: None, Amount: 1000, AmountUnAllocated: 0.00, CustomerId: None, CreatedOn: None  row@: 0x10970f610 - 2020-12-23 05:56:45,688 - logic_logger - DEBUG
Logic Phase:		COMMIT   									 - 2020-12-23 05:56:45,689 - logic_logger - DEBUG
Logic Phase:		FLUSH   (sqlalchemy flush processing       	 - 2020-12-23 05:56:45,689 - logic_logger - DEBUG

add_payment, update completed
```


## Key Points
Allocation illustrates some key points regarding logic.

### Extensibility
While Allocation is part of Logic Bank, you could have recognized
the pattern yourself, and provided the implementation.  This is
enabled since Event rules can invoke Python.  You can make your
Python code generic, using meta data (from SQLAlchemy),
parameters, etc.

### Rule Chaining
Note how the created ```PaymentAllocation``` row triggered
the more standard rules such as sums and formulas.  This
required no special machinery: rules watch and react to changes in data -
if you change the data, rules will "notice" that, and fire.  Automatically.

