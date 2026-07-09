# 成员 C — Simulation 模块四天冲刺任务清单

> **适用时间**：2026-07-07（周二）至 2026-07-10（周五）
> **负责模块**：`hospital_team1/simulation/`
> **答辩核心三问**：① 病人怎么调度？ ② 等待/开始时间怎么算？ ③ 合规率怎么判断？

---

## 一、当前 simulation/ 代码现状

| 文件 | 行数 | 作用 | 存在的问题 |
|------|------|------|-----------|
| `shift_simulation.py` | 207 | **核心**：离散事件仿真引擎 | 手写 list.sort 排序，未复用 Part 1 的 PriorityQueue |
| `compliance.py` | 14 | 判断等待时间是否合规 | **阈值数据与 `models/patient.py` 完全重复** |
| `engine.py` | 28 | 薄封装层 | 价值不大，可考虑合并或删除 |
| `report.py` | 28 | 从仿真结果生成统计摘要 | 功能正确，0 除边界未处理 |
| `__init__.py` | 4 | 导出符号 | OK |

### 与 simulation 相关的依赖

| 依赖模块 | 作用 | 注意事项 |
|----------|------|----------|
| `queues/base.py` → `PriorityQueue` ABC | 优先队列抽象基类 | simulation 目前**没有用**它，需要接入 |
| `queues/heap_priority_queue.py` | 堆实现的优先队列 | 第 2 天会统一改用自写 heap |
| `queues/ordered_linked_priority_queue.py` | 有序链表实现的优先队列 | 作为对比实现保留 |
| `models/patient.py` → `Patient.get_max_allowed_wait()` | 唯一的合规阈值数据源 | `compliance.py` 不应自己维护一份 |
| `data/csv_loader.py` | 从 CSV 加载病人列表 | `engine.py` 用它加载数据 |

---

## 二、第 1 天（7/7 周二）：理解 + 清理

> **全组目标**：缩小 Part 1，确定最终结构，删重复和部署内容
> **你的个人交付**：读懂核心代码 + 修复 compliance.py 重复 + 确认删除清单

### 任务 1.1：逐行读懂 `shift_simulation.py`（约 30 分钟）

这是你答辩最核心的文件，必须彻底理解。

#### `build_queue_snapshot()` 算法流程

```
输入：patients（所有病人）, snapshot_time（观测时刻）, workstation_count（工作站数）
输出：records, waiting_patients, in_service_patients, station_available_times

Step 1: 筛选 snapshot_time 之前到达的病人，按到达时间排序
Step 2: 初始化 station_available_times = [shift_start] × workstation_count
Step 3: 离散事件循环（事件 = 病人到达 或 工作站空闲）
        ├─ 到达事件 → 新病人加入 waiting 列表
        │   ├─ CRITICAL：立即治疗，等待时间 = 0
        │   └─ 其他级别：放入 waiting，按 (emergency_rank, triage.value, arrival_time) 排序
        └─ 空闲事件 → 从 waiting 取队首病人，分配工作站
Step 4: 返回结果
```

#### 关键计算

| 变量 | 公式 | 代码位置 |
|------|------|----------|
| 等待时间 | `(treatment_start_time - patient.arrival_time) / 60` 分钟 | `_build_record()` |
| 合规判断 | `wait_minutes <= patient.get_max_allowed_wait()` | `_build_record()` |
| 治疗结束时间 | `treatment_start_time + estimated_treatment_minutes` | `_record_end_time()` |
| 工作站最早可用时间规范化 | 多工作站时间对齐 | `_normalise_station_times()` |

#### `project_waiting_starts()` 预估逻辑

```
输入：waiting_patients, current_time, station_available_times
输出：每个等待病人的预计治疗开始时间

按优先队列顺序为每个等待病人分配未来可用的工作站槽位
```

#### `run_shift_simulation()` 顶层接口

