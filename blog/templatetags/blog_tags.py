from django import template
from ..models import Post
from django.db.models import Count

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    ''' C по мощью функции annotate() формируется набор запросов QuerySet,
     чтобы агрегировать общее число комментариев к каждому посту. Функция агрегирования Count используется для
    сохранения количества комментариев в вычисляемом поле total_comments по каждому объекту Post.
    Набор запросов QuerySet упорядочивается по вычисляемому полю в убывающем порядке.
    Также предоставляется опциональная переменная count, чтобы ограничивать общее число возвращаемых объектов.'''
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]
