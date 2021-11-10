from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import SearchWordForm, NewUserForm
from .models import Notes, SearchHistory, Favourites

from deep_translator import GoogleTranslator, PonsTranslator
from serpapi import GoogleSearch
from datetime import datetime

User = get_user_model()


def image_search(word):
    """
    :param word:
    :return: returns a link to an image based on user's input
    """
    try:
        search = GoogleSearch(
            {"q": word, "api_key": "f95b3392006ab58721e533504f6356cf5834fabbf391f367d5f00e69669a3e72"})
        result = search.get_dict()
        return result.get('knowledge_graph')['header_images'][0]['image']
    except:
        return 0


class HomeView(View):
    """
    homepage/search form to lookup words and get them translated
    """
    def get(self, request, *args, **kwargs):
        my_form = SearchWordForm()
        context = {'form': my_form}
        return render(request, 'ordbog_app/home.html', context)

    def post(self, request, *args, **kwargs):
        form = SearchWordForm(request.POST)
        current_user = request.user
        context = {'form': form}

        if form.is_valid():
            """
            translates user's word to english and danish
            """
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
    """
    uses Django's built-in user registration form to register new users
    """
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
    """
    uses Django's built-in user form to log in users
    """
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
    """
    uses Django's built-in user form to log out users
    """
    logout(request)
    messages.info(request, "Pomyślnie wylogowano użytkownika.")
    return redirect("/")


# @login_required
# def search_history(request):
#     history = SearchHistory.objects.filter(user_id=request.user.id)
#     context = {"history": history}
#     return render(request, "ordbog_app/history.html", context)


@login_required
def search_history(request):
    """
    fetches search history for a logged in user
    """
    if request.method == "GET":
        history = SearchHistory.objects.filter(user_id=request.user.id)
        context = {"history": history}
        return render(request, "ordbog_app/history.html", context)

    if request.method == "POST":
        """
        adds selected words from search history to favourites 
        """
        current_user = request.user
        word_id = request.POST.keys()

        text = [*word_id][1]
        date_now = datetime.now()
        word_en = text.split('|')[0]
        word_pl = text.split('|')[1]
        word_dk = text.split('|')[2]

        Favourites.objects.create(date_added=date_now, word_en=word_en, word_pl=word_pl,
                                  word_dk=word_dk, user_id=current_user.id)

        messages.success(request, "Dodano do ulubionych")
        return redirect("/search_history")


@login_required
def favourites(request):
    if request.method == "GET":
        favourite_words = Favourites.objects.filter(user_id=request.user.id)
        context = {"favourite_words": favourite_words}
        return render(request, "ordbog_app/favourites.html", context)

    if request.method == "POST":
        """
        deletes selected words from favourites 
        """
        word = request.POST.keys()
        word_id = [*word][1]

        Favourites.objects.filter(id=word_id).delete()

        messages.info(request, "Usunięto z ulubionych")
        return redirect("/favourites")


@login_required
def user_profile(request):
    current_user = request.user
    if request.method == "GET":
        user_info = User.objects.filter(id=current_user.id)
        notes = Notes.objects.filter(user_id=request.user.id)
        context = {"user_info": user_info,
                   "notes": notes}
        return render(request, "ordbog_app/user_profile.html", context)

    if request.method == "POST":
        """
        adds new notes on the user_profile page
        """
        notes = request.POST.keys()
        note_test = request.POST.get('note')

        Notes.objects.update_or_create(note=note_test, user_id=current_user.id)

        messages.success(request, "Dodano notatkę")
        return redirect("/user_profile")
