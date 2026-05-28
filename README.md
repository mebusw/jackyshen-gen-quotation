# jackyshen-gen-quotation SKLL

专业 PDF 报价单、培训提案和商业文档生成器。

## 快速开始

`npx skills add  https://github.com/mebusw/jackyshen-gen-quotation`

## 功能概述

从自然语言、Markdown 或结构化数据生成品牌一致、风格专业的 PDF 报价单和培训提案。支持中英文内容。

## 工作流程

```
用户输入（自然语言 / Markdown / 结构化数据）
        ↓
    LLM 结构化提取
        ↓
  QuoteDocument Schema (Pydantic)
        ↓
     Jinja2 模板渲染
        ↓
        HTML 输出
        ↓
      Playwright PDF
        ↓
        PDF 输出
```

## 支持的文档类型

| 类型 | 标题 | 说明 |
|------|------|------|
| `quotation` | 报价单 / Quotation | 包含客户信息、报价明细、付款条款 |
| `outline` | 培训大纲 / Outline | 包含课程目标、大纲模块、受众群体 |
| `mixed` | 培训方案及报价 / Proposal | 报价 + 大纲两者兼有 |

## 品牌主题

**UPerform** 品牌配置：

- **主色：** `#083A67`（深海蓝）
- **辅色：** `#4F82BA`（钢蓝）
- **点缀色：** `#FFFFFF`（白色）
- **Logo：** 页面右上角

## 快速开始

当用户说"生成报价单"或类似内容时，回复：

```
好的，我来帮您生成专业报价单。

请提供以下信息（可以一次性全部提供，也可以逐项回答）：

1. 客户信息 — 客户名称、公司名
2. 服务项目 — 培训/咨询内容、人数、天数、单价
3. 文档标题 — 报价单标题
4. 报价日期 — YYYY/M/D
5. 付款信息 — 银行账户信息（可选）
```

## 报价项目分类

| category | 中文 | 示例 |
|----------|------|------|
| training | 培训 | 讲师授课、培训课程 |
| travel | 差旅 | 讲师差旅、交通住宿 |
| interview | 访谈 | 前期调研、访谈 |
| consulting | 咨询 | 咨询服务、顾问费 |
| material | 材料 | 教材、设计物料 |
| other | 其他 | 其他费用 |

## 输出格式

- **PDF（默认）：** 通过 Playwright `page.pdf()` 生成
- **HTML（预览）：** 仅预览时使用

## 核心规则

1. **LLM 输出 JSON，不输出 HTML** — 样式全部由模板控制
2. **Schema 是数据源** — 所有输入必须映射到 QuoteDocument
3. **doc_type 控制条件渲染** — 必须显式声明 `"quotation"` | `"outline"` | `"mixed"`
4. **品牌一致性** — Logo 右上角、深蓝页眉、蓝色点缀
5. **中英双语** — 单文档支持中文和英文
6. **PDF 是最终输出** — 使用 Playwright 将 HTML 转为 PDF
7. **禁止直接注入 CSS** — 所有样式来自模板

## 文件结构

```
jackyshen-gen-quotation/
├── SKILL.md                 # 技能定义文件
├── config/
│   └── config.yaml          # 固定配置信息
├── scripts/
│   └── render_quotation.py  # 渲染脚本
├── templates/
│   └── modern/
│       └── quotation.html   # Jinja2 HTML 模板
├── output/                   # 渲染输出目录
└── logo.png                 # 品牌 Logo
```

## 渲染流程

1. 用户提供信息（自然语言/结构化数据）
2. LLM 提取并结构化为 QuoteDocument JSON
3. JSON 传入 `templates/modern/quotation.html` Jinja2 模板
4. 模板渲染生成 HTML，输出到 `output/quotation_output.html`
5. Playwright 将 HTML 转为 PDF，输出到 `output/`

> **注意：** 始终使用 `scripts/render_quotation.py` 中的 Python 脚本，不要重写 Node.js 或 JavaScript 脚本。

## 条件渲染对照表

模板根据 `doc_type` 字段决定显示哪些区块：

| 字段 | quotation | outline | mixed |
|------|-----------|---------|-------|
| 报价明细 pricing_items | ✅ | ❌ | ✅ |
| 银行账户 signature | ✅ | ❌ | ✅ |
| 课程大纲 outline | ❌ | ✅ | ✅ |
| 备注 notes | ✅ | ✅ | ✅ |