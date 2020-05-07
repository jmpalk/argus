from django.contrib import admin

from .models import Scan, Host, Port

# Register your models here.
admin.site.register(Scan)
admin.site.register(Port)
admin.site.register(Host)

