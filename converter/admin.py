from django.contrib import admin
from converter.models import Currency, FullName, LastUpdateTable
# Register your models here.


admin.site.register(Currency)
admin.site.register(FullName)
admin.site.register(LastUpdateTable)
