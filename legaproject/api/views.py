from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, MentorInteractSerializer, ModuloComTarefasSerializer, RoadmapSerializer, RoadmapComModulosSerializer, TarefaCreateSerializer
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


from datetime import date, timedelta
from django.utils import timezone

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
            periodo = serializer.validated_data.get('periodo_estudo')
            
            # Mapeamento do tempo em string para inteiro (minutos)
            horas_to_minutos = {
                "10 minutos": 10,
                "30 minutos": 30,
                "1 hora": 60,
                "1 hora e 30 minutos": 90,
                "2 horas": 120,
                "2 horas e 30 minutos": 150,
                "3 horas": 180
            }
            minutos_por_dia = horas_to_minutos.get(horas, 60)

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
                f"Prazo esperado: {tempo} estudando {horas} por dia, no período da {periodo}.\n"
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
                
                current_date = timezone.now().date()
                minutos_hoje = 0

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
                        try:
                            tempo_estimado = int(t_data.get('tempo_estimado', 15))
                        except (ValueError, TypeError):
                            tempo_estimado = 15
                        
                        # Verifica se o tempo desta tarefa estoura o limite de hoje
                        if minutos_hoje + tempo_estimado > minutos_por_dia and minutos_hoje > 0:
                            current_date += timedelta(days=1)
                            minutos_hoje = 0
                            
                        minutos_hoje += tempo_estimado

                        Tarefa.objects.create(
                            modulo=modulo,
                            titulo=t_data.get('titulo', 'Tarefa sem título'),
                            conteudo_exercicio=t_data.get('conteudo_exercicio', ''),
                            tempo_estimado=tempo_estimado,
                            pontos_dificuldade=t_data.get('pontos_dificuldade', 1),
                            pergunta=t_data.get('pergunta', ''),
                            opcoes=t_data.get('opcoes', []),
                            resposta_correta=t_data.get('resposta_correta', ''),
                            data_agendada=current_date
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
        roadmap_id = request.query_params.get('roadmap_id')
        if roadmap_id:
            modulos = Modulo.objects.filter(roadmap__user=request.user, roadmap_id=roadmap_id).order_by('ordem', 'id')
        else:
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
        
        # Verifica se o campo status ou concluido foi enviado na requisição
        novo_status = request.data.get('status')
        concluido = request.data.get('concluido')
        
        updated = False
        if novo_status in dict(Tarefa.STATUS_CHOICES).keys():
            tarefa.status = novo_status
            if novo_status == 'concluido':
                tarefa.concluido = True
            else:
                tarefa.concluido = False
            updated = True
            
        elif concluido is not None:
            tarefa.concluido = bool(concluido)
            tarefa.status = 'concluido' if tarefa.concluido else 'pendente'
            updated = True
            
        if updated:
            tarefa.save()
            return Response({
                "detail": "Status atualizado com sucesso.", 
                "concluido": tarefa.concluido,
                "status": tarefa.status
            }, status=status.HTTP_200_OK)
        
        return Response({"detail": "Status inválido ou não fornecido."}, status=status.HTTP_400_BAD_REQUEST)


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
            tarefa.status = 'concluido'
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

class RoadmapDeleteView(APIView):
    """
    DELETE /api/roadmaps/<id>/
    Exclui uma trilha de estudos.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        roadmap = get_object_or_404(Roadmap, pk=pk)
        
        # Garante que a trilha pertence ao usuário logado
        if roadmap.user != request.user:
            return Response({"detail": "Você não tem permissão para excluir esta trilha."}, status=status.HTTP_403_FORBIDDEN)
            
        roadmap.delete()
        return Response({"detail": "Trilha excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)

class CalendarioAPIView(APIView):
    """
    GET /api/calendario/
    Retorna as tarefas formatadas para o FullCalendar.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tarefas = Tarefa.objects.filter(modulo__roadmap__user=request.user, data_agendada__isnull=False)
        eventos = []
        for t in tarefas:
            color = '#38bdf8' 
            if t.concluido:
                color = '#4ade80'
            
            eventos.append({
                'id': t.id,
                'title': t.titulo,
                'start': t.data_agendada.strftime('%Y-%m-%d'),
                'color': color,
                'extendedProps': {
                    'status': t.status,
                    'modulo': t.modulo.nome_modulo,
                    'roadmap_id': t.modulo.roadmap.id
                }
            })
        return Response(eventos, status=status.HTTP_200_OK)

class TarefaRescheduleView(APIView):
    """
    PATCH /api/tarefas/<int:pk>/agendar/
    Atualiza a data_agendada da tarefa.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            tarefa = Tarefa.objects.get(pk=pk, modulo__roadmap__user=request.user)
        except Tarefa.DoesNotExist:
            return Response({"detail": "Tarefa não encontrada ou não pertence a você."}, status=status.HTTP_404_NOT_FOUND)

        nova_data_str = request.data.get('data_agendada')
        if not nova_data_str:
            return Response({"detail": "Data agendada não fornecida."}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import datetime
        try:
            # Fullcalendar often sends YYYY-MM-DD
            # We can parse the first 10 characters just to be safe if ISO 8601 is sent
            nova_data_str = nova_data_str[:10]
            nova_data = datetime.strptime(nova_data_str, '%Y-%m-%d').date()
            tarefa.data_agendada = nova_data
            tarefa.save()
            return Response({"detail": "Data da tarefa atualizada com sucesso.", "data_agendada": nova_data_str}, status=status.HTTP_200_OK)
        except ValueError:
             return Response({"detail": "Formato de data inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

class RoadmapOpcoesView(APIView):
    """
    GET /api/roadmaps/opcoes/
    Retorna os roadmaps e seus módulos para preencher selects.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roadmaps = Roadmap.objects.filter(user=request.user).order_by('-criado_em')
        serializer = RoadmapComModulosSerializer(roadmaps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TarefaCreateView(APIView):
    """
    POST /api/tarefas/criar/
    Cria uma nova tarefa associada a um módulo.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TarefaCreateSerializer(data=request.data)
        if serializer.is_valid():
            modulo = serializer.validated_data['modulo']
            if modulo.roadmap.user != request.user:
                return Response({"detail": "Você não tem permissão para adicionar tarefas a esta trilha."}, status=status.HTTP_403_FORBIDDEN)
            
            tarefa = serializer.save(
                conteudo_exercicio=request.data.get('conteudo_exercicio', 'Tarefa criada manualmente pelo usuário.'),
                pergunta=request.data.get('pergunta', '')
            )
            return Response({"detail": "Tarefa criada com sucesso.", "id": tarefa.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
