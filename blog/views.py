from django.shortcuts import render
from blog.models import Post, PostViews, Profile, PostLikes, ContentToPost, Category, SubCategory, TrackHits
from django.http import HttpResponse
from django.db.models import F
from django.views import View
from blog.filter import PostFilter
from django.db.models import Case, When, Count
from blog.utils import get_image_url, encode_url, get_pk_from_url, add_image_and_url, get_location
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

class BlogBase:
    @staticmethod
    def get_categories_queryset():
        return Category.objects.filter(
            visible = True
        ).annotate(
            total_count = Count('post')
        ).order_by('-priority')
    
    @staticmethod
    def get_subcategories_queryset():
        return SubCategory.objects.filter(
            visible = True
        ).order_by(
            '-priority'
        )

    @staticmethod
    def save_hits(request, title, successful = True):
        loc = get_location(request)
        hit_data = TrackHits.objects.create(
            city = loc['city'],
            country = loc['country'],
            ip_address = loc['ip'],
            requested_url = request.build_absolute_uri(),
            page_title = title,
            successful = successful
        )
        if request.user.is_authenticated:
            hit_data.user = request.user
            hit_data.save()
        return

    @staticmethod
    def build_canonical_url(request):
        params = [f'{each}={request.GET[each]}' for each in request.GET if each in ['category', 'subcategory', 'search']]
        if len(params):
            return request.build_absolute_uri(request.path) + "?" + "&".join(params)
        return request.build_absolute_uri(request.path)

class BlogSelectedView(View):
    main_queryset = Post.objects.filter(visible = True)
    queryset = Post.objects.filter(visible = True, visible_at_homepage = True)
    template_name = 'blog/blog_main_new.html'

    def get_queryset(self, post_id):
        return self.main_queryset.filter(
            id = post_id
        )
    
    def extend_qs_list(self, _qs, exclude_list):
        _new_exclude = _qs.exclude(
            id__in = exclude_list
        ).order_by(
            '-priority', '-created_at'
        ).values_list(
            'id', flat = True
        )
        exclude_list.extend(_new_exclude)
        return exclude_list

    def get_suggested_queryset(self, post_obj):
        exclude_list = [post_obj.id]

        _qs = self.queryset.filter(
            subcategory = post_obj.subcategory, category = post_obj.category
        ).exclude(
            id__in = exclude_list
        ).order_by(
            '-priority', '-created_at'
        )

        if _qs.count() < 10:
            exclude_list = self.extend_qs_list(_qs, exclude_list)
            _qs2 = self.queryset.filter(category = post_obj.category)
            exclude_list = self.extend_qs_list(_qs2, exclude_list)
            
            if len(exclude_list) < 10:
                exclude_list = self.extend_qs_list(self.queryset, exclude_list)
        
            exclude_list = exclude_list[1:]
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(exclude_list)])
            final_list = self.queryset.filter(id__in=exclude_list).order_by(preserved)[0:10]
            return final_list
        return _qs

    def get(self, request, pk):
        pk = get_pk_from_url(pk)
        obj = self.get_queryset(pk)
        if obj.count():
            post_obj = obj.first()
            if post_obj.code != request.GET.get('code', None):
                return HttpResponse("Password Protected")

            post_obj.views += 1
            post_obj.save()

            post_obj.contents = ContentToPost.objects.filter(post__id = pk).order_by(
                'priority', 'created_at', 'updated_at', 'id'
            )

            if request.user.is_authenticated:
                PostViews.objects.create(user = request.user, post = post_obj)
            
            BlogBase.save_hits(request, post_obj.title)

            context = {
                "post_obj": get_image_url(post_obj),
                "suggestions": add_image_and_url(self.get_suggested_queryset(post_obj)[:10]),
                "popular_posts": add_image_and_url(self.queryset.order_by('-views')[0:3]),
                "latest_posts": add_image_and_url(self.queryset.order_by('-created_at')[0:3]),
                "categories": BlogBase.get_categories_queryset(),
                "subcategories": BlogBase.get_subcategories_queryset(),
                "canonical_url": BlogBase.build_canonical_url(request)
            }
            return render(request, self.template_name, context)
        BlogBase.save_hits(request, "Not found", False)
        return HttpResponse("Not Found")


class HomeView(View):
    queryset = Post.objects.filter(visible = True, visible_at_homepage = True)
    template_name = 'blog/home_main.html'
    filter_class = PostFilter

    def get_queryset(self):
        return self.filter_class(
            self.request.GET, self.queryset
        ).qs.order_by(
            '-priority', '-views', '-id',
        )
    
        

    def get(self, request):
        page_number = request.GET.get('page')
        post_objects = self.get_queryset()
        paginator = Paginator(post_objects, 3)
        page_obj = paginator.get_page(page_number)

        params = "&".join([f'{each}={request.GET[each]}' for each in request.GET if each != "page"])

        context = {
            "post_objects": add_image_and_url(page_obj),
            "page_range": range(1, page_obj.paginator.num_pages + 1),
            "params": params,
            "categories": BlogBase.get_categories_queryset(),
            "subcategories": BlogBase.get_subcategories_queryset(),
            "searched": request.GET.get('search','').strip(" "),
            "canonical_url": BlogBase.build_canonical_url(request)
        }

        BlogBase.save_hits(request, "Homepage")
        return render(request, self.template_name, context)


class BlogLikeView(View):
    queryset = Post.objects.all()

    def get_queryset(self):
        return get_object_or_404(
            self.queryset, 
            self.request.query_params.get('post_id')
        )
        

    def post(self, request):
        post_obj = self.get_queryset()
        obj, created = PostLikes.objects.get_or_create(
            post = post_obj, 
            user = request.user
        ) 
        if not created:
            obj.delete()
        return HttpResponse({'status': 200, "created": created})
    

class ProfileView(View):
    template_name = 'blog/profile.html'

    def get_queryset(self, username):
        return Profile.objects.filter(username = username)
    
    def get_post_objects(self, username):
        return Post.objects.filter(
            visible = True, 
            visible_at_homepage = True, 
            author__username = username
        ).order_by(
            '-priority', '-views', '-id',
        )
    
    def get(self, request, username = None):
        if not username and request.user.is_authenticated:
            username = request.user.username
        user_details = self.get_queryset(username)
        if user_details.count():
            user_details = user_details.first()
            context = {
                "user_details": user_details,
                "post_objects": add_image_and_url(self.get_post_objects(username)),
                "categories": BlogBase.get_categories_queryset(),
                "subcategories": BlogBase.get_subcategories_queryset(),
                "canonical_url": BlogBase.build_canonical_url(request)
            }
            
            BlogBase.save_hits(request, user_details.username)
            return render(request, self.template_name, context)
        
        BlogBase.save_hits(request, "Not Found", False)
        return HttpResponse("Not Found")


class ContactView(View):
    template_name = 'blog/contact.html'
    def get(self, request):
        context = {
            "categories": BlogBase.get_categories_queryset(),
            "subcategories": BlogBase.get_subcategories_queryset(),
            "canonical_url": BlogBase.build_canonical_url(request)
        }
        return render(request, self.template_name, context)
    


"""
1. API Creation



2. API Calling



"""
import json
class APICreate(View):
    # 127.0.0.1:8000/api_create
    def get(self, request):
        # API Creation
        context = {
            "name": "Swati Mishra",
            "age": 25,
            "profession": "Engineer"
        }
        return HttpResponse(json.dumps(context))