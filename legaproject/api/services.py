from google import genai
from django.conf import settings

class SocraticMentorService:
    """
    Serviço dedicado à comunicação com a API do Google Gemini.
    Atualizado para utilizar o SDK 'google-genai'.
    """
    
    SYSTEM_INSTRUCTION = (
        "Você é um Mentor educacional especializado em planejar trilhas de aprendizado (Roadmaps). "
        "Sua missão é gerar um plano de estudos detalhado, claro e estruturado, entregando a resposta "
        "pronta para o usuário em Markdown. NÃO faça perguntas de volta e NÃO aja de forma socrática. "
        "Apenas entregue o roteiro definitivo que o aluno solicitou."
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
                    system_instruction=self.SYSTEM_INSTRUCTION
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
