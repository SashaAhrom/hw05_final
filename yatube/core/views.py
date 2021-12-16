from django.shortcuts import render


def page_not_found(request, exception):
    context = {
        'path': request.path,
        'title': 'Custom 404'
    }
    return render(request, 'core/404.html', context, status=404)


def server_error(request):
    context = {
        'title': 'Custom 500'
    }
    return render(request, 'core/500.html', context, status=500)


def permission_denied_view(request, exception):
    context = {
        'title': 'Custom 403'
    }
    return render(request, 'core/403.html', context, status=403)
