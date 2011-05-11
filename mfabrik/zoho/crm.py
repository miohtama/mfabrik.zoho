"""

    Zoho CRM API bridge.

"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"


try:
    from xml import etree
    from xml.etree.ElementTree import Element, tostring, fromstring
except ImportError:
    try:
        from lxml import etree
        from lxml.etree import Element, tostring, fromstring
    except ImportError:
        raise RuntimeError("XML library not available:  no etree, no lxml")
   
from core import Connection, ZohoException, decode_json

class CRM(Connection):
    """ CRM specific Zoho APIs mapped to Python """
    
    def get_service_name(self):
        """ Called by base class """
        return "ZohoCRM"
    
    def check_successful_xml(self, response):
        """ Make sure that we get "succefully" response.
        
        Throw exception of the response looks like something not liked.
        
        @raise: ZohoException if any error
        
        @return: Always True
        """

        # Example response
        # <response uri="/crm/private/xml/Leads/insertRecords"><result><message>Record(s) added successfully</message><recorddetail><FL val="Id">177376000000142007</FL><FL val="Created Time">2010-06-27 21:37:20</FL><FL val="Modified Time">2010-06-27 21:37:20</FL><FL val="Created By">Ohtamaa</FL><FL val="Modified By">Ohtamaa</FL></recorddetail></result></response>

        root = fromstring(response)
            
        # Check error response
        # <response uri="/crm/private/xml/Leads/insertRecords"><error><code>4401</code><message>Unable to populate data, please check if mandatory value is entered correctly.</message></error></response>
        for error in root.findall("error"):
            print "Got error"
            for message in error.findall("message"):
                raise ZohoException(message.text)
        
        return True
    
    def insert_records(self, leads, extra_post_parameters={}):
        """ Insert new leads to Zoho CRM database.
        
        The contents of the lead parameters can be defined in Zoho CRM itself.
        
        http://zohocrmapi.wiki.zoho.com/insertRecords-Method.html
        
        @param leads: List of dictionaries. Dictionary content is directly mapped to 
            <FL> XML parameters as described in Zoho CRM API.
        
        @param extra_post_parameters: Parameters appended to the HTTP POST call. 
            Described in Zoho CRM API.
        
        @return: List of record ids which were created by insert recoreds
        """        

        self.ensure_opened()
        
        root = Element("Leads")

        # Row counter
        no = 1

        for lead in leads:
            row = Element("row", no=str(no))
            root.append(row)

            assert type(lead) == dict, "Leads must be dictionaries inside a list, got:" + str(type(lead))
        
            for key, value in lead.items():
                # <FL val="Lead Source">Web Download</FL>
                # <FL val="First Name">contacto 1</FL>
                fl = Element("fl", val=key)
                fl.text = value
                row.append(fl)
                
            no += 1

        post = {
            'newFormat':    1,
            'duplicateCheck':   2
        }

        post.update(extra_post_parameters)
        
        response = self.do_xml_call("https://crm.zoho.com/crm/private/xml/Leads/insertRecords", post, root)

        self.check_successful_xml(response)
                
        return self.get_inserted_records(response)
        
    
    def get_inserted_records(self, response):
        """
        @return: List of record ids which were created by insert recoreds
        """
        root = fromstring(response)
        
        records = []
        for result in root.findall("result"):
            for record in result.findall("recorddetail"):
                record_detail = {}
                for fl in record.findall("FL"):
                    record_detail[fl.get("val")] = fl.text
                records.append(record_detail)
        return records
        
    
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

        response = self.do_call("https://crm.zoho.com/crm/private/json/Leads/getRecords", post_params)
        
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
        post_params["id"] = id
        post_params.update(parameters)
        
        response = self.do_call("https://crm.zoho.com/crm/private/xml/Leads/deleteRecords", post_params)
        
        self.check_successful_xml(response)
        