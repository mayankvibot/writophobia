
from django_filters import rest_framework as filters
from django_filters import Filter
from blog.models import Post, PostViews, Profile, PostLikes
from blog.utils import clean_text_to_list
from django.db.models import Count, F, Q


class PostFilter(filters.FilterSet):
    category = Filter(method = 'category_filter')
    subcategory = Filter(method = 'subcategory_filter')
    search = Filter(method = 'search_filter')
    class Meta:
        model = Post
        fields = ['category', 'subcategory']
    
    def category_filter(self, queryset, name, value):
        return queryset.filter(
            category__title = value
        )
    def subcategory_filter(self, queryset, name, value):
        return queryset.filter(
            subcategory__title = value
        )
    def search_filter(self, queryset, name, value):
        value = value.strip()
        if len(value):
            clean_text = clean_text_to_list(value)
            filtered = Q(title__in=clean_text)
            for each in clean_text:
                filtered |= Q(title__icontains=each)
                filtered |= Q(description__icontains=each)
                filtered |= Q(contenttopost__content__icontains=each)
                filtered |= Q(tags__icontains=each)
            return queryset.filter(
                filtered
            ).distinct()
        return queryset