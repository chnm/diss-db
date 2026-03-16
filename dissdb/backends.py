from django.contrib.auth import get_user_model

User = get_user_model()


class MagicLinkBackend:
    """Authentication backend that allows login() to work for magic link users."""

    def authenticate(self, request, user_id=None, **kwargs):
        if user_id is None:
            return None
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
