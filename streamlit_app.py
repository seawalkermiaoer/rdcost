#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit 周报表管理应用
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import WeeklyReportDB
from streamlit_option_menu import option_menu


# 页面配置
st.set_page_config(
    page_title="周报表管理系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 登录验证
def check_credentials(username, password):
    """验证用户名和密码"""
    import hashlib
    import os
    import base64
    
    # 使用环境变量或secrets存储盐值，这里使用固定盐值作为示例
    # 实际应用中应该使用环境变量或其他安全方式存储
    salt = "RD_COST_SALT"
    
    # 对密码进行加盐哈希
    def hash_password(pwd, salt_value):
        salted = (pwd + salt_value).encode('utf-8')
        return hashlib.sha256(salted).hexdigest()
    
    try:
        # 首选从secrets中获取凭据
        secrets = st.secrets["login"]
        stored_username = secrets["username"]
        stored_password_hash = secrets.get("password_hash")
        
        # 如果存储的是哈希密码
        if stored_password_hash:
            return username == stored_username and hash_password(password, salt) == stored_password_hash
        # 如果存储的是明文密码（不推荐）
        else:
            return username == stored_username and password == secrets["password"]
    except Exception as e:
        # 回退到默认凭据（仅用于开发环境）
        default_username = "xd"
        print(hash_password(password, salt) == stored_password_hash)
        default_password_hash = "5c28b8dab232deda9713e631a3d5e2718f5cb082f5e8a688eec4742c3ac56e77"
        
        return username == default_username and hash_password(password, salt) == default_password_hash

def login_page():
    """显示登录页面"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
        margin-top: 100px;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header"><h1>🔐 登录</h1></div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            
            submitted = st.form_submit_button("登录", use_container_width=True, type="primary")
            
            if submitted:
                if check_credentials(username, password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ 用户名或密码错误")
        
        st.markdown('</div>', unsafe_allow_html=True)

# 检查登录状态
if not st.session_state.authenticated:
    login_page()
    st.stop()

# 初始化数据库
def init_database():
    return WeeklyReportDB()

db = init_database()

# 侧边栏导航
# 设置侧边栏样式，使其更窄
st.markdown("""
<style>
.css-1d391kg {
    width: 200px !important;
}
.css-1lcbmhc {
    width: 200px !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    # 显示当前登录用户
    st.markdown(f"👤 **当前用户**: xd")
    
    selected = option_menu(
        "主菜单",
        ["数据可视化", "数据录入", "数据管理"],
        icons=["bar-chart", "pencil-square", "table"],
        menu_icon="cast",
        default_index=0,
    )
    
    # 添加登出按钮
    if st.button("🚪 登出", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# 主标题
st.title("📊 周报表管理系统")

def calculate_week_over_week_change(current_value, previous_value):
    """计算周环比变化"""
    if previous_value == 0:
        return 0 if current_value == 0 else 100
    return ((current_value - previous_value) / previous_value) * 100

def format_change_display(change):
    """格式化变化显示"""
    if change > 0:
        return f"📈 +{change:.1f}%"
    elif change < 0:
        return f"📉 {change:.1f}%"
    else:
        return "➡️ 0.0%"

def format_change_with_color(value, change):
    """格式化带颜色的变化显示"""
    if change > 0:
        return f"{value} <span style='color: #28a745; font-weight: bold;'>▲(+{change:.1f}%)</span>"
    elif change < 0:
        return f"{value} <span style='color: #dc3545; font-weight: bold;'>▼({change:.1f}%)</span>"
    else:
        return f"{value} <span style='color: #6c757d;'>➡️(0.0%)</span>"

# 数据录入页面
if selected == "数据录入":
    st.header("📝 周报数据录入")
    
    with st.form("weekly_report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 时间范围")
            # 选择日期，自动计算周一和周日
            selected_date = st.date_input(
                "选择本周任意一天",
                value=datetime.now().date(),
                help="系统会自动计算该周的周一和周日日期"
            )
            
            # 计算周一和周日日期
            monday_date, sunday_date = db.get_week_dates(selected_date.strftime('%Y-%m-%d'))
            st.info(f"本周范围: {monday_date} (周一) 至 {sunday_date} (周日)")
            
            st.subheader("🚀 需求相关")
            online_requirements = st.number_input(
                "上线的需求数",
                min_value=0,
                value=0,
                help="本周成功上线的需求数量"
            )
            
            online_req_count = st.number_input(
                "上线需求关联的req数",
                min_value=0,
                value=0,
                help="上线需求关联的需求文档数量"
            )
            
            st.subheader("🐛 BUG相关")
            fixed_bugs = st.number_input(
                "解决的BUG数",
                min_value=0,
                value=0,
                help="本周解决的BUG数量"
            )
        
        with col2:
            st.subheader("🚀 发布相关")
            release_orders = st.number_input(
                "发布工单数",
                min_value=0,
                value=0,
                help="本周提交的发布工单数量"
            )
            
            release_failures = st.number_input(
                "发布失败数",
                min_value=0,
                value=0,
                help="本周发布失败的工单数量"
            )
            
            st.subheader("🔄 复用相关")
            new_reuse_units = st.number_input(
                "新增可复用的最小单元数",
                min_value=0,
                value=0,
                help="本周新增的可复用单元数量"
            )
            
            new_reuse_events = st.number_input(
                "新增复用事件数",
                min_value=0,
                value=0,
                help="本周新增的复用事件数量"
            )
        
        # 提交按钮
        submitted = st.form_submit_button(
            "💾 保存周报数据",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # 准备数据
            report_data = {
                'monday_date': monday_date,
                'sunday_date': sunday_date,
                'online_requirements': online_requirements,
                'online_req_count': online_req_count,
                'fixed_bugs': fixed_bugs,
                'bug_fix_rate': 95.0,  # 默认值，保持数据库兼容性
                'release_orders': release_orders,
                'release_failures': release_failures,
                'new_reuse_units': new_reuse_units,
                'new_reuse_events': new_reuse_events
            }
            
            try:
                report_id = db.insert_weekly_report(report_data)
                st.success(f"✅ 周报数据保存成功！记录ID: {report_id}，周期：{monday_date} 至 {sunday_date}，上线需求数：{online_requirements}，需求关联req数：{online_req_count}，解决的BUG数：{fixed_bugs}，发布工单数：{release_orders}，发布失败数：{release_failures}，新增可复用的最小单元数：{new_reuse_units}，新增复用事件数：{new_reuse_events}")
                st.balloons()
            except Exception as e:
                st.error(f"❌ 保存失败: {str(e)}")

# 数据可视化页面
if selected == "数据可视化":
    st.header("📈 数据可视化分析")
    
    # 获取所有报告数据
    reports = db.get_all_reports()
    
    if not reports:
        st.warning("📭 暂无数据，请先在数据录入页面添加周报数据。")
    else:
        # 转换为DataFrame
        df = pd.DataFrame(reports)
        df['monday_date'] = pd.to_datetime(df['monday_date'])
        df = df.sort_values('monday_date')
        
        # 计算周环比
        metrics = ['online_requirements', 'online_req_count', 'fixed_bugs', 
                  'release_orders', 'release_failures', 
                  'new_reuse_units', 'new_reuse_events']
        
        for metric in metrics:
            df[f'{metric}_change'] = df[metric].pct_change() * 100
        
        # 近4周数据对比（移到第一部分）
        st.subheader("📊 近4周数据对比")
        
        # 获取最近4周的数据
        recent_weeks = df.tail(4) if len(df) >= 4 else df
        
        if len(recent_weeks) > 0:
            # 准备表格数据（倒序显示，最新周在顶部）
            weekly_data = []
            recent_weeks_reversed = recent_weeks.iloc[::-1]  # 倒序
            
            for i, (_, week_data) in enumerate(recent_weeks_reversed.iterrows()):
                # 格式化周期显示
                week_period = f"{week_data['monday_date'].strftime('%m-%d')} 至 {pd.to_datetime(week_data['sunday_date']).strftime('%m-%d')}"
                
                # 计算环比（与上一周对比）
                if i < len(recent_weeks_reversed) - 1:
                    # 获取上一周数据（在倒序数组中的下一个元素）
                    prev_week_data = recent_weeks_reversed.iloc[i + 1]
                    
                    # 计算各指标的环比
                    req_change = calculate_week_over_week_change(week_data['online_requirements'], prev_week_data['online_requirements'])
                    req_count_change = calculate_week_over_week_change(week_data['online_req_count'], prev_week_data['online_req_count'])
                    bug_change = calculate_week_over_week_change(week_data['fixed_bugs'], prev_week_data['fixed_bugs'])
                    release_change = calculate_week_over_week_change(week_data['release_orders'], prev_week_data['release_orders'])
                    failure_change = calculate_week_over_week_change(week_data['release_failures'], prev_week_data['release_failures'])
                    unit_change = calculate_week_over_week_change(week_data['new_reuse_units'], prev_week_data['new_reuse_units'])
                    event_change = calculate_week_over_week_change(week_data['new_reuse_events'], prev_week_data['new_reuse_events'])
                    
                    row_data = {
                        '周期': week_period,
                        '上线需求数': format_change_with_color(int(week_data['online_requirements']), req_change),
                        '需求关联req数': format_change_with_color(int(week_data['online_req_count']), req_count_change),
                        '解决的BUG数': format_change_with_color(int(week_data['fixed_bugs']), bug_change),
                        '发布工单数': format_change_with_color(int(week_data['release_orders']), release_change),
                        '发布失败数': format_change_with_color(int(week_data['release_failures']), failure_change),
                        '新增可复用的最小单元数': format_change_with_color(int(week_data['new_reuse_units']), unit_change),
                        '新增复用事件数': format_change_with_color(int(week_data['new_reuse_events']), event_change)
                    }
                else:
                    # 最早的一周没有环比数据
                    row_data = {
                        '周期': week_period,
                        '上线需求数': f"{int(week_data['online_requirements'])} (-)",
                        '需求关联req数': f"{int(week_data['online_req_count'])} (-)",
                        '解决的BUG数': f"{int(week_data['fixed_bugs'])} (-)",
                        '发布工单数': f"{int(week_data['release_orders'])} (-)",
                        '发布失败数': f"{int(week_data['release_failures'])} (-)",
                        '新增可复用的最小单元数': f"{int(week_data['new_reuse_units'])} (-)",
                        '新增复用事件数': f"{int(week_data['new_reuse_events'])} (-)"
                    }
                
                weekly_data.append(row_data)
            
            # 显示表格
            weekly_df = pd.DataFrame(weekly_data)
            
            # 使用HTML表格来支持颜色显示
            html_table = "<table style='width: 100%; border-collapse: collapse; font-size: 14px;'>"
            
            # 表头
            html_table += "<thead><tr style='background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;'>"
            for col in weekly_df.columns:
                html_table += f"<th style='padding: 12px; text-align: left; border: 1px solid #dee2e6; font-weight: bold;'>{col}</th>"
            html_table += "</tr></thead>"
            
            # 表体
            html_table += "<tbody>"
            for i, row in weekly_df.iterrows():
                bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                html_table += f"<tr style='background-color: {bg_color};'>"
                for col in weekly_df.columns:
                    html_table += f"<td style='padding: 10px; border: 1px solid #dee2e6;'>{row[col]}</td>"
                html_table += "</tr>"
            html_table += "</tbody></table>"
            
            st.markdown(html_table, unsafe_allow_html=True)
            
            # 添加说明信息
            st.info("💡 表格按时间倒序排列，最新一周在顶部。▲绿色表示上升，▼红色表示下降，➡️灰色表示无变化，'-'表示无对比数据。")
        
        # 显示最新一周的关键指标
        st.subheader("📊 本周关键指标")
        
        if len(df) >= 1:
            latest_report = df.iloc[-1]
            previous_report = df.iloc[-2] if len(df) >= 2 else None
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                change = latest_report['online_requirements_change'] if previous_report is not None else 0
                st.metric(
                    "上线需求数",
                    int(latest_report['online_requirements']),
                    delta=f"{change:.1f}%" if previous_report is not None else None
                )
            
            with col2:
                change = latest_report['fixed_bugs_change'] if previous_report is not None else 0
                st.metric(
                    "解决的BUG数",
                    int(latest_report['fixed_bugs']),
                    delta=f"{change:.1f}%" if previous_report is not None else None
                )
            
            with col3:
                change = latest_report['release_orders_change'] if previous_report is not None else 0
                st.metric(
                    "发布工单数",
                    int(latest_report['release_orders']),
                    delta=f"{change:.1f}%" if previous_report is not None else None
                )
        
        # 趋势图表
        st.subheader("📈 趋势分析")
        
        # 选择要显示的指标
        chart_options = {
            "上线需求数": "online_requirements",
            "需求关联req数": "online_req_count",
            "解决的BUG数": "fixed_bugs",
            "发布工单数": "release_orders",
            "发布失败数": "release_failures",
            "新增可复用的最小单元数": "new_reuse_units",
            "新增复用事件数": "new_reuse_events"
        }
        
        selected_metrics = st.multiselect(
            "选择要显示的指标",
            options=list(chart_options.keys()),
            default=["上线需求数", "解决的BUG数"]
        )
        
        if selected_metrics:
            # 创建趋势图
            fig = go.Figure()
            
            for metric_name in selected_metrics:
                metric_col = chart_options[metric_name]
                fig.add_trace(go.Scatter(
                    x=df['monday_date'],
                    y=df[metric_col],
                    mode='lines+markers',
                    name=metric_name,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
            
            fig.update_layout(
                title="周报指标趋势图",
                xaxis_title="周期 (周一日期)",
                yaxis_title="数值",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        


# 数据管理页面
elif selected == "数据管理":
    st.header("🗂️ 数据管理")
    
    # 获取所有报告数据
    reports = db.get_all_reports()
    
    if not reports:
        st.info("📭 暂无数据")
    else:
        # 显示数据表格
        df = pd.DataFrame(reports)
        
        # 重新排列和重命名列
        display_columns = {
            'id': 'ID',
            'monday_date': '周一日期',
            'sunday_date': '周日日期',
            'online_requirements': '上线需求数',
            'online_req_count': '需求关联req数',
            'fixed_bugs': '解决的BUG数',
            'release_orders': '发布工单数',
            'release_failures': '发布失败数',
            'new_reuse_units': '新增可复用的最小单元数',
            'new_reuse_events': '新增复用事件数',
            'created_at': '创建时间'
        }
        
        # 选择要显示的列
        df_display = df[list(display_columns.keys())].rename(columns=display_columns)
        
        st.subheader("📋 周报数据列表")
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
        # 数据统计
        st.subheader("📊 数据统计")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总记录数", len(df))
        
        with col2:
            total_requirements = df['online_requirements'].sum()
            st.metric("累计上线需求", int(total_requirements))
        
        with col3:
            total_bugs = df['fixed_bugs'].sum()
            st.metric("累计解决BUG", int(total_bugs))
        
        with col4:
            avg_release_orders = df['release_orders'].mean()
            st.metric("平均发布工单", f"{avg_release_orders:.1f}")
        
        # 编辑功能
        st.subheader("✏️ 数据编辑")
        
        if st.checkbox("启用编辑功能"):
            record_to_edit = st.selectbox(
                "选择要编辑的记录",
                options=[(row['id'], f"ID: {row['id']} - {row['monday_date']} 至 {row['sunday_date']}") 
                        for _, row in df.iterrows()],
                format_func=lambda x: x[1]
            )
            
            if record_to_edit:
                # 获取选中记录的数据
                selected_record = df[df['id'] == record_to_edit[0]].iloc[0]
                
                with st.form("edit_report_form"):
                    st.write(f"**编辑记录 ID: {selected_record['id']}**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📅 时间范围")
                        st.info(f"周期: {selected_record['monday_date']} 至 {selected_record['sunday_date']}")
                        
                        st.subheader("🚀 需求相关")
                        edit_online_requirements = st.number_input(
                            "上线的需求数",
                            min_value=0,
                            value=int(selected_record['online_requirements']),
                            help="本周成功上线的需求数量"
                        )
                        
                        edit_online_req_count = st.number_input(
                            "上线需求关联的req数",
                            min_value=0,
                            value=int(selected_record['online_req_count']),
                            help="上线需求关联的需求文档数量"
                        )
                        
                        st.subheader("🐛 BUG相关")
                        edit_fixed_bugs = st.number_input(
                            "解决的BUG数",
                            min_value=0,
                            value=int(selected_record['fixed_bugs']),
                            help="本周解决的BUG数量"
                        )
                    
                    with col2:
                        st.subheader("🚀 发布相关")
                        edit_release_orders = st.number_input(
                            "发布工单数",
                            min_value=0,
                            value=int(selected_record['release_orders']),
                            help="本周提交的发布工单数量"
                        )
                        
                        edit_release_failures = st.number_input(
                            "发布失败数",
                            min_value=0,
                            value=int(selected_record['release_failures']),
                            help="本周发布失败的工单数量"
                        )
                        
                        st.subheader("🔄 复用相关")
                        edit_new_reuse_units = st.number_input(
                            "新增可复用的最小单元数",
                            min_value=0,
                            value=int(selected_record['new_reuse_units']),
                            help="本周新增的可复用单元数量"
                        )
                        
                        edit_new_reuse_events = st.number_input(
                            "新增复用事件数",
                            min_value=0,
                            value=int(selected_record['new_reuse_events']),
                            help="本周新增的复用事件数量"
                        )
                    
                    # 提交按钮
                    submitted = st.form_submit_button(
                        "💾 更新数据",
                        type="primary",
                        use_container_width=True
                    )
                    
                    if submitted:
                        # 准备更新数据
                        update_data = {
                            'monday_date': selected_record['monday_date'],
                            'sunday_date': selected_record['sunday_date'],
                            'online_requirements': edit_online_requirements,
                            'online_req_count': edit_online_req_count,
                            'fixed_bugs': edit_fixed_bugs,
                            'bug_fix_rate': 95.0,  # 默认值，保持数据库兼容性
                            'release_orders': edit_release_orders,
                            'release_failures': edit_release_failures,
                            'new_reuse_units': edit_new_reuse_units,
                            'new_reuse_events': edit_new_reuse_events
                        }
                        
                        try:
                            # 确保ID是Python原生int类型
                            record_id = int(selected_record['id'])
                            if db.update_report(record_id, update_data):
                                st.success(f"✅ 数据更新成功！记录ID: {record_id}")
                                st.rerun()
                            else:
                                st.error("❌ 更新失败！")
                        except Exception as e:
                            st.error(f"❌ 更新失败: {str(e)}")
        
        # 删除功能
        st.subheader("🗑️ 数据删除")
        st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
        
        if st.checkbox("启用删除功能"):
            record_to_delete = st.selectbox(
                "选择要删除的记录",
                options=[(row['id'], f"ID: {row['id']} - {row['monday_date']} 至 {row['sunday_date']}") 
                        for _, row in df.iterrows()],
                format_func=lambda x: x[1]
            )
            
            if st.button("🗑️ 确认删除", type="secondary"):
                # 确保ID是Python原生int类型
                delete_id = int(record_to_delete[0])
                if db.delete_report(delete_id):
                    st.success("✅ 删除成功！")
                    st.rerun()
                else:
                    st.error("❌ 删除失败！")

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"  
    "📊 周报表管理系统 | 基于 Streamlit 构建"  
    "</div>", 
    unsafe_allow_html=True
)