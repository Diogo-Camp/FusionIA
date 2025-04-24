import time
import requests
import json
from requests.exceptions import JSONDecodeError

class ChatbotClient:
    def __init__(self, base_url="http://192.168.0.36:5000"):
        self.base_url = base_url
        self.conversation_id = None
        self.session = requests.Session()  # Session para melhor performance
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _safe_request(self, method, endpoint, **kwargs):
        """Wrapper para lidar com erros de JSON"""
        try:
            response = getattr(self.session, method)(f"{self.base_url}{endpoint}", **kwargs)
            response.raise_for_status()  # Levanta erro para status 4xx/5xx
            return response.json()
        except JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            print(f"Resposta bruta: {response.text[:200]}...")
            return None
        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None
    
    def start_conversation(self, title="Nova Conversa"):
        payload = json.dumps({'title': title})
        result = self._safe_request('post', '/api/start', data=payload)
        if result:
            self.conversation_id = result.get('conversation_id')
            print(f"Conversa iniciada: {self.conversation_id}")
        else:
            print("Falha ao iniciar conversa")
    
    # def send_message(self, message):
    #     if not self.conversation_id:
    #         self.start_conversation()
        
    #     payload = json.dumps({
    #         'conversation_id': self.conversation_id,
    #         'message': message
    #     })
        
    #     result = self._safe_request('post', '/api/chat', data=payload)
    #     if result:
    #         print(f"\nAssistente: {result.get('response')}")
    #         print(f"Modelo: {result.get('metadata', {}).get('model')}")
    #     else:
    #         print("Não foi possível obter resposta")
    def send_message(self, message):
        if not self.conversation_id:
            self.start_conversation()
        
        payload = json.dumps({
            'conversation_id': self.conversation_id,
            'message': message
        })
        
        result = self._safe_request('post', '/api/chat', data=payload)
        if result:
            print(f"\nAssistente: {result.get('response')}")
            print(f"Modelo: {result.get('metadata', {}).get('model')}")
            print(f"Tokens usados: {result.get('metadata', {}).get('tokens_used', 'N/A')}")
        else:
            print("Não foi possível obter resposta")
        
        return result  # Opcional: retorna o resultado completo para uso posterior


def main():
    client = ChatbotClient()
    
    # Testa conexão
    try:
        health = requests.get(f"{client.base_url}/api/health", timeout=2)
        print(f"Conectado ao servidor: {health.json()}")
    except:
        print("Não foi possível conectar ao servidor. Verifique se está rodando.")
        return
    
    client.start_conversation()
    
    while True:
        try:
            message = input("\nVocê: ")
            if message.lower() in ['sair', 'exit', 'quit']:
                break
            client.send_message(message)
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break

if __name__ == "__main__":
    main()
