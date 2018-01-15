CREATE TABLE TransactionMgmtInfo(
    transaction_id     uuid     NOT NULL,
    transaction_status Integer  NOT NULL,
    service_type       Integer  NOT NULL,
    order_type         Integer  NOT NULL,
    order_text         text     NOT NULL,
    PRIMARY KEY (transaction_id)
);

CREATE TABLE DeviceStatusMgmtInfo(
    device_name        text    NOT NULL,
    transaction_id     uuid    NOT NULL,
    transaction_status Integer NOT NULL,
    PRIMARY KEY (device_name, transaction_id),
    FOREIGN KEY (transaction_id)
        REFERENCES TransactionMgmtInfo(transaction_id)
);

CREATE TABLE DeviceRegistrationInfo(
    device_name             text     NOT NULL,
    device_type             Integer  NOT NULL,
    platform_name           text     NOT NULL,
    os                      text     NOT NULL,
    firm_version            text     NOT NULL,
    username                text     NOT NULL,
    password                text     NOT NULL,
    mgmt_if_address         text     NOT NULL,
    mgmt_if_prefix          Integer  NOT NULL,
    loopback_if_address     text     NOT NULL,
    loopback_if_prefix      Integer  NOT NULL,
    snmp_server_address     text     NOT NULL,
    snmp_community          text     NOT NULL,
    ntp_server_address      text     NOT NULL,
    as_number               Integer,
    pim_other_rp_address    text,
    pim_self_rp_address     text,
    pim_rp_address          text,
    vpn_type                Integer,
    virtual_link_id         text,
    ospf_range_area_address text,
    ospf_range_area_prefix  Integer,
    cluster_ospf_area       text,
    rr_loopback_address     text,
    rr_loopback_prefix      Integer,
    PRIMARY KEY (device_name)
);

CREATE TABLE PhysicalIfInfo(
    device_name text NOT NULL,
    if_name     text NOT NULL,
    condition   Integer DEFAULT 1 NOT NULL,
    PRIMARY KEY (device_name, if_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

CREATE TABLE VlanIfInfo(
    device_name       text    NOT NULL,
    if_name           text    NOT NULL,
    vlan_id           Integer NOT NULL,
    slice_name        text    NOT NULL,
    slice_type        Integer NOT NULL,
    port_mode         Integer,
    vni               Integer,
    multicast_group   text,
    ipv4_address      text,
    ipv4_prefix       Integer,
    ipv6_address      text,
    ipv6_prefix       Integer,
    bgp_flag          boolean,
    ospf_flag         boolean,
    static_flag       boolean,
    direct_flag       boolean,
    vrrp_flag         boolean,
    mtu_size          Integer,
    metric            Integer,
    esi               text,
    system_id         text,
    shaping_rate      float,
    remark_menu       text,
    egress_queue_menu text,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

CREATE TABLE LagIfInfo(
    device_name    text NOT NULL,
    lag_if_name    text NOT NULL,
    lag_type       Integer NOT NULL,
    minimum_links  Integer NOT NULL,
    link_speed     text,
    PRIMARY KEY (device_name, lag_if_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo(device_name)
);

CREATE TABLE LagMemberIfInfo(
    device_name    text NOT NULL,
    lag_if_name    text NOT NULL,
    if_name        text NOT NULL,
    PRIMARY KEY (device_name, lag_if_name, if_name),
    FOREIGN KEY (device_name,lag_if_name)
        REFERENCES LagIfInfo(device_name,lag_if_name),
    FOREIGN KEY (device_name,if_name)
        REFERENCES PhysicalIfInfo(device_name,if_name)
);

CREATE TABLE L3VpnLeafBgpBasicInfo(
    device_name             text NOT NULL,
    neighbor_ipv4           text NOT NULL,
    bgp_community_value     text,
    bgp_community_wildcard  text,
    PRIMARY KEY (device_name, neighbor_ipv4),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo(device_name)
);

CREATE TABLE VrfDetailInfo(
    device_name     text    NOT NULL,
    if_name         text    NOT NULL,
    vlan_id         Integer NOT NULL,
    slice_name      text    NOT NULL,
    vrf_name        text    NOT NULL,
    rt              text    NOT NULL,
    rd              text    NOT NULL,
    router_id       text    NOT NULL,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name),
    FOREIGN KEY (device_name, if_name, vlan_id, slice_name)
        REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE VrrpDetailInfo(
    device_name          text NOT NULL,
    if_name              text NOT NULL,
    vlan_id              Integer NOT NULL,
    slice_name           text NOT NULL,
    vrrp_group_id        Integer NOT NULL,
    virtual_ipv4_address text,
    virtual_ipv6_address text,
    priority             Integer NOT NULL,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name),
    FOREIGN KEY (device_name, if_name, vlan_id, slice_name)
         REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE VrrpTrackIfInfo(
    vrrp_group_id   Integer NOT NULL,
    track_if_name   text    NOT NULL,
    PRIMARY KEY (vrrp_group_id, track_if_name)
);

CREATE TABLE BgpDetailInfo(
    device_name         text    NOT NULL,
    if_name             text    NOT NULL,
    vlan_id             Integer NOT NULL,
    slice_name          text    NOT NULL,
    remote_as_number    Integer NOT NULL,
    local_ipv4_address  text,
    remote_ipv4_address text,
    local_ipv6_address  text,
    remote_ipv6_address text,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name),
    FOREIGN KEY (device_name, if_name, vlan_id, slice_name)
        REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE StaticRouteDetailInfo(
    device_name  text    NOT NULL,
    if_name      text    NOT NULL,
    vlan_id      Integer NOT NULL,
    slice_name   text    NOT NULL,
    address_type Integer NOT NULL,
    address      text    NOT NULL,
    prefix       Integer NOT NULL,
    nexthop      text    NOT NULL,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name, address_type, address, prefix, nexthop),
    FOREIGN KEY (device_name,if_name,vlan_id,slice_name)
        REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE BreakoutIfInfo(
    device_name        text    NOT NULL,
    base_Interface     text    NOT NULL,
    speed              text    NOT NULL,
    breakout_num       Integer NOT NULL,
    PRIMARY KEY (device_name, base_Interface),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

CREATE TABLE ClusterLinkIfInfo(
    device_name             text    NOT NULL,
    if_name                 text    NOT NULL,
    if_type                 Integer NOT NULL,
    cluster_link_ip_address text,
    cluster_link_ip_prefix  Integer,
    igp_cost                Integer,
    PRIMARY KEY (device_name, if_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

CREATE TABLE EmSystemStatusInfo(
    service_status  Integer NOT NULL,
    PRIMARY KEY (service_status)
);

CREATE TABLE InnerLinkIfInfo(
    device_name                  text    NOT NULL,
    if_name                      text    NOT NULL,
    if_type                      Integer NOT NULL,
    link_speed                   text,
    Internal_link_ip_address     text,
    Internal_link_ip_prefix      Integer,
    PRIMARY KEY (device_name, if_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

