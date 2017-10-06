import unittest
from imp import load_source


class TestVersionedQueries(unittest.TestCase):

    def test_min(self):
        pgmg = load_source('pgmg', 'pg_multigraph')
        queries = {
            'foo': {
                (1, 0, 0): 'foo-100',
                (2, 0, 0): 'foo-200',
                (3, 0, 0): 'foo-300',
            }
        }
        result = pgmg.queries_for_version(queries, (1, 0, 0))
        self.assertEqual(result, {'foo': 'foo-100'})

    def test_mid(self):
        pgmg = load_source('pgmg', 'pg_multigraph')
        queries = {
            'foo': {
                (1, 0, 0): 'foo-100',
                (2, 0, 0): 'foo-200',
                (3, 0, 0): 'foo-300',
            }
        }
        result = pgmg.queries_for_version(queries, (2, 0, 0))
        self.assertEqual(result, {'foo': 'foo-200'})

    def test_max(self):
        pgmg = load_source('pgmg', 'pg_multigraph')
        queries = {
            'foo': {
                (1, 0, 0): 'foo-100',
                (2, 0, 0): 'foo-200',
                (3, 0, 0): 'foo-300',
            }
        }
        result = pgmg.queries_for_version(queries, (3, 0, 0))
        self.assertEqual(result, {'foo': 'foo-300'})

    def test_below_min(self):
        pgmg = load_source('pgmg', 'pg_multigraph')
        queries = {
            'foo': {
                (1, 0, 0): 'foo-100',
                (2, 0, 0): 'foo-200',
                (3, 0, 0): 'foo-300',
            }
        }
        result = pgmg.queries_for_version(queries, (0, 5, 0))
        self.assertEqual(result, {})

    def test_between_versions(self):
        pgmg = load_source('pgmg', 'pg_multigraph')
        queries = {
            'foo': {
                (1, 0, 0): 'foo-100',
                (2, 0, 0): 'foo-200',
                (3, 0, 0): 'foo-300',
            }
        }
        result = pgmg.queries_for_version(queries, (2, 1, 0))
        self.assertEqual(result, {'foo': 'foo-200'})

    def test_after_max(self):
        pgmg = load_source('pgmg', 'pg_multigraph')
        queries = {
            'foo': {
                (1, 0, 0): 'foo-100',
                (2, 0, 0): 'foo-200',
                (3, 0, 0): 'foo-300',
            }
        }
        result = pgmg.queries_for_version(queries, (4, 0, 0))
        self.assertEqual(result, {'foo': 'foo-300'})
