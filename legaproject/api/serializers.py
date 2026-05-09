from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """ Serializer de Saída: Retorna informações do usuário autenticado """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'data_de_nascimento', 'telefone', 'escola_ou_faculdade', 'area_de_atuacao', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """ Serializer de Entrada: Lida com a criação segura de contas com criptografia e os novos campos """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    data_de_nascimento = serializers.DateField(required=True)
    telefone = serializers.CharField(required=True, max_length=20)
    escola_ou_faculdade = serializers.CharField(required=False, allow_blank=True, max_length=255)
    area_de_atuacao = serializers.CharField(required=False, allow_blank=True, max_length=255)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'data_de_nascimento', 'telefone', 'escola_ou_faculdade', 'area_de_atuacao']

    def create(self, validated_data):
        # Utiliza o gerenciador da model 'create_user' para hash da senha
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            data_de_nascimento=validated_data.get('data_de_nascimento'),
            telefone=validated_data.get('telefone'),
            escola_ou_faculdade=validated_data.get('escola_ou_faculdade', ''),
            area_de_atuacao=validated_data.get('area_de_atuacao', '')
        )
        return user


class MentorInteractSerializer(serializers.Serializer):
    """ Serializer de Entrada: Valida o formato JSON recebido do aluno para interação """
    prompt = serializers.CharField(required=True, min_length=1, help_text="A dúvida ou instrução do aluno.")
