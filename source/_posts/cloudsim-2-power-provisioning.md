---
title: CloudSim 笔记（2）- 能耗节约的虚拟机调度评估
tags:
  - 服务评估
  - 云计算
date: 2016-06-24 20:21:15
---


CloudSim 的能耗模块是在 3.0 版本完善的。最早的工作可能在 2011 年到 2012 年之间，论文：
 - Anton Beloglazov, and Rajkumar Buyya, "[Optimal Online Deterministic Algorithms and Adaptive Heuristics for Energy and Performance Efficient Dynamic Consolidation of Virtual Machines in Cloud Data Centers](http://dx.doi.org/10.1002/cpe.1867)", Concurrency and Computation: Practice and Experience (CCPE), Volume 24, Issue 13, Pages: 1397-1420, John Wiley & Sons, Ltd, New York, USA, 2012

<!-- more -->

论文主要讨论了能耗和性能之间平衡的最优方法。首先阐述了单机上的 VM 迁移问题，确定单机的最佳迁移时机（用的是 offline 分析，需要全局信息）并应用竞争分析建立一个在线最优算法。然后分析多机动态迁移，分别使用竞争分析说明确定性的 online 最优算法、用平均情况说明非确定性的 online 最优算法。


相应地支持仿真实验， CloudSim 在核心程序中加入了 `org.cloudbus.cloudsim.power` 包，即虚拟机能耗仿真的包。其目录结构如下：

```
.
├── PowerDatacenter.java
├── PowerDatacenterBroker.java
├── PowerDatacenterNonPowerAware.java
├── PowerHost.java
├── PowerHostUtilizationHistory.java
├── PowerVm.java
├── PowerVmAllocationPolicyAbstract.java
├── PowerVmAllocationPolicyMigrationAbstract.java
├── PowerVmAllocationPolicyMigrationInterQuartileRange.java
├── PowerVmAllocationPolicyMigrationLocalRegression.java
├── PowerVmAllocationPolicyMigrationLocalRegressionRobust.java
├── PowerVmAllocationPolicyMigrationMedianAbsoluteDeviation.java
├── PowerVmAllocationPolicyMigrationStaticThreshold.java
├── PowerVmAllocationPolicySimple.java
├── PowerVmSelectionPolicy.java
├── PowerVmSelectionPolicyMaximumCorrelation.java
├── PowerVmSelectionPolicyMinimumMigrationTime.java
├── PowerVmSelectionPolicyMinimumUtilization.java
├── PowerVmSelectionPolicyRandomSelection.java
├── lists
│   └── PowerVmList.java
└── models
    ├── PowerModel.java
    ├── PowerModelCubic.java
    ├── PowerModelLinear.java
    ├── PowerModelSpecPower.java
    ├── PowerModelSpecPowerHpProLiantMl110G3PentiumD930.java
    ├── PowerModelSpecPowerHpProLiantMl110G4Xeon3040.java
    ├── PowerModelSpecPowerHpProLiantMl110G5Xeon3075.java
    ├── PowerModelSpecPowerIbmX3250XeonX3470.java
    ├── PowerModelSpecPowerIbmX3250XeonX3480.java
    ├── PowerModelSpecPowerIbmX3550XeonX5670.java
    ├── PowerModelSpecPowerIbmX3550XeonX5675.java
    ├── PowerModelSqrt.java
    └── PowerModelSquare.java
```

可以看出，对于能耗的模拟仿真， CloudSim 采用了一种侵入式的设计。为了获得性能参数，甚至改变了原来 CloudSim 的事件循环进行了修改。在数据收集方面，放弃了之前 CloudSim 论文发表时候用的 Sensor 类，而是采用在 `PowerDatacenter` 和 `VM` 等实体里嵌入数据收集的代码。分解起来有点费劲。

以下是简要的修改说明：
1. 实体相关：
   * 能耗数据中心（`PowerDatacenter`）：覆盖了调度更新的算法以支持能耗的计算，包括能耗调度算法的嵌入（见调度策略）、能耗收集计算两方面的更新
   * 能耗数据中心用户（`PowerDatacenterBroker`）：在处理出错上提前退出，几乎没更新
   * 能耗主机（`PowerHost`、`PowerHostUtilizationHistory`）：新增能耗模型相关的更新
   * 能耗虚拟机（`PowerVm`）：覆盖方法记录 CPU 使用历史