```python
run_shift_simulation(patients, slot_interval, workstation_count)
→ {records, untreated, slot_interval, shift_start, shift_end}
```

---

### 任务 1.2：修复 `compliance.py` 的重复数据

**问题**：`compliance.py` 自己维护了一份 `SERVICE_LIMIT_MINUTES` 字典，与 `models/patient.py` 的 `get_max_allowed_wait()` **完全重复**。老师明确要求"删掉讲不清楚的重复模块和内容"。

**当前代码**（`compliance.py`）：
```python
SERVICE_LIMIT_MINUTES = {
    TriageLevel.CRITICAL: 0,
    TriageLevel.URGENT: 20,
    TriageLevel.SEMI_URGENT: 35,
    TriageLevel.NON_URGENT: 60,
}

def is_wait_time_compliant(triage_level, wait_minutes):
    return wait_minutes <= SERVICE_LIMIT_MINUTES[triage_level]
```

**目标代码**：
```python
from hospital_team1.models.patient import Patient

def is_wait_time_compliant(patient: Patient, wait_minutes: float) -> bool:
    """判断某病人的等待时间是否在其分诊级别的允许范围内。"""
    return wait_minutes <= patient.get_max_allowed_wait()
```

**注意事项**：
- 函数签名从 `(triage_level, wait_minutes)` 改为 `(patient, wait_minutes)`
- 需要同步更新 `shift_simulation.py` 中 `_build_record()` 的调用方
- `_build_record()` 目前直接用 `patient.get_max_allowed_wait()`，**不经过 `is_wait_time_compliant()`**——检查一下是否需要统一调用

---

### 任务 1.3：与协调人确认删除清单

以下内容需要你确认并提出建议：

| 待确认项 | 建议 | 理由 |
|----------|------|------|
| `engine.py` | **建议删除或合并到 `shift_simulation.py`** | 只有 28 行，薄封装无实质价值 |
| `compliance.py` 重复字典 | **必删** | 老师明确要求，且与 `patient.py` 重复 |
| `work/` 目录（4 份快照） | **建议删除** | 已在 .gitignore，不在版本控制中，约 70 个文件 |

---

## 三、第 2 天（7/8 周三）：接入统一队列 + 压实接口

> **全组目标**：统一自写 heap，补抽象基类，补队列测试
> **你的个人交付**：让 simulation 用上 PriorityQueue ABC

### 任务 2.1：用 PriorityQueue 替代手写排序

**当前问题**：`build_queue_snapshot()` 用 `list.sort(key=_queue_sort_key)` 手动管理等待队列，没有复用 Part 1 的优先队列。

**目标架构**：
```
之前：waiting = [] → waiting.sort(key=_queue_sort_key) → waiting.pop(0)
之后：waiting: PriorityQueue = HeapPriorityQueue() → waiting.enqueue(p) → waiting.dequeue()
```

**具体改动位置**（`shift_simulation.py`）：

```python
# 改造前
waiting = []
waiting.append(patient)
waiting.sort(key=_queue_sort_key)

# 改造后
from hospital_team1.queues.base import PriorityQueue
from hospital_team1.queues.heap_priority_queue import HeapPriorityQueue

waiting: PriorityQueue = HeapPriorityQueue()
waiting.enqueue(patient)
```

### 任务 2.2：验证两种实现排序一致性

**核心问题**：`_queue_sort_key` 和 `Patient.__lt__` 的排序逻辑等价吗？

| 比较维度 | `_queue_sort_key` | `Patient.__lt__` |
|----------|-------------------|-------------------|
| 危重优先 | `emergency_rank`: CRITICAL=0, 其他=1 | 无此维度（用 triage.value，CRITICAL=1 天然最小） |
| 分诊级别 | `triage_level.value` | `triage_level.value` |
| 到达时间 | `arrival_time` | `arrival_time` |

**结论**：危重病人已在到达时立即治疗，不进入 waiting 队列，所以 waiting 中只有非危重病人。在非危重范围内，两者排序等价。

