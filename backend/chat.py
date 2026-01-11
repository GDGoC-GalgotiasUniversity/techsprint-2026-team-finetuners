from google import genai
from google.genai import types
from pydantic import BaseModel
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    book_context: str  
    book_title: Optional[str] = "the book"


class ChatResponse(BaseModel):
    success: bool
    response: str
    error: Optional[str] = None


async def generate_chat_response(
    client: genai.Client,
    message: str,
    book_context: str,
    book_title: str,
    text_semaphore: asyncio.Semaphore,
    retry_func
) -> ChatResponse:
   
    logger.info(f"Generating chat response for message: '{message[:50]}...'")
    
    prompt = f"""You are a helpful assistant that answers questions about a children's storybook.

Book Title: {book_title}

Book Content:
{book_context}

User Question: {message}

Instructions:
- Answer the question based ONLY on the book content provided above
- If the answer is not in the book, say "I don't have that information in the story"
- Keep answers simple and friendly, suitable for children aged 6-8
- Be concise but informative
- Use a warm, storytelling tone

Answer:"""

    async def _call_api():
        async with text_semaphore:
            logger.debug("Calling Gemini API for chat response")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
        return response

    try:
        response = await retry_func(_call_api)
        answer = response.text.strip()
        logger.info(f"Chat response generated successfully. Length: {len(answer)} chars")
        
        return ChatResponse(
            success=True,
            response=answer
        )
    
    except Exception as e:
        logger.error(f"Failed to generate chat response: {str(e)}", exc_info=True)
        return ChatResponse(
            success=False,
            response="",
            error=f"Failed to generate response: {str(e)}"
        )
