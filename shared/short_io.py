import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ShortIOService:
    """Service to interact with Short.io API"""

    BASE_URL = "https://api.short.io"

    def __init__(self):
        self.api_key = getattr(settings, "PUBLIC_SHORT_API", None) or getattr(
            settings, "SHORT_IO_API_KEY", None
        )
        import os

        if not self.api_key:
            self.api_key = os.getenv("PUBLIC_SHORT_API")

        self.domain = getattr(settings, "SHORT_IO_DOMAIN", None) or os.getenv(
            "SHORT_IO_DOMAIN"
        )

        self.folder_id = getattr(settings, "SHORT_IO_FOLDER_ID", None) or os.getenv(
            "SHORT_IO_FOLDER_ID"
        )

    def shorten_url(self, original_url, title=None, folder_id=None):
        """
        Create a short URL for the given original URL.

        Args:
            original_url: The destination URL to shorten
            title: Optional title for the link
            folder_id: Optional folder ID to organize links. If not provided, uses default from settings.
        """
        if not self.api_key:
            logger.error("Short.io API key is missing.")
            return None

        endpoint = f"{self.BASE_URL}/links"

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "originalURL": original_url,
            "domain": self.domain,
        }

        if title:
            payload["title"] = title

        effective_folder_id = folder_id or self.folder_id
        if effective_folder_id:
            payload["folderId"] = effective_folder_id

        logger.info(
            f"Short.io API request - Domain: {self.domain}, Folder ID: {effective_folder_id}"
        )
        logger.info(f"Short.io payload: {payload}")

        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            logger.info(f"Short.io response status: {response.status_code}")
            logger.info(f"Short.io response body: {response.text}")
            response.raise_for_status()
            data = response.json()

            return {
                "shortURL": data.get("shortURL"),
                "idString": data.get("idString"),
                "secureShortURL": data.get("secureShortURL"),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error shortening URL: {e}")
            if response:
                logger.error(f"Response: {response.text}")
            return None

    def get_clicks(self, link_id):
        """
        Get click statistics for a specific link ID.
        """
        if not self.api_key or not link_id:
            return 0

        endpoint = f"{self.BASE_URL}/statistics/link/{link_id}"

        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
        }

        params = {"period": "total", "tzOffset": 0}

        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("humanClicks", 0)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching stats for link {link_id}: {e}")
            return 0

    def update_link(self, link_id, original_url, title=None):
        """
        Update the destination URL of an existing short link.
        """
        if not self.api_key or not link_id:
            return None

        endpoint = f"{self.BASE_URL}/links/{link_id}"

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "originalURL": original_url,
        }

        if title:
            payload["title"] = title

        try:
            # According to Short.io API, updating a link uses POST to /links/{id}
            # Reference: https://developers.short.io/reference/post_links-linkid
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            return {
                "shortURL": data.get("shortURL"),
                "idString": data.get("idString"),
                "secureShortURL": data.get("secureShortURL"),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating link {link_id}: {e}")
            if response:
                logger.error(f"Response: {response.text}")
            return None

    def get_link_statistics(self, link_id, period="total"):
        """
        Get detailed statistics for a link.
        """
        if not self.api_key or not link_id:
            return None

        # Statistics endpoint uses a different subdomain
        endpoint = f"https://statistics.short.io/statistics/link/{link_id}"

        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
        }

        # Determine date range based on period
        params = {"period": period, "tzOffset": 0}

        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching statistics for link {link_id}: {e}")
            return None

    def get_aggregated_link_statistics(self, link_ids, period="total"):
        """
        Aggregate statistics across multiple links.
        """
        if not link_ids:
            return {
                "totalClicks": 0,
                "humanClicks": 0,
                "clickStatistics": {"timeline": []},
            }

        aggregated = {
            "totalClicks": 0,
            "humanClicks": 0,
            "clickStatistics": {"timeline": []},
        }

        timeline_map = {}  # date -> clicks

        # Ensure we only count each Short.io link once
        unique_link_ids = set(link_ids)

        for lid in unique_link_ids:
            stats = self.get_link_statistics(lid, period)
            if not stats:
                continue

            aggregated["totalClicks"] += stats.get("totalClicks", 0)
            aggregated["humanClicks"] += stats.get("humanClicks", 0)

            # Aggregate timeline (handle both Short.io response formats)
            click_stats = stats.get("clickStatistics", {})
            timeline = []

            if "datasets" in click_stats and click_stats["datasets"]:
                data = click_stats["datasets"][0].get("data", [])
                # Convert {x: date, y: value} to {moment: date, clicks: value}
                timeline = [
                    {"moment": p["x"], "clicks": int(p["y"])}
                    for p in data
                    if "x" in p and "y" in p
                ]
            elif "timeline" in click_stats:
                timeline = click_stats.get("timeline", [])

            for point in timeline:
                moment = point.get("moment")
                clicks = point.get("clicks", 0)
                if moment:
                    timeline_map[moment] = timeline_map.get(moment, 0) + clicks

        # Convert map back to sorted list of points
        sorted_moments = sorted(timeline_map.keys())
        aggregated["clickStatistics"]["timeline"] = [
            {"moment": m, "clicks": timeline_map[m]} for m in sorted_moments
        ]

        return aggregated
