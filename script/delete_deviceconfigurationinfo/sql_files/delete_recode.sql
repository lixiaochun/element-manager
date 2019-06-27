DELETE
FROM
    deviceconfigrationinfo AS DevConfD
USING
    (
        SELECT
            DevConfA.device_name,
            DevConfA.working_date,
            DevConfA.working_time
        FROM
            (
                SELECT
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY
                            DevConfB.device_name
                        ORDER BY
                            to_timestamp((DevConfB.working_date || DevConfB.working_time), 'YYYYMMDDHH24MISS') DESC
                    ) AS TimestampRank,
                    DevConfB.device_name,
                    DevConfB.working_date,
                    DevConfB.working_time
                FROM
                    (
                        SELECT
                            DevConfC.device_name,
                            DevConfC.working_date,
                            DevConfC.working_time
                        FROM
                            deviceconfigrationinfo AS DevConfC
                        GROUP BY
                            DevConfC.device_name,
                            DevConfC.working_date,
                            DevConfC.working_time
                    ) AS DevConfB
            ) AS DevConfA
        WHERE
            DevConfA.TimestampRank > :exist_num
    ) AS DevConfE
WHERE
    DevConfD.device_name = DevConfE.device_name
AND DevConfD.working_date = DevConfE.working_date
AND DevConfD.working_time = DevConfE.working_time
;