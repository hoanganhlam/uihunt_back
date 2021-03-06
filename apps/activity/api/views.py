from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter
from base import pagination
from . import serializers
from apps.activity import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from apps.activity import verbs
from utils.other import get_paginator
from django.contrib.contenttypes.models import ContentType


class ActionViewSet(viewsets.ModelViewSet):
    models = models.Action
    queryset = models.objects.order_by('-id').prefetch_related('user_mention').prefetch_related('actor') \
        .prefetch_related('action_object') \
        .prefetch_related('target')
    serializer_class = serializers.ActivitySerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        p = get_paginator(request)
        target_id = self.request.GET.get('target')
        target_content_id = self.request.GET.get('target_content')
        hash_tag = self.request.GET.get('hash_tag')

        user_id = self.request.user.id if self.request.user.is_authenticated else None
        with connection.cursor() as cursor:
            out = {}
            cursor.execute("SELECT COUNT_ACTIVITIES(%s, %s, %s)", [p.get("search"), target_content_id, target_id])
            out["count"] = cursor.fetchone()[0]
            cursor.execute("SELECT FETCH_ACTIVITIES(%s, %s, %s, %s, %s, %s)",
                           [p.get("page_size"), p.get("offs3t"), p.get("search"), target_content_id, target_id,
                            user_id])
            out["results"] = cursor.fetchone()[0]
            return Response(out)

    def retrieve(self, request, *args, **kwargs):
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        with connection.cursor() as cursor:
            cursor.execute("SELECT FETCH_ACTION(%s, %s)", [kwargs.get("pk"), user_id])
            out = cursor.fetchone()[0]
        return Response(out)

    def perform_create(self, serializer):
        serializer.save(
            actor_object_id=self.request.user.id,
            actor_content_type=ContentType.objects.get(model="user"),
            verb=verbs.CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    models = models.Comment
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.CommentSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        activity = int(request.GET.get("activity"))
        self.queryset = self.queryset.filter(activity__id=activity)
        return super(CommentViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


@api_view(['GET'])
def list_following(request):
    if request.user.is_authenticated:
        p = get_paginator(request)
        with connection.cursor() as cursor:
            cursor.execute("SELECT FETCH_LIST_FOLLOWING(%s, %s, %s, %s)",
                           [
                               p.get("page_size"),
                               p.get("offs3t"),
                               request.user.id,
                               request.GET.get("content_type")
                           ])
            return Response(cursor.fetchone()[0])
    return Response({})


@api_view(['POST'])
def vote_post(request, pk):
    user = request.user
    if not request.user.is_authenticated:
        result = False
    else:
        post = models.Action.objects.get(pk=pk)
        if user in post.voters.all():
            post.voters.remove(user)
            result = False
        else:
            post.voters.add(user)
            result = True
    return Response({
        "result": result
    })


@api_view(['POST'])
def vote_comment(request, pk):
    user = request.user
    if not user.is_authenticated:
        result = False
    else:
        instance = models.Comment.objects.get(pk=pk)
        if user in instance.voters.all():
            instance.voters.remove(user)
            result = False
        else:
            instance.voters.add(user)
            result = True
    return Response({
        "result": result
    })


@api_view(['POST'])
def follow(request):
    content_type_id = request.data.get("content_type_id")
    object_id = request.data.get("object_id")
    user = request.user
    if not request.user.is_authenticated:
        return Response(False)
    else:
        instance = models.Follow.objects.filter(user=user, content_type_id=content_type_id, object_id=object_id).first()
        if instance is None:
            instance = models.Follow(user=user, content_type_id=content_type_id, object_id=object_id)
            instance.save()
            return Response(True)
        else:
            instance.delete()
            return Response(False)


@api_view(['GET'])
def is_following(request):
    if request.user.is_authenticated:
        content_type_id = request.GET.get("contentType")
        object_id = request.GET.get("objectId")
        instance = models.Follow.objects.filter(
            user=request.user,
            content_type_id=content_type_id,
            object_id=object_id
        ).first()
        if instance:
            return Response(True)
    return Response(False)


@api_view(['GET'])
def get_vote_object(request):
    pk = request.GET.get("pk")
    try:
        activity = models.Action.objects.get(pk=pk)
        total_votes = activity.voters.count()
        status = False
        if request.user.is_authenticated:
            if request.user in activity.voters.all():
                status = True
        return Response({
            "total": total_votes,
            "is_voted": status
        })
    except:
        return Response({
            "total": 0,
            "is_voted": False
        })
