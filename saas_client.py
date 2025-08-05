from fastmcp.client import Client, StreamableHttpTransport

from auth import get_tokens

HOST_URL = "http://localhost:8000"

tok = get_tokens()["access_token"]
transport = StreamableHttpTransport(HOST_URL, headers={"Authorization": f"Bearer {tok}"})
client = Client(transport)

if __name__ == "__main__":
    tickets = client.call_tool("list_tickets")
    print("First ticket:", tickets[0]["subject"]) 

    lead = client.call_tool("create_lead", arguments={"last_name": "Doe", "company": "ExampleCorp"})
    print("Created lead id", lead["id"])
