from langchain_community.tools.tavily_search import TavilySearchResults

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Initialize the Tavily Search tool
search_tool = TavilySearchResults(max_results=3)

# Define a test query
query = "What are the impacts of climate change on Gilgit-Baltistan"

# Run the search
results = search_tool.run(query)

# Print the results
print("Search Results:")
print(type(results))
for result in results:
    print(result["content"])
    print("                                                            ")