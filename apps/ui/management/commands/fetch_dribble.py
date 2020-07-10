from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from utils.other import save_from_dribble


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(5):
            req = requests.get("https://dribbble.com/shots/popular/product-design?page=" + str(i + 1))
            soup = BeautifulSoup(req.text, "html5lib")
            a_list = soup.select(".shots-grid .dribbble-shot .shot-thumbnail-link")
            for a in a_list:
                url = "https://dribbble.com" + a["href"]
                print(url)
                save_from_dribble(url)
                print("======================DONE=====================")
