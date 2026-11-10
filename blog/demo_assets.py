"""Demo projects, notes, and small site content."""
from __future__ import annotations

PROJECTS = [
    {
        "title": "llvm-dfa-pass",
        "slug": "llvm-dfa-pass",
        "subtitle": "一个可复用的 LLVM 数据流分析框架与示例 Pass。",
        "summary": "在 New PM 上实现前向/后向数据流分析的通用骨架，附带 reaching definitions 与 live variables 两个示例。",
        "description": r"""## 它解决什么问题

LLVM 已经自带了很多分析，但当你需要验证一个新算法时，直接改 `lib/Analysis` 太重。这个项目把通用的数据流迭代框架抽出来，让一个新的 must/may 分析只需要提供：

- 格上的 meet / join 操作；
- 每个基本块的 transfer function；
- 初始状态与边界条件。

## 设计

```cpp
template <typename Lattice>
class ForwardAnalysis {
public:
    using State = typename Lattice::State;

    void run(Function &F, DominatorTree &DT) {
        for (BasicBlock &BB : F) {
            in_[&BB] = Lattice::bottom();
            out_[&BB] = Lattice::bottom();
        }
        in_[&F.getEntryBlock()] = Lattice::initial();

        bool changed = true;
        while (changed) {
            changed = false;
            for (BasicBlock *BB : inversePostOrder(F, DT)) {
                State newIn = Lattice::bottom();
                for (BasicBlock *P : predecessors(BB))
                    newIn = Lattice::join(newIn, out_[P]);
                if (newIn != in_[BB]) {
                    in_[BB] = newIn;
                    out_[BB] = transfer(*BB, newIn);
                    changed = true;
                }
            }
        }
    }
};
```

## 当前状态

- 前向分析：可用，已接入 `opt -passes=dfa-reach`；
- 后向分析：接口已定，测试还在补；
- 可视化：计划导出 DOT，方便和 Mermaid/Graphviz 对照。

## 下一阶段

1. 把 worklist 版本补齐，和朴素迭代做性能对比；
2. 增加 `-verify-each` 下的 CFG 修改测试；
3. 写一篇从零实现数据流分析的教程。
""",
        "category": "research",
        "status": "live",
        "progress": 88,
        "tech_stack": "C++, LLVM, CMake, FileCheck",
        "repo_url": "https://github.com/linxu/llvm-dfa-pass",
        "demo_url": "",
        "cover_style": "cfg",
        "is_featured": True,
        "sort_order": 1,
        "launched_at": "2025-10-12",
    },
    {
        "title": "trust-analyzer",
        "slug": "trust-analyzer",
        "subtitle": "面向 C 子集的静态分析原型：区间 + 谓词域。",
        "summary": "一个还在长身体的分析器：前端用 Clang AST，中间转自定义 IR，后端组合区间域与谓词域，输出可解释的告警。",
        "description": r"""## 目标

不是做一个工业级分析器，而是验证一个组合域的想法：

- 区间域负责数值范围；
- 谓词域负责分支上的关系；
- 两者通过 reduced product 共享信息；
- 每条告警都必须附带一段“为什么”的路径。

## 为什么不用 LLVM 直接做

LLVM IR 很适合优化，但原型阶段需要频繁改变抽象域和路径敏感策略。自定义一层很小的 IR，反而让实验迭代更快。等策略稳定后，再把核心算法搬回 LLVM。

## 当前进度

- [x] C 子集前端（变量、赋值、if、while、assert）
- [x] 区间域与 worklist 迭代
- [x] 基本块级路径可行性检查
- [ ] 谓词域的 reduced product
- [ ] 告警解释生成
- [ ] 与 CBMC 的对比实验

## 一个输出示例

```text
warning: assertion may fail at line 17
  path: entry -> loop(2) -> if(x > 10) -> assert(x < 20)
  interval: x ∈ [11, +∞]
  predicate: x > 10
  reason: upper bound is not established
```

## 近期计划

先不加新域，把现有分析的误报率测出来。没有基线的“更精确”没有意义。
""",
        "category": "research",
        "status": "wip",
        "progress": 62,
        "tech_stack": "C++, Clang, Z3, Python",
        "repo_url": "https://github.com/linxu/trust-analyzer",
        "demo_url": "",
        "cover_style": "lattice",
        "is_featured": True,
        "sort_order": 2,
        "launched_at": "2026-03-01",
    },
    {
        "title": "verilog-uart-lab",
        "slug": "verilog-uart-lab",
        "subtitle": "从 UART 到 SPI 的可复现 Verilog 实验箱。",
        "summary": "一组带 testbench、Makefile 和波形检查的数字电路实验，目标是把“仿真能跑”变成“结果可复现”。",
        "description": r"""## 包含什么

- UART TX / RX；
- 同步 FIFO；
- SPI master；
- 一个简单的 AXI-Lite 寄存器文件（进行中）。

每个模块都有：

- RTL 与 testbench；
- 固定随机种子的激励；
- `make sim` 和 `make wave`；
- 一份 README，记录时序假设和踩坑。

## 仿真命令

```bash
make sim MODULE=uart_tx
make wave
```

## 设计原则

1. testbench 不依赖手写延时，尽量等待 `ready` / `valid`；
2. 所有时钟频率与分频系数显式参数化；
3. 断言优先于波形肉眼检查；
4. 每个实验都能在干净的 Docker 镜像里跑。

## 为什么做这个

夏宇闻老师的教材给了很好的起点，但教材代码和真实工具链之间还有一段距离：Verilator 的 lint、时序、覆盖率、跨平台路径。这个仓库用来填这段距离。
""",
        "category": "research",
        "status": "live",
        "progress": 100,
        "tech_stack": "Verilog, Verilator, GTKWave, Make",
        "repo_url": "https://github.com/linxu/verilog-uart-lab",
        "demo_url": "",
        "cover_style": "wave",
        "is_featured": True,
        "sort_order": 3,
        "launched_at": "2026-02-14",
    },
    {
        "title": "agent-static-analysis",
        "slug": "agent-static-analysis",
        "subtitle": "让 Agent 提出假设，让分析器给出证据。",
        "summary": "探索 LLM Agent 与静态分析工具的双向协作：模型负责提出不变量与测试，分析器负责验证或给出反例。",
        "description": r"""## 核心假设

让模型直接“找 bug”很难评估；让模型提出**可被工具验证的假设**，则可以把开放问题转化成可检查的命题。

流程：

1. 输入一段 LLVM IR 和一个待验证性质；
2. Agent 阅读 IR，提出候选不变量；
3. 分析器检查不变量的语法与类型；
4. SMT / alive2 尝试证明或给出反例；
5. Agent 根据反例修正假设；
6. 人类审核最终报告。

## 目前实现

- 一个只读 IR 的 tool wrapper；
- 基于 Z3 的简单谓词检查；
- 一个记录“假设—证据—结论”的 trace 格式；
- 还没有可靠的 benchmark，这是最大的问题。

## 风险

- 模型可能生成看似合理但不可验证的性质；
- 反例可能来自建模错误，而不是程序错误；
- 评估成本高，容易过拟合到几个样例。

## 下一步

先做一个 50 条样例的小 benchmark，人工标注“可验证 / 不可验证 / 无关”，再谈自动化。
""",
        "category": "research",
        "status": "wip",
        "progress": 38,
        "tech_stack": "Python, LLVM, Z3, LangGraph",
        "repo_url": "https://github.com/linxu/agent-static-analysis",
        "demo_url": "",
        "cover_style": "agent",
        "is_featured": False,
        "sort_order": 4,
        "launched_at": "2026-06-20",
    },
    {
        "title": "玉锦轩 · 线上小铺",
        "slug": "jade-atelier",
        "subtitle": "一家玉器小店的轻量展示页，不做商城。",
        "summary": "给家里的玉器店做的一张线上名片：作品、故事、联系方式。没有购物车，没有投流，只有慢慢看。",
        "description": r"""## 为什么不是商城

玉器不是标准品，照片也很难还原种水和光。线上成交的沟通成本高，售后复杂。这个页面只承担三件事：

- 让人知道「玉锦轩」在做什么；
- 展示几件作品和它们的故事；
- 提供一个可靠的线下联系方式。

## 技术选择

- Django + SQLite：足够小，部署简单；
- 图片使用响应式 `srcset`，移动端不加载原图；
- 不做用户系统，减少维护面；
- 后台只给店主使用，移动端可编辑。

## 设计

留白、暖色、少动画。玉器本身的光泽已经足够，页面不应该抢戏。

## 当前状态

展示页已完成，正在补作品摄影和文字说明。商城功能明确不做。
""",
        "category": "engineering",
        "status": "live",
        "progress": 92,
        "tech_stack": "Django, SQLite, HTML, CSS",
        "repo_url": "https://github.com/linxu/jade-atelier",
        "demo_url": "",
        "cover_style": "jade",
        "is_featured": False,
        "sort_order": 5,
        "launched_at": "2026-04-05",
    },
    {
        "title": "local-llm-kit",
        "slug": "local-llm-kit",
        "subtitle": "本地模型部署、LoRA 微调与 API 接入的一站式脚本。",
        "summary": "把 vLLM、PEFT、FastAPI 和几个常用评测脚本包在一起，减少每次换模型时重复搭环境的时间。",
        "description": r"""## 包含什么

- `serve/`：vLLM / llama.cpp 启动脚本；
- `train/`：LoRA / QLoRA 的最小训练配置；
- `eval/`：格式合法率、准确率、延迟；
- `api/`：OpenAI 兼容的 FastAPI 包装；
- `docker/`：固定 CUDA 与 Python 版本。

## 一条命令

```bash
docker compose -f docker/compose.yml up -d
python scripts/train_lora.py --config configs/qwen_lora.yaml
python scripts/eval.py --adapter outputs/qwen-lora --suite ir-qa
```

## 踩过的坑

- `transformers` 与 `vllm` 的 tokenizer 版本冲突；
- bitsandbytes 在 WSL2 下的 CUDA 版本匹配；
- 训练时 `padding_side` 与推理不一致；
- 评测集泄漏进训练集。

这些都在 `docs/pitfalls.md` 里。
""",
        "category": "engineering",
        "status": "live",
        "progress": 80,
        "tech_stack": "Python, vLLM, PEFT, FastAPI, Docker",
        "repo_url": "https://github.com/linxu/local-llm-kit",
        "demo_url": "",
        "cover_style": "layers",
        "is_featured": False,
        "sort_order": 6,
        "launched_at": "2025-12-08",
    },
    {
        "title": "algo-notes",
        "slug": "algo-notes",
        "subtitle": "算法题解与可交互的图论小演示。",
        "summary": "CSP / 蓝桥杯的题解仓库，附带几个用 Canvas 写的图算法可视化，方便检查自己是不是真的理解了。",
        "description": r"""## 内容

- 基础数据结构：单调栈、并查集、线段树；
- 图论：最短路、拓扑排序、强连通分量；
- 动态规划：区间、树形、状压；
- 数学：数论、组合计数。

## 一个小坚持

每道题除了代码，必须写三段：

1. 这题的关键观察是什么；
2. 为什么这个复杂度可以接受；
3. 如果数据范围变大，算法会怎么失效。

## 可视化

`/viz` 下有几个 Canvas 演示：Dijkstra 的松弛顺序、拓扑排序的入度变化、单调栈的弹出过程。它们不是教学产品，只是我用来检查自己理解的道具。
""",
        "category": "demo",
        "status": "live",
        "progress": 100,
        "tech_stack": "C++, Python, JavaScript, Canvas",
        "repo_url": "https://github.com/linxu/algo-notes",
        "demo_url": "",
        "cover_style": "algo",
        "is_featured": False,
        "sort_order": 7,
        "launched_at": "2025-07-16",
    },
    {
        "title": "ir-notes",
        "slug": "ir-blog",
        "subtitle": "你现在正在看的这个站点。",
        "summary": "用 Django 手写的个人站：文章、项目、双向链接知识库、搜索、RSS、暗色模式，没有前端框架。",
        "description": r"""## 为什么是 Django

静态站更快，但我想在发布后也能：

- 在后台直接改一篇文章；
- 查看阅读量；
- 给知识卡片做真正的双向链接；
- 按标签、分类动态聚合。

Django 的 admin 和 ORM 让这些需求变得很便宜。

## 技术栈

- Django 6 + SQLite；
- 手写 CSS，没有 Tailwind / Bootstrap；
- Python-Markdown + Pygments；
- KaTeX、Mermaid、Giscus 按需加载；
- 部署目标是任意 WSGI 服务器。

## 设计目标

- 读代码舒服：深色优先，代码块高对比；
- 写作舒服：Markdown + 自动目录 + 更新日志；
- 长期可维护：内容与模板分离，数据可迁移；
- 轻量：不接推荐算法，不收集用户画像。

## 正在做

- [x] 首页、文章、项目、知识库、归档、关于；
- [x] 全文搜索、RSS、Giscus 接口；
- [x] 知识卡片双链与反向链接；
- [ ] 图片上传与文章封面；
- [ ] 部署脚本与备份。
""",
        "category": "engineering",
        "status": "wip",
        "progress": 74,
        "tech_stack": "Django, SQLite, Markdown, Pygments",
        "repo_url": "https://github.com/linxu/ir-notes",
        "demo_url": "http://127.0.0.1:8000",
        "cover_style": "terminal",
        "is_featured": False,
        "sort_order": 8,
        "launched_at": "2025-09-01",
    },
]

