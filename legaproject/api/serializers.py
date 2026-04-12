from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """ Serializer de Saída: Retorna informações do usuário autenticado """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """ Serializer de Entrada: Lida com a criação segura de contas com criptografia """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Utiliza o gerenciador da model 'create_user' para hash da senha
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class MentorInteractSerializer(serializers.Serializer):
    """ Serializer de Entrada: Valida o formato JSON recebido do aluno para interação """
    prompt = serializers.CharField(required=True, min_length=1, help_text="A dúvida ou instrução do aluno.")
