from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    """Passes the last ten Post model objects and title."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGINATOR_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Passes the last ten Post model objects
    filtered by group field and title."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.community.all()
    paginator = Paginator(post_list, settings.PAGINATOR_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': group.title
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """All posts author."""
    author = get_object_or_404(User, username=username)
    post_list = author.author_posts.all()
    paginator = Paginator(post_list, settings.PAGINATOR_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Профайл пользователя {author}'
    following = author.following.count()
    context = {
        'post_list': post_list,
        'page_obj': page_obj,
        'author': author,
        'title': title,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Post details."""
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author=post.author)
    post_comments = post.comments.all()
    title = f'Пост {post.text[:30]}'
    form = CommentForm()
    context = {
        'post': post,
        'title': title,
        'post_count': post_count,
        'form': form,
        'comments': post_comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Create post."""
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author_id = request.user.id
            post.save()
            return redirect(f'/profile/{request.user.username}/')
        return render(request, 'posts/create_post.html', {'form': form})
    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    """Post edit."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author.id != request.user.id:
        return redirect(f'/posts/{post.pk}/')
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post.pk}/')
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'posts/create_post.html', context)


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
    """All author subscriptions."""
    user = request.user
    author_follow = user.follower.values_list('author', flat=True)
    post_list = Post.objects.filter(author__in=author_follow)
    paginator = Paginator(post_list, settings.PAGINATOR_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Add subscription."""
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.create(
        user=user,
        author=author
    ).save()
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Delete subscription."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
