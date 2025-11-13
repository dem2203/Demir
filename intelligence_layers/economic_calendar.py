"""
ECONOMIC CALENDAR ENTEGRASYONU
- Ekonomik haberler/yüksek etki event'lar öncesi işlemi durdurur.
"""
import requests
from datetime import datetime, timedelta

class EconomicCalendar:
    api_url = "https://nfs.fxeconomic.com/calendar/api"  # Örnek: Gerçek event API veya alternatifi

    @staticmethod
    def get_high_impact_events(date=None):
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        # Gerçek API ile değiştirin
        params = {"date": date, "impact": "high"}
        response = requests.get(EconomicCalendar.api_url, params=params)
        if response.ok:
            events = response.json().get("events", [])
            return [e for e in events if e.get("impact") == "high"]
        return []

    @staticmethod
    def should_pause_trading(upcoming_events, now=None, pre_minutes=60):
        # Olay başlamadan 1 saat önce işlemleri durdur
        now = now or datetime.utcnow()
        for event in upcoming_events:
            t = datetime.strptime(event["time_utc"], "%Y-%m-%dT%H:%M:%SZ")
            if 0 <= (t - now).total_seconds() < pre_minutes * 60:
                return True, event
        return False, None
