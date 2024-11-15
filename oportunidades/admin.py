from django.contrib import admin
from .models import Opportunity

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'posted_by', 'date_posted', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description', 'category')
