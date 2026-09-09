# KuzH888-ShoppingAgent

> 基于 HelloAgents 的多语言智能购物客服，根据用户的核心需求推荐合适的商品。

## 📝 项目简介

KuzH888-ShoppingAgent 面向商品数量和品类有限的小型综合商城。用户可以通过网页右下角的客服聊天窗口描述预算、使用场景、核心功能和个人偏好，智能客服会澄清需求、检索候选商品，并给出有依据的推荐和对比说明。

项目采用前后端分离架构：Python 与 FastAPI 提供后端接口，HelloAgents 负责智能体和工具调用，Vue 3、TypeScript、Vite 与 Pinia 构建模拟商城和客服弹窗。

适用场景包括：

- 根据预算、用途和偏好推荐商品
- 比较多件候选商品并解释差异
- 回答商品规格、库存和商城政策问题
- 使用中文、英文或其他受支持语言与用户交流

## ✨ 核心功能

- [x] 核心需求提取：识别使用场景、预算、必要功能、偏好和排除条件
- [x] 商品搜索与推荐：过滤不符合条件的商品并生成 Top 3 推荐
- [x] 可解释商品比较：返回评分构成、匹配条件及主要取舍
- [x] 中英文需求解析：自动识别中文或英文购物需求
- [x] 对话编排：最多提出两个澄清问题，并在当前会话中合并用户补充信息
- [x] 结构化双语回复：输出首选、最多两个备选、理由和主要取舍
- [x] 网页客服窗口：在模拟商城页面中提供浮动聊天弹窗
- [x] 商品详情抽屉：展示完整规格、库存、评分和模拟保修期
- [x] 可视化商品对比：选择 2–3 件商品并并排查看关键差异
- [x] 商城政策问答：查询配送、退换货、保修和隐私说明
- [x] 可复现离线评估：19 个案例、五项质量指标和商品目录指纹
- [x] 一键本地运行：启动、健康检查和安全停止 PowerShell 脚本
- [x] 安全边界：只引用商品数据库中的价格、库存和产品属性

## 🛍️ 模拟商城数据

KuzMall 当前包含 24 件虚构商品，统一使用澳元（AUD）：

- 数码配件：8 件
- 居家办公：8 件
- 旅行生活：8 件

`data/products.json` 保存中英文名称与描述、固定价格、库存、评分、使用场景、
功能标签、颜色、保修期、规格和本地图片路径。数据模型位于
`src/models/product.py`，可以运行以下命令验证数据：

```powershell
python -m src.utils.catalog
```

## 🛠️ 技术栈

- 智能体框架：HelloAgents
- 智能体范式：SimpleAgent 与工具调用
- 后端：Python、FastAPI、Uvicorn
- 前端：Vue 3、TypeScript、Vite 8、Pinia 4
- 前端质量：vue-tsc、ESLint、Prettier、Vitest
- 配置管理：python-dotenv
- 开发与演示：Jupyter Notebook
- 数据存储：JSON（后续可升级为 SQLite）
- LLM：支持通过 API Key、Base URL 和模型 ID 配置兼容服务

商城用户可以从后端提供的模型白名单中选择模型。API Key 始终保存在服务端，
不会发送到浏览器。

## 🧠 智能客服架构

`ShoppingAssistant` 是开发和演示阶段使用的本地客服编排器。它保存当前进程内的
会话信息、判断缺少的核心需求，并确保整个会话最多提出两个澄清问题。获得足够
信息后，它调用确定性的推荐引擎，再生成与用户语言一致的结构化回复。

`create_live_agent()` 用于最终联网测试。它根据用户从白名单选择的模型创建一个
HelloAgents `SimpleAgent`，并注册商品搜索、详情查询、商品比较和政策查询四个工具。模拟模式
下会阻止在线智能体启动，因此现在不需要填写 API Key。

## 🏗️ 整体架构

本项目采用前后端分离架构。Vue 单页应用与 Python 后端分别启动、构建和测试，
二者只通过 HTTP JSON 接口通信。

```text
浏览器商城前端（Vue 3 / TypeScript / Vite / Pinia）
  ├─ 商品分类、卡片、详情抽屉、商品对比与模型选择
  ├─ 浮动客服窗口与当前浏览器会话
  └─ 类型化 API 客户端（frontend/src/api）
                    │
                    │ HTTP + JSON
                    ▼
FastAPI 后端（src/api）
  ├─ 模型、商品详情/对比、政策、聊天和会话接口
  ├─ ShoppingAssistant 本地客服编排器
  └─ HelloAgents SimpleAgent 在线模式
                    │
                    ▼
商品工具层（src/tools）
  ├─ 商品搜索
  ├─ 商品详情
  ├─ 商品比较
  └─ 商城政策查询
                    │
                    ▼
业务服务层（src/services）
  ├─ 中英文需求解析
  ├─ 硬性条件过滤与 100 分排序
  └─ 双语回复格式化
                    │
                    ▼
本地数据与配置（data/products.json、data/store_policies.json、config/models.json、.env）
```

`scripts/` 提供原型运行编排，不改变前后端分离关系：它只负责启动两个独立服务、
执行 HTTP 健康检查并记录本次启动的进程编号。

