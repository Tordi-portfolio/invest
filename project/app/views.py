from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib import messages
from .models import Wallet, Plan
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from django.urls import reverse
from .models import *
from bs4 import BeautifulSoup


import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

# def scrape_quotes(request):
#     url = 'https://quotes.toscrape.com'
#     response = requests.get(url)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         quotes_data = []

#         quotes = soup.find_all('div', class_='quote')
#         for quote in quotes:
#             text = quote.find('span', class_='text').get_text(strip=True)
#             author = quote.find('small', class_='author').get_text(strip=True)
#             quotes_data.append({'text': text, 'author': author})

#         return render(request, 'quotes.html', {'quotes': quotes_data})
#     else:
#         return render(request, 'quotes.html', {'error': 'Failed to fetch data'})



# def scrape_quotes(request):
#     url = 'https://coinmarketcap.com/currencies/ethereum/'
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
#     }
#     response = requests.get(url)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         quotes_data = []

#         quotes = soup.find_all('div', class_='quote')
#         for quote in quotes:
#             text = quote.find('span', class_='sc-65e7f566-0 WXGwg base-text').get_text(strip=True)
#             author = quote.find('small', class_='author').get_text(strip=True)
#             quotes_data.append({'text': text, 'author': author})

#         return render(request, 'quotes.html', {'quotes': quotes_data})
#     else:
#         return render(request, 'quotes.html', {'error': 'Failed to fetch data'})


def scrape_quotes(request):
    url = 'https://coinmarketcap.com/currencies/ethereum/'  # Replace with actual page URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the <span> with the specific data-test attribute
        price_span = soup.find('span', attrs={'data-test': 'text-cdp-price-disclaimer'})

        if price_span:
            price = price_span.get_text(strip=True)
        else:
            price = "Price not found"

        return render(request, 'quotes.html', {'price': price})
    else:
        return render(request, 'quotes.html', {'price': 'Failed to fetch page'})



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request, 'home.html', {})

def base(request):
    return render(request, 'base.html', {})


def dashboard(request):
    posts = Plan.objects.all()
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'plan/dashboard.html', {'wallet': wallet, 'posts': posts})


def view_plan(request, pk):
    posts = Plan.objects.get(id=pk)
    return render(request, 'plan/view_plan.html', {'posts': posts})

def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        
            email_message = EmailMessage(
                'Reset your password', # email subject
                email_body,
                settings.EMAIL_HOST_USER, # email sender
                [email] # email  receiver 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')
    return render(request, 'accounts/forgot_password.html')


def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')

    return redirect('forgot_password')



def ResetPassword(request, reset_id):

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)

    
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')
        
    return render(request, 'accounts/reset_password.html')