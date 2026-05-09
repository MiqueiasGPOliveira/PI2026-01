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

def login_page(request):
    """
    Renderiza a página de login do Front-end.
    """
    return render(request, 'login.html')

def perfil_page(request):
    """
    Renderiza a página de perfil do Front-end.
    """
    return render(request, 'perfil.html')

def roadmap_page(request):
    """
    Renderiza a página de gerador de roadmap educacional.
    """
    return render(request, 'roadmap.html')
