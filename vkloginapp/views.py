from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
import requests


# ID приложения
client_id = '5744475'
# Защищенный ключ
client_secret = 'VJMSQYpDxaWVWV1540Qz'
# Адрес сайта
redirect_uri = 'http://127.0.0.1:8000/vkloginapp/complete/'
# Метод получения данных VK
method_url = 'https://api.vk.com/method/'



def home(request):
    # Проверяем аунтефикацию пользователя
    if not request.user.is_authenticated():
        return render(request, 'home.html')
    user = request.user
    user_id = user.username
    try:
        friends = get_friends(user_id)
    except KeyError:
        return render(request, 'home.html')
    return render(request, 'complete.html', {'user': user, 'friends': friends})


def auth(request):
    # Запускаем авторизацию VK
    return redirect('https://oauth.vk.com/authorize?'
                    'client_id=%s&redirect_uri=%s&scope=%s&display=%s'
                    % (client_id, redirect_uri, 'email', 'page'))


def complete(request):
    # Получаем данные пользователя
    code = request.GET['code']
    par_token = {'client_id': client_id, 'client_secret': client_secret,
                 'redirect_uri': redirect_uri, 'code': code}
    response = requests.get('https://oauth.vk.com/access_token', params=par_token)
    token = response.json()['access_token']
    email = response.json()['email']
    response_user = requests.get(method_url + 'users.get',
                                 params={'access_token': token})
    user_vk = response_user.json()['response'][0]
    return create_user(request, user_vk, email)


def get_friends(user_id):
    # Получаем друзей
    response_friends = requests.get(method_url + 'friends.get',
                                    params={'user_id': user_id, 'count': '5', 'fields': '[nickname]'})
    friends = response_friends.json()['response']
    return friends


def create_user(request, user_vk, email):
    # Регистрируем нового пользователя(если нужно) и выводим
    try:
        user = User.objects.get(username=user_vk['uid'])
    except User.DoesNotExist:
        user = None
    if not user:
        user = User.objects.create(username=user_vk['uid'], first_name=user_vk['first_name'],
                                   last_name=user_vk['last_name'], email=email,
                                   is_staff=False, is_active=True)
    login(request, user)
    return redirect('home')


def logout_view(request):
    # Выход
    logout(request)
    return redirect('home')
