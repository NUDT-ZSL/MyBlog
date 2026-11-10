"""Additional demo posts (kept separate to keep demo_content readable)."""
from __future__ import annotations

POSTS_MORE = [
    {
        "title": "从一道 CSP 题看单调栈的边界处理",
        "slug": "csp-monotonic-stack",
        "summary": "单调栈的模板很短，但“什么时候弹栈、弹到哪、相等的元素怎么处理”才是决定正确性的地方。用一道柱状图题复盘。",
        "category": "algorithm",
        "tags": ["算法", "CSP", "C++"],
        "published_at": "2026-09-18T20:40:00+08:00",
        "cover_style": "graph",
        "is_featured": False,
        "views": 153,
        "update_log": "2026.09.18 初稿。",
        "errata": "代码中的哨兵技巧依赖数组下标从 0 开始，移植时注意边界。",
        "content": r"""题目很经典：给定 $n$ 个非负整数，表示柱状图中每个柱子的高度，求能勾勒出的最大矩形面积。

暴力枚举左右边界是 $O(n^2)$，单调栈可以做到 $O(n)$。但模板背下来之后，我依然在三个地方写错过。

## 1. 为什么是单调递增栈

固定一根柱子 $i$，如果它能向左右扩展，那么左右两侧第一个比它矮的柱子就是边界。矩形的宽度是：

$$
\text{right}_i - \text{left}_i - 1
$$

面积是 $h_i \times \text{width}$。

维护一个高度单调递增的栈。当遇到一根更矮的柱子时，栈顶柱子的右边界就确定了；左边界则是弹出后新的栈顶。

```cpp
#include <bits/stdc++.h>
using namespace std;

long long largestRectangleArea(vector<int>& heights) {
    heights.push_back(0);              // 哨兵，强制清空栈
    vector<int> st;                    // 存下标，高度递增
    long long ans = 0;
    for (int i = 0; i < (int)heights.size(); ++i) {
        while (!st.empty() && heights[st.back()] > heights[i]) {
            int h = heights[st.back()];
            st.pop_back();
            int left = st.empty() ? -1 : st.back();
            ans = max(ans, 1LL * h * (i - left - 1));
        }
        st.push_back(i);
    }
    return ans;
}
```

## 2. 第一个坑：`>` 还是 `>=`

如果写成 `>=`，相等高度的柱子会被提前弹出。对于最大矩形面积，这通常仍然正确，因为最后那根等高的柱子会以相同高度再算一次。但如果题目要求的是“每个柱子作为最小值的区间个数”，相等元素的处理会直接影响计数。

我的原则是：**先想清楚“相等时保留哪一个”对答案意味着什么**，再决定比较符号，而不是背模板。

## 3. 第二个坑：哨兵的位置

在末尾 `push_back(0)` 可以保证循环结束时栈被清空，省掉一段收尾逻辑。但如果原数组允许高度为 0，末尾加 0 仍然有效；如果允许负数，0 就不是最小值，哨兵会失效。

更稳妥的写法是显式收尾：

```cpp
for (int i = 0; i <= n; ++i) {
    int cur = (i == n) ? -1 : heights[i];
    while (!st.empty() && heights[st.back()] > cur) {
        int h = heights[st.back()];
        st.pop_back();
        int left = st.empty() ? -1 : st.back();
        ans = max(ans, 1LL * h * (i - left - 1));
    }
    st.push_back(i);
}
```

## 4. 第三个坑：宽度计算

我一开始写的是 `i - st.back()`，忘了减 1。原因是把“下标差”和“元素个数”混了。用一个小例子手算：

```text
heights = [2, 1, 2]
i = 2, 弹出高度 2 的柱子，left = 1，right = 2
width = 2 - 1 - 1 = 0  ← 错了
```

等等，这里 `i=2` 是当前柱子，右边界应该是 `i-1`。正确宽度是 `(i-1) - left`。所以公式 `i - left - 1` 里的 `i` 是“右边界再右一格”。这也是为什么末尾加哨兵很方便：哨兵的下标天然就是右边界 + 1。

## 5. 一个可复用的检查清单

- 栈里存的是下标还是值？存下标才能算宽度。
- 弹栈时，右边界是 `i` 还是 `i-1`？
- 相等元素保留左边还是右边？
- 有没有处理栈非空但循环结束的情况？
- 面积用 `long long` 了吗？

## 6. 复杂度

每个元素最多入栈一次、出栈一次，所以是 $O(n)$；栈的空间是 $O(n)$。这道题的价值不在于难度，而在于它把“边界”这个词具体化了。

相关卡片：[[循环不变式]]（单调栈的循环不变式：栈内高度单调递增，且每个元素都还没找到右边界）。
""",
    },
    {
        "title": "玉锦轩手记：一块糯冰种边角料的去与留",
        "slug": "jade-stone-story",
        "summary": "家里的小店进了一块边角料。去皮、看裂、定题，最后留下的不是最贵的那件，而是最耐看的那件。",
        "category": "life",
        "tags": ["玉器", "生活"],
        "published_at": "2026-09-08T22:30:00+08:00",
        "cover_style": "jade",
        "is_featured": False,
        "views": 98,
        "update_log": "2026.09.08 初稿。",
        "errata": "",
        "content": r"""家里有一间很小的玉器店，叫「玉锦轩」。它和我的代码没有关系，但和我的很多判断方式有关系。

上周回去，店里进了一块糯冰种的边角料。形状不规整，一面有棉，一侧有裂。按照生意人的算法，它应该被切成几颗小戒面，回本最快。但我爸把它放在窗边，看了两天。

## 1. 先去皮

玉料的第一层往往不是它真正的样子。皮壳、氧化层、甚至一道看起来很深的水线，都可能只是表象。去皮之后，才看得到种水、颜色和裂的走向。

这很像读代码。函数签名、目录结构、README，都是“皮”。真正的问题往往在状态的生命周期、错误的传播路径、以及那些“大家都默认它不会发生”的分支里。

## 2. 裂不是瑕疵，是约束

那块料子有一条斜裂。切戒面会避开它，但避开的代价是剩下的形状更碎。我爸最后决定保留裂，顺着裂做一件小山水：裂变成山脊，棉变成云雾。

这不是“把缺陷说成特点”的鸡汤。它是一次明确的工程取舍：**在约束下寻找仍然成立的整体**。编译器优化也是，寄存器数量、指令延迟、别名关系，都是裂；好的方案不是假装没有裂，而是让裂成为设计的一部分。

## 3. 光

玉的价值很大一部分在光。同一个物件，上午的自然光、下午的暖光、晚上的射灯，看起来完全不同。所以看玉不能只看照片，也不能只看一个角度。

代码也一样。单元测试通过、集成测试通过、线上跑了一周，是三种不同的光。只看一种，判断很容易过头。

## 4. 留白

最后成品是一件很小的牌子，没有复杂的雕工。我爸说，这块料子最好的地方是那一片干净的水头，雕满了就浪费了。

我把它放在书桌上，旁边是显示器和一摞论文。写代码卡住的时候，会拿起来看一眼。它提醒我：不是所有空间都需要被填满。删掉一个不必要的抽象，往往比再加一层更接近正确。

## 5. 不写成商城

有人建议把「玉锦轩」做成线上商城。我想了想，没有做。它可以有一个页面，放几张照片、几段故事，但不应该变成一个需要运营、投流、比价的地方。

爱好一旦变成 KPI，就会失去它作为“休息”的功能。这个站点里的玉器内容也会保持很轻：偶尔写，不带货，不直播。

相关卡片：[[抽象解释]]（是的，看玉和做分析都需要知道自己在哪个抽象层）。
""",
    },
    {
        "title": "我的 2026 阅读清单：编译器、逻辑与一点物理",
        "slug": "reading-list-2026",
        "summary": "上半年读完和没读完的书。不是推荐榜，只是一份诚实的进度记录，以及每本书留下的一句话。",
        "category": "study",
        "tags": ["书单", "生活"],
        "published_at": "2026-08-30T18:10:00+08:00",
        "cover_style": "paper",
        "is_featured": False,
        "views": 132,
        "update_log": "2026.08.30 初稿；每季度更新一次。",
        "errata": "",
        "content": r"""读书笔记很容易变成“已读”列表。今年我换了一个做法：每本书只记一句真正带走的话，哪怕书没读完。

## 在读 / 常翻

### 《Principles of Program Analysis》

Nielson 三件套。公式密度很高，但抽象解释那一章值得反复读。带走的一句话：

> 分析的正确性来自具体语义与抽象语义之间的连接，而不是来自算法本身。

### 《高级编译器设计与实现》

Muchnick。当作工具书查，不适合从头读到尾。SSA 和支配关系那几章对写 Pass 很有帮助。

### 《Verilog 数字系统设计教程》

夏宇闻。每次写 testbench 之前翻一下时序和阻塞/非阻塞赋值的章节。经典之所以经典，是因为它真的会把坑提前告诉你。

## 读完

### 《置身事内》

兰小欢。理解地方政府与经济行为的一本很好的入门书。带走的一句话：

> 很多看似不合理的现象，在约束条件下其实是理性的。

### 《强风吹拂》

三浦紫苑。关于跑步，也关于一群人如何把一件“没有意义”的事做成意义。很适合在论文被拒之后读。

### 《逻辑哲学论》

维特根斯坦。说实话，很多地方没读懂。但“语言的边界就是世界的边界”这句话，在写规格说明的时候会突然冒出来。

## 没读完的

- 《A Discipline of Programming》：Dijkstra 的推导风格很迷人，但需要整块时间。
- 《The Little Schemer》：读到一半去写代码了，明年重来。
- 《计算机体系结构：量化研究方法》：太厚，目前只读了存储层次。

## 一点方法

- 技术书用“问题驱动”：带着一个具体问题去查，比从头读效率高。
- 闲书用“睡前 20 分钟”：不设 KPI，读多少算多少。
- 每本书只留一句摘录，写进知识库，不追求完整摘要。

明年的目标不是读更多，而是把《程序分析原理》真正读完一遍，并整理成一组可以讲的卡片。

相关卡片：[[抽象解释]]、[[谓词逻辑]]。
""",
    },
    {
        "title": "用 Mermaid 画 CFG：组会 PPT 之外的可维护方案",
        "slug": "mermaid-cfg-workflow",
        "summary": "把控制流图、支配树和数据流方程写进 Markdown。比截图可维护，比手绘可复现，也比 PPT 更适合长期积累。",
        "category": "research",
        "tags": ["LLVM", "效率", "论文阅读"],
        "published_at": "2026-08-18T19:00:00+08:00",
        "cover_style": "blueprint",
        "is_featured": False,
        "views": 175,
        "update_log": "2026.08.18 初稿。",
        "errata": "Mermaid 的自动布局不保证与 LLVM 的 CFG 完全一致，重要图仍建议手工校对。",
        "content": r"""组会讲 CFG，最痛苦的不是讲，而是下周还要改。PPT 里的截图一旦结构变化就要重画，Visio 文件又很难进 Git。

今年开始，我把结构图都写进 Markdown，用 Mermaid 渲染。它不是万能的，但对“可维护的示意图”来说已经够用。

## 1. 一个循环的 CFG

```mermaid
flowchart TD
    A["entry<br/>i = 0, sum = 0"] --> B{"i < n ?"}
    B -->|true| C["body<br/>sum += a[i]"]
    C --> D["i = i + 1"]
    D --> B
    B -->|false| E["exit<br/>return sum"]
    style A fill:#0f1b27,stroke:#7fa9ff,color:#dce6ef
    style B fill:#12332c,stroke:#61d7bd,color:#dce6ef
    style E fill:#0f1b27,stroke:#9bb3c4,color:#dce6ef
```

对应的数据流方程可以直接写在图下面：

$$
\mathrm{IN}(B) = \bigcup_{P \in pred(B)} \mathrm{OUT}(P)
$$

$$
\mathrm{OUT}(B) = f_B(\mathrm{IN}(B))
$$

图和方程放在同一个源文件里，改结构时不容易漏改文字。

## 2. 支配树

```mermaid
flowchart TD
    E[entry] --> L[loop]
    L --> B[body]
    L --> X[exit]
    B --> C[continue]
    style E fill:#0f1b27,stroke:#7fa9ff,color:#dce6ef
    style L fill:#12332c,stroke:#61d7bd,color:#dce6ef
```

支配树和 CFG 是两张图。不要试图用同一张图表达所有关系，读者会迷路。

## 3. 数据流图

```mermaid
flowchart LR
    IN([IN]) --> GEN["gen / kill"]
    GEN --> OUT([OUT])
    OUT -.->|"back edge"| IN
    style IN fill:#12332c,stroke:#61d7bd,color:#dce6ef
    style OUT fill:#12332c,stroke:#61d7bd,color:#dce6ef
```

## 4. 什么时候不要用 Mermaid

- 需要精确坐标的论文插图：用 TikZ 或 draw.io 导出 PDF；
- 节点超过 30 个的 CFG：Mermaid 的自动布局会变成一团毛线；
- 需要复杂嵌套子图的架构图：PlantUML 或手绘更合适；
- 对字体、颜色、线宽有严格要求的正式出版：不要用网页渲染器。

## 5. 写作流程

1. 在笔记里先写文字假设；
2. 用 Mermaid 画最小结构；
3. 对着真实 IR 校对节点名和边；
4. 导出 SVG 放进论文/PPT；
5. 把源文件留在版本库里。

Mermaid 的最大价值不是“好看”，而是**图也能被 diff**。当 CFG 多了一条边，Git 会告诉你。

相关卡片：[[SSA]]、[[支配边界]]。
""",
    },
    {
        "title": "第一次读 LLVM IR：先把这五个概念分清",
        "slug": "llvm-ir-first-read",
        "summary": "写给刚进组的自己：Module、Function、BasicBlock、Instruction、Value 不是同一层的东西。用一段 IR 把它们拆开。",
        "category": "research",
        "tags": ["LLVM", "SSA", "C++"],
        "published_at": "2025-12-21T20:00:00+08:00",
        "cover_style": "terminal",
        "is_featured": False,
        "views": 289,
        "update_log": "2025.12.21 初稿；2026.01.04 修正 Value/User 的描述。",
        "errata": "文中对 `User` 的解释做了简化，完整关系见 LLVM 的 Programmer's Manual。",
        "content": r"""刚接触 LLVM 时，我最大的困惑不是语法，而是对象层次：为什么 `Function` 可以遍历 `BasicBlock`，`BasicBlock` 又可以遍历 `Instruction`，而 `Instruction` 又是 `Value`？

## 1. 五个层次

```text
Module
└── Function
    └── BasicBlock
        └── Instruction (is-a Value, is-a User)
```

- **Module**：一个翻译单元，包含函数、全局变量、元数据；
- **Function**：一个函数，包含参数和基本块；
- **BasicBlock**：一段顺序执行的指令，最后一条必须是终结指令；
- **Instruction**：具体操作，比如 `add`、`load`、`br`；
- **Value**：任何可以产生结果的东西，包括常量、参数、指令。

`Instruction` 继承自 `User`，`User` 继承自 `Value`。所以一条指令既是一个值（它产生结果），也是一个使用者（它引用操作数）。

## 2. 一段最小 IR

```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
  %sum = add i32 %a, %b
  ret i32 %sum
}
```

对应关系：

- `@add` 是一个 `Function`；
- `entry` 是一个 `BasicBlock`；
- `%sum = add ...` 是一条 `Instruction`；
- `%sum` 同时是一个 `Value`；
- `ret i32 %sum` 是终结指令，它的操作数 `%sum` 是一个 `Use`。

## 3. 为什么 SSA 让分析变简单

在 SSA 里，每个 `Value` 只有一次定义。于是一条指令的 def-use 链非常清晰：

```cpp
for (User *U : I.users()) {
    if (auto *Inst = dyn_cast<Instruction>(U)) {
        // 直接拿到使用点，不需要再做 reaching definition
    }
}
```

这也是为什么很多分析喜欢先转到 SSA。不是 SSA 更快，而是它把“这个值从哪来”变成了图上的边。

## 4. 常被混淆的两件事

### `Value` 不等于“运行时值”

`Value` 是编译期的 IR 对象，不是程序运行时的具体数值。常量 `42` 是 `ConstantInt`，也是 `Value`。

### `BasicBlock` 不是“语句块”

它没有花括号的概念，只是一段以终结指令结尾的指令序列。前端生成 IR 时，控制流已经被显式化了。

## 5. 建议的阅读顺序

1. 写一个 `Hello, IR`，用 `clang -S -emit-llvm` 生成；
2. 用 `opt -passes=print<domtree>` 看支配树；
3. 写一个只统计指令数的 FunctionPass；
4. 再去看 SSA 构造和内存优化。

不要一上来读 `InstructionSimplify.cpp`。先建立对象模型，再读优化算法。

相关卡片：[[SSA]]、[[LLVM 常用命令]]。
""",
    },
    {
        "title": "把游戏机制当作系统设计来读",
        "slug": "game-systems-design",
        "summary": "最近重玩《杀出重围》和《异星工厂》，发现游戏和编译器共享同一个问题：如何在有限资源下，让一套规则产生可理解的行为。",
        "category": "life",
        "tags": ["游戏", "游戏机制", "生活"],
        "published_at": "2025-11-02T21:00:00+08:00",
        "cover_style": "graph",
        "is_featured": False,
        "views": 117,
        "update_log": "2025.11.02 初稿。",
        "errata": "",
        "content": r"""我玩游戏很慢。不是因为操作差，而是因为总在拆系统。

最近重玩《杀出重围》，又打开了《异星工厂》。一个是沉浸式模拟，一个是自动化工厂，看起来毫无关系，但它们在设计上回答的是同一个问题：

> 如何用一组有限的规则，产生玩家可以理解、又可以组合的行为？

## 1. 规则的数量不等于复杂度

好的系统往往规则很少，但交互很多。《杀出重围》的核心规则无非是“噪音、光、视野、路径”，组合起来却能产生几十种通关方式。

编译器也是这样。SSA、支配关系、数据流，都是很朴素的数学对象；组合起来，才长出常量传播、死代码消除、循环优化。

## 2. 可解释性是一种设计目标

《异星工厂》的传送带会堵，堵了之后你能沿着物品流找到瓶颈。它没有隐藏状态，所有因果都在屏幕上。

静态分析工具也应该这样。一个误报如果无法解释“为什么它认为这里可能出错”，用户就不会信任它。精度不是唯一指标，可解释性是。

## 3. 约束产生风格

《杀出重围》的弹药有限，所以玩家会尝试潜行；《异星工厂》的地图资源有限，所以玩家会设计铁路。约束不是限制，而是风格的来源。

论文也一样。页数限制、实验资源、可用的 benchmark，都会塑造一篇论文的写法。接受约束，比假装没有约束更专业。

## 4. 玩游戏的收获

- 学会看系统而不是看画面；
- 学会接受“足够好”的解；
- 学会在失败后重开，而不是硬撑；
- 学会享受过程，而不是只盯着成就列表。

这几点，写代码和做科研都用得上。

相关卡片：[[抽象解释]]（把一个复杂系统映射到一个可理解的抽象层，是游戏设计，也是程序分析）。
""",
    },
]
