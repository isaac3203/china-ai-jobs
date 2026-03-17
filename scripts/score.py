"""
AI Exposure Scoring Script for Chinese Occupations
使用 Claude API 或 OpenAI API 为每个职业打 AI 暴露度评分

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
    python score.py

Or for OpenAI:
    pip install openai
    export OPENAI_API_KEY=your_key_here
    python score.py --provider openai
"""

import json
import os
import time
import argparse
from pathlib import Path

SCORING_PROMPT = """你是一位AI和劳动经济学专家。请评估以下中国职业被AI替代或重塑的程度。

评分标准（0-10分）：
- 0-1分：几乎不受影响。纯体力劳动，需要在复杂物理环境中操作，如建筑工人、清洁工。
- 2-3分：低影响。主要是体力或现场工作，AI仅能辅助少量环节，如护士、电工、消防员。
- 4-5分：中等影响。工作中有部分数字化环节可被AI辅助，但核心职能仍需人工，如医生、零售店员。
- 6-7分：较高影响。大量工作内容可被AI辅助或部分替代，工作方式将显著改变，如教师、工程师、管理者。
- 8-9分：高度影响。工作几乎完全在电脑上完成，核心任务（写作、编程、分析、设计）AI已能高质量完成，如软件工程师、翻译、编辑。
- 10分：最大影响。纯粹的数字信息处理，完全可自动化，如数据录入员。

关键判断信号：
1. 这份工作能否完全在家用电脑上完成？如果是，AI暴露度至少为7。
2. 工作的核心产出是数字化的（文本、代码、数据、设计）还是物理性的（实物、服务、操作）？
3. 工作是否需要面对面的人际互动或身体接触？
4. 工作环境是否固定且可预测，还是多变且需要即时判断？

请注意中国特有的因素：
- 体制内岗位（公务员、事业单位）的替代速度可能较慢
- 中国劳动力成本相对较低，部分自动化经济动力不足
- 中国在某些AI应用（如AI客服、无人零售）上走在前列
- 中国特有职业如中医、社区工作者等有独特的AI暴露特征

职业信息：
名称：{name}
类别：{category}
描述：{description}
学历要求：{education}

请仅以JSON格式回复，不要包含其他文字：
{{"exposure": <0-10的整数>, "rationale": "<2-3句话解释关键因素>"}}
"""


def score_with_anthropic(occupation: dict) -> dict:
    """使用 Claude API 评分"""
    import anthropic
    
    client = anthropic.Anthropic()
    
    prompt = SCORING_PROMPT.format(
        name=occupation["name"],
        category=occupation["category"],
        description=occupation["description"],
        education=occupation["education"]
    )
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text.strip()
    # 清理可能的 markdown 格式
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    return json.loads(response_text)


def score_with_openai(occupation: dict) -> dict:
    """使用 OpenAI API 评分"""
    import openai
    
    client = openai.OpenAI()
    
    prompt = SCORING_PROMPT.format(
        name=occupation["name"],
        category=occupation["category"],
        description=occupation["description"],
        education=occupation["education"]
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    
    response_text = response.choices[0].message.content.strip()
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    return json.loads(response_text)


def main():
    parser = argparse.ArgumentParser(description="Score Chinese occupations for AI exposure")
    parser.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic",
                       help="API provider to use (default: anthropic)")
    parser.add_argument("--input", default="data/occupations.json",
                       help="Input occupations file")
    parser.add_argument("--output", default="data/scores.json",
                       help="Output scores file")
    parser.add_argument("--delay", type=float, default=1.0,
                       help="Delay between API calls in seconds")
    args = parser.parse_args()
    
    # 加载职业数据
    with open(args.input, "r", encoding="utf-8") as f:
        occupations = json.load(f)
    
    # 加载已有评分（支持断点续传）
    scores = {}
    if Path(args.output).exists():
        with open(args.output, "r", encoding="utf-8") as f:
            existing = json.load(f)
            scores = {s["id"]: s for s in existing}
        print(f"已加载 {len(scores)} 条已有评分")
    
    # 选择评分函数
    score_fn = score_with_anthropic if args.provider == "anthropic" else score_with_openai
    
    # 逐个评分
    for i, occ in enumerate(occupations):
        if occ["id"] in scores:
            print(f"[{i+1}/{len(occupations)}] 跳过已评分: {occ['name']}")
            continue
        
        print(f"[{i+1}/{len(occupations)}] 评分中: {occ['name']}...", end=" ")
        
        try:
            result = score_fn(occ)
            scores[occ["id"]] = {
                "id": occ["id"],
                "name": occ["name"],
                "exposure": result["exposure"],
                "rationale": result["rationale"]
            }
            print(f"得分: {result['exposure']}/10")
            
            # 每次评分后保存（防止中断丢失）
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(list(scores.values()), f, ensure_ascii=False, indent=2)
            
            time.sleep(args.delay)
            
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(3)  # 出错后等待更久
    
    print(f"\n完成！共评分 {len(scores)} 个职业，结果保存至 {args.output}")


if __name__ == "__main__":
    main()
