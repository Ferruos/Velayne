import json
import datetime
import redis
from typing import Dict, Any
from services.logging import get_logger

class BlendManager:
    def __init__(self, redis_url: str):
        self.redis = redis.Redis.from_url(redis_url)
        self.key = "blend:current"
        self.logger = get_logger("blend")

    def publish_blend(self, blend_json: Dict[str, Any]):
        try:
            blend_json['created_at'] = datetime.datetime.utcnow().isoformat()
            version = blend_json.get('version', datetime.datetime.utcnow().strftime('%Y%m%d%H%M'))
            blend_json['version'] = version
            self.redis.set(self.key, json.dumps(blend_json))
            self.redis.publish('blend_updates', json.dumps({'version': version}))
            self.logger.info(f"Blend {version} published.")
        except Exception as e:
            self.logger.error(f"Ошибка публикации blend: {e}")

    def get_current_blend(self) -> Dict[str, Any]:
        try:
            val = self.redis.get(self.key)
            if val is None:
                raise RuntimeError("No blend published yet")
            return json.loads(val)
        except Exception as e:
            self.logger.error(f"Ошибка получения blend: {e}")
            return {}

    def subscribe_updates(self):
        pubsub = self.redis.pubsub()
        pubsub.subscribe('blend_updates')
        return pubsub