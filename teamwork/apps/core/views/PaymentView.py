from django.shortcuts import get_object_or_404, redirect, render
import os
import stripe
from decimal import Decimal
from django.conf import settings
from teamwork.apps.core.forms import PaymentForm

"""
Simple view only accessible via the URL to donate/accept payments temporarily
"""

def payment(request):

    if settings.IS_PRODUCTION:
        publicKey = "pk_live_gzjeFHYF6EZxNfmJy6ZJS0Ua"
    else:
        publicKey = "pk_test_P7FKe7l3uiySL3UAPy7mvRxM"

    paymentForm = PaymentForm()

    if (request.method == "POST"):
        paymentForm = PaymentForm(request.POST)

        if not paymentForm.is_valid():
            print("form is not valid")
            return redirect('core/payment.html')

        amount = Decimal(request.POST.get('amount'))
        memo = request.POST.get('memo')

        stripe.api_key = settings.STRIPE_API_KEY

        # Token is created using Checkout or Elements
        # Get the payment token ID submitted by the form
        token = request.POST['stripeToken']
        
        # TODO: add a mask to the form to force decimal entry
        if ((amount % 1) != 0):
            # amount contains pennies. i.e: $3.95
            print("amount contains pennies.")
            amount = int(amount * 100)

        charge = stripe.Charge.create(
            amount=amount, # this is pennies?
            currency='usd',
            description='Donation',
            source=token,
        )

        # TODO: validate that the payment was successful
        return render(request, 'core/success_payment.html', {'amount':amount, 'memo':memo})

    return render(request, 'core/payment.html', {'paymentForm':paymentForm, 'publicKey':publicKey})
