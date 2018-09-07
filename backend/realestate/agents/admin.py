from django.contrib import admin
from .models import AgentPage


@admin.register(AgentPage)
class AgentPageAdmin(admin.ModelAdmin):
    pass
