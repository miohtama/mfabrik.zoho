"""

    Zoho Support API bridge.

"""

__copyright__ = "2013 Local Motors,  mFabrik Research Oy"
__author__ = "Vincent Prime <vprime@local-motors.com>, Mikko Ohtamaa <mikko@mfabrik.com>"
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

class SUPPORT(Connection):
    """ Zoho Support APIs mapped to Python """
    
    """ Define the standard parameter for the XML data """
    parameter_xml = 'xml'

    def get_service_name(self):
        """ Called by base class """
        return "ZohoSupport"

    def add_records(self, records, department, portal, extra_post_parameters={}):
        """ 
            Submits a new support request to Zoho Support 

            @param records: List of dictionaries. Dictionary content is directly mapped to 
            <FL> XML parameters as described in Zoho Support API.

            @param department: String containing the name of the department for the request

            @param portal: String containing the portal name

            @param extra_post_parameters: Parameters appended to the HTTP POST call. 
            Described in Zoho Support API.
        
            @return: List of record ids which were created by add recoreds

        """
        self.ensure_opened()
        
        root = Element("requests")

        # Row counter
        no = 1

        for record in records:
            row = Element("row", no=str(no))
            root.append(row)

            assert type(record) == dict, "Records must be dictionaries inside a list, got:" + str(type(record))
        
            for key, value in record.items():
                # <FL val="Lead Source">Web Download</FL>
                # <FL val="First Name">contacto 1</FL>
                fl = Element("fl", val=key)
                fl.text = value
                row.append(fl)
                
            no += 1

        post = {
            'department': department,
            'portal' : portal 
        }

        post.update(extra_post_parameters)
        
        response = self.do_xml_call("https://support.zoho.com/api/xml/requests/addrecords", post, root)

        self.check_successful_xml(response)
        
        return self.get_inserted_records(response)