- [ ] `turn_logs.jsonl` 中同一会话的 `turn_id` 为递增序列（不再全 0）
- [ ] `session_summary.jsonl.turn_count` 与该会话 turn 数一致（口径一致）
- [ ] `history_summary` 能在长对话中被稳定更新，且不会被后续节点/主循环覆盖丢失
- [ ] 并发仿真时 `pipeline_*.log` / 控制台输出不再严重混行，且每条日志可追溯到 `session_id`
- [ ] JSONL 日志写入在并发下保持“一条记录一行”，无截断/拼接
- [ ] 遇到 Arrearage/429/超时等关键 LLM 错误时，会话被标记为 abnormal，并写入清晰原因
- [ ] 轻量测试通过：`tests/simple_test.py` 可运行；小规模并发仿真可完成且日志/指标正常

