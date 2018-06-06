from django.shortcuts import get_object_or_404, redirect, render
import os
import stripe
from django.conf import settings

"""
Simple view only accessible via the URL to donate/accept payments temporarily
"""

def payment(request):


    if (request.method == "POST"):
        stripe.api_key = settings.STRIPE_API_KEY
        print(stripe.api_key)
        # Token is created using Checkout or Elements
        # Get the payment token ID submitted by the form
        token = request.POST['stripeToken'] # Using Flask

        charge = stripe.Charge.create(
            amount=10000, # this is pennies?
            currency='usd',
            description='dev charge',
            source=token,
        )

        # TODO: validate that the payment was successful
        return render(request, 'core/success_payment.html')

    return render(request, 'core/payment.html')
