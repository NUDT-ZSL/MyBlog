"""Demo content for the site.

The persona is intentionally editable demo material. Everything here is
seeded by ``python manage.py seed_demo``; replace it in the admin or adapt
this module for your own writing.
"""
from __future__ import annotations

CATEGORIES = [
    {
        "name": "科研笔记",
        "slug": "research",
        "description": "编译原理、程序分析、形式化方法与 Verilog 的学习记录。",
        "icon": "◈",
        "accent": "jade",
        "order": 1,
    },
    {
        "name": "工程实践",
        "slug": "engineering",
        "description": "LLVM、C++、Python、后端、Docker 与本地大模型的踩坑现场。",
        "icon": "⌘",
        "accent": "blue",
        "order": 2,
    },
    {
        "name": "算法与竞赛",
        "slug": "algorithm",
        "description": "CSP、蓝桥杯与基础算法的题解和复盘。",
        "icon": "∴",
        "accent": "amber",
        "order": 3,
    },
    {
        "name": "兴趣随笔",
        "slug": "life",
        "description": "游戏、健身、玉器，以及代码之外的一些时刻。",
        "icon": "◌",
        "accent": "rose",
        "order": 4,
    },
    {
        "name": "学习归档",
        "slug": "study",
        "description": "书单、课程笔记、考试与求职信息的整理。",
        "icon": "▤",
        "accent": "violet",
        "order": 5,
    },
]

TAGS = [
    {"name": "LLVM", "slug": "llvm", "accent": "jade"},
    {"name": "SSA", "slug": "ssa", "accent": "jade"},
    {"name": "数据流分析", "slug": "dataflow", "accent": "jade"},
    {"name": "静态分析", "slug": "static-analysis", "accent": "jade"},
    {"name": "抽象解释", "slug": "abstract-interpretation", "accent": "blue"},
    {"name": "Verilog", "slug": "verilog", "accent": "amber"},
    {"name": "形式化验证", "slug": "formal-verification", "accent": "violet"},
    {"name": "C++", "slug": "cpp", "accent": "blue"},
    {"name": "Python", "slug": "python", "accent": "blue"},
    {"name": "Django", "slug": "django", "accent": "jade"},
    {"name": "Docker", "slug": "docker", "accent": "blue"},
    {"name": "LoRA", "slug": "lora", "accent": "violet"},
    {"name": "论文阅读", "slug": "paper-reading", "accent": "violet"},
    {"name": "算法", "slug": "algorithms", "accent": "amber"},
    {"name": "CSP", "slug": "csp", "accent": "amber"},
    {"name": "游戏", "slug": "gaming", "accent": "rose"},
    {"name": "玉器", "slug": "jade", "accent": "rose"},
    {"name": "生活", "slug": "life", "accent": "rose"},
    {"name": "书单", "slug": "books", "accent": "violet"},
    {"name": "Git", "slug": "git", "accent": "blue"},
    {"name": "数字电路", "slug": "digital-circuits", "accent": "amber"},
    {"name": "Linux", "slug": "linux", "accent": "blue"},
    {"name": "效率", "slug": "productivity", "accent": "violet"},
    {"name": "游戏机制", "slug": "game-design", "accent": "rose"},
]

