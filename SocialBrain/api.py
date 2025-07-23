from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, load_prompt
from typing import TypedDict, List, Annotated

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


import uvicorn
load_dotenv()



#pydantic model schema
from pydantic import BaseModel
from typing import List, Optional
from generate_post import get_trending_keywords

class user_input(BaseModel):
    prompt: str
    num_posts: int = 1
    tone: Optional[str] = None
    num_words: int = 50
    generate_image: bool = False



from fastapi import FastAPI, HTTPException
model = ChatOpenAI(temperature=0.7, model_name="gpt-4")
app = FastAPI(title="SocialBrain API", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or use ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# output schemas
class KeywordOutput(TypedDict):
    keywords: List[str]


class PostPrompt(TypedDict):
    prompt: Annotated[str, "The full prompt text"]
    hashtags: Annotated[str, "Relevant hashtags for the prompt"]

class PromptOutput(TypedDict):
    post_prompts: Annotated[list[PostPrompt], "List of post prompts, each containing the full prompt and relevant hashtags"]
    
class PostOutput(TypedDict):
    title: Annotated[str, "Title of the post"]
    post: Annotated[str, "Content of the post"] 
    hashtags: Annotated[str, "Hashtags for the post"]
    image_prompt: Annotated[str, "well described Image prompt for the post"]

## Generate whole post
@app.post("/generate_post")
async def generate_post(input: user_input):
    """
    Generate a social media post based on user input.
    """
    if not input.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    try:
        # Step 1: Extract trending keywords
        tempelate = load_prompt("keyword_prompt_template.json")
        formatted_prompt = tempelate.format(user_prompt=input.prompt)
        structured_keywords_model = model.with_structured_output(KeywordOutput, method="function_calling")
        keywords_result = structured_keywords_model.invoke(formatted_prompt)

        if isinstance(keywords_result, dict) and "keywords" in keywords_result:
            keywords = keywords_result["keywords"]
        else:
            raise HTTPException(status_code=500, detail="Failed to extract keywords")

        # Step 2: Generate post prompts
        post_template = load_prompt("post_prompt_template.json")
        formatted_post_prompt = post_template.format(
            user_prompt=input.prompt,
            keywords=keywords,
            tone=input.tone or "informative",
            num_posts=input.num_posts
        )
        structured_prompts_model = model.with_structured_output(PromptOutput, method="function_calling")
        prompts_result = structured_prompts_model.invoke(formatted_post_prompt)

        if "post_prompts" not in prompts_result:
            raise HTTPException(status_code=500, detail="Failed to generate post prompts")

        post_prompts = prompts_result["post_prompts"]

        # Step 3: Generate posts
        post_gen_template = load_prompt("post_generation_template.json")
        structured_post_model = model.with_structured_output(PostOutput, method="function_calling")
        posts = []

        for prompt in post_prompts:
            formatted_post_gen_prompt = post_gen_template.format(
                post_prompt=prompt,
                num_words=input.num_words,
                tone=input.tone or "informative"
            )
            post_result = structured_post_model.invoke(formatted_post_gen_prompt)

            if all(key in post_result for key in ["title", "post", "hashtags", "image_prompt"]):
                posts.append({
                    "title": post_result["title"],
                    "content": post_result["post"],
                    "hashtags": post_result["hashtags"],
                    "image_prompt": post_result["image_prompt"]
                })
            else:
                raise HTTPException(status_code=500, detail="Failed to generate post content")

        return {"posts": posts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


    # Generate trending keywords
@app.post("/get_keywords")
async def get_keywords(input: user_input):
    """
    Extract trending keywords based on user input.
    """
    if not input.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    try:
        # Step 1: Extract trending keywords
        tempelate = load_prompt("keyword_prompt_template.json")
        formatted_prompt = tempelate.format(user_prompt=input.prompt)
        structured_keywords_model = model.with_structured_output(KeywordOutput, method="function_calling")
        keywords_result = structured_keywords_model.invoke(formatted_prompt)

        if isinstance(keywords_result, dict) and "keywords" in keywords_result:
            keywords = keywords_result["keywords"]
        else:
            raise HTTPException(status_code=500, detail="Failed to extract keywords")

        return {"keywords": keywords}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

## Generate post prompts based on keywords
@app.post("/generate_post_prompts")
async def generate_post_prompts(input: user_input, keywords: List[str]):
    """
    Generate post prompts based on user input and selected keywords.
    """
    if not input.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    if not keywords or not isinstance(keywords, list):
        raise HTTPException(status_code=400, detail="Keywords must be a non-empty list")

    try:
        # Step 1: Generate post prompts
        post_template = load_prompt("post_prompt_template.json")
        formatted_post_prompt = post_template.format(
            user_prompt=input.prompt,
            keywords=keywords,
            tone=input.tone or "informative",
            num_posts=input.num_posts
        )
        structured_prompts_model = model.with_structured_output(PromptOutput, method="function_calling")
        prompts_result = structured_prompts_model.invoke(formatted_post_prompt)

        if "post_prompts" not in prompts_result:
            raise HTTPException(status_code=500, detail="Failed to generate post prompts")

        post_prompts = prompts_result["post_prompts"]

        return {"post_prompts": post_prompts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# Generate post with media
from image_generation import generate_image

@app.post("/generate_posts_with_media")
async def generate_posts_with_media(input: user_input, prompts: List[str]):
    """
    Generate posts based on selected prompts and optionally generate media.
    """
    if not prompts or not isinstance(prompts, list):
        raise HTTPException(status_code=400, detail="Prompts must be a non-empty list")

    try:
        # Initialize the post generation template
        post_gen_template = load_prompt("post_generation_template.json")
        structured_post_model = model.with_structured_output(PostOutput, method="function_calling")
        posts = []

        for prompt in prompts:
            # Step 1: Generate post content
            formatted_post_gen_prompt = post_gen_template.format(
                post_prompt=input.prompt,
                num_words=input.num_words or 300, 
                tone=input.tone or"informative"  # Default tone
            )
            post_result = structured_post_model.invoke(formatted_post_gen_prompt)

            if all(key in post_result for key in ["title", "post", "hashtags", "image_prompt"]):
                post_data = {
                    "title": post_result["title"],
                    "content": post_result["post"],
                    "hashtags": post_result["hashtags"],
                    "image_prompt": post_result["image_prompt"]
                }

                # Step 2: Optionally generate media
                if input.generate_image:
                    image_url , image_binary = generate_image(prompt=post_result["image_prompt"])

                    post_data["media_url"] = image_url
                    post_data["media_binary"] = image_binary

                posts.append(post_data)
            else:
                raise HTTPException(status_code=500, detail="Failed to generate post content")

        return {"posts": posts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# generate prompts based on user input
@app.post("/generate_ideas")
def generate_prompts(input: user_input):
    """
    Generate post prompts based on user input.
    """
    if not input.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    try:
        # Step 1: Extract trending keywords
        keywords = get_trending_keywords(input.prompt)

        # Step 2: Generate post prompts
        post_template = load_prompt("post_prompt_template.json")
        formatted_post_prompt = post_template.format(
            user_prompt=input.prompt,
            keywords=keywords,
            tone=input.tone or "informative",
            num_posts=input.num_posts
        )
        structured_prompts_model = model.with_structured_output(PromptOutput, method="function_calling")
        prompts_result = structured_prompts_model.invoke(formatted_post_prompt)

        if "post_prompts" not in prompts_result:
            raise HTTPException(status_code=500, detail="Failed to generate post prompts")

        post_prompts = prompts_result["post_prompts"]

        return {"post_prompts": post_prompts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
