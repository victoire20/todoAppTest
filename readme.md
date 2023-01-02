# We can change show mode sqlite3
- column
- markdown
- box
- table

# Alembic command
- alembic init <folder name> (initialize a new, generic environment)
- alembic revision -m <message> (create a new revision of the environment)
- alembic upgrade <revision #> (run our upgrade migration to our database)
- alembic downgrade <revision #> (run our downgrade migrate to our database)