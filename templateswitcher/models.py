from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

#from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^ckeditor\.fields\.RichTextField"])

template_sets = map(lambda k: (k,k), settings.DEVICE_TEMPLATE_DIRS.keys())

#==============================================================================
class Page(models.Model):
    url = models.CharField(max_length=512)
    title = models.CharField(max_length=255, help_text='A short, descriptive title.')
    sub_title = models.CharField(max_length=255, blank=True, null=True, help_text='A short, descriptive sub title.')
    strapline = models.CharField(max_length=500, help_text='A very short description.', blank=True, null=True)
    content = RichTextField(help_text='The actual, formatted content.')
    template = models.CharField(max_length=512, blank=True)
    template_set = models.CharField(
                        max_length=20,
                        blank=True,
                        choices=template_sets
                        )
    
    #--------------------------------------------------------------------------
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Flat Page'
        verbose_name_plural = 'Flat Pages'