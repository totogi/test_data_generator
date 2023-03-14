from typing import Any
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode


class AsyncGqlClientService:
    def __init__(self, graphql_url: str, access_token: str) -> None:
        self.transport = AIOHTTPTransport(
            url=graphql_url,
            verify=True,
            retries=3,
            headers={"Authorization": access_token}
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
    
    
    async def execute(self, graphql_doc: DocumentNode, variable_values: dict) -> Any:
        return (await self.client.execute(graphql_doc, variable_values=variable_values))  