NOTES = [
    {
        "title": "SSA",
        "slug": "ssa",
        "summary": "Static Single Assignment：每个变量只被赋值一次，用 φ 函数在控制流汇合处合并版本。",
        "note_type": "concept",
        "tags": ["SSA", "LLVM", "数据流分析"],
        "aliases": "Static Single Assignment, 静态单赋值",
        "is_pinned": True,
        "body": r"""## 一句话

SSA（Static Single Assignment）要求每个变量在程序中**只被定义一次**。控制流汇合处用 φ 函数选择不同路径上的版本。

## 最小例子

```c
// 原始程序
x = 1;
if (cond) x = 2;
use(x);
```

```llvm
; SSA
br i1 %cond, label %then, label %merge
then:
  br label %merge
merge:
  %x = phi i32 [ 1, %entry ], [ 2, %then ]
  call void @use(i32 %x)
```

## 为什么有用

- def-use 链清晰，很多分析不需要再做 reaching definition；
- 稀疏分析更自然；
- 优化 Pass 更容易写。

## 代价

- 构造 φ 需要支配边界；
- 临界边可能需要拆分；
- 调试时 IR 比源代码更难读。

## 相关

- [[支配边界]]：φ 应该插在哪里；
- [[LLVM 常用命令]]：如何查看 SSA 形式的 IR。
""",
    },
    {
        "title": "支配边界",
        "slug": "dominance-frontier",
        "summary": "节点 n 的支配边界，是所有“被 n 支配但其后继不被 n 严格支配”的节点集合。它是 φ 插入位置的理论依据。",
        "note_type": "concept",
        "tags": ["SSA", "LLVM", "数据流分析"],
        "aliases": "Dominance Frontier, DF, 支配边界集",
        "is_pinned": True,
        "body": r"""## 定义

$DF(n)$ 包含所有满足以下条件的节点 $y$：

- 存在 $y$ 的一个前驱 $p$，使得 $n$ 支配 $p$；
- $n$ 不严格支配 $y$。

直观地说：$n$ 的“支配势力”在 $y$ 这里遇到了另一条路径，因此需要合并。

## 迭代支配边界

如果 φ 本身也是一次定义，那么插入 φ 之后还会产生新的边界：

$$
DF^{+}(S) = \operatorname{lfp}(\lambda X. S \cup \bigcup_{n \in X} DF(n))
$$

## 计算直觉

从每个前驱沿支配树向上走，直到直接支配者：

```cpp
runner = pred;
while (runner != idom(block)) {
    DF[runner].insert(block);
    runner = idom(runner);
}
```

## 相关

- [[SSA]]：为什么需要 φ；
- [[循环不变式]]：循环头部的支配关系。
""",
    },
    {
        "title": "抽象解释",
        "slug": "abstract-interpretation",
        "summary": "用抽象域近似具体语义，并通过单调函数的不动点保证分析结果覆盖所有具体行为。",
        "note_type": "concept",
        "tags": ["静态分析", "抽象解释", "形式化验证"],
        "aliases": "Abstract Interpretation, AI（静态分析语境）",
        "is_pinned": True,
        "body": r"""## 核心结构

- 具体域 $C$：程序真实状态的集合；
- 抽象域 $A$：我们关心的性质；
- 抽象化 $\alpha: \mathcal{P}(C) \to A$；
- 具体化 $\gamma: A \to \mathcal{P}(C)$；
- Galois 连接：$\alpha(S) \sqsubseteq a \iff S \subseteq \gamma(a)$。

## 安全性

抽象语义 $F^\sharp$ 必须满足：

$$
F(\gamma(a)) \subseteq \gamma(F^\sharp(a))
$$

即抽象计算的结果覆盖所有具体行为。精度是“尽量小”，安全性是“不能漏”。

## 终止性

- 有限高度格 + 单调函数 ⇒ 有限步到达不动点；
- 无限高度格（如区间）需要 widening；
- widening 之后用 narrowing 收回精度。

## 相关

- [[循环不变式]]：不动点与归纳；
- [[谓词逻辑]]：抽象域可以建立在谓词上；
- [[支配边界]]：SSA 上的稀疏分析。
""",
    },
    {
        "title": "谓词逻辑",
        "slug": "predicate-logic",
        "summary": "用谓词、量词和连接词描述程序性质。霍尔逻辑、循环不变式与 SMT 查询的共同语言。",
        "note_type": "concept",
        "tags": ["形式化验证", "抽象解释"],
        "aliases": "First-Order Logic, 一阶逻辑, FOL",
        "is_pinned": False,
        "body": r"""## 语法

一阶谓词逻辑的基本成分：

- 项：变量、常量、函数应用；
- 原子公式：$P(t_1, \ldots, t_n)$；
- 连接词：$\neg, \land, \lor, \to, \leftrightarrow$；
- 量词：$\forall x. \varphi$，$\exists x. \varphi$。

## 程序性质

霍尔三元组：

$$
\{P\}\ C\ \{Q\}
$$

表示：如果执行 $C$ 前 $P$ 成立，且 $C$ 终止，则执行后 $Q$ 成立。

循环不变式 $I$ 需要满足：

1. 初始时 $I$ 成立；
2. $I \land B$ 执行循环体后仍保持 $I$；
3. $I \land \neg B$ 能推出所需的后置条件。

## 和 SMT 的关系

SMT 求解器可以判定许多一阶公式的可满足性。静态分析器常把“这条路径是否可行”编码成 SMT 查询，再把模型当作反例。

## 相关

- [[循环不变式]]；
- [[抽象解释]]。
""",
    },
    {
        "title": "FIR",
        "slug": "fir",
        "summary": "Finite Impulse Response：输出只依赖有限个当前与过去输入。用抽头、卷积和线性相位描述。",
        "note_type": "concept",
        "tags": ["Verilog", "数字电路"],
        "aliases": "Finite Impulse Response, 有限脉冲响应",
        "is_pinned": False,
        "body": r"""## 定义

FIR 滤波器的输出是输入序列与滤波器系数的卷积：

$$
y[n] = \sum_{k=0}^{N-1} h[k] \cdot x[n-k]
$$

其中 $h[k]$ 是抽头系数，$N$ 是阶数。它不需要反馈，因此天然稳定。

## Verilog 结构

```verilog
module fir #(parameter N = 4) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [11:0] x,
    output reg  [15:0] y
);
    reg [11:0] tap [0:N-1];
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < N; i = i + 1) tap[i] <= 12'd0;
            y <= 16'd0;
        end else begin
            for (i = N - 1; i > 0; i = i - 1) tap[i] <= tap[i-1];
            tap[0] <= x;
            y <= (tap[0] + tap[1] + tap[2] + tap[3]) >> 2;
        end
    end
endmodule
```

这是一个四点滑动平均，不是通用 FIR。真实实现需要乘法器、系数存储和位宽管理。

## 相关

- [[同步复位与异步复位]]：上面的 `negedge rst_n` 是异步复位；
- [[Verilator 报错速查]]。
""",
    },
    {
        "title": "同步复位与异步复位",
        "slug": "sync-async-reset",
        "summary": "同步复位等待时钟沿，异步复位立即生效。两者在时序、复位释放和跨时钟域上的取舍不同。",
        "note_type": "concept",
        "tags": ["Verilog", "数字电路"],
        "aliases": "Synchronous Reset, Asynchronous Reset, 同步复位, 异步复位",
        "is_pinned": False,
        "body": r"""## 写法

异步复位：

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) q <= 1'b0;
    else        q <= d;
end
```

同步复位：

```verilog
always @(posedge clk) begin
    if (!rst_n) q <= 1'b0;
    else        q <= d;
end
```

## 对比

| 维度 | 同步复位 | 异步复位 |
| --- | --- | --- |
| 生效时机 | 时钟沿 | 立即 |
| 复位树 | 需要满足时序 | 不需要时钟 |
| 释放 | 自然同步 | 需要同步器 |
| 毛刺敏感 | 较低 | 较高 |

## 异步复位的释放问题

如果 `rst_n` 在时钟沿附近释放，触发器可能进入亚稳态。常见做法是异步置位、同步释放：

```verilog
reg rst_meta, rst_sync;
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) {rst_sync, rst_meta} <= 2'b00;
    else        {rst_sync, rst_meta} <= {rst_meta, 1'b1};
end
```

## 相关

- [[FIR]]；
- [[Verilator 报错速查]]。
""",
    },
    {
        "title": "LLVM 常用命令",
        "slug": "llvm-commands",
        "summary": "生成 IR、跑 Pass、看支配树、导出 CFG 的常用命令。按调试场景整理。",
        "note_type": "cheatsheet",
        "tags": ["LLVM", "Linux", "效率"],
        "aliases": "LLVM 命令, opt 命令, llvm-config",
        "is_pinned": True,
        "body": r"""## 生成 IR

```bash
clang -S -emit-llvm -O0 hello.c -o hello.ll
clang -S -emit-llvm -O2 -Xclang -disable-llvm-passes hello.c -o hello.ll
```

## 跑 Pass

```bash
opt -passes='print<domtree>' -disable-output hello.ll
opt -passes='function(mem2reg,instcombine)' -S hello.ll -o out.ll
opt -passes='default<O2>' -S hello.ll -o opt.ll
```

## 查看 CFG

```bash
opt -passes='view-cfg' -disable-output hello.ll
opt -passes='dot-cfg' hello.ll
```

## 自定义插件

```bash
opt -load-pass-plugin=./MyPass.so -passes='function(my-pass)' -disable-output test.ll
```

## 版本与编译参数

```bash
llvm-config --version
llvm-config --cxxflags --ldflags --libs core analysis passes
```

## 相关

- [[SSA]]；
- [[支配边界]]。
""",
    },
    {
        "title": "Verilator 报错速查",
        "slug": "verilator-errors",
        "summary": "Verilator lint 与仿真常见报错：UNUSED、WIDTH、BLKSEQ、timing，以及排查顺序。",
        "note_type": "cheatsheet",
        "tags": ["Verilog", "Linux", "效率"],
        "aliases": "Verilator 踩坑, Verilator 报错",
        "is_pinned": False,
        "body": r"""## 先跑 lint

```bash
verilator --lint-only -Wall -Wno-fatal top.v
```

## 高频 warning

| Warning | 含义 | 处理 |
| --- | --- | --- |
| `UNUSED` | 信号未使用 | 确认是否预留；局部关闭 |
| `WIDTH` | 位宽不匹配 | 显式截断或扩展 |
| `BLKSEQ` | 组合逻辑用了阻塞赋值 | 按语义改 `=` / `<=` |
| `LATCH` | 组合 always 产生锁存器 | 补全所有分支 |
| `TIMESCALE` | 缺少时间尺度 | 在 testbench 加 `` `timescale `` |

## 仿真参数

```bash
verilator --binary --timing --trace -Wno-fatal --top-module tb -Mdir build tb.v dut.v
```

## 排查顺序

1. 时钟和复位是否真的在动；
2. `x` 是否在复位后消失；
3. 位宽是否在拼接时被悄悄截断；
4. `always` 的敏感列表是否完整；
5. 最后才看波形细节。

## 相关

- [[同步复位与异步复位]]；
- [[FIR]]。
""",
    },
    {
        "title": "循环不变式",
        "slug": "loop-invariant",
        "summary": "在循环每次迭代前后都成立的性质。它是霍尔逻辑证明循环、抽象解释求不动点的交汇点。",
        "note_type": "concept",
        "tags": ["形式化验证", "静态分析", "抽象解释"],
        "aliases": "Loop Invariant, 循环不变量",
        "is_pinned": False,
        "body": r"""## 定义

循环不变式 $I$ 是在循环入口、每次迭代后都成立的性质。要证明循环满足后置条件 $Q$，通常需要三条：

1. **初始化**：进入循环前 $I$ 成立；
2. **保持**：$I \land B$ 执行循环体后 $I$ 仍成立；
3. **终止**：$I \land \neg B \Rightarrow Q$。

## 例子

```c
int sum = 0;
for (int i = 0; i < n; i++) sum += a[i];
```

一个不变式：

$$
I \equiv 0 \le i \le n \land sum = \sum_{k=0}^{i-1} a[k]
$$

## 自动发现为什么难

- 不变式的空间太大；
- 需要结合具体域（区间、谓词、数组）；
- 抽象解释能给出一个保守的 $I$，但不一定是最精确的；
- widening 会丢失信息，narrowing 也不保证恢复。

## 相关

- [[抽象解释]]；
- [[谓词逻辑]]；
- [[SSA]]。
""",
    },
    {
        "title": "Git 救火手册",
        "slug": "git-rescue",
        "summary": "撤销提交、找回丢失分支、清理大文件、解决 rebase 冲突的应急命令。先备份，再操作。",
        "note_type": "cheatsheet",
        "tags": ["Git", "Linux", "效率"],
        "aliases": "Git 急救, git reflog, git 撤销",
        "is_pinned": False,
        "body": r"""## 先别慌

任何“危险”操作之前，先创建一个备份分支：

```bash
git branch backup/before-rescue
```

## 撤销最近一次提交（保留改动）

```bash
git reset --soft HEAD~1
```

## 撤销提交并丢弃改动（确认！）

```bash
git reset --hard HEAD~1
```

## 找回丢失的提交

```bash
git reflog
git branch rescue <sha>
```

## rebase 冲突

```bash
git rebase --continue
git rebase --abort
```

## 误删分支

```bash
git reflog --all
git branch recovered <sha>
```

## 大文件清理

```bash
git filter-repo --path path/to/big.file --invert-paths
```

`filter-repo` 会改写历史，团队仓库操作前必须同步。

## 相关

- [[LLVM 常用命令]]。
""",
    },
]

