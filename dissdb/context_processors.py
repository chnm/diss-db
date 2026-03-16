from django.conf import settings


def magic_link_settings(request):
    return {
        "MAGIC_LINK_EXPIRY_MINUTES": settings.MAGIC_LINK_EXPIRY_MINUTES,
    }
