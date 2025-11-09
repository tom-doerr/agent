"""Context provider for nlco_iter - handles system info, weather, etc."""

import datetime
import subprocess
import json
from pathlib import Path


# Load location from validated config
from config import get_config

config = get_config()
LOCATION = config.weather.location.city if config.weather.location else "Mering"


def get_post_queue_status():
    """Return a status string describing remaining posts in the queue."""
    queue_path = config.social.post_queue_path if hasattr(config, "social") else None
    if not queue_path:
        return ""

    try:
        raw = Path(queue_path).read_text()
    except FileNotFoundError:
        return f"Post queue: file not found at {queue_path}"
    except Exception as exc:  # pragma: no cover - unexpected I/O failure
        return f"Post queue: error reading {queue_path}: {exc}"

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return f"Post queue: invalid JSON at {queue_path}"

    if isinstance(data, list):
        count = len(data)
    elif isinstance(data, dict):
        posts = data.get("posts")
        count = len(posts) if isinstance(posts, list) else 0
    else:
        count = 0

    return f"Post queue: {count} posts remaining"


def get_autoposter_alert():
    """Warn if the posted posts file is stale or missing."""
    posted_path = config.social.posted_posts_path if hasattr(config, "social") else None
    if not posted_path:
        return ""

    path = Path(posted_path)
    if not path.exists():
        return f"Autoposter alert: posted posts file missing at {posted_path}"

    try:
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime, tz=datetime.timezone.utc)
    except OSError as exc:  # pragma: no cover - unexpected filesystem failure
        return f"Autoposter alert: unable to read posted posts file: {exc}"

    now = datetime.datetime.now(datetime.timezone.utc)
    minutes_since_edit = (now - mtime).total_seconds() / 60

    if minutes_since_edit > 35:
        formatted_time = mtime.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        return (
            "Autoposter alert: posted_posts.json last updated at "
            f"{formatted_time} ({minutes_since_edit:.0f} minutes ago)"
        )

    return ""


def get_weather_info():
    """Get weather information for configured location."""
    try:
        # Get current + 3 day forecast with hourly data
        weather_raw = subprocess.run(['curl', '-s', f'wttr.in/{LOCATION}?format=j1'], 
                                   capture_output=True, text=True, timeout=5).stdout
        w = json.loads(weather_raw)
        
        # Current conditions
        current = w['current_condition'][0]
        weather = (f"{LOCATION}: {current['weatherDesc'][0]['value']} {current['temp_C']}°C "
                  f"feels:{current['FeelsLikeC']}°C humidity:{current['humidity']}% "
                  f"wind:{current['windspeedKmph']}km/h pressure:{current['pressure']}mb")
        
        # Next 24 hours forecast - show every 3 hours
        weather += "\n    Next 24h (temp/rain/wind):"
        # wttr.in provides 8 data points per day (every 3 hours starting at 00:00)
        for day_idx in range(2):  # Today and tomorrow
            day_data = w['weather'][day_idx]
            for hour_idx in range(8):  # 8 x 3-hour intervals = 24 hours
                h = day_data['hourly'][hour_idx]
                hour = int(h['time']) // 100  # Convert "300" to 3, "1500" to 15
                weather += f"\n      {hour:02d}:00: {h['tempC']}°C/{h['precipMM']}mm/{h['windspeedKmph']}km/h {h['weatherDesc'][0]['value']}"
                if day_idx == 1 and hour_idx >= 7:  # Stop after 24 hours
                    break
        
        # 3-day forecast
        weather += "\n    3-day forecast:"
        for i, day in enumerate(w['weather'][:3]):
            day_name = ["Today", "Tomorrow", "Day 3"][i]
            weather += (f"\n      {day_name}: {day['hourly'][4]['weatherDesc'][0]['value']} "
                       f"{day['maxtempC']}°/{day['mintempC']}°C "
                       f"rain:{day['hourly'][4]['precipMM']}mm "
                       f"UV:{day['uvIndex']}")
        
        return weather
    except Exception as e:
        return f"{LOCATION}: unavailable (error: {str(e)})"


def get_system_info():
    """Get system memory and disk info."""
    mem = subprocess.run(['free', '-h'], capture_output=True, text=True, check=True).stdout
    df_output = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, check=True).stdout
    return f"'free -h':\n{mem}\n'df -h /':\n{df_output}"


def get_home_status():
    """Get home automation status if available."""
    try:
        from home_automation import get_home_status as get_status
        return get_status()
    except:
        return ""


def create_context_string():
    """Create the full context string for the AI."""
    now = datetime.datetime.now()
    context_parts = [
        f"Datetime: {now:%Y-%m-%d %H:%M:%S} ({now:%A})",
        f"Weather: {get_weather_info()}",
    ]
    
    # Add home status if available
    home_status = get_home_status()
    if home_status:
        context_parts.append(home_status)

    post_queue_status = get_post_queue_status()
    if post_queue_status:
        context_parts.append(post_queue_status)

    autoposter_alert = get_autoposter_alert()
    if autoposter_alert:
        context_parts.append(autoposter_alert)

    context_parts.append(get_system_info())

    return "\n".join(context_parts)