STATUSES = [
    {
        "text": "在调一个 alias analysis 的误报，怀疑问题出在循环里的 PHI 节点。",
        "mood": "work",
        "days_ago": 0,
    },
    {
        "text": "把夏宇闻第 6 章的练习重新仿真了一遍，波形终于对上了。",
        "mood": "build",
        "days_ago": 1,
    },
    {
        "text": "本周读完《抽象解释》第 3 章；周末去看了块玉料。",
        "mood": "read",
        "days_ago": 4,
    },
    {
        "text": "重新整理知识库，把散落在 Obsidian 里的卡片搬了过来。",
        "mood": "build",
        "days_ago": 7,
    },
    {
        "text": "晚上跑了 5 公里。配速没变，心率降了一点，算是一次小优化。",
        "mood": "life",
        "days_ago": 10,
    },
]

FRIENDS = [
    {
        "name": "LLVM Project Blog",
        "url": "https://blog.llvm.org/",
        "description": "LLVM 官方博客，新版本、设计讨论与社区动态。",
        "avatar_text": "LL",
        "accent": "jade",
        "order": 1,
    },
    {
        "name": "Julia Evans",
        "url": "https://jvns.ca/",
        "description": "把系统底层讲得清楚又有趣。想学怎么做技术写作时会翻。",
        "avatar_text": "J",
        "accent": "rose",
        "order": 2,
    },
    {
        "name": "酷壳 CoolShell",
        "url": "https://coolshell.cn/",
        "description": "中文技术博客的老朋友。很多工程判断从这里开始。",
        "avatar_text": "酷",
        "accent": "amber",
        "order": 3,
    },
    {
        "name": "Compiler Explorer",
        "url": "https://godbolt.org/",
        "description": "在线看汇编与 IR。调优化、确认代码生成的第一站。",
        "avatar_text": "CE",
        "accent": "blue",
        "order": 4,
    },
    {
        "name": "Verilator",
        "url": "https://www.veripool.org/verilator/",
        "description": "开源 Verilog 仿真器。文档不算友好，但值得读。",
        "avatar_text": "V",
        "accent": "violet",
        "order": 5,
    },
]

