-- Read-only account the app connects as, so the database itself refuses writes
-- even if a query slips past src/safety.py.
CREATE USER IF NOT EXISTS 'talktodata_ro'@'%' IDENTIFIED BY 'readonly123';
GRANT SELECT ON talktodata.* TO 'talktodata_ro'@'%';
FLUSH PRIVILEGES;
