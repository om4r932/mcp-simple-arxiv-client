# Simple MCP arXiv client

A simple Python client to interact with the arXiv MCP server.

## Description

This project is a MCP (Model Context Protocol) client that connects to the arXiv MCP server to perform searches on arXiv. It uses Groq as a language model to process user queries and call the appropriate server tools in a chat-based interface.

## Prerequisites

- Python 3.10.6 or higher
- A Groq API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/om4r932/mcp-simple-arxiv-server.git
cd mcp-simple-arxiv-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file at the project root with your Groq API key:
```
GROQ_API_KEY=your_groq_api_key
```

An `.env.example` file is provided as a template.

## Usage

Run the client:
```bash
python client.py
```

This will start an interactive chat interface where you can ask questions about scientific papers.

## Credits

Andy Brandt and his ArXiv server "mcp-simple-arxiv" : [Repository](https://github.com/andybrandt/mcp-simple-arxiv)