from django.contrib import admin
from .models import Announcement, Notification, EmailNotification


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'target_role', 'publish_date', 'is_published', 'sent_by')
    list_filter = ('priority', 'target_role', 'is_published', 'publish_date')
    search_fields = ('title', 'message')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title')


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'subject', 'sent_at', 'status')
    list_filter = ('status', 'sent_at')
    search_fields = ('recipient', 'subject')