"""
直接执行优先级1的API同步，无需确认
"""
import asyncio
from sync_priority1_apis import sync_apis

async def main():
    print("🚀 开始同步优先级1（核心业务）API...")
    await sync_apis(dry_run=False)
    print("\n✅ 同步完成！")

if __name__ == '__main__':
    asyncio.run(main())
