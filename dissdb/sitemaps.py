from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Scholar


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            "index",
            "about",
            "contributing",
            "scholars",
            "dissertations",
            "committeemembers",
        ]

    def location(self, item):
        return reverse(item)


class ScholarSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Scholar.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()
