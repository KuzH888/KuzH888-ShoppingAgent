# 商品与配图修改准备说明

本文件用于下一阶段。当前开发基线完成后，可以手动替换商城商品和配图；最终评估必须在修改完成后再运行。

## 商品数据位置

商品保存在 `data/products.json`。当前验证规则要求：

- 商品 ID 格式为 `ABC-001`，并且不能重复
- SKU 格式为 `KUZ-ABC-001`，并且不能重复
- 保留三个分类：`digital_accessories`、`home_office`、`travel_lifestyle`
- 当前每个分类必须正好包含 8 件商品
- 价格必须大于 0，库存不能小于 0，评分必须在 0–5 之间
- `name` 和 `description` 必须同时包含 `zh` 与 `en`
- `use_cases`、`features`、`colors` 中不能出现重复值
- `image_path` 必须是安全的项目相对路径

## 修改后必须同步检查

商品 ID、价格或功能改变后，需要同步修改：

- `data/evaluation_cases.json` 中的预期商品
- `data/test_cases.json` 中的推荐回归案例
- README 中的商品数量或分类说明
- 任何包含旧商品 ID 的演示文字

商品图片的实际目录和网页渲染方式将在下一阶段确认后统一设置。不要将图片写成外部临时链接，也不要覆盖 `frontend/public/kuzmall-lifestyle.png`，它是首页横幅而不是商品图片。

## 修改后的验证顺序

```powershell
.\.venv\Scripts\python.exe -m src.utils.catalog
.\.venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm run test
npm run build
```

上述检查全部通过后，才进行真实 API 联调和最终评估。
