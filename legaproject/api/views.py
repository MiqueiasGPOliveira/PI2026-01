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
                    "usuario": user.usuario,
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


from datetime import date

class MentorInteractView(APIView):
    """
    POST /api/mentor/interagir
    Endpoint protegido responsável por gerar o Roadmap Educacional com Gemini.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = MentorInteractSerializer(data=request.data)
        if serializer.is_valid():
            # Extraindo dados do formulário preenchido pelo usuário
            assunto = serializer.validated_data.get('assunto')
            tempo = serializer.validated_data.get('tempo_pretendido')
            objetivo = serializer.validated_data.get('objetivo')
            nivel = serializer.validated_data.get('nivel')
            horas = serializer.validated_data.get('horas_diarias')
            formato = serializer.validated_data.get('formato')
            
            # Recuperando informações protegidas do usuário autenticado
            user = request.user
            
            # Cálculo seguro da idade
            hoje = date.today()
            idade = "Não informada"
            if user.dt_nasc:
                idade = hoje.year - user.dt_nasc.year - ((hoje.month, hoje.day) < (user.dt_nasc.month, user.dt_nasc.day))
                
            instituicao = user.instituicao if user.instituicao else 'Não informada'
            area_atuacao = user.area_atuacao if user.area_atuacao else 'Não informada'
            
            # Construção do Prompt (A regra de negócio fica inteira no Back-end)
            user_prompt = (
                f"Atue como um mentor educacional avançado. Crie um roadmap detalhado "
                f"(com cronograma, tópicos de estudo, dicas de livros e cursos) em Markdown "
                f"para um aluno com o seguinte perfil:\n"
                f"- Idade: {idade} anos\n"
                f"- Instituição: {instituicao}\n"
                f"- Área de Atuação: {area_atuacao}\n\n"
                f"O objetivo principal dele é: {objetivo}\n"
                f"Assunto que deseja aprender: {assunto}\n"
                f"Nível de conhecimento atual: {nivel}\n"
                f"Prazo esperado: {tempo} estudando {horas} por dia.\n"
                f"Formato preferido de conteúdo: {formato}\n\n"
                f"Por favor, estruture a resposta de forma clara, usando cabeçalhos, listas e negritos do Markdown."
            )
            
            try:
                # Instancia a camada de Service sem misturar a lógica de negócio na View
                mentor_service = SocraticMentorService()
                resposta_ia = mentor_service.interact(user_prompt)
                
                return Response({
                    "response": resposta_ia
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                # Retorna erro amigável caso a IA ou a Service falhem
                return Response({
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({
                    "error": f"Erro interno: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
