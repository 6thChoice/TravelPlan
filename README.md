# Travel Planning Agent System

An agent-based system designed to help users plan their trips efficiently and personally.

## Introduction

This project builds an agent system that combines technologies like Retrieval Augmented Generation (RAG) and Multi-modal Collaboration/Capability (MCP) to create an intelligent agent capable of understanding complex travel needs, retrieving real-time information, and utilizing external tools (Tool Calling). It aims to provide users with a one-stop travel consultation and service, from recommending attractions to planning itineraries.

The system aims to address the pain points in traditional travel planning, such as fragmented information, poor real-time data, and lack of personalization, providing users with a smarter and more convenient planning experience.

## Features

-   **Smart Itinerary Planning:** Generates personalized travel itineraries based on user preferences, time, budget, and other factors.
-   **Real-time Information Retrieval (RAG):** Uses a retrieval module to fetch the latest travel information, such as attraction opening hours, ticket prices, traffic conditions, etc.
-   **Tool Calling (MCP):** The agent can call external tools or APIs as required by the task, such as weather queries, map navigation, and potential booking interfaces (if implemented or planned).
-   **Conversational Interaction:** Engages in multi-turn conversations with users using natural language to understand and refine requirements.
-   **Extensibility:** Based on modular design, making it easy to integrate new tools, data sources, or agent capabilities.

## Technology Stack

This project mainly relies on the following technology stack:

-   **Core Agent Framework:** Built upon [LangChain](https://www.langchain.com/) to construct the entire agent system, providing abstractions and management capabilities for core components like Agents, Chains, and Tools.
-   **Retrieval Augmented Generation (RAG):** Uses [lightrag](https://github.com/your-lightrag-repo-link) as a lightweight RAG module responsible for retrieving travel information relevant to user queries from the project's data sources.
    -   **Embedding Model:** Utilizes the `nomic-embed-text` model provided by [Ollama](https://ollama.com/) to generate text embedding vectors for similarity search within the RAG module.
-   **Agent Capability (MCP):** Uses MCP to call external tools like Amap (Gaode Maps), Google Search, etc., to enhance the agent's tool-calling capabilities and decision-making logic, enabling it to effectively utilize information obtained from RAG or call external tools.
-   **Large Language Model (LLM):** The system interacts with a Large Language Model via LangChain, serving as the agent's core reasoning engine.
    -   This project uses the Azure OpenAI API to integrate GPT series LLMs.
 
## System Architecture
![image](https://github.com/user-attachments/assets/4038a9e5-afca-48f4-b7df-4a766d2721f3)


## Installation and Usage

### Prerequisites

Python 3.11+

Install Ollama and pull the nomic-embed-text model:

ollama pull nomic-embed-text

Configure Azure OpenAI API key and endpoint.

### Installation

Clone this repository:

git clone https://github.com/6thChoice/TravelPlan.git

### Install dependencies:

pip install -r requirements.txt

### Usage Instructions

Start the MCP server:

python gaode_mcp_server.py

Ensure Ollama service is running:

ollama serve

Start the main program (Agent System):

python main_end.py

Start the frontend interface:

python app_end.py

After the program starts, interact with the agent by accessing the frontend interface.

## Example Input:

### First Page
<img width="1280" alt="first_page" src="https://github.com/user-attachments/assets/77dea419-128a-403b-bd4a-7f82e83bb45b" />

### Usage

Configure: Shanghai, 4-day-trip

Prompt：I want to have a comfortable travel with my family, and I like cycling.

Draft:
![draft](https://github.com/user-attachments/assets/1d2b65c8-141f-4d18-a5bf-0df8ea270ef0)

According draft, the system make final detailed plan:
![detail_plan_p1](https://github.com/user-attachments/assets/045c6516-d52b-45de-84a4-a053f87bee3b)
![detail_plan_p2](https://github.com/user-attachments/assets/9bf401aa-19e0-4c7a-83b3-a901db5518eb)
![detail_plan_p3](https://github.com/user-attachments/assets/141619f6-a23e-472b-aeaf-cdace363a9d3)

If need, the system supports to detailed adjust the travel plan.

## Acknowledgements

Thanks to the following open-source projects and communities for their strong support:

LangChain

lightrag

Ollama

Azure OpenAI Service

Amap (Gaode Maps) Open Platform

Search-Engines-Scraper
