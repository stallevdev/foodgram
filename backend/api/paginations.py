"""Кастомная пагинация для API."""

from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAGES_LIMIT_DEFAULT


class Pagination(PageNumberPagination):
    """Пагинация с параметром 'limit'."""

    page_size_query_param = 'limit'
    page_size = PAGES_LIMIT_DEFAULT
