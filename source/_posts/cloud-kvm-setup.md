---
title: KVM 虚拟机配置
date: 2016-10-30 14:31:40
tags:
  - 云计算
  - 虚拟化
---

KVM 是一种全虚拟化技术，由 Linux 内核自身集成，市面上很多云服务提供商都是用该技术进行资源的虚拟化，也是 OpenStack 等云计算架构的虚拟化基础。很不博客列出了 KVM 的安装和使用过程，但是都不够具体，本博客在总结网络博客的基础上，收集整理自己遇到的坑，以方便大家做参考。

<!-- more -->

### 安装准备

确定物理服务器支持虚拟化技术：

```sh
grep vmx /proc/cpuinfo # Intel 系列
grep svm /proc/cpuinfo # AMD 系列
```

需要安装 Qemu、KVM 等组件：

```sh
sudo apt-get install kvm qemu qemu-kvm libvirt-bin
```

如果需要安装图形界面，还可以安装：

```sh
sudo apt-get install virt-manager
```

### 安装

进行以下操作时，请注意当前用户拥有高级的读写权限。用 virsh 创建的虚拟机，一般会赋予 kvm 用户组读写的权限，因此，可以把当前操作用户加入到 kvm 组里。更简单的办法是使用 root 来执行以下操作。

1. 新建硬盘镜像：

   ```sh
   qemu-img create -f qcow2 /var/lib/libvirt/images/test.qcow2 20G
   ```

2. 在服务器上准备好 OS 的镜像文件，例如从 http://mirrors.ustc.edu.cn 上下载。

3. 使用 virt-instal 或 virsh 进行远程安装

   1. 使用命令行的安装方式

      ```shell
      virt-install --virt-type kvm --name=test--ram=4096 --vcpus=2 \
      --os-type=linux \
      --location=/root/rhel-server-7.0-x86_64-dvd.iso \
      --disk path=/var/lib/libvirt/images/test.qcow2,format=qcow2 \
      --network bridge:virbr0 \
      --graphics none \
      --extra-args='console=tty0 console=ttyS0,115200n8 serial'
      ```

   2. 使用 VNC 的方式进行安装：

      ```shell
      virt-install --virt-type kvm --name=test --ram=1024 --vcpus=1 \
      --os-type=linux \
      --location=/root/rhel-server-7.0-x86_64-dvd.iso \
      --disk /var/lib/libvirt/images/test.qcow2,format=qcow2 \
      --network bridge:brx \
      --graphics vnc,password=123456
      ```

      显示 VNC 端口

      ```shell
      virsh vncdisplay test
      ```

      网上也有人提到 /etc/libvirt/qemu.conf 中的需要解锁

      ```ini
      # vnc_listen="0.0.0.0"
      ```

      然后重启 libvirtd 服务

      ```shell
      systemctl restart libvirtd
      ```

   3. 使用 virsh 来创建虚拟机：

      创建虚拟机描述文件，例如 ubuntu.xml ，内容如下：

      ```xml
      <domain type='kvm'>
        <name>ubuntu2</name>
        <memory>1048576</memory>
        <vcpu>1</vcpu>
        <os>
          <type arch='x86_64' machine='pc'>hvm</type>
          <boot dev='cdrom'/>
          <boot dev='hd'/>
        </os>
        <features>
          <acpi/>
          <apic/>
          <pae/>
        </features>
        <clock offset = 'localtime'/>
        <on_poweroff>destroy</on_poweroff>
        <on_reboot>restart</on_reboot>
        <on_crash>destroy</on_crash>
        <devices>
          <emulator>/usr/bin/kvm</emulator>
          <disk type='file' device='disk'>
            <driver name='qemu' type='qcow2'/>
            <source file='/home/zhi/qemu/ubuntu2.img'/>
            <target dev='hda' bus='ide'/>
          </disk>
          <disk type='file' device='cdrom'>
            <source file='/home/zhi/img/ubuntu-16.10-server-amd64.iso'/>
            <target dev='hdb' bus='ide'/>
          </disk>
          <interface type='bridge'>
            <source bridge='virbr0'/>
          </interface>
          <input type='tablet' bus='usb'/>
          <input type='mouse' bus='ps2'/>
          <graphics type ='vnc' port='-1' listen='0.0.0.0' keymap='en-us'/>
        </devices>
      </domain>
      ```

      其中需要注意编辑 device='cdrom'/device='disk'/interface 这几个标签的内容。然后执行

      ```sh
      virsh define ubuntu.xml
      ```

      即启动安装过程，可以用 VNC Viewer 进行远程安装。

   注：以上 3 个步骤选择一种进行操作即可，其作用是等价的。其中前两种需要安装 virtinst 工具。

4. 如果是通过 virbr0 这个网卡进行操作的话（默认 virbr0 是 NAT 并使用 dnsmaq 来分配 IP 地址），可以通过以下命令查看生成的虚拟机的 IP 地址：

   ```sh
   cat /var/lib/libvirt/dnsmasq/virbr0.status
   ```

   注意其中的 hostname 对应的 IP 地址。

### 启动

可以使用 virsh 来管理虚拟机，其中比较常见的命令有

```
virsh start    VM_ID  # 启动虚拟机
      shutdown VM_ID  # 关闭虚拟机
      destroy  VM_ID  # 强制关闭虚拟机
      edit     VM_ID  # 更改虚拟机的配置
```

另外一个值得一提的功能是在线迁移（live migration）。

```sh
virsh migrate  VM_ID  DEST_URI --live
```

需要注意，在线迁移需要对方 QEMU 支持，最好在两个相同版本的 QEMU 服务器之间迁移，否则容易出错。其中 DEST_URI 的写法是 qemu+ssh://IP_ADDR/system ，详细文档见 `virsh migrate --help`。

### 常见问题

1. error: internal error Attempt to migrate guest to the same host 00020003-0004-0005-0006-000700080009

   应该是服务器提供商的问题，重新生成一下 UUID ：

   ```sh
   sed -i "/#host_uuid/ahost_uuid = \"`uuidgen`\"" /etc/libvirt/libvirtd.conf
   ```

   然后重启 libvirtd 服务：

   ```sh
   service libvirt-bin restart
   ```

2. error: internal error: process exited while connecting to monitor: qemu-system-x86_64: -machine pc-i440fx-2.2,accel=kvm,usb=off: Unsupported machine type

   这个错误在动态迁移（在线迁移，live migration）的时候会遇到，接收方的 QEMU 版本较低，不支持该版本的虚拟机。

3. Cannot recv data: Value too large for defined data type

   很可能是因为调用的某个程序、某个库出现错误了，因为这个错误很广泛。我当时遇到这个问题是因为 ssh 的钥匙没配置好。建议重新生成秘钥。
