from datetime import datetime, timezone


async def get_health_payload() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

