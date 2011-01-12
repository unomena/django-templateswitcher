import os
import importlib

from django.http import Http404
from django.conf import settings
from django.core.cache import cache

from templateswitcher.views import flatpageview

#from mobile.sniffer.chain import ChainedSniffer

#==============================================================================
class TemplateDirSwitcher(object):
    """
    Template Switching Middleware. Switches template dirs by using preset conditions
    and device families according to the devices capabilities. Returns the device
    object in the request object and resets the TEMPLATE_DIRS attr in the project 
    settings.
    """
    
    #--------------------------------------------------------------------------
    def process_request(self, request):
        if request.path.startswith("/admin"):
            return None
        
        device_families = importlib.import_module(getattr(settings, 'DEVICE_FAMILIES', 'templateswitcher.device_families'))
        device_obj = getattr(request, 'device', None)
        # Use hash as the key since UA's can be quite llong, dont want to hit memcache 250 byte limit
        device_cache_key = hash(request.META['HTTP_USER_AGENT'])
        template_set = cache.get(device_cache_key)
        full_path = request.get_full_path()
        media_request = (full_path.startswith(settings.MEDIA_URL) or
                        full_path.startswith(settings.ADMIN_MEDIA_PREFIX) or full_path.startswith('/favicon'))
        
        if not template_set:
            
            template_set = request.META['TEMPLATE_SET']
            
#            # set the device switcher library according to the settings - defaults to wurfl
#            device_switch_libs = getattr(settings, 'DEVICE_SWITCH_LIB', ['WurlfSniffer'])
#            da_api = getattr(settings, 'DEVICE_ATLAS_API_FILE', None)
#            device_cache_timeout = getattr(settings, 'DEVICE_CACHE_TIMEOUT', 72000)
#                
#            # import requied device library classes
#            if 'ApexVertexSniffer' in device_switch_libs:
#                from mobile.sniffer.apexvertex.sniffer import ApexVertexSniffer
#            if 'WAPProfileSniffer' in device_switch_libs:
#                from mobile.sniffer.wapprofile.sniffer import WAPProfileSniffer
#            if 'DeviceAtlasSniffer' in device_switch_libs:
#                if not os.path.exists(da_api):
#                    raise Exception('DEVICE_ATLAS_API_FILE must be in your setting and contain a valid path to use Device Atlas.')
#                from mobile.sniffer.deviceatlas.sniffer import DeviceAtlasSniffer
#            if 'WurlfSniffer' in device_switch_libs:
#                from mobile.sniffer.wurlf.sniffer import WurlfSniffer
#            
#            chained_libs = []
#            for device_lib in device_switch_libs:
#                chained_libs.append(eval(device_lib)())
#            
#            # instantiate the sniffer and device object
#            sniffer = ChainedSniffer(chained_libs)
#            device_object = sniffer.sniff(request)
#            template_set = device_families.get_device_family(device_object)
#                
#            # copy the device object to the request object
#            request.device = device_object
#            cache.set(device_cache_key, template_set, device_cache_timeout)
            
        if not media_request:
            # switch the template dir for the given device
            settings.TEMPLATE_DIRS = settings.DEVICE_TEMPLATE_DIRS[template_set]
        
        request.template_set = template_set

        return None

#==============================================================================
class FlatpageFallbackMiddleware(object):
    """
    Template Switching Flatpages.   Works exactly the same as regular flatpages,
    just template-set aware.
    """
    
    #--------------------------------------------------------------------------
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            return flatpageview(request)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response