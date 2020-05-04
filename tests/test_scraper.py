import unittest
from unittest.mock import Mock, patch

import json

import scraper
import tests.mock_output


class TestMatched(unittest.TestCase):
    def setUp(self):
        self.scraper_config = {
            'scraper': {'frequency': 1, 'run_once': True},
            'request': {'timeout': 10},
            'http://127.0.0.1:81': {'pattern': "foo.*"}
        }
        self.s = scraper.Scraper(tests.mock_output.MockOutput(), self.scraper_config)
        pass

    @patch('scraper.requests.get')
    @patch('tests.mock_output.MockOutput.send')
    def test_matched(self, mock_send, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.status_code = 201
        mock_get.return_value.text = "foobar"
        mock_get.return_value.elapsed.total_seconds = lambda: 0.5

        self.s.run()
        self.assertEqual(mock_send.called, True)
        self.assertEqual(mock_get.called, True)

        result = mock_send.call_args[0][0]
        self.assertEqual(type(result), scraper.ScrapeResult)
        self.assertEqual(result.url, "http://127.0.0.1:81")
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.response_time, 0.5)
        self.assertEqual(result.error, None)
        self.assertEqual(result.matched, True)

    @patch('scraper.requests.get')
    @patch('tests.mock_output.MockOutput.send')
    def test_nomatched(self, mock_send, mock_get):
        mock_get.return_value.text = "nomatch"
        self.s.run()
        result = mock_send.call_args[0][0]
        self.assertEqual(result.matched, False)

    @patch('scraper.requests.get')
    @patch('tests.mock_output.MockOutput.send')
    def test_error(self, mock_send, mock_get):
        mock_get.return_value.text = "nomatch"
        mock_get.side_effect = Mock(side_effect=Exception('Test'))
        self.s.run()
        result = mock_send.call_args[0][0]
        self.assertEqual(result.status_code, None)
        self.assertEqual(result.response_time, None)
        self.assertEqual(result.error, "Test")


class TestScrapeResultOK(unittest.TestCase):
    def setUp(self):
        self.sr = scraper.ScrapeResult(url="http://foo", scrape_time=1588571439.95631, status_code=200,
                                       matched=False, response_time=0.5, error=None)

    def test_serialize(self):
        re_encode = json.loads(self.sr.serialize().decode('utf-8'))
        for x in vars(self.sr):
            self.assertEqual(self.sr.__getattribute__(x), re_encode[x])

    def test_deserialize(self):
        deserialized = self.sr.deserialize(self.sr.serialize())
        for x in vars(self.sr):
            self.assertEqual(self.sr.__getattribute__(x), deserialized.__getattribute__(x))

    def test_repr(self):
        self.assertEqual(repr(self.sr), "2020-05-04 05:50:39: http://foo: 200 False 0.5")


if __name__ == '__main__':
    unittest.main()
