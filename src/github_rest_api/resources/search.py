"""Search resource handlers."""

from __future__ import annotations

from typing import Any, Iterator, AsyncIterator

from github_rest_api.resources.base import Resource, AsyncResource


class SearchResource(Resource):
    """Synchronous search operations."""

    def issues(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> Iterator[dict[str, Any]]:
        """Search issues and pull requests.

        Args:
            query: Search query (e.g., "bug label:critical repo:owner/repo").
            sort: Sort field (comments, reactions, created, updated).
            order: Sort order (asc, desc).

        Yields:
            Issue/PR data dictionaries.

        Example queries:
            - "bug label:critical" - issues with "bug" and label "critical"
            - "is:issue is:open repo:owner/repo" - open issues in a repo
            - "is:pr is:merged author:username" - merged PRs by user
        """
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        for item in self._paginate("GET", "/search/issues", params=params):
            yield item

    def repositories(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> Iterator[dict[str, Any]]:
        """Search repositories.

        Args:
            query: Search query (e.g., "machine learning stars:>1000").
            sort: Sort field (stars, forks, help-wanted-issues, updated).
            order: Sort order (asc, desc).

        Yields:
            Repository data dictionaries.

        Example queries:
            - "machine learning language:python" - ML repos in Python
            - "stars:>1000 forks:>100" - popular repos
            - "topic:cli" - repos with cli topic
        """
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        for item in self._paginate("GET", "/search/repositories", params=params):
            yield item

    def code(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> Iterator[dict[str, Any]]:
        """Search code.

        Args:
            query: Search query (e.g., "addClass repo:jquery/jquery").
            sort: Sort field (indexed).
            order: Sort order (asc, desc).

        Yields:
            Code search result dictionaries.

        Example queries:
            - "addClass in:file language:js" - code with addClass in JS files
            - "function repo:owner/repo" - functions in specific repo
        """
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        for item in self._paginate("GET", "/search/code", params=params):
            yield item

    def users(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> Iterator[dict[str, Any]]:
        """Search users.

        Args:
            query: Search query (e.g., "fullname:John location:SF").
            sort: Sort field (followers, repositories, joined).
            order: Sort order (asc, desc).

        Yields:
            User data dictionaries.

        Example queries:
            - "type:user location:tokyo" - users in Tokyo
            - "type:org followers:>1000" - orgs with many followers
        """
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        for item in self._paginate("GET", "/search/users", params=params):
            yield item

    def commits(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> Iterator[dict[str, Any]]:
        """Search commits.

        Args:
            query: Search query.
            sort: Sort field (author-date, committer-date).
            order: Sort order (asc, desc).

        Yields:
            Commit data dictionaries.

        Example queries:
            - "fix bug repo:owner/repo" - commits with "fix bug"
            - "author:username" - commits by user
        """
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        for item in self._paginate("GET", "/search/commits", params=params):
            yield item

    def _paginate(
        self, method: str, path: str, params: dict[str, Any]
    ) -> Iterator[dict[str, Any]]:
        """Paginate through search results.

        Search API returns results in a different format than other endpoints.
        """
        params["per_page"] = 100
        page = 1

        while True:
            params["page"] = page
            response = self._client._client.request(method, path, params=params)
            if response.status_code >= 400:
                from github_rest_api.client import _handle_error_response
                _handle_error_response(response)

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            yield from items

            # Check if we've gotten all results
            if len(items) < 100 or page * 100 >= data.get("total_count", 0):
                break
            page += 1


class AsyncSearchResource(AsyncResource):
    """Asynchronous search operations."""

    async def issues(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> AsyncIterator[dict[str, Any]]:
        """Search issues and pull requests."""
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        async for item in self._paginate("GET", "/search/issues", params=params):
            yield item

    async def repositories(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> AsyncIterator[dict[str, Any]]:
        """Search repositories."""
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        async for item in self._paginate("GET", "/search/repositories", params=params):
            yield item

    async def code(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> AsyncIterator[dict[str, Any]]:
        """Search code."""
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        async for item in self._paginate("GET", "/search/code", params=params):
            yield item

    async def users(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> AsyncIterator[dict[str, Any]]:
        """Search users."""
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        async for item in self._paginate("GET", "/search/users", params=params):
            yield item

    async def commits(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
    ) -> AsyncIterator[dict[str, Any]]:
        """Search commits."""
        params: dict[str, Any] = {"q": query, "order": order}
        if sort:
            params["sort"] = sort
        async for item in self._paginate("GET", "/search/commits", params=params):
            yield item

    async def _paginate(
        self, method: str, path: str, params: dict[str, Any]
    ) -> AsyncIterator[dict[str, Any]]:
        """Paginate through search results asynchronously."""
        params["per_page"] = 100
        page = 1

        while True:
            params["page"] = page
            response = await self._client._client.request(method, path, params=params)
            if response.status_code >= 400:
                from github_rest_api.client import _handle_error_response
                _handle_error_response(response)

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                yield item

            # Check if we've gotten all results
            if len(items) < 100 or page * 100 >= data.get("total_count", 0):
                break
            page += 1
