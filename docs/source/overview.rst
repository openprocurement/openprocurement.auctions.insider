Overview
========

openprocurement.auctions.dutch contains documentaion for Deposit Guarantee Fund auctions.


Features
--------

* Procedure can be switched from *draft* status to *active.tendering*.
* During *active.tendering* period participants can ask questions, submit proposals, and upload documents.
* The only date Organizer has to provide is *Tender.auctionPeriod.startDate*, the rest will be calculated automatically.
* Organizer can't edit procedure's significant properties (*Auction.value*, etc.).
* There is obligatory participant qualification (*Bid.selfQualified*) via guarantee payment. It has to be paid till 16:00 of the auction day.
* The only currency (*Value.currency*) for this procedure is hryvnia (UAH).
* Auction consists of 3 stages: Dutch auction, sealed bid and best bid parts.
* Auction is passing within a day.
* *Auction.value* is gradually decreasing per 1% during the Dutch part.
* In case of no bid has been made within Dutch auction, the whole procedure will be marked as unsuccessful.
* Bidders can enter the auction till the end of the Dutch part.


Conventions
-----------

API accepts `JSON <http://json.org/>`_ or form-encoded content in
requests.  It returns JSON content in all of its responses, including
errors.  Only the UTF-8 character encoding is supported for both requests
and responses.

All API POST and PUT requests expect a top-level object with a single
element in it named `data`.  Successful responses will mirror this format. 
The data element should itself be an object, containing the parameters for
the request.  In the case of creating a new auction, these are the fields we
want to set on the auction itself.

If the request was successful, we will get a response code of `201`
indicating the object was created.  That response will have a data field at
its top level, which will contain complete information on the new auction,
including its ID.

If something went wrong during the request, we'll get a different status
code and the JSON returned will have an `errors` field at the top level
containing a list of problems.  We look at the first one and print out its
message.


Project status
--------------

The project has pre alpha status.

The source repository for this project is on GitHub: 
`<https://github.com/openprocurement/openprocurement.auctions.insider>`_.
 

Documentation of related packages
---------------------------------

* `OpenProcurement API <http://api-docs.openprocurement.org/en/latest/>`_

API stability
-------------

API is relatively stable. The changes in the API are communicated via 
`Open Procurement API <https://groups.google.com/group/open-procurement-api>`_ 
maillist.


Next steps
----------
You might find it helpful to look at the :ref:`tutorial`.
