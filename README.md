# 🤖 SocialBrain AI Microservice

This microservice powers the AI capabilities of the **SocialBrain** app — an intelligent social media automation tool that generates high-quality, on-brand content for users. This service handles prompt processing, trend analysis, and content generation using cutting-edge LLM frameworks and APIs.

## 🧠 Overview

The AI microservice is built using **FastAPI** and leverages **LangChain**, **OpenAI APIs**, and **Retrieval-Augmented Generation (RAG)** to deliver intelligent responses for:

- Trend analysis on user prompts
- Generating new, refined prompts
- Brainstorming creative post ideas
- Crafting complete social media posts

This service runs independently and communicates with the main Node.js backend of SocialBrain.

---

## 🚀 Tech Stack

| Component | Description |
|----------|-------------|
| **FastAPI** | Lightweight Python web framework for serving AI endpoints |
| **LangChain** | Framework to build LLM-powered applications |
| **OpenAI API** | Used for GPT-powered content generation |
| **MongoDB** | Stores metadata and intermediate prompt/post data |
| **Python** | Core programming language for this service |

---

## 📦 Features

### 1. Prompt Refinement & Trend Analysis
Analyzes the user’s original input to extract topics and generate a more targeted prompt using LangChain chains and OpenAI LLMs.

### 2. Idea Generation
Takes the refined prompt and generates multiple post ideas with appropriate tone and intent.

### 3. Post Creation
Generates well-structured, platform-optimized social media posts (e.g., for Twitter, LinkedIn) using prompt templates and LLMs.
