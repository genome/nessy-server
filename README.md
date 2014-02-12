# REST-Based Locking Service

[![Build Status](https://travis-ci.org/genome/nessy-server.png?branch=master)](https://travis-ci.org/genome/nessy-server)
[![Coverage Status](https://coveralls.io/repos/genome/nessy-server/badge.png?branch=master)](https://coveralls.io/r/genome/nessy-server?branch=master)

The purpose of this project is to provide a replacement for the network disk
based locking system currently in place in the
[Genome Modeling System](https://github.com/genome/gms-core).

## Testing

First, you should have a [Postgres](http://www.postgresql.org/) server running
somewhere with a database already created.  You can specify the
[sqlalchemy](http://http://www.sqlalchemy.org/) connection string to use for
testing with the `LOCKING_TEST_DB` environment variable (the default is
`postgres://postgres@localhost/locking_test`).

Once Postgres is setup, run the tests using tox:

    pip install tox
    tox

Note that [SQLite](https://sqlite.org/) is not supported, due to weak DATETIME
subtraction features.
