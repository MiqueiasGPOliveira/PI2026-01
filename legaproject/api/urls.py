from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, MentorInteractView

urlpatterns = [
    # Auth
    path('auth/cadastro', RegisterView.as_view(), name='auth_register'),
    path('auth/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('usuarios/perfil', UserProfileView.as_view(), name='user_profile'),
    
    # IA Mentor
    path('mentor/interagir', MentorInteractView.as_view(), name='mentor_interact'),
]
