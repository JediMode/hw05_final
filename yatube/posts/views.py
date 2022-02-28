from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.conf import settings

from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count = Post.objects.filter(author=author).count()
    following = (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()
    )
    context = {
        'count': count,
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post_detail = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    title = 'Пост' + post_detail.text[:30]
    author = post_detail.author
    comments = post_detail.comments.all()
    context = {
        'post_detail': post_detail,
        'title': title,
        'author': author,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups
    }
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups,
        'is_edit': is_edit
    }
    if request.user == author:
        if request.method == 'POST' and form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    user = request.user
    posts = Post.objects.filter(author__following__user=user)
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    exist = Follow.objects.filter(user=request.user, author=author).exists()
    if author != request.user and not exist:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
