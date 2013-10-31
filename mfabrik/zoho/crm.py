"""

    Zoho CRM API bridge.

"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"


try:
    from xml import etree
    from xml.etree.ElementTree import Element, tostring, fromstring, SubElement
except ImportError:
    try:
        from lxml import etree
        from lxml.etree import Element, tostring, fromstring, SubElement
    except ImportError:
        raise RuntimeError("XML library not available:  no etree, no lxml")
   
from core import Connection, ZohoException, decode_json

class CRM(Connection):
    """ CRM specific Zoho APIs mapped to Python """
    
    """ Define the standard parameter for the XML data """
    parameter_xml = 'xmlData'

    def get_service_name(self):
        """ Called by base class """
        return "ZohoCRM"
    
    def insert_records(self, module, leads, extra_post_parameters={}):
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
        
        root = Element(module)

        # Row counter
        no = 1

        for lead in leads:
            row = Element("row", no=str(no))
            root.append(row)

            assert type(lead) == dict, "Leads must be dictionaries inside a list, got:" + str(type(lead))
        
            for key, value in lead.items():
                # <FL val="Lead Source">Web Download</FL>
                # <FL val="First Name">contacto 1</FL>
                fl = Element("FL", val=key)
                if type(value) == dict: # If it's an attached module, accept multiple groups
                    mod_attach_no = 1
                    for module_key, module_value in value.items(): # The first group defines the module name, yank that and iterate through the contents
                        for mod_item in module_value:
                            mod_fl = SubElement(fl, module_key, no=str(mod_attach_no))
                            for mod_item_key, mod_item_value in mod_item.items():
                                attach_fl = SubElement(mod_fl, "FL", val=mod_item_key)
                                attach_fl.text = mod_item_value
                            mod_attach_no += 1
                elif type(value) != str:
                    fl.text = str(value)
                else:
                    fl.text = value
                row.append(fl)

                
            no += 1

        post = {
            'newFormat':    1,
            'duplicateCheck':   2
        }

        post.update(extra_post_parameters)
        
        response = self.do_xml_call("https://crm.zoho.com/crm/private/xml/" + module + "/insertRecords", post, root)

        self.check_successful_xml(response)
                
        return self.get_inserted_records(response)
        
    
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
        