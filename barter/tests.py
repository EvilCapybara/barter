from django.test import TestCase, Client, override_settings  # в Django используется unittest
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from ads.models import Ad
from exchanges.models import ExchangeProposal


User = get_user_model()  # класс модели, не объект (функция возвращает класс) - либо можно просто импортировать,
# так как это жестко прописано в settings.AUTH_USER_MODEL


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # для проверки прав на редактирование
        self.other_user = User.objects.create_user(username='othertestuser', password='othertestpassword')


class CreateAdTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.create_url = reverse(viewname='create_ad')

    def test_create_ad_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')

        test_ad_data = {
            'title': 'Test Ad',
            'description': 'This is a test ad',
            'image_url': 'https://example.com/image.jpg',
            'category': 'Electronics',
            'condition': 'new',
        }

        previous_count = Ad.objects.count()

        response = self.client.post(path=self.create_url, data=test_ad_data)  # отправка POST-запроса

        self.assertEqual(response.status_code, 302)  # 302 - временное перенаправление

        self.assertEqual(Ad.objects.count(), previous_count + 1)  # проверка, что объявление появилось в БД
        ad = Ad.objects.last()
        self.assertEqual(ad.title, 'Test Ad')
        self.assertEqual(ad.owner, self.user)
        self.assertRedirects(response=response, expected_url=reverse('home'))

        # проверка сообщения об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('создано' in str(message) for message in messages))

    def test_create_ad_unauthenticated_user(self):
        response = self.client.get(path=self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)  # проверка url редиректа


class EditAdTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.user.password)

        self.ad = Ad.objects.create(
            title='Old title',
            description='Old description',
            category='Books',
            condition='used',
            owner=self.user
        )

    def test_edit_ad_success(self):
        response = self.client.post(path=reverse('edit_ad', kwargs={'pk': self.ad.pk}),
                                    data={
                                        'title': 'New title',
                                        'description': 'New description',
                                        'category': 'Tools',
                                        'condition': 'new',
                                    }
                                    )

        self.ad.refresh_from_db()

        self.assertEqual(self.ad.title, 'New title')
        self.assertEqual(self.ad.description, 'New description')
        self.assertEqual(self.ad.category, 'Tools')
        self.assertEqual(self.ad.condition, 'new')
        self.assertRedirects(response=response, expected_url=reverse('ad_detail', kwargs={'pk': self.ad.pk}))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('изменено' in str(message) for message in messages))

    @override_settings(DEBUG=False)
    def test_edit_ad_not_found_shows_custom_404(self):
        # попытка отредактировать объявление с несуществующим id
        response = self.client.get(reverse('edit_ad', kwargs={'pk': 9999999999}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_edit_ad_forbidden(self):
        # входим под другим пользователем, который не является автором объявления
        self.client.logout()
        self.client.login(username=self.other_user.username, password=self.other_user.password)

        response = self.client.get(reverse('edit_ad', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 403)


class DeleteAdTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.user.password)

        self.ad = Ad.objects.create(
            title='Delete me',
            description='To be deleted',
            category='Food',
            condition='used',
            owner=self.user
        )

    def test_delete_ad_success(self):
        response = self.client.post(reverse('delete_ad', kwargs={'pk': self.ad.pk}))

        # объявление должно быть удалено
        with self.assertRaises(Ad.DoesNotExist):
            Ad.objects.get(pk=self.ad.pk)

        self.assertRedirects(response, reverse('home'))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('удалено' in str(message) for message in messages))

    def test_delete_ad_forbidden(self):
        self.client.logout()
        self.client.login(username=self.other_user.username, password=self.other_user.password)

        response = self.client.post(reverse('delete_ad', kwargs={'pk': self.ad.pk}))

        self.assertEqual(response.status_code, 403)


class AdSearchFilterTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.user.password)

        # Объявления для тестов
        Ad.objects.create(
            title='iPhone 13',
            description='New iPhone',
            image_url='https://example.com/iphone.jpg',
            category='Electronics',
            condition='new',
            owner=self.user
        )
        Ad.objects.create(
            title='Apple Watch',
            description='Old but gold',
            image_url='https://example.com/watch.jpg',
            category='Electronics',
            condition='used',
            owner=self.user
        )
        Ad.objects.create(
            title='Barbie Doll',
            description='Brand new Barbie doll',
            image_url='https://example.com/barbie.jpg',
            category='Toys',
            condition='new',
            owner=self.user
        )

    def test_search_by_query(self):
        response = self.client.get(reverse('ads_list'), {'q': 'iPhone'})
        self.assertEqual(response.status_code, 200)  # 200 - успешный ответ
        self.assertContains(response, 'iPhone')
        self.assertNotContains(response, 'Apple Watch')

        # response = self.client.get(reverse('ads_list'), {'q': 'Apple'})
        # self.assertEqual(response.status_code, 200)  # 200 - успешный ответ
        # self.assertNotContains(response, 'iPhone')
        # self.assertContains(response, 'Apple Watch')

    def test_filter_by_category(self):
        response = self.client.get(reverse('ads_list'), {'category': 'Toys'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'iPhone')
        self.assertNotContains(response, 'Apple Watch')
        self.assertContains(response, 'Barbie Doll')

    def test_filter_by_condition(self):
        response = self.client.get(reverse('ads_list'), {'condition': 'new'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone')
        self.assertNotContains(response, 'Apple Watch')
        self.assertContains(response, 'Barbie Doll')

    def test_combined_filters(self):
        response = self.client.get(reverse('ads_list'), {
            'category': 'Electronics',
            'condition': 'new',
            'q': 'Apple'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'iPhone')
        self.assertNotContains(response, 'Apple Watch')
        self.assertNotContains(response, 'Barbie Doll')
        self.assertContains(response, 'Объявлений не найдено')

    def test_ads_pagination(self):
        for i in range(5):
            Ad.objects.create(
                title=f'Test Ad {i}',
                description='description',
                image_url='https://example.com/image.jpg',
                category='Другое',
                condition='used',
                owner=self.user
            )

        response = self.client.get(reverse('ads_list'), {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 2)

        response = self.client.get(reverse('ads_list'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 2)

        response = self.client.get(reverse('ads_list'), {'page': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)  # 5 = 2 + 2 + 1


class ExchangeOfferTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.user.password)

        self.ad1 = Ad.objects.create(
            title='Ad 1', description='Description', category='Pets', condition='new',
            owner=self.user
        )
        self.ad2 = Ad.objects.create(
            title='Ad 2', description='Description', category='Pets', condition='new',
            owner=self.other_user
        )

    def test_create_exchange_offer(self):
        previous_count = ExchangeProposal.objects.count()

        response = self.client.post(reverse('create_exchange_offer'), {
            'ad_sender_id': self.ad1.id,
            'ad_receiver_id': self.ad2.id,
            'comment': 'Готов обменяться',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url=reverse('home'))
        self.assertEqual(ExchangeProposal.objects.count(), previous_count + 1)

        offer = ExchangeProposal.objects.last()
        self.assertEqual(offer.ad_sender_id, self.ad1.id)
        self.assertEqual(offer.ad_receiver_id, self.ad2.id)
        self.assertEqual(offer.status, 'pending')
        self.assertEqual(offer.comment, 'Готов обменяться')

    def test_cannot_offer_to_self(self):
        previous_count = ExchangeProposal.objects.count()

        response = self.client.post(reverse('create_exchange_offer'), {
            'ad_sender_id': self.ad1.id,
            'ad_receiver_id': self.ad1.id,
            'comment': 'Попытка обменяться с собой',
        })

        self.assertEqual(ExchangeProposal.objects.count(), previous_count)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('самому себе' in str(m) for m in messages))

    def test_cannot_offer_from_other_user(self):
        self.client.logout()
        self.client.login(username=self.other_user.username, password=self.other_user.password)

        previous_count = ExchangeProposal.objects.count()

        response = self.client.post(reverse('create_exchange_offer'), {
            'ad_sender_id': self.ad1.id,
            'ad_receiver_id': self.ad2.id,
            'comment': 'Пытаюсь отправить не от своего объявления',
        })

        self.assertEqual(ExchangeProposal.objects.count(), previous_count)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('только от своих' in str(m) for m in messages))


class RespondOfferTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.other_user.username, password=self.other_user.password)

        self.ad1 = Ad.objects.create(
            title='Ad 1', description='Description', category='Pets', condition='new',
            owner=self.user
        )
        self.ad2 = Ad.objects.create(
            title='Ad 2', description='Description', category='Pets', condition='new',
            owner=self.other_user
        )

        self.offer = ExchangeProposal.objects.create(
            ad_sender_id=self.ad1.id,
            ad_receiver_id=self.ad2.id,
            comment='Согласен?',
            status='pending'
        )

    def test_accept_offer(self):
        url = reverse('respond_offer', kwargs={'offer_id': self.offer.offer_id})
        response = self.client.post(url, {'action': 'accept'})

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, 'accepted')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('приняли' in str(m) for m in messages))

    def test_reject_offer(self):
        url = reverse('respond_offer', kwargs={'offer_id': self.offer.offer_id})
        response = self.client.post(url, {'action': 'reject'})

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, 'rejected')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('отклонили' in str(m) for m in messages))

    def test_cannot_respond_if_not_receiver(self):
        self.client.login(username=self.user.username, password=self.user.password)
        url = reverse('respond_offer', kwargs={'offer_id': self.offer.offer_id})
        response = self.client.post(url, {'action': 'accept'})

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, 'pending')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("нет прав" in str(m) for m in messages))

    def test_invalid_action(self):
        url = reverse('respond_offer', kwargs={'offer_id': self.offer.offer_id})
        response = self.client.post(url, {'action': 'foobar'})

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, 'pending')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Неверное действие" in str(m) for m in messages))