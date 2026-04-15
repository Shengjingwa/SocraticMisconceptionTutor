# Socratic Misconception Tutor (生成式 AI 苏格拉底导师系统)

本项目是一个面向初中物理迷思概念纠正的 **生成式 AI 导师系统**。针对通用大语言模型（LLM）在教育场景下容易沦为“直接给答案的作业帮手”的痛点，本项目提出并实现了一种基于 **有限状态机 (FSM)** 与 **动态安全护栏 (Guardrails)** 的智能体架构，强制大模型遵循严格的苏格拉底式启发教学法。

本项目无需真实人类受试者，内置了基于大模型的**多智能体仿真（Multi-Agent Simulation）**和**自动化评估（LLM-as-a-Judge）**工作流，是一套完整的设计科学（Design Science）实证研究代码库，可直接用于教育技术学（EdTech）或 AI in Education (AIED) 的学术论文支撑。

---

## 🌟 核心特性 (Key Features)

1. **FSM 教学状态机 (`router.py`)**
   - 将苏格拉底式对话解构为 9 个动态流转的教学状态（S0 到 S8），包括：新概念探索、认知冲突触发、微支架引导、事实兜底等。
   - 内置防死循环与情绪感知逻辑，根据学生的认知僵局或挫败感动态降级教学策略。

2. **动态教学护栏 (`guardrails.py`)**
   - **双重防泄漏机制**：结合正则匹配与 `LLM-as-a-Judge`，精准拦截 AI 直接剧透答案的行为。
   - **教育学豁免规则**：智能识别并豁免优秀的启发式行为（如：极端归谬法思想实验、日常类比展开、确认性总结），确保系统在“防溺爱”的同时不失教学灵活性。

3. **多智能体计算仿真 (`simulator.py`)**
   - 彻底摆脱人类受试者依赖。基于认知心理学构建带有特定物理错念（如 M-ELE-001：电流消耗模型）和不同性格特征（P1：极度固执，P2：易动摇）的“虚拟学生画像（Student Personas）”。
   - 支持自动化开展 `Baseline` vs `FSM` vs `FSM+Guardrail` 的系统架构消融实验（Ablation Study）。

4. **多维自动化评估 (`evaluator.py` & `llm_judge.py`)**
   - 从系统日志中自动化提取核心量化指标：认知纠偏率、平均对话轮数、意图识别准确率、状态流转成功率、答案泄露率。
   - 利用 `LLM-as-a-Judge` 作为教育专家，对每段对话进行“苏格拉底度”和“教学有效性”的盲评量表打分。

---

## 📂 项目结构 (Project Structure)

```text
/workspace
├── src/                      # 核心源代码目录
│   ├── main.py               # 交互式终端应用入口
│   ├── router.py             # FSM 状态机路由器
│   ├── guardrails.py         # 教学底线与安全护栏
│   ├── simulator.py          # 多智能体虚拟学生仿真器
│   ├── evaluator.py          # 客观指标自动化计算器
│   ├── llm_judge.py          # LLM 专家盲评裁判模块
│   └── graph.py              # 基于 LangGraph 的工作流编排
├── data/                     # 实验配置与数据集
│   ├── misconceptions.json   # 物理迷思概念库
│   └── simulation_profiles.json # 虚拟学生画像配置
├── logs/                     # 运行时日志与会话记录
│   ├── app.log               # 系统底层运行日志
│   ├── turn_logs.jsonl       # 对话轮次级全量数据
│   └── evaluation_results.json # LLM 专家打分报告
├── results/                  # 评估输出结果
│   ├── summary_metrics.csv   # 核心评估指标汇总表
│   └── manual_audit.csv      # 用于人工审计的抽样会话
└── requirements.txt          # Python 依赖清单
```

---

## 🚀 快速开始 (Getting Started)

### 1. 环境配置
请确保您的 Python 版本 >= 3.9，并安装必要的依赖：
```bash
pip install -r requirements.txt
```

配置大模型 API Key（本项目默认调用阿里通义千问模型）：
```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

### 2. 运行交互式体验 (MVP)
您可以亲自扮演带有物理迷思概念的学生，与 AI 导师进行实时的终端对话测试：
```bash
python src/main.py
```

### 3. 运行自动化仿真实验 (Pipeline)
如果您需要为学术论文收集量化数据，可以通过以下一条命令执行完整的“仿真-评估-裁判”流水线：
```bash
LOG_FILE="logs/pipeline_$(date +%F_%H-%M-%S).log"
(

  export DASHSCOPE_API_KEY="your_api_key_here"
  python src/simulator.py &&
  python src/evaluator.py &&
  python src/llm_judge.py
) > "$LOG_FILE" 2>&1
echo "实验已完成，完整过程已保存到: $LOG_FILE"
```

运行结束后，您可以直接查看 `results/summary_metrics.csv` 获取各架构版本的性能对比数据。

---

