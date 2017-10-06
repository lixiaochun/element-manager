CREATE TABLE TransactionMgmtInfo (
    transaction_id      uuid PRIMARY KEY not null,
    transaction_status  integer          not null,
    service_type        integer          not null,
    order_type          integer          not null,
    order_text          Text             not null
);

CREATE TABLE DeviceRegistrationInfo(
    device_name             Text PRIMARY KEY not null,
    device_type             Integer          not null,
    platform_name           Text             not null,
    os                      Text             not null,
    firm_version            Text             not null,
    username                Text             not null,
    password                Text             not null,
    mgmt_if_address         Text             not null,
    mgmt_if_prefix          Text             not null,
    loopback_if_address     Text             not null,
    loopback_if_prefix      Text             not null,
    snmp_server_address     Text             not null,
    snmp_community          Text             not null,
    ntp_server_address      Text             not null,
    msdp_peer_address       Text,
    msdp_local_address      Text,
    as_number               Integer,
    pim_other_rp_address    Text,
    pim_self_rp_address     Text,
    pim_rp_address          Text,
    vpn_type                Integer
);

CREATE TABLE DeviceStatusMgmtInfo (
    device_name             Text         not null,
    transaction_id          uuid         not null REFERENCES TransactionMgmtInfo(transaction_id),
    transaction_status      Integer      not null,
    PRIMARY KEY(device_name,transaction_id)
);



CREATE TABLE CpInfo(
    device_name             Text      not null REFERENCES DeviceRegistrationInfo(device_name),
    if_name                 Text      not null,
    vlan_id                 Integer   not null,
    slice_name              Text      not null,
    slice_type              Integer   not null,
    port_mode               Integer,
    vni                     Integer,
    multicast_group         Text,
    ipv4_address            Text,
    ipv4_prefix             Integer,
    ipv6_address            Text,
    ipv6_prefix             Integer,
    bgp_flag                Boolean,
    ospf_flag               Boolean,
    static_flag             Boolean,
    direct_flag             Boolean,
    vrrp_flag               Boolean,
    mtu_size                Integer,
    metric                  Integer,
    PRIMARY KEY(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE MaintenancePortInfo(
    device_name             Text     not null REFERENCES DeviceRegistrationInfo(device_name),
    mainte_port_if_name     Text     not null,
    mainte_port_ip_address  Text     not null,
    mainte_port_ip_prefix   Integer  not null,
    mtu_size                Integer  not null,
    ospf_flag               Boolean,
    direct_flag             Boolean,
    vrrp_flag               Boolean,
    metric                  Integer,
    PRIMARY KEY(device_name,mainte_port_if_name)
);

CREATE TABLE LagIfInfo(
    device_name             Text     not null REFERENCES DeviceRegistrationInfo(device_name),
    lag_if_name             Text     not null,
    lag_type                Integer  not null,
    minimum_links           Integer  not null,
    link_speed              Text,
    internal_link_ip_address    Text,
    internal_link_ip_prefix Text,
    PRIMARY KEY(device_name,lag_if_name)
);

CREATE TABLE LagMemberIfInfo(
    lag_if_name             Text not null,
    if_name                 Text not null,
    device_name             Text not null,
    PRIMARY KEY(lag_if_name,if_name,device_name),
    FOREIGN KEY (device_name,lag_if_name)
        REFERENCES LagIfInfo(device_name,lag_if_name)
);

CREATE TABLE L3VpnLeafBgpBasicInfo(
    device_name             Text not null REFERENCES DeviceRegistrationInfo(device_name),
    neighbor_ipv4           Text not null,
    bgp_community_value     Text not null,
    bgp_community_wildcard  Text not null,
    PRIMARY KEY(device_name,neighbor_ipv4)
);

CREATE TABLE VrfDetailInfo(
    device_name             Text      not null,
    if_name                 Text      not null,
    vlan_id                 Integer   not null,
    slice_name              Text      not null,
    vrf_name                Text      not null,
    rt                      Text      not null,
    rd                      Text      not null,
    router_id               Text      not null,
    PRIMARY KEY(device_name,if_name,vlan_id,slice_name),
    FOREIGN KEY (device_name,if_name,vlan_id,slice_name)
        REFERENCES CpInfo(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE VrrpDetailInfo(
    device_name             Text      not null,
    if_name                 Text      not null,
    vlan_id                 Integer   not null,
    slice_name              Text      not null,
    vrrp_group_id           Integer   not null,
    virtual_ipv4_address    Text,
    virtual_ipv6_address    Text,
    priority                Integer   not null,
    PRIMARY KEY(device_name,if_name,vlan_id,slice_name),
    FOREIGN KEY (device_name,if_name,vlan_id,slice_name)
         REFERENCES CpInfo(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE MaintenancePortVrrpDetailInfo(
    device_name             Text      not null,
    mainte_port_if_name     Text      not null,
    vrrp_group_id           Integer   not null,
    virtual_ipv4_address    Text,
    priority                Integer   not null,
    PRIMARY KEY(device_name,mainte_port_if_name),
    FOREIGN KEY (device_name,mainte_port_if_name)
        REFERENCES MaintenancePortInfo(device_name,mainte_port_if_name)
);

CREATE TABLE VrrpTrackIfInfo(
    vrrp_group_id           Integer not null,
    track_if_name           Text    not null,
    PRIMARY KEY(vrrp_group_id,track_if_name)
);

CREATE TABLE BgpDetailInfo(
    device_name             Text      not null,
    if_name                 Text      not null,
    vlan_id                 Integer   not null,
    slice_name              Text      not null,
    remote_as_number        Integer   not null,
    local_ipv4_address      Text,
    remote_ipv4_address     Text,
    local_ipv6_address      Text,
    remote_ipv6_address     Text,
    PRIMARY KEY(device_name,if_name,vlan_id,slice_name),
    FOREIGN KEY (device_name,if_name,vlan_id,slice_name)
        REFERENCES CpInfo(device_name,if_name,vlan_id,slice_name)
);

CREATE TABLE StaticRouteDetailInfo(
    device_name             Text     not null,
    if_name                 Text     not null,
    vlan_id                 Integer  not null,
    slice_name              Text     not null,
    address_type            Integer  not null,
    address                 Text     not null,
    prefix                  Integer  not null,
    nexthop                 Text     not null,
    PRIMARY KEY(device_name,if_name,vlan_id,slice_name,address_type,address,prefix,nexthop),
    FOREIGN KEY (device_name,if_name,vlan_id,slice_name)
        REFERENCES CpInfo(device_name,if_name,vlan_id,slice_name)
);

