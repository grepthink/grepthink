from django.shortcuts import get_object_or_404, redirect, render
import os
import stripe
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
            return

        amount = request.POST.get('amount')
        memo = request.POST.get('memo')

        stripe.api_key = settings.STRIPE_API_KEY

        # Token is created using Checkout or Elements
        # Get the payment token ID submitted by the form
        token = request.POST['stripeToken']

        # TODO: convert amount from dollars to pennies if needed. Better yet, add a mask to the form to force decimal entry

        charge = stripe.Charge.create(
            amount=amount, # this is pennies?
            currency='usd',
            description='Donation',
            source=token,
        )

        # TODO: validate that the payment was successful
        return render(request, 'core/success_payment.html', {'amount':amount, 'memo':memo})

    return render(request, 'core/payment.html', {'paymentForm':paymentForm, 'publicKey':publicKey})
