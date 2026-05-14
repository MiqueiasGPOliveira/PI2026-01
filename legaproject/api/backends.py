from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Autentica usando usuario ou email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # O SimpleJWT vai passar a credencial principal no kwarg correspondente ao USERNAME_FIELD
        # (que no nosso caso é 'usuario'). Então a string digitada vai estar em kwargs.get('usuario')
        # ou no parâmetro username.
        login_id = kwargs.get(User.USERNAME_FIELD) or username
        
        if not login_id:
            return None

        try:
            # Tenta encontrar o usuário pelo usuario ou pelo email
            user = User.objects.get(Q(usuario=login_id) | Q(email=login_id))
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
