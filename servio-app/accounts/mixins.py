from django.core.cache import cache
from django.http import HttpRequest
from django.utils import timezone
from datetime import timedelta
import hashlib


class LoginRateLimitMixin:
    max_attempts = 4
    cooldown_hours = 1
    
    def get_client_fingerprint(self, request:HttpRequest):
        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        raw = f"{ip}:{ua}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_cache_keys(self, fingerprint):
        return (
            f"login_attempts:{fingerprint}",
            f"login_lockout:{fingerprint}",
        )

    def is_locked_out(self, fingerprint):
        attempts_key, lockout_key = self.get_cache_keys(fingerprint)
        lockout_until = cache.get(lockout_key)
        now = timezone.now()

        if lockout_until and lockout_until > now:
            remaining = lockout_until - now
            return True, int(remaining.total_seconds() // 60)
        return False, None

    def register_failed_attempt(self, fingerprint):
        attempts_key, lockout_key = self.get_cache_keys(fingerprint)

        attempts = cache.get(attempts_key, 0) + 1
        cache.set(attempts_key, attempts, timeout=3600)

        if attempts >= self.max_attempts:
            lockout_until = timezone.now() + timedelta(hours=self.cooldown_hours)
            cache.set(lockout_key, lockout_until, timeout=self.cooldown_hours * 3600)
            return False, self.cooldown_hours

        return True, self.max_attempts - attempts

    def reset_attempts(self, fingerprint):
        attempts_key, lockout_key = self.get_cache_keys(fingerprint)
        cache.delete(attempts_key)
        cache.delete(lockout_key)
