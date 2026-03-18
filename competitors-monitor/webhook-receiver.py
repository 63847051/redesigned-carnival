#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook 接收端
接收来自 daily_stock_analysis 的分析报告
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# 存储接收到的报告
REPORTS_FILE = "data/stock-webhook-reports.json"


def save_report(report_data: dict):
    """保存报告到文件"""
    try:
        # 读取现有报告
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                reports = json.load(f)
        else:
            reports = []
        
        # 添加新报告
        report_data["received_at"] = datetime.now().isoformat()
        reports.append(report_data)
        
        # 保存
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"保存报告失败: {e}")
        return False


@app.route('/webhook/stock', methods=['POST'])
def receive_stock_report():
    """接收股票分析报告"""
    try:
        data = request.json
        
        # 验证数据
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # 保存报告
        if save_report(data):
            return jsonify({
                "status": "success",
                "message": "Report received and saved",
                "received_at": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to save report"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/webhook/stock/reports', methods=['GET'])
def get_reports():
    """获取所有报告"""
    try:
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                reports = json.load(f)
            
            return jsonify({
                "status": "success",
                "count": len(reports),
                "reports": reports
            }), 200
        else:
            return jsonify({
                "status": "success",
                "count": 0,
                "reports": []
            }), 200
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "stock-webhook-receiver",
        "timestamp": datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    print("🚀 启动 Webhook 接收端...")
    print(f"📡 Webhook URL: http://0.0.0.0:5001/webhook/stock")
    print(f"📊 报告查询: http://0.0.0.0:5001/webhook/stock/reports")
    print(f"❤️ 健康检查: http://0.0.0.0:5001/health")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
