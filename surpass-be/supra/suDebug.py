import os

import logging

from supra.suLogging import logger

# 使用 logger 打印信息
logger.info(f"__name__ is {__name__}")

systemUser = os.environ.get("USER")
dbUrl = os.environ.get("RECORD_MANAGER_DB_URL")
debug = os.environ.get("SU_DEBUG") or "supra" == systemUser
# debug = os.environ.get("SU_DEBUG") or "supra" == systemUser or not dbUrl or "empty" == dbUrl

# 使用 logger 打印信息
logger.info(f"devMode[{debug}] \n systemUser is {systemUser} \n dbUrl is {dbUrl}")
