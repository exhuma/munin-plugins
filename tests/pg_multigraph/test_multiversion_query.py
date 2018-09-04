'''
Unit Tests for multiversioned queries for pg_multigraph
'''
# pylint: disable=redefined-outer-name
#
# pytest relies on having the same outer-name for fixtures.

from imp import load_source

import pytest


@pytest.fixture
def pgmg():
    '''
    The script is a monolithic executable without a .py exension so normal
    importing wont work and we need to use load_source.

    To simplify this, we wrap it in a fixture.
    '''
    pgmg = load_source('pgmg', 'pg_multigraph')
    return pgmg


@pytest.fixture
def mv_query(pgmg):
    '''
    Create a fake new multi-versioned query and returns the instance.
    '''
    class FakeQuery(pgmg.MultiVersionQuery):

        VARIANTS = {
            (1, 0, 0): 'foo-100',
            (2, 0, 0): 'foo-200',
            (3, 0, 0): 'foo-300',
        }

    return FakeQuery()


def test_min(mv_query):
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    result = mv_query.get((1, 0, 0))
    assert result == 'foo-100'


def test_mid(mv_query):
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    result = mv_query.get((2, 0, 0))
    assert result == 'foo-200'


def test_max(mv_query):
    '''
    Retrieving a query with the exact version than one of the defined versions
    should return that value.
    '''
    result = mv_query.get((3, 0, 0))
    assert result == 'foo-300'


def test_below_min(mv_query):
    '''
    Retrieving a query with a version lower than any defined version should
    return an empty value.
    '''
    result = mv_query.get((0, 5, 0))
    assert result == ''


def test_between_versions(mv_query):
    '''
    Retrieving a query with a version larger laying between two defined
    versions should return the next *lower* one.
    '''
    result = mv_query.get((2, 1, 0))
    assert result == 'foo-200'


def test_after_max(mv_query):
    '''
    Retrieving a query with a version larger than any specified version should
    return the latest value.
    '''
    result = mv_query.get((4, 0, 0))
    assert result == 'foo-300'
