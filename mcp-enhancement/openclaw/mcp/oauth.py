import json
import os
import time
import hashlib
import base64
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Token:
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    issued_at: int = 0

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        if self.issued_at == 0:
            return True
        return time.time() > (self.issued_at + self.expires_in - buffer_seconds)


class OAuthProvider:
    PROVIDERS = {
        "google": {
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "scope": "openid email profile",
        },
        "github": {
            "auth_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "scope": "user:email read:user",
        },
        "microsoft": {
            "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "scope": "openid email profile",
        },
    }

    def __init__(
        self,
        provider: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        config_path: Optional[str] = None,
    ):
        if provider not in self.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. Supported: {list(self.PROVIDERS.keys())}"
            )

        self.provider = provider
        self.config = self.PROVIDERS[provider]
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.config_path = config_path or os.path.expanduser(
            "~/.openclaw/mcp_oauth_tokens.json"
        )

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def _generate_state(self) -> str:
        raw = f"{time.time()}{self.client_id}".encode()
        return base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode()[:32]

    def get_authorization_url(
        self, state: Optional[str] = None, scopes: Optional[list] = None
    ) -> tuple[str, str]:
        if state is None:
            state = self._generate_state()

        scope = scopes or self.config.get("scope", "").split()
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": " ".join(scope),
            "access_type": "offline" if self.provider == "google" else "",
        }

        if self.provider == "microsoft":
            params["response_mode"] = "query"

        params = {k: v for k, v in params.items() if v}

        return f"{self.config['auth_url']}?{urllib.parse.urlencode(params)}", state

    def _load_tokens(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except:
            return {}

    def _save_tokens(self, tokens: Dict[str, Any]):
        with open(self.config_path, "w") as f:
            json.dump(tokens, f, indent=2)

    def get_token(self, auth_code: str) -> Token:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        headers = {"Accept": "application/json"}
        if self.provider == "github":
            headers["Accept"] = "application/json"

        req = urllib.request.Request(
            self.config["token_url"],
            data=urllib.parse.urlencode(data).encode(),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                token_data = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            raise ValueError(f"Token exchange failed: {e.read().decode()}")

        token = Token(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
            issued_at=int(time.time()),
        )

        tokens = self._load_tokens()
        tokens[self.provider] = asdict(token)
        self._save_tokens(tokens)

        return token

    def refresh_token(self, refresh_token: Optional[str] = None) -> Token:
        if refresh_token is None:
            tokens = self._load_tokens()
            provider_tokens = tokens.get(self.provider, {})
            refresh_token = provider_tokens.get("refresh_token")

        if not refresh_token:
            raise ValueError("No refresh token available")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = {"Accept": "application/json"}

        req = urllib.request.Request(
            self.config["token_url"],
            data=urllib.parse.urlencode(data).encode(),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                token_data = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            raise ValueError(f"Token refresh failed: {e.read().decode()}")

        token = Token(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            refresh_token=token_data.get("refresh_token", refresh_token),
            scope=token_data.get("scope"),
            issued_at=int(time.time()),
        )

        tokens = self._load_tokens()
        tokens[self.provider] = asdict(token)
        self._save_tokens(tokens)

        return token

    def get_valid_token(self, force_refresh: bool = False) -> Optional[Token]:
        tokens = self._load_tokens()
        provider_tokens = tokens.get(self.provider)

        if not provider_tokens:
            return None

        token = Token(**provider_tokens)

        if force_refresh or token.is_expired():
            if token.refresh_token:
                return self.refresh_token(token.refresh_token)
            return None

        return token

    def revoke_token(self, token: Optional[str] = None):
        if token is None:
            tokens = self._load_tokens()
            provider_tokens = tokens.get(self.provider, {})
            token = provider_tokens.get("access_token")

        if not token:
            return

        revoke_urls = {
            "google": "https://oauth2.googleapis.com/revoke",
            "microsoft": "https://login.microsoftonline.com/common/oauth2/v2.0/logout",
        }

        if self.provider in revoke_urls:
            data = {"token": token}
            req = urllib.request.Request(
                revoke_urls[self.provider],
                data=urllib.parse.urlencode(data).encode(),
                method="POST",
            )
            try:
                urllib.request.urlopen(req)
            except:
                pass

        tokens = self._load_tokens()
        tokens.pop(self.provider, None)
        self._save_tokens(tokens)


def create_oauth_provider(provider: str, config: Dict[str, str]) -> OAuthProvider:
    required = ["client_id", "client_secret", "redirect_uri"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")

    return OAuthProvider(
        provider=provider,
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri=config["redirect_uri"],
        config_path=config.get("config_path"),
    )
