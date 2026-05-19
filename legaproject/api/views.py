from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, MentorInteractSerializer, ModuloComTarefasSerializer, RoadmapSerializer
from .services import SocraticMentorService
from .models import Modulo, Tarefa, Roadmap
from django.shortcuts import get_object_or_404
import json

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
                
                # A resposta_ia é uma string JSON graças ao response_schema
                try:
                    dados_json = json.loads(resposta_ia)
                except json.JSONDecodeError:
                    raise ValueError("A IA não retornou um formato JSON válido.")
                
                # 1. Salva o Roadmap
                roadmap = Roadmap.objects.create(
                    user=user,
                    assunto=assunto
                )
                
                # 2. Itera sobre os módulos
                ordem_modulo = 1
                for mod_data in dados_json.get('modulos', []):
                    modulo = Modulo.objects.create(
                        roadmap=roadmap,
                        nome_modulo=mod_data.get('nome_modulo', f'Módulo {ordem_modulo}'),
                        ordem=ordem_modulo
                    )
                    ordem_modulo += 1
                    
                    # 3. Itera sobre as tarefas
                    for t_data in mod_data.get('tarefas', []):
                        Tarefa.objects.create(
                            modulo=modulo,
                            titulo=t_data.get('titulo', 'Tarefa sem título'),
                            conteudo_exercicio=t_data.get('conteudo_exercicio', ''),
                            tempo_estimado=t_data.get('tempo_estimado', 15),
                            pontos_dificuldade=t_data.get('pontos_dificuldade', 1),
                            pergunta=t_data.get('pergunta', ''),
                            opcoes=t_data.get('opcoes', []),
                            resposta_correta=t_data.get('resposta_correta', '')
                        )
                
                return Response({
                    "message": "Trilha gerada e salva com sucesso!",
                    "roadmap_id": roadmap.id
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


class TarefaListView(APIView):
    """
    GET /api/tarefas/
    Retorna as tarefas do usuário logado agrupadas por Módulo.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Busca todos os módulos que pertencem aos roadmaps do usuário
        modulos = Modulo.objects.filter(roadmap__user=request.user).order_by('ordem', 'id')
        serializer = ModuloComTarefasSerializer(modulos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TarefaStatusUpdateView(APIView):
    """
    PATCH /api/tarefas/<id>/status/
    Atualiza o status de conclusão de uma tarefa.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        tarefa = get_object_or_404(Tarefa, pk=pk)
        
        # Garante que a tarefa pertence a um roadmap do usuário logado
        if tarefa.modulo.roadmap.user != request.user:
            return Response({"detail": "Você não tem permissão para alterar esta tarefa."}, status=status.HTTP_403_FORBIDDEN)
        
        # Verifica se o campo concluido foi enviado na requisição
        concluido = request.data.get('concluido')
        if concluido is not None:
            # Garante que seja booleano
            tarefa.concluido = bool(concluido)
            tarefa.save()
            return Response({"detail": "Status atualizado com sucesso.", "concluido": tarefa.concluido}, status=status.HTTP_200_OK)
        
        return Response({"detail": "O campo 'concluido' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)


class TarefaResponderView(APIView):
    """
    POST /api/tarefas/<id>/responder/
    Recebe a resposta do usuário para a pergunta de validação.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tarefa = get_object_or_404(Tarefa, pk=pk)
        
        # Garante que a tarefa pertence a um roadmap do usuário logado
        if tarefa.modulo.roadmap.user != request.user:
            return Response({"detail": "Você não tem permissão para alterar esta tarefa."}, status=status.HTTP_403_FORBIDDEN)
        
        resposta_usuario = request.data.get('resposta')
        if not resposta_usuario:
            return Response({"detail": "Nenhuma resposta fornecida."}, status=status.HTTP_400_BAD_REQUEST)
            
        if resposta_usuario.strip().lower() == (tarefa.resposta_correta or "").strip().lower():
            tarefa.concluido = True
            tarefa.save()
            return Response({
                "sucesso": True, 
                "detail": "Resposta correta! Tarefa concluída.", 
                "concluido": True
            }, status=status.HTTP_200_OK)
            
        return Response({
            "sucesso": False, 
            "detail": "Resposta incorreta. Tente novamente."
        }, status=status.HTTP_200_OK)


class RoadmapListView(APIView):
    """
    GET /api/roadmaps/
    Retorna a lista de roadmaps criados pelo usuário logado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roadmaps = Roadmap.objects.filter(user=request.user).order_by('-criado_em')
        serializer = RoadmapSerializer(roadmaps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
