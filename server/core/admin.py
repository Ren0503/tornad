from django.contrib import admin
from datetime import timedelta
from .models import Write, Vote

# Register your models here.


class AdminWrite(admin.ModelAdmin):
    list_display = ('user', 'vote_rank', 'created', 'get_utc')
    search_fields = ('user',)
    list_filter = ('created', 'vote_rank', 'user',)
    empty_value_display = '-empty field-'

    def get_utc(self, obj):
        return obj.created + timedelta(minutes=330)

    get_utc.short_description = 'Created (UTC)'


class AdminVote(admin.ModelAdmin):
    list_display = ('user', 'write', 'value')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-empty field-'


admin.site.register(Write, AdminWrite)
admin.site.register(Vote, AdminVote)
