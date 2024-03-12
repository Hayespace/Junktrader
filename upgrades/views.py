from django.shortcuts import render, redirect, reverse
from django.conf import settings
from .models import Upgrade
from django.contrib import messages
import stripe

def all_upgrades(request):
    upgrades = Upgrade.objects.all()
    context = {'upgrades': upgrades}
    return render(request, 'upgrades/all_upgrades.html', context)

def upgrade_success(request, upgrade_id):
    # Retrieve the upgrade object based on the upgrade_id
    upgrade = Upgrade.objects.get(pk=upgrade_id)
    
    # Render a template with a success message
    return redirect('open_backpack')


def purchase_upgrade(request, upgrade_id):
    # Retrieve the upgrade object based on the upgrade_id
    upgrade = Upgrade.objects.get(pk=upgrade_id)

    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': upgrade.name,
                    },
                    'unit_amount': int(upgrade.price * 100),  
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('upgrade_success', kwargs={'upgrade_id': upgrade_id})),  # Redirect to the success page after successful payment
            cancel_url=request.build_absolute_uri(reverse('all_upgrades')),  # Redirect back to the upgrades page if payment is cancelled
        )

        # Redirect to the checkout session URL, which opens in a new window
        return redirect(session.url)

    # Update session data with the new capacity
    request.session['backpack_capacity'] = upgrade.capacity
    
    # Add a success message
    messages.success(request, f"Successfully purchased {upgrade.name}. Backpack capacity increased to {upgrade.capacity}.")
    
    return redirect('open_backpack')
