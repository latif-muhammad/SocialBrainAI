from langchain_core.prompts import PromptTemplate

prompt1 = PromptTemplate(
    validate_template=True,
    input_variables=["user_prompt"],
    template="""
    You are a social media trend analyst. Given a user prompt, your job is to extract
    the most trending keywords, hashtags, and related tags that people are searching or using online.

    Rules:
    - Focus on keywords that are popular in 2025.
    - Include hashtags that are trending on Facebook, X, TikTok, Instagram, Linkedin and YouTube.
    - Return exactly 25 items as a list.
    - Don't include explanations, only output the tags or keywords.

    User Prompt: "{user_prompt}"

    Trending Keywords:
    """
)
prompt1.save("keyword_prompt_template.json")


prompt2 = PromptTemplate(
    template="""
You are a creative social media strategist and Prompt Engineer.

    Based on the following:
    - User Topic: {user_prompt}
    - Trending Keywords: {keywords}
    - Tone: {tone}
    - Number of Posts: {num_posts}

    Generate {num_posts} UNIQUE and engaging social media post prompts.

    Rules:
    - Incorporate multiple trending keywords into each post idea (at least 2 per post)
    - Match the tone: {tone}
    - Write breifly about the post structure and things to include (7 sentences max)
    - Include a separate line with 7-10 hashtags
    - Each post should be unique and not repetitive.
    - specify that the post is a text based social media post.


    Format:
    1. prompt: ...
       Hashtags: ...

    Start now.
""",
input_variables=["user_prompt" ,"keywords","tone","num_posts"],
    validate_template=True,
)

prompt2.save("post_prompt_template.json")   


post_generation_template = PromptTemplate(
    template="""
You are a professional social media content creator.

    Based on the following:
    - Post Prompt: {post_prompt}
    - Number of Words: {num_words}
    - Tone: {tone}

    Generate a high-quality social media post.

    Rules:
    - Ensure the post adheres to the specified tone: {tone} and {post_prompt}.
    - The post should be {num_words} words.
    - Include a call-to-action (CTA) at the end of the post.
    - Use engaging language to capture the audience's attention.
    - If applicable, include 3-5 relevant hashtags at the end of the post.

    Also Generate a well designed image prompt for the post.
    - The image prompt should be visually appealing and relevant to the post content.
    - Include details about colors, style, and any specific elements to include in the image.
    - The image prompt should be suitable for platforms like Instagram, Facebook, or Twitter.
    - The image prompt should be 2-4 sentences.

    Format:
    Post: ...
    Hashtags: ...
    imaege prompt: ...

    Start now.
""",
    input_variables=["post_prompt", "num_words", "tone"],
    validate_template=True,
)

post_generation_template.save("post_generation_template.json")  