Changelog
=========

1.1.3
-----

*fixed* Connection count statistics filtered out the connection caused by this
    munin plugin by username. This could cause incorrect counts if another
    utility would run with the same user-name as munin. We now use the client
    PID to filter out such connections which fixes that issue.

1.1.2
-----

*fixed* Statistics of IO operations fixed in ``1.1.1`` used incorrect column
    names. This is now fixed.

1.1.1
-----

*fixed* Statistics if IO operations on PostgreSQL table now uses the correct
    statistics collector.
