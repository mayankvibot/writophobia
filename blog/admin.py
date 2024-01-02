from django.contrib import admin
from blog.models import (
    Profile, 
    Post, 
    PostLikes, 
    PostViews, 
    Category, 
    ContentToPost, 
    SubCategory,
    TrackHits
)
from django.contrib.auth.models import User

# Register your models here.
class ContentToPostAdmin(admin.ModelAdmin):
    model = ContentToPost
    list_display = ('post', 'short_description', 'content_type', 'editor_type', 'priority', 'created_at', 'updated_at')
    search_fields = ('post__title', 'content', 'content_type', 'editor_type', )

class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ('title', 'category', 'subcategory', 'thumbnail', 'author', 'created_at', 'updated_at')

class SubCategoryAdmin(admin.ModelAdmin):
    model = SubCategory
    list_display = ('title', 'category', 'thumbnail', 'created_at', 'updated_at')

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('title', 'thumbnail', 'created_at', 'updated_at')
    
class TrackHitsAdmin(admin.ModelAdmin):
    model = TrackHits
    list_display = ('user', 'city', 'country', 'ip_address', 'requested_url', 'page_title', 'successful', 'created_at')
    search_fields = ('user__username', 'city', 'country', 'ip_address', 'requested_url', 'page_title', )

#admin.site.register(User)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PostLikes)
admin.site.register(PostViews)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(ContentToPost, ContentToPostAdmin)
admin.site.register(TrackHits, TrackHitsAdmin)