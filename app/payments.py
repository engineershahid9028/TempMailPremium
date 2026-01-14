import stripe
from .settings import STRIPE_SECRET,DOMAIN
stripe.api_key=STRIPE_SECRET

def create_stripe_checkout(amount_usd:int,user_id:int):
    session=stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data":{
                "currency":"usd",
                "product_data":{"name":"TempMailPremium — Premium Plan"},
                "unit_amount":amount_usd*100,
            },
            "quantity":1,
        }],
        mode="payment",
        success_url=f"https://{DOMAIN}/success?u={user_id}",
        cancel_url=f"https://{DOMAIN}/cancel",
        metadata={"user_id":str(user_id)}
    )
    return session.url
