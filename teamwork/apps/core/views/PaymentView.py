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

    # Grabs either the TEST version or the LIVE public key, dependent on IS_PRODUCTION
    if settings.IS_PRODUCTION:
        publicKey = "pk_live_gzjeFHYF6EZxNfmJy6ZJS0Ua"
    else:
        publicKey = "pk_test_P7FKe7l3uiySL3UAPy7mvRxM"

    paymentForm = PaymentForm()

    # If POST, then handle the payment, creating a stripe.Charge object
    if (request.method == "POST"):
        paymentForm = PaymentForm(request.POST)

        if not paymentForm.is_valid():
            # TODO: show error message, also TODO: validate values as being typed, display error message instantly.
            return redirect('/payment')

        # Grab the As-Typed Amount, the Decimal Amount and Memo from the form
        asTypedAmount = request.POST.get('amount')
        decimalAmount = Decimal(asTypedAmount)
        memo = request.POST.get('memo')

        # Grab the API Key from the setttings file
        stripe.api_key = settings.STRIPE_API_KEY

        # Get the payment token ID submitted by the form
        token = request.POST['stripeToken']

        # Round the decimalAmount to 2 decimal spaces
        roundedAmount = round(decimalAmount, 2)

        # Force the amount to an integer since stripe charges in pennies
        amount = int(decimalAmount * 100)

        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Donation - ' + memo,
            source=token,
        )

        # TODO: validate that the payment was successful
        return render(request, 'core/success_payment.html', {'amount':amount, 'memo':memo, 'asTypedAmount':asTypedAmount})

    return render(request, 'core/payment.html', {'paymentForm':paymentForm, 'publicKey':publicKey})

"""
View that displays the invalid payment template
"""
def invalid_template(request):
    return render(request, 'core/invalid_payment.html')