**关键验证**：用相同的病人列表，分别跑 `HeapPriorityQueue` 和 `OrderedLinkedPriorityQueue`，确认 dequeue 顺序一致（成员 B 的第 2 天交付会包含这个测试）。

### 任务 2.3：列一个 simulation 对队列的依赖清单给成员 B

你需要队列提供的接口：

| 方法 | 用途 | simulation 中调用位置 |
|------|------|----------------------|
| `enqueue(patient)` | 病人进入等待队列 | 到达事件处理 |
| `dequeue()` | 取出下一个治疗的病人 | 工作站空闲事件处理 |
| `peek()` | 查看队首病人（不取出） | 可选，用于调试/日志 |
| `is_empty()` | 判断队列是否为空 | 事件循环条件判断 |
| `__len__()` | 队列当前长度 | 统计等待人数 |

这些接口在 `queues/base.py` 中已定义，确保成员 B 不会改掉。

---

## 四、第 3 天（7/9 周三）：写 simulation 专项测试

> **全组目标**：四个人各写各的模块和测试，独立建分支和提交
> **你的个人交付**：仿真引擎的完整边界测试套件

### 任务 3.1：创建测试文件

创建目录和文件（仿照 `tests/test_models/` 的结构）：

```
tests/test_simulation/
├── __init__.py
├── test_compliance.py          # 合规判断测试
├── test_shift_simulation.py    # 核心仿真引擎测试
└── test_report.py              # 报告生成测试
```

### 任务 3.2：`test_compliance.py` — 合规判断测试

| # | 场景 | 输入 | 期望输出 |
|---|------|------|----------|
| 1 | 危重零等待合规 | CRITICAL, 0 min | `True` |
| 2 | 危重超时不合规 | CRITICAL, 1 min | `False` |
| 3 | 紧急刚好合规 | URGENT, 20 min | `True` |
| 4 | 紧急超时不合规 | URGENT, 21 min | `False` |
| 5 | 半紧急刚好合规 | SEMI_URGENT, 35 min | `True` |
| 6 | 半紧急超时不合规 | SEMI_URGENT, 36 min | `False` |
| 7 | 非紧急刚好合规 | NON_URGENT, 60 min | `True` |
| 8 | 非紧急超时不合规 | NON_URGENT, 61 min | `False` |
| 9 | 浮点数边界 | URGENT, 20.0 min | `True` |
| 10 | 浮点数超一点点 | URGENT, 20.001 min | `False` |

### 任务 3.3：`test_shift_simulation.py` — 核心仿真引擎测试

| # | 场景 | 输入 | 关键断言 |
|---|------|------|----------|
| 1 | **空病人列表** | `patients=[]` | `treated_patients=0`, `untreated=0` |
| 2 | **单个危重病人** | 1 CRITICAL, arrival 08:00 | `wait_minutes=0`, `within_threshold=True` |
| 3 | **单个普通病人** | 1 NON_URGENT, arrival 08:00 | `treated=1`, 工作站空闲所以等待=0 |
| 4 | **相同优先级，不同到达** | 2 URGENT, 08:00 和 08:10 | 先到先治（records 顺序验证） |
| 5 | **不同优先级，同时到达** | 1 URGENT + 1 NON_URGENT, 同 08:00 | URGENT 先治 |
| 6 | **工作站全满** | 4 病人同时到达, 3 工作站 | 3 in_service + 1 waiting |
| 7 | **危重插队** | NON_URGENT 正在治疗中，CRITICAL 到达 | CRITICAL 立即治疗，wait=0 |
| 8 | **合规边界：刚好** | NON_URGENT 到治疗时正好等 60 min | `within_threshold=True` |
| 9 | **不合规：超 1 分钟** | NON_URGENT 等 61 min | `within_threshold=False` |
| 10 | **shift 结束后未治疗** | 病人到达太晚，shift 结束前没排到 | `untreated > 0` |
| 11 | **project_waiting_starts：空队列** | `waiting_patients=[]` | 返回空列表/空字典 |
| 12 | **project_waiting_starts：有等待** | 2 个在 waiting | 预计时间合理（不早于 current_time） |
| 13 | **run_shift_simulation：8 小时班次** | 正常数据集 | shift_end - shift_start = 8 小时 |

