"""Check freshness boundaries and graph parsing used by news discovery."""
from datetime import datetime, timedelta, timezone
import unittest
from news_sitemap import Metadata, nodes, recent_articles
from homepage_latest import latest_articles, render as render_latest

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


class HomepageLatestTest(unittest.TestCase):
    def test_order_uses_publication_not_modification_and_excludes_future(self):
        now = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)
        articles = [
            ('may', {'datePublished': '2026-05-27T12:00:00Z', 'dateModified': '2026-10-17T11:00:00Z'}),
            ('october16', {'datePublished': '2026-10-16T00:00:00-06:00'}),
            ('archive', {'headline': 'Unknown publication date'}),
            ('future', {'datePublished': '2026-10-18T00:00:00Z'}),
            ('october17', {'datePublished': '2026-10-17T05:00:00-06:00'}),
        ]
        self.assertEqual([row[1] for row in latest_articles(articles, now)], ['october17', 'october16', 'may'])

    def test_bounded_list_preserves_other_content_and_escapes_text(self):
        html = 'before<!-- latest-articles:start -->old<!-- latest-articles:end -->after'
        articles = [('articles/example.html', {'headline':'A < B', 'description':'Costs & choices',
                    'datePublished':'2026-10-17T00:00:00Z'})]
        result = render_latest(html, articles, datetime(2026, 10, 17, 12, tzinfo=timezone.utc))
        self.assertTrue(result.startswith('before<!-- latest-articles:start -->'))
        self.assertTrue(result.endswith('<!-- latest-articles:end -->after'))
        self.assertIn('A &lt; B', result)
        self.assertIn('Costs &amp; choices', result)
        self.assertNotIn('>old<', result)

if __name__ == '__main__':
    unittest.main()
