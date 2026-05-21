"""
title: Web Search and Crawl
description: Search and crawl local/self-hosted sources using SearXNG, OpenWebUI Native Search, and Crawl4AI. Public network access is blocked by default for Air-Gap operation.
author: lexiismadd
author_url: https://github.com/lexiismadd
funding_url: https://github.com/open-webui
version: 3.0.6
license: MIT
offline: false
"""
# Air-gap integration note:
# Imported from the public OpenWebUI tool export stored under
# Tools/openwebui_ext/third_party/public_openwebui_tools/.
# Defaults were adjusted for offline operation: no public API fallback, no
# external CDN by default, and no public web crawling/search unless an admin
# explicitly configures local/self-hosted endpoints and allowlists.
import traceback
import requests
import re
import json
try:
    import orjson
except ImportError:
    class _OrjsonCompat:
        JSONDecodeError = json.JSONDecodeError

        @staticmethod
        def dumps(value):
            return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        @staticmethod
        def loads(value):
            if isinstance(value, (bytes, bytearray)):
                value = value.decode("utf-8")
            return json.loads(value)

    orjson = _OrjsonCompat()
import aiohttp
import asyncio
import ipaddress
from urllib.parse import parse_qs, urlparse, quote
from pydantic import BaseModel, Field, model_validator
from typing import Any, List, Optional, Union, Callable, Literal
try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger("web_search_and_crawl")

# Import HTMLResponse for rich UI embedding
try:
    from fastapi.responses import HTMLResponse
    HTMLRESPONSE_AVAILABLE = True
except ImportError:
    HTMLRESPONSE_AVAILABLE = False
    logger.info("fastapi not available, rich UI embeds disabled")

# tiktoken is optional - use fallback estimation if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.info("tiktoken not available, using fallback token estimation")


# ============================================================================
# Crawl4AI Configuration Stubs
# These classes mirror the crawl4ai library's config classes but are lightweight
# stubs that just serialize to JSON for the remote Crawl4AI API. This avoids
# requiring the full crawl4ai package (which has heavy browser dependencies).
# ============================================================================

