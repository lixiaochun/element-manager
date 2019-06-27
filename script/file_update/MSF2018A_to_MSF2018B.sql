CREATE TABLE DeviceConfigrationinfo(
    device_configration_id  serial  NOT NULL,
    device_name             text    NOT NULL,
    working_date            text    NOT NULL,
    working_time            text    NOT NULL,
    platform_name           text    NOT NULL,
    vrf_name                text,
    practice_system         text,
    log_type                text,
    get_timing              Integer,
    config_file             text    NOT NULL,
    PRIMARY KEY (device_configration_id, working_date),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

CREATE TABLE NvrAdminPasswordMgmt(
    device_name             text    NOT NULL,
    administrator_password  text    NOT NULL,
    PRIMARY KEY (device_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

ALTER TABLE DeviceRegistrationInfo ADD COLUMN q_in_q_type text;

ALTER TABLE LagIfInfo ADD COLUMN condition Integer;
UPDATE LagIfInfo SET condition=1;
ALTER TABLE LagIfInfo ALTER COLUMN condition set NOT NULL;

ALTER TABLE VlanIfInfo ADD COLUMN q_in_q boolean DEFAULT FALSE;

