import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all()

    # Return posts in reverse chronologial order
    posts = posts.order_by("-timestamp").all()

    paginator = Paginator(posts, 10) # Show 10 posts per page.
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": page_posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        if username == "following" or "all":
            return render(request, "network/register.html", {
                "message": "Username can't be 'following' or 'all'."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        post = Post(content = content, author = request.user)
        post.save()

        return HttpResponseRedirect(reverse("index"))

    return HttpResponseRedirect(reverse("index"))


# API Single Post
def get_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
            return JsonResponse({"error": "Invalid path."}, status=400)

    return JsonResponse(post.serialize(), safe=False)


# API Save edited Post
@login_required
def save_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
            return JsonResponse({"error": "Invalid path."}, status=400)

    if request.method == "PUT":
        if request.user == post.author:
            data = json.loads(request.body)
            content = data.get("content", "")
            post.content = content
            #post.content = data["content"]
            post.save()

            return JsonResponse({"content": post.content}, status=200)
        else:
            return JsonResponse({"error": "You cannot edit another user’s posts."}, status=403)

    # It must be via PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)


# Like or Dislike post API
@login_required
def like_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
            return JsonResponse({"error": "Invalid path."}, status=400)

    if request.method == "PUT":

        user = request.user

        if (user.likes.filter(pk=post_id).exists()):
            post.liked_by.remove(user)
            heart_icon = "bi bi-heart"
        else:
            post.liked_by.add(user)
            heart_icon = "bi bi-heart-fill"

        return JsonResponse({"heart_icon": heart_icon, "likes": post.likes()}, status=200)

    # It must be via PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)


def profile_page(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "network/index.html")

    following = Follow.objects.filter(follower=user.id)
    followers = Follow.objects.filter(followed=user.id)
    btn_following = "Follow"

    for f in followers:
        if request.user == f.follower:
            btn_following = "Unfollow"
            break

    # Get user profile posts
    user = User.objects.get(username=username)
    posts = Post.objects.filter(author=user.id)

    # Return posts in reverse chronologial order
    posts = posts.order_by("-timestamp").all()

    paginator = Paginator(posts, 10) # Show 10 posts per page.
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "username": username,
        "followers": len(followers),
        "following": len(following),
        "btn_following": btn_following,
        "posts": page_posts
    })


@login_required(login_url='/login')
def following(request):
    #posts = Post.objects.all()
    follow = Follow.objects.filter(follower=request.user)
    list_followed = []
    for f in follow:
        list_followed.append(f.followed)
    posts = Post.objects.filter(author__in=list_followed)

    # Return posts in reverse chronologial order
    posts = posts.order_by("-timestamp").all()

    paginator = Paginator(posts, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": page_posts
    })


@login_required
def follow_unfollow(request):
    if request.method == "POST":
        flw_unflw = request.POST["flw_unflw"]
        username = request.POST["username"]
        user = User.objects.get(username=username)

        if flw_unflw == "Follow":
            followers = Follow(follower=request.user, followed=user)
            followers.save()
        elif flw_unflw == "Unfollow":
            followers = Follow.objects.get(follower=request.user, followed=user)
            followers.delete()

        return HttpResponseRedirect(reverse("username", args=(username,)))