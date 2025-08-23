from django.contrib import admin
from .models import Quote

# Register your models here.
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text', 'source', 'weight', 'likes', 'dislikes', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('text', 'source')
    readonly_fields = ('created_at',)