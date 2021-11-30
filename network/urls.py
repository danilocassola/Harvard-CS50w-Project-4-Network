
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"),
    path("user/<str:username>", views.profile_page, name="username"),
    path("following", views.following, name="following"),
    path("follow_unfollow", views.follow_unfollow, name="follow_unfollow"),

    # API Routes

    path("posts_api/id/<int:post_id>", views.get_post, name="get_post"),
    path("posts_api/save/<int:post_id>", views.save_post, name="save_post"),
    path("posts_api/like/<int:post_id>", views.like_post, name="like_post")

]
