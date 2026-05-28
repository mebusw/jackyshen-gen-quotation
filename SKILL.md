---
name: jackyshen-gen-quotation
description: Generate professional PDF quotations, training proposals, and business documents for Chinese enterprises. Trigger when the user mentions 报价单(quotation)、报价(bid/pricing)、提案(proposal)、培训方案(training plan)、商业文档(business document)、生成PDF(generate PDF)，or when they provide details about training services, consulting fees, or pricing. Works with both Chinese and English content.
---

# Quotation & Business Document Generator

Generate brand-consistent, professionally styled PDF quotations and training proposals from natural language, Markdown, or structured data.
Always use existing python scripts in `scripts/render_quotation.py`, don't rewrite nodejs or javascripts scripts.

## Core Flow

```
User Input (自然语言 / Markdown / 结构化数据)
                ↓
    LLM Structured Extraction
                ↓
  QuoteDocument Schema (Pydantic)
                ↓
     Jinja2 Template Render
                ↓
        HTML Output
                ↓
      Playwright PDF
                ↓
        PDF Output
```

## Brand Theme: UPerform

**Primary:** `#083A67` (深海蓝 Navy)
**Secondary:** `#4F82BA` (钢蓝 Steel Blue)
**Accent:** `#FF9B7D` (珊瑚橙 Coral)
**Background:** `#FFFFFF` / `#FFF0D1` (暖米色)

Logo position: **top-right corner** of the header.

## Step 1 — Identify Document Type

根据原始输入自动判断生成的类型，如果不确定，Ask the user: **"请确认文档类型"**

| 类型 | 说明 | key fields |
|------|------|------------|
| `quotation` | 报价单/报价方案 | pricing_items, total, payment_terms |
| `proposal` | 培训方案/课程大纲 | outline, modules, objectives |
| `mixed` | 报价单 + 课程大纲 | both above |

If unclear, default to `mixed`.

## Step 2 — Gather Information

Collect these fields in order. Ask the user for any missing required fields.

### 必须字段

固定信息存放在  `config/config.yaml` 文件里，应作为默认值

```markdown
## 必需信息

1. **贵司信息**
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

## Step 3 — Structure with QuoteDocument Schema

Always produce a structured JSON matching this schema:

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

### CourseOutline (optional)

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

## Step 4 — Render to HTML → PDF

Use the **Jinja2 template** approach. Do NOT let the LLM generate HTML directly.

**Template path:** `templates/modern/quotation.html`

The template uses UPerform brand theme:
- Header: deep navy gradient (`#041C32` → `#083A67` → `#0A477E`)
- Accent line: coral orange (`#FF9B7D`)
- Logo: top-right corner
- Customer section: warm beige background (`#F1E2C5`)
- Notes section: pale beige (`#FFF0D1`)
- Bank section: sky blue (`#EBF4FF`)

**Key rule:** The LLM outputs JSON → JSON goes into Jinja2 → Jinja2 produces HTML → Playwright renders PDF. LLM never writes final HTML.

## Step 5 — Output Format

**Default output: PDF file** via Playwright `page.pdf()`

For HTML preview only, use `html` output.

## Quick Start Template

When user says "生成报价单" or similar, reply with:

```markdown
好的，我来帮您生成专业报价单。

请提供以下信息（可以一次性全部提供，也可以逐项回答）：

1. **客户信息** — 客户名称、公司名
2. **服务项目** — 培训/咨询内容、人数、天数、单价
3. **文档标题** — 报价单标题
4. **报价日期** — YYYY/M/D
5. **付款信息** — 银行账户信息（可选）
```

## Category Reference

| category | 中文 | 示例 |
|----------|------|------|
| training | 培训 | 讲师授课、培训课程 |
| travel | 差旅 | 讲师差旅、交通住宿 |
| interview | 访谈 | 前期调研、访谈 |
| consulting | 咨询 | 咨询服务、顾问费 |
| material | 材料 | 教材、设计物料 |
| other | 其他 | 其他费用 |

## Sample Structure (from parsed document)

```
公司: Shanghai UPerform Limited
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

## Important Principles

1. **AI outputs JSON, not HTML** — Templates control all styling
2. **Schema is the source of truth** — All inputs must map to QuoteDocument
3. **Brand consistency** — Logo top-right, navy header, coral accents
4. **Chinese + English** — Support both languages in a single document
5. **PDF is final output** — Use Playwright to convert HTML to PDF
6. **No direct CSS injection** — All styles come from template

## Error Handling

- Missing required field → Ask user explicitly for that field
- Unclear category → Ask user to confirm category
- Missing template → Fall back to basic HTML structure
- Parsing failure → Show user the raw text and ask to correct