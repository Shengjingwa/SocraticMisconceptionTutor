# Tasks
- [ ] Task 1: 删除根目录下的明显冗余与临时文件
  - [ ] SubTask 1.1: 删除 `are in the directory`
  - [ ] SubTask 1.2: 删除 `diff_output.txt`
  - [ ] SubTask 1.3: 删除 `test.ipynb`
  - [ ] SubTask 1.4: 删除单次修复脚本 `fix_misconceptions.py`
  
- [ ] Task 2: 删除 `data/` 目录下未使用的冗余数据文件
  - [ ] SubTask 2.1: 删除 `data/adversarial_inputs.json`
  - [ ] SubTask 2.2: 删除 `data/test_cases_normal.json`
  - [ ] SubTask 2.3: 删除 `data/strategy_templates.json`

- [x] Task 3: 归档或清理散落的测试脚本
  - [x] SubTask 3.1: 将 `test_classifier.py`, `test_generator.py`, `test_graph.py`, `test_run.py`, `test_s2_off_topic.py` 移动至 `tests/` 目录。
  - [x] SubTask 3.2: 更新这些脚本内部对 `src` 模块的相对导入路径（例如：`sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))`），确保它们在 `tests/` 目录下仍可正常运行。
