from django.contrib import admin
from .models import Activity, ActivityLog


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'activity_type', 'status', 'planned_date', 'created_at']
    list_filter = ['activity_type', 'status', 'created_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'activity_type')
        }),
        ('Status & Dates', {
            'fields': ('status', 'planned_date', 'completed_date')
        }),
        ('Metrics', {
            'fields': ('duration_minutes', 'calories_burned', 'calories_consumed', 'steps_count'),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['activity', 'old_status', 'new_status', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['activity__title', 'activity__user__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('activity', 'activity__user')