from django.shortcuts import get_object_or_404, redirect, render
import os
import stripe
from django.conf import settings
from teamwork.apps.core.forms import PaymentForm

"""
Simple view only accessible via the URL to donate/accept payments temporarily
"""

def payment(request):

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
        return render(request, 'core/success_payment.html')

    return render(request, 'core/payment.html', {'paymentForm':paymentForm})
