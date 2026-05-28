---
name: jackyshen-gen-quotation
description: 生成专业PDF报价单、培训提案和商业文档。当用户提及报价单、报价、提案、培训方案、商业文档、生成PDF，或提供培训服务、咨询费用、定价详情时触发。支持中英文内容。
---

# 报价单 & 商业文档生成器

从自然语言、Markdown 或结构化数据生成品牌一致、风格专业的 PDF 报价单和培训提案。
始终使用 `scripts/render_quotation.py` 中的 Python 脚本，不要重写 Node.js 或 JavaScript 脚本。

## 核心流程

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

## 品牌主题：UPerform

**主色：** `#083A67`（深海蓝 Navy）
**辅色：** `#4F82BA`（钢蓝 Steel Blue）
**点缀色：** `#FFFFFF`（白色 White）
**背景色：** `#FFFFFF`（白色）

Logo 位置：**页面右上角**。

## 步骤一 — 识别文档类型

根据原始输入自动判断生成的类型，如果不确定，询问用户：**"请确认文档类型"**

| 类型 | 说明 | 关键字段 |
|------|------|----------|
| `quotation` | 报价单/报价方案 | pricing_items, total, payment_terms |
| `proposal` | 培训方案/课程大纲 | outline, modules, objectives |
| `mixed` | 报价单 + 课程大纲 | 两者兼有 |

不明确时，默认为 `mixed`。

## 步骤二 — 收集信息

按顺序收集以下字段，如有缺失请询问用户。

### 必须字段

固定信息存放在 `config/config.yaml` 文件里，应作为默认值。

```markdown
## 必需信息

1. **我司信息**
   - 公司名称 company_name
   - 地址 company_address (可选)
   - 电话 company_tel (可选)
   - 邮箱 company_email (可选)

2. **客户信息**
   - 客户名称 customer_name
   - 联系人 contact_person (可选)

3. **文档信息**
   - 报价单号 quotation_no (格式: QL-YYYYMMDD-序号)
   - 报价日期 quotation_date (YYYY/M/D)
   - 文档标题 title

4. **报价项目** (至少1项)
   - 服务名称 service_name
   - 单价 unit_price (CNY)
   - 数量 quantity
   - 单位 unit (天/人/次/项)
   - 分类 category: training | travel | interview | consulting | material | other

5. **汇总信息**
   - 小计 subtotal
   - 税率 tax_rate (如: 6%)
   - 税费 tax_amount
   - 总计 total_amount
   - 币种 currency (默认 CNY)
   - 含税否 tax_included (可选)

6. **付款条款**
   - 付款方式 payment_method (可选)
   - 付款阶段 payment_schedule (可选)
   - 银行信息 bank_info (可选)

7. **有效期**
   - 有效至 valid_until (可选)
   - 有效期天数 validity_days (可选)

8. **签章信息**
   - 账户名称 account_name
   - 开户行 bank_name
   - 银行账号 account_number
```

### 可选字段

- 课程大纲 (CourseOutline) — title, modules[], learning_objectives[], target_audience[]
- 备注 notes[]
- 品牌配置 branding{logo_path, primary_color, secondary_color, accent_color}

## 步骤三 — 按 QuoteDocument Schema 组织数据

输出必须匹配以下 Schema 的结构化 JSON：

```python
QuoteDocument:
  company: CompanyInfo         # 供方信息
  customer: CustomerInfo       # 需方信息
  quotation: QuotationInfo     # 文档基本信息
  pricing_items: list[PricingItem]  # 报价明细
  pricing_summary: PricingSummary  # 汇总
  payment_terms: PaymentTerms  # 付款条款
  tax: TaxInfo                # 税费
  validity: ValidityInfo      # 有效期
  outline: CourseOutline | None  # 课程大纲(可选)
  notes: list[str] = []      # 备注
  signature: SignatureInfo   # 签章信息
  branding: BrandingConfig   # 品牌配置
```

### PricingItem

