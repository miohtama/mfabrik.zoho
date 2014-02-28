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
    
    def _parse_json_response(self, data):
        if data["response"].get("nodata"):
            return []
        
        # Sanify output data to more Python-like format
        output = []
        rows = data["response"]["result"]["Leads"]["row"]
        # If single item returned
        if type(rows) == dict:
            rows = [rows]
        for row in rows:
            item = {}
            for cell in row["FL"]:
                item[cell["val"]] = cell["content"]
            
            output.append(item)
            
        return output
    
    def _prepare_xml_request(self, module, leads):
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
        return root
    
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
        
        xmldata = self._prepare_xml_request(module, leads)
        
        post = {
            'newFormat':    1,
            'duplicateCheck':   2
        }
        
        post.update(extra_post_parameters)
        
        response = self.do_xml_call("https://crm.zoho.com/crm/private/xml/" + module + "/insertRecords", post, xmldata)
        
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
        
        return self._parse_json_response(data)
    
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
    
    def update_record(self, module, id, lead):
        """ Update record in Zoho CRM database.
        
        https://www.zoho.com/crm/help/api/updaterecords.html
        
        @param id: String. Zoho CRM lead id.
        
        @param data: Dictionary. Dictionary content is directly mapped to 
            <FL> XML parameters as described in Zoho CRM API.
        
        @return: List of record ids which were updated
        """
        self.ensure_opened()
        
        xmldata = self._prepare_xml_request(module, [lead])
        
        post = {
            'newFormat':    1,
            'duplicateCheck':   2,
            'id': id,
        }
        
        response = self.do_xml_call("https://crm.zoho.com/crm/private/xml/" + module + "/updateRecords", post, xmldata)
        
        self.check_successful_xml(response)
    
    def get_record_by_id(self, id):
        """
        
        https://www.zoho.com/crm/help/api/getrecordbyid.html
        
        @param id: String. Lead id to fetch.
        
        @return: Python dictionary which contains lead key-value pairs.
        
        """
        self.ensure_opened()
        
        
        post_params = {
            "id": id,
            "newFormat" : 2
        }
        
        response = self.do_call("https://crm.zoho.com/crm/private/json/Leads/getRecordById", post_params)
        
        # raw data looks like {'response': {'result': {'Leads': {'row': [{'FL': [{'content': '177376000000142085', 'val': 'LEADID'}, ...
        data =  decode_json(response)
        
        parsed = self._parse_json_response(data)
        
        return parsed[0] if len(parsed) else None
    
    def search_records(self, searchCondition, selectColumns='leads(First Name,Last Name,Company)'):
        """
        
        https://www.zoho.com/crm/help/api/getsearchrecords.html
        
        @param searchCondition: String. Search condition (see ZOHO API doc for details).
        
        @param selectColumns: String. What columns to query. For example query format,
            see API doc. Default is leads(First Name,Last Name,Company).
        
        @return: Python list of dictionarizied leads. Each dictionary contains lead key-value pairs. LEADID column is always included.
        
        """
        self.ensure_opened()
        
        
        post_params = {
            "selectColumns" : selectColumns,
            "searchCondition": searchCondition,
            "newFormat" : 2
        }
        
        response = self.do_call("https://crm.zoho.com/crm/private/json/Leads/getSearchRecords", post_params)
        
        # raw data looks like {'response': {'result': {'Leads': {'row': [{'FL': [{'content': '177376000000142085', 'val': 'LEADID'}, ...
        data =  decode_json(response)
        
        return self._parse_json_response(data)
    
    def search_records_pdc(self, searchColumn, searchValue, selectColumns='leads(First Name,Last Name,Company)'):
        """
        
        https://www.zoho.com/crm/help/api/getsearchrecordsbypdc.html
        
        @param searchColumn: String. Which Predefined column to search.
        
        @param searchValue: String. Value to search for.
        
        @param selectColumns: String. What columns to query. For example query format,
            see API doc. Default is leads(First Name,Last Name,Company).
        
        @return: Python list of dictionarizied leads. Each dictionary contains lead key-value pairs. LEADID column is always included.
        
        """
        self.ensure_opened()
        
        
        post_params = {
            "selectColumns" : selectColumns,
            "searchColumn": searchColumn,
            "searchValue": searchValue,
            "newFormat" : 2
        }
        
        response = self.do_call("https://crm.zoho.com/crm/private/json/Leads/getSearchRecordsByPDC", post_params)
        
        # raw data looks like {'response': {'result': {'Leads': {'row': [{'FL': [{'content': '177376000000142085', 'val': 'LEADID'}, ...
        data =  decode_json(response)
        
        return self._parse_json_response(data)
