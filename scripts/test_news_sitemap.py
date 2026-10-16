"""Check freshness boundaries and graph parsing used by news discovery."""
from datetime import datetime, timedelta, timezone
import unittest
from news_sitemap import Metadata, nodes, recent_articles

class NewsSitemapTest(unittest.TestCase):
    def test_publication_window(self):
        now = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)
        entries = [(label, {'datePublished': stamp.isoformat()}) for label, stamp in [
            ('old', now - timedelta(days=2)),
            ('recent', now - timedelta(days=2) + timedelta(seconds=1)),
            ('now', now),
            ('future', now + timedelta(seconds=1)),
        ]]
        self.assertEqual([p for p, _ in recent_articles(entries, now)], ['recent', 'now'])

    def test_graph_and_no_invented_dates(self):
        page = Metadata()
        page.feed('<script type="application/ld+json">{"@graph":[{"@type":"Article","headline":"Archive"}]}</script>')
        article = next(node for node in nodes(page.jsonld) if node.get('@type') == 'Article')
        self.assertEqual(list(recent_articles([('archive', article)], datetime.now(timezone.utc))), [])

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            list(recent_articles([('bad', {'datePublished':'2026-10-16T12:00:00'})], datetime.now(timezone.utc)))

if __name__ == '__main__':
    unittest.main()