2. 模型：
   * 调度策略
     * 选择策略（`PowerVmSelectionPolicy`）：找出给定的 `PowerHost` 要迁移的虚拟机
     * 放置策略（`PowerVmAllocationPolicyAbstract`）：继承自 `VmAllocationPolicy`，简单实现了分配虚拟机到主机的策略，并在 `optimizeAllocation(vmList)` 方法中返回主机和虚拟机的优化配对
   * 资源利用率的能耗模型（`PowerModel`）：主要是根据资源利用率（CPU？）获取能耗

提出的几种算法：
1. 虚拟机放置（分配）择策略：主要是使用稳定估计量估计主机是否需要过载
   * 基础统计量：`MigrationInterQuartileRange`、`MigrationMedianAbsoluteDeviation`
   * 回归预测：`MigrationLocalRegression`、`MigrationLocalRegressionRobust`
   * 固定阈值判断：`MigrationStaticThreshold`
   * 不优化（对照实验）：`Simple`
2. 虚拟机选择策略：
   * 最大相关性：`MaximumCorrelation` 选择资源利用率向量的相关性最大的虚拟机进行迁移
   * 最短迁移时间：`MinimumMigrationTime` 尽可能近，并且内存尽可能少的虚拟机进行迁移
   * 最低利用率：`MinimumUtilization` 选择利用率最低的进行迁移，使性能损失减小
   * 随机选择（对照实验）：`RandomSelection`

其选择虚拟机的基础主要基于资源利用率和能耗的历史统计量。基本的算法过程可以参考论文。

现在说说我认为分析上的一些瑕疵。对于能耗的仿真，只考虑了 CPU 的消耗，这是个复杂的分析问题。如果考虑所有的能耗，可能就很难进行优化。于是，作者采用了 CPU 利用率能耗模型。这个说法，在粗粒度下，也是得到文献引证的：

- Kusic D, Kephart JO, Hanson JE, Kandasamy N, Jiang G. Power and performance management of virtualized computing environments via lookahead control. Cluster Computing 2009; 12(1):1–15.
- Fan, Xiaobo, W. D. Weber, and L. A. Barroso. "Power provisioning for a warehouse-sized computer." Acm Sigarch Computer Architecture News 35.2(2007):13-23.

于是，作者采用了简单的线性模型、二次方模型以及从 [SPECPower 2008](http://www.spec.org/power_ssj2008/) 公布的 CPU 利用率和功耗的对应表。

但是也有细分的情况，说明能耗不仅仅依靠 CPU 利用率来调整：

- Kansal, Aman, et al. "Virtual machine power metering and provisioning." Acm Symposium on Cloud Computing ACM, 2010:39-50.

但是 RAM 和 Disk 消耗在低 CPU 占用率的地方，还是会占据很大一部分的能耗。不过论文也承认，详细考虑能耗模型是一件复杂的事情。

在实验部分，在考虑“过载”这个问题上，论文和实际实现可能有一定出入。论文中，分配 CPU 的时候，总的虚拟机核心数和物理机的核心数还是一致的，而过载的定义是在所有 VM 都满负载运行。但是实际中，一台物理机可以虚拟出很多 VM，总的 VM 核数应该是大于物理机的核数，以最大化利用CPU核心。再后来修改版里，CloudSim 3.0 也引入了这样的概念。但采用的是简单的分时调度。分时调度意味着，随着 VM 的增加，每个 VM 获得的实际 MIPS 比所请求的 MIPS 少，然而 VM 在实际的调度环境中，是可以进入休眠状态而基本不消耗资源。另外一点是调度器也没有考虑优先级的问题。

在 CloudSim 3.0 里还有一个问题，不同的 CloudletScheduler 可能导致不同的过载发生，即 cloudlet 的总消耗比 VM 还高，物理机的过载可能是由于 cloudlet 越界运行导致的。我觉得在虚拟机动态迁移调度的问题上，采用 CloudletScheduler 这样细粒度的程序调度器，模拟并行调度过程会产生很多不确定的问题。
