# Cleanup Useless Files Spec

## Why
随着项目的迭代和多次实验的运行，项目目录中积累了许多不再使用的旧日志、临时测试脚本和无用的文件。清理这些文件有助于保持代码库的整洁，降低维护成本。

## What Changes
- 扫描并识别项目中不再被引用的脚本文件（如临时测试代码、冗余文件）。
- 清理 `logs/` 目录下过期的、冗余的旧实验日志文件，仅保留最新的参考日志或清空无用日志。
- 清理其他任何冗余文件。
- **BREAKING**: 被删除的文件将被移除，请确保这些文件确实不再使用。

## Impact
- Affected specs: 无
- Affected code: 无用脚本、旧日志文件、冗余文档。

## ADDED Requirements
### Requirement: Project Cleanup
系统需要保持目录结构清晰，移除所有冗余文件。

#### Scenario: 成功清理文件
- **WHEN** 代理执行清理任务
- **THEN** 无用文件被删除，且项目的核心功能（如模拟器、评估器）依然能够正常运行。