前端只能通过后端接口取得商品和推荐结果，不直接访问 API Key、LLM 服务或本地
商品文件。这样可以分别开发、测试和替换前后端。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 22.12+ 或 24+
- Jupyter Notebook 或 JupyterLab
- 一个可用的 LLM API 服务（仅最终在线测试需要）

### 安装依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 配置 API

复制 `.env.example` 为 `.env`。开发阶段保持模拟模式，无需填写 API Key；
最终在线测试时再填写真实密钥并关闭模拟模式。不要将真实密钥提交到 GitHub。

```env
LLM_PROVIDER=openai
LLM_MODEL_ID=gpt-5.6-luna
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
APP_SIMULATION_MODE=true
```

当前可选模型由 `config/models.json` 管理，默认使用 `gpt-5.6-luna`。

### 运行 Notebook

```powershell
jupyter lab
```

打开 `main.ipynb`，从上到下依次运行单元格。

### 运行网页应用

#### 推荐：一键启动

在项目根目录打开 PowerShell，运行：

```powershell
.\scripts\start.ps1
```

脚本会使用项目自己的 `.venv` 启动 FastAPI 和 Vite、完成健康检查，并打开
`http://127.0.0.1:5173/`。后台日志保存在 `outputs/logs/`，不会提交到 GitHub。

随时可以单独检查运行状态：

```powershell
.\scripts\check.ps1
```

使用结束后安全关闭本次脚本启动的服务：

```powershell
.\scripts\stop.ps1
```

如果不希望启动脚本自动打开浏览器，可以运行
`.\scripts\start.ps1 -NoBrowser`。脚本不会自动安装依赖、填写 API Key，或关闭
不是由它启动的进程。

#### 手动启动

打开第一个 PowerShell 终端，在项目根目录启动 FastAPI 后端：

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```

启动成功后保持该终端窗口运行，然后访问：

- 接口文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`
- 可选模型：`http://127.0.0.1:8000/api/models`
- 商品列表：`http://127.0.0.1:8000/api/products`
- 商城政策：`http://127.0.0.1:8000/api/policies`

当前后端处于模拟模式，因此聊天接口可以运行，但不会调用或产生任何 LLM API
费用。

打开第二个 PowerShell 终端，进入前端目录并启动 Vite：

```powershell
Set-Location frontend
npm install
npm run dev
```

浏览器访问 `http://127.0.0.1:5173/`。开发服务器会把 `/api` 请求代理到
`http://127.0.0.1:8000`，浏览器不会直接读取 Python 文件、商品 JSON 或 API Key。

### 运行自动化测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

```powershell
Set-Location frontend
npm run test
npm run build
```

当前测试覆盖商品数据验证、中英文需求解析、硬性条件过滤、稳定排序、
无精确匹配回退、商品详情、比较和政策查询工具，以及前端聊天与对比状态。

### 运行开发基线评估

```powershell
.\.venv\Scripts\python.exe -m src.evaluation
```

评估会生成 `outputs/evaluation_baseline.md` 和同名 JSON 文件，并记录当前
`products.json` 的 SHA-256 指纹。当前结果只是商品修改前的开发基线，不能代替
最终 LLM 评估。完整指标定义见 [`docs/evaluation.md`](docs/evaluation.md)。

## 📖 使用示例

```text
用户：I need lightweight headphones for commuting. My budget is AUD 100,
and noise cancellation is important.

客服：
```

## 🎯 项目亮点

- 将自然语言需求转换为结构化推荐条件
- 使用 Python 工具处理硬性过滤和商品评分，降低 LLM 编造商品信息的风险
- 将商品推荐理由与真实商品属性对应
- 前后端分离，并支持扩展不同 LLM 和界面语言

## 📊 性能评估

当前商品修改前的离线开发基线包含 19 个中英文案例：

- 总体案例通过率：100%
- 预期推荐结果正确率：100%
- 硬性约束满足率：100%
- 商品目录事实忠实度：100%
- 语言一致性：100%

这些数字只衡量本地确定性逻辑。最终成绩将在替换商品与配图，并完成真实 LLM
联调后重新生成。当前报告见
[`outputs/evaluation_baseline.md`](outputs/evaluation_baseline.md)。

## 🔮 未来计划

- [x] 建立模拟商城商品数据
- [x] 实现商品搜索、过滤、评分和比较工具
- [x] 完成 HelloAgents 推荐智能体及本地模拟编排器
- [x] 实现 FastAPI 后端接口
- [x] 实现 Vue 3 商城网页和客服聊天窗口
- [x] 实现商品详情、2–3 件商品可视化对比和商城政策问答
- [x] 完成中英文推荐测试案例和本地性能评估
- [x] 建立可重复运行、区分开发基线与最终结果的评估流程
- [x] 完成一键启动、状态检查、安全停止和浏览器原型验收
- [ ] 手动替换商品数据与商品配图（参见 [`docs/catalog-editing.md`](docs/catalog-editing.md)）
- [ ] 完成真实 OpenAI API 联调和最终评估

## 🤝 贡献指南

欢迎提出 Issue 和 Pull Request。

## 📄 许可证

MIT License

## 👤 作者

- 姓名：
- GitHub：[@KuzH888](https://github.com/KuzH888)
- Email：

## 🙏 致谢

感谢 Datawhale 社区和 Hello-Agents 项目提供的教程与框架支持。
