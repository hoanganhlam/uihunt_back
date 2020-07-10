from rest_framework.response import Response
from rest_framework.decorators import api_view
from utils.other import get_paginator, save_from_dribble
from django.db import connection
from apps.ui.api.serializers import UISerializer
from apps.ui.models import UI


@api_view(['GET'])
def list_ui(request):
    p = get_paginator(request)
    with connection.cursor() as cursor:
        cursor.execute("SELECT FETCH_LIST_UI(%s, %s, %s, %s, %s, %s, %s)",
                       [
                           p.get("page_size"),
                           p.get("offs3t"),
                           p.get("search"),
                           request.user.id if request.user.is_authenticated else None,
                           '{' + request.GET.get('hash_tags') + '}' if request.GET.get('hash_tags') else None,
                           request.GET.get("user", None),
                           request.GET.get("order_by", None),
                       ])
        result = cursor.fetchone()[0]
        if result.get("results") is None:
            result["results"] = []
        cursor.close()
        connection.close()
        return Response(result)


@api_view(['GET'])
def detail_ui(request, pk):
    ui = UI.objects.get(pk=pk)
    if ui.options is None or ui.options.get("view_count", None) is None:
        if ui.options is None:
            ui.options = {"view_count": 1}
        elif ui.options.get("view_count", None) is None:
            ui.options["view_count"] = 1
    else:
        ui.options["view_count"] = ui.options["view_count"] + 1
    ui.save()
    with connection.cursor() as cursor:
        cursor.execute("SELECT FETCH_DETAIL_UI(%s, %s)", [
            pk,
            request.user.id if request.user.is_authenticated else None
        ])
        out = cursor.fetchone()[0]
    return Response(out)


@api_view(['GET'])
def fetch_url(request):
    url = request.GET.get("url")
    return Response(UISerializer(save_from_dribble(url)).data)
