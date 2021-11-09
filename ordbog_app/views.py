from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SearchWordForm, NewUserForm
from django.contrib import messages

from deep_translator import GoogleTranslator, PonsTranslator
from serpapi import GoogleSearch

User = get_user_model()


def image_search(word):
    try:
        search = GoogleSearch(
            {"q": word, "api_key": "f95b3392006ab58721e533504f6356cf5834fabbf391f367d5f00e69669a3e72"})
        result = search.get_dict()
        return result.get('knowledge_graph')['header_images'][0]['image']
    except:
        return 0
    # try:
    #     params = {
    #         "engine": "google",
    #         "q": word,
    #         "tbm": "isch",
    #         "api_key": "f95b3392006ab58721e533504f6356cf5834fabbf391f367d5f00e69669a3e72"
    #     }
    #
    #     client = GoogleSearch(params)
    #     data = client.get_dict()
    #
    #     for result in data['images_results'][:5]:
    #         return f"""{result['original']}"""
    # except:
    #     return 0


class HomeView(View):
    def get(self, request, *args, **kwargs):
        my_form = SearchWordForm()
        context = {'form': my_form}
        return render(request, 'ordbog_app/home.html', context)

    def post(self, request, *args, **kwargs):
        form = SearchWordForm(request.POST)
        context = {'form': form}

        if form.is_valid():  # -> True/False
            word_value = form.cleaned_data['word']

            translated_word = GoogleTranslator(source='pl', target='da').translate(word_value)
            synonym_words = PonsTranslator(source='polish', target='english').translate(word_value, return_all=True)
            image_url = image_search(GoogleTranslator(source='pl', target='en').translate(word_value))

            context = {'translated_word': translated_word,
                       'synonyms': synonym_words,
                       'image_url': image_url}

        return render(request, 'ordbog_app/home.html', context)


def register_user(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Rejestracja zakończona sukcesem.")
            return redirect("/")
        messages.error(request, "Wystąpił błąd. Rejestracja nie udała się.")
    form = NewUserForm()
    return render(request, "ordbog_app/register.html", context={"register_form": form})


#
# class RegisterView(View):
#     def get(self, request, *args, **kwargs):
#         my_form = NewUserForm()
#         context = {'form': my_form}
#         return render(request, 'ordbog_app/home.html', context)
#
#     def post(self, request, *args, **kwargs):
#         form = NewUserForm(request.POST)
#         context = {'form': form}
#
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return render(request, 'ordbog_app/home.html', context)
#         messages.error(request, "Wystąpił błąd. Rejestracja nie udała się.")
#         # return render(request, 'ordbog_app/register.html', context)

def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Zalogowany jako {username}.")
                return redirect("/")
            else:
                messages.error(request, "Niewłaściwa nazwa użytkownika lub hasło.")
        else:
            messages.error(request, "Niewłaściwa nazwa użytkownika lub hasło.")
    form = AuthenticationForm()
    return render(request, "ordbog_app/login.html", context={"login_form": form})


def logout_user(request):
    logout(request)
    messages.info(request, "Pomyślnie wylogowano użytkownika.")
    return redirect("/")
