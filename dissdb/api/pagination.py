from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Page-number pagination for the public API: 25 per page, up to 100."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
