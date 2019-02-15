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
    irb_type                text,
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
    inflow_shaping_rate float,
    outflow_shaping_rate float,
    remark_menu       text,
    egress_queue_menu text,
    clag_id           Integer,
    speed             text,
    irb_ipv4_address  text,
    irb_ipv4_prefix   Integer,
    virtual_mac_address text,
    virtual_gateway_address text,
    virtual_gateway_prefix  Integer,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);

CREATE TABLE LagIfInfo(
    device_name    text NOT NULL,
    lag_if_name    text NOT NULL,
    lag_type       Integer NOT NULL,
    lag_if_id      Integer NOT NULL,
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
        REFERENCES LagIfInfo(device_name,lag_if_name) ON UPDATE CASCADE,
    FOREIGN KEY (device_name,if_name)
        REFERENCES PhysicalIfInfo(device_name,if_name) ON UPDATE CASCADE
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

CREATE TABLE ACLInfo(
    device_name             text NOT NULL,
    acl_id                  int  NOT NULL,
    if_name                 text,
    vlan_id                 Integer,
    PRIMARY KEY (device_name,acl_id),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo(device_name)
);

CREATE TABLE VrfDetailInfo(
    device_name     text    NOT NULL,
    if_name         text    NOT NULL,
    vlan_id         Integer NOT NULL,
    slice_name      text    NOT NULL,
    vrf_name        text    NOT NULL,
    vrf_id          Integer, 
    rt              text    NOT NULL,
    rd              text    NOT NULL,
    router_id       text    NOT NULL,
    l3_vni          Integer,
    l3_vlan_id      Integer,
    vrf_loopback_interface_address  text,
    vrf_loopback_interface_prefix   Integer,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name),
    FOREIGN KEY (device_name, if_name, vlan_id, slice_name)
        REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name) ON UPDATE CASCADE
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
         REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name) ON UPDATE CASCADE
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
    master              boolean NOT NULL,
    remote_as_number    Integer NOT NULL,
    local_ipv4_address  text,
    remote_ipv4_address text,
    local_ipv6_address  text,
    remote_ipv6_address text,
    PRIMARY KEY (device_name, if_name, vlan_id, slice_name),
    FOREIGN KEY (device_name, if_name, vlan_id, slice_name)
        REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name) ON UPDATE CASCADE
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
        REFERENCES VlanIfInfo(device_name,if_name,vlan_id,slice_name) ON UPDATE CASCADE
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

CREATE TABLE ACLDetailInfo(
    device_name             text NOT NULL,
    acl_id                  int  NOT NULL,
    term_name               text NOT NULL,
    action                  text NOT NULL,
    direction               text NOT NULL,
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

CREATE TABLE EmSystemStatusInfo(
    service_status  Integer NOT NULL,
    PRIMARY KEY (service_status)
);

CREATE TABLE InnerLinkIfInfo(
    device_name                  text    NOT NULL,
    if_name                      text    NOT NULL,
    if_type                      Integer NOT NULL,
    vlan_id                      Integer,
    link_speed                   text,
    Internal_link_ip_address     text,
    Internal_link_ip_prefix      Integer,
    cost                         Integer,
    PRIMARY KEY (device_name, if_name),
    FOREIGN KEY (device_name)
        REFERENCES DeviceRegistrationInfo (device_name)
);


