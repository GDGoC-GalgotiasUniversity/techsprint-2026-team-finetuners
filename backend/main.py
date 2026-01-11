from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import ServerError
import os
import base64
import re
import asyncio
from typing import List, Optional
import json
from dotenv import load_dotenv
import PyPDF2
import io
import random
import logging

from chat import ChatRequest, ChatResponse, generate_chat_response

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=api_key)



TEXT_SEMAPHORE = asyncio.Semaphore(2)      
IMAGE_SEMAPHORE = asyncio.Semaphore(1)     

IMAGE_CACHE: dict[str, str] = {}           


class Chapter(BaseModel):
    chapter_number: int
    title: Optional[str] = ""
    raw_text: str  
    simplified_text: Optional[str] = ""
    image: Optional[str] = ""
    image_prompt: Optional[str] = ""
    simplified: bool = False  

class ProcessedBook(BaseModel):
    title: str
    total_chapters: int
    chapters: List[Chapter]

class ImageRequest(BaseModel):
    chapter_number: int
    image_prompt: str

class SimplifyChapterRequest(BaseModel):
    chapter_number: int
    raw_text: str

# Retry Logic

async def retry_with_backoff(func, *args, max_retries=5, initial_delay=1, **kwargs):
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except ServerError as e:
            if attempt == max_retries - 1:
                logger.error(f"Max retries ({max_retries}) reached. Last error: {e}")
                print(f"Max retries reached. Last error: {e}")
                raise e
            
            if hasattr(e, 'code') and e.code != 503:
                logger.error(f"Non-503 ServerError encountered: {e}")
                raise e

            delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Gemini 503 Error (Overloaded). Retrying in {delay:.2f}s... (Attempt {attempt + 1}/{max_retries})")
            print(f"Gemini 503 Error (Overloaded). Retrying in {delay:.2f}s... (Attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay)
    return await func(*args, **kwargs) 



def extract_text_from_pdf(pdf_file: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def split_into_chapters(text: str) -> List[dict]:
    pattern = r'(?:Chapter|CHAPTER)\s+(\d+)(.*?)(?=Chapter\s+\d+|$)'
    matches = re.findall(pattern, text, re.S)

    chapters = []
    for i, (_, content) in enumerate(matches[:10]):
        chapters.append({
            "number": i + 1,
            "text": content.strip()[:2500]
        })

    if not chapters:
        words = text.split()
        for i in range(0, min(len(words), 5000), 500):
            chapters.append({
                "number": len(chapters) + 1,
                "text": " ".join(words[i:i+500])
            })

    return chapters[:10]

# Chapter Processing using API

async def process_chapter_ai(text: str) -> dict:
    logger.info(f"Starting AI processing for chapter (text length: {len(text)} chars)")
    
    prompt = f"""
You are creating a children's storybook for kids aged 6 to 8.

Your task:
1. Create a SHORT chapter title
2. Rewrite the chapter in VERY SIMPLE ENGLISH
3. Create ONE image description for an illustration

IMPORTANT RULES:
- Use simple words a child can understand
- Use short sentences (8–12 words max)
- Sound like a bedtime story
- Do NOT explain morals
- Do NOT use difficult words
- Do NOT talk to the reader
- Do NOT mention chapters, summaries, or rewriting
- Start the story directly

TITLE RULES:
- 2 or 3 words only
- NO verbs (only nouns & adjectives)
- Easy words for kids
- Title Case (Example: "Magic Forest", "Lost Puppy")

IMAGE PROMPT RULES:
- Describe ONE clear scene
- Colorful children's book illustration
- Happy, soft, friendly style
- No violence, fear, or darkness

Return ONLY valid JSON in this exact format:

{{
  "title": "Example Title",
  "simplified_text": "Very simple story text here.",
  "image_prompt": "Colorful children's illustration description"
}}

Chapter text:
{text[:2200]}
"""

    async def _call_api():
        async with TEXT_SEMAPHORE:
            logger.debug("Calling Gemini API for chapter processing")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.6
                )
            )
        return response

    response = await retry_with_backoff(_call_api)
    result = json.loads(response.text)
    logger.info(f"Chapter AI processing completed. Title: '{result.get('title', 'N/A')}'")
    return result


#  Image Generation 

