from django.contrib import admin

from .models import User,Transaction,Category

admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Category)