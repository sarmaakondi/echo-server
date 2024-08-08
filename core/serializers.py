from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        profile_picture_url = (
            user.profile.profile_picture.url
            if hasattr(user, "profile") and user.profile.profile_picture
            else None
        )

        if profile_picture_url:
            # Build absolute URL for the profile picture
            profile_picture_url = settings.DOMAIN_URL + profile_picture_url

        token["user_profile_picture"] = profile_picture_url

        return token
