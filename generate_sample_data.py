#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成近7周的测试数据
"""

import random
from datetime import datetime, timedelta
from database import WeeklyReportDB


def generate_sample_data():
    """生成近7周的测试数据"""
    db = WeeklyReportDB()
    
    # 获取当前日期
    today = datetime.now().date()
    
    # 计算7周前的周一
    current_monday = today - timedelta(days=today.weekday())
    start_monday = current_monday - timedelta(weeks=6)
    
    print("开始生成近7周的测试数据...")
    
    for week in range(7):
        # 计算当前周的周一和周日
        monday = start_monday + timedelta(weeks=week)
        sunday = monday + timedelta(days=6)
        
        # 生成随机但合理的数据
        # 基础值随着周数有一定的趋势变化
        base_trend = 1 + (week * 0.1)  # 轻微上升趋势
        
        # 上线需求数 (5-20)
        online_requirements = random.randint(5, 15) + int(week * 0.5)
        
        # 需求关联req数 (通常是需求数的1-3倍)
        online_req_count = online_requirements * random.randint(1, 3)
        
        # 修复BUG数 (3-25)
        fixed_bugs = random.randint(3, 20) + int(week * 0.3)
        
        # BUG按时修复率 (80-100%)
        bug_fix_rate = round(random.uniform(85.0, 100.0), 1)
        
        # 发布工单数 (8-30)
        release_orders = random.randint(8, 25) + int(week * 0.4)
        
        # 发布失败数 (0-5，通常较少)
        release_failures = random.randint(0, min(5, release_orders // 5))
        
        # 新增复用unit数 (1-10)
        new_reuse_units = random.randint(1, 8) + int(week * 0.2)
        
        # 新增复用事件数 (2-15)
        new_reuse_events = random.randint(2, 12) + int(week * 0.3)
        
        # 准备数据
        report_data = {
            'monday_date': monday.strftime('%Y-%m-%d'),
            'sunday_date': sunday.strftime('%Y-%m-%d'),
            'online_requirements': online_requirements,
            'online_req_count': online_req_count,
            'fixed_bugs': fixed_bugs,
            'bug_fix_rate': bug_fix_rate,
            'release_orders': release_orders,
            'release_failures': release_failures,
            'new_reuse_units': new_reuse_units,
            'new_reuse_events': new_reuse_events
        }
        
        # 插入数据
        report_id = db.insert_weekly_report(report_data)
        print(f"第{week+1}周数据已生成 (ID: {report_id}): {monday} 至 {sunday}")
        print(f"  - 上线需求: {online_requirements}, 修复BUG: {fixed_bugs}, 修复率: {bug_fix_rate}%")
    
    print("\n✅ 测试数据生成完成！")
    print("\n📊 数据概览:")
    
    # 显示生成的数据统计
    reports = db.get_all_reports()
    if reports:
        total_requirements = sum(r['online_requirements'] for r in reports)
        total_bugs = sum(r['fixed_bugs'] for r in reports)
        avg_fix_rate = sum(r['bug_fix_rate'] for r in reports) / len(reports)
        
        print(f"  - 总记录数: {len(reports)}")
        print(f"  - 累计上线需求: {total_requirements}")
        print(f"  - 累计修复BUG: {total_bugs}")
        print(f"  - 平均修复率: {avg_fix_rate:.1f}%")
    
    print("\n🚀 现在可以运行 'streamlit run app.py' 查看数据可视化效果！")


if __name__ == "__main__":
    generate_sample_data()