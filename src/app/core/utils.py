from __future__ import annotations
from math import ceil
from urllib.parse import parse_qs
from starlette.requests import Request
from pydantic import BaseModel


class PaginationInfo(BaseModel):
    total_elements: int
    page: int
    size: int
    pages: int


class Links(BaseModel):
    current_url: str
    first: str
    last: str
    next: str | None
    prev: str | None


def get_pagination_info(total_elements, page, size) -> PaginationInfo:
    info = PaginationInfo(
        total_elements=total_elements,
        page=page,
        size=size,
        pages=ceil(total_elements / size)
    )
    return info


def create_links(request: Request, pagination_info: PaginationInfo) -> Links:
    """
    Creates pagination links based on the provided request and pagination information.

    Parameters:
        request (Request): HTTP request object containing URL information.
        pagination_info (PaginationInfo): Information about pagination, such as total elements, current page, and page size.

    Returns:
        Links: An object containing pagination links, including current, first, last, next, and previous links.
    """
   
    pi = pagination_info

    links = Links(
        current_url=f"{request.url}",
        first=f"{result_url(request, 1, pi.size)}",
        last=f"{result_url(request, pi.pages, pi.size)}",
        next=f"{result_url(request, pi.page + 1, pi.size)}" if pi.page * pi.size < pi.total_elements else None,
        prev=f"{result_url(request, pi.page - 1, pi.size)}" if pi.page - 1 >= 1 else None
    )
    return links


def result_url(request: Request, page: int, size: int) -> str:
    """
    Constructs a new URL based on the provided request URL with updated query parameters for pagination.

    Parameters:
        request (Request): HTTP request object containing the URL information.
        page (int): page number for pagination.
        size (int): page size for pagination.

    Returns:
        str: The constructed URL with updated query parameters for pagination.
    """
    parsed_query = parse_qs(request.url.query)

    parsed_query.update({'page': [str(page)], 'size': [str(size)]})
    new_query = '&'.join(f'{key}={val[0]}' for key, val in parsed_query.items())
    
    #constructs the base URL combining the scheme, netloc(includes hostname and port num),and path components from the request.url
    new_url = f'{request.url.scheme}://{request.url.netloc}{request.url.path}'
  
    new_url += f'?{new_query}'

    return new_url