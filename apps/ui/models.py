from django.db import models
from base.interface import BaseModel
from apps.general.models import HashTag
from apps.media.models import Media
from apps.media.api.serializers import MediaSerializer
from apps.authentication.models import Profile
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone


# Create your models here.


class UserTemp(BaseModel):
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=150, null=True, blank=True)
    source = models.CharField(max_length=150)
    avatar_url = models.CharField(max_length=260, null=True, blank=True)
    extra = JSONField(null=True, blank=True)
    user = models.ForeignKey(User, related_name="user_temp", on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, **kwargs):
        test = User.objects.filter(username=self.username).first()
        if test is None:
            test = User.objects.create_user(username=self.username, password="DKM@VKL1234$#@!")
            if not hasattr(test, 'profile'):
                profile = Profile.objects.create(user=test, nick=self.display_name)
            else:
                test.profile.nick = self.display_name
                test.profile.save()
                profile = test.profile
            if profile.media is None and self.avatar_url is not None:
                media = Media.objects.save_url(self.avatar_url)
                profile.media = media
                print(MediaSerializer(media).data)
                profile.save()
            test.save()
        self.user = test
        super(UserTemp, self).save(**kwargs)


class UI(BaseModel):
    title = models.CharField(max_length=200)
    short_description = models.TextField(max_length=260, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    medias = models.ManyToManyField(Media, related_name="uis")
    user = models.ForeignKey(User, related_name="uis", on_delete=models.CASCADE)
    user_temp = models.ForeignKey(UserTemp, related_name="uis", on_delete=models.SET_NULL, null=True, blank=True)
    voters = models.ManyToManyField(User, related_name="voted_uis", blank=True)
    options = JSONField(null=True, blank=True)
    score = models.FloatField(default=0)
    date_published = models.DateTimeField(default=timezone.now)


class UITag(BaseModel):
    ui = models.ForeignKey(UI, related_name="ui_tags", on_delete=models.CASCADE)
    hash_tag = models.ForeignKey(HashTag, related_name="ui_tags", on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)


class Comment(BaseModel):
    ui = models.ForeignKey(UI, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    user_temp = models.ForeignKey(UserTemp, related_name="comments", on_delete=models.SET_NULL, null=True, blank=True)
    content = models.CharField(max_length=500)
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, null=True)
