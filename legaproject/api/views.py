from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, MentorInteractSerializer
from .services import SocraticMentorService

class RegisterView(APIView):
    """
    POST /api/auth/cadastro
    Endpoint público para registrar novos usuários
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Usuário criado com sucesso",
                "user": {
                    "username": user.username,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    GET /api/usuarios/perfil
    Endpoint protegido para buscar perfil do usuário logado
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MentorInteractView(APIView):
    """
    POST /api/mentor/interagir
    Endpoint protegido responsável pela comunicação com o Google Gemini.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = MentorInteractSerializer(data=request.data)
        if serializer.is_valid():
            user_prompt = serializer.validated_data.get('prompt')
            
            # Instancia a camada de Service sem misturar a lógica de negócio na View
            mentor_service = SocraticMentorService()
            resposta_ia = mentor_service.interact(user_prompt)
            
            return Response({
                "response": resposta_ia
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
