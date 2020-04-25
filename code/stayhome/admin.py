from django.contrib import admin
from .models import User, Card, HashTags

admin.site.register(User)
admin.site.register(Card)
admin.site.register(HashTags)
