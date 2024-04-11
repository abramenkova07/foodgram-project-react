from rest_framework.pagination import PageNumberPagination

from .constants import MAX_PAGE_SIZE_VALUE, PAGE_SIZE_VALUE


class StandardResultsSetPagination(PageNumberPagination):
    page_size = PAGE_SIZE_VALUE
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE_VALUE
