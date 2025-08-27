from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
import secrets
import random
from .models import Quote, Vote
from .forms import QuoteForm

# Create your views here.

def index(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        quotes = Quote.objects.all()
        if not quotes.exists():
            return JsonResponse({'error': 'Нет цитат'}, status=400)

        weighted_quotes = []
        for q in quotes:
            weighted_quotes.extend([q] * q.weight)

        if not weighted_quotes:
            return JsonResponse({'error': 'Нет цитат для отображения'}, status=400)

        quote = random.choice(weighted_quotes)
        quote.views += 1
        quote.save(update_fields=['views'])

        return JsonResponse({
            'id': quote.id,
            'text': quote.text,
            'source': quote.source,
            'likes': quote.likes,
            'dislikes': quote.dislikes,
            'views': quote.views,
        })

    key = "random_quote"
    cached_data = cache.get(key)
    if cached_data:
        quote, views_count = cached_data
    else:
        quotes = Quote.objects.all()
        if not quotes.exists():
            return HttpResponse("Нет цитат")

        weighted_quotes = []
        for q in quotes:
            weighted_quotes.extend([q] * q.weight)

        if not weighted_quotes:
            return HttpResponse("Нет цитат для отображения")

        quote = random.choice(weighted_quotes)
        views_count = getattr(quote, 'views', 0) or 0
        cache.set(key, (quote, views_count), 10)

    quote.views = getattr(quote, 'views', 0) + 1
    quote.save(update_fields=['views'])

    context = {
        'quote': quote,
        'views_count': quote.views,
    }
    return render(request, 'show_quote/index.html', context)


def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text'].strip()
            source = form.cleaned_data['source'].strip()
            weight = form.cleaned_data['weight']

            # Проверка на дубликат
            if Quote.objects.filter(text__iexact=text).exists():
                messages.error(request, "Цитата уже существует!")
            else:
                # Проверка: не больше 3 цитат с одного источника
                if Quote.objects.filter(source=source).count() >= 3:
                    messages.error(request, f"Нельзя добавить больше 3 цитат из источника '{source}'.")
                else:
                    quote = form.save(commit=False)
                    quote.text = text
                    quote.source = source
                    quote.weight = weight
                    quote.save()
                    messages.success(request, "Цитата успешно добавлена!")
                    return redirect('index')  # после добавления — на главную
    else:
        form = QuoteForm()

    return render(request, 'show_quote/add.html', {'form': form})

def top_quotes(request):
    top_quotes = Quote.objects.order_by('-likes')[:10]
    context = {
        'top_quotes': top_quotes
    }
    return render(request, 'show_quote/top.html', context)

def get_or_create_visitor_id(request):
    """Получаем ID посетителя из куки или создаём новый"""
    if 'visitor_id' not in request.COOKIES:
        return secrets.token_hex(16)  # временный ID
    return request.COOKIES['visitor_id']

@require_http_methods(["POST"])
@csrf_protect
def like_quote(request, quote_id):
    visitor_id = get_or_create_visitor_id(request)
    quote = Quote.objects.get(id=quote_id)

    # Проверяем, голосовал ли уже этот посетитель
    existing_vote = Vote.objects.filter(quote=quote, session_id=visitor_id).first()

    if existing_vote:
        return JsonResponse({
            'error': 'Вы уже голосовали за эту цитату',
            'likes': quote.likes,
            'dislikes': quote.dislikes
        }, status=400)

    Vote.objects.create(
        quote=quote,
        session_id=visitor_id,
        vote_type='like'
    )
    quote.likes += 1
    quote.save(update_fields=['likes'])

    response = JsonResponse({'likes': quote.likes, 'dislikes': quote.dislikes})
    if 'visitor_id' not in request.COOKIES:
        response.set_cookie('visitor_id', visitor_id, max_age=365 * 24 * 60 * 60)
    return response


@require_http_methods(["POST"])
@csrf_protect
def dislike_quote(request, quote_id):
    visitor_id = get_or_create_visitor_id(request)
    quote = Quote.objects.get(id=quote_id)

    existing_vote = Vote.objects.filter(quote=quote, session_id=visitor_id).first()

    if existing_vote:
        return JsonResponse({
            'error': 'Вы уже голосовали за эту цитату',
            'likes': quote.likes,
            'dislikes': quote.dislikes
        }, status=400)

    Vote.objects.create(
        quote=quote,
        session_id=visitor_id,
        vote_type='dislike'
    )
    quote.dislikes += 1
    quote.save(update_fields=['dislikes'])

    response = JsonResponse({'dislikes': quote.dislikes, 'likes': quote.likes})
    if 'visitor_id' not in request.COOKIES:
        response.set_cookie('visitor_id', visitor_id, max_age=365 * 24 * 60 * 60)
    return response