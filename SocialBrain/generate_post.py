from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate, load_prompt

load_dotenv()

# Initialize the LLM
model = ChatOpenAI(temperature=0.7, model_name="gpt-4")


# Function for user inpput
def get_user_input():
    user_input = input("Please enter the topic for your social media post: ")
    num_posts = input("How many posts would you like to generate? ")
    tone = input("What tone would you like for the posts? (e.g., professional, casual, humorous , informative): ")

    if not num_posts.isdigit() or int(num_posts) <= 0:
        print("Invalid input. Please enter a positive integer.")
        return get_user_input()
    
    return user_input , int(num_posts), tone



# Function to extract trending keywords related to the prompt 
tempelate = load_prompt("keyword_prompt_template.json")

## structured keyword output json schema
from typing import TypedDict, List, Annotated

class KeywordOutput(TypedDict):
    keywords: List[str]

structured_keywords_model = model.with_structured_output(KeywordOutput, method="function_calling")


import json  # Add this import for JSON handling

# Function to get keywords
def get_trending_keywords(user_prompt):
    # Format the template with the user prompt
    formatted_prompt = tempelate.format(user_prompt=user_prompt)
    # Pass the formatted string to the model
    result = structured_keywords_model.invoke(formatted_prompt)
    
    # Ensure the result is a dictionary and contains the "keywords" key
    if isinstance(result, dict) and "keywords" in result:
        return result["keywords"]
    else:
        print("Error: Unexpected result format or missing 'keywords' key.")
        return []




# Json schema for post prompt output

class PromptOutput(TypedDict):
    post_prompts : Annotated[list[str], "List of post prompts each prompt contains the full prompt and the relevent hashtags"]

structured_prompts_model = model.with_structured_output(PromptOutput, method="function_calling")

# Function to generate post prompts
def generate_post_prompts(user_prompt, keywords, tone, num_posts):
    # Load the post prompt template
    post_template = load_prompt("post_prompt_template.json")
    
    # Format the template with the user inputs
    formatted_post_prompt = post_template.format(
        user_prompt=user_prompt,
        keywords=keywords,
        tone=tone,
        num_posts=num_posts
    )
    
    # Pass the formatted string to the model
    result = structured_prompts_model.invoke(formatted_post_prompt)
    return result["post_prompts"]



## Post Generation

class PostOutput(TypedDict):
    title: Annotated[str, "Title of the post"]
    post: Annotated[str, "Content of the post"] 
    hashtags: Annotated[str, "Hashtags for the post"]
    image_prompt: Annotated[str, "well described Image prompt for the post"]


structured_post_model = model.with_structured_output(PostOutput, method="function_calling")

def post_generation(post_prompt, num_words, tone):
    # Load the post generation template
    post_gen_template = load_prompt("post_generation_template.json")
    
    # Format the template with the user inputs
    formatted_post_gen_prompt = post_gen_template.format(
        post_prompt=post_prompt,
        num_words=num_words,
        tone=tone
    )
    
    # Pass the formatted string to the model
    result = structured_post_model.invoke(formatted_post_gen_prompt)
    
    # Return the generated post content and hashtags
    return result["title"], result["post"], result["hashtags"], result["image_prompt"]



# ## Main
# user_input = "impacts of climate change on Gilgit-Baltistan"
# num_posts = 3
# tone = "informative"
# #user_input, num_posts , tone = get_user_input()
# keywords = get_trending_keywords(user_input)
# # print(user_input)
# # print("-----------------------------------------------------")
# # print("Trending Keywords:")
# # print("-----------------------------------------------------")
# # print(keywords)
# # print("-----------------------------------------------------")

# # for kw in keywords:
# #     print(kw.strip())
# # print("-----------------------------------------------------")
# # print(type(keywords))
# prompts = generate_post_prompts(user_input, keywords, tone, num_posts)
 
# # # print(prompts)
# # for prompt in prompts:
# #     print(prompt)
# #     print("                                                             ")

# # print("-----------------------------------------------------")
# # print(len(prompts))
# for prompt in prompts:
#     print("Post Prompt:")
#     print(prompt)
#     print("-----------------------------------------------------")
#     # Generate the post based on the prompt
#     title, post, hashtags = post_generation(prompt, 300, tone)
#     print("Title:")
#     print(title)
#     print("Post:")
#     print(post)
#     print("Hashtags:")
#     print(hashtags)
#     print("-----------------------------------------------------")
