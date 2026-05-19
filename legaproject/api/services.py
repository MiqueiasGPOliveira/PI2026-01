from google import genai
from django.conf import settings
from pydantic import BaseModel, Field

class TarefaSchema(BaseModel):
    titulo: str = Field(description="Título curto do exercício")
    conteudo_exercicio: str = Field(description="O que o aluno deve fazer detalhadamente")
    tempo_estimado: int = Field(description="Tempo estimado em minutos")
    pontos_dificuldade: int = Field(description="Um número inteiro de 1 a 5 representando a dificuldade (1 = muito fácil, 5 = muito difícil)")
    pergunta: str = Field(description="Uma pergunta de múltipla escolha para validar se o aluno entendeu a tarefa")
    opcoes: list[str] = Field(description="Uma lista contendo exatamente 4 opções curtas de resposta para a pergunta")
    resposta_correta: str = Field(description="O texto exato da opção correta (deve ser idêntico a um dos itens da lista de opções)")

class ModuloSchema(BaseModel):
    nome_modulo: str = Field(description="O nome do módulo. Ex: Módulo 1 - Fundamentos")
    tarefas: list[TarefaSchema] = Field(description="Lista de tarefas (exercícios) deste módulo")

class RoadmapSchema(BaseModel):
    modulos: list[ModuloSchema] = Field(description="Lista de módulos do roteiro")
class SocraticMentorService:
    """
    Serviço dedicado à comunicação com a API do Google Gemini.
    Atualizado para utilizar o SDK 'google-genai'.
    """
    
    SYSTEM_INSTRUCTION = (
        "Você é um Mentor educacional especializado em planejar trilhas de aprendizado (Roadmaps). "
        "Sua missão é gerar um plano de estudos detalhado, claro e estruturado, dividido em módulos lógicos, "
        "com cada módulo contendo exercícios práticos. NÃO aja de forma socrática e não faça perguntas. "
        "Apenas construa o roteiro rigorosamente dentro da estrutura de dados solicitada. O tempo_estimado da tarefa deve caber no tempo total que o aluno solicitou. "
        "Para CADA tarefa, crie uma 'pergunta' de múltipla escolha para testar o conhecimento do aluno sobre aquela tarefa, forneça 4 'opcoes' curtas e a 'resposta_correta' exata."
    )
    
    def __init__(self, model_name='gemini-2.5-flash'):
        self.model_name = model_name
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        if not self.api_key:
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None
                raise ValueError(f"Falha ao inicializar o cliente do Google Gemini: {str(e)}")

    def interact(self, user_prompt: str) -> str:
        """
        Recebe o texto do aluno e retorna a resposta construtiva do mentor socrático.
        """
        if not self.client:
            raise ValueError("Google Gemini API não está configurada corretamente no servidor.")
            
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=RoadmapSchema,
                    temperature=0.7
                )
            )
            # Retorna apenas o texto puro (conteúdo da resposta)
            if response.text:
                return response.text
            else:
                raise ValueError("A IA não retornou nenhum texto.")
                
        except Exception as e:
            # Levanta a exceção para que a camada de controle (View) decida como lidar
            raise ValueError(f"Ocorreu um erro ao comunicar com o Mentor: {str(e)}")
