from django.conf import settings

from rest_framework import pagination


class Pagination(pagination.PageNumberPagination):
    page_size = settings.POSTS_ON_PAGE
    page_size_query_param = settings.PAGE_SIZE_QUERY_PARAM
    max_page_size = settings.MAX_PAGE_SIZE
