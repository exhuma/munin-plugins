'''
Unit Tests for pg_multigraph.
'''

from imp import load_source


def test_min():
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    pgmg = load_source('pgmg', 'pg_multigraph')
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (1, 0, 0))
    assert result == {'foo': 'foo-100'}


def test_mid():
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    pgmg = load_source('pgmg', 'pg_multigraph')
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (2, 0, 0))
    assert result == {'foo': 'foo-200'}


def test_max():
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    pgmg = load_source('pgmg', 'pg_multigraph')
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (3, 0, 0))
    assert result == {'foo': 'foo-300'}


def test_below_min():
    '''
    Retrieving a query with a version lower than any defined version should
    return an empty value.
    '''
    pgmg = load_source('pgmg', 'pg_multigraph')
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (0, 5, 0))
    assert result == {}


def test_between_versions():
    '''
    Retrieving a query with a version larger laying between two defined
    versions should return the next *lower* one.
    '''
    pgmg = load_source('pgmg', 'pg_multigraph')
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (2, 1, 0))
    assert result == {'foo': 'foo-200'}


def test_after_max():
    '''
    Retrieving a query with a version larger than any specified version should
    return the latest value.
    '''
    pgmg = load_source('pgmg', 'pg_multigraph')
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (4, 0, 0))
    assert result == {'foo': 'foo-300'}
