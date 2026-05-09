from django.shortcuts import render

def landing_page(request):
    """
    Renderiza a Landing Page principal.
    """
    return render(request, 'landing_page.html')

def cadastro_page(request):
    """
    Renderiza a página de cadastro do Front-end.
    """
    return render(request, 'cadastro.html')