```python
PricingItem:
  category: str       # training | travel | interview | consulting | material | other
  service_name: str  # 服务名称
  unit_price: float  # 单价
  quantity: float    # 数量
  unit: str          # 天/人/次/项
  days: float | None # 天数(可选)
  subtotal: float    # 小计
  remarks: str | None # 备注(可选)
```

### CourseOutline (可选)

```python
CourseOutline:
  title: str
  modules: list[CourseModule]
  learning_objectives: list[str] = []
  target_audience: list[str] = []

CourseModule:
  module_title: str
  duration: str | None  # 如 "2小时"
  topics: list[str]
  exercises: list[str] = []
```

## 步骤四 — Jinja2 渲染为 HTML → PDF

使用 **Jinja2 模板**方式。禁止 LLM 直接生成 HTML。

**模板路径：** `templates/modern/quotation.html`

模板使用 UPerform 品牌主题：
- 页眉：深海蓝 (`#083A67`) + 白色背景
- 强调线：深海蓝 (`#083A67`)
- Logo：右上角
- 客户区域：白色背景 + 深海蓝边框
- 备注区域：白色背景 + 深海蓝边框
- 银行账户区域：白色背景 + 深海蓝边框
- 所有文字：黑色 (`#1a1a1a`) + 白色背景
- 字体：宋体 (SimSun) 用于中文
- 内容区域：左右各 20% 边距

**核心规则：** LLM 输出 JSON → JSON 传入 Jinja2 → Jinja2 生成 HTML → Playwright 渲染 PDF。LLM 绝不直接写 HTML。

## 步骤五 — 输出格式

**默认输出：PDF 文件**，通过 Playwright `page.pdf()` 生成。

仅预览 HTML 时，使用 `html` 输出。

## 快速开始模板

当用户说"生成报价单"或类似内容时，回复：

```markdown
好的，我来帮您生成专业报价单。

请提供以下信息（可以一次性全部提供，也可以逐项回答）：

1. **客户信息** — 客户名称、公司名
2. **服务项目** — 培训/咨询内容、人数、天数、单价
3. **文档标题** — 报价单标题
4. **报价日期** — YYYY/M/D
5. **付款信息** — 银行账户信息（可选）
```

## 分类参考

| category | 中文 | 示例 |
|----------|------|------|
| training | 培训 | 讲师授课、培训课程 |
| travel | 差旅 | 讲师差旅、交通住宿 |
| interview | 访谈 | 前期调研、访谈 |
| consulting | 咨询 | 咨询服务、顾问费 |
| material | 材料 | 教材、设计物料 |
| other | 其他 | 其他费用 |

## 示例结构

```
公司: 上海优普丰企业管理有限公司
客户: 皇家 ROYAL CANIN
日期: 2026/5/28

报价项目:
| 项目 | 时长 | 人数 | 单价 | 小计 |
|------|------|------|------|------|
| 变革管理敏捷项目培训 | 2天 | 30人以内 | 25,000.00/天 | 50,000.00 |
| 课前访谈调研（线上） | 0.5天 | — | — | 5,000.00 |
| 讲师差旅 | 2天 | — | — | 5,000.00 |

含税共计: 60,000.00 CNY

备注:
- 培训时间: 9:00am-5:00pm, 1.5小时午餐
- 报价含讲师差旅、课程费、教材费等

银行信息:
- 开户行: 上海银行愚园路支行
- 账号: 3164 1803 0002 50561
- 账户名称: 上海优普丰企业管理有限公司
```

## 重要原则

1. **L LLM 输出 JSON，不输出 HTML** — 样式全部由模板控制
2. **Schema 是数据源** — 所有输入必须映射到 QuoteDocument
3. **品牌一致性** — Logo 右上角、深蓝页眉、蓝色点缀
4. **中英双语** — 单文档支持中文和英文
5. **PDF 是最终输出** — 使用 Playwright 将 HTML 转为 PDF
6. **禁止直接注入 CSS** — 所有样式来自模板

## 错误处理

- 缺少必填字段 → 明确询问用户
- 分类不明确 → 请用户确认分类
- 模板缺失 → 回退到基础 HTML 结构
- 解析失败 → 展示原始文本并请用户修正