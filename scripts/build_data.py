"""
Build Site Data - 合并职业数据和评分，生成前端所需的 data.json

Usage:
    python build_data.py
"""

import json
from pathlib import Path


def main():
    # 加载职业数据
    with open("data/occupations.json", "r", encoding="utf-8") as f:
        occupations = json.load(f)
    
    # 如果有独立的评分文件，合并评分
    scores_path = Path("data/scores.json")
    if scores_path.exists():
        with open(scores_path, "r", encoding="utf-8") as f:
            scores_list = json.load(f)
            scores = {s["id"]: s for s in scores_list}
        
        for occ in occupations:
            if occ["id"] in scores:
                occ["exposure"] = scores[occ["id"]]["exposure"]
                occ["rationale"] = scores[occ["id"]]["rationale"]
    
    # 构建前端数据
    site_data = {
        "meta": {
            "title": "中国就业市场 AI 暴露度分析",
            "description": "基于《中华人民共和国职业分类大典》，分析中国主要职业被AI影响的程度",
            "total_occupations": len(occupations),
            "total_jobs": sum(o["employment"] for o in occupations),
            "data_source": "国家统计局、人社部《职业分类大典(2022)》",
            "scoring_method": "Claude/GPT AI评分 (0-10)"
        },
        "categories": sorted(list(set(o["category"] for o in occupations))),
        "occupations": []
    }
    
    for occ in occupations:
        site_data["occupations"].append({
            "id": occ["id"],
            "name": occ["name"],
            "category": occ["category"],
            "employment": occ["employment"],
            "salary": occ["median_salary"],
            "education": occ["education"],
            "exposure": occ["exposure"],
            "rationale": occ.get("rationale", ""),
            "description": occ.get("description", "")
        })
    
    # 计算统计信息
    total_jobs = site_data["meta"]["total_jobs"]
    weighted_exposure = sum(
        o["employment"] * o["exposure"] for o in occupations
    ) / total_jobs
    site_data["meta"]["weighted_avg_exposure"] = round(weighted_exposure, 1)
    
    # 按暴露度分层统计
    tiers = {
        "0-1": {"label": "几乎不受影响", "jobs": 0, "wages": 0},
        "2-3": {"label": "低影响", "jobs": 0, "wages": 0},
        "4-5": {"label": "中等影响", "jobs": 0, "wages": 0},
        "6-7": {"label": "较高影响", "jobs": 0, "wages": 0},
        "8-9": {"label": "高度影响", "jobs": 0, "wages": 0},
        "10":  {"label": "最大影响", "jobs": 0, "wages": 0},
    }
    
    for occ in occupations:
        e = occ["exposure"]
        if e <= 1: tier = "0-1"
        elif e <= 3: tier = "2-3"
        elif e <= 5: tier = "4-5"
        elif e <= 7: tier = "6-7"
        elif e <= 9: tier = "8-9"
        else: tier = "10"
        
        tiers[tier]["jobs"] += occ["employment"]
        tiers[tier]["wages"] += occ["employment"] * occ["median_salary"]
    
    site_data["tiers"] = tiers
    
    # 保存
    output_path = "site/data.json"
    Path("site").mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(site_data, f, ensure_ascii=False)
    
    print(f"数据已构建: {output_path}")
    print(f"职业数: {len(occupations)}")
    print(f"总就业人数: {total_jobs:,}")
    print(f"加权平均暴露度: {weighted_exposure:.1f}/10")
    
    # 打印分层统计
    print("\n暴露度分层统计:")
    for tier, info in tiers.items():
        pct = info["jobs"] / total_jobs * 100
        print(f"  {tier} ({info['label']}): {info['jobs']:>12,} 人 ({pct:.1f}%)")


if __name__ == "__main__":
    main()
