#!/usr/bin/env python3
"""
Genesis WebSearch Module
Free multi-source web search with concurrent querying and result aggregation
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path
import hashlib
import re
from bs4 import BeautifulSoup


class WebSearchCache:
    """Simple file-based cache for search results"""

    def __init__(self, cache_dir: str = "data/cache", ttl_minutes: int = 15):
        """
        Initialize cache

        Args:
            cache_dir: Directory for cache files
            ttl_minutes: Time-to-live in minutes
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_minutes * 60

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query: str) -> Optional[Dict]:
        """
        Get cached result if available and fresh

        Args:
            query: Search query

        Returns:
            Cached result or None
        """
        try:
            cache_file = self.cache_dir / f"{self._get_cache_key(query)}.json"

            if not cache_file.exists():
                return None

            # Check age
            age = time.time() - cache_file.stat().st_mtime
            if age > self.ttl_seconds:
                cache_file.unlink()  # Remove stale cache
                return None

            with open(cache_file, 'r') as f:
                return json.load(f)

        except Exception:
            return None

    def set(self, query: str, result: Dict):
        """
        Cache a search result

        Args:
            query: Search query
            result: Result to cache
        """
        try:
            cache_file = self.cache_dir / f"{self._get_cache_key(query)}.json"

            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)

        except Exception as e:
            print(f"⚠️ Warning: Could not cache result: {e}")


class WebSearchSource:
    """Base class for web search sources"""

    def __init__(self, name: str, timeout: int = 10):
        """
        Initialize search source

        Args:
            name: Source name
            timeout: Request timeout in seconds
        """
        self.name = name
        self.timeout = timeout

    def search(self, query: str) -> Tuple[bool, List[Dict]]:
        """
        Perform search

        Args:
            query: Search query

        Returns:
            (success, results) tuple
        """
        raise NotImplementedError


