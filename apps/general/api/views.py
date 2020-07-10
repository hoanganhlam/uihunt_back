from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.general import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

client_id = "1c9c426ee079a60ccb9705a970c697bd7b93b6c4b913aee0538e41b94dd00091"
client_secret = "fddd82e02796b3e32cdd6fdc0e5db18c9a2aad787ca7744ecf793b15bc88f651"
redirect_uri = ""
code = ""


class HashTagViewSet(viewsets.ModelViewSet):
    models = models.HashTag
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.HashTagSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        if request.GET.get("for_model"):
            self.queryset = self.queryset.filter(for_models__overlap=[request.GET.get("for_model")])
        return super(HashTagViewSet, self).list(request, *args, **kwargs)


@api_view(['GET'])
def get_config(request):
    return Response(
        {
            "content_type": {
                "user": ContentType.objects.get(model="user").pk,
                "hash_tag": ContentType.objects.get(model="hashtag").pk,
            }
        }
    )
