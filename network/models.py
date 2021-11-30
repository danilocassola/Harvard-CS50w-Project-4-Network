from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_author")
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(User, blank=True, related_name="likes")

    def __str__(self):
        return f"author: {self.author}, content: {self.content}, timestamp: {self.timestamp}"

    def likes(self):
        return self.liked_by.all().count()

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": [user.username for user in self.liked_by.all()]
        }


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")

    def __str__(self):
        return f"follower: {self.follower}, followed: {self.followed}"

    def serialize(self):
        return {
            "follower": self.follower.username,
            "followed": self.followed.username
        }