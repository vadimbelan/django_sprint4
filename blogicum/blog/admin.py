from django.contrib import admin
from .models import Post, Category, Location


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'created_at')
    empty_value_display = '—'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')
    empty_value_display = '—'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'is_published', 'category')
    list_editable = ('is_published',)
    search_fields = ('title', 'text')
    list_filter = ('is_published', 'pub_date', 'category')
    date_hierarchy = 'pub_date'
    empty_value_display = '—'