### 任务 3.4：`test_report.py` — 报告生成测试

| # | 场景 | 关键断言 |
|---|------|----------|
| 1 | **空仿真结果**（0 treated） | compliance_rate 不为 None/不崩 |
| 2 | **全部合规** | `compliance_rate = 100.0` |
| 3 | **一半合规** | `compliance_rate = 50.0` |
| 4 | **全部不合规** | `compliance_rate = 0.0` |
| 5 | **avg_wait 计算正确** | 已知两个病人等 10 和 20 min → avg = 15.0 |
| 6 | **max_wait 正确** | 等最久的那个 |
| 7 | **untreated 人数正确** | 和输入一致 |

### 任务 3.5：独立建分支 + 提交

```bash
git checkout -b simulation-member-c
# 写代码和测试...
git add tests/test_simulation/ hospital_team1/simulation/
git commit -m "成员C: 修复compliance重复 + 接入PriorityQueue + 补充仿真测试"
git push origin simulation-member-c
```

---

## 五、第 4 天（7/10 周四）：合并、报告、演练

> **全组目标**：只合并能讲清楚的内容，重写报告，完整答辩演练
> **你的个人交付**：三个答辩问题的讲稿 + 现场演示

### 任务 4.1：准备答辩讲稿（必须脱稿）

#### Q1：病人怎么调度的？

> "我们实现了一个离散事件仿真引擎，核心是 `build_queue_snapshot()` 函数。
>
> 它模拟一个急诊班次（8 小时）内的病人流动。时间以分钟为单位推进，有两类事件驱动：
> - **病人到达事件**：危重病人（CRITICAL）到达即治疗，等待时间为 0；其他病人进入优先队列等待。
> - **工作站空闲事件**：从优先队列头部取出优先级最高的等待病人分配治疗。
>
> 优先级排序规则：分诊级别高的优先（URGENT > SEMI_URGENT > NON_URGENT），同级别按到达时间先到先治。
>
> 这个优先队列复用了我们 Part 1 的 `PriorityQueue` 抽象基类和两种实现（堆和有序链表），保证两种实现下调度结果完全一致。"

#### Q2：等待/开始时间怎么算的？

> "治疗开始时间减去病人到达时间，就是等待时间，单位是分钟。具体在 `_build_record()` 函数里计算。
>
> 危重病人的等待时间强制为 0——因为规定必须立即救治。
>
> 对于班次结束时还在排队的病人，我们有一个 `project_waiting_starts()` 函数，它基于当前工作站可用时间来预估每个等待病人的未来治疗开始时间——这在分析模块中被用来预测超时风险。
>
> 工作站可用时间用 `_normalise_station_times()` 规范化，保证多工作站的时间轴对齐。"

#### Q3：合规率怎么判断的？

> "每个分诊级别有法定的最长等待时间标准：
> - 危重 CRITICAL：0 分钟（必须立即救治）
> - 紧急 URGENT：20 分钟
> - 半紧急 SEMI_URGENT：35 分钟
> - 非紧急 NON_URGENT：60 分钟
>
> 这个阈值数据存在 `Patient.get_max_allowed_wait()` 方法里，是项目中的唯一数据源——simulation 和 analysis 模块都从这里取，避免数据重复。
>
> 合规率 = 等待时间不超过阈值的病人数 ÷ 总治疗人数 × 100%。
>
> 例如，如果 100 个病人中有 15 个等待超时，合规率就是 85%。这个指标直接反映了急诊科的服务质量和资源是否充足。"

### 任务 4.2：演示清单

