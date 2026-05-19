from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, MentorInteractView, TarefaListView, TarefaStatusUpdateView, RoadmapListView, RoadmapDeleteView, TarefaResponderView, CalendarioAPIView, TarefaRescheduleView, RoadmapOpcoesView, TarefaCreateView

urlpatterns = [
    # Auth
    path('auth/cadastro', RegisterView.as_view(), name='auth_register'),
    path('auth/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('usuarios/perfil', UserProfileView.as_view(), name='user_profile'),
    
    # IA Mentor
    path('mentor/interagir', MentorInteractView.as_view(), name='mentor_interact'),
    
    # Tarefas
    path('tarefas/', TarefaListView.as_view(), name='tarefas-list'),
    path('tarefas/criar/', TarefaCreateView.as_view(), name='tarefas-create'),
    path('tarefas/calendario/', CalendarioAPIView.as_view(), name='tarefas-calendario'),
    path('tarefas/<int:pk>/status/', TarefaStatusUpdateView.as_view(), name='tarefas-update-status'),
    path('tarefas/<int:pk>/agendar/', TarefaRescheduleView.as_view(), name='tarefas-agendar'),
    path('tarefas/<int:pk>/responder/', TarefaResponderView.as_view(), name='tarefas-responder'),

    # Roadmaps (Trilhas)
    path('roadmaps/', RoadmapListView.as_view(), name='roadmaps-list'),
    path('roadmaps/opcoes/', RoadmapOpcoesView.as_view(), name='roadmaps-opcoes'),
    path('roadmaps/<int:pk>/', RoadmapDeleteView.as_view(), name='roadmaps-delete'),
]
