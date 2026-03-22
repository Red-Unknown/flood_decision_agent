infra/ 存放基础设施能力（日志、运行门控等）。

接口约定：
- require_kimi_api_key()：启动门控，缺失时输出“需要kimi_api_key”并退出
- setup_logging()：loguru 日志初始化，控制台+按日期落盘

