'''
Unit Tests for pg_multigraph.
'''
# pylint: disable=redefined-outer-name
#
# pytest relies on having the same outer-name for fixtures.

from imp import load_source

import pytest


@pytest.fixture
def pgmg():
    '''
    Dynamically loads the module.

    As it has no ".py" extension it cannot be loaded using a normal "import"
    statement.
    '''
    return load_source('pgmg', 'pg_multigraph')


def test_min(pgmg):
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (1, 0, 0))
    assert result == {'foo': 'foo-100'}


def test_mid(pgmg):
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (2, 0, 0))
    assert result == {'foo': 'foo-200'}


def test_max(pgmg):
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (3, 0, 0))
    assert result == {'foo': 'foo-300'}


def test_below_min(pgmg):
    '''
    Retrieving a query with a version lower than any defined version should
    return an empty value.
    '''
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (0, 5, 0))
    assert result == {}


def test_between_versions(pgmg):
    '''
    Retrieving a query with a version larger laying between two defined
    versions should return the next *lower* one.
    '''
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (2, 1, 0))
    assert result == {'foo': 'foo-200'}


def test_after_max(pgmg):
    '''
    Retrieving a query with a version larger than any specified version should
    return the latest value.
    '''
    queries = {
        'foo': {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }
    }
    result = pgmg.queries_for_version(queries, (4, 0, 0))
    assert result == {'foo': 'foo-300'}
