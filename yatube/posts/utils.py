from django.core.paginator import Paginator

DEFAULT_POST_PER_PAGE: int = 10


def paginate_page(request, post_list, post_per_page=DEFAULT_POST_PER_PAGE):
    paginator = Paginator(post_list, post_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
