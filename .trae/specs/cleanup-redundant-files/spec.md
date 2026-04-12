# Cleanup Redundant Files Spec

## Why
当前项目根目录下存在大量的测试脚本、临时文件、错误生成的文件（如 `are in the directory`）以及在重构过程中遗留的冗余数据文件，导致项目结构杂乱，降低了代码可读性和维护性。清理这些文件能使项目结构更加清晰。

## What Changes
- 识别并删除根目录下的临时文件、无用的输出日志和单次使用的脚本。
- 清理 `data/` 目录下在核心代码中不再引用的废弃数据文件。
- 将根目录下散落的各个测试脚本归档移动到 `tests/` 目录，或者直接删除不再使用的旧测试代码。
- **BREAKING**: 删除文件后将无法直接运行部分旧版测试脚本，但这不影响核心系统的运行。

## Impact
- Affected specs: 无
- Affected code: 
  - `are in the directory`, `diff_output.txt`, `test.ipynb`, `fix_misconceptions.py` 等根目录文件
  - `data/adversarial_inputs.json`, `data/test_cases_normal.json`, `data/strategy_templates.json` 等无用数据文件
  - 根目录下的各类 `test_*.py` 脚本

## REMOVED Requirements
### Requirement: 旧有废弃数据结构与一次性脚本
**Reason**: 经过全局代码搜索确认，`adversarial_inputs.json`、`test_cases_normal.json`、`strategy_templates.json` 等文件在核心逻辑（`src/`）和测试脚本中已不再被读取。根目录下的各种临时文本、数据清理脚本（如 `fix_misconceptions.py`）已经完成了它们的历史使命，继续保留只会造成干扰。
**Migration**: 直接删除。

## MODIFIED Requirements
### Requirement: 测试脚本归档管理
将原来散落在根目录下的 `test_classifier.py`, `test_generator.py`, `test_graph.py`, `test_run.py`, `test_s2_off_topic.py` 移动至 `tests/` 目录进行统一管理，或者对内容已过时的测试脚本进行清理。
