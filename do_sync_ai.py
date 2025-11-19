"""
直接执行AI监测API的同步，无需确认
"""
import asyncio
from sync_ai_apis import sync_apis

async def main():
    print("🚀 开始同步AI监测相关API...")
    await sync_apis(dry_run=False)
    print("\n✅ 同步完成！")

if __name__ == '__main__':
    asyncio.run(main())
