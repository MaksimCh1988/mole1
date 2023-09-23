from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def post_list(request, tag_slug=None):
    post_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = Post.objects.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)  # Список активных комментариев к этому посту
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)  # получаем все тэги, в виде списка значений , а не кортежей
    # print(post.tags.similar_objects()) встроенный в приложение способо найти объекты со схожими тэгами
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)  # все посты с тегами,убрать наш
    # сгруппировать по тегам ,генерирует вычисляемое поле same_tag, упорядочить , взять первые 5
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})


class PostListView(ListView):
    '''Представлени на основе класса'''
    queryset = Post.published.all()  # либо достаточно указать model=Post
    context_object_name = 'posts'  # либо будет контекстная переменная по умолчанию object_list
    paginate_by = 3  # задаем постраничную разбивку
    template_name = 'blog/post/list.html'  # либо используется по умолчанию blog/post_list.html.


def post_share(request, post_id):
    post = get_object_or_404(Post,  # извлесь пост по id
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())  # полный адрес,включая HTTP-схему и hostname
            subject = f"{cd['name']} рекомендовал вам почитать {post.title}"
            message = f"Почитай {post.title} по ссылке {post_url}\n\n{cd['name']} оставил комментарий {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,  # извлесь пост по id
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)  # Комментарий был отправлен
    if form.is_valid():
        comment = form.save(commit=False)  # Создать объект класса Comment, не сохраняя его в базе данных
        comment.post = post  # Назначить пост комментарию
        comment.save  # Сохранить комментарий в базе данных
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post,
                                                      'form': form,
                                                      'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body', config='russian')
            search_query = SearchQuery(query, config='russian')
            results = Post.published.annotate(search=search_vector,
                                              rank = SearchRank(search_vector,search_query)).filter(search=search_query).order_by('-rank')

    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})
