from jinja2 import Template
from controllers.Celery.celery_worker import celery
from controllers.auth import send_email

def booking_confirmation_email_with_cost(user_email, lot_name, spot_id, start_time,end_time,cost):
    from datetime import datetime
    dt = datetime.fromisoformat(end_time)
    end_time = dt.strftime("%d %b %Y, %I:%M %p").lower()
    dt = datetime.fromisoformat(start_time)
    start_time = dt.strftime("%d %b %Y, %I:%M %p").lower()
    html_template = open("src/components/Email tickets/BookingSummary.html").read()
    html = Template(html_template).render(
        lot=lot_name,
        spot=spot_id,
        start=start_time,
        end=end_time,
        cost=cost
    )

    send_email.delay("SafePark Booking Confirmation", user_email, html)

def booking_confirmation_email_without_cost(user_email, lot_name, spot_id, start_time):
    from datetime import datetime
    dt = datetime.fromisoformat(start_time)
    start_time = dt.strftime("%d %b %Y, %I:%M %p").lower()
    html_template = open("src/components/Email tickets/BookingSummarywithoutcost.html").read()
    html = Template(html_template).render(
        lot=lot_name,
        spot=spot_id,
        start=start_time,
    )
    send_email.delay("SafePark Booking Confirmation", user_email, html)

def Endtimeprovided(user_email, lot_name, spot_id, start_time,end_time,cost):
    from datetime import datetime
    dt = datetime.fromisoformat(str(end_time))
    end_time = dt.strftime("%d %b %Y, %I:%M %p").lower()
    dt = datetime.fromisoformat(str(start_time))
    start_time = dt.strftime("%d %b %Y, %I:%M %p").lower()
    html_template = open("src/components/Email tickets/ProvidedEndTime.html").read()
    html = Template(html_template).render(
        lot=lot_name,
        spot=spot_id,
        start=start_time,
        end=end_time,
        cost=cost
    )

    send_email.delay("SafePark Booking Confirmation", user_email, html)