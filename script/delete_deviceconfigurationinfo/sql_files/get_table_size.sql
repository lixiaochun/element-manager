SELECT
    pg_table_size(oid) as tablesize
FROM
    pg_class
WHERE
    relname = 'deviceconfigrationinfo'
;