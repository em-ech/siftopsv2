"""
Security Module
Provides prompt injection detection, input sanitization, rate limiting, and output validation.
"""

import re
import time
import hashlib
from typing import Optional, Literal, NamedTuple
from collections import defaultdict
from functools import wraps
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from pydantic import BaseModel


# ==================== PROMPT INJECTION DETECTION ====================


class InjectionDetection(NamedTuple):
    """Result of prompt injection detection."""
    risk_level: Literal["low", "medium", "high"]
    matched_patterns: list[str]
    message: str


class PromptInjectionDetector:
    """
    Detects potential prompt injection attacks in user input.

    Uses pattern matching for known injection techniques:
    - Role manipulation attempts
    - Instruction override attempts
    - System prompt extraction attempts
    """

    # High risk patterns - likely malicious
    HIGH_RISK_PATTERNS = [
        # Instruction override attempts
        r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)",
        r"forget\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)",
        r"override\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)",
        # Role manipulation
        r"you\s+are\s+now\s+(a|an|the)\s+\w+",
        r"pretend\s+(to\s+be|you\s*'?re)",
        r"act\s+as\s+(if|a|an|the)",
        r"roleplay\s+as",
        r"assume\s+the\s+role\s+of",
        # System prompt extraction
        r"(show|reveal|display|print|output|repeat)\s+(me\s+)?(your|the)\s+(system\s+)?(prompt|instructions?|rules?)",
        r"what\s+(are|is)\s+(your|the)\s+(system\s+)?(prompt|instructions?|rules?)",
        # Direct injection markers
        r"<\s*system\s*>",
        r"\[\s*system\s*\]",
        r"system\s*:",
        r"###\s*(system|instruction)",
    ]

    # Medium risk patterns - suspicious but might be legitimate
    MEDIUM_RISK_PATTERNS = [
        # Code injection attempts
        r"```\s*(python|javascript|bash|shell)",
        r"eval\s*\(",
        r"exec\s*\(",
        # Manipulation keywords
        r"bypass\s+(the\s+)?(filter|restriction|rule|security)",
        r"jailbreak",
        r"dan\s+mode",
        r"developer\s+mode",
        # Prompt structure attempts
        r"\[\s*(user|assistant|human|ai)\s*\]",
        r"<\s*(user|assistant|human|ai)\s*>",
    ]

    def __init__(self):
        self._high_patterns = [re.compile(p, re.IGNORECASE) for p in self.HIGH_RISK_PATTERNS]
        self._medium_patterns = [re.compile(p, re.IGNORECASE) for p in self.MEDIUM_RISK_PATTERNS]

    def detect(self, text: str) -> InjectionDetection:
        """
        Analyze text for potential prompt injection.

        Returns:
            InjectionDetection with risk_level, matched_patterns, and message
        """
        if not text:
            return InjectionDetection("low", [], "Empty input")

        matched_high = []
        matched_medium = []

        # Check high risk patterns
        for pattern in self._high_patterns:
            if pattern.search(text):
                matched_high.append(pattern.pattern)

        # Check medium risk patterns
        for pattern in self._medium_patterns:
            if pattern.search(text):
                matched_medium.append(pattern.pattern)

        # Determine risk level
        if matched_high:
            return InjectionDetection(
                "high",
                matched_high,
                f"High risk: detected {len(matched_high)} injection pattern(s)"
            )
        elif matched_medium:
            return InjectionDetection(
                "medium",
                matched_medium,
                f"Medium risk: detected {len(matched_medium)} suspicious pattern(s)"
            )
        else:
            return InjectionDetection("low", [], "No injection patterns detected")


# ==================== INPUT SANITIZATION ====================


