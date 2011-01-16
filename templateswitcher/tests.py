import unittest

from django.conf import settings
from django.test.client import Client

class TemplateDirSwitcherTestCase(unittest.TestCase):
    def setUp(self):
        self.user_agents = {
            'basic': "LGE-AX4750",
            'high': "Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaE63-1/100.21.110; Profile/MIDP-2.0 Configuration/CLDC-1.1 ) AppleWebKit/413 (KHTML, like Gecko) Safari/413",
            'ipad': "Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10",
        }
    
    def testBypassAdmin(self):
        """
        Test any admin urls are bypassed.
        """
        client = Client()
        extras = {settings.USERAGENT_HEADER_KEY: self.user_agent_basic}
        response = client.get('/admin', **extras)
        self.failUnlessEqual(response.status_code, '200', "Admin urls could not be bypassed.")
    
    def testGetTemplateSetBasic(self):
        """
        Test that the correct template set is returned.
        """
        count = 0
        for k, v in self.user_agents:
            client = Client()
            extras = {
                settings.USERAGENT_HEADER_KEY: self.user_agents[k],
            }
            response = client.get('/', **extras)
            
            self.FailUnlessEqual(settings.TEMPLATE_DIRS[0], settings.DEVICE_TEMPLATE_DIRS[count])
            count += 1
