from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class UserManager(BaseUserManager):
    """
    Manager customizado para lidar com a criação de usuários sem usar os campos padrão do Django.
    """
    def create_user(self, usuario, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        if not usuario:
            raise ValueError('O usuário é obrigatório')
        
        email = self.normalize_email(email)
        user = self.model(usuario=usuario, email=email, **extra_fields)
        # O Django ainda precisa do 'password' no Python para o set_password (hash da senha)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, usuario, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
            
        return self.create_user(usuario, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Model de usuário limpa, substituindo o AbstractUser.
    Campos estritos e nomenclatura customizada no banco de dados.
    """
    # 1. Id é injetado automaticamente pelo Django (BigAutoField)
    
    # 2. usuario (substitui o username)
    usuario = models.CharField(max_length=150, unique=True)
    
    # 3. nome_completo (substitui first_name e last_name)
    nome_completo = models.CharField(max_length=255, blank=False)
    
    # 4. email
    email = models.EmailField(unique=True, blank=False)
    
    # 5. telefone
    telefone = models.CharField(max_length=20, unique=True, blank=False)
    
    # 6. dt_nasc
    dt_nasc = models.DateField(null=True, blank=False)
    
    # 7. instituicao
    instituicao = models.CharField(max_length=255, null=True, blank=True)
    
    # 8. area_atuacao
    area_atuacao = models.CharField(max_length=255, null=True, blank=True)
    
    # 9. password -> senha (Renomeado apenas no banco de dados)
    password = models.CharField('senha', max_length=128, db_column='senha')
    
    # 10. dt_cadastro
    dt_cadastro = models.DateTimeField(default=timezone.now)
    
    # 11. last_login -> dt_login (Renomeado apenas no banco de dados)
    last_login = models.DateTimeField('último login', blank=True, null=True, db_column='dt_login')
    
    # 12. is_superuser (Vem do PermissionsMixin)
    
    # 13. is_staff
    is_staff = models.BooleanField(default=False)
    
    # 14. is_active
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    # Define qual campo será a principal chave de login do sistema (opcionalmente email ou usuario)
    USERNAME_FIELD = 'usuario'
    # Campos que o createsuperuser irá pedir pelo terminal além de usuario e senha
    REQUIRED_FIELDS = ['nome_completo', 'email', 'telefone', 'dt_nasc']

    def __str__(self):
        return f"{self.nome_completo} ({self.usuario})"


class Roadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    assunto = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Roadmap de {self.user.usuario} - {self.assunto}"

class Modulo(models.Model):
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='modulos')
    nome_modulo = models.CharField(max_length=255)
    ordem = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome_modulo

class Tarefa(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='tarefas')
    titulo = models.CharField(max_length=255)
    conteudo_exercicio = models.TextField(blank=True, null=True)
    concluido = models.BooleanField(default=False)
    tempo_estimado = models.PositiveIntegerField(help_text="Em minutos")
    pontos_dificuldade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Campos de Validação (Q&A)
    pergunta = models.TextField(blank=True, null=True, help_text="Pergunta para validação da tarefa")
    opcoes = models.JSONField(blank=True, null=True, help_text="Lista de opções de múltipla escolha")
    resposta_correta = models.CharField(max_length=255, blank=True, null=True, help_text="O texto exato da opção correta")

    def __str__(self):
        return self.titulo
