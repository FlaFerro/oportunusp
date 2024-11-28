from django.contrib import admin
from .models import Opportunity, Profile

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'posted_by', 'date_posted', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description', 'category')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name','user_type', 'description', 'profile_pic')
    list_filter = ('user_type',)

admin.site.register(Profile, ProfileAdmin)