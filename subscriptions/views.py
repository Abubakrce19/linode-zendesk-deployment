import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # new
from django.http.response import JsonResponse, HttpResponse  # updated
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import StripeCustomer  # new



from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.views.generic import FormView
from django.urls import reverse
import json 
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from users.models import CustomUser



class Upgrade(View):
    template = "upgrade.html"
    def get(self, request, *args, **kwargs):
        try:
            print(request.user)
            # Retrieve the subscription & product
            stripe_customer = StripeCustomer.objects.get(user=request.user)
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
            product = stripe.Product.retrieve(subscription.plan.product)

            # Feel free to fetch any additional data from 'subscription' or 'product'
            # https://stripe.com/docs/api/subscriptions/object
            # https://stripe.com/docs/api/products/object

            context = {

            }

            return render(request, self.template, context)

        except StripeCustomer.DoesNotExist:
            return render(self.request, self.template)


class StripeConfig(View):
    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
            return JsonResponse(stripe_config, safe=False)


class Create_checkout_session(View):
    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            domain_url = 'http://localhost:8000/'
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url + 'cancel/',
                    payment_method_types=['card'],
                    mode='subscription',
                    line_items=[
                        {
                            'price': settings.STRIPE_PRICE_ID,
                            'quantity': 1,
                        }
                    ]
                )
                return JsonResponse({'sessionId': checkout_session['id']})
            except Exception as e:
                return JsonResponse({'error': str(e)})


class Success(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'success.html')


class Cancel(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'cancel.html')



from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class Stripe_webhook(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Fetch all the required data from session
            client_reference_id = session.get('client_reference_id')
            stripe_customer_id = session.get('customer')
            stripe_subscription_id = session.get('subscription')

            print(client_reference_id, stripe_customer_id, stripe_subscription_id)

            # Get the user and create a new StripeCustomer
            user = CustomUser.objects.get(id=client_reference_id)
            StripeCustomer.objects.create(
                user=user,
                stripeCustomerId=stripe_customer_id,
                stripeSubscriptionId=stripe_subscription_id,
            )
            user.subscription_status = 'true'
            user.user_plan = 'ZendeskAI_PRO'
            user.docs_left = 1000
            user.save()
            print(user.username + ' just subscribed.')

        return HttpResponse(status=200)
