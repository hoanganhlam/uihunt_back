import requests
from bs4 import BeautifulSoup
from apps.ui.models import UI, UserTemp, UITag
from apps.media.models import Media
from apps.general.models import HashTag
from django.template.defaultfilters import slugify
from apps.media.api.serializers import MediaSerializer


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_inner(array, array2):
    for i in array:
        if i in array2:
            return True
    return False


def get_paginator(request):
    search = request.GET.get('search')
    page_size = 10 if request.GET.get('page_size') is None else int(request.GET.get('page_size'))
    page = 1 if request.GET.get('page') is None else int(request.GET.get('page'))
    offs3t = page_size * page - page_size
    return {
        "search": search,
        "page_size": page_size,
        "page": page,
        "offs3t": offs3t
    }


def get_web_meta(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")
    title = ""
    if soup.title:
        title = soup.title.string
    description = soup.find("meta", property="og:description")
    if description is None:
        description = soup.find("meta", property="description")
    if description:
        description = description.get('content')
    else:
        description = ''
    images = []
    for img in soup.findAll('img'):
        images.append(img.get('src'))
    data = {
        "title": title,
        "description": description,
        "images": images
    }
    return data


def get_dribble(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html5lib")
    user = soup.select(".shot-header .slat-details .hoverable.url")[0]
    soup_images = soup.select(".shot-media-section .media-image img")
    soup_comments = soup.select(".comments .response.comment")
    soup_colors = soup.select(".shot-colors .color-chips.group .color a")
    soup_tags = soup.select(".shot-tags .tag a")
    images = list(map(lambda x: {
        "title": x["alt"],
        "src": x["data-src"]
    }, soup_images))
    comments = list(map(lambda x: {
        "user": {
            "full_name": x.select(".hoverable.url .display-name")[0].string,
            "username": x["href"],
            "avatar_url": x.select(".hoverable.url .photo")["src"]
        }
    }, soup_comments))
    colors = list(map(lambda x: x.string, soup_colors))
    tags = list(map(lambda x: x.string, soup_tags))
    data = {
        "title": soup.select('.shot-title')[0].string,
        "description": str(soup.select(".shot-desc")[0]) if len(soup.select(".shot-desc")) > 0 else None,
        "short_description": soup.select(".shot-desc p")[0].string if len(soup.select(".shot-desc p")) > 0 else None,
        "user": {
            "full_name": user['title'],
            "username": user['href'].replace('/', ''),
            "avatar_url": user.select("picture .photo")[0]["src"].replace('/small/', '/normal/')
        },
        "images": images,
        "comments": comments,
        "options": {
            "colors": colors,
            "source_url": url,
            "source_domain": "dribbble"
        },
        "tags": tags
    }
    return data


def save_from_dribble(url):
    ui = UI.objects.filter(options__source_url=url).first()
    if ui is None:
        temp = get_dribble(url)
        if temp.get("images").__len__() > 0:
            user_temp = UserTemp.objects.filter(username=temp.get("user").get("username")).first()
            if user_temp is None:
                user_temp = UserTemp(
                    username=temp.get("user").get("username"),
                    display_name=temp.get("user").get("username"),
                    avatar_url=temp.get("user").get("avatar_url"),
                )
                user_temp.save()
            ui = UI(
                title=temp.get("title"),
                description=temp.get("description"),
                short_description=temp.get("short_description"),
                options=temp.get("options"),
                user_temp=user_temp,
                user=user_temp.user
            )
            ui.save()
            for image in temp.get("images"):
                media = Media.objects.save_url(image.get("src"))
                if media is not None:
                    ui.medias.add(media)
                    print(MediaSerializer(media).data)
            for tag in temp.get("tags"):
                hash_tag = HashTag.objects.filter(slug=slugify(tag)).first()
                if hash_tag is None:
                    hash_tag = HashTag(title=tag.capitalize())
                    hash_tag.save()
                UITag.objects.create(hash_tag=hash_tag, ui=ui)
            ui.save()
    return ui
