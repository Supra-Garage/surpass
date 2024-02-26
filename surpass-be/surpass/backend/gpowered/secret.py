import os

from google.cloud import secretmanager

import logging

# 配置根日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用 logger 打印信息
logger.info(f"__name__ is {__name__}")


# 使用 logger 打印信息
logger.info("配置环境变量")


class GCloudSecrety:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GCloudSecrety, cls).__new__(cls)
            # 放置初始化代码在这里
            # cls.initialize_env_vars()
        return cls._instance

    def __init__(self) -> None:
        self.secrets = {}

    def access_secret_version(self, secret_key):
        """Return the value of a secret's version"""

        if self.secrets[secret_key]:
            logger.info(f"access_secret_version get {secret_key} = {self.secrets[secret_key]}")
            return self.secrets[secret_key]

        # Create the Secret Manager client.
        client = secretmanager.SecretManagerServiceClient()

        project_id = self.getProjectId()
        # 替换为你的 Google Cloud 项目ID
        # secret_id = "WEAVIATE_API_KEY"  # 秘密名称
        secret_id = secret_key  # 秘密名称
        version_id = "latest"  # 可以指定为 "latest" 或具体的版本号

        secret_key = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        # Access the secret version.
        response = client.access_secret_version(name=secret_key)

        # Return the decoded payload.
        secret_value = response.payload.data.decode("UTF-8")
        self.secrets[secret_key] = secret_value
        return secret_value

    def secretToEnv(self):
        if self.secrets:
            logger.info("has secretToEnv already")
            return

        logger.info("start run secretToEnv")

        # Create the Secret Manager client.
        client = secretmanager.SecretManagerServiceClient()
        project_id = self.getProjectId()
        # 构建项目名称
        parent = f"projects/{project_id}"
        # 列出所有密钥
        for secret in client.list_secrets(request={"parent": parent}):
            secret_name = secret.name
            secret_id = secret_name.split("/")[-1]

            # 获取每个秘密的最新版本的值
            version_name = f"{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": version_name})
            secret_value = response.payload.data.decode("UTF-8")

            # 将秘密设置为环境变量
            os.environ[secret_id] = secret_value
            self.secrets[secret_id] = secret_value
            logger.info(
                f"Set secret {secret_id}[{secret_value}] as environment variable."
            )

    def getProjectId(self):
        return os.environ["PROJECT_ID"]
