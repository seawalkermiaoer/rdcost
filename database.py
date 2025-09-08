#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化和操作模块
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class WeeklyReportDB:
    """周报表数据库操作类"""
    
    def __init__(self, db_path: str = "rd_report.db"):
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建周报表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monday_date DATE NOT NULL,
                sunday_date DATE NOT NULL,
                online_requirements INTEGER DEFAULT 0,
                online_req_count INTEGER DEFAULT 0,
                fixed_bugs INTEGER DEFAULT 0,
                bug_fix_rate REAL DEFAULT 0.0,
                release_orders INTEGER DEFAULT 0,
                release_failures INTEGER DEFAULT 0,
                new_reuse_units INTEGER DEFAULT 0,
                new_reuse_events INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_weekly_report(self, data: Dict) -> int:
        """插入周报数据
        
        Args:
            data: 周报数据字典
            
        Returns:
            插入记录的ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否存在相同时间范围的记录
        cursor.execute("""
            SELECT id FROM weekly_reports 
            WHERE monday_date = ? AND sunday_date = ?
        """, (data['monday_date'], data['sunday_date']))
        
        existing_record = cursor.fetchone()
        if existing_record:
            conn.close()
            raise ValueError(f"该时间范围 ({data['monday_date']} 至 {data['sunday_date']}) 已存在记录 (ID: {existing_record[0]})，无法重复添加")
        
        cursor.execute("""
            INSERT INTO weekly_reports (
                monday_date, sunday_date, online_requirements, online_req_count,
                fixed_bugs, bug_fix_rate, release_orders, release_failures,
                new_reuse_units, new_reuse_events
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['monday_date'],
            data['sunday_date'],
            data['online_requirements'],
            data['online_req_count'],
            data['fixed_bugs'],
            data['bug_fix_rate'],
            data['release_orders'],
            data['release_failures'],
            data['new_reuse_units'],
            data['new_reuse_events']
        ))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    def get_all_reports(self) -> List[Dict]:
        """获取所有周报数据
        
        Returns:
            周报数据列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM weekly_reports 
            ORDER BY monday_date DESC
        """)
        
        reports = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return reports
    
    def get_report_by_id(self, report_id: int) -> Optional[Dict]:
        """根据ID获取周报数据
        
        Args:
            report_id: 周报ID
            
        Returns:
            周报数据字典或None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM weekly_reports WHERE id = ?", 
            (report_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_report(self, report_id: int, data: Dict) -> bool:
        """更新周报数据
        
        Args:
            report_id: 周报ID
            data: 更新的数据字典
            
        Returns:
            更新是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute(
            "SELECT id FROM weekly_reports WHERE id = ?", 
            (report_id,)
        )
        
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"记录 ID: {report_id} 不存在")
        
        # 直接更新记录，不进行时间范围重复检查
        # 因为这是更新已存在的记录，允许保持相同的时间范围
        cursor.execute("""
            UPDATE weekly_reports SET
                monday_date = ?, sunday_date = ?, online_requirements = ?,
                online_req_count = ?, fixed_bugs = ?, bug_fix_rate = ?,
                release_orders = ?, release_failures = ?, new_reuse_units = ?,
                new_reuse_events = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data['monday_date'],
            data['sunday_date'],
            data['online_requirements'],
            data['online_req_count'],
            data['fixed_bugs'],
            data['bug_fix_rate'],
            data['release_orders'],
            data['release_failures'],
            data['new_reuse_units'],
            data['new_reuse_events'],
            report_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_report(self, report_id: int) -> bool:
        """删除周报数据
        
        Args:
            report_id: 周报ID
            
        Returns:
            删除是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM weekly_reports WHERE id = ?", (report_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_week_dates(self, date_str: str) -> tuple:
        """根据给定日期获取该周的周一和周日日期
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            (周一日期, 周日日期) 元组
        """
        date = datetime.strptime(date_str, '%Y-%m-%d')
        monday = date - timedelta(days=date.weekday())
        sunday = monday + timedelta(days=6)
        
        return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')


if __name__ == "__main__":
    # 测试数据库初始化
    db = WeeklyReportDB()
    print("数据库初始化完成")