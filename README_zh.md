# 旅游规划智能体系统

一个基于智能体技术，旨在帮助用户高效、个性化地进行旅游规划的系统。

## 简介

本项目构建了一个智能体系统，通过结合检索增强生成（RAG）和多模态协作（MCP）等技术，创建一个能够理解复杂旅游需求、检索实时信息并利用外部工具（Tool Calling）的智能体，为用户提供从景点推荐到行程规划等一站式旅游咨询与服务。

系统旨在解决传统旅游规划中信息碎片化、实时性差、个性化不足等痛点，让用户获得更智能、更便捷的规划体验。

## 特性

-   **智能行程规划:** 根据用户的偏好、时间、预算等因素，生成个性化的旅游行程。
-   **实时信息检索 (RAG):** 利用检索模块获取最新的旅游信息，如景点开放时间、门票价格、交通状况等。
-   **工具调用 (MCP):** 智能体能够根据任务需求，调用外部工具或API，例如天气查询、地图导航、潜在的预订接口（如果已实现或计划）。
-   **对话式交互:** 通过自然语言与用户进行多轮对话，理解并细化需求。
-   **可扩展性:** 基于模块化设计，易于集成新的工具、数据源或智能体能力。

## 技术栈

本项目主要依赖以下技术栈：

-   **核心智能体框架:** 基于 [LangChain](https://www.langchain.com/) 构建整个智能体系统，提供Agent、Chain、Tool等核心组件的抽象和管理能力。
-   **检索增强生成 (RAG):** 使用 [lightrag](https://github.com/your-lightrag-repo-link) 作为轻量级RAG模块，负责从项目的数据源中检索与用户查询相关的旅游信息。
    -   **嵌入模型:** 利用 [Ollama](https://ollama.com/) 提供的 `nomic-embed-text` 模型生成文本嵌入向量，用于RAG模块的相似度搜索。
-   **智能体能力(MCP):** 使用MCP调用高德地图、谷歌搜索等外部工具来增强智能体的工具调用能力和决策逻辑，使其能更有效地利用RAG获取的信息或调用外部工具。
-   **大型语言模型 (LLM):** 系统通过LangChain与一个大型语言模型进行交互，作为智能体的核心推理引擎。
    -   本项目使用 Azure OpenAI API 接入 GPT 系列 LLM。

## 架构概览
![image](https://github.com/user-attachments/assets/bf9f9b1b-b2cc-4202-ae25-7ecb8bb5d99b)



## 安装与使用

### 前置条件
Python 3.11+
安装 Ollama 并拉取 nomic-embed-text 模型：

ollama pull nomic-embed-text
配置 Azure OpenAI API 密钥和端点。

安装
克隆本项目仓库：

git clone https://github.com/6thChoice/TravelPlan.git

安装依赖：

pip install -r requirements.txt

## 使用说明

启动 MCP 服务器：

python gaode_mcp_server.py

确保 Ollama 服务正在运行：

ollama serve

启动主程序（Agent 系统）：

python main_end.py

启动前端界面：

python app_end.py

程序启动后，通过访问前端界面与智能体进行交互。

## 示例输入：

### 首页
<img width="1280" alt="first_page" src="https://github.com/user-attachments/assets/40eb8458-4c60-4f23-8148-7ac0a3e501a4" />

### 使用

设置：上海，游玩四天

偏好：我想和家人一起舒适地旅行，我喜欢骑自行车。
![draft](https://github.com/user-attachments/assets/6c935b0f-fa93-417d-ba85-ff87e48c20ba)

根据草稿，系统继续生成详细方案：
![detail_plan_p1](https://github.com/user-attachments/assets/32b823c3-885f-449a-a3ea-91d738d0c7cf)
![detail_plan_p2](https://github.com/user-attachments/assets/cab67ff6-1491-4a1a-a5bc-084ba2f8a38b)
![detail_plan_p3](https://github.com/user-attachments/assets/7206c0e0-2e58-40ce-9406-a31cf7e43d63)

如有需要，系统支持详细调整旅行计划。

## 致谢
感谢以下开源项目和社区提供的强大支持：

LangChain

lightrag

Ollama

Azure OpenAI Service

高德开放平台

Search-Engines-Scraper
