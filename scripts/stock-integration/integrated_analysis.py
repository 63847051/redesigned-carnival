#!/usr/bin/env python3
"""
股票分析集成脚本
自动配合 A 股 MCP 服务和 daily_stock_analysis
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from pathlib import Path

# 配置
MCP_URL = "http://82.156.17.205/cnstock/mcp"
DAILY_STOCK_API = "http://127.0.0.1:8000"  # daily_stock_analysis API


class StockIntegration:
    """股票分析集成器"""

    def __init__(self):
        self.mcp_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

    async def query_mcp(self, tool: str, symbol: str) -> dict:
        """
        查询 A 股 MCP 服务

        Args:
            tool: 工具名称 (brief/medium/full)
            symbol: 股票代码

        Returns:
            dict: 股票数据
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool,
                    "arguments": {"symbol": symbol}
                },
                "id": 1
            }

            try:
                response = await client.post(MCP_URL, json=payload, headers=self.mcp_headers)
                if response.status_code == 200:
                    # 解析 SSE 响应
                    lines = response.text.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = json.loads(line[6:])
                            if 'result' in data:
                                result = data['result']
                                if 'content' in result:
                                    for item in result['content']:
                                        if item.get('type') == 'text':
                                            return {"success": True, "data": item['text']}
                return {"success": False, "error": "解析失败"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def query_daily_stock(self, symbol: str) -> dict:
        """
        查询 daily_stock_analysis

        Args:
            symbol: 股票代码

        Returns:
            dict: 分析结果
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # 调用 daily_stock_analysis API
                # 注意：需要根据实际 API 调整
                url = f"{DAILY_STOCK_API}/api/analyze"
                response = await client.post(url, json={"symbol": symbol})
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
            except Exception as e:
                # 如果 API 不可用，返回提示
                return {
                    "success": False,
                    "error": str(e),
                    "note": "daily_stock_analysis API 不可用，请检查服务是否运行"
                }

    async def integrated_analysis(self, symbol: str) -> dict:
        """
        集成分析：结合 MCP 和 daily_stock_analysis

        Args:
            symbol: 股票代码

        Returns:
            dict: 综合分析结果
        """
        print(f"\n🔍 开始集成分析: {symbol}")
        print("=" * 60)

        # 1. 使用 MCP 获取实时数据
        print(f"\n📡 步骤 1: 查询实时数据...")
        mcp_result = await self.query_mcp("brief", symbol)
        
        if not mcp_result["success"]:
            return {
                "success": False,
                "error": f"MCP 查询失败: {mcp_result.get('error', '未知错误')}"
            }

        print(f"✅ 实时数据获取成功")
        real_data = mcp_result["data"]

        # 2. 使用 daily_stock_analysis 进行深度分析
        print(f"\n🤖 步骤 2: AI 深度分析...")
        daily_result = await self.query_daily_stock(symbol)
        
        if daily_result["success"]:
            print(f"✅ AI 分析完成")
            ai_analysis = daily_result["data"]
        else:
            print(f"⚠️  AI 分析不可用: {daily_result.get('error', '未知错误')}")
            print(f"   提示: {daily_result.get('note', '')}")
            ai_analysis = None

        # 3. 生成综合报告
        print(f"\n📊 步骤 3: 生成综合报告...")
        report = self.generate_report(symbol, real_data, ai_analysis)
        
        return {
            "success": True,
            "symbol": symbol,
            "real_data": real_data,
            "ai_analysis": ai_analysis,
            "report": report
        }

    def generate_report(self, symbol: str, real_data: str, ai_analysis: dict = None) -> str:
        """
        生成综合报告

        Args:
            symbol: 股票代码
            real_data: MCP 实时数据
            ai_analysis: daily_stock_analysis 分析结果

        Returns:
            str: 综合报告
        """
        report = f"""
# 📊 {symbol} 集成分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📡 实时数据（A 股 MCP 服务）

```
{real_data}
```

---

## 🤖 AI 深度分析（daily_stock_analysis）
"""

        if ai_analysis:
            report += f"\n```\n{json.dumps(ai_analysis, indent=2, ensure_ascii=False)}\n```\n"
        else:
            report += "\n⚠️  AI 分析暂时不可用，请检查 daily_stock_analysis 服务\n"

        report += "\n---\n\n**💡 建议**: 结合实时数据和 AI 分析，做出更明智的投资决策。\n"

        return report

    def save_report(self, symbol: str, report: str):
        """
        保存报告到文件

        Args:
            symbol: 股票代码
            report: 报告内容
        """
        output_dir = Path("/root/.openclaw/workspace/stock-reports")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = output_dir / f"{symbol}_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 报告已保存: {filename}")
        return filename


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 integrated_analysis.py <股票代码>")
        print("示例: python3 integrated_analysis.py SH600000")
        sys.exit(1)

    symbol = sys.argv[1]

    # 创建集成器
    integration = StockIntegration()

    # 执行集成分析
    result = await integration.integrated_analysis(symbol)

    if result["success"]:
        # 保存报告
        integration.save_report(symbol, result["report"])
        
        # 打印报告
        print("\n" + "=" * 60)
        print(result["report"])
    else:
        print(f"\n❌ 分析失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
