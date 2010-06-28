"""

    Zoho CRM API bridge.

"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"

try:
    from xml import etree
except ImportError:
    # Python 2.4
    try:
        from lxml import etree
    except ImportError:
        raise RuntimeError("lxml or xml libraries or not available")
    
from core import Connection, ZohoException, decode_json

class CRM(Connection):
    """ CRM specific Zoho APIs mapped to Python """
    
    def get_service_name(self):
        """ Called by base class """
        return "ZohoCRM"
    
    def check_successful_xml(self, response):
        """ Make sure that we get "succefully" response.
        
        Throw exception of the response looks like something not liked.
        """

        # Example response
        # <response uri="/crm/private/xml/Leads/insertRecords"><result><message>Record(s) added successfully</message><recorddetail><FL val="Id">177376000000142007</FL><FL val="Created Time">2010-06-27 21:37:20</FL><FL val="Modified Time">2010-06-27 21:37:20</FL><FL val="Created By">Ohtamaa</FL><FL val="Modified By">Ohtamaa</FL></recorddetail></result></response>

        root = etree.fromstring(response)
        
        # Check error response
        # <response uri="/crm/private/xml/Leads/insertRecords"><error><code>4401</code><message>Unable to populate data, please check if mandatory value is entered correctly.</message></error></response>
        for error in root.iter("error"):
            for message in error.iter("message"):
                raise ZohoException(message.text)
    
    def insert_records(self, leads, extra_post_parameters={}):
        """ Insert one new lead to Zoho CRM database.
        
        The contents of the lead parameters can be defined in Zoho CRM itself.
        
        http://zohocrmapi.wiki.zoho.com/insertRecords-Method.html
        
        @param leads: List of dictionaries. Dictionary content is directly mapped to 
            <FL> XML parameters as described in Zoho CRM API.
        
        @param extra_post_parameters: Parameters appended to the HTTP POST call. 
            Described in Zoho CRM API.
        
        """        

        # Ba
        self.ensure_opened()
        
        root = etree.Element("Leads")

        # Row counter
        no = 1

        for lead in leads:
            row = etree.Element("row", no=str(no))
            root.append(row)

            assert type(lead) == dict, "Leads must be dictionaries inside a list, got:" + str(type(lead))
        
            for key, value in lead.items():
                # <FL val="Lead Source">Web Download</FL>
                # <FL val="First Name">contacto 1</FL>
                fl = etree.Element("fl", val=key)
                fl.text = value
                row.append(fl)
                
            no += 1

        post = {
            'newFormat':    1,
            'duplicateCheck':   2
        }

        post.update(extra_post_parameters)
        
        response = self.do_xml_call("http://crm.zoho.com/crm/private/xml/Leads/insertRecords", post, root)
        

        self.check_successful_xml(response)
    
    def get_records(self, selectColumns='leads(First Name,Last Name,Company)', parameters={}):
        """ 
        
        http://zohocrmapi.wiki.zoho.com/getRecords-Method.html
        
        @param selectColumns: String. What columns to query. For example query format,
            see API doc. Default is leads(First Name,Last Name,Company).
        
        @param parameters: Dictionary of filtering parameters which are part of HTTP POST to Zoho.
            For example parameters see Zoho CRM API docs.
        
        @return: Python list of dictionarizied leads. Each dictionary contains lead key-value pairs. LEADID column is always included.

        """
        
        self.ensure_opened()
        

        post_params = {
            "selectColumns" : selectColumns,
            "newFormat" : 2
        }
        
        post_params.update(parameters)

        response = self.do_call("http://crm.zoho.com/crm/private/json/Leads/getRecords", post_params)
        
        # raw data looks like {'response': {'result': {'Leads': {'row': [{'FL': [{'content': '177376000000142085', 'val': 'LEADID'}, ...
        data =  decode_json(response)
        
        # Sanify output data to more Python-like format
        output = []
        for row in data["response"]["result"]["Leads"]["row"]:
            item = {}
            for cell in row["FL"]:
                item[cell["val"]] = cell["content"]
            
            output.append(item)
            
        return output
        
                
    def delete_record(self, id, parameters={}):
        """ Delete one record from Zoho CRM.
        
        
        
        @param id: Record id
        
        @param parameters: Extra HTTP post parameters
        
        """
        
        self.ensure_opened()
    
        post_params = {}
        post_params[id] = id
        post_params.update(parameters)
        
        response = self.do_call("http://crm.zoho.com/crm/private/xml/Leads/deleteRecords", post_params)
        
        self.check_successful_xml(response)
        