class CacheMode:
    """Cache mode enumeration for Crawl4AI."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    BYPASS = "bypass"
    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"


class LLMConfig:
    """LLM configuration for Crawl4AI extraction strategies."""
    def __init__(
        self,
        provider: str = "openai/gpt-4o-mini",
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
    ):
        self.provider = provider
        self.base_url = base_url
        self.api_token = api_token
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def dump(self) -> dict:
        """Serialize to Crawl4AI API format: {"type": "ClassName", "params": {...}}"""
        params = {"provider": self.provider, "temperature": self.temperature}
        if self.base_url:
            params["base_url"] = self.base_url
        if self.api_token:
            params["api_token"] = self.api_token
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.frequency_penalty is not None:
            params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty is not None:
            params["presence_penalty"] = self.presence_penalty
        return {"type": "LLMConfig", "params": params}


class LLMExtractionStrategy:
    """LLM-based extraction strategy for Crawl4AI."""
    def __init__(
        self,
        llm_config: LLMConfig,
        instruction: str = "",
        input_format: str = "fit_markdown",
        schema: Optional[dict] = None,
    ):
        self.llm_config = llm_config
        self.instruction = instruction
        self.input_format = input_format
        self.schema = schema

    def dump(self) -> dict:
        """Serialize to Crawl4AI API format: {"type": "ClassName", "params": {...}}"""
        params = {
            "llm_config": self.llm_config.dump(),
            "instruction": self.instruction,
            "input_format": self.input_format,
        }
        if self.schema:
            params["schema"] = {"type": "dict", "value": self.schema}
        return {"type": "LLMExtractionStrategy", "params": params}


class PruningContentFilter:
    """Content filter that prunes irrelevant content."""
    def __init__(self, threshold: float = 0.5, threshold_type: str = "fixed", min_word_threshold: int = 50):
        self.threshold = threshold
        self.threshold_type = threshold_type
        self.min_word_threshold = min_word_threshold

    def dump(self) -> dict:
        """Serialize to Crawl4AI API format: {"type": "ClassName", "params": {...}}"""
        return {
            "type": "PruningContentFilter",
            "params": {
                "threshold": self.threshold,
                "threshold_type": self.threshold_type,
                "min_word_threshold": self.min_word_threshold,
            }
        }


class DefaultMarkdownGenerator:
    """Default markdown generator for Crawl4AI."""
    def __init__(self, content_filter: Optional[PruningContentFilter] = None, options: Optional[dict] = None):
        self.content_filter = content_filter
        self.options = options or {}

    def dump(self) -> dict:
        """Serialize to Crawl4AI API format: {"type": "ClassName", "params": {...}}"""
        params = {"options": {"type": "dict", "value": self.options}}
        if self.content_filter:
            params["content_filter"] = self.content_filter.dump()
        return {"type": "DefaultMarkdownGenerator", "params": params}


class DefaultTableExtraction:
    """Default table extraction strategy."""
    def __init__(self):
        pass

    def dump(self) -> dict:
        """Serialize to Crawl4AI API format: {"type": "ClassName", "params": {...}}"""
        return {"type": "DefaultTableExtraction", "params": {}}


class BrowserConfig:
    """Browser configuration for Crawl4AI."""
    def __init__(
        self,
        headless: bool = True,
        light_mode: bool = False,
        headers: Optional[dict] = None,
        extra_args: Optional[List[str]] = None,
        user_agent: Optional[str] = None,
    ):
        self.headless = headless
        self.light_mode = light_mode
        self.headers = headers or {}
        self.extra_args = extra_args or []
        self.user_agent = user_agent

    def dump(self) -> dict:
        """Serialize to Crawl4AI API format: {"type": "ClassName", "params": {...}}"""
        params = {
            "headless": self.headless,
            "light_mode": self.light_mode,
            "headers": {"type": "dict", "value": self.headers},
            "extra_args": self.extra_args,
        }
        if self.user_agent:
            params["user_agent"] = self.user_agent
        return {"type": "BrowserConfig", "params": params}


class CrawlerRunConfig:
    """Crawler run configuration for Crawl4AI."""
    def __init__(
        self,
        markdown_generator: Optional[DefaultMarkdownGenerator] = None,
        extraction_strategy: Optional[LLMExtractionStrategy] = None,
        table_extraction: Optional[DefaultTableExtraction] = None,
        exclude_external_links: bool = False,
        exclude_social_media_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        user_agent: Optional[str] = None,
        stream: bool = False,
        cache_mode: str = CacheMode.BYPASS,
        page_timeout: int = 60000,
        only_text: bool = False,
        word_count_threshold: int = 200,
        exclude_all_images: bool = False,
        exclude_external_images: bool = False,
    ):
        self.markdown_generator = markdown_generator
        self.extraction_strategy = extraction_strategy
        self.table_extraction = table_extraction
        self.exclude_external_links = exclude_external_links
        self.exclude_social_media_domains = exclude_social_media_domains or []
        self.exclude_domains = exclude_domains or []
        self.user_agent = user_agent
        self.stream = stream
        self.cache_mode = cache_mode
        self.page_timeout = page_timeout
        self.only_text = only_text
        self.word_count_threshold = word_count_threshold
        self.exclude_all_images = exclude_all_images
        self.exclude_external_images = exclude_external_images

    def dump(self) -> dict:
        """Serialize to Crawl4AI API format: {"type": "ClassName", "params": {...}}"""
        params = {
            "exclude_external_links": self.exclude_external_links,
            "exclude_social_media_domains": self.exclude_social_media_domains,
            "exclude_domains": self.exclude_domains,
            "stream": self.stream,
            "cache_mode": self.cache_mode,
            "page_timeout": self.page_timeout,
            "only_text": self.only_text,
            "word_count_threshold": self.word_count_threshold,
            "exclude_all_images": self.exclude_all_images,
            "exclude_external_images": self.exclude_external_images,
        }
        if self.markdown_generator:
            params["markdown_generator"] = self.markdown_generator.dump()
        if self.extraction_strategy:
            params["extraction_strategy"] = self.extraction_strategy.dump()
        if self.table_extraction:
            params["table_extraction"] = self.table_extraction.dump()
        if self.user_agent:
            params["user_agent"] = self.user_agent
        return {"type": "CrawlerRunConfig", "params": params}


# Unused stubs kept for potential future use
class BestFirstCrawlingStrategy:
    """Best-first crawling strategy stub."""
    pass


class KeywordRelevanceScorer:
    """Keyword relevance scorer stub."""
    pass


# ============================================================================
# End of Crawl4AI Configuration Stubs
# ============================================================================

# OpenWebUI imports for native search
try:
    from fastapi import Request
    from open_webui.main import app  # type: ignore
    from open_webui.models.users import UserModel, Users  # type: ignore
    from open_webui.routers.retrieval import SearchForm, process_web_search  # type: ignore
    NATIVE_SEARCH_AVAILABLE = True
except ImportError as e:
    NATIVE_SEARCH_AVAILABLE = False
    logger.warning(f"OpenWebUI native search not available: {e}")


class ArticleData(BaseModel):
    topic: str
    summary: str


class ResearchCrawlMode:
    """Enumeration of research crawling modes."""
    PSEUDO_ADAPTIVE = "pseudo_adaptive"
    LLM_GUIDED = "llm_guided"
    BFS_DEEP = "bfs_deep"
    RESEARCH_FILTER = "research_filter"


class Tools:
    class Valves(BaseModel):
        INITIAL_RESPONSE: str = Field(
            title="Initial delta response",
            default="One moment while I crawl local/offline sources...",
            description="The response the tool will post in the chat window when it starts its search and crawl. Set as blank for no response."
        )
        USE_NATIVE_SEARCH: bool = Field(
            title="Use Native Search",
            default=False,
            description="Air-gap default: disabled. Enable only if OpenWebUI native search is configured for local/self-hosted sources.",
        )
        SEARCH_WITH_SEARXNG: bool = Field(
            title="Search with SearXNG",
            default=False,
            description="Use SearXNG for gathering additional URLs for crawling.",
        )
        SEARXNG_BASE_URL: str = Field(
            title="SearXNG Search URL",
            default="http://searxng:8888/search?format=json&q=<query>",
            description="The full URL for your SearXNG API instance. Insert <query> where the search terms should go.",
        )
        SEARXNG_API_TOKEN: str = Field(
            title="SearXNG API Token",
            default="",
            description="The API token or Secret for your SearXNG instance.",
        )
        SEARXNG_METHOD: Literal["GET", "POST"] = Field(
            title="SearXNG HTTP Method",
            default="GET",
            description="HTTP method to use for SearXNG API calls (GET or POST).",
        )
        SEARXNG_TIMEOUT: int = Field(
            title="SearXNG Timeout",
            default=30,
            description="The timeout (in seconds) for SearXNG API requests.",
        )
        SEARXNG_MAX_RESULTS: int = Field(
            title="SearXNG Max Results",
            default=10,
            description="The maximum number of results to return from SearXNG.",
        )
        CRAWL4AI_BASE_URL: str = Field(
            title="Crawl4AI Base URL",
            default="http://crawl4ai:11235",
            description="The base URL for your Crawl4AI instance.",
        )
        CRAWL4AI_API_TOKEN: str = Field(
            title="Crawl4AI API Token",
            default="",
            description="API token for authenticating with your Crawl4AI instance. Leave empty if no authentication is required.",
        )
        CRAWL4AI_USER_AGENT: str = Field(
            title="Crawl4AI User Agent",
            default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.1.2.3 Safari/537.36",
            description="Custom User-Agent string for Crawl4AI.",
        )
        CRAWL4AI_TIMEOUT: int = Field(
            title="Crawl4AI Timeout",
            default=60,
            description="The timeout (in seconds) for Crawl4AI requests.",
        )
        CRAWL4AI_BATCH: int = Field(
            title="Crawl4AI Batch",
            default=5,
            description="The number of URLs to send to Crawl4AI per batch. If more than this number of URLs are found in total, the tool will send them to Crawl4AI in batches of this number. Useful for reducing the tokens used by the LLM per crawl.",
        )
        CRAWL4AI_MAX_URLS: int = Field(
            title="Crawl4AI Maximum URLs to crawl",
            default=20,
            description="The maximum number of URLs to crawl with Crawl4AI.",
        )
        CRAWL4AI_EXTERNAL_DOMAINS: bool = Field(
            title="Crawl External Domains",
            default=False,
            description="Allow Crawl4AI to crawl external/additional URL domains.",
        )
        CRAWL4AI_EXCLUDE_DOMAINS: str = Field(
            title="Excluded Domains",
            default="",
            description="Comma-separated list of external domains to exclude from crawling.",
        )
        CRAWL4AI_EXCLUDE_SOCIAL_MEDIA_DOMAINS: str = Field(
            title="Excluded Social Media Domains",
            default="facebook.com,twitter.com,x.com,linkedin.com,instagram.com,pinterest.com,tiktok.com,snapchat.com,reddit.com",
            description="Comma-separated list of social media domains to exclude from crawling.",
        )
        CRAWL4AI_EXCLUDE_IMAGES: Literal["None", "External", "All"] = Field(
            title="Exclude Images",
            default="External",
            description="Air-gap default excludes external images. Use All for text-only environments.",
        )
        CRAWL4AI_WORD_COUNT_THRESHOLD: int = Field(
            title="Word Count Threshold",
            default=200,
            description="The minimum word count threshold for content to be included.",
        )
        CRAWL4AI_TEXT_ONLY: bool = Field(
            title="Text Only",
            default=False,
            description="Only extract text content, excluding images and other media.",
        )
        CRAWL4AI_MAX_IMAGES: int = Field(
            title="Max Images",
            default=0,
            description="Air-gap default includes no images. Set above 0 only for local/internal media.",
        )
        CRAWL4AI_MIN_IMAGE_SCORE: int = Field(
            title="Min Image Score To Include",
            default=6,
            ge=0,
            le=10,
            description="Minimum image score from Crawl4AI to consider including in the response. Min 0, Max 10.",
        )
        CRAWL4AI_VALIDATE_IMAGES: bool = Field(
            title="Validate Image Links",
            default=False,
            description="Air-gap default: disabled to avoid external HEAD requests for images.",
        )
        CRAWL4AI_MAX_TOKENS: int = Field(
            title="Max Tokens used by web content",
            default=0,
            description="Maximum tokens to use for the web search content response. Set to 0 for unlimited.",
        )
        # Output Settings
        RESPONSE_MODE: Literal["rich", "text"] = Field(
            title="Response Mode",
            default="text",
            description="Air-gap default: plain markdown with cited sources. Rich mode is only useful with local/internal images.",
        )
        OUTPUT_MAX_CHARS: int = Field(
            title="Max Output Characters",
            default=50000,
            description="Maximum characters in the final output to prevent response crashes. Set to 0 for unlimited (not recommended).",
        )
        LLM_BASE_URL: str = Field(
            title="LLM Base URL",
            default="http://localhost:3000/api",
            description="Local OpenAI-compatible LLM base URL for Crawl4AI extraction. Air-gap default uses localhost OpenWebUI.",
        )
        LLM_API_TOKEN: str = Field(
            title="LLM API Token",
            default="",
            description="Optional API Token for your preferred OpenAI-compatible LLM.",
        )
        LLM_PROVIDER: str = Field(
            title="LLM Provider and model",
            default="openai/coder",
            description="Local Crawl4AI LLM provider/model. Air-gap default targets local OpenWebUI model coder.",
            examples=[
                "openai/coder",
                "ollama/llama3",
            ],
        )
        LLM_TEMPERATURE: float = Field(
            title="LLM Temperature",
            default=0.3,
            description="The temperature to use for the LLM.",
        )
        LLM_INSTRUCTION: str = Field(
            title="LLM Extraction Instruction",
            default="""Focus on extracting the core content. Summarize lengthy sections into concise points
            Include:
            - Key concepts and explanations
            - Important examples
            - Critical details that enhance understanding
            - Data from tables that support the main content
            - Any relevant data snippets
            Exclude:
            - Navigation elements
            - Sidebars
            - Footer content
            - Marketing or promotional material
            - Advertisements
            - User comments
            - Any other non-essential information
            Format the output as clean markdown with proper code blocks and headers.
            """,
            description="The instruction to use for the LLM when extracting from the webpage.",
        )
        LLM_MAX_TOKENS: int = Field(
            title="LLM Max Tokens",
            default=4096,
            description="The maximum number of tokens to use for the LLM.",
        )
        LLM_TOP_P: float = Field(
            title="LLM Top P",
            default=None,
            description="The top_p value to use for the LLM.",
        )
        LLM_FREQUENCY_PENALTY: float = Field(
            title="LLM Frequency Penalty",
            default=None,
            description="The frequency penalty to use for the LLM.",
        )
        LLM_PRESENCE_PENALTY: float = Field(
            title="LLM Presence Penalty",
            default=None,
            description="The presence penalty to use for the LLM.",
        )
        ALLOW_PUBLIC_NETWORK: bool = Field(
            title="Allow Public Network",
            default=False,
            description="Air-gap guard. When false, only localhost, private IPs and allowlisted internal hosts are crawled.",
        )
        ALLOWED_HOSTS: str = Field(
            title="Allowed Internal Hosts",
            default="localhost,127.0.0.1,::1,host.docker.internal,searxng,crawl4ai",
            description="Comma-separated hosts allowed when public network access is disabled. Add internal DNS names as needed.",
        )
        MORE_STATUS: bool = Field(
            title="More status updates",
            default=False,
            description="Show more status updates during local/offline search and crawl"
        )
        DEBUG: bool = Field(
            title="Debug logging",
            default=False,
            description="Enable detailed debug logging"
        )
        
        @model_validator(mode='after')
        def validate_settings(self):
            """Validate the conditional settings."""

            # Air-gap mode may crawl explicitly supplied URLs without enabling search.
            
            # SEARXNG_BASE_URL is required only when SEARCH_WITH_SEARXNG is True
            if self.SEARCH_WITH_SEARXNG and (not self.SEARXNG_BASE_URL or not self.SEARXNG_BASE_URL.strip()):
                raise ValueError(
                    "'SearXNG Search URL' is required when 'Search with SearXNG' is enabled. "
                    "Please provide the URL for your SearXNG instance."
                )
            return self

    class UserValves(BaseModel):
        """Per-user configurable options for Research Mode and crawling strategies."""
        SEARXNG_MAX_RESULTS: int = Field(
            title="SearXNG Max Results",
            default=None,
            description="The maximum number of results to return from SearXNG.",
        )
        CRAWL4AI_MAX_URLS: int = Field(
            title="Crawl4AI Maximum URLs to crawl",
            default=None,
            description="The maximum number of URLs to crawl with Crawl4AI.",
        )
        CRAWL4AI_MAX_IMAGES: int = Field(
            title="Max Images",
            default=None,
            description="Maximum number of images to include (overrides admin setting).",
        )
        RESEARCH_MODE: bool = Field(
            default=False,
            description="Enable research mode using Crawl4AI with Deep Crawling.",
        )
        RESEARCH_CRAWL_MODE: Literal[
            "pseudo_adaptive",
            "llm_guided",
            "bfs_deep",
            "research_filter"
        ] = Field(
            default="pseudo_adaptive",
            description="""The crawling strategy to use in Research Mode:
            - pseudo_adaptive: Keyword-based URL scoring and iterative crawling
            - llm_guided: Use LLM to intelligently select which links to crawl next
            - bfs_deep: Breadth-first search style deep crawling
            - research_filter: Research mode with URL filtering and relevance scoring""",
        )
        RESEARCH_KEYWORD_WEIGHT: float = Field(
            default=0.7,
            description="The keyword relevance weight when using Research mode.",
        )
        RESEARCH_MAX_DEPTH: int = Field(
            default=2,
            le=10,
            description="The maximum depth of links to follow for the Research mode. CAUTION: Too high a value may cause excessive crawling.",
        )
        RESEARCH_MAX_PAGES: int = Field(
            default=15,
            le=25,
            description="The maximum number of pages to crawl in Research mode. CAUTION: Too high a value may cause excessive crawling.",
        )
        RESEARCH_BATCH_SIZE: int = Field(
            default=5,
            description="Number of URLs to process per batch during research crawling.",
        )
        RESEARCH_LLM_LINK_SELECTION: bool = Field(
            default=True,
            description="Use LLM to select next links when in llm_guided mode.",
        )
        RESEARCH_INCLUDE_EXTERNAL: bool = Field(
            default=False,
            description="Allow following external domains during research crawling.",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.user_valves = self.UserValves()
        if self.valves.SEARCH_WITH_SEARXNG and self.valves.SEARXNG_BASE_URL:
            # Ensure SearXNG URL is properly formatted
            searxng_parsed_url = urlparse(self.valves.SEARXNG_BASE_URL)
            searxng_parsed_url_query = parse_qs(searxng_parsed_url.query)
            if "q" not in searxng_parsed_url_query:
                searxng_parsed_url_query["q"] = ["<query>"]
            if "format" in searxng_parsed_url_query:
                if searxng_parsed_url_query["format"][0] != "json":
                    searxng_parsed_url_query["format"][0] = "json"
            reconstructed_query = "&".join([f"{key}={value[0]}" for key, value in searxng_parsed_url_query.items()])
            self.valves.SEARXNG_BASE_URL = f"{searxng_parsed_url.scheme}://{searxng_parsed_url.netloc}{searxng_parsed_url.path}?{reconstructed_query}"
        
        # Define tools for better LLM integration
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_and_crawl",
                    "description": "Search the web and crawl the resulting pages to extract detailed content with images and videos. Use this for current events, news, research, or any information that needs web search and detailed content extraction. The user can optionally provide specific URLs to include in the crawl. When research_mode is enabled, multiple crawling strategies are available including pseudo-adaptive keyword scoring, LLM-guided link selection, BFS deep crawling, and research filtering.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query (e.g., 'latest AI developments', 'Python tutorial')",
                            },
                            "urls": {
                                "type": "array",
                                "description": "Optional list of specific URLs to crawl in addition to search results",
                                "items": {"type": "string"},
                                "default": [],
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of search results to crawl (default uses valve setting)",
                                "default": None,
                            },
                            "research_mode": {
                                "type": "boolean",
                                "description": "Enables Research Mode which performs deeper web crawling using advanced strategies. When enabled, the LLM can also specify a research_crawl_mode parameter to choose the crawling strategy.",
                                "default": False,
                            },
                            "research_crawl_mode": {
                                "type": "string",
                                "description": "Optional crawling strategy for research mode: pseudo_adaptive (keyword-based scoring), llm_guided (LLM selects links), bfs_deep (breadth-first), research_filter (URL filtering). Only used when research_mode is true.",
                                "default": None,
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
        ]
            
        self.crawl_counter = 0
        self.content_counter = 0
        self._debug_log = []  # Collect debug messages for response
        self._seen_images = set()  # Track unique images to avoid duplicates
        logger.info("Web Search and Crawl tool initialized")
        self.total_urls = 0


    def _allowed_hostnames(self) -> set[str]:
        return {h.strip().lower() for h in self.valves.ALLOWED_HOSTS.split(",") if h.strip()}

    def _is_offline_allowed_url(self, url: str) -> bool:
        if self.valves.ALLOW_PUBLIC_NETWORK:
            return True
        try:
            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            if not host:
                return False
            if host in self._allowed_hostnames():
                return True
            try:
                ip = ipaddress.ip_address(host.strip("[]"))
                return ip.is_private or ip.is_loopback or ip.is_link_local
            except ValueError:
                return False
        except Exception:
            return False

    def _filter_offline_allowed_urls(self, urls: List[str]) -> List[str]:
        allowed = []
        for url in urls:
            if self._is_offline_allowed_url(url):
                allowed.append(url)
            else:
                self._log_debug(f"Blocked non-air-gap URL: {url}")
        return allowed

    def _log_debug(self, message: str):
        """Log debug message and collect for response when DEBUG is enabled."""
        if self.valves.DEBUG:
            logger.info(f"[DEBUG] {message}")
            self._debug_log.append(message)

    def _clear_debug_log(self):
        """Clear debug log and seen images for new request."""
        self._debug_log = []
        self._seen_images = set()

    def _create_image_gallery_html(self, images: list, query: str) -> str:
        """Create an HTML image gallery for Rich UI embedding."""
        # Escape query for safe HTML embedding
        safe_query = query.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        image_items = ""
        for idx, img_url in enumerate(images[:12], 1):  # Limit to 12 images
            # Air-gap build: no public image proxy; use the original local/internal URL.
            thumb_url = img_url
            safe_url = img_url.replace('"', '&quot;')
            image_items += f'''
                <div class="img-card" onclick="window.open('{safe_url}', '_blank')">
                    <img src="{thumb_url}" alt="Image {idx}" loading="lazy" onerror="this.style.display='none'"/>
                    <div class="img-overlay">
                        <span class="img-num">{idx}</span>
                    </div>
                </div>'''
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: transparent;
            padding: 12px;
            color: #e5e7eb;
        }}
        .header {{
            margin-bottom: 10px;
            padding-bottom: 6px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .header h2 {{
            font-size: 0.9em;
            font-weight: 600;
            color: #f3f4f6;
        }}
        .header .query {{
            font-size: 0.8em;
            color: #9ca3af;
            margin-top: 2px;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 8px;
        }}
        .img-card {{
            position: relative;
            aspect-ratio: 1;
            border-radius: 6px;
            overflow: hidden;
            cursor: pointer;
            background: rgba(255,255,255,0.05);
            transition: transform 0.2s, opacity 0.2s;
        }}
        .img-card:hover {{
            transform: scale(1.05);
            opacity: 0.9;
        }}
        .img-card img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .img-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 2px 6px;
            background: linear-gradient(transparent, rgba(0,0,0,0.5));
            color: #fff;
        }}
        .img-num {{
            font-size: 0.7em;
            font-weight: 600;
        }}
        .footer {{
            margin-top: 8px;
            font-size: 0.7em;
            color: #6b7280;
            text-align: center;
        }}
        @media (prefers-color-scheme: light) {{
            body {{ color: #374151; }}
            .header {{ border-bottom-color: rgba(0,0,0,0.1); }}
            .header h2 {{ color: #111827; }}
            .header .query {{ color: #6b7280; }}
            .img-card {{ background: rgba(0,0,0,0.05); }}
            .footer {{ color: #9ca3af; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Images Found</h2>
        <div class="query">{safe_query}</div>
    </div>
    <div class="gallery">
        {image_items}
    </div>
    <div class="footer">Click to open full size</div>
    <script>
        function reportHeight() {{
            const h = document.documentElement.scrollHeight;
            parent.postMessage({{ type: 'iframe:height', height: h }}, '*');
        }}
        window.addEventListener('load', reportHeight);
        new ResizeObserver(reportHeight).observe(document.body);
    </script>
</body>
</html>'''
        return html

    async def _count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text using tiktoken if available, otherwise estimate."""
        if not TIKTOKEN_AVAILABLE:
            # Fallback: estimate ~4 characters per token (conservative estimate)
            return len(text) // 4
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


    async def _truncate_content(self, content: str, max_tokens: int, model: str = "gpt-4") -> str:
        """Truncate content to fit within max_tokens."""
        if not TIKTOKEN_AVAILABLE:
            # Fallback: estimate ~4 characters per token
            max_chars = max_tokens * 4
            if len(content) <= max_chars:
                return content
            return content[:max_chars] + "\n\n[Content truncated due to length...]"
        
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        tokens = encoding.encode(content)
        if len(tokens) <= max_tokens:
            return content
        
        # Truncate and add indicator
        truncated_tokens = tokens[:max_tokens]
        truncated_text = encoding.decode(truncated_tokens)
        return truncated_text + "\n\n[Content truncated due to length...]"

    def _format_output(self, crawl_results: list, query: str, sources: list = None, images: list = None) -> str:
        """
        Format crawl results into clean markdown with cited sources.
        
        Args:
            crawl_results: List of content items from crawling
            query: The original search query
            sources: Optional list of source URLs
            images: Optional list of unique image URLs
            
        Returns:
            Formatted markdown string with citations
        """
        max_chars = self.valves.OUTPUT_MAX_CHARS
        
        if not crawl_results:
            result = f"No content found for query: {query}"
            if self._debug_log and self.valves.DEBUG:
                result += "\n\n---\n## Debug Log\n" + "\n".join(f"- {log}" for log in self._debug_log[-50:])
            return result
        
        sections = []
        sections.append(f"## Web Search Results: {query}\n")
        
        for idx, item in enumerate(crawl_results, 1):
            if isinstance(item, dict):
                topic = item.get("topic", "")
                summary = item.get("summary", "")
                url = item.get("url", "")
                
                # Include source ID [idx] for LLM to cite
                if topic:
                    sections.append(f"### [{idx}] {topic}\n")
                elif url:
                    sections.append(f"### [{idx}] {url}\n")
                else:
                    sections.append(f"### [{idx}] Content\n")
                
                if url:
                    sections.append(f"**Source:** {url}\n")
                
                if summary:
                    sections.append(f"{summary}\n")
                
                if idx < len(crawl_results):
                    sections.append("---\n")
                    
            elif isinstance(item, str):
                sections.append(f"### [{idx}] Content\n")
                sections.append(f"{item}\n")
                if idx < len(crawl_results):
                    sections.append("---\n")
        
        # Add sources section with IDs
        if sources:
            sections.append("\n---\n## Sources\n")
            sections.append("*Use [id] to cite these sources in your response.*\n")
            for idx, src in enumerate(sources[:20], 1):
                sections.append(f"[{idx}] {src}")
        
        # Add images section if provided (text mode only)
        if images:
            sections.append("\n---\n## Images Found\n")
            sections.append("*Include relevant images using markdown: `![description](url)`*\n")
            for idx, img_url in enumerate(images[:10], 1):
                sections.append(f"[Image {idx}] {img_url}")
        
        # Add debug log if enabled
        if self._debug_log and self.valves.DEBUG:
            sections.append("\n---\n## Debug Log\n")
            sections.append("```")
            for log in self._debug_log[-50:]:
                sections.append(log)
            sections.append("```")
        
        output = "\n".join(sections)
        
        # Apply character limit if set
        if max_chars > 0 and len(output) > max_chars:
            output = output[:max_chars]
            last_para = output.rfind("\n\n")
            last_sentence = output.rfind(". ")
            
            if last_para > max_chars * 0.8:
                output = output[:last_para]
            elif last_sentence > max_chars * 0.8:
                output = output[:last_sentence + 1]
            
            output += "\n\n---\n*[Output truncated]*"
        
        return output


    async def _validate_image_url(self, url: str) -> bool:
        """
        Validate if an image URL is accessible and returns an image.
        Returns True if valid, False otherwise.
        
        Note: Skip validation for proxy services like weserv.nl as they handle broken images.
        """
        try:
            if not self.valves.CRAWL4AI_VALIDATE_IMAGES:
                return True
            
            url = url.strip()
            
            if not self._is_offline_allowed_url(url):
                return False
            
            # Skip data URIs
            if url.startswith('data:'):
                return True
            
            timeout = aiohttp.ClientTimeout(total=3)  # Reduced timeout
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            async with aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                skip_auto_headers={'Accept-Encoding', 'Content-Type'}
            ) as session:
                async with session.head(url, allow_redirects=True) as response:
                    # Check if status is OK
                    if response.status != 200:
                        self._log_debug(f"Image validation failed for {url}: Status {response.status}")
                        return False
                    
                    # Check if content-type is an image
                    content_type = response.headers.get('Content-Type', '').lower()
                    if not content_type.startswith('image/'):
                        self._log_debug(f"Image validation failed for {url}: Content-Type {content_type}")
                        return False
                    
                    return True
        except asyncio.TimeoutError:
            self._log_debug(f"Image validation timeout for {url}")
            return False
        except Exception as e:
            self._log_debug(f"Image validation error for {url}: {str(e)}")
            return False
    
    async def _validate_images_batch(self, urls: List[str]) -> List[str]:
        """
        Validate multiple image URLs concurrently.
        Returns list of valid URLs only.
        """
        tasks = [self._validate_image_url(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        valid_urls = [url for url, is_valid in zip(urls, results) if is_valid]
        
        if len(valid_urls) < len(urls):
            if self.valves.DEBUG:
                logger.info(f"Image validation: {len(valid_urls)}/{len(urls)} images are valid")
        
        return valid_urls


    async def get_request(self) -> "Request":
        """Helper to create a request object for native search."""
        if not NATIVE_SEARCH_AVAILABLE:
            raise ImportError("OpenWebUI native search not available")
        return Request(scope={"type": "http", "app": app})

    async def _search_native(
        self,
        query: str,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: Optional[dict] = None
    ) -> List[str]:
        """Search using OpenWebUI's native web search and return URLs."""

        if not self.valves.USE_NATIVE_SEARCH:
            self._log_debug("Native search is disabled.")
            return []

        if not NATIVE_SEARCH_AVAILABLE:
            logger.warning("Native search not available - missing OpenWebUI imports")
            return []

        if __user__ is None:
            logger.error("User information required for native search")
            return []

        try:
            # v0.9.5: get_user_by_id is now async
            user = await Users.get_user_by_id(__user__["id"])
            if user is None:
                logger.error("User not found")
                return []

            if __event_emitter__ and self.valves.MORE_STATUS:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Searching using Open WebUI native search...", "done": False},
                    }
                )

            # Use native search - SearchForm expects a list of queries
            form = SearchForm.model_validate({"queries": [query]})
            result = await process_web_search(
                request=Request(scope={"type": "http", "app": app}), form_data=form, user=user
            )
            self._log_debug(f"Native search for '{query}' returned {result}")

            # Extract URLs from result items - v0.9.5 returns items with 'link' field
            urls = []
            items = result.get("items", [])
            for item in items:
                # Handle both dict and object formats
                if isinstance(item, dict):
                    link = item.get("link")
                elif hasattr(item, "link"):
                    link = item.link
                else:
                    continue
                if link:
                    urls.append(link)

            self._log_debug(f"Native search for '{query}' returned {len(urls)} URLs")

            if __event_emitter__ and self.valves.MORE_STATUS:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"Found {len(urls)} websites...", "done": False},
                    }
                )

            return urls

        except Exception as e:
            logger.error(f"Error in native search: {str(e)}")
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"Native search encountered an error: {str(e)}", "done": False},
                    }
                )
            return []
    
    async def _search_searxng(self,
        query: str,
        __event_emitter__: Callable[[dict], Any] = None
    ) -> List[str]:
        """Search SearXNG and return a list of URLs."""

        if not self.valves.SEARCH_WITH_SEARXNG:
            self._log_debug("SearXNG search is disabled.")
            return []

        if not self.valves.SEARXNG_BASE_URL:
            logger.error("SearXNG base URL is not configured.")
            return []

        # Use the pre-formatted URL
        url = self.valves.SEARXNG_BASE_URL.replace("<query>", quote(query))
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Add token if configured
        if self.valves.SEARXNG_API_TOKEN:
            headers["Authorization"] = f"Bearer {self.valves.SEARXNG_API_TOKEN}"

        if __event_emitter__ and self.valves.MORE_STATUS:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Searching using SearXNG...", "done": False},
                }
            )
        
        try:
            if self.valves.SEARXNG_METHOD == "POST":
                response = requests.post(
                    url,
                    data={"q": query, "format": "json"},
                    headers=headers,
                    timeout=self.valves.SEARXNG_TIMEOUT
                )
            else:  # GET
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.valves.SEARXNG_TIMEOUT
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract URLs from results
            results = data.get("results", [])
            urls = []
            max_results = self.user_valves.SEARXNG_MAX_RESULTS or self.valves.SEARXNG_MAX_RESULTS
            for result in results[:max_results]:
                if result.get("url"):
                    urls.append(result["url"])
            
            if self.valves.DEBUG:
                logger.info(f"SearXNG search for '{query}' returned {len(urls)} URLs")
            
            if __event_emitter__ and self.valves.MORE_STATUS:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"Found {len(urls)} results...", "done": False},
                    }
                )
            
            return urls
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching SearXNG: {str(e)}")
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"SearXNG search error: {str(e)}", "done": False},
                    }
                )
            return []
        except Exception as e:
            logger.error(f"Unexpected error in SearXNG search: {str(e)}")
            return []

    async def search_and_crawl(
        self, 
        query: str,
        urls: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        max_images: Optional[int] = None,
        research_mode: Optional[bool] = False,
        research_crawl_mode: Optional[str] = None,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: Optional[dict] = None
    ) -> Union[str, tuple]:
        """
        USE THIS TOOL whenever the user asks to 'search' for, 'lookup', 'find' information,
        'browse' the web, 'gather' data on a specific topic, or when any information or data 
        is needed from configured local or internal sources to respond to the user.
        This tool performs local/self-hosted searches using Native Search and/or SearXNG to gather relevant URLs,
        then crawls those URLs using Crawl4AI to extract clean content with media.
        
        :param query: The search query to use.
        :param urls: Optional list of URLs to crawl in addition to those found from searching.
        :param max_results: The maximum number of search results to crawl (per search).
        :param max_images: The maximum number of images results to display in the chat window.
        :param research_mode: Enables Research Mode for deeper web crawling with advanced strategies.
        :param research_crawl_mode: Optional crawling strategy for research mode:
            - pseudo_adaptive: Keyword-based URL scoring and iterative crawling
            - llm_guided: Use LLM to intelligently select which links to crawl next
            - bfs_deep: Breadth-first search style deep crawling
            - research_filter: Research mode with URL filtering and relevance scoring
        """
        logger.info(f"Starting search and crawl for '{query}'")

        # Clear state for new request
        self._clear_debug_log()
        gathered_urls = []
        all_sources = []
        all_unique_images = []
        self.crawl_counter = 0
        self.content_counter = 0
        self.total_urls = 0
        
        self._log_debug(f"Query: {query}")
        self._log_debug(f"Research mode: {research_mode}, Mode: {research_crawl_mode}")
        
        if not max_images:
            max_images = self.user_valves.CRAWL4AI_MAX_IMAGES if self.user_valves.CRAWL4AI_MAX_IMAGES is not None else self.valves.CRAWL4AI_MAX_IMAGES
        
        # Add any user-provided URLs first
        if urls:
            for url in urls:
                # Ensure URL starts with http; default to local-friendly http for hostnames without scheme.
                if not url.startswith("http"):
                    url = f"http://{url}"
                if self._is_offline_allowed_url(url) and url not in gathered_urls:
                    gathered_urls.append(url)
                elif not self._is_offline_allowed_url(url):
                    self._log_debug(f"Blocked non-air-gap URL: {url}")
        
        if __event_emitter__ and str(self.valves.INITIAL_RESPONSE).strip() != "":
            await __event_emitter__(
                {
                    "type": "chat:message:delta",
                    "data": {
                        "content": str(self.valves.INITIAL_RESPONSE).strip()
                    },
                }
            )
        
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": f"Searching for '{query}'...", "done": False},
                }
            )
        # Search with Native Search if enabled
        if self.valves.USE_NATIVE_SEARCH:
            native_urls = await self._search_native(query, __event_emitter__, __user__)
            for url in native_urls:
                if url not in gathered_urls:
                    gathered_urls.append(url)
        
        # Search with SearXNG if enabled
        if self.valves.SEARCH_WITH_SEARXNG:
            searxng_urls = await self._search_searxng(query, __event_emitter__)
            # Apply max_results limit for SearXNG
            max_results = self.user_valves.SEARXNG_MAX_RESULTS or max_results or self.valves.SEARXNG_MAX_RESULTS
            for url in searxng_urls[:max_results]:
                if url not in gathered_urls:
                    gathered_urls.append(url)
        
        gathered_urls = self._filter_offline_allowed_urls(gathered_urls)

        # Check if we have URLs to crawl
        if not gathered_urls:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"Nothing found for query '{query}'.", "done": True},
                    }
                )
            if self.valves.DEBUG:
                logger.info(f"No URLs gathered to crawl for query '{query}'.")
            return f"No URLs found to crawl for the query: {query}."
        
        max_urls = self.user_valves.CRAWL4AI_MAX_URLS or self.valves.CRAWL4AI_MAX_URLS
        if len(gathered_urls) > max_urls:
            # max_urls = max_results or max_urls
            gathered_urls = gathered_urls[:max_urls]
            
            
        # Emit status
        if __event_emitter__ and self.valves.MORE_STATUS:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Found {len(gathered_urls)} results. Inspecting the content...",
                        "done": False,
                    },
                }
            )
        
        # Determine the crawl mode - priority: 1) LLM input, 2) UserValves, 3) Default
        effective_research_mode = research_mode or self.user_valves.RESEARCH_MODE
        effective_crawl_mode = research_crawl_mode or self.user_valves.RESEARCH_CRAWL_MODE
        
        # Now crawl all gathered URLs
        crawl_results = []
        batch_count = 1
        image_list = []
        video_list = []
        seen_images = set()
        seen_videos = set()
        total_tokens = 0
        self.total_urls = len(gathered_urls)
        
        # Handle research mode with the selected crawling strategy
        if effective_research_mode and len(gathered_urls) > 0:
            if __event_emitter__ and self.valves.MORE_STATUS:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"Research Mode enabled. Using '{effective_crawl_mode}' strategy...", "done": False},
                })
            
            # Use the selected research crawling strategy
            research_result = await self._research_crawl(
                urls=gathered_urls,
                query=query,
                mode=effective_crawl_mode,
                __event_emitter__=__event_emitter__
            )
            
            # Merge research results
            if "content" in research_result:
                crawl_results.extend(research_result["content"])
            if "images" in research_result:
                image_list.extend(research_result["images"])
            if "videos" in research_result:
                video_list.extend(research_result["videos"])
        else:
            # Standard batch crawling
            for i in range(0, len(gathered_urls), self.valves.CRAWL4AI_BATCH):
                batch = gathered_urls[i:i + self.valves.CRAWL4AI_BATCH]
                batch_count += 1
                try:
                    crawled_batch = await self._crawl_url(
                        urls=batch,
                        query=query,
                        __event_emitter__=__event_emitter__
                    )
                    
                    if self.valves.DEBUG:
                        logger.info(f"Found {len(crawled_batch.get('content',[]))} content, {len(crawled_batch.get('images',[]))} images, {len(crawled_batch.get('videos',[]))} videos.")
                    
                    # Compile images
                    if crawled_batch.get("images",[]):
                        
                        for img_url in crawled_batch.get("images",[]):
                            parsed_image = urlparse(img_url)
                            base_image_url = f"{parsed_image.scheme}://{parsed_image.netloc}{parsed_image.path}"
                            if base_image_url in seen_images:
                                # Don't display duplicates!
                                continue
                            else:
                                seen_images.add(base_image_url)
                                image_valid = True
                                if self.valves.CRAWL4AI_VALIDATE_IMAGES:
                                    image_valid = await self._validate_image_url(img_url)
                                if image_valid and self._is_offline_allowed_url(img_url):
                                    # Add if valid and local/internal according to Air-Gap guard
                                    image_list.append(img_url)
                                    
                    # Compile videos
                    if crawled_batch.get("videos",[]):
                        
                        for vid_url in crawled_batch.get("videos",[]):
                            parsed_video = urlparse(vid_url)
                            base_video_url = f"{parsed_video.scheme}://{parsed_video.netloc}{parsed_video.path}"
                            if base_video_url in seen_videos:
                                # Don't display duplicates!
                                continue
                            else:
                                seen_videos.add(base_video_url)
                                video_list.append(vid_url)
                                
                    
                    # Process content, making sure not to exceed the total token count
                    data_list = crawled_batch.get("content",[])
                    content_list = crawled_batch.get("content",[])
                    content_str = orjson.dumps(content_list).decode('utf-8')
                    page_tokens = await self._count_tokens(content_str)

                    # Check if we need to truncate this page's content
                    if self.valves.CRAWL4AI_MAX_TOKENS > 0 and page_tokens > self.valves.CRAWL4AI_MAX_TOKENS:
                        content_str = await self._truncate_content(content_str, self.valves.CRAWL4AI_MAX_TOKENS)
                        # Re-parse the truncated content
                        try:
                            content_list = orjson.loads(content_str.replace("\n\n[Content truncated due to length...]", ""))
                        except:
                            # If parsing fails, use original but truncated
                            pass
                        page_tokens = self.valves.CRAWL4AI_MAX_TOKENS
                        if self.valves.DEBUG:
                            logger.info(f"Truncated content from {url} to {self.valves.CRAWL4AI_MAX_TOKENS} tokens")
                    
                        # Check if adding this page would exceed total limit
                        if total_tokens + page_tokens > self.valves.CRAWL4AI_MAX_TOKENS:
                            logger.warning(f"Reached token limit ({self.valves.CRAWL4AI_MAX_TOKENS}). Skipping remaining pages of content.")
                            if __event_emitter__ and self.valves.MORE_STATUS:
                                await __event_emitter__(
                                    {
                                        "type": "status",
                                        "data": {"description": f"Token limit reached. Processed {len(content_list)} of {len(data_list)} pages.", "done": False},
                                    }
                                )
                            continue
                    
                    total_tokens += page_tokens
                    self._log_debug(f"Page {url}: {page_tokens} tokens (Total: {total_tokens}/{self.valves.CRAWL4AI_MAX_TOKENS if self.valves.CRAWL4AI_MAX_TOKENS > 0 else 'unlimited'})")
                    crawl_results.extend(content_list)
                    all_sources.append(url)
                    
                except Exception as e:
                    error_message = f"An unexpected error occurred: {str(e)}\n{traceback.format_exc()}"
                    logger.error(error_message)
                    self._log_debug(f"Error crawling {url}: {str(e)}")
        
        # Deduplicate images - limit to 1 image per domain to avoid clutter
        def get_image_domain(url: str) -> str:
            """Extract domain from image URL for per-domain limiting."""
            try:
                parsed = urlparse(url)
                return parsed.netloc.lower()
            except Exception:
                return url
        
        seen_domains = set()
        for img in image_list:
            domain = get_image_domain(img)
            if domain not in seen_domains and img not in self._seen_images:
                seen_domains.add(domain)
                self._seen_images.add(img)
                all_unique_images.append(img)
        
        self._log_debug(f"Total unique images: {len(all_unique_images)} (from {len(image_list)} raw, {len(seen_domains)} domains)")
        self._log_debug(f"Total sources: {len(all_sources)}")
        
        # Limit images based on valve setting
        max_images = self.user_valves.CRAWL4AI_MAX_IMAGES if self.user_valves.CRAWL4AI_MAX_IMAGES is not None else self.valves.CRAWL4AI_MAX_IMAGES
        if max_images > 0:
            all_unique_images = all_unique_images[:max_images]
        
        # Return based on RESPONSE_MODE valve
        if self.valves.RESPONSE_MODE == "rich" and all_unique_images and HTMLRESPONSE_AVAILABLE:
            # Rich UI mode: Return HTML gallery with text context for LLM
            try:
                gallery_html = self._create_image_gallery_html(all_unique_images, query)
                
                # Format text output WITH image URLs so LLM can reference them
                text_output = self._format_output(crawl_results, query, sources=all_sources, images=all_unique_images)
                
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": f"Found {len(crawl_results)} items, {len(all_unique_images)} images from {len(all_sources)} pages.", "done": True},
                        }
                    )
                
                self._log_debug(f"Returning HTMLResponse with {len(all_unique_images)} images in gallery")
                
                # Return tuple: HTMLResponse renders the gallery, text_output gives LLM the content + image URLs
                headers = {"Content-Disposition": "inline"}
                return HTMLResponse(content=gallery_html, headers=headers), text_output
                
            except Exception as e:
                self._log_debug(f"Rich UI gallery failed, falling back to text: {str(e)}")
                # Fall through to text output
        
        # Text mode: Return plain markdown with citations
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": f"Found {len(crawl_results)} items from {len(all_sources)} pages.", "done": True},
                }
            )
        
        self._log_debug(f"Final crawl results: {len(crawl_results)} items")
        
        return self._format_output(crawl_results, query, sources=all_sources, images=all_unique_images if not self.valves.CRAWL4AI_TEXT_ONLY else None)


    async def _research_crawl(
        self,
        urls: List[str],
        query: str,
        mode: str = "pseudo_adaptive",
        __event_emitter__: Callable[[dict], Any] = None
    ) -> dict:
        """
        Route to the appropriate research crawling strategy.
        
        :param urls: List of starting URLs
        :param query: The search query for relevance scoring
        :param mode: The crawling strategy to use
        :returns: Dictionary with content, images, videos
        """
        if mode == ResearchCrawlMode.PSEUDO_ADAPTIVE:
            return await self._pseudo_adaptive_crawl(urls, query, __event_emitter__)
        elif mode == ResearchCrawlMode.LLM_GUIDED:
            return await self._llm_guided_crawl(urls, query, __event_emitter__)
        elif mode == ResearchCrawlMode.BFS_DEEP:
            return await self._bfs_deep_crawl(urls, query, __event_emitter__)
        elif mode == ResearchCrawlMode.RESEARCH_FILTER:
            return await self._research_filter_crawl(urls, query, __event_emitter__)
        else:
            # Default to pseudo_adaptive for unknown modes
            logger.warning(f"Unknown research crawl mode: {mode}, defaulting to pseudo_adaptive")
            return await self._pseudo_adaptive_crawl(urls, query, __event_emitter__)


    async def _pseudo_adaptive_crawl(
        self,
        start_urls: List[str],
        query: str,
        __event_emitter__: Callable[[dict], Any] = None
    ) -> dict:
        """
        Implement a simplified adaptive-like crawling using:
        1. Initial crawl to discover links
        2. Keyword-based filtering of discovered links
        3. Iterative crawling with priority scoring
        """
        from collections import deque
        from urllib.parse import urlparse, urljoin
        
        max_pages = self.user_valves.RESEARCH_MAX_PAGES
        max_depth = self.user_valves.RESEARCH_MAX_DEPTH
        batch_size = self.user_valves.RESEARCH_BATCH_SIZE
        include_external = self.user_valves.RESEARCH_INCLUDE_EXTERNAL
        
        keywords = query.lower().split()
        
        # Track crawled pages and discovered links
        crawled_pages = set()
        crawled_results = []
        all_images = []
        all_videos = []
        
        # Queue of (url, depth, initial_score)
        queue = deque()
        
        # Add initial URLs with base score
        for url in start_urls[:5]:  # Limit starting URLs
            if url not in crawled_pages:
                score = sum(1 for kw in keywords if kw in url.lower())
                queue.append((url, 0, score))
        
        self.total_urls = max_pages
        
        while queue and len(crawled_pages) < max_pages:
            # Get batch of URLs to process
            batch = []
            for _ in range(min(batch_size, len(queue))):
                if queue:
                    batch.append(queue.popleft())
            
            # Sort batch by score (highest first)
            batch.sort(key=lambda x: x[2], reverse=True)
            
            for url, depth, score in batch:
                if len(crawled_pages) >= max_pages or depth > max_depth:
                    continue
                
                if url in crawled_pages:
                    continue
                
                crawled_pages.add(url)
                
                if __event_emitter__ and self.valves.MORE_STATUS:
                    await __event_emitter__({
                        "type": "status",
                        "data": {"description": f"[Pseudo-Adaptive] Depth {depth}: Crawling {url[:60]}... ({len(crawled_pages)}/{max_pages})", "done": False},
                    })
                
                # Crawl the page with link extraction
                result = await self._crawl_url(urls=[url], query=query, extract_links=True, __event_emitter__=__event_emitter__)
                
                if result.get("content"):
                    crawled_results.extend(result["content"])
                
                if result.get("images"):
                    all_images.extend(result["images"])
                
                if result.get("videos"):
                    all_videos.extend(result["videos"])
                
                # If we haven't reached max depth, discover and score new links
                if depth < max_depth:
                    discovered_links = result.get("links", [])
                    
                    for link in discovered_links:
                        if link in crawled_pages:
                            continue
                        
                        parsed_link = urlparse(link)
                        parsed_url = urlparse(url)
                        
                        # Check domain restrictions
                        if not include_external:
                            if parsed_link.netloc and parsed_link.netloc != parsed_url.netloc:
                                continue
                        
                        # Score the link
                        link_lower = link.lower()
                        link_score = sum(1 for kw in keywords if kw in link_lower)
                        
                        if link_score > 0:  # Only follow relevant links
                            queue.append((link, depth + 1, link_score))
        
        if self.valves.DEBUG:
            logger.info(f"[Pseudo-Adaptive] Crawled {len(crawled_pages)} pages")
        
        return {
            "content": crawled_results,
            "images": all_images,
            "videos": all_videos,
            "pages_crawled": len(crawled_pages)
        }


    async def _llm_guided_crawl(
        self,
        start_urls: List[str],
        query: str,
        __event_emitter__: Callable[[dict], Any] = None
    ) -> dict:
        """
        Use LLM to intelligently select which links to crawl next.
        This provides a form of "intelligent" crawling via the API.
        """
        from urllib.parse import urlparse
        
        max_pages = self.user_valves.RESEARCH_MAX_PAGES
        use_llm_selection = self.user_valves.RESEARCH_LLM_LINK_SELECTION
        include_external = self.user_valves.RESEARCH_INCLUDE_EXTERNAL
        
        crawled_pages = set()
        crawled_results = []
        all_images = []
        all_videos = []
        
        # Configure LLM for link evaluation
        llm_config = LLMConfig(
            provider=self.valves.LLM_PROVIDER,
            base_url=self.valves.LLM_BASE_URL,
            temperature=0.3,
            max_tokens=500,
        )
        if self.valves.LLM_API_TOKEN:
            llm_config.api_token = self.valves.LLM_API_TOKEN
        
        # Process starting URLs
        urls_to_process = list(start_urls[:5])
        
        while urls_to_process and len(crawled_pages) < max_pages:
            current_url = urls_to_process.pop(0)
            
            if current_url in crawled_pages:
                continue
            
            crawled_pages.add(current_url)
            
            if __event_emitter__ and self.valves.MORE_STATUS:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"[LLM-Guided] Crawling {current_url[:60]}... ({len(crawled_pages)}/{max_pages})", "done": False},
                })
            
            # Crawl page with link extraction
            result = await self._crawl_url(urls=[current_url], query=query, extract_links=True, __event_emitter__=__event_emitter__)
            
            if result.get("content"):
                crawled_results.extend(result["content"])
            
            if result.get("images"):
                all_images.extend(result["images"])
            
            if result.get("videos"):
                all_videos.extend(result["videos"])
            
            # Get discovered links
            discovered_links = result.get("links", [])[:15]
            
            if not discovered_links:
                continue
            
            # Filter links by domain
            if not include_external:
                parsed_current = urlparse(current_url)
                filtered_links = []
                for link in discovered_links:
                    parsed_link = urlparse(link)
                    if not parsed_link.netloc or parsed_link.netloc == parsed_current.netloc:
                        filtered_links.append(link)
                discovered_links = filtered_links
            
            if not discovered_links:
                continue
            
            if use_llm_selection:
                # Use LLM to select next links
                link_selection_prompt = f"""Given the research query: "{query}"

These links were discovered from the current page:
{chr(10).join([f"{i+1}. {link}" for i, link in enumerate(discovered_links[:10])])}

Select the 3 most relevant links to explore next that would best help answer the research query.
Return only the link numbers (e.g., "1, 3, 5"), nothing else."""

                try:
                    extraction_strategy = LLMExtractionStrategy(
                        llm_config=llm_config,
                        instruction=link_selection_prompt,
                        input_format="text",
                        schema={"type": "string"},
                    )
                    crawler_config = CrawlerRunConfig(
                        extraction_strategy=extraction_strategy,
                        cache_mode=CacheMode.BYPASS,
                        page_timeout=30000,
                    )
                    # Make API call for LLM-based link selection
                    # For now, we'll fall back to keyword scoring if this fails
                    selected_indices = []
                    try:
                        # This would require a separate API call - simplify for now
                        pass
                    except:
                        pass
                except Exception as e:
                    logger.warning(f"LLM link selection failed: {e}")

            # Fallback:            # Fallback: Add high-scoring links based on keyword relevance
            keywords = query.lower().split()
            scored_links = []
            for link in discovered_links:
                if link in crawled_pages or link in urls_to_process:
                    continue
                link_lower = link.lower()
                score = sum(1 for kw in keywords if kw in link_lower)
                if score > 0:
                    scored_links.append((link, score))
            
            scored_links.sort(key=lambda x: x[1], reverse=True)
            
            # Add top links to processing queue
            for link, score in scored_links[:3]:
                if link not in urls_to_process and link not in crawled_pages:
                    urls_to_process.append(link)
        
        if self.valves.DEBUG:
            logger.info(f"[LLM-Guided] Crawled {len(crawled_pages)} pages")
        
        return {
            "content": crawled_results,
            "images": all_images,
            "videos": all_videos,
            "pages_crawled": len(crawled_pages)
        }


    async def _bfs_deep_crawl(
        self,
        start_urls: List[str],
        query: str,
        __event_emitter__: Callable[[dict], Any] = None
    ) -> dict:
        """
        Breadth-first deep crawling using the API.
        Crawls level by level, respecting domain boundaries.
        """
        from collections import deque
        from urllib.parse import urlparse
        
        max_pages = self.user_valves.RESEARCH_MAX_PAGES
        max_depth = self.user_valves.RESEARCH_MAX_DEPTH
        batch_size = self.user_valves.RESEARCH_BATCH_SIZE
        include_external = self.user_valves.RESEARCH_INCLUDE_EXTERNAL
        
        crawled_pages = set()
        crawled_results = []
        all_images = []
        all_videos = []
        
        # Get base domain from first URL
        if start_urls:
            parsed_start = urlparse(start_urls[0])
            base_domain = parsed_start.netloc
        else:
            base_domain = ""
        
        # Queue: (url, depth)
        queue = deque()
        
        # Add starting URLs
        for url in start_urls[:5]:
            if url not in crawled_pages:
                queue.append((url, 0))
        
        self.total_urls = max_pages
        
        while queue and len(crawled_pages) < max_pages:
            # Process level by level
            level_size = min(batch_size, len(queue))
            
            level_batch = []
            for _ in range(level_size):
                if queue:
                    level_batch.append(queue.popleft())
            
            for url, depth in level_batch:
                if len(crawled_pages) >= max_pages:
                    break
                
                if url in crawled_pages:
                    continue
                
                if depth > max_depth:
                    continue
                
                crawled_pages.add(url)
                
                if __event_emitter__ and self.valves.MORE_STATUS:
                    await __event_emitter__({
                        "type": "status",
                        "data": {"description": f"[BFS-Deep] Depth {depth}: Crawling {url[:60]}... ({len(crawled_pages)}/{max_pages})", "done": False},
                    })
                
                # Crawl page with link extraction
                result = await self._crawl_url(urls=[url], query=query, extract_links=True, __event_emitter__=__event_emitter__)
                
                if result.get("content"):
                    crawled_results.extend(result["content"])
                
                if result.get("images"):
                    all_images.extend(result["images"])
                
                if result.get("videos"):
                    all_videos.extend(result["videos"])
                
                # Add discovered links to queue (if within depth limit)
                if depth < max_depth:
                    discovered_links = result.get("links", [])
                    
                    for link in discovered_links[:10]:  # Limit new links per page
                        if link in crawled_pages:
                            continue
                        
                        parsed_link = urlparse(link)
                        
                        # Domain check
                        if not include_external:
                            if parsed_link.netloc and parsed_link.netloc != base_domain:
                                continue
                        
                        if link not in queue:
                            queue.append((link, depth + 1))
        
        if self.valves.DEBUG:
            logger.info(f"[BFS-Deep] Crawled {len(crawled_pages)} pages")
        
        return {
            "content": crawled_results,
            "images": all_images,
            "videos": all_videos,
            "pages_crawled": len(crawled_pages)
        }


    async def _research_filter_crawl(
        self,
        start_urls: List[str],
        query: str,
        __event_emitter__: Callable[[dict], Any] = None
    ) -> dict:
        """
        Custom research mode that:
        1. Crawls multiple starting URLs
        2. Follows relevant internal links
        3. Scores content by query relevance
        """
        max_pages = self.user_valves.RESEARCH_MAX_PAGES
        include_external = self.user_valves.RESEARCH_INCLUDE_EXTERNAL
        
        keywords = query.lower().split()
        
        results = {
            "content": [],
            "images": [],
            "videos": [],
            "sources": {},
            "total_pages": 0
        }
        
        for source_url in start_urls[:5]:  # Max 5 starting sources
            if results["total_pages"] >= max_pages:
                break
            
            if __event_emitter__ and self.valves.MORE_STATUS:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"[Research-Filter] Researching: {source_url[:60]}... ({results['total_pages']}/{max_pages})", "done": False},
                })
            
            # Crawl source page
            source_result = await self._crawl_url(urls=[source_url], query=query, extract_links=True, __event_emitter__=__event_emitter__)
            
            if source_result.get("content"):
                # Score content relevance
                content_text = str(source_result["content"])
                relevance_score = sum(1 for kw in keywords if kw in content_text.lower())
                
                results["sources"][source_url] = {
                    "content": source_result["content"],
                    "relevance_score": relevance_score,
                    "links": source_result.get("links", [])[:10]
                }
                
                results["content"].extend(source_result["content"])
                results["total_pages"] += 1
            
            if source_result.get("images"):
                results["images"].extend(source_result["images"])
            
            if source_result.get("videos"):
                results["videos"].extend(source_result["videos"])
            
            # Follow relevant internal links
            relevant_links = []
            for link in source_result.get("links", [])[:15]:
                if results["total_pages"] >= max_pages:
                    break
                
                link_lower = link.lower()
                score = sum(1 for kw in keywords if kw in link_lower)
                if score > 0:
                    relevant_links.append((link, score))
            
            relevant_links.sort(key=lambda x: x[1], reverse=True)
            
            # Crawl relevant links
            crawled = 0
            max_links_per_source = 3
            for link, score in relevant_links:
                if results["total_pages"] >= max_pages:
                    break
                
                if crawled >= max_links_per_source:
                    break
                
                # Check domain
                if not include_external:
                    from urllib.parse import urlparse
                    parsed_link = urlparse(link)
                    parsed_source = urlparse(source_url)
                    if parsed_link.netloc and parsed_link.netloc != parsed_source.netloc:
                        continue
                
                if __event_emitter__ and self.valves.MORE_STATUS:
                    await __event_emitter__({
                        "type": "status",
                        "data": {"description": f"[Research-Filter] Following: {link[:60]}...", "done": False},
                    })
                
                link_result = await self._crawl_url(urls=[link], query=query, __event_emitter__=__event_emitter__)
                
                if link_result.get("content"):
                    content_text = str(link_result["content"])
                    relevance_score = sum(1 for kw in keywords if kw in content_text.lower())
                    
                    results["content"].extend(link_result["content"])
                    results["total_pages"] += 1
                    crawled += 1
                
                if link_result.get("images"):
                    results["images"].extend(link_result["images"])
                
                if link_result.get("videos"):
                    results["videos"].extend(link_result["videos"])
        
        # Sort all content by relevance
        results["content"].sort(
            key=lambda x: sum(1 for kw in keywords if kw in x.get("summary", "").lower()),
            reverse=True
        )
        
        if self.valves.DEBUG:
            logger.info(f"[Research-Filter] Crawled {results['total_pages']} pages")
        
        return results


    async def _crawl_url(self, 
        urls: Union[list, str],
        query: Optional[str] = None,
        extract_links: bool = False,
        __event_emitter__: Callable[[dict], Any] = None
    ) -> dict:
        """
        Internal function to crawl URLs and extract content.
        This tool converts any webpage into clean content and extracts images and videos.
        
        :param urls: The exact web URL(s) to extract data from.
        :param query: Optional search query for research mode.
        :param extract_links: Whether to extract and return discovered links for research mode.
        """
        if isinstance(urls, str):
            urls = [urls]
            
        for idx, url in enumerate(urls):
            # Ensure URL starts with http; default to local-friendly http for hostnames without scheme.
            if not url.startswith("http"):
                urls[idx] = f"http://{url}"

        urls = self._filter_offline_allowed_urls(urls)
        if not urls:
            return {"content": [], "images": [], "videos": [], "links": []}

        endpoint = f"{self.valves.CRAWL4AI_BASE_URL}/crawl"
        if not self._is_offline_allowed_url(endpoint):
            raise ValueError(f"Crawl4AI endpoint is not allowed by Air-Gap guard: {endpoint}")
        
        if self.valves.DEBUG:
            logger.info(f"Using LLM provider: {self.valves.LLM_PROVIDER}")
        
        # Building configs
        browser_config = BrowserConfig(
            headless=True,
            light_mode=True,
            headers={
                "sec-ch-ua": '"Chromium";v="116", "Not_A Brand";v="8", "Google Chrome";v="116"'
            },
            extra_args=[
                "--no-sandbox",
                "--disable-gpu",
            ],
        )
        
        llm_config = LLMConfig(
            provider=self.valves.LLM_PROVIDER,
            base_url=self.valves.LLM_BASE_URL,
            temperature=self.valves.LLM_TEMPERATURE or 0.3,
            max_tokens=self.valves.LLM_MAX_TOKENS or None,
            top_p=self.valves.LLM_TOP_P or None,
            frequency_penalty=self.valves.LLM_FREQUENCY_PENALTY or None,
            presence_penalty=self.valves.LLM_PRESENCE_PENALTY or None
        )
        if self.valves.LLM_API_TOKEN:
            llm_config.api_token = self.valves.LLM_API_TOKEN

        extraction_strategy = LLMExtractionStrategy(
            llm_config=llm_config,
            instruction=self.valves.LLM_INSTRUCTION,
            input_format="fit_markdown",
            schema=ArticleData.model_json_schema(),
        )
        
        md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(),
            options={
                "ignore_links": True,
                "escape_html": False,
                "body_width": 80
            }
        )
        
        crawler_config = CrawlerRunConfig(
            markdown_generator=md_generator,
            extraction_strategy=extraction_strategy,
            table_extraction=DefaultTableExtraction(),
            exclude_external_links=not self.valves.CRAWL4AI_EXTERNAL_DOMAINS,
            exclude_social_media_domains=[d.strip() for d in self.valves.CRAWL4AI_EXCLUDE_SOCIAL_MEDIA_DOMAINS.split(",") if d.strip()],
            exclude_domains=[d.strip() for d in self.valves.CRAWL4AI_EXCLUDE_DOMAINS.split(",") if d.strip()],
            user_agent=self.valves.CRAWL4AI_USER_AGENT,
            stream=False,
            cache_mode=CacheMode.BYPASS,
            page_timeout=self.valves.CRAWL4AI_TIMEOUT * 1000,  # Convert to milliseconds
            only_text=self.valves.CRAWL4AI_TEXT_ONLY,
            word_count_threshold=self.valves.CRAWL4AI_WORD_COUNT_THRESHOLD,
            exclude_all_images=self.valves.CRAWL4AI_EXCLUDE_IMAGES == "All",
            exclude_external_images=self.valves.CRAWL4AI_EXCLUDE_IMAGES == "External",
        )

        if __event_emitter__ and self.valves.MORE_STATUS and len(urls) > 1:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Processing {len(urls)} URLs...", "done": False},
            })
        elif __event_emitter__ and self.valves.MORE_STATUS:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Processing {urls[0]}...", "done": False},
            })

        self.crawl_counter += len(urls)
        
        if self.valves.DEBUG:
            logger.info(f"Contacting Crawl4AI at {endpoint} for URLs: {urls}")

        headers = {"Content-Type": "application/json"}
        
        # Add API token if configured
        if self.valves.CRAWL4AI_API_TOKEN:
            headers["Authorization"] = f"Bearer {self.valves.CRAWL4AI_API_TOKEN}"

        payload = {
            "urls": urls,
            "browser_config": browser_config.dump(),
            "crawler_config": crawler_config.dump()
        }

        try:
            # Using a timeout to prevent the UI from hanging
            timeout = self.valves.CRAWL4AI_TIMEOUT*len(urls) + 60
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=timeout
            )
            response.raise_for_status()
            data = response.json()

            # Crawl4AI returns content in the 'results' key as a list
            results = []
            seen_images = set()
            seen_videos = set()
            all_images = []
            all_videos = []
            all_links = []  # For research mode link extraction
            
            data_list = data.get("results", [])
            for item in data_list:
                if item.get("success") is not True:
                    continue
                    
                url = item.get("url", "")
                parsed_url = urlparse(url)
                
                # Extract media - use consistent min score valve for both images and videos
                image_list = []
                min_score = self.valves.CRAWL4AI_MIN_IMAGE_SCORE
                found_images = list(filter(lambda x: x.get("score", 0) >= min_score, item.get("media", {}).get("images", [])))
                for img in found_images:
                    src = img.get("src")
                    if src:
                        # Fix protocol-relative URLs
                        if src.startswith("//"):
                            src = f"https:{src}"
                        elif not src.startswith("http"):
                            # Handle relative URLs
                            src = f"{parsed_url.scheme}://{parsed_url.netloc}/{src.lstrip('/')}"
                        parsed_image = urlparse(src)
                        if f"{parsed_image.scheme}://{parsed_image.netloc}/{parsed_image.path}" not in seen_images:
                            seen_images.add(f"{parsed_image.scheme}://{parsed_image.netloc}/{parsed_image.path}")
                            image_list.append(src)
                
                video_list = []
                found_videos = list(filter(lambda x: x.get("score", 0) >= min_score, item.get("media", {}).get("videos", [])))
                for vid in found_videos:
                    src = vid.get("src")
                    if src:
                        # Fix protocol-relative URLs
                        if src.startswith("//"):
                            src = f"https:{src}"
                        elif not src.startswith("http"):
                            # Handle relative URLs
                            src = f"{parsed_url.scheme}://{parsed_url.netloc}/{src.lstrip('/')}"
                        parsed_video = urlparse(src)
                        if f"{parsed_video.scheme}://{parsed_video.netloc}/{parsed_video.path}" not in seen_images:
                            seen_videos.add(f"{parsed_video.scheme}://{parsed_video.netloc}/{parsed_video.path}")
                            video_list.append(src)
                
                # Extract links for research mode
                if extract_links:
                    links = []
                    html_content = item.get("html", "")
                    # Simple link extraction from HTML using pre-imported re module
                    link_pattern = r'href=["\'](.*?)["\']'
                    for match in re.findall(link_pattern, html_content):
                        if match and not match.startswith("#") and not match.startswith("javascript:"):
                            # Convert relative URLs to absolute
                            if not match.startswith("http"):
                                if match.startswith("/"):
                                    match = f"{parsed_url.scheme}://{parsed_url.netloc}{match}"
                                else:
                                    match = f"{parsed_url.scheme}://{parsed_url.netloc}/{match}"
                            if match.startswith("http"):
                                links.append(match)
                    all_links.extend(links)

                # Note: Files event removed to prevent duplicate images.
                # Images are now deduplicated and displayed via the main search_and_crawl function.
                
                # Extract content - handle various formats from Crawl4AI
                extracted = item.get("extracted_content", "[]")
                try:
                    if isinstance(extracted, str):
                        tmp_content = orjson.loads(extracted)
                    elif isinstance(extracted, list):
                        tmp_content = extracted
                    else:
                        tmp_content = []
                except (orjson.JSONDecodeError, TypeError) as e:
                    self._log_debug(f"Failed to parse extracted_content: {e}")
                    tmp_content = []

                content_list = []
                for content_item in tmp_content:
                    if isinstance(content_item, dict) and content_item.get("error") is not True:
                        content_list.append({
                            "topic": content_item.get("topic", ""),
                            "summary": content_item.get("summary", "")
                        })
                
                # Build result with URL included
                results.append({
                    "url": url,
                    "title": item.get("metadata", {}).get("title", ""),
                    "content": content_list,
                    "images": image_list,
                    "videos": video_list
                })
                all_images.extend(image_list)
                all_videos.extend(video_list)
                
                # Emit citation for this URL
                if __event_emitter__:
                    await __event_emitter__({
                        "type": "citation",
                        "data": {
                            "document": [f"Content from {url}"],
                            "metadata": [{"source": url}],
                            "source": {"name": item.get("metadata", {}).get("title", url)},
                        },
                    })
                
            self.content_counter += len(results)
            if __event_emitter__ and self.valves.MORE_STATUS:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"Analyzed {self.content_counter} page{'s' if self.content_counter > 1 else ''} from {self.total_urls} URL{'s' if self.crawl_counter > 1 else ''}...", "done": False},
                })
            
            if self.valves.DEBUG:
                logger.info(f"Successfully crawled {len(results)} URLs")
            response = {
                "content": results,
                "images": all_images or [],
                "videos": all_videos or [],
                "links": all_links if extract_links else []
            }
            return response

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error connecting to Crawl4AI: {str(e)}. Check if the URL {self.valves.CRAWL4AI_BASE_URL} is accessible."
            logger.error(error_msg)
            if __event_emitter__:
                await __event_emitter__({
                    "type": "error",
                    "data": {"description": error_msg, "done": True},
                })
            return {"error": error_msg, "details": e}
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            if __event_emitter__:
                await __event_emitter__({
                    "type": "error",
                    "data": {"description": error_msg, "done": True},
                })
            return {"error": error_msg, "details": e}
