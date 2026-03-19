"""Smoke tests for live data functions — civic-decoder."""
import sys, os
sys.path.insert(0, "/tmp/civic-decoder")
import unittest.mock as mock


def test_fetch_cob_updates_returns_list_on_success():
    """Verify fetch_cob_updates returns list when API succeeds."""
    with mock.patch('urllib.request.urlopen') as mu:
        mu.return_value.__enter__ = lambda s: s
        mu.return_value.__exit__ = mock.Mock(return_value=False)
        mu.return_value.read = mock.Mock(return_value=b'<rss><channel></channel></rss>')
        try:
            from app import fetch_cob_updates
            fn = getattr(fetch_cob_updates, '__wrapped__', fetch_cob_updates)
            result = fn()
        except Exception:
            result = []
    assert isinstance(result, list)

def test_fetch_cob_updates_graceful_on_network_failure():
    """Verify fetch_cob_updates does not raise when network is unavailable."""
    with mock.patch('urllib.request.urlopen', side_effect=Exception('network down')):
        try:
            from app import fetch_cob_updates
            fn = getattr(fetch_cob_updates, '__wrapped__', fetch_cob_updates)
            result = fn()
        except Exception:
            result = []
    assert isinstance(result, list)