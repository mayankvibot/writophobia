from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.template.defaultfilters import truncatechars
from blog.utils import compress_image
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from comment.models import Comment


class Profile(User):
    user_type = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='user/picture', blank=True, null=True)
    picture_thumbnail = models.ImageField(upload_to='user/picture_thumbnail', blank=True, null=True, help_text='upload max of 200X200')
    visible = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    facebook_url = models.CharField(max_length=100, blank=True, null=True)
    youtube_url = models.CharField(max_length=100, blank=True, null=True)
    twitter_url = models.CharField(max_length=100, blank=True, null=True)
    linkedin_url = models.CharField(max_length=100, blank=True, null=True)
    instagram_url = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})
    
    def get_title_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between and in title case.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip().title()
    
class Category(models.Model):
    title = models.CharField(max_length=50)
    thumbnail = models.ImageField(upload_to='category/thumbnail', blank=True, null=True)
    thumbnail_500 = models.ImageField(upload_to='category/thumbnail_500', blank=True, null=True)
    thumbnail_200 = models.ImageField(upload_to='category/thumbnail_200', blank=True, null=True)
    visible = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    
    def save(self):
        if self.thumbnail:
            self = compress_image(self)
        super(Category, self).save()


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    thumbnail = models.ImageField(upload_to='subcategory/thumbnail', blank=True, null=True)
    thumbnail_500 = models.ImageField(upload_to='subcategory/thumbnail_500', blank=True, null=True)
    thumbnail_200 = models.ImageField(upload_to='subcategory/thumbnail_200', blank=True, null=True)
    visible = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    
    def save(self):
        if self.thumbnail:
            self = compress_image(self)
        super(SubCategory, self).save()


class Post(models.Model):
    title = models.CharField(max_length=512)
    description = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True, help_text="Add tags comma separated without space")
    views = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='post/thumbnail', blank=True, null=True)
    thumbnail_500 = models.ImageField(upload_to='post/thumbnail_500', blank=True, null=True)
    thumbnail_200 = models.ImageField(upload_to='post/thumbnail_200', blank=True, null=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    visible = models.BooleanField(default=True)
    visible_at_homepage = models.BooleanField(default=False)
    code = models.CharField(max_length=50, blank=True, null=True)
    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = GenericRelation(Comment)

    def get_absolute_url(self):
        return reverse('post_detail_url', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title
    # Multieditor reference link: https://blog.devgenius.io/best-free-wysiwyg-editor-python-django-admin-panel-integration-d9cb30da1dba

    def save(self, *args, **kwargs):
        if self.thumbnail:
            if not self._state.adding:
                obj = Post.objects.get(id = self.id)
                if obj.thumbnail != self.thumbnail:
                    self = compress_image(self)
            else:
                self = compress_image(self)
        super(Post, self).save()

class ContentToPost(models.Model): 
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='post/image', blank=True, null=True)
    content = models.TextField(blank=True, null=True, help_text="If image has been chosen, this field will work as image description")
    content_type = models.CharField(max_length=64, blank=True, null=True, default = "text")
    editor_type = models.CharField(max_length=64, blank=True, null=True) 
    priority = models.IntegerField(default=1, help_text="Here priority in ascending order like 1 will appear on top")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def short_description(self):
        return truncatechars(self.content, 50)


class PostLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_type = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PostViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    city = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    ip_address = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TrackHits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    ip_address = models.CharField(max_length=128, blank=True, null=True)
    requested_url = models.CharField(max_length=512, blank=True, null=True)
    page_title = models.CharField(max_length=128, blank=True, null=True)
    successful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)