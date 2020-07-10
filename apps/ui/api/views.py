from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.ui import models
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response


class UIViewSet(viewsets.ModelViewSet):
    models = models.UI
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.UISerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        return super(UIViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, options={})
        if request.data.get("hash_tags", None) is not None:
            for hash_tag in request.data.get("hash_tags"):
                models.UITag.objects.create(hash_tag_id=hash_tag, ui_id=serializer.data.get("id"))
        if request.data.get("source_url", None) is not None:
            ui = models.UI.objects.get(pk=serializer.data.get("id"))
            ui.options['source_url'] = request.data.get("source_url")
            ui.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if request.data.get("hash_tags"):
            models.UITag.objects.filter(ui=instance).delete()
            for hash_tag in request.data.get("hash_tags"):
                models.UITag.objects.create(hash_tag_id=hash_tag, ui=instance)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    models = models.Comment
    queryset = models.objects.order_by('-id').prefetch_related("user", "user__profile", "user__profile__media")
    serializer_class = serializers.CommentSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        ui_id = int(request.GET.get("ui")) if request.GET.get("ui") else None
        parent_id = int(request.GET.get("parent")) if request.GET.get("parent") else None
        self.queryset = self.queryset.filter(ui_id=ui_id, parent_id=parent_id)
        return super(CommentViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
def vote(request, pk):
    ui = models.UI.objects.get(pk=int(pk))
    x = False
    if request.user.is_authenticated:
        if request.user in ui.voters.all():
            ui.voters.remove(request.user)
            x = False
        else:
            ui.voters.add(request.user)
            x = True
    return Response(x, status=200)
