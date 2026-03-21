from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.services.daily_log import queue_pending_message, get_today_summary

# BackgroundScheduler runs jobs in a background thread while FastAPI keeps serving requests.
# It starts when the app starts and shuts down cleanly when the app stops.
scheduler = BackgroundScheduler()


def morning_checkin():
    """
    Fires at 5:00 AM every day.
    Queues a wake-up message from Anyanwu. It'll appear the next time the user opens the app.
    Anyanwu's tone here should match her personality — direct, not gentle.
    """
    message = "You should be up by now. What's the plan for today?"
    queue_pending_message(message)


def evening_checkin():
    """
    Fires at 9:00 PM every day.
    Checks what the user has already logged today, then crafts a message that references it.
    If nothing was logged, she calls that out. If things were logged, she asks what's next.
    This message goes into the pending queue — delivered when the user opens the app.
    """
    summary = get_today_summary()

    if summary:
        # User logged things today — Anyanwu acknowledges and asks about the rest
        message = (
            f"End of day check-in. {summary}. "
            "What didn't get done that you said it would?"
        )
    else:
        # Nothing logged — Anyanwu calls it out directly
        message = (
            "9pm. You haven't logged anything today. "
            "Was today a wash, or did things happen that you just didn't track? "
            "Tell me what you actually did."
        )

    queue_pending_message(message)


def start_scheduler():
    """
    Register both jobs and start the scheduler.
    Called once on FastAPI app startup via the lifespan event in main.py.

    CronTrigger uses 24-hour time. hour=5, minute=0 = 5:00 AM.
    The scheduler runs in the local system timezone by default.
    """
    scheduler.add_job(
        morning_checkin,
        CronTrigger(hour=5, minute=0),
        id="morning_checkin",
        replace_existing=True,
    )
    scheduler.add_job(
        evening_checkin,
        CronTrigger(hour=21, minute=0),  # 21:00 = 9:00 PM
        id="evening_checkin",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler():
    """Cleanly shut down the scheduler when FastAPI stops. Prevents zombie threads."""
    if scheduler.running:
        scheduler.shutdown()
