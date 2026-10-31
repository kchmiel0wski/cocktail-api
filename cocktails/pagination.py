from rest_framework.pagination import PageNumberPagination

from .serializers import PaginationQuerySerializer


class ValidatedPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        serializer = PaginationQuerySerializer(data=request.query_params.dict())
        serializer.is_valid(raise_exception=True)
        return super().paginate_queryset(queryset, request, view)
