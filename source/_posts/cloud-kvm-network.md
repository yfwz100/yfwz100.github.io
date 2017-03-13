---
title: KVM 以及桥接网络配置
date: 2016-10-30 15:21:24
tags:
  - 云计算
  - 虚拟化
---

最近在折腾 KVM 以及虚拟化，KVM安装后默认的网络链接方式是NAT，此时虚拟机虽然可以与本机通信，但虚拟机的IP地址是一个私有地址，本机外的网络无法访问该虚拟机。

<!-- more -->

### 虚拟机网络连接的方式

接触过 VirtualBox、VMware 的话，对虚拟机网络配置肯定不会陌生。虚拟机网络连接常见的有 3 种方式：

1. NAT 网络：即内部地址转换，相当于从物理网卡外接了一个虚拟的路由，然后所有虚拟机都连接到该“路由器”上，虚拟机可以借助这个路由器访问到外面的网络，但外面的网络却无法访问，因为虚拟机的地址只是路由器上唯一的，出了路由器就不再唯一了。
2. 桥接网络：也叫物理设备共享，相当于虚拟了一个和服务网卡一样的网卡，这个虚拟网卡和物理网卡是平行的关系，并且虚拟机共用物理网卡额资源。这样，虚拟机能够接入外部网络，不受物理机的限制了。
3. Host-Only 网络：与 NAT 类似，但是比 NAT 更封闭，只有物理机能够访问该虚拟机，其他虚拟机也不能访问。

一般安装 KVM 后都会安装 bridge-util，这是 Linux 下用于桥接网卡的工具集，通过该工具集可以虚拟出一个新的网卡。其中， bridge-util 安装后会自动建立一个 NAT 网络，即 virbr0 网卡，如果虚拟机连接到该网卡上，则连接到 NAT 网络了。而下文主要介绍建立桥接网络的做法。

### 桥接网络的建立

1. 新建虚拟网桥

   编辑 /etc/network/interfaces 文件，根据以下两种情况的一种添加如下内容：

   1. 假设外部网络是一个 DHCP 动态分配 IP 的网络环境，并且网卡名字为 eth0 ：

      ```
      auto br0
      iface br0 inet dhcp
      bridge_ports eth0
      bridge_stp off
      bridge_fd 0
      ```

      其中第一句话建立了虚拟网桥 br0，并且该接口使用 DHCP 分配 IP 等信息，后三句是配置网桥相关的属性。bridge_ports 配置了该网桥连接到的虚拟网卡 eth0，并关闭 [stp（生成树协议）](http://baike.baidu.com/link?url=wa8X56FKMcQ00SxYDZZmEFvetw-FI83bKa3pnHs62KLbGWEGz0rMKPM6xGY0aW0qRYpUc7cQaui3sCxkDXwJ8IrjgVd4rbZaqOfVnDmv4wO)，设置 fd（forwarding delay，转发延迟） 为 0 。

   2. 假设外部网络是静态分配的网络，并且网卡名字为 eth0 ：

      ```
      auto br0
      iface br0 inet static
      address 192.168.200.130
      network 192.168.200.0
      netmask 255.255.255.0
      broadcast 192.168.200.255
      gateway 192.168.200.1
      dns-nameservers 8.8.8.8
      bridge_ports eth0
      bridge_stp off
      bridge_fd 0
      bridge_maxwait 0
      ```

      需要在文件中编辑 address/network/netmask/broadcast/gateway/dsn-nameservers 等内容。

2. 重新启动网络服务（以 Ubuntu 为例）：

   ```sh
   service networking restart
   ```

3. 为 KVM 虚拟机配置网络，编辑虚拟机配置文件：

   ```sh
   virsh edit VM_ID
   ```

   文件示意如下：

   ```xml
   <interface type='...'>
     <mac address='...'/>
     <source bridge='...'/>
     <model type='rtl8139'/>
     <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
   </interface>
   ```

   把其中 type 改为 bridge，并且 source 标签中的 bridge 属性改为 br0 。

   重启虚拟机。
