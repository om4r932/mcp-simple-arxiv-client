import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import os
import json
import httpx
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq

# Load environment variables
load_dotenv()


class MCPClient:
    """Main client class for interacting with MCP server and Groq API."""

    def __init__(self):
        """
        Initialize the MCP client with:
        - Session management
        - AsyncExitStack for resource cleanup
        - Groq API client
        """
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None
        self.groq = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
            http_client=httpx.Client(verify=False)
        )

    async def connect_to_server(self) -> None:
        """
        Establish connection to the MCP server using stdio transport.
        Initializes the session and lists available tools.
        """
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_simple_arxiv"]
        )

        # Create stdio transport and initialize session
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        print("Connected ! Available tools :", [tool.name for tool in response.tools])

    async def process_query(self, query: str) -> str:
        """
        Process a user query by:
        1. Getting available tools from MCP server
        2. Sending query to Groq API with tools information
        3. Handling tool calls if needed
        4. Returning final response
        
        Args:
            query: User input string
            
        Returns:
            Processed response string
        """
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]

        response = self.groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        tool_results = []
        final_text = []

        print("Choices :", len(response.choices))
        for choice in response.choices:
            if choice.message.tool_calls is None:
                print("Text found ! (Choice)")
                final_text.append(choice.message.content)
            else:
                print("Tool call ! (Choice)")
                for tool in choice.message.tool_calls:
                    t = tool.function
                    tool_name = t.name
                    tool_args = t.arguments

                    result = await self.session.call_tool(tool_name, json.loads(tool_args))
                    tool_results.append({"call": tool_name, "result": result})
                    print(f"Function call {tool_name}({tool_args})")
                
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                response = self.groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    max_tokens=1000,
                    messages=messages
                )

                final_text.append(response.choices[0].message.content)
        return "\n".join(final_text)

    async def chat_loop(self) -> None:
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\n>>> ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources by closing the AsyncExitStack."""
        await self.exit_stack.aclose()


async def main():
    """Main async function to run the MCP client."""
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())