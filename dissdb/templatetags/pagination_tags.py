from django import template

register = template.Library()

@register.filter
def get_page_range(page, delta=3):
    current_page = page.number
    total_pages = page.paginator.num_pages
    
    start_page = max(1, current_page - delta)
    end_page = min(total_pages + 1, current_page + delta + 1)
    
    # Adjust to always show 2*delta + 1 pages when possible
    if end_page - start_page < 2 * delta + 1:
        if start_page == 1:
            end_page = min(total_pages + 1, start_page + 2 * delta + 1)
        elif end_page == total_pages + 1:
            start_page = max(1, end_page - 2 * delta - 1)
    
    return {
        'page_range': range(start_page, end_page),
        'show_first': start_page > 1,
        'show_first_ellipsis': start_page > 2,
        'show_last': end_page <= total_pages,
        'show_last_ellipsis': end_page <= total_pages - 1,
        'total_pages': total_pages
    }