class DuckDuckGoSearch(WebSearchSource):
    """DuckDuckGo HTML search (no API key needed)"""

    def __init__(self, timeout: int = 10):
        super().__init__("DuckDuckGo", timeout)
        self.base_url = "https://html.duckduckgo.com/html/"

    def search(self, query: str) -> Tuple[bool, List[Dict]]:
        """Search DuckDuckGo"""
        try:
            # Prepare POST data
            data = urllib.parse.urlencode({'q': query}).encode()

            # Create request with headers
            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Genesis/1.0',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )

            # Execute search
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html = response.read().decode('utf-8')

            # Parse results
            results = self._parse_results(html)
            return True, results

        except Exception as e:
            return False, []

    def _parse_results(self, html: str) -> List[Dict]:
        """Parse DuckDuckGo HTML results"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []

            # Find result divs
            for result_div in soup.find_all('div', class_='result'):
                try:
                    # Extract title and link
                    title_elem = result_div.find('a', class_='result__a')
                    snippet_elem = result_div.find('a', class_='result__snippet')

                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': self.name
                        })

                        if len(results) >= 5:  # Limit to top 5
                            break
                except:
                    continue

            return results

        except Exception:
            return []


class WikipediaSearch(WebSearchSource):
    """Wikipedia API search"""

    def __init__(self, timeout: int = 10):
        super().__init__("Wikipedia", timeout)
        self.api_url = "https://en.wikipedia.org/w/api.php"

    def search(self, query: str) -> Tuple[bool, List[Dict]]:
        """Search Wikipedia"""
        try:
            # Search for pages
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': 3,
                'format': 'json'
            }

            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Genesis/1.0'}
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())

            # Parse response
            results = []
            if len(data) >= 4:
                titles = data[1]
                descriptions = data[2]
                urls = data[3]

                for title, desc, url in zip(titles, descriptions, urls):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': desc,
                        'source': self.name
                    })

            return True, results

        except Exception:
            return False, []


class ArXivSearch(WebSearchSource):
    """ArXiv API search for academic papers"""

    def __init__(self, timeout: int = 10):
        super().__init__("ArXiv", timeout)
        self.api_url = "http://export.arxiv.org/api/query"

    def search(self, query: str) -> Tuple[bool, List[Dict]]:
        """Search ArXiv"""
        try:
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': 3,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }

            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Genesis/1.0'}
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                xml = response.read().decode()

            # Parse XML results (basic parsing)
            results = []
            entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)

            for entry in entries[:3]:
                title_match = re.search(r'<title>(.*?)</title>', entry)
                summary_match = re.search(r'<summary>(.*?)</summary>', entry)
                link_match = re.search(r'<id>(.*?)</id>', entry)

                if title_match and link_match:
                    results.append({
                        'title': title_match.group(1).strip(),
                        'url': link_match.group(1).strip(),
                        'snippet': summary_match.group(1).strip()[:200] if summary_match else "",
                        'source': self.name
                    })

            return True, results

        except Exception:
            return False, []


class WebSearch:
    """Multi-source web search with concurrent querying"""

    def __init__(self, cache_ttl_minutes: int = 15, max_workers: int = 3):
        """
        Initialize web search

        Args:
            cache_ttl_minutes: Cache TTL in minutes
            max_workers: Max concurrent search workers
        """
        self.cache = WebSearchCache(ttl_minutes=cache_ttl_minutes)
        self.max_workers = max_workers

        # Initialize search sources
        self.sources = [
            DuckDuckGoSearch(),
            WikipediaSearch(),
            ArXivSearch()
        ]

    def search(self, query: str, use_cache: bool = True, min_confidence: float = 0.7) -> Tuple[bool, str, float]:
        """
        Perform multi-source web search

        Args:
            query: Search query
            use_cache: Whether to use cached results
            min_confidence: Minimum confidence threshold

        Returns:
            (success, synthesized_answer, confidence) tuple
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(query)
            if cached:
                return True, cached['answer'], cached['confidence']

        # Perform concurrent search across sources
        all_results = []
        successful_sources = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(source.search, query): source
                for source in self.sources
            }

            for future in as_completed(future_to_source, timeout=15):
                source = future_to_source[future]
                try:
                    success, results = future.result(timeout=10)
                    if success and results:
                        all_results.extend(results)
                        successful_sources.append(source.name)
                except Exception:
                    continue

        # Check if we got any results
        if not all_results:
            return False, "No search results found", 0.0

        # Synthesize and rank results
        synthesized, confidence = self._synthesize_results(all_results, successful_sources)

        # Cache result if confidence is high enough
        if confidence >= min_confidence:
            self.cache.set(query, {
                'answer': synthesized,
                'confidence': confidence,
                'sources': successful_sources,
                'timestamp': time.time()
            })

        return True, synthesized, confidence

    def _synthesize_results(self, results: List[Dict], sources: List[str]) -> Tuple[str, float]:
        """
        Synthesize search results into coherent answer

        Args:
            results: List of search results
            sources: List of successful source names

        Returns:
            (synthesized_answer, confidence_score) tuple
        """
        if not results:
            return "No information found", 0.0

        # Calculate confidence based on result quality
        confidence = min(1.0, len(results) / 10.0)  # More results = higher confidence
        confidence *= min(1.0, len(sources) / 3.0)  # More sources = higher confidence

        # Build synthesized answer
        lines = []

        # Group by source
        by_source = {}
        for result in results:
            source = result['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)

        # Format results
        for source, source_results in by_source.items():
            lines.append(f"\n**{source}:**")
            for i, result in enumerate(source_results[:3], 1):
                title = result['title']
                snippet = result['snippet'][:150] if result['snippet'] else "No description"
                url = result['url']

                lines.append(f"{i}. {title}")
                if snippet:
                    lines.append(f"   {snippet}...")
                lines.append(f"   {url}")

        synthesized = "\n".join(lines)

        # Add source citation
        if sources:
            synthesized += f"\n\n**Sources consulted:** {', '.join(sources)}"

        return synthesized, confidence

    def quick_search(self, query: str) -> str:
        """
        Perform quick search and return simple string result

        Args:
            query: Search query

        Returns:
            Search result string
        """
        success, answer, confidence = self.search(query)

        if success:
            return f"{answer}\n\nConfidence: {confidence:.2f}"
        else:
            return "Search failed or no results found"


# Global instance
_websearch_instance = None


def get_websearch() -> WebSearch:
    """Get or create global WebSearch instance"""
    global _websearch_instance
    if _websearch_instance is None:
        _websearch_instance = WebSearch()
    return _websearch_instance


if __name__ == "__main__":
    # Test the web search module
    search = WebSearch()

    test_query = "latest AI breakthroughs 2025"
    print(f"Testing search for: {test_query}\n")

    success, answer, confidence = search.search(test_query)

    print(f"Success: {success}")
    print(f"Confidence: {confidence:.2f}")
    print(f"\nAnswer:\n{answer}")
