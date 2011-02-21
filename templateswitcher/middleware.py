import ua_mapper
from ua_mapper.mapper import UAMapper

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
        # Use hash as the key since UA's can be quite llong, dont want to hit memcache 250 byte limit
        device_cache_key = hash(request.META['HTTP_USER_AGENT'])
        template_set = cache.get(device_cache_key)
        full_path = request.get_full_path()
        media_request = (full_path.startswith(settings.MEDIA_URL) or
                        full_path.startswith(settings.ADMIN_MEDIA_PREFIX) or full_path.startswith('/favicon'))
        
        if not template_set:
            
            template_set = ua_mapper.get_template_set(request.META['HTTP_USER_AGENT'])
            
            if not template_set:
                
                mapper = UAMapper()
                user_agent, device, template_set = mapper.map_by_request(request) 
            
            device_cache_timeout = getattr(settings, 'DEVICE_CACHE_TIMEOUT', 72000)
            cache.set(device_cache_key, template_set, device_cache_timeout)            
            
        if not media_request and template_set:
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