POSTS = [
    {
        "title": "从支配边界到 Φ 函数：SSA 构造里最容易忽略的三个细节",
        "slug": "ssa-dominance-phi",
        "summary": "把支配树、支配边界和 φ 插入串起来。重点不是背算法，而是理解为什么循环头部的 φ 总是出现在那个位置。",
        "category": "research",
        "tags": ["LLVM", "SSA", "数据流分析"],
        "published_at": "2026-11-08T21:40:00+08:00",
        "cover_style": "graph",
        "is_featured": True,
        "views": 328,
        "update_log": "2026.11.09 补充 Cytron 算法的伪代码与一个循环例子。\n2026.11.08 初稿。",
        "errata": "如果发现支配边界的迭代顺序有误，欢迎来信；文中的代码只保留核心逻辑，省去了 LLVM 的 CFG 适配层。",
        "content": r"""组会讨论 SSA 的时候，我被问了一个很基础的问题：

> 为什么循环头部的 φ 节点总是出现得“刚刚好”？

当时的回答是“因为支配边界”。但这四个字其实什么也没解释。支配边界为什么能界定 φ 的插入位置？它和支配树是什么关系？如果 CFG 里有不可达块，算法还成立吗？

这篇笔记试着把这条链补完整。

## 1. 先把三个词放进同一张图

在 SSA（Static Single Assignment）里，每个变量只被赋值一次。原来的程序可能是这样：

```c
int sum = 0;
for (int i = 0; i < n; i++) {
    sum += a[i];
}
return sum;
```

如果直接把 `sum` 拆成多个版本，会遇到一个控制流汇合的问题：循环结束时，`sum` 到底来自循环体还是来自入口？于是需要 φ 函数在汇合点“选一个”：

```llvm
define i32 @sum(ptr %a, i32 %n) {
entry:
  br label %loop
loop:
  %i = phi i32 [ 0, %entry ], [ %i.next, %body ]
  %sum = phi i32 [ 0, %entry ], [ %sum.next, %body ]
  %cond = icmp slt i32 %i, %n
  br i1 %cond, label %body, label %exit
body:
  %idx = sext i32 %i to i64
  %p = getelementptr i32, ptr %a, i64 %idx
  %v = load i32, ptr %p
  %sum.next = add i32 %sum, %v
  %i.next = add i32 %i, 1
  br label %loop
exit:
  ret i32 %sum
}
```

这张 CFG 的关键结构是：

```mermaid
flowchart TD
    E[entry] --> L[loop header]
    L -->|i < n| B[body]
    L -->|i >= n| X[exit]
    B --> L
    style L fill:#12332c,stroke:#61d7bd,color:#dce6ef
    style E fill:#0f1b27,stroke:#7fa9ff,color:#dce6ef
    style X fill:#0f1b27,stroke:#9bb3c4,color:#dce6ef
```

φ 节点都落在 `loop` 这个块里。为什么是它，而不是 `entry` 或 `body`？

## 2. 支配关系：谁必然经过谁

设 $n$ 是 CFG 中的一个节点。如果从入口到 $n$ 的每一条路径都经过 $d$，就说 $d$ 支配 $n$，记作 $d \in \mathrm{Dom}(n)$。严格的支配关系要求 $d \neq n$。

对于循环：

- `entry` 支配所有节点；
- `loop` 支配 `body` 和 `exit`；
- `body` 不支配 `loop`，因为存在 `entry -> loop -> exit` 这条不进循环体的路径。

支配集合可以用下面的不动点公式计算：

$$
\mathrm{Dom}(n) = \{n\} \cup \bigcap_{p \in \mathrm{pred}(n)} \mathrm{Dom}(p)
$$

入口节点单独处理：$\mathrm{Dom}(entry)=\{entry\}$。

这看起来很像数据流分析，确实如此。它是前向的 must-analysis，格是集合的交，方向是从入口向出口。LLVM 里可以用 `DominatorTree` 直接拿到这个关系，不必自己迭代。

## 3. 支配边界：φ 的“势力范围”

定义 $DF(n)$ 为 $n$ 的支配边界：存在一个节点 $y \in \mathrm{succ}(n)$，使得 $n$ 支配 $y$ 但不严格支配 $y$。

换句话说，$n$ 的“势力”在 $y$ 这里断掉了。对于循环来说，`body` 有一个后继 `loop`；`body` 不支配 `loop`，而 `body` 的后继正是 `loop`。所以：

```text
loop ∈ DF(body)
```

如果 `body` 里定义了变量 `sum.next`，那么它的定义会沿着回边到达 `loop`，与入口的定义汇合。所以 `loop` 需要 φ。这个推理比“循环头需要 φ”更接近本质。

计算支配边界时，一个常见的做法是：

```cpp
for (BasicBlock *b : blocks) {
    if (pred_size(b) < 2) continue;
    for (BasicBlock *p : predecessors(b)) {
        BasicBlock *runner = p;
        while (runner != idom(b)) {
            DF[runner].insert(b);
            runner = idom(runner);
        }
    }
}
```

这段代码的直觉是：从每个前驱沿支配树往上走，直到走到 $b$ 的直接支配者。路径上的每个节点都把 $b$ 加入自己的支配边界。

在 LLVM 中，可以用：

```cpp
DominatorTree &DT = getAnalysis<DominatorTreeWrapperPass>().getDomTree();
for (BasicBlock &BB : F) {
    if (auto *Term = BB.getTerminator()) {
        for (unsigned I = 0; I < Term->getNumSuccessors(); ++I) {
            BasicBlock *Succ = Term->getSuccessor(I);
            if (!DT.dominates(&BB, Succ)) {
                // BB 到 Succ 的边跨越了支配边界
            }
        }
    }
}
```

## 4. 真正插入 φ 的时候，还要再走一步

有了支配边界，仍然不能直接“每个边界都插 φ”。经典的 Cytron 算法会先计算变量的定义集合，再对每个定义点求支配边界的传递闭包（iterated dominance frontier）。原因是 φ 本身也是一次定义：在某个块插入 φ 之后，这个定义可能又需要传递到更远的汇合点。

一个容易忽略的细节是：**φ 的插入和变量重命名是两个阶段**。如果一边插 φ 一边改名，后续看到的名字空间已经变了，支配边界的判断会被污染。先把所有 φ 的位置定下来，再做 rename，代码会干净很多。

### 细节一：不可达块

如果 CFG 中存在从入口不可达的块，支配集合的定义会变得不直观：它们不属于任何从入口出发的路径。工程上通常先删掉不可达块，或者把它们当作独立区域处理。否则 `idom` 可能为空，支配边界的循环会直接崩掉。

### 细节二：临界边

如果一条边的源节点有多个后继，目标节点有多个前驱，这条边就是临界边（critical edge）。在临界边上直接插 φ 有时不方便，通常要先拆分边，插入一个空块。LLVM 的 `SplitCriticalEdge` 可以帮你做这件事，但拆边会改变 CFG，记得同步更新支配树。

### 细节三：重命名时的栈

在支配树上做 DFS 时，每个变量维护一个栈，记录当前路径上的定义。遇到 φ 时，φ 的目标变量也要入栈；离开块时要弹出本块产生的所有定义。这个“入栈—弹出”的顺序如果写错，最常见的症状是 φ 的操作数指向了一个已经离开作用域的版本。

## 5. 用一个循环验证

回到开头的例子，构造过程可以压缩成：

1. 计算支配树：`entry -> loop -> {body, exit}`；
2. 计算 `DF(body) = {loop}`；
3. `sum` 在 `entry` 和 `body` 定义，`DF(entry)` 为空，`DF(body)` 包含 `loop`；
4. 在 `loop` 插入 `sum` 的 φ；
5. 重命名，得到 `[0, %entry]` 与 `[%sum.next, %body]` 两个入参。

这解释了为什么 φ 不需要出现在 `body`：`body` 不是汇合点。也解释了为什么 `exit` 不需要 φ：`sum` 在 `exit` 只有一条来自 `loop` 的路径，虽然那条路径本身包含了循环。

## 6. 留给自己的一道题

如果循环体里有 `break`，CFG 会多出一个从 `body` 直接到 `exit` 的边。此时 `exit` 的前驱变成两个：`loop` 和 `body`。φ 需要插在哪里？支配边界会怎么变化？

我先把问题留在这里。下一篇笔记会从“循环不变式”的角度继续拆这个例子。

## 参考资料

- Cytron et al., *Efficiently Computing Static Single Assignment Form and the Control Dependence Graph*, TOPLAS 1991.
- LLVM 文档：*Dominator Tree* 与 `DominatorTree` 类。
- 相关卡片：[[SSA]]、[[支配边界]]、[[循环不变式]]。
""",
    },
    {
        "title": "LLVM Pass 开发：从 ModulePass 到 New Pass Manager 的一次迁移",
        "slug": "llvm-new-pm-pass",
        "summary": "把旧版 ModulePass 迁移到 New PM，顺手补上依赖分析、测试与 opt 命令行注册。踩过的坑比 Pass 本身长。",
        "category": "research",
        "tags": ["LLVM", "C++", "数据流分析"],
        "published_at": "2026-11-03T20:10:00+08:00",
        "cover_style": "blueprint",
        "is_featured": True,
        "views": 271,
        "update_log": "2026.11.03 初稿；补充 `opt -passes` 的调试方法。",
        "errata": "不同 LLVM 版本的 PassBuilder 注册接口偶有差异，本文以 LLVM 19 为基准。",
        "content": r"""旧代码是一个典型的 `ModulePass`：

```cpp
struct MyAnalysis : public ModulePass {
    static char ID;
    MyAnalysis() : ModulePass(ID) {}
    bool runOnModule(Module &M) override {
        // ...
        return false;
    }
};
```

它能跑，但每次加一个新分析都要改 legacy pass manager 的注册，测试也不好写。趁着重构，我把它迁到了 New Pass Manager。

## 1. 先理解“分析”和“变换”的边界

New PM 里最重要的变化不是 API 名字，而是把 **analysis** 和 **transformation** 分开了：

- `AnalysisInfoMixin` 负责计算并缓存结果；
- `PassInfoMixin` 负责改写 IR；
- `PreservedAnalyses` 明确告诉框架：这次改写破坏了哪些缓存。

这逼着我想清楚：我这个 Pass 到底只是读 IR，还是会改 IR？如果会改，支配树是否还有效？

## 2. 一个最小的分析类

```cpp
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"

using namespace llvm;

struct DFAInfo {
    DenseMap<const BasicBlock *, unsigned> depth;
};

class DFAnalysis : public AnalysisInfoMixin<DFAnalysis> {
    friend struct AnalysisInfoMixin<DFAnalysis>;
    static AnalysisKey Key;

public:
    using Result = DFAInfo;
    Result run(Function &F, FunctionAnalysisManager &FAM);
};

AnalysisKey DFAnalysis::Key;

DFAnalysis::Result DFAnalysis::run(Function &F, FunctionAnalysisManager &FAM) {
    DFAInfo Info;
    auto &DT = FAM.getResult<DominatorTreeAnalysis>(F);
    for (BasicBlock &BB : F) {
        Info.depth[&BB] = DT.getNode(&BB)->getLevel();
    }
    return Info;
}
```

注意 `AnalysisKey` 必须是类内静态成员，并且要定义一次。少了这一句，链接错误通常不会直接指向这里。

## 3. 注册到 PassBuilder

```cpp
extern "C" LLVM_ATTRIBUTE_WEAK PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "DFAnalysis", LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "dfa") {
                        FPM.addPass(DFAPrinter());
                        return true;
                    }
                    return false;
                });
        }};
}
```

编译成插件：

```bash
clang++ -fPIC -shared -g -O2 dfa.cpp -o DFAnalysis.so \
  $(llvm-config --cxxflags --ldflags --libs core analysis passes)
```

然后：

```bash
opt -load-pass-plugin=./DFAnalysis.so \
    -passes='function(dfa)' \
    -disable-output test.ll
```

这里的 `function(dfa)` 是 New PM 的文本管线语法。`-passes='dfa'` 不行，因为 `dfa` 是 function pass，必须放在 `function(...)` 里。

## 4. 迁移时最容易崩的三处

| 现象 | 常见原因 | 处理 |
| --- | --- | --- |
| `PassManager` 编译失败 | 混用了 legacy 头文件 | 只保留 `llvm/IR/PassManager.h` |
| 分析结果为空 | 没在 `FAM` 中注册依赖 | 使用 `FAM.getResult<T>()`，不要自己 new |
| 改完 IR 后后续 Pass 崩 | 没有正确返回 `PreservedAnalyses` | 改动 CFG 时返回 `none()` |

我遇到的是第二种：在 `run` 里直接构造了一个 `DominatorTree`，没有走 `FAM`。单独测试没问题，接进 pipeline 后每次都要重算，性能非常差。改成 `FAM.getResult` 之后，框架会自动复用缓存。

## 5. 测试不要只靠 `opt`

一个 Pass 的测试至少要有三层：

1. **单元级**：对一小段 `.ll` 跑 `opt`，用 `FileCheck` 检查输出；
2. **回归级**：把历史 bug 缩减成最小 IR，沉淀在 `test/`；
3. **集成级**：跑真实的 C/C++ 项目，观察编译时间和误报。

`FileCheck` 的写法：

```llvm
; RUN: opt -load-pass-plugin=%librun -passes='function(dfa)' -S %s | FileCheck %s
; CHECK: loop
; CHECK-NEXT: depth=2
```

注意 `%librun` 这种路径最好通过 `lit` 的配置注入，不要写死本机路径。

## 6. 最后一点心得

New PM 的 API 看起来更啰嗦，但它把“依赖什么、破坏什么”变成了类型系统的一部分。迁移完成后，我的 Pass 反而更容易测试了——因为每个分析都可以独立构造，不再依赖全局的 PassManager 状态。

相关卡片：[[SSA]]、[[LLVM 常用命令]]。
""",
    },
    {
        "title": "用 Verilator 做一次可复现的 UART 仿真",
        "slug": "verilator-uart-repro",
        "summary": "从 testbench、时钟复位到 VCD 波形，搭一个最小但可复现的 UART 发送仿真。附几个 Verilator 常见报错的排查顺序。",
        "category": "research",
        "tags": ["Verilog", "数字电路", "Linux"],
        "published_at": "2026-10-28T22:05:00+08:00",
        "cover_style": "wave",
        "is_featured": False,
        "views": 214,
        "update_log": "2026.10.28 初稿；补充 `--timing` 与 `--trace` 的组合。",
        "errata": "仿真参数依赖具体波特率与时钟频率，移植时请重新计算分频系数。",
        "content": r"""硬件仿真最让人沮丧的，不是波形不对，而是“上次明明能跑”。所以这次我把 UART 发送模块的仿真做成了一个小闭环：固定工具版本、固定时钟、固定激励、固定检查。

## 1. 被仿真的模块

```verilog
module uart_tx #(
    parameter integer CLK_HZ = 50_000_000,
    parameter integer BAUD   = 115_200
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       valid,
    input  wire [7:0] data,
    output reg        tx,
    output reg        ready
);

localparam integer DIV = CLK_HZ / BAUD;

reg [15:0] div_cnt;
reg [3:0]  bit_idx;
reg [9:0]  shift;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        tx      <= 1'b1;
        ready   <= 1'b1;
        div_cnt <= 16'd0;
        bit_idx <= 4'd0;
        shift   <= 10'h3FF;
    end else if (ready && valid) begin
        shift   <= {1'b1, data, 1'b0}; // stop + data + start
        ready   <= 1'b0;
        div_cnt <= 16'd0;
        bit_idx <= 4'd0;
        tx      <= 1'b0;
    end else if (!ready) begin
        if (div_cnt == DIV - 1) begin
            div_cnt <= 16'd0;
            bit_idx <= bit_idx + 4'd1;
            tx      <= shift[bit_idx + 4'd1];
            if (bit_idx == 4'd9) begin
                ready <= 1'b1;
                tx    <= 1'b1;
            end
        end else begin
            div_cnt <= div_cnt + 16'd1;
        end
    end
end

endmodule
```

这里用了一个 10 位移位寄存器：起始位、8 个数据位、停止位。注意 `shift[bit_idx + 1]` 的索引范围，仿真时如果 bit_idx 到了 9，下一拍就会越界。实际代码里应该加保护，或者把状态机拆得更明确。

## 2. Testbench 的三个约定

```verilog
`timescale 1ns / 1ps

module tb_uart_tx;
    reg clk = 0;
    reg rst_n = 0;
    reg valid = 0;
    reg [7:0] data = 0;
    wire tx, ready;

    always #10 clk = ~clk; // 50 MHz

    uart_tx #(.CLK_HZ(50_000_000), .BAUD(115_200)) dut (
        .clk(clk), .rst_n(rst_n), .valid(valid),
        .data(data), .tx(tx), .ready(ready)
    );

    task send_byte(input [7:0] value);
        begin
            @(posedge clk);
            data  <= value;
            valid <= 1'b1;
            @(posedge clk);
            valid <= 1'b0;
        end
    endtask

    initial begin
        $dumpfile("uart.vcd");
        $dumpvars(0, tb_uart_tx);
        repeat (5) @(posedge clk);
        rst_n = 1;
        repeat (5) @(posedge clk);
        send_byte(8'h55);
        wait (ready);
        repeat (20) @(posedge clk);
        send_byte(8'hA3);
        wait (ready);
        repeat (20) @(posedge clk);
        $display("PASS: two bytes sent");
        $finish;
    end
endmodule
```

三个约定：

1. **时钟周期固定**，否则分频计数不可复现；
2. **复位至少保持几个周期**，避免 `x` 传播；
3. **检查 `ready` 而不是固定延时**，否则换一个波特率就要改测试。

## 3. 用 Verilator 跑起来

```bash
verilator --binary --timing --trace \
  -Wno-fatal \
  --top-module tb_uart_tx \
  -Mdir build \
  tb_uart_tx.v uart_tx.v
./build/Vtb_uart_tx
```

- `--binary`：直接生成可执行文件，省掉手写 C++ harness；
- `--timing`：支持 `#10` 这类延时；
- `--trace`：生成 VCD；
- `-Wno-fatal`：先把 warning 降级，但不要长期依赖它。

跑完用 GTKWave 打开：

```bash
gtkwave uart.vcd
```

观察 `tx` 在起始位拉低，随后每 8680 ns 左右翻转一次（50 MHz / 115200 ≈ 434 个周期）。如果周期数不对，先查 `DIV` 的整数除法是否被综合工具当成常量折叠。

## 4. 常见报错与排查顺序

### `%Error: ... Expecting ';'`

优先检查 `always` 块里的非阻塞赋值和 `begin/end` 是否配对。Verilog 对换行不敏感，错误行号经常指向下一行。

### `%Warning-UNUSED`

不一定是 bug。先看信号是否只用于调试；如果是接口预留，用 `/* verilator lint_off UNUSED */` 局部关闭，不要全局关。

### `%Error: Cannot find file containing module`

检查 `-I` 路径和文件名大小写。Linux 区分大小写，Windows 不区分，跨平台时很容易漏。

### 仿真卡住

先看时钟有没有跑起来，再看 `ready` 是否一直为低。用 `$display` 打印状态机，比盯着波形猜快。

## 5. 把“可复现”写进仓库

最终目录：

```text
uart-lab/
├── rtl/uart_tx.v
├── tb/tb_uart_tx.v
├── Makefile
└── README.md
```

`Makefile` 里固定命令，而不是把命令留在 shell history：

```makefile
SIM ?= verilator
TOP := tb_uart_tx
RTL := rtl/uart_tx.v
TB  := tb/tb_uart_tx.v

sim:
	$(SIM) --binary --timing --trace -Wno-fatal --top-module $(TOP) \
	  -Mdir build $(TB) $(RTL)
	./build/V$(TOP)

clean:
	rm -rf build uart.vcd
```

这篇的下一步，是把这个 testbench 改成带随机激励和 scoreboard 的版本，再用覆盖率收口。

相关卡片：[[同步复位与异步复位]]、[[Verilator 报错速查]]。
""",
    },
    {
        "title": "论文笔记：抽象解释——从格到不动点",
        "slug": "abstract-interpretation-notes",
        "summary": "用程序分析课的视角重读抽象解释：具体域、抽象域、Galois 连接、单调函数与 widening，最后落回一个区间分析的小例子。",
        "category": "research",
        "tags": ["静态分析", "抽象解释", "形式化验证", "论文阅读"],
        "published_at": "2026-10-19T19:30:00+08:00",
        "cover_style": "paper",
        "is_featured": False,
        "views": 402,
        "update_log": "2026.10.21 补充 Galois 连接的方向与 widening 的例子。\n2026.10.19 初稿。",
        "errata": "文中把“抽象域”与“抽象值集合”混用了几次，严谨表述以 Nielson 原书为准。",
        "content": r"""抽象解释（Abstract Interpretation）经常被讲成“在抽象域上跑一遍程序”。这句话没错，但漏掉了最重要的部分：**为什么这样跑是安全的**。

这篇笔记不打算复述教材，而是把几个关键定义放回一个具体例子里，看看它们各自在做什么。

## 1. 具体语义与抽象语义

设具体状态集合为 $\Sigma$，程序的一个操作可以看成函数 $f: \Sigma \to \Sigma$。我们关心的性质可能不是完整状态，而是某个变量的取值范围。

抽象域 $A$ 是具体域的一个近似。用区间域举例：

$$
A = \{ [l, u] \mid l, u \in \mathbb{Z} \cup \{-\infty, +\infty\},\ l \le u \} \cup \{\bot\}
$$

具体状态到抽象值的映射 $\alpha$ 叫抽象化，反过来 $\gamma$ 叫具体化：

$$
\alpha: \mathcal{P}(\Sigma) \to A, \qquad \gamma: A \to \mathcal{P}(\Sigma)
$$

它们满足：

$$
\alpha(S) \sqsubseteq a \iff S \subseteq \gamma(a)
$$

这就是 Galois 连接。它保证了“先抽象再计算”不会比“先具体计算再抽象”更精确——但同时也不会漏掉具体行为。

## 2. 一个区间分析例子

考虑：

```c
int x = 0;
while (x < 10) {
    x = x + 1;
}
```

抽象状态可以写成 $x \mapsto [l, u]$。循环入口的抽象值一开始是 $\bot$，然后迭代：

| 迭代 | 循环头抽象值 | 说明 |
| --- | --- | --- |
| 0 | $\bot$ | 还没有路径到达 |
| 1 | $[0,0]$ | 入口赋值 |
| 2 | $[0,1]$ | 循环体回边 |
| 3 | $[0,2]$ | 继续扩大 |
| ... | ... | ... |
| 11 | $[0,10]$ | 条件 $x<10$ 收窄 |
| 12 | $[0,10]$ | 不动点 |

如果循环条件是 `x < 1000000`，这个迭代会跑一百万次。实际分析不会这么干，于是有了 widening。

## 3. 单调性与不动点

抽象语义函数 $F: A \to A$ 需要是单调的：

$$
a \sqsubseteq b \implies F(a) \sqsubseteq F(b)
$$

如果 $A$ 是有限高度的格，且 $F$ 单调，那么从 $\bot$ 开始迭代：

$$
\bot \sqsubseteq F(\bot) \sqsubseteq F^2(\bot) \sqsubseteq \cdots
$$

一定会在有限步内到达不动点。这个不动点是 $F$ 的最小不动点，也是程序所有可达状态的保守近似。

但区间域的高度是无限的（上界可以一直增大），所以需要 widening 把无限上升链压成有限步。一个常见的 widening：

$$
[l_1, u_1] \nabla [l_2, u_2] =
[\text{if } l_2 < l_1 \text{ then } -\infty \text{ else } l_1,\
 \text{if } u_2 > u_1 \text{ then } +\infty \text{ else } u_1]
$$

它故意“扔掉”精度来换取终止。之后再用 narrowing 把过宽的结果收回来。

## 4. 安全性到底在保证什么

抽象解释的核心定理可以粗略写成：

$$
\forall a \in A,\quad F(\gamma(a)) \subseteq \gamma(F^\sharp(a))
$$

其中 $F^\sharp$ 是抽象语义。也就是说，抽象计算的结果覆盖了所有具体行为。它不是“证明程序一定正确”，而是“证明我们没有漏掉某类错误”。

这解释了为什么抽象解释器经常需要**组合**多个域：区间域擅长数值范围，谓词域擅长关系，指针域擅长别名。每个域都有自己的精度与成本。

## 5. 和 SSA 的关系

SSA 让每个变量只有一次定义，这天然适合做稀疏分析：φ 节点就是控制流汇合处的“抽象合并”。在 SSA 上做常量传播或区间分析，通常比在原始 IR 上做更直接，因为 def-use 链很清楚。

但 SSA 不是免费的：构造 φ、维护支配树、处理临界边，都是成本。对于简单的局部优化，直接在基本块内扫描可能更快。工程上永远是精度、速度和实现复杂度的三角 trade-off。

## 6. 我还没想清楚的问题

- 在 LLVM 的 New PM 里，如何优雅地组合多个抽象域，而不让缓存失效逻辑变成一团乱麻？
- 机器学习生成的“候选不变式”应该怎样接入抽象解释，才能既利用模型的直觉，又保留形式化的保证？
- 如果抽象域本身是学出来的，单调性还能保证吗？

这几问暂时没有答案，先记在[[循环不变式]]和[[谓词逻辑]]的卡片里。

## 参考资料

- Nielson, Nielson, Hankin. *Principles of Program Analysis*. Springer, 1999.
- Cousot & Cousot. *Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints*. POPL 1977.
- 课程笔记：Dataflow Analysis, University of ...（组会内部分享）
""",
    },
    {
        "title": "WSL2 + Docker 的磁盘又满了？一份不删库的清理清单",
        "slug": "wsl2-docker-disk",
        "summary": "从 Docker 的镜像层、构建缓存到 WSL2 的 ext4.vhdx，按风险从低到高整理一套清理顺序。先测量，再删除。",
        "category": "engineering",
        "tags": ["Docker", "Linux", "效率"],
        "published_at": "2026-10-09T23:15:00+08:00",
        "cover_style": "terminal",
        "is_featured": False,
        "views": 186,
        "update_log": "2026.10.09 初稿；2026.10.10 补充 `docker system df` 的解读。",
        "errata": "`Optimize-VHD` 需要 Hyper-V 模块；家庭版请使用 `diskpart` 的 compact 或第三方工具。",
        "content": r"""周五晚上，`df -h` 告诉我根分区只剩 1.2G。第一反应是删镜像，第二反应是——万一删掉了正在用的数据库卷呢？

所以先别删。把“测量”和“清理”分开。

## 1. 先看清楚空间去哪了

```bash
docker system df
docker system df -v
```

典型输出：

```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          38        7         46.2GB    31.4GB (67%)
Containers      12        2         1.8GB     1.1GB (61%)
Local Volumes   15        4         8.3GB     2.1GB (25%)
Build Cache     128       0         12.6GB    12.6GB
```

注意 `RECLAIMABLE` 不是“可以随便删”，它只是按引用计数估算的。`ACTIVE` 为 0 的镜像通常安全，但如果有容器处于 stopped 状态，仍然可能被引用。

WSL2 的磁盘还有一个额外现象：即使容器里删了文件，`ext4.vhdx` 也不会自动缩小。需要在 Windows 侧做 compact。

## 2. 低风险清理

先清构建缓存和悬空对象：

```bash
docker builder prune
docker image prune
docker container prune
```

`docker image prune` 默认只删 dangling 镜像；要删所有未被容器引用的镜像，用 `-a`，但先看一眼列表：

```bash
docker image ls --filter dangling=true
```

再清网络和无用卷：

```bash
docker network prune
docker volume ls
```

卷要格外小心。`docker volume prune` 会删掉所有未被容器引用的卷，数据库数据可能就在里面。先列出并确认：

```bash
docker volume inspect pgdata
```

## 3. 中等风险：按项目清理

我习惯按 compose 项目分组：

```bash
docker compose ls
docker compose -p old-project down --volumes
```

`--volumes` 会删掉该项目的命名卷。只对确定不再需要的项目使用。删之前先导出：

```bash
docker run --rm -v old-project_pgdata:/data -v "$PWD":/backup \
  alpine tar czf /backup/pgdata.tar.gz -C /data .
```

## 4. WSL2 的虚拟磁盘

在 PowerShell 中查看：

```powershell
wsl --list --verbose
Get-ChildItem "$env:LOCALAPPDATA\Docker\wsl" -Recurse -Filter ext4.vhdx |
  Select-Object FullName, @{n='GB';e={[math]::Round($_.Length/1GB,2)}}
```

关闭 WSL 后再压缩：

```powershell
wsl --shutdown
Optimize-VHD -Path "C:\Users\you\AppData\Local\Docker\wsl\data\ext4.vhdx" -Mode Full
```

如果没有 Hyper-V 模块，可以用 `diskpart`：

```text
select vdisk file="C:\path\to\ext4.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
```

**不要在 WSL 运行中做这件事。** 文件被占用时，轻则失败，重则损坏。

## 5. 一个容易忽略的坑

Docker Desktop 的磁盘路径可能有两份：`docker-desktop-data` 和 `docker-desktop`。新版 Docker Desktop 可能把它们合并到 `disk\docker_data.vhdx`。先确认路径，再操作。

另外，Windows 的“磁盘清理”不会碰 vhdx。别指望它。

## 6. 清理后的检查

```bash
docker system df
df -h /
du -sh /var/lib/docker 2>/dev/null
```

最后跑一个 `docker compose up -d`，确认服务能起来。清理的意义不是数字好看，而是系统仍然可用。

相关卡片：[[Git 救火手册]]。
""",
    },
    {
        "title": "LoRA 微调踩坑：显存、packing 与 loss 的三件小事",
        "slug": "lora-finetune-notes",
        "summary": "用 PEFT 在单卡上微调一个小模型时，最影响结果的往往不是超参，而是数据打包、mask 和评估口径。记录一次从 22G 到 11G 的排查。",
        "category": "engineering",
        "tags": ["LoRA", "Python", "Linux"],
        "published_at": "2026-09-27T21:20:00+08:00",
        "cover_style": "terminal",
        "is_featured": False,
        "views": 247,
        "update_log": "2026.09.27 初稿；2026.09.28 补充 packing 对 loss 的影响。",
        "errata": "不同 transformers 版本的 `DataCollatorForLanguageModeling` 参数名可能不同，以当前版本文档为准。",
        "content": r"""目标很简单：在一张 24G 的卡上，用 LoRA 微调一个 7B 模型，让它能根据给定的 IR 片段回答“这个循环是否可能不终止”。

结果第一版 OOM，第二版 loss 不降，第三版 loss 降了但评估一塌糊涂。下面按踩坑顺序记录。

## 1. 显存：先看谁在吃

```python
import torch
print(torch.cuda.memory_summary(device=None, abbreviated=False))
```

第一版配置：

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, config)
model.print_trainable_parameters()
```

可训练参数只有 0.2%，但显存依然爆。原因是：

- 序列长度 4096，batch size 4；
- 没有开 gradient checkpointing；
- 优化器状态仍然按全量参数分配（如果用了 `AdamW` 而不是 `paged_adamw_8bit`）；
- 数据 collator 把 padding 补到了整个 batch 的最大长度。

把 `per_device_train_batch_size` 降到 1、`gradient_accumulation_steps` 提到 8，并开启：

```python
model.gradient_checkpointing_enable()
model.enable_input_require_grads()
training_args = TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    bf16=True,
    max_length=2048,
)
```

显存从 22G 降到 11G。代价是训练慢了约 30%，可以接受。

## 2. packing：别把不同样本拼成一句话

为了提升吞吐，我开了 packing，把多条短样本拼进同一个 2048 长度。结果模型学会了“接着上一道题回答下一道题”。

问题在于 attention mask 没有正确隔离样本。使用 `DataCollatorForLanguageModeling` 时，至少要做到：

- 每条样本单独计算 loss；
- 不同样本之间用 attention mask 隔开；
- 如果框架不支持块对角 attention，宁可不 packing。

一个简化版本：

```python
def tokenize(example):
    prompt = build_prompt(example["ir"], example["question"])
    answer = example["label"]
    text = prompt + answer + tokenizer.eos_token
    out = tokenizer(text, truncation=True, max_length=2048)
    out["labels"] = out["input_ids"].copy()
    prompt_len = len(tokenizer(prompt, add_special_tokens=False)["input_ids"])
    out["labels"][:prompt_len] = [-100] * prompt_len
    return out
```

`-100` 让 loss 只计算回答部分。如果连 prompt 一起算，模型会把大量注意力花在复述问题上，loss 看起来很低，实际生成能力没有提升。

## 3. loss 不降：检查 label 和 mask

第二个坑是 `labels` 和 `input_ids` 共享了同一个 list 引用：

```python
out["labels"] = out["input_ids"]  # 错误：后续修改会互相影响
```

改成 `copy()`。另一个坑是 tokenizer 的 `pad_token` 没有设置：

```python
tokenizer.pad_token = tokenizer.eos_token
```

如果不设置，collator 可能用 `0` 填充，而 `0` 恰好是某个特殊 token，模型会学到奇怪的模式。

## 4. 评估口径：不要只看 loss

我最初的评估是“在验证集上算 loss”。但任务是判断循环是否终止，属于二分类，loss 低不代表判断对。

至少加三个指标：

| 指标 | 看什么 |
| --- | --- |
| Accuracy | 整体判断正确率 |
| False Positive | 把不终止判成终止的比例 |
| 输出格式合法率 | 能不能稳定输出 JSON |

尤其是第三个。模型可能损失很低，但输出永远是“根据分析，这个循环可能不终止”，格式完全不合法。

## 5. 小模型 + 小数据时的现实建议

- 先跑一个 100 条样本的过拟合实验，确认管线没问题；
- 固定随机种子，记录数据版本；
- 用 `wandb` 或本地日志记录每次配置；
- 不要在验证集上调 prompt；
- 把“模型输出”与“形式化工具结论”分开存储，避免混淆。

这次实验最后没有带来性能提升，但得到了一套可复现的训练脚本。对科研来说，后者可能更重要。

相关卡片：[[抽象解释]]。
""",
    },
]
