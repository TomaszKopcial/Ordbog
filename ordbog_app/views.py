from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model
from .forms import SearchWordForm

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
    #     for result in data['images_results'][:1]:
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
