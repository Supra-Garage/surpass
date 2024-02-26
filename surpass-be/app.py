"""
A sample Hello World server.
"""
import os
import logging
from dotenv import load_dotenv

from surpass.backend.gpowered.secret import GCloudSecrety

import surpass.backend.gpowered.secret as secret


# 配置根日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用 logger 打印信息
logger.info(f"__name__ is {__name__}")


# 使用 logger 打印信息
logger.info("配置环境变量")

gCloudSecrety = GCloudSecrety()
gCloudSecrety.secretToEnv()

weaviateApiKey = gCloudSecrety.access_secret_version("WEAVIATE_API_KEY")
openaiApikey = gCloudSecrety.access_secret_version("openai-apikey")

logger.info(f"access_secret_version >> WEAVIATE_API_KEY = {weaviateApiKey}")
logger.info(f"access_secret_version >> openai-apikey = {openaiApikey}")

# 获取当前文件所在目录的路径
current_dir = os.path.dirname(__file__)

# logger.info(f"当前工作目录：{current_dir}")

# 指定 .env 文件的路径
dotenv_path = os.path.join(current_dir, 'chat-langchain', '.env')
# logger.info(f"dotenv加载：{dotenv_path}")

load_dotenv(dotenv_path=dotenv_path)
# logger.info(f"dotenv加载完毕：")
# # 打印所有环境变量
# for key, value in os.environ.items():
#     print(f"env >>> {key}: {value}")

import asyncio
from typing import Optional, Union
from uuid import UUID
import langsmith
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from langsmith import Client
from pydantic import BaseModel
from surpass.backend.chain import ChatRequest, answer_chain

client = Client()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


add_routes(
    app,
    answer_chain,
    path="/chat",
    input_type=ChatRequest,
    config_keys=["metadata", "configurable", "tags"],
)


class SendFeedbackBody(BaseModel):
    run_id: UUID
    key: str = "user_score"

    score: Union[float, int, bool, None] = None
    feedback_id: Optional[UUID] = None
    comment: Optional[str] = None


@app.post("/feedback")
async def send_feedback(body: SendFeedbackBody):
    client.create_feedback(
        body.run_id,
        body.key,
        score=body.score,
        comment=body.comment,
        feedback_id=body.feedback_id,
    )
    return {"result": "posted feedback successfully", "code": 200}


class UpdateFeedbackBody(BaseModel):
    feedback_id: UUID
    score: Union[float, int, bool, None] = None
    comment: Optional[str] = None


@app.patch("/feedback")
async def update_feedback(body: UpdateFeedbackBody):
    feedback_id = body.feedback_id
    if feedback_id is None:
        return {
            "result": "No feedback ID provided",
            "code": 400,
        }
    client.update_feedback(
        feedback_id,
        score=body.score,
        comment=body.comment,
    )
    return {"result": "patched feedback successfully", "code": 200}


# TODO: Update when async API is available
async def _arun(func, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args, **kwargs)


async def aget_trace_url(run_id: str) -> str:
    for i in range(5):
        try:
            await _arun(client.read_run, run_id)
            break
        except langsmith.utils.LangSmithError:
            await asyncio.sleep(1**i)

    if await _arun(client.run_is_shared, run_id):
        return await _arun(client.read_run_shared_link, run_id)
    return await _arun(client.share_run, run_id)


class GetTraceBody(BaseModel):
    run_id: UUID


@app.post("/get_trace")
async def get_trace(body: GetTraceBody):
    run_id = body.run_id
    if run_id is None:
        return {
            "result": "No LangSmith run ID provided",
            "code": 400,
        }
    return await aget_trace_url(str(run_id))


# from flask import Flask, render_template

# # pylint: disable=C0103
# app = Flask(__name__)


# @app.route('/')
# def hello():
#     """Return a friendly HTTP greeting."""
#     message = "It's running!"

#     """Get Cloud Run environment variables."""
#     service = os.environ.get('K_SERVICE', 'Unknown service')
#     revision = os.environ.get('K_REVISION', 'Unknown revision')

#     return render_template('index.html',
#         c=message,
#         Service=service,
#         Revision=revision)


logger.info(f'is __main__ >>> {__name__ == "__main__"}')
if __name__ == "__main__":
    logger.info(">>> log by __main_")
    server_port = os.environ.get('PORT', '8080')
    # app.run(debug=False, port=server_port, host='0.0.0.0')
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

