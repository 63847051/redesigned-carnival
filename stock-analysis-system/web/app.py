# -*- coding: utf-8 -*-
"""
股票分析系统 - Streamlit Web 应用
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import DataFetcher, DataProcessor
from src.analysis.technical import TechnicalAnalysis

# 页面配置
st.set_page_config(
    page_title="📊 股票分析系统",
    page_icon="📈",
    layout="wide"
)

# 标题
st.title("📊 股票分析系统")
st.markdown("---")

# 侧边栏
st.sidebar.header("🔧 股票查询")

# 股票代码输入
symbol = st.sidebar.text_input(
    "股票代码",
    value="600318.SS",
    help="输入股票代码，如 600318.SS（中国平安）"
)

# 时间周期选择
period = st.sidebar.selectbox(
    "时间周期",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3,
    help="选择数据时间范围"
)

# 查询按钮
if st.sidebar.button("🔍 查询"):
    st.info(f"正在查询 {symbol} 的数据...")
    
    try:
        # 初始化
        fetcher = DataFetcher()
        processor = DataProcessor()
        ta = TechnicalAnalysis()
        
        # 获取数据
        with st.spinner("正在获取数据..."):
            df = fetcher.get_historical_data(symbol, period)
        
        if df.empty:
            st.error("❌ 未找到数据，请检查股票代码")
        else:
            # 清洗数据
            df = processor.clean_data(df)
            
            # 计算技术指标
            df = ta.calculate_all_indicators(df)
            
            # 显示基本信息
            st.subheader("📌 基本信息")
            info = fetcher.get_stock_info(symbol)
            if "error" not in info:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("股票名称", info.get("name", "N/A"))
                with col2:
                    st.metric("行业", info.get("industry", "N/A"))
                with col3:
                    st.metric("市值", f"{info.get('market_cap', 0):,.0f}")
                with col4:
                    st.metric("市盈率", f"{info.get('pe_ratio', 0):.2f}")
            
            st.markdown("---")
            
            # K线图
            st.subheader("📈 K线图")
            
            # 创建K线图
            fig = make_subplots(
                rows=3, 
                cols=1, 
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.5, 0.2, 0.3],
                subplot_titles=('K线图', '成交量', 'MACD')
            )
            
            # K线图
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='K线'
                ),
                row=1, col=1
            )
            
            # 移动平均线
            for ma in ['MA5', 'MA20', 'MA50']:
                if ma in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[ma],
                            name=ma,
                            line=dict(width=1)
                        ),
                        row=1, col=1
                    )
            
            # 成交量
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name='成交量',
                    marker_color='lightblue'
                ),
                row=2, col=1
            )
            
            # MACD
            if 'MACD' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['MACD'],
                        name='MACD',
                        line=dict(color='blue', width=1)
                    ),
                    row=3, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['MACD_Signal'],
                        name='Signal',
                        line=dict(color='orange', width=1)
                    ),
                    row=3, col=1
                )
            
            # 更新布局
            fig.update_layout(
                height=800,
                xaxis_rangeslider_visible=False,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # 技术指标
            st.subheader("📊 技术指标")
            
            latest = df.iloc[-1]
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("当前价格", f"¥{latest['Close']:.2f}")
            with col2:
                if 'RSI' in df.columns:
                    rsi = latest['RSI']
                    st.metric("RSI", f"{rsi:.2f}")
            with col3:
                if 'MACD' in df.columns:
                    macd = latest['MACD']
                    st.metric("MACD", f"{macd:.2f}")
            with col4:
                st.metric("成交量", f"{latest['Volume']:,.0f}")
            
            st.markdown("---")
            
            # 趋势分析
            st.subheader("🎯 趋势分析")
            
            trend_analysis = ta.identify_trend(df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"📈 趋势: {trend_analysis['trend']}")
            with col2:
                st.info(f"💰 价格: ¥{trend_analysis['current_price']:.2f}")
            
            # 数据表格
            st.markdown("---")
            st.subheader("📋 历史数据")
            st.dataframe(df.tail(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ 错误: {str(e)}")
        st.exception(e)

# 页脚
st.markdown("---")
st.markdown("💡 **提示**: 本系统仅供学习和研究使用，不构成投资建议。")
st.markdown("🤖 **设计**: 大领导 🎯 | **实现**: OpenCode AI")