async def generate_image_cached(prompt: str) -> str:
    if prompt in IMAGE_CACHE:
        logger.info(f"Image cache HIT for prompt: '{prompt[:50]}...'")
        return IMAGE_CACHE[prompt]
    
    logger.info(f"Image cache MISS. Generating new image for prompt: '{prompt[:50]}...'")

    async def _call_api():
        async with IMAGE_SEMAPHORE:
            logger.debug("Calling Gemini API for image generation")
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=f"Children's book illustration, colorful: {prompt}",
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
        return response

    response = await retry_with_backoff(_call_api)

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image = "data:image/png;base64," + base64.b64encode(
                part.inline_data.data
            ).decode()
            IMAGE_CACHE[prompt] = image
            logger.info(f"Image generated and cached successfully. Cache size: {len(IMAGE_CACHE)}")
            return image

    logger.warning("No image data found in API response")
    return ""



@app.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    
    logger.info(f"Received PDF upload request: {file.filename}")
    
    async def stream():
        try:
            pdf_bytes = await file.read()
            logger.info(f"PDF file read successfully. Size: {len(pdf_bytes)} bytes")
            yield f"data: {json.dumps({'type': 'progress', 'progress': 10})}\n\n"

            text = extract_text_from_pdf(pdf_bytes)
            logger.info(f"Text extracted from PDF. Total length: {len(text)} characters")
            title = text.split("\n")[0][:80] or "Kids Book"
            logger.info(f"Book title: '{title}'")

            yield f"data: {json.dumps({'type': 'progress', 'progress': 30})}\n\n"

            chapters_raw = split_into_chapters(text)
            logger.info(f"Split into {len(chapters_raw)} chapters")
            chapters: list[Chapter] = []

            # Extract chapters without AI processing
            for i, ch in enumerate(chapters_raw):
                logger.debug(f"Processing chapter {i+1}/{len(chapters_raw)}: Chapter {ch['number']}")
                yield f"data: {json.dumps({'type': 'progress', 'message': f'Extracting chapter {i+1}', 'progress': 40 + i * 5})}\n\n"

                chapters.append(Chapter(
                    chapter_number=ch["number"],
                    title=f"Chapter {ch['number']}",  
                    raw_text=ch["text"],  
                    simplified_text="",  
                    image_prompt="",
                    image="",
                    simplified=False  
                ))

            book = ProcessedBook(
                title=title,
                total_chapters=len(chapters),
                chapters=chapters
            )

            logger.info(f"PDF processing complete. Book: '{title}' with {len(chapters)} chapters")
            yield f"data: {json.dumps({'type': 'complete', 'data': book.model_dump(), 'progress': 100})}\n\n"
        
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")



@app.post("/simplify_chapter")
async def simplify_chapter(req: SimplifyChapterRequest):
    
    # Simplify singular chapter per demand

    logger.info(f"Received simplify_chapter request for chapter {req.chapter_number}")
    try:
        # Process the chapter with AI
        ai_result = await process_chapter_ai(req.raw_text)
        
        logger.info(f"Chapter {req.chapter_number} simplified successfully. Title: '{ai_result['title']}'")
        return {
            "success": True,
            "chapter_number": req.chapter_number,
            "title": ai_result["title"],
            "simplified_text": ai_result["simplified_text"],
            "image_prompt": ai_result["image_prompt"]
        }
    except Exception as e:
        logger.error(f"Failed to simplify chapter {req.chapter_number}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to simplify chapter: {str(e)}"
        )


@app.post("/generate_images")
async def generate_images(req: ImageRequest):
    logger.info(f"Received generate_images request for chapter {req.chapter_number}")
    image = await generate_image_cached(req.image_prompt)
    logger.info(f"Image generation complete for chapter {req.chapter_number}")
    return {"image": image}


@app.post("/chat")
async def chat(req: ChatRequest):
    
    logger.info(f"Received chat request: '{req.message[:50]}...'")
    
    response = await generate_chat_response(
        client=client,
        message=req.message,
        book_context=req.book_context,
        book_title=req.book_title,
        text_semaphore=TEXT_SEMAPHORE,
        retry_func=retry_with_backoff
    )
    
    if response.success:
        logger.info("Chat response generated successfully")
        return {"success": True, "response": response.response}
    else:
        logger.error(f"Chat response failed: {response.error}")
        raise HTTPException(
            status_code=500,
            detail=response.error or "Failed to generate chat response"
        )