BOOKS = [
    {
        "title": "编译原理",
        "author": "Alfred V. Aho 等",
        "category": "专业",
        "status": "reference",
        "rating": 5,
        "review": "龙书。不是每章都常翻，但前端、类型系统和优化的整体地图很稳。",
        "accent": "jade",
        "order": 1,
    },
    {
        "title": "高级编译器设计与实现",
        "author": "Steven S. Muchnick",
        "category": "专业",
        "status": "reading",
        "rating": 5,
        "review": "鲸书。SSA 与数据流分析章节值得反复读，当工具书用。",
        "accent": "blue",
        "order": 2,
    },
    {
        "title": "程序分析原理",
        "author": "Flemming Nielson 等",
        "category": "专业",
        "status": "reading",
        "rating": 5,
        "review": "公式密度高，但抽象解释讲得很完整。适合带着问题读。",
        "accent": "violet",
        "order": 3,
    },
    {
        "title": "Verilog 数字系统设计教程",
        "author": "夏宇闻",
        "category": "专业",
        "status": "reference",
        "rating": 4,
        "review": "中文 Verilog 入门经典。时序与阻塞/非阻塞赋值的章节常翻。",
        "accent": "amber",
        "order": 4,
    },
    {
        "title": "数字设计和计算机体系结构",
        "author": "David Harris 等",
        "category": "专业",
        "status": "queued",
        "rating": 4,
        "review": "待读。想补一补从门电路到流水线的完整链路。",
        "accent": "amber",
        "order": 5,
    },
    {
        "title": "置身事内",
        "author": "兰小欢",
        "category": "闲读",
        "status": "finished",
        "rating": 5,
        "review": "把约束条件下的理性讲得很清楚。理解很多“不合理”现象的开始。",
        "accent": "rose",
        "order": 6,
    },
    {
        "title": "强风吹拂",
        "author": "三浦紫苑",
        "category": "闲读",
        "status": "finished",
        "rating": 5,
        "review": "跑步、伙伴和一件没有意义却必须完成的事。论文被拒后读很合适。",
        "accent": "rose",
        "order": 7,
    },
    {
        "title": "逻辑哲学论",
        "author": "路德维希·维特根斯坦",
        "category": "闲读",
        "status": "finished",
        "rating": 4,
        "review": "没完全读懂。但“语言的边界”这句话，在写规格说明时会冒出来。",
        "accent": "violet",
        "order": 8,
    },
]

