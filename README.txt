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

To communicate with Zoho you need username, password and API KEY.
For further information, see *Setup > Admin > Developer key* in 
your Zoho application.

API support
-----------

Currently out of box support includes:

* CRM apis: insert_records, get_records, delete_lead

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

        # Import CRM connector class
        from mfabrik.zoho.crm import CRM
        from mfabrik.zoho.core import ZohoException

        # Initialize Zoho CRM API connection
        # You need valid Zoho credentials and API key for this.
        # You get necessary data from Zoho > Setup > Admin > Developer key
        crm = CRM(username="myusername", password="foobar", apikey="12312312312312312323")

        # Open connection can be used to make as many as possible API calls
        # This will raise ZohoException if credentials are incorrect.
        # Also IOError or URLError will be raised if you the connection to Zoho servers
        # does not work.
        crm.open()

        # Lead is just a bunch of dictionaried data
        # For possible lead parameters see crm.py.
        
        # Zoho default compulsory fields: Last Name, Company
        
        lead = {
            u"First Name" : u"Mikko",
            u"Last Name" : u"Ohtamaa",
            u"Company" : u"mFabrik Research Oy"   
        }

        # Insert a new lead to Zoho CRM lead database.
        # We support multiple leads per call, so we need to listify our one lead first.
        responses = crm.insert_records([lead]) # This will raise ZohoException if lead data is invalid
        
        # list of responses. one response is {'Modified Time': '2010-10-07 13:24:49', 'Created By': 'Developer', 'Modified By': 'Developer', 'Id': '177376000000253053', 'Created Time': '2010-10-07 13:24:49'}
        # At least one response is guaranteed, otherwise an exception is raised
        
        lead_id = responses[0]["Id"]
        

Special field *Lead Owner* must be the registered email fo Zoho CRM user.        
        
        
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

       