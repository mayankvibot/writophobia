from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)

@register.filter(name='split_strip')
def split_strip(value):
    """
        Returns the value turned into a list separated by comma and stripping each item.
    """
    return [each.strip() for each in value.split(",")]

from comment.utils import (
    is_comment_moderator, is_comment_admin, get_gravatar_img, get_profile_instance, get_wrapped_words_number,
    can_block_user
)

@register.simple_tag(name='get_img_path_custom')
def get_img_path_custom(obj):
    """ returns url of profile image of a user """
    profile = get_profile_instance(obj.user)
    if not profile:
        return get_gravatar_img(obj.email)
    if profile.picture_thumbnail:
        return profile.picture_thumbnail.url
    return get_gravatar_img(obj.email)
