import google.generativeai as genai
from django.conf import settings

# Configura a API de IA generativa com a chave armazenada em .env
if getattr(settings, 'GEMINI_API_KEY', None):
    genai.configure(api_key=settings.GEMINI_API_KEY)

class SocraticMentorService:
    """
    Serviço dedicado à comunicação com a API do Google Gemini.
    """
    
    SYSTEM_INSTRUCTION = (
        "Você é o 'Mentor', um tutor socrático de inteligência artificial. "
        "Sua missão não é fornecer a resposta pronta ou resolver o problema diretamente para o aluno. "
        "Em vez disso, faça perguntas instigantes, dê dicas guiadas, e incentive "
        "o pensamento crítico e o raciocínio. Ajude o usuário a chegar na conclusão por conta própria."
    )
    
    def __init__(self, model_name='gemini-1.5-flash'):
        self.model_name = model_name
        
        # Inicializa o modelo de IA e insere o prompt de sistema socrático global
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.SYSTEM_INSTRUCTION
            )
        except Exception as e:
            self.model = None

    def interact(self, user_prompt: str) -> str:
        """
        Recebe o texto do aluno e retorna a resposta construtiva do mentor socrático.
        """
        if not self.model:
            return "Erro: Google Gemini API não está configurada corretamente no servidor."
            
        try:
            response = self.model.generate_content(user_prompt)
            # Retorna apenas o texto puro (conteúdo da resposta)
            return response.text
        except Exception as e:
            return f"Ocorreu um erro ao comunicar com o Mentor: {str(e)}"
