from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Comment, Like, User, WorshipRecord


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'real_name', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('real_name',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('real_name',)}),
    )


@admin.register(WorshipRecord)
class WorshipRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'title', 'worship_type', 'user', 'is_shared')
    list_filter = ('worship_type', 'is_shared', 'date')
    search_fields = ('title', 'content')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'record', 'created_at')
    list_filter = ('created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'record', 'created_at')
