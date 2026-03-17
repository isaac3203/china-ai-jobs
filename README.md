# 中国就业市场 AI 暴露度分析

分析中国主要职业被 AI 影响的程度，通过交互式 Treemap 可视化展示。

灵感来源：[Andrej Karpathy - AI Exposure of the US Job Market](https://karpathy.ai/jobs/)

## 效果预览

交互式 Treemap：矩形面积 = 就业人数，颜色 = AI 暴露度（绿色安全 → 红色高暴露）

## 数据来源

- **职业分类**：参考《中华人民共和国职业分类大典（2022年版）》8 大类体系
- **就业人数**：基于国家统计局分行业就业数据估算
- **薪资数据**：综合国家统计局城镇单位就业人员平均工资和招聘平台数据
- **AI 评分**：使用 LLM（Claude/GPT）对每个职业进行 0-10 分的 AI 暴露度评估

## 项目结构

```
china-ai-jobs/
├── data/
│   └── occupations.json    # 职业数据（含就业人数、薪资、学历、AI评分）
├── scripts/
│   ├── score.py            # AI 评分脚本（调用 Claude/GPT API）
│   └── build_data.py       # 构建前端数据
├── site/
│   ├── index.html          # 交互式 Treemap 可视化
│   └── data.json           # 前端数据（由 build_data.py 生成）
└── README.md
```

## 快速开始

### 1. 本地预览

```bash
cd site
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

### 2. 更新 AI 评分（可选）

如果想用最新的 LLM 重新评分：

```bash
# 使用 Claude API
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
python scripts/score.py

# 或使用 OpenAI API
pip install openai
export OPENAI_API_KEY=your_key_here
python scripts/score.py --provider openai
```

### 3. 重新构建网站数据

```bash
python scripts/build_data.py
```

## 部署

### GitHub Pages

```bash
git init
git add .
git commit -m "init: 中国就业市场 AI 暴露度"
git remote add origin https://github.com/your-username/china-ai-jobs.git
git push -u origin main

# 在 GitHub 仓库 Settings → Pages → Source 选择 main 分支的 /site 目录
```

### Vercel

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署 site 目录
cd site && vercel
```

## AI 暴露度评分标准

| 分数 | 含义 | 举例 |
|------|------|------|
| 0-1 | 几乎不受影响 | 建筑工人、清洁工、消防员 |
| 2-3 | 低影响 | 护士、电工、快递员、厨师 |
| 4-5 | 中等影响 | 医生、教师、公务员 |
| 6-7 | 较高影响 | 工程师、管理者、律师 |
| 8-9 | 高度影响 | 软件工程师、翻译、编辑、客服 |
| 10 | 最大影响 | 数据录入员 |

## 免责声明

AI 暴露度评分由大语言模型生成，仅供参考和可视化探索。这不是学术论文，不是经济预测，也不构成就业建议。用 LLM 评估 LLM 对职业的影响，存在明显的自我参照偏差。

## License

MIT
