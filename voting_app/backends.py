import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

logger = logging.getLogger(__name__)

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate using either
    their email address or their username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        
        if not username:
            return None

        user = None
        # Detect automatically whether the entered value is an email or username
        if '@' in username:
            # Detected as email
            try:
                user = UserModel.objects.get(email__iexact=username)
            except UserModel.DoesNotExist:
                pass
        else:
            # Detected as username
            try:
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                pass

        # Fallback to query both fields if no user was found by specific detection
        if user is None:
            try:
                user = UserModel.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
            except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
                pass

        if user is not None:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        else:
            # Run the password hasher to protect against timing attacks
            UserModel().set_password(password)
            
        return None
