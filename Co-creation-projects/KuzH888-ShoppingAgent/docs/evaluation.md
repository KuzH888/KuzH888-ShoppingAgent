# 评估方案

## 目标

评估系统用于证明 ShoppingAgent 能够稳定理解中英文需求、遵守硬性约束，并且只使用商品目录与政策文件中的事实。开发阶段和最终提交阶段必须分开记录。

## 开发基线

开发基线完全在本地模拟模式运行，不连接 LLM，也不会产生 API 费用。当前案例位于 `data/evaluation_cases.json`，覆盖：

- 12 个中英文精确推荐案例
- 1 个无精确匹配案例
- 2 个商品详情案例
- 2 个商品比较案例
- 2 个商城政策案例

运行命令：

```powershell
.\.venv\Scripts\python.exe -m src.evaluation
```

命令会生成：

- `outputs/evaluation_baseline.md`：适合阅读和放入 GitHub 的报告
- `outputs/evaluation_baseline.json`：便于后续统计和绘图的机器可读结果

## 指标定义

| 指标 | 定义 |
|---|---|
| Overall case pass rate | 同时通过预期结果、语言和事实检查的案例比例 |
| Expected recommendation result | 推荐状态和第一推荐商品与人工标注一致的比例 |
| Hard-constraint satisfaction | 推荐结果没有违反预算、品类、库存、必备与排除条件的比例 |
| Catalogue grounding | 返回的商品 ID、价格和结构化事实与本地目录完全一致的比例 |
| Language consistency | 系统识别并使用预期中文或英文的比例 |
| Average/P95 latency | 本地确定性处理的平均和第 95 百分位耗时，不含网络延迟 |

## 商品修改后的处理

修改 `data/products.json` 后，原有的预期商品 ID 可能不再正确。此时应先更新 `data/evaluation_cases.json`，再运行完整测试。不要为了得到 100% 而直接把失败结果复制成预期值；每个预期结果都应根据预算、场景和功能条件人工检查。

目录 SHA-256 会写入报告，用于证明报告对应的具体商品版本。商品目录改变后，指纹也会改变，因此旧基线不会被误认为最终结果。

## 最终评估

完成商品和配图修改、离线测试以及真实 API 联调后，再运行：

```powershell
.\.venv\Scripts\python.exe -m src.evaluation --label final --output outputs/evaluation_report.md
```

最终报告还需要人工补充真实 LLM 的工具调用成功率、语言质量、网络响应时间、失败案例与改进说明。API Key 不得出现在报告、Notebook 输出或截图中。
