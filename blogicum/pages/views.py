from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RulesPageView(TemplateView):
    template_name = 'pages/rules.html'


def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request,
                  'registration/registration_form.html', {'form': form})


def server_error_custom(request):
    return render(request, 'pages/500.html', status=500)


def page_not_found_custom(request, exception):
    return render(request, 'pages/404.html', status=404)
