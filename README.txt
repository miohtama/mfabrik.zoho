Introduction
------------

*mfabrik.zoho* package provides Python classes for making easy Zoho API calls. 
They allow you to integrate `Zoho web application data <http://www.zoho.com>`_
into your Python software.  

Features
--------

* Creating Zoho API session a.k.a ticket

* Extendable API using a base class architecture

* Logging all incoming and outgoing API traffic with Zoho

* Support Python 2.4, 2.5 and 2.6 (2.4 needs additional lxml and simplejson libraries installed)

* Compatible with non-ASCII or Unicode letters

* Unit tests to guarantee the high quality of the code

*mfabrik.zoho* is intended to use for machine-to-machine communication and
will work with any web framework, like Plone, Django, Google App Engine.

To communicate with Zoho you need username, password or API KEY.
For further information, see *Setup > Admin > Developer key* in 
your Zoho application.

API support
-----------

Currently out of box support includes:

* CRM apis: insert_records, get_records, delete_lead
* Support API: add_records

You can easily wrap Zoho API calls you need using this library.
Please contribute patches to the package.

Installation
------------

To install mfabrik.zoho to your system-wide Python 
do as below. 

Example (UNIX)::

        sudo easy_install mfabrik.zoho
        
Example (UNIX, Python 2.4)::

        sudo easy_install mfabrik.zoho lxml simplejson 
        
Usage
-----

To learn how to use this library, it is best to study its unit test source code (tests.py).

Example usage::

        # Import CRM connector class for Zoho CRM
        from mfabrik.zoho.crm import CRM
        # Import Support connector class for Zoho Support
        from mfabrik.zoho.crm import SUPPORT
        # (optional) Use to raise a ZohoException in your application.
        from mfabrik.zoho.core import ZohoException

        # Initialize Zoho CRM API connection
        # You need valid Zoho API key for this.
        # You get necessary data from Zoho > Setup > Admin > Developer key
        crm = CRM(authtoken="authtoken", scope="crmapi")
        # same for support
        support = SUPPORT(authtoken="authtoken", scope="supportapi")

        # If you're going to use session tickets, include a username and password 
        # Then run MODULE.open() to generate the session ticket.
        # This functionality is currently Deprecated for CRM & Support and will cause a 4500 error
        # It might be available with other Zoho API's
        crm = CRM(username="myusername", password="foobar", authtoken="12312312312312312323", scope="crmapi")
        crm.open()
        

CRM input example::

        # Input is just a bunch of dictionaried data
        # For possible parameters see https://www.zoho.com/crm/help/api/insertrecords.html
        # To discover required fields in CRM, log into zoho and visit Setup > Customization > Layouts
        # Everything marked with red, or with a padlock is a required field.
        
        # Zoho default compulsory fields for Leads: Last Name, Company
        
        lead = {
            u"First Name" : u"Mikko",
            u"Last Name" : u"Ohtamaa",
            u"Company" : u"mFabrik Research Oy"   
        }
        # Special fields *Lead Owner* must be the Email of the CRM user.

        # Insert a new lead to Zoho CRM lead database.
        # We support multiple leads per call, so we need to listify our one lead first.
        responses = crm.insert_records('Leads',[lead]) # This will raise ZohoException if lead data is invalid

        # To insert records attached to a parent record, like a Product on a SalesOrder
        # This functionality is currently only written for the CRM. 
        SalesOrders = {
            'Subject': "Subjuct is required", # Subject is required
            'Sales Order Owner': "you@youremail.com", # Must be the registered Email for the CRM user
            'Contact Name': Zoho ID from either Leads, Contacts, OR a string containing the Full Contact Name.
            'Sub Total': "100",
            'Tax': "5",
            'Adjustment':"5",
            'Grand Total': "110",
            'Billing Street': "123 Fake Street",
            'Shipping Street': "123 Fake Street",
            'Billing City': "San Francisco",
            'Shipping City': "San Francisco",
            'Billing State': "CA",
            'Shipping State': "CA",
            'Billing Code': "90001",
            'Shipping Code': "90001",
            'Billing Country': "US",
            'Shipping Country': "US",
            'Product Details':{ # Add a For Each, add a list full of dictionaries contaning at least a Product Id
                'product': [
                    {
                        'Product Id': '1470000001', # The Zoho ID from the item in the "Products" module
                        'Product Name': "Foo",
                        'Qty': "20",
                        'Unit Price': "10",
                        'List Price': "10",
                        'Total': "200",
                        'Discount': "100",
                        'Total After Discount':"100",
                        'Net Total':"100",
                    },
                ],
            },
        }
        response = crm.insert_records('SalesOrders', [SalesOrders])

        # list of responses. one response is {'Modified Time': '2010-10-07 13:24:49', 'Created By': 'Developer', 'Modified By': 'Developer', 'Id': '177376000000253053', 'Created Time': '2010-10-07 13:24:49'}
        # At least one response is guaranteed, otherwise an exception is raised
        
        lead_id = responses[0]["Id"]
            

Support input example::

        incomingData = {
            'Contact Name': 'John Doe',
            'Email': 'jdoe@example.com',
            'Phone': '555-555-1234',
            'Classification': 'Software Issue',
            'Subject': 'Support request subject here',
            'Description': 'Body of the support request text.'
        }
        response = support.add_records([incomingData], 'Department Name', 'Portal Name')
        record_id = response[0]["Id"]
  
        
        
.. note::
        
        Some calls (e.g. delete) seem to have delay and the changes might not be instantly
        reflected in the next API call (getRecords).
        
        
Logging
=======

Python `logging` module logger *Zoho API* is used to output API traffic
on DEBUG log level.

Source code
-----------

* http://github.com/miohtama/mfabrik.zoho

Commercial development
-----------------------

This package is licensed under open source GPL license.
If you wish to use this code in a commercial product, 
relicense it or you are 
looking for high quality Zoho/Python support, please contact
`mFabrik Research <mailto:research@mfabrik.com>`_.
Our top class Python developers are ready to help you with your software development.

Further reading
---------------

* Zoho CRM API: http://zohocrmapi.wiki.zoho.com/API-Methods.html

* API update notes: http://forums.zoho.com/topic/zoho-crm-api-update-important

Author
------

`mFabrik Research Oy <mailto:info@mfabrik.com>`_ - Python and Plone professionals for hire.

* `mFabrik web site <http://mfabrik.com>`_ 

* `mFabrik mobile site <http://mfabrik.mobi>`_ 

* `Blog <http://blog.mfabrik.com>`_

       