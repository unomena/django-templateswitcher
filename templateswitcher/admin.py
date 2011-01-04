from django.contrib import admin
from models import *

#==============================================================================
class PageAdmin(admin.ModelAdmin):
    list_display = ('title','url', 'template_set')

admin.site.register(Page, PageAdmin)