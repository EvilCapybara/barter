from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from users.forms import RegisterForm
from ads.forms import AdForm
from ads.models import Ad
from exchanges.forms import ExchangeProposalForm
from exchanges.models import ExchangeProposal


def home(request):
    return render(request, 'home.html')


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Получаем пользователя из формы
            user = form.get_user()
            login(request=request, user=user)  # Логиним пользователя
            return redirect('home')  # Перенаправляем после успешного входа
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # или куда хочешь после регистрации
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


# same as login_required(create_ad)
@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.owner = request.user
            ad.save()
            messages.success(request, f'Объявление "{form.instance.title}" успешно создано!')
            return redirect('home')  # или куда хочешь после регистрации return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm
    return render(request, 'create_ad.html', {'form': form})


def ad_detail(request, pk: int):
    ad = get_object_or_404(Ad, pk=pk)
    return render(request, 'ad_detail.html', {'ad': ad})


@login_required
def delete_ad(request, pk: int):
    ad = get_object_or_404(Ad, pk=pk)  # только если объявление твоё

    if ad.owner != request.user:
        return HttpResponseForbidden("У вас нет прав на удаление этого объявления!")

    if request.method == 'POST':
        messages.success(request, f'Объявление "{ad.title}" удалено')
        ad.delete()
        return redirect('home')  # или куда тебе нужно после удаления

    return render(request, 'confirm_delete.html', {'ad': ad})


@login_required
def edit_ad(request, pk: int):
    ad = get_object_or_404(Ad, pk=pk)

    if ad.owner != request.user:
        return HttpResponseForbidden("У вас нет прав на редактирование этого объявления!")

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)  # Заполняем форму данными из изменяемого объявления
        if form.is_valid():
            ad = form.save()
            messages.success(request, f'Объявление "{ad.title}" изменено')
            return redirect('ad_detail', pk=ad.pk)  # После сохранения — на страницу объявления
    else:
        form = AdForm(instance=ad)

    return render(request, 'edit_ad.html', {'form': form, 'ad': ad})


def search_and_filter_ads(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    condition = request.GET.get('condition', '')

    ads = Ad.objects.all()

    if query:
        ads = ads.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category:
        ads = ads.filter(category=category)
    if condition:
        ads = ads.filter(condition=condition)

    paginator = Paginator(object_list=ads, per_page=2)  # ads.order_by('-created_at')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем уникальные категории из базы
    categories = Ad.objects.values_list('category', flat=True).distinct()
    # Получаем доступные состояния из choices модели
    CONDITION_CHOICES = Ad.CONDITION_CHOICES

    return render(request, 'ads_list.html', {
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'condition': condition,
        'categories': categories,
        'condition_choices': CONDITION_CHOICES,
    })


@login_required
def create_exchange_offer(request):
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            exchange_offer = form.save(commit=False)
            # Проверяем, что ad_sender_id принадлежит текущему пользователю (защита от поддельных POST-запросов)
            if exchange_offer.ad_sender_id.owner != request.user:
                messages.error(request, "Вы можете отправлять предложения только от своих объявлений")
                return redirect('ads_list')

            # Можно добавить проверку, чтобы ad_receiver не был объявлением того же пользователя
            # (защита от поддельных POST-запросов)
            if exchange_offer.ad_receiver_id.owner == request.user:
                messages.error(request, "Нельзя отправлять предложение самому себе")
                return redirect('ads_list')

            exchange_offer.save()
            messages.success(request, "Предложение обмена отправлено!")
            return redirect('home')  # или return redirect('ad_detail', pk=offer.ad_receiver.pk)
    else:
        form = ExchangeProposalForm()
        # чтобы предлагать отдать можно было только свои объявления
        form.fields['ad_sender_id'].queryset = Ad.objects.filter(owner=request.user)
        form.fields['ad_receiver_id'].queryset = Ad.objects.exclude(owner=request.user)
    return render(request, 'exchange_offer.html', {'form': form})


# @login_required
# def my_offers(request):
#     my_ads = Ad.objects.filter(owner=request.user)  # или лучше user_ads?
#
#     # не доступ к полям, а указание Django ORM, как сформировать SQL-запрос
#     sent_offers = ExchangeOffer.objects.filter(ad_sender_id__owner=request.user)
#     received_offers = ExchangeOffer.objects.filter(ad_receiver_id__in=my_ads)
#
#     return render(request, 'my_offers.html', {
#         'sent_offers': sent_offers,
#         'received_offers': received_offers,
#     })


@login_required
def respond_offer(request, offer_id):
    offer = get_object_or_404(ExchangeProposal, offer_id=offer_id)

    # Проверяем, что текущий пользователь владеет объявлением-получателем
    if offer.ad_receiver_id.owner != request.user:
        messages.error(request, "У вас нет прав изменять этот запрос.")
        return redirect('my_offers')

    if request.method == 'POST':
        action = request.POST.get('action')  # в html-коде кнопки имеют name='action' и value='accept' например
        if action == 'accept':
            offer.status = 'accepted'
            # Тут добавила логику обмена или уведомления
            messages.success(request, "Вы приняли предложение обмена!")
        elif action == 'reject':
            offer.status = 'rejected'
            messages.success(request, "Вы отклонили предложение обмена")
        else:
            messages.error(request, "Неверное действие")
            return redirect('my_offers')

        offer.save()
        return redirect('my_offers')

    # На GET не должна попадать — можно редиректить
    return redirect('my_offers')


@login_required
def filter_offers(request):
    sender_username = request.GET.get('sender', '')  # username отправителя
    receiver_username = request.GET.get('receiver', '')  # username получателя
    offer_status = request.GET.get('status', '')

    my_ads = Ad.objects.filter(owner=request.user)

    sent_offers = ExchangeProposal.objects.none()
    received_offers = ExchangeProposal.objects.none()

    filters_applied = sender_username or receiver_username or offer_status

    if filters_applied:
        sent_offers = ExchangeProposal.objects.filter(ad_sender_id__owner=request.user)
        if receiver_username:
            sent_offers = sent_offers.filter(ad_receiver_id__owner__username__icontains=receiver_username)
        if offer_status:
            sent_offers = sent_offers.filter(status=offer_status)

        # Входящие (текущий пользователь — владелец объявления)
        received_offers = ExchangeProposal.objects.filter(ad_receiver_id__in=my_ads)
        if sender_username:
            received_offers = received_offers.filter(ad_sender_id__owner__username__icontains=sender_username)
        if receiver_username:
            received_offers = received_offers.filter(ad_receiver_id__owner__username__icontains=receiver_username)
        if offer_status:
            received_offers = received_offers.filter(status=offer_status)

    else:
        # Если фильтры не заданы — показываем все предложения, где участвует пользователь
        sent_offers = ExchangeProposal.objects.filter(ad_sender_id__owner=request.user)
        received_offers = ExchangeProposal.objects.filter(ad_receiver_id__in=my_ads)

    sent_paginator = Paginator(sent_offers, per_page=2)
    received_paginator = Paginator(received_offers, per_page=2)

    sent_page = sent_paginator.get_page(request.GET.get('sent_page'))
    received_page = received_paginator.get_page(request.GET.get('received_page'))

    STATUS_CHOICES = ExchangeProposal.StatusChoices.choices

    return render(request, 'filter_offers.html', {
        'sent_page': sent_page,
        'received_page': received_page,
        'sender_username': sender_username,
        'receiver_username': receiver_username,
        'offer_status': offer_status,
        'status_choices': STATUS_CHOICES,
    })


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)