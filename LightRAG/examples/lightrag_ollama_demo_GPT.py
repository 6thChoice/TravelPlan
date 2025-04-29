import asyncio
import nest_asyncio

nest_asyncio.apply()
import os
import inspect
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

from tqdm import tqdm

WORKING_DIR = r"/Volumes/extenal/lvyou_agent/trip_planing_agents/LightRAG/database"
os.environ['OPENAI_API_BASE'] = 'https://api.nuwaapi.com/v1'
os.environ['OPENAI_API_KEY'] = 'sk-8n0vEAf4Ybw1sjCXY1SKKb18byO6g5ytFOqwRUaddPTizExT'

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model="nomic-embed-text", host="http://localhost:11434"
            ),
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())

    # Test different query modes
    print("\nNaive Search:")
    print(
        rag.query(
            "详细规划河南游玩计划", param=QueryParam(mode="naive", only_need_context = False)
        )
    )

    print("\nLocal Search:")
    print(
        rag.query(
            "详细规划河南游玩计划", param=QueryParam(mode="local", only_need_context = False)
        )
    )

    print("\nGlobal Search:")
    print(
        rag.query(
            "详细规划河南游玩计划", param=QueryParam(mode="global", only_need_context = False)
        )
    )

    print("\nHybrid Search:")
    print(
        rag.query(
            "详细规划河南游玩计划", param=QueryParam(mode="hybrid", only_need_context = False)
        )
    )

    # stream response
    resp = rag.query(
        "详细规划河南游玩计划",
        param=QueryParam(mode="hybrid", stream=True),
    )


if __name__ == "__main__":
    main()
