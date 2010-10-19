"""

    Zoho API core functions.

"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"

import urllib, urllib2

import logging

try:
    from xml import etree
    from xml.etree.ElementTree import Element, tostring, fromstring
except ImportError:
     try:
         from lxml import etree
         from lxml.etree import  Element, tostring, fromstring
     except ImportError:
         print "XML library not available:  no etree, no lxml"
         raise
   

try:
    import json
except ImportError:
    try:
        import simplejson
    except ImportError:
        # Python 2.4, no simplejson installed
        raise RuntimeError("You need json or simplejson library with your Python")


logger = logging.getLogger("Zoho API")


class ZohoException(Exception):
    """ Bad stuff happens. 
    
    If it's level 15 or higher bug, you usually die.
    If it's lower level then you just lose all your data.
    
    Play some Munchkin.
    """


class Connection(object):
    """ Zoho API connector.
        
    Absract base class for all different Zoho API connections.
    Subclass this and override necessary methods to support different Zoho API groups.
    """

    
    def __init__(self, username, password, apikey, extra_auth_params = {}, auth_url="https://accounts.zoho.com/login"):        
        """
        @param username: manifisto@mfabrik.com 
        
        @param password: xxxxxxx
        
        @param apikey: Given by Zoho, string like 123123123-rVI20JVBveUOHIeRYWV5b5kQaMGWeIdlI$
                
        @param extra_auth_params: Dictionary of optional HTTP POST parameters passed to the login call
        
        
        @param auth_url: Which URL we use for authentication
        """        
        self.username = username
        self.password = password
        self.apikey = apikey
        # 
        self.auth_url = None
        
        # Ticket is none until the conneciton is opened
        self.ticket = None
        
    def get_service_name(self):
        """ Return API name which we are using. """
        raise NotImplementedError("Subclass must implement")
        
    def open(self):
        """ Open a new Zoho API session """
        self.ticket = self._create_ticket()
    
    def _create_ticket(self):
        """ 
        Ticket idenfities Zoho session.
        
        It is a bit like cookie authentication.
        
        @return: Ticket code
        """
        #servicename=ZohoCRM&FROM_AGENT=true&LOGIN_ID=Zoho Username or Email Address&PASSWORD=Password
        params = {
            'servicename': self.get_service_name(),
            'FROM_AGENT': 'true',
            'LOGIN_ID': self.username,
            'PASSWORD': self.password
        }
        
        requestUrl = "https://accounts.zoho.com/login?%s" % (urllib.urlencode(params))
        request = urllib2.Request(requestUrl, None)
        body = urllib2.urlopen(request).read()
        
        data = self._parse_ticket_response(body)
        
        if data["WARNING"] != "null":
            # Zoho has set an error field
            raise ZohoException("Could not auth:" + data["WARNING"])
        
        if data["RESULT"] != "TRUE":
            raise ZohoException("Ticket result was not valid")

        return data["TICKET"]
    
    def _parse_ticket_response(self, data):
        """ Dictionarize ticket opening response
       
        Example response::
        
            # #Sun Jun 27 20:10:30 PDT 2010 GETUSERNAME=null WARNING=null PASS_EXPIRY=-1 TICKET=3bc26b16d97473a1245dbf93a5dcd153 RESULT=TRUE 
        """
        
        output = {}
        
        lines = data.split("\n")
        for line in lines:
            
            if line.startswith("#"):
                # Comment
                continue
            
            if line.strip() == "":
                # Empty line
                continue
            
            if not "=" in line:
                raise ZohoException("Bad ticket data:" + data)
        
            key, value = line.split("=")
            output[key] = value
            
        return output

    def ensure_opened(self):
        """ Make sure that the Zoho Connection is correctly opened """
        
        if self.ticket is None:
            raise ZohoException("Need to initialize Zoho ticket first")
        
    def do_xml_call(self, url, parameters, root):
        """  Do Zoho API call with outgoing XML payload.
        
        Ticket and apikey parameters will be added automatically.
        
        @param url: URL to be called
        
        @param parameters: Optional POST parameters. 
        
        @param root: ElementTree DOM root node to be serialized.
        """
        
        parameters = parameters.copy()
        parameters["xmlData"] = tostring(root)
        return self.do_call(url, parameters)

    def do_call(self, url, parameters):
        """ Do Zoho API call.
        
        @param url: URL to be called
        
        @param parameters: Optional POST parameters. 
        """
        # Do not mutate orginal dict
        parameters = parameters.copy()
        parameters["ticket"] = self.ticket
        parameters["apikey"] = self.apikey
        
        stringify(parameters)
        
        if logger.getEffectiveLevel() == logging.DEBUG:                                          
            # Output Zoho API call payload
            logger.debug("Doing ZOHO API call:" + url)
            for key, value in parameters.items():
                logger.debug(key + ": " + value)
                
        request = urllib2.Request(url, urllib.urlencode(parameters))
        response = urllib2.urlopen(request).read()

        if logger.getEffectiveLevel() == logging.DEBUG:                                          
            # Output Zoho API call payload
            logger.debug("ZOHO API response:" + url)
            logger.debug(response)
        
        return response

def stringify(params):
    """ Make sure all params are urllib compatible strings """
    for key, value in params.items():
        
        if type(value) == str:
            params[key] == value.decode("utf-8")
        elif type(value) == unicode:
            pass
        else:
            # call __unicode__ of object
            params[key] = unicode(value)
            

def decode_json(json_data):
    """ Helper function to handle Zoho specific JSON decode.

    @return: Python dictionary/list of incoming JSON data
    
    @raise: ZohoException if JSON'ified error message is given by Zoho
    """
    
    # {"response": {"uri":"/crm/private/json/Leads/getRecords","error": {"code":4500,"message":"Problem occured while processing the request"}}}
    data = simplejson.loads(json_data)
    
    response = data.get("response", None)
    if response:
        error = response.get("error", None)
        if error:
            raise ZohoException("Error while calling JSON Zoho api:" + str(error))
    
    return data