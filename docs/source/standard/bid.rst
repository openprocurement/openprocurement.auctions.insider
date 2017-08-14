.. . Kicking page rebuild 2014-10-30 17:00:08

.. index:: Bid, Parameter, LotValue, bidder, participant, pretendent

.. _bid:

Bid
===

Schema
------

:tenderers:
    List of :ref:`Organization` objects

:date:
    string, :ref:`date`, auto-generated
    
    Date when bid has been submitted.

:id:
    UID, auto-generated

:status:
    string

    Possible values are:

    * `draft`
    * `active`

:value:
    :ref:`Value`, required

    Validation rules:

    * `currency` should either be absent or match `Auction.value.currency`
    * `valueAddedTaxIncluded` should either be absent or match `Auction.value.valueAddedTaxIncluded`

:documents:
    List of :ref:`Document` objects

:parameters:
    List of :ref:`Parameter` objects

.. :lotValues:
    List of :ref:`LotValue` objects

:participationUrl:
    URL

    A web address for participation in auction.

:qualified:
    bool, required

    
.. _Parameter:

Parameter
=========

Schema
------

:code:
    string, required

    Feature code.

:value:
    float, required

    Feature value.