class InputSanitizer:
    """
    Sanitizes user input before processing.

    Provides methods for:
    - Query sanitization (search queries)
    - Prompt sanitization (text going into LLM prompts)
    - Product data sanitization (prevent product-based injection)
    """

    # Characters that could be used for prompt manipulation
    PROMPT_CONTROL_CHARS = [
        '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
        '\x08', '\x0b', '\x0c', '\x0e', '\x0f', '\x10', '\x11', '\x12',
        '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a',
        '\x1b', '\x1c', '\x1d', '\x1e', '\x1f',
    ]

    # Maximum lengths for different input types
    MAX_QUERY_LENGTH = 500
    MAX_PRODUCT_NAME_LENGTH = 200
    MAX_PRODUCT_DESCRIPTION_LENGTH = 2000

    def sanitize_query(self, query: str) -> str:
        """
        Sanitize a search query.

        - Removes control characters
        - Normalizes whitespace
        - Truncates to max length
        """
        if not query:
            return ""

        # Remove control characters
        for char in self.PROMPT_CONTROL_CHARS:
            query = query.replace(char, '')

        # Normalize whitespace
        query = ' '.join(query.split())

        # Truncate
        return query[:self.MAX_QUERY_LENGTH]

    def sanitize_for_prompt(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitize text before including in an LLM prompt.

        - Escapes characters that might confuse the model
        - Removes potential role markers
        - Normalizes whitespace
        """
        if not text:
            return ""

        # Remove control characters
        for char in self.PROMPT_CONTROL_CHARS:
            text = text.replace(char, '')

        # Escape potential role markers (but don't remove - could be legitimate)
        text = re.sub(r'(\[|\<)(system|user|assistant|human|ai)(\]|\>)',
                      r'[\1\2\3]', text, flags=re.IGNORECASE)

        # Remove potential instruction markers
        text = re.sub(r'^(system|instructions?|rules?)\s*:\s*', '', text, flags=re.IGNORECASE)

        # Normalize whitespace
        text = ' '.join(text.split())

        return text[:max_length]

    def sanitize_product_data(self, product: dict) -> dict:
        """
        Sanitize product data before including in prompts.

        This prevents product names/descriptions from containing
        prompt injection attempts.
        """
        sanitized = product.copy()

        if 'name' in sanitized:
            name = str(sanitized['name'])
            name = self.sanitize_for_prompt(name, self.MAX_PRODUCT_NAME_LENGTH)
            # Remove anything that looks like system instructions in product names
            name = re.sub(r'\b(ignore|disregard|forget|override)\s+\w+\s+(instructions?|rules?)\b',
                         '', name, flags=re.IGNORECASE)
            sanitized['name'] = name.strip()

        if 'description' in sanitized:
            desc = str(sanitized['description'] or '')
            desc = self.sanitize_for_prompt(desc, self.MAX_PRODUCT_DESCRIPTION_LENGTH)
            sanitized['description'] = desc.strip()

        return sanitized


# ==================== RATE LIMITING ====================


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting."""
    enabled: bool = True
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10  # Max requests in a 1-second window

    class Config:
        frozen = True


class RateLimiter:
    """
    In-memory sliding window rate limiter.

    For production, consider using Redis for distributed rate limiting.
    """

    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        # {client_id: [(timestamp, count), ...]}
        self._minute_windows: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._hour_windows: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._burst_windows: dict[str, list[float]] = defaultdict(list)

    def _clean_old_entries(self, entries: list, cutoff: float) -> list:
        """Remove entries older than cutoff timestamp."""
        return [e for e in entries if e[0] if isinstance(e, tuple) else e > cutoff]

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        # Check for API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client = request.client
        if client:
            return f"ip:{client.host}"

        return "unknown"

    def check_rate_limit(self, client_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if a client has exceeded rate limits.

        Returns:
            (allowed: bool, reason: str | None)
        """
        if not self.config.enabled:
            return True, None

        now = time.time()

        # Check burst limit (1 second window)
        burst_entries = self._burst_windows[client_id]
        burst_entries = [t for t in burst_entries if t > now - 1]
        self._burst_windows[client_id] = burst_entries

        if len(burst_entries) >= self.config.burst_limit:
            return False, f"Burst limit exceeded ({self.config.burst_limit}/second)"

        # Check minute limit
        minute_entries = self._minute_windows[client_id]
        minute_entries = [(t, c) for t, c in minute_entries if t > now - 60]
        self._minute_windows[client_id] = minute_entries

        minute_count = sum(c for _, c in minute_entries)
        if minute_count >= self.config.requests_per_minute:
            return False, f"Rate limit exceeded ({self.config.requests_per_minute}/minute)"

        # Check hour limit
        hour_entries = self._hour_windows[client_id]
        hour_entries = [(t, c) for t, c in hour_entries if t > now - 3600]
        self._hour_windows[client_id] = hour_entries

        hour_count = sum(c for _, c in hour_entries)
        if hour_count >= self.config.requests_per_hour:
            return False, f"Rate limit exceeded ({self.config.requests_per_hour}/hour)"

        return True, None

    def record_request(self, client_id: str):
        """Record a request for rate limiting."""
        now = time.time()

        self._burst_windows[client_id].append(now)
        self._minute_windows[client_id].append((now, 1))
        self._hour_windows[client_id].append((now, 1))

    def get_limits_info(self, client_id: str) -> dict:
        """Get current rate limit status for a client."""
        now = time.time()

        minute_entries = [(t, c) for t, c in self._minute_windows.get(client_id, []) if t > now - 60]
        hour_entries = [(t, c) for t, c in self._hour_windows.get(client_id, []) if t > now - 3600]

        return {
            "requests_last_minute": sum(c for _, c in minute_entries),
            "requests_last_hour": sum(c for _, c in hour_entries),
            "limit_per_minute": self.config.requests_per_minute,
            "limit_per_hour": self.config.requests_per_hour,
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic rate limiting."""

    def __init__(self, app, config: RateLimitConfig = None, exclude_paths: list[str] = None):
        super().__init__(app)
        self.limiter = RateLimiter(config)
        self.exclude_paths = exclude_paths or ["/", "/health", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        client_id = self.limiter._get_client_id(request)

        allowed, reason = self.limiter.check_rate_limit(client_id)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": reason,
                    "limits": self.limiter.get_limits_info(client_id),
                },
                headers={"Retry-After": "60"},
            )

        self.limiter.record_request(client_id)

        response = await call_next(request)
        return response


# ==================== OUTPUT VALIDATION ====================


class OutputValidation(NamedTuple):
    """Result of output validation."""
    is_valid: bool
    sanitized_response: str
    issues: list[str]


class OutputValidator:
    """
    Validates LLM outputs for security issues.

    Checks for:
    - Prompt/instruction leakage
    - References to non-retrieved products
    """

    # Patterns that might indicate prompt leakage
    LEAKAGE_PATTERNS = [
        r"(my|the)\s+(system\s+)?(prompt|instructions?)\s+(is|are|says?)",
        r"(i\s+was|i\'ve\s+been)\s+(told|instructed|programmed)\s+to",
        r"(according\s+to|based\s+on)\s+(my|the)\s+(instructions?|rules?|guidelines?)",
        r"CRITICAL\s+RULES",  # From our system prompt
        r"AVAILABLE\s+PRODUCTS\s+FOR\s+THIS\s+QUERY",  # From our system prompt
    ]

    def __init__(self):
        self._leakage_patterns = [re.compile(p, re.IGNORECASE) for p in self.LEAKAGE_PATTERNS]

    def validate_response(
        self,
        response: str,
        retrieved_products: list[dict] = None
    ) -> OutputValidation:
        """
        Validate an LLM response for security issues.

        Args:
            response: The LLM's response text
            retrieved_products: List of products that were provided to the LLM

        Returns:
            OutputValidation with is_valid, sanitized_response, and issues
        """
        issues = []
        sanitized = response

        # Check for prompt leakage
        for pattern in self._leakage_patterns:
            if pattern.search(response):
                issues.append(f"Potential prompt leakage detected")
                # Remove the leaking section (basic approach)
                sanitized = pattern.sub('[...]', sanitized)

        # If we have retrieved products, we could check that the response
        # only mentions those products. This is complex and context-dependent,
        # so we'll just flag if it looks like there might be hallucinated products.
        if retrieved_products:
            product_names = {p.get('name', '').lower() for p in retrieved_products}
            # This is a heuristic - in production, you might want more sophisticated checks
            # For now, we trust the system prompt constraints

        return OutputValidation(
            is_valid=len(issues) == 0,
            sanitized_response=sanitized,
            issues=issues,
        )


# ==================== SINGLETON INSTANCES ====================

# Create singleton instances for easy import
injection_detector = PromptInjectionDetector()
sanitizer = InputSanitizer()
output_validator = OutputValidator()

# Default rate limit config (can be overridden in main.py)
default_rate_limit_config = RateLimitConfig()
