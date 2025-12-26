import os
from langchain_openai import AzureChatOpenAI
from langchain_core.language_models.base import BaseLanguageModel
import streamlit as st

# Set Azure OpenAI environment variables
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://****************openai.azure.com"
os.environ["OPENAI_API_KEY"] = "0a07**********************1"

class ModelManager:
    """Manages Azure OpenAI GPT-4o model and connection"""
    def __init__(self):
        self._azure_llm = None

    @property
    def azure_llm(self) -> BaseLanguageModel:
        """Get or create AzureChatOpenAI LLM instance"""
        if self._azure_llm is None:
            try:
                self._azure_llm = AzureChatOpenAI(
                    deployment_name="gpt-4o",
                    model_name="gpt-4o",
                    openai_api_version="2023-05-15",
                    openai_api_type="azure",
                    temperature=0.0,
                    verbose=True
                )
            except Exception as e:
                st.error(f"Failed to initialize Azure OpenAI GPT-4o: {e}")
                st.error("Please ensure Azure OpenAI credentials and deployment are correct.")
                raise
        return self._azure_llm

    def test_connection(self) -> bool:
        """Test if Azure OpenAI connection is working"""
        try:
            response = self.azure_llm.invoke("Hello")
            return True
        except Exception as e:
            st.error(f"Azure OpenAI connection failed: {e}")
            return False

# Global model manager instance
model_manager = ModelManager()