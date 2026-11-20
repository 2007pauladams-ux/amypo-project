from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from .models import UserProfile
from news.models import NewsCategory, NewsArticle, SavedArticle

@csrf_protect
def login_view(request):
    """
    Handles analyst terminal authentication.
    """
    if request.user.is_authenticated:
        return redirect('news:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}. Intelligence terminal activated.")
            next_url = request.GET.get('next') or request.POST.get('next') or 'news:dashboard'
            return redirect(next_url)
        else:
            error = "Invalid analyst credentials. Please verify your username and password."

    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    return render(request, 'auth/login.html', {'error': error, 'breaking_news': breaking_news})


@csrf_protect
def register_view(request):
    """
    Registers a new analyst profile.
    """
    if request.user.is_authenticated:
        return redirect('news:dashboard')

    error = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            error = "All required fields must be provided."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."
        elif User.objects.filter(username=username).exists():
            error = "Username already allocated in the intelligence registry."
        elif User.objects.filter(email=email).exists():
            error = "Email address is already associated with an active terminal account."
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, f"Analyst profile successfully established for {username}.")
            return redirect('news:dashboard')

    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    return render(request, 'auth/register.html', {'error': error, 'breaking_news': breaking_news})


def logout_view(request):
    """
    Terminates the analyst session.
    """
    logout(request)
    messages.info(request, "Analyst session closed. Disconnected from command terminal.")
    return redirect('news:index')


@csrf_protect
def forgot_password_view(request):
    """
    Interface for dispatching password recovery instructions.
    """
    success = False
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        success = True

    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    return render(request, 'auth/forgot_password.html', {'success': success, 'breaking_news': breaking_news})


def profile_view(request):
    """
    Analyst profile view: update bio, name, email, preferred news categories.
    """
    user = request.user
    if not user.is_authenticated:
        demo_user = User.objects.filter(username='demo_analyst').first()
        user = demo_user if demo_user else User.objects.first()

    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST' and request.user.is_authenticated:
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.save()

        profile.bio = request.POST.get('bio', profile.bio).strip()
        cat_ids = request.POST.getlist('categories')
        if cat_ids:
            profile.preferred_categories.set(NewsCategory.objects.filter(id__in=cat_ids))
        profile.save()

        messages.success(request, "Analyst profile and domain preferences updated successfully.")
        return redirect('accounts:profile')

    all_categories = NewsCategory.objects.all().order_by('order')
    
    # Saved articles for this user
    saved_instances = SavedArticle.objects.filter(user=user).select_related('article', 'article__category').order_by('-created_at')
    saved_articles = [s.article for s in saved_instances]
    if not saved_articles:
        saved_articles = list(NewsArticle.objects.all()[:4])

    reading_history = list(NewsArticle.objects.all()[:5])
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]

    context = {
        'user': user,
        'profile': profile,
        'all_categories': all_categories,
        'saved_articles': saved_articles,
        'reading_history': reading_history,
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/profile.html', context)
