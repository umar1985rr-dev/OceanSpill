from backend.config import settings

from backend.services.satellite_feed.base import FeedFrame, SatelliteFeed

from backend.services.satellite_feed.sentinel_hub import SentinelHubFeed


def create_feed():

    """
    Factory: return the feed selected by FEED_SOURCE.

    The runtime config (set via the /config UI) takes precedence over
    the environment variable so officials can switch feeds without
    editing env vars or restarting the backend.
    """

    try:

        from backend.api.config_store import get_config

        feed_source = get_config().get(
            "feed_source",
            settings.feed_source,
        )

    except Exception:

        feed_source = settings.feed_source

    if feed_source == "sentinel_hub":

        return SentinelHubFeed()

    raise ValueError(
        f"Unknown satellite feed source '{feed_source}'. "
        "Configure a valid feed in the Configuration page "
        "(e.g. 'sentinel_hub')."
    )
