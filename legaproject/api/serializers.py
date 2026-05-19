from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Roadmap, Modulo, Tarefa
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """ Serializer de Saída: Retorna informações do usuário autenticado """
    class Meta:
        model = User
        fields = ['id', 'usuario', 'nome_completo', 'email', 'telefone', 'dt_nasc', 'instituicao', 'area_atuacao', 'dt_cadastro']


class RegisterSerializer(serializers.ModelSerializer):
    """ Serializer de Entrada: Lida com a criação segura de contas com os novos campos e validações """
    
    # Recebemos 'senha' no payload, mas o model do Django espera 'password' no set_password.
    # Usamos o 'source' para dizer ao DRF que o campo 'senha' no JSON alimenta o atributo 'password' da classe
    senha = serializers.CharField(source='password', write_only=True, required=True, style={'input_type': 'password'})
    
    usuario = serializers.CharField(required=True, max_length=150)
    nome_completo = serializers.CharField(required=True, max_length=255)
    email = serializers.EmailField(required=True)
    dt_nasc = serializers.DateField(required=True)
    telefone = serializers.CharField(required=True, max_length=20)
    instituicao = serializers.CharField(required=False, allow_blank=True, max_length=255)
    area_atuacao = serializers.CharField(required=False, allow_blank=True, max_length=255)

    class Meta:
        model = User
        # Listamos 'senha' em vez de 'password' para que a API espere e valide a chave 'senha' no JSON
        fields = ['usuario', 'nome_completo', 'email', 'senha', 'dt_nasc', 'telefone', 'instituicao', 'area_atuacao']
        # O DRF valida a unicidade automaticamente com base no model (unique=True em usuario, email e telefone)

    def create(self, validated_data):
        # Utiliza o gerenciador customizado 'create_user' para hash da senha
        user = User.objects.create_user(
            usuario=validated_data['usuario'],
            email=validated_data['email'],
            password=validated_data['password'],  # O source='password' fez o DRF mapear 'senha' para 'password'
            nome_completo=validated_data['nome_completo'],
            dt_nasc=validated_data.get('dt_nasc'),
            telefone=validated_data.get('telefone'),
            instituicao=validated_data.get('instituicao', ''),
            area_atuacao=validated_data.get('area_atuacao', '')
        )
        return user


class MentorInteractSerializer(serializers.Serializer):
    """ Serializer de Entrada: Valida o formato JSON recebido do formulário de Roadmap """
    assunto = serializers.CharField(required=True)
    tempo_pretendido = serializers.CharField(required=True)
    objetivo = serializers.CharField(required=True)
    nivel = serializers.CharField(required=True)
    horas_diarias = serializers.CharField(required=True)
    formato = serializers.CharField(required=True)
    periodo_estudo = serializers.CharField(required=True)


class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'conteudo_exercicio', 'status', 'concluido', 'tempo_estimado', 'pontos_dificuldade', 'pergunta', 'opcoes']

class ModuloComTarefasSerializer(serializers.ModelSerializer):
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Modulo
        fields = ['id', 'nome_modulo', 'ordem', 'tarefas']

class RoadmapSerializer(serializers.ModelSerializer):
    modulos_count = serializers.SerializerMethodField()

    class Meta:
        model = Roadmap
        fields = ['id', 'assunto', 'criado_em', 'modulos_count']
        
    def get_modulos_count(self, obj):
        return obj.modulos.count()

class ModuloSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = ['id', 'nome_modulo']

class RoadmapComModulosSerializer(serializers.ModelSerializer):
    modulos = ModuloSimplesSerializer(many=True, read_only=True)
    
    class Meta:
        model = Roadmap
        fields = ['id', 'assunto', 'modulos']

class TarefaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = ['modulo', 'titulo', 'data_agendada', 'tempo_estimado', 'pontos_dificuldade', 'conteudo_exercicio', 'pergunta']
        extra_kwargs = {
            'conteudo_exercicio': {'required': False, 'allow_blank': True},
            'pergunta': {'required': False, 'allow_blank': True}
        }
