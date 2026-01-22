import os
import dotenv
dotenv.load_dotenv()

import requests
import re
from crewai.tools import tool
from typing import Optional


def create_web_search_tool(domains: Optional[list[str]] = None):
    """
    Create a web search tool with optional domain filtering.

    Args:
        domains: List of domains to search within (e.g., ["linkedin.com", "jobkorea.co.kr"])
    """
    @tool
    def web_search_tool(query: str):
        """
        Web Search Tool.
        Args:
            query: str
                The query to search the web for.
        Returns:
            A list of search results with the website content in Markdown format.
        """
        url = "https://api.firecrawl.dev/v1/search"
        api_key = os.getenv("FIRECRAWL_API_KEY")

        # Add site: operator to query if domains are specified
        search_query = query
        if domains:
            site_filter = " OR ".join([f"site:{domain}" for domain in domains])
            search_query = f"({site_filter}) {query}"

        payload = {
            "query": search_query,
            "limit": 5,
            "scrapeOptions": {
                "formats": ["markdown"]
            }
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        response = response.json()

        if not response.get("success"):
            return f"Error using tool: {response}"

        cleaned_chunks = []
        for result in response.get("data", []):
            title = result.get("title", "")
            result_url = result.get("url", "")
            markdown = result.get("markdown", "")

            cleaned = re.sub(r'\\+|\n+', '', markdown).strip()
            cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

            cleaned_result = {
                "title": title,
                "url": result_url,
                "markdown": cleaned,
            }

            cleaned_chunks.append(cleaned_result)

        return cleaned_chunks

    return web_search_tool


# Default tool without domain filtering (for backward compatibility)
web_search_tool = create_web_search_tool()
