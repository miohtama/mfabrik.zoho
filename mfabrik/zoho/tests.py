# -*- coding: utf-8 -*-
"""

    Zoho API bridge unit tests.
    
    These unit-test assume you have set-up your user account specific environment varibles:
    
    * ZOHO_USERNAME
    
    * ZOHO_PASSWORD
    
    * ZOHO_APIKEY
    
    Since you are probably using proudction Zoho database to testing, 
    all tests include clean-up functions which should clear all test data
    if tests are succesfully completed.

"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"

import os, sys
import unittest

#import mfabrik
#from mfabrik import zoho
from crm import CRM
from core import ZohoException
     
def enable_debug_log():
    """ Enable context.plone_log() output from Python scripts """
    import sys, logging
    from Products.CMFPlone.log import logger
    logger.root.setLevel(logging.DEBUG)
    logger.root.addHandler(logging.StreamHandler(sys.stdout))

enable_debug_log()

class TestCRM(unittest.TestCase):
    """ Zoho CRM specific tests. """

    def setUp(self):
        
        
        self.username = os.environ.get("ZOHO_USERNAME", None)
        self.password = os.environ.get("ZOHO_PASSWORD", None)
        self.apikey = os.environ.get("ZOHO_APIKEY", None)
        
        if self.username and self.password and self.apikey:
            # All ok
            pass
        else:
            raise RuntimeError("Please set-up unit-test environment variables: ZOHO_USERNAME, ZOHO_PASSWORD and ZOHO_APIKEY to run tests")

        # Initialize Zoho CRM api connection
        # You get necessary data from Zoho > Setup > Admin > Developer key
        self.crm = CRM(username=self.username, password=self.password, apikey=self.apikey)

        # Open connection can be used to make as many as possible API calls
        self.crm.open()
        
        self.clear_test_leads()
        
    def tearDown(self):
        self.clear_test_leads()
        

    def add_dummy_lead(self):

        # Lead is just a bunch of dictionaried data
        # For possible lead parameters see crm.py.
        # Include non-ASCII characters.
        
        lead = {
            u"First Name" : u"TEST",
            u"Last Name" : u"UNIT TEST ÅÄÖ",
            u"Company" : u"mFabrik Research Oy"   
        }

        # Insert a new lead to Zoho CRM lead database.
        # We support multiple leads per call, so we need to listify our one lead first.
        self.crm.insert_records([lead])
        
    def clear_test_leads(self):
        """ Remove all test leads from the database """
        
        records = self.crm.get_records()
        
        for record in records:
            if record["First Name"] == "TEST":
                self.crm.delete_record(record["LEADID"])
        
        
    def test_insert_lead(self):
        """ Sample insert lead scenario. """

        self.add_dummy_lead()

        
    def xxx_test_insert_duplicate(self):
        """ What happens when a duplicate lead is inserted """

        self.add_dummy_lead()
        self.add_dummy_lead()

        # TODO: Need to figure out how to force Zoho correctly detect duplicates
        
    def test_insert_missing_field(self):
        """ Company and Last name are required lead fields """

        
        lead = {
            "First Name" : "Who?"
        }

        try:
            self.crm.insert_records([lead])
            raise AssertionError("Should not be reached")
        except ZohoException:
            pass
        
    def test_get_leads(self):

        # Make sure we have add least one lead there
        self.add_dummy_lead()
        
        leads = self.crm.get_records()
        print "Got leads"
        print leads
        
    def test_delete_leads(self):

        # Make sure we have add least one lead there
        self.add_dummy_lead()
        
        records = self.crm.get_records()
        
        # Count number of test items
        counter = 0
        for r in records:
            if r["First Name"] == "TEST":
                counter += 1
                
        self.assertEqual(counter, 1)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCRM))
    return suite

if __name__ == '__main__':
    unittest.main()