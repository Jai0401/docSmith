"""OpenRouter API client using langchain-openai."""
import os

# OpenRouter config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Free model on OpenRouter that supports web search + streaming
MODEL = "tencent/hy3-preview:free"

# Site metadata for OpenRouter
HTTP_REFERER = "https://docsmith.ai"
X_TITLE = "docSmith"

_lc_llm = None


def get_llm():
    """Get or create the langchain-openai LLM instance."""
    global _lc_llm
    if _lc_llm is None:
        from langchain_openai import ChatOpenAI
        _lc_llm = ChatOpenAI(
            model=MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.1,
            default_headers={
                "HTTP-Referer": HTTP_REFERER,
                "X-Title": X_TITLE,
            },
        )
    return _lc_llm


class ChatOpenRouter:
    """
    Drop-in replacement for ChatGroq using OpenRouter.
    Wraps langchain-openai ChatOpenAI with OpenRouter base URL.
    """

    def __init__(self, api_key: str = None, model: str = MODEL, temperature: float = 0.1, streaming: bool = True):
        from langchain_openai import ChatOpenAI
        self.model = model
        self.temperature = temperature
        self.streaming = streaming
        self._lc_llm = ChatOpenAI(
            model=model,
            api_key=api_key or OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=temperature,
            default_headers={
                "HTTP-Referer": HTTP_REFERER,
                "X-Title": X_TITLE,
            },
        )

    async def agenerate(self, message_batch: list, **kwargs):
        """Non-streaming async generate. Returns GenerationResult-like object."""
        from langchain_core.messages import HumanMessage, SystemMessage

        formatted = []
        for group in message_batch:
            for msg in group:
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    role = msg.get("role", "user")
                    if role == "system":
                        formatted.append(SystemMessage(content=content))
                    else:
                        formatted.append(HumanMessage(content=content))
                else:
                    formatted.append(msg)

        return await self._lc_llm.agenerate([formatted])

    def bind_tools(self, tools):
        """Delegate to langchain-openai bind_tools."""
        return self._lc_llm.bind_tools(tools)