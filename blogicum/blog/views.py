from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Post, Category
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.core.mail import send_mail
from django.db.models import Count
from .forms import ProfileEditForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import Comment
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


def paginate_queryset(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = (Post.objects.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True
    ).annotate(comment_count=Count('comments')).order_by('-pub_date'))
    page_obj = paginate_queryset(post_list, request)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        if (not post.is_published
                or not post.category.is_published
                or post.pub_date > now()):
            raise Http404

    comments = post.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = CommentForm()
    return render(request,
                  'blog/detail.html',
                  {'post': post, 'comments': comments, 'form': form})


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug, is_published=True)
    post_list = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=now()
    ).order_by('-pub_date')  # Явная сортировка
    page_obj = paginate_queryset(post_list, request)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = (Post.objects.filter
             (author=user).annotate
             (comment_count=Count('comments')).order_by('-pub_date'))
    page_obj = paginate_queryset(posts, request)
    context = {
        'profile_user': user,
        'page_obj': page_obj,
    }
    if request.user == user:
        context['is_owner'] = True
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request,
                  'blog/create.html',
                  {'form': form, 'is_edit': True, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request,
                  'blog/create.html', {'post': post, 'is_delete': True})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    return render(request,
                  'blog/comment.html', {'comment': comment, 'is_delete': True})


def test_email():
    send_mail(
        'Тестовое письмо',
        'Это содержимое тестового письма.',
        'admin@blogicum.com',
        ['user@example.com'],
        fail_silently=False,
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', id=post_id)
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment,
                                id=comment_id, post_id=post_id,
                                author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request,
                  'blog/comment.html', {'form': form, 'comment': comment})


@login_required
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=username)
    else:
        form = ProfileEditForm(instance=user)
    return render(request,
                  'blog/user.html', {'form': form, 'profile_user': user})


@login_required
def change_password(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Обновление сессии
            return redirect('blog:password_change_done', username=username)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request,
                  'registration/password_change_form.html', {'form': form})


@login_required
def password_change_done(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)
    return render(request, 'registration/password_change_done.html')
