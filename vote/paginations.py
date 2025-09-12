from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import Serializer, CharField, JSONField

class CustomPaginator():
    def paginate_queryset(queryset, request, page_size=2):
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        return paginator.paginate_queryset(queryset, request)
    
    def format_json_response(paginator, data):
        serializer = ResponseSerializer({
            "previous" : paginator.get_previous_link(),
            "next": paginator.get_next_link(),
            "data": data
        })
        return serializer.data
    
class ResponseSerializer(Serializer):
    previous = CharField()
    next = CharField()
    data = JSONField()