import logging

# 配置根日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用 logger 打印信息
logger.info(f"__name__ is {__name__}")