TOOLS = [
    {
        "name": "Compiler Explorer",
        "url": "https://godbolt.org/",
        "description": "在线查看 C/C++ 的汇编与 LLVM IR，支持多版本编译器。",
        "category": "编译与程序分析",
        "icon": "CE",
        "order": 1,
    },
    {
        "name": "LLVM Programmer's Manual",
        "url": "https://llvm.org/docs/ProgrammersManual.html",
        "description": "LLVM 数据结构与遍历方式的权威入口，写 Pass 必备。",
        "category": "编译与程序分析",
        "icon": "LL",
        "order": 2,
    },
    {
        "name": "LLVM Language Reference",
        "url": "https://llvm.org/docs/LangRef.html",
        "description": "LLVM IR 语法与指令语义。遇到不确定的指令先查这里。",
        "category": "编译与程序分析",
        "icon": "IR",
        "order": 3,
    },
    {
        "name": "Verilator Docs",
        "url": "https://verilator.org/guide/latest/",
        "description": "Verilator 用户指南与 lint 选项说明。",
        "category": "硬件验证",
        "icon": "V",
        "order": 1,
    },
    {
        "name": "GTKWave",
        "url": "https://gtkwave.sourceforge.net/",
        "description": "看 VCD 波形。界面复古，但足够好用。",
        "category": "硬件验证",
        "icon": "GW",
        "order": 2,
    },
    {
        "name": "arXiv cs.PL",
        "url": "https://arxiv.org/list/cs.PL/recent",
        "description": "编程语言方向的预印本。每天早上刷一眼标题。",
        "category": "论文与检索",
        "icon": "ar",
        "order": 1,
    },
    {
        "name": "Semantic Scholar",
        "url": "https://www.semanticscholar.org/",
        "description": "找引用关系和相关工作。比盲目搜索更高效。",
        "category": "论文与检索",
        "icon": "SS",
        "order": 2,
    },
    {
        "name": "Zotero",
        "url": "https://www.zotero.org/",
        "description": "文献管理。配合 Better BibTeX 管理引用键。",
        "category": "论文与检索",
        "icon": "Z",
        "order": 3,
    },
    {
        "name": "Excalidraw",
        "url": "https://excalidraw.com/",
        "description": "画架构图和草图，手绘风格但不影响阅读。",
        "category": "写作与效率",
        "icon": "EX",
        "order": 1,
    },
    {
        "name": "Mermaid Live",
        "url": "https://mermaid.live/",
        "description": "在线编辑 Mermaid 图，导出 SVG / PNG。",
        "category": "写作与效率",
        "icon": "M",
        "order": 2,
    },
]
