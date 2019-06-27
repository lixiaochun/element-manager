CREATE TABLE ACLInfo(
    device_name             text     NOT NULL,
    acl_id                  Integer  NOT NULL,
    if_name                 text,
    vlan_id                 Integer,
    PRIMARY KEY (device_name,acl_id),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo(device_name)
);

CREATE TABLE ACLDetailInfo(
    device_name             text     NOT NULL,
    acl_id                  Integer  NOT NULL,
    term_name               text     NOT NULL,
    action                  text     NOT NULL,
    direction               text     NOT NULL,
    source_mac_address      text,
    destination_mac_address text,
    source_ip_address       text,
    destination_ip_address  text,
    source_port  	        Integer,
    destination_port        Integer,
    protocol                text,
    acl_priority            Integer,
    PRIMARY KEY (device_name,acl_id,term_name),
    FOREIGN KEY (device_name,acl_id)
        REFERENCES ACLInfo(device_name,acl_id) ON UPDATE CASCADE
);

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

CREATE TABLE DummyVlanifInfo(
    device_name             text     NOT NULL,
    vlan_id                 Integer  NOT NULL,
    slice_name              text     NOT NULL,
    vni                     Integer,
    irb_ipv4_address        text,
    irb_ipv4_prefix         Integer,
    vrf_name                text,
    vrf_id                  Integer,
    rt                      text,
    rd                      text,
    router_id               text,
    vrf_loopback_interface_address text,
    vrf_loopback_interface_prefix  Integer,
    PRIMARY KEY (device_name,vlan_id,slice_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo(device_name)
);

CREATE TABLE MultiHomingInfo(
    device_name     text    NOT NULL,
    anycast_id      Integer NOT NULL,
    anycast_address text    NOT NULL,
    clag_if_address text    NOT NULL,
    clag_if_prefix  Integer NOT NULL,
    backup_address  text    NOT NULL,
    peer_address    text    NOT NULL,
    PRIMARY KEY (device_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo(device_name) 
);

CREATE TABLE NvrAdminPasswordMgmt(
    device_name             text    NOT NULL,
    administrator_password  text    NOT NULL,
    PRIMARY KEY (device_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

ALTER TABLE DeviceRegistrationInfo ADD COLUMN irb_type text;
ALTER TABLE DeviceRegistrationInfo ADD COLUMN q_in_q_type text;

ALTER TABLE InnerLinkIfInfo ADD COLUMN vlan_id Integer;
ALTER TABLE InnerLinkIfInfo ADD COLUMN cost Integer;

ALTER TABLE LagIfInfo ADD COLUMN condition Integer;
UPDATE LagIfInfo SET condition=1;
ALTER TABLE LagIfInfo ALTER COLUMN condition set NOT NULL;

ALTER TABLE VlanIfInfo ADD COLUMN clag_id Integer;
ALTER TABLE VlanIfInfo ADD COLUMN speed text;
ALTER TABLE VlanIfInfo ADD COLUMN irb_ipv4_address text;
ALTER TABLE VlanIfInfo ADD COLUMN irb_ipv4_prefix Integer;
ALTER TABLE VlanIfInfo ADD COLUMN virtual_mac_address text;
ALTER TABLE VlanIfInfo ADD COLUMN virtual_gateway_address text;
ALTER TABLE VlanIfInfo ADD COLUMN virtual_gateway_prefix Integer;
ALTER TABLE VlanIfInfo ADD COLUMN q_in_q boolean DEFAULT FALSE;

ALTER TABLE VrfDetailInfo ADD COLUMN vrf_id Integer;
ALTER TABLE VrfDetailInfo ADD COLUMN l3_vni Integer;
ALTER TABLE VrfDetailInfo ADD COLUMN l3_vlan_id Integer;
ALTER TABLE VrfDetailInfo ADD COLUMN vrf_loopback_interface_address text;
ALTER TABLE VrfDetailInfo ADD COLUMN vrf_loopback_interface_prefix Integer;

