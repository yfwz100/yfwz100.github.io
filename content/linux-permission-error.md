Title: 记一次 Linux 权限故障
Date: 2016-05-26 23:10
Category: 杂记
Tags: Linux
Slug: articles/linux/permission-error
Author: yfwz100
Summary: 记一次误操作导致的全线故障。

想起今天的误操作还真的心有余悸，差点就要重新安装系统了。缘起想改变 `/data` 这个目录的所有者，结果手误运行了 `sudo chown zhi:zhi /` ，导致整个系统的权限都重置为当前用户 zhi ！这样会导致什么问题？看看这篇讨论： [AskUbuntu: sudo 权限错误][] ，会导致 `sudo` 命令无法执行、 SSH 服务器停止响应，无法安装软件，无法远程登录。糟糕的是，这台服务器还是一台远程主机，我无法直接重装系统或者进入“recovery mode”修复 root 权限。想着今天做的基础设施就要报废了，心里真不是滋味。

要解决这个问题，首先要从恢复最高管理员权限开始。由于现代 Linux 系统，例如 Ubuntu 系，都已经采用 `sudo` 方案并设置 root 密码为随机密码，直接 su 切换到 root 并不现实。而直接运行 `sudo` ，则会出现：

```
sudo: /usr/bin/sudo must be owned by uid 0
```

这个错误，多半是由于手误把 `/usr` 目录或者子目录的权限改变导致的了。

解决的思路很简单，就是把 `/usr/bin/sudo` 这个命令的权限复原。一种方法是进入 recovery mode，这种模式下，基本上可以随心所欲了，详情参见 [AskUbuntu: sudo 权限错误][] 。但是如果是远程主机，就没那么好办了。那么我们需要找到一些漏洞。而我这次是从 `/data` 这个共享的 NFS 目录开始的（幸亏 **之前搭建 NFS 的时候没有设置权限** ，否则可能无法挂载了）。

由于 NFS 共享目录可以保留权限，使用 **另一台机器** 挂载这个 NFS 目录，并且执行：

```
$ sudo cp -a /usr/bin/sudo /data
$ sudo cp -a /usr/lib/sudo/* /data
```

得到保留所有权限信息的 `sudo` 命令以及相关的库文件。

然后在原来的主机上，执行：

```
$ rm /usr/bin/sudo
$ mv /usr/lib/sudo /usr/local/lib/sudo.bak
$ ln -s /data /usr/lib/sudo
```

先删除 `/usr/bin/sudo` ，然后把 `/usr/lib` 目录用 `/data` 取代。由于运行 `sudo` 命令实际上会连接调用 `/usr/lib/sudo` 目录下的库，并且会检查库文件的权限，但是不检查 `/usr/lib/sudo` 目录的形式和权限，感觉这是个漏洞。但不管怎样，现在执行：

```
$ /data/sudo
```

成功了！

接下来就是一步步地利用 `/data/sudo` 命令恢复 `/usr/bin/sudo` 以及 `/usr/lib/sudo` 了：

```
$ /data/sudo cp -a /data/sudo /usr/bin/sudo
$ /data/sudo chown -R root:root /usr/lib/sudo.bak
$ /data/sudo cp -a /usr/lib/sudo.bak /usr/lib/sudo
```

至此，`sudo` 命令恢复完毕。接下来就是对照着原来的 Ubuntu，把其余权限错误的目录恢复为原来的权限了。其中一个至关重要的权限：

```
$ sudo chown -R root:root /var/run/ssh*
```

恢复 SSH 服务，使得在断线后还可以重新连接（切记，因为网络状态不是谁都可以预料的 😓）。其余命令，参考 [AskUbuntu: 恢复 /* 目录权限][]

[AskUbuntu: sudo 权限错误]: http://askubuntu.com/questions/452860/usr-bin-sudo-must-be-owned-by-uid-0-and-have-the-setuid-bit-set
[AskUbuntu: 恢复 /* 目录权限]: http://askubuntu.com/questions/265080/how-can-i-recover-from-chmod-r-a-wrx-command
