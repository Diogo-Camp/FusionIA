import ollama
import torch
import time
import logging
from typing import List, Dict, Optional

class OllamaWrapper:
    def __init__(self):
        self.gpu_layers = -1 if torch.cuda.is_available() else 0
        self.timeout = 30
        self.logger = logging.getLogger(__name__)
        self._verify_connection()

    def _verify_connection(self):
        """Verificação tolerante que não depende da estrutura exata"""
        try:
            # Tentativa simples de comunicação
            try:
                ollama.list()
            except:
                # Fallback para versões mais novas
                ollama.chat(model='mistral', messages=[], stream=False)
                
            self.logger.info("Conexão com Ollama verificada")
        except Exception as e:
            self.logger.error(f"Ollama não disponível: {str(e)}")
            raise RuntimeError("Ollama não respondeu. Execute 'ollama serve' primeiro")

    def generate_response(self, messages: List[Dict], config: Optional[Dict] = None) -> str:
        """Geração com fallbacks robustos"""
        try:
            response = ollama.chat(
                model='mistral',
                messages=messages,
                stream=False,
                options={
                    'temperature': 0.7,
                    'num_ctx': 2048,
                    'num_gpu': self.gpu_layers,
                } | (config or {})
            )
            
            # Extração tolerante do conteúdo
            content = ""
            if isinstance(response, dict):
                message = response.get('message', {})
                if isinstance(message, dict):
                    content = message.get('content', '')

            if not content.strip():
                raise ValueError("Resposta vazia do modelo")
                
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"Falha na geração: {str(e)}")
            raise RuntimeError(f"Erro ao gerar resposta: {str(e)}")