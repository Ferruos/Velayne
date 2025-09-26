import logging

class LogUpdateMiddleware:
    async def __call__(self, handler, event, data):
        try:
            text = getattr(event, "text", None) or getattr(getattr(event, "message", None), "text", None)
            logging.info("[UPDATE] %s %s", event.__class__.__name__, (text or "")[:64])
        except Exception:
            logging.debug("[UPDATE] %s", event)
        return await handler(event, data)