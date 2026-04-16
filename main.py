import sys
import asyncio
from loguru import logger
from src.utils import ensure_dirs
from src.discovery import run_discovery
from src.tester import run_tester
from src.merger import merge_data, save_merged_data
from src.exporter import run_exporter

def main():
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        encoding="utf-8"
    )
    
    logger.info("🚀 Mira Play 全自动采集系统启动")
    logger.info("📌 输出格式: index.js.md5 (Mira Play 可直接订阅)")
    logger.info("🔗 支持链接: http://user:pass@host/index.js.md5")
    logger.info("🔤 中文保证: 100% 保留原始中文名 (UTF-8)")
    
    ensure_dirs()
    
    # 1. 全网自动发现
    raw_apis = run_discovery()
    if not raw_apis:
        logger.warning("⚠️ 本轮未发现接口，流程终止")
        return
    
    # 2. 异步测试 + 中文提取
    valid_apis = asyncio.run(run_tester(raw_apis))
    
    # 3. 滚雪球合并
    final_apis = merge_data(valid_apis)
    
    # 4. 存档原始数据（可选）
    save_merged_data(final_apis)
    
    # 5. ✅ 生成 Mira Play 订阅文件 (index.js.md5)
    run_exporter(final_apis)
    
    logger.success("🎉 本轮完成 | index.js.md5 已生成并准备提交")

if __name__ == "__main__":
    main()
