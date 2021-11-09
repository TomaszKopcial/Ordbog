from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import SearchWordForm, NewUserForm
from .models import UserProfile, SearchHistory, Favourites

from deep_translator import GoogleTranslator, PonsTranslator
from serpapi import GoogleSearch
from datetime import datetime

User = get_user_model()


def image_search(word):
    try:
        search = GoogleSearch(
            {"q": word, "api_key": "f95b3392006ab58721e533504f6356cf5834fabbf391f367d5f00e69669a3e72"})
        result = search.get_dict()
        return result.get('knowledge_graph')['header_images'][0]['image']
    except:
        return 0


class HomeView(View):
    def get(self, request, *args, **kwargs):
        my_form = SearchWordForm()
        context = {'form': my_form}
        return render(request, 'ordbog_app/home.html', context)

    def post(self, request, *args, **kwargs):
        form = SearchWordForm(request.POST)
        current_user = request.user
        context = {'form': form}

        if form.is_valid():  # -> True/False
            word_value = form.cleaned_data['word']

            translated_word = GoogleTranslator(source='pl', target='da').translate(word_value)
            translated_word_en = GoogleTranslator(source='pl', target='en').translate(word_value)
            synonym_words = PonsTranslator(source='polish', target='english').translate(word_value, return_all=True)
            image_url = image_search(GoogleTranslator(source='pl', target='en').translate(word_value))

            context = {'translated_word': translated_word,
                       'synonyms': synonym_words,
                       'image_url': image_url}

            date_now = datetime.now()
            SearchHistory.objects.create(date_searched=date_now, word_en=translated_word_en, word_pl=word_value,
                                         word_dk=translated_word, user_id=current_user.id)

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


@login_required
def search_history(request):
    history = SearchHistory.objects.filter(user_id=request.user.id)
    context = {"history": history}
    return render(request, "ordbog_app/history.html", context)


@login_required
def search_history(request):
    if request.method == "GET":
        history = SearchHistory.objects.filter(user_id=request.user.id)
        context = {"history": history}
        return render(request, "ordbog_app/history.html", context)

    if request.method == "POST":
        current_user = request.user
        word_id = request.POST.keys()
        print([*word_id][1])
        print(current_user)

        # date_now = datetime.now()
        # Favourites.objects.create(date_added=date_now, word_en=translated_word_en, word_pl=word_value,
        #                              word_dk=translated_word, user_id=current_user.id)

        messages.success(request, "Dodano do ulubionych")
        return redirect("/search_history")


@login_required
def favourites(request):
    favourite_words = Favourites.objects.filter(user_id=request.user.id)
    context = {"favourite_words": favourite_words}
    return render(request, "ordbog_app/favourites.html", context)