准备一个可运行的演示：

```bash
# 1. 加载数据
python -c "from hospital_team1.data.csv_loader import load_patients_from_csv; \
           patients = load_patients_from_csv('datasets/patients_dataset.csv'); \
           print(f'Loaded {len(patients)} patients')"

# 2. 运行仿真
python -c "from hospital_team1.simulation import run_shift_simulation; \
           from hospital_team1.data.csv_loader import load_patients_from_csv; \
           patients = load_patients_from_csv('datasets/patients_dataset.csv'); \
           result = run_shift_simulation(patients, slot_interval=30, workstation_count=3); \
           print(f'Treated: {len(result[\"records\"])}, Untreated: {result[\"untreated\"]}')"

# 3. 查看报告
python -c "from hospital_team1.simulation import run_shift_simulation, build_shift_report; \
           from hospital_team1.data.csv_loader import load_patients_from_csv; \
           patients = load_patients_from_csv('datasets/patients_dataset.csv'); \
           result = run_shift_simulation(patients, 30, 3); \
           report = build_shift_report(result); \
           print(f'Compliance: {report[\"compliance_rate\"]:.1f}%, Avg Wait: {report[\"average_wait_minutes\"]:.1f}min')"

# 4. 运行你的测试
python -m pytest tests/test_simulation/ -v
```

### 任务 4.3：报告贡献部分

在最终报告中，你负责写 simulation 部分——用自己的话回答：
- 这个模块做什么
- 为什么用离散事件仿真而不是简单算平均
- 一个具体例子：某病人什么时候到、什么时候开始治、等了多久、合规吗

---

## 六、每天检查清单

### 第 1 天 ✅
- [ ] 逐行读懂 `shift_simulation.py`，能在纸上画出流程图
- [ ] 修复 `compliance.py`，删除重复的 `SERVICE_LIMIT_MINUTES`，改为调用 `Patient.get_max_allowed_wait()`
- [ ] 更新 `_build_record()` 等调用方
- [ ] 向协调人提出删除 `engine.py` 的建议
- [ ] 提交第一天的改动

### 第 2 天 ✅
- [ ] 将 `build_queue_snapshot()` 的 waiting 列表改为使用 `PriorityQueue` ABC
- [ ] 验证 `Patient.__lt__` 和原排序逻辑在非危重场景下等价
- [ ] 确认成员 B 的队列改动不影响 simulation 的调用
- [ ] 提交第二天的改动

### 第 3 天 ✅
- [ ] 创建 `tests/test_simulation/` 目录结构
- [ ] 写完 `test_compliance.py`（至少 10 个用例）
- [ ] 写完 `test_shift_simulation.py`（至少 13 个用例）
- [ ] 写完 `test_report.py`（至少 7 个用例）
- [ ] 所有测试通过
- [ ] 在自己的分支 `simulation-member-c` 上提交和 push

### 第 4 天 ✅
- [ ] 准备三个答辩问题的讲稿，脱稿练习
- [ ] 准备可运行演示
- [ ] 参与全组合并讨论
- [ ] 写报告中的 simulation 部分

---

## 七、老师检查你的模块时大概率问的追问

| 追问 | 准备方向 |
|------|----------|
| "为什么危重病人等待时间是 0？" | 答：因为我们模型规定 CRITICAL 到达即治疗，不进入等待队列 |
| "两种优先队列实现结果一样吗？为什么？" | 答：一样，因为非危重场景下排序键等价，都按 (triage, arrival_time) |
| "如果不合规率很高怎么办？" | 答：说明工作站不够或病人太多，可以调 `workstation_count` 参数对比 |
| "你怎么验证仿真结果是正确的？" | 答：用边界测试验证：空队列、单人、同优先级、不同优先级、满工作站等场景都有覆盖 |
| "simulation 和 analysis 的关系是什么？" | simulation 产出原始记录（records），analysis 消费这些记录做统计和预测 |
