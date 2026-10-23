"""Explicit public-source acquisition and immutable, offline snapshot replay.

This module records what was retrieved and where a selected passage occurred.
It does not decide whether a passage proves a financial claim. Source specs and
retention permissions are reviewed inputs; website text never grants authority.
"""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import socket
from typing import Callable
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

MAX_BYTES = 2 * 1024 * 1024
MAX_ROBOTS_BYTES = 128 * 1024
TIMEOUT_SECONDS = 10
USER_AGENT = "InvestmentResearchSourceMVP/0.1"
SOURCE_VERSION = "source_snapshot_v1"
_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,99}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_TYPES = {"primary", "institution", "data_provider", "research", "news", "expert", "community"}
_MIME_TYPES = {"application/json", "text/html", "application/xhtml+xml", "text/plain", "text/csv"}


class SourceError(ValueError):
    """Invalid configuration or corrupt replay input, rather than a market result."""


@dataclass(frozen=True)
class SourceSpec:
    id: str
    url: str
    canonical_url: str
    type: str
    publisher: str
    title: str
    published_at: str | None = None
    observed_at: str | None = None
    valid_as_of: str | None = None
    jurisdiction: str = "unknown"
    topics: tuple[str, ...] = ()
    asset_ids: tuple[str, ...] = ()
    content_type: str = "text/html"
    access_method: str = "public_http"
    policy_url: str = ""
    policy_note: str = ""
    retention: str = "excerpt"
    max_age_days: int = 30
    origin_source_id: str | None = None
    excerpts: tuple[dict, ...] = ()
    full_retention_permission: str | None = None


@dataclass(frozen=True)
class FetchResponse:
    body: bytes
    content_type: str
    status: int = 200
    final_url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Snapshot:
    source_id: str
    snapshot_id: str
    status: str
    source: dict
    retrieved_at: str
    raw_sha256: str | None
    normalized_sha256: str | None
    payload_sha256: str
    payload: dict
    diagnostics: tuple[str, ...]
    http: dict
    policy: dict

    def to_dict(self) -> dict:
        return {"schema_version": "source-snapshot-v1", **asdict(self)}


Fetcher = Callable[[str, int, int], FetchResponse]


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _text(value: str) -> str:
    return " ".join(value.split())


def _time(value: str | None) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise SourceError("timestamps must be ISO strings or null")
    try:
        if len(value) == 10:
            parsed = datetime.combine(date.fromisoformat(value), datetime.min.time(), timezone.utc)
        else:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise SourceError("timestamp must include an explicit timezone")
        return parsed.astimezone(timezone.utc)
    except ValueError as exc:
        raise SourceError("invalid ISO timestamp") from exc


def _url(value: str) -> urllib.parse.SplitResult:
    if not isinstance(value, str) or any(ord(char) < 33 for char in value):
        raise SourceError("source URL must be a printable HTTPS URL")
    try:
        parts = urllib.parse.urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise SourceError("invalid source URL") from exc
    host = (parts.hostname or "").lower().rstrip(".")
    if parts.scheme != "https" or not host or parts.username or parts.password or parts.fragment:
        raise SourceError("only HTTPS URLs without credentials or fragments are permitted")
    if (
        port not in (None, 443)
        or "." not in host
        or host == "localhost"
        or host.endswith((".localhost", ".local", ".internal", ".test", ".invalid"))
    ):
        raise SourceError("only public HTTPS hosts on the default port are permitted")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise SourceError("IP literals are not permitted source destinations")
    if not re.fullmatch(r"[a-z0-9.-]+", host) or any(
        not label or label.startswith("-") or label.endswith("-") for label in host.split(".")
    ):
        raise SourceError("source hostname is invalid")
    # Numeric legacy IP spellings (e.g. 2130706433 or 127.1) must not bypass
    # the literal-IP restriction. DNS names ending in a numeric label fail too.
    if host.split(".")[-1].isdigit():
        raise SourceError("numeric hostnames are not permitted")
    authentication_keys = {"access_token", "authorization", "api_key", "apikey", "token", "password", "secret"}
    if any(
        key.lower() in authentication_keys for key, _ in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    ):
        raise SourceError("authenticated or secret-bearing URLs are not supported")
    return parts


def _validate(spec: SourceSpec) -> None:
    if not isinstance(spec, SourceSpec) or not isinstance(spec.id, str) or not _ID.fullmatch(spec.id):
        raise SourceError("source ID must be a safe, stable identifier")
    _url(spec.url)
    _url(spec.canonical_url)
    if spec.policy_url:
        _url(spec.policy_url)
    from .semiconductor_data import pdf_allowed
    from .commodity_data import pdf_supported

    commodity_pdf = pdf_supported(spec.url) and spec.type == (
        'institution' if urllib.parse.urlsplit(spec.url).hostname == 'www.ishares.com' else 'primary'
    )
    reviewed_pdf = (
        spec.content_type == 'application/pdf'
        and spec.retention == 'excerpt'
        and ((spec.type == 'primary' and pdf_allowed(spec.url)) or commodity_pdf)
    )
    if (
        not isinstance(spec.type, str)
        or not isinstance(spec.content_type, str)
        or spec.type not in _TYPES
        or (spec.content_type not in _MIME_TYPES and not reviewed_pdf)
    ):
        raise SourceError("unsupported source type or content type")
    if not isinstance(spec.access_method, str) or spec.access_method not in {"public_http", "public_api"}:
        raise SourceError("only explicit public HTTP or documented public API acquisition is supported")
    if (
        not isinstance(spec.publisher, str)
        or not isinstance(spec.title, str)
        or not spec.publisher.strip()
        or not spec.title.strip()
    ):
        raise SourceError("publisher and document title are required")
    if not spec.policy_url or not isinstance(spec.policy_note, str) or not spec.policy_note.strip():
        raise SourceError("reviewed public-access and retention policy provenance is required")
    if not isinstance(spec.retention, str) or spec.retention not in {"full", "excerpt"}:
        raise SourceError("retention must be full or excerpt")
    if spec.retention == "full" and (
        spec.type == "community"
        or not isinstance(spec.full_retention_permission, str)
        or not spec.full_retention_permission.strip()
    ):
        raise SourceError("full retention requires explicit permission and is never used for community content")
    if not isinstance(spec.jurisdiction, str) or not spec.jurisdiction.strip():
        raise SourceError("source jurisdiction must be explicit text or unknown")
    for sequence in (spec.topics, spec.asset_ids):
        if not isinstance(sequence, (list, tuple)) or any(
            not isinstance(value, str) or not value.strip() for value in sequence
        ):
            raise SourceError("source topics and asset IDs must be explicit nonempty strings")
    if isinstance(spec.max_age_days, bool) or not isinstance(spec.max_age_days, int) or spec.max_age_days < 0:
        raise SourceError("max_age_days must be a nonnegative integer")
    for value in (spec.published_at, spec.observed_at, spec.valid_as_of):
        _time(value)
    if spec.origin_source_id is not None and (
        not isinstance(spec.origin_source_id, str)
        or not _ID.fullmatch(spec.origin_source_id)
        or spec.origin_source_id == spec.id
    ):
        raise SourceError("origin_source_id must reference another safe source ID")
    if not isinstance(spec.excerpts, (list, tuple)) or not spec.excerpts or len(spec.excerpts) > 3:
        raise SourceError("one to three explicit excerpt selectors are required")
    ids = set()
    for excerpt in spec.excerpts:
        if not isinstance(excerpt, dict) or set(excerpt) != {"id", "quote", "locator", "definition"}:
            raise SourceError("excerpt requires exactly id, quote, locator and definition")
        if not isinstance(excerpt["id"], str) or not _ID.fullmatch(excerpt["id"]) or excerpt["id"] in ids:
            raise SourceError("excerpt IDs must be valid and unique")
        ids.add(excerpt["id"])
        if not all(isinstance(excerpt[key], str) for key in ("quote", "locator")) or not isinstance(
            excerpt["definition"], (str, dict)
        ):
            raise SourceError("excerpt quote/location must be strings and definition must be text or a JSON object")
        if (
            not excerpt["locator"].strip()
            or not excerpt["definition"]
            or (isinstance(excerpt["definition"], str) and not excerpt["definition"].strip())
        ):
            raise SourceError("excerpt location and financial/semantic definition are required")
        if not _text(excerpt["quote"]) or len(_text(excerpt["quote"])) > 1200:
            raise SourceError("excerpt quote must contain at most 1200 normalized characters")
        if spec.type == "community" and _text(excerpt["quote"]).lower() in {
            "[deleted]",
            "[removed]",
            "deleted",
            "removed",
        }:
            raise SourceError("deleted/removed community placeholders are not excerpt selectors")
        if spec.type == "community" and re.search(
            r"(?:^|/)(?:author|username|user|user_id|author_fullname|name|id)(?:/|$)", excerpt["locator"], flags=re.I
        ):
            raise SourceError("community personal identifiers are not retained")
    try:
        if len(_json_bytes(asdict(spec))) > 64 * 1024:
            raise SourceError("source specification exceeds the metadata size limit")
    except (TypeError, ValueError) as exc:
        raise SourceError("source metadata must contain finite JSON-compatible values") from exc


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _fetch_http(url: str, timeout: int, max_bytes: int) -> FetchResponse:
    """Use inherited proxy and CA configuration; never inject authentication."""
    parts = _url(url)
    # Reject local destinations resolved through ordinary DNS. The session's
    # inherited HTTP proxy remains in use, so no direct connection is attempted.
    for address in socket.getaddrinfo(parts.hostname, 443, type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(address[4][0]).is_global:
            raise SourceError("source hostname resolves to a non-public address")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/html, text/plain, text/csv",
            "Accept-Encoding": "identity",
        },
        method="GET",
    )
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        response = opener.open(request, timeout=min(timeout, TIMEOUT_SECONDS))
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise SourceError("response exceeds the acquisition size limit")
        if response.headers.get("Content-Encoding", "identity").lower() != "identity":
            raise SourceError("compressed HTTP responses are not supported by this bounded collector")
        headers = {
            key.lower(): response.headers[key]
            for key in ("Content-Type", "ETag", "Last-Modified")
            if key in response.headers
        }
        return FetchResponse(
            body, response.headers.get("Content-Type", ""), response.status, response.geturl(), headers
        )


def _response(fetcher: Fetcher, url: str, limit: int) -> FetchResponse:
    result = fetcher(url, TIMEOUT_SECONDS, limit)
    if not isinstance(result, FetchResponse) or not isinstance(result.body, bytes):
        raise SourceError("fetcher must return FetchResponse with a bytes body")
    if (
        not isinstance(result.content_type, str)
        or not isinstance(result.headers, dict)
        or any(not isinstance(key, str) or not isinstance(value, str) for key, value in result.headers.items())
    ):
        raise SourceError("HTTP content type and retained headers must be strings")
    if len(result.body) > limit:
        raise SourceError("response exceeds the acquisition size limit")
    if result.final_url is not None and result.final_url != url:
        raise SourceError("redirects are refused; review and explicitly configure the final URL")
    if not isinstance(result.status, int) or isinstance(result.status, bool):
        raise SourceError("HTTP status must be an integer")
    return result


def _access_policy(url, access_method, perform, retrieved_at, policy):
    """Shared access boundary for planned sources and discovery documents."""
    if access_method == "public_api":
        policy["robots"] = "documented_public_api"
        return
    if access_method != "public_http":
        raise SourceError("unsupported public access method")
    parts = _url(url)
    robots_url = urllib.parse.urlunsplit(("https", parts.netloc, "/robots.txt", "", ""))
    robots = _response(perform, robots_url, MAX_ROBOTS_BYTES)
    policy.update(
        robots_url=robots_url, robots_status=robots.status, robots_sha256=_sha(robots.body), checked_at=retrieved_at
    )
    if robots.status == 404:
        policy["robots"] = "absent"
    elif robots.status == 200 and robots.content_type.split(";", 1)[0].strip().lower() in {
        "text/plain",
        "text/robots",
        "",
    }:
        parser = urllib.robotparser.RobotFileParser(robots_url)
        parser.parse(_decode(robots.body, robots.content_type).splitlines())
        if not parser.can_fetch(USER_AGENT, url):
            raise SourceError("robots policy disallows this source")
        policy["robots"] = "allowed"
    else:
        raise SourceError("robots policy could not be reliably established")


@dataclass(frozen=True)
class PublicDocument:
    """Opened bytes are research data, not evidence or executable instructions."""

    status: str
    response: FetchResponse | None
    retrieved_at: str
    policy: dict
    diagnostics: tuple[str, ...]


def read_public(url, *, access_method, policy_url, policy_note, fetcher=None, now=None):
    """Read a bounded discovery index/candidate through the existing collector.

    No passage is promoted here. The caller must apply an explicit data contract
    and create a SourceSpec for acquire/replay. No redirects or access bypass.
    """
    _url(url)
    _url(policy_url)
    if not isinstance(policy_note, str) or not policy_note.strip():
        raise SourceError("reviewed discovery access/retention policy is required")
    instant = now or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise SourceError("aware discovery clock required")
    retrieved = instant.astimezone(timezone.utc).isoformat()
    policy = dict(url=policy_url, review_note=policy_note, access_method=access_method, robots="not_checked")
    perform = fetcher or _fetch_http
    response = None
    stage = "policy"
    status = "available"
    diagnostics = []
    try:
        _access_policy(url, access_method, perform, retrieved, policy)
        stage = "fetch"
        response = _response(perform, url, MAX_BYTES)
        if response.status != 200:
            raise SourceError(f"source returned HTTP {response.status}")
    except (TimeoutError, socket.timeout):
        status = "timeout"
        diagnostics.append(stage + ": request timed out")
    except urllib.error.URLError as exc:
        status = (
            "timeout"
            if isinstance(exc.reason, (TimeoutError, socket.timeout))
            else ("policy_blocked" if stage == "policy" else "unavailable")
        )
        diagnostics.append(stage + ": request failed (" + type(exc.reason).__name__ + ")")
    except (SourceError, OSError, ValueError) as exc:
        status = "policy_blocked" if stage == "policy" else "unavailable"
        diagnostics.append(stage + ": " + str(exc))
    if now is None:
        retrieved = datetime.now(timezone.utc).isoformat()
    return PublicDocument(status, response, retrieved, policy, tuple(diagnostics))


def _decode(body: bytes, content_type: str) -> str:
    match = re.search(r"charset\s*=\s*[\"']?([a-zA-Z0-9_-]+)", content_type, flags=re.I)
    charset = match.group(1) if match else "utf-8"
    try:
        return body.decode(charset, errors="strict")
    except (LookupError, UnicodeDecodeError) as exc:
        raise SourceError("source text cannot be decoded with its declared charset") from exc


class _VisibleText(HTMLParser):
    _HIDDEN = {"script", "style", "head", "template", "noscript"}
    _VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        hidden = tag in self._HIDDEN or "hidden" in attributes or attributes.get("aria-hidden") == "true"
        if self.stack and self.stack[-1][1]:
            hidden = True
        if tag not in self._VOID:
            self.stack.append((tag, hidden))
        if not hidden:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        if not self.stack or not self.stack[-1][1]:
            self.parts.append(" ")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self._VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if not self.stack or not self.stack[-1][1]:
            self.parts.append(data)


def _visible_html(value: str) -> str:
    parser = _VisibleText()
    parser.feed(value)
    parser.close()
    return _text("".join(parser.parts))


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SourceError("duplicate JSON keys are ambiguous")
        result[key] = value
    return result


def _parse_json(text: str):
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda _: (_ for _ in ()).throw(SourceError("nonfinite JSON number")),
        )
    except (ValueError, RecursionError) as exc:
        raise SourceError("source JSON is invalid or ambiguous") from exc


def _normalize(body: bytes, mime: str, declared: str, url: str = '') -> tuple[str, object | None]:
    actual = mime.split(";", 1)[0].strip().lower()
    expected = declared.split(";", 1)[0]
    compatible = (
        actual == expected
        or {actual, expected} <= {"text/html", "application/xhtml+xml"}
        or {actual, expected} <= {"text/plain", "text/csv"}
    )
    if not compatible:
        raise SourceError("returned content type does not match the reviewed source specification")
    from .semiconductor_data import source_document as semiconductor_document, pdf_text

    if expected == 'application/pdf':
        from .commodity_data import pdf_supported, pdf_text as commodity_pdf_text

        if pdf_supported(url):
            return _text(commodity_pdf_text(body)), None
        document = semiconductor_document(body, actual, url)
        return _text(pdf_text(body)), document
    decoded = _decode(body, mime)
    if expected == "application/json":
        value = _parse_json(decoded)
        return _json_bytes(value).decode("utf-8"), value
    if expected in {"text/html", "application/xhtml+xml"}:
        from .korean_data import source_document

        document = source_document(url, decoded)
        if document is None:
            document = semiconductor_document(body, actual, url)
        normalized = _visible_html(decoded)
        # A reviewed issuer-linked financial page may expose its data solely
        # as a JSON literal. Preserve that decoded data, never execute scripts.
        if not normalized and document is not None:
            normalized = _json_bytes(document).decode('utf-8')
        return normalized, document
    return _text(decoded), None


def _pointer(value: object, pointer: str, *, community: bool = False, html: bool = False) -> str:
    current = value
    try:
        for raw in pointer.split("/")[1:]:
            if (
                community
                and isinstance(current, dict)
                and (current.get("dead") is True or current.get("deleted") is True or current.get("removed") is True)
            ):
                raise SourceError("dead, deleted or removed community items are not retained")
            if re.search(r"~(?![01])", raw):
                raise SourceError("invalid JSON pointer escape")
            key = raw.replace("~1", "/").replace("~0", "~")
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and re.fullmatch(r"0|[1-9][0-9]*", key):
                current = current[int(key)]
            else:
                raise SourceError("JSON pointer cannot be resolved")
    except (KeyError, IndexError, ValueError) as exc:
        raise SourceError("JSON pointer cannot be resolved") from exc
    if not isinstance(current, str):
        raise SourceError("JSON excerpt pointer must select a string, not a whole object or array")
    if _text(current).lower() in {"[deleted]", "[removed]", "deleted", "removed"}:
        raise SourceError("deleted or removed community text is not retained")
    return _visible_html(current) if html or re.search(r"<[A-Za-z][^>]*>", current) else _text(current)


def _scalar_pointer(value, pointer):
    """Explicit non-community JSON scalar selector, never a whole object."""
    current = value
    try:
        for raw in pointer.split("/")[1:]:
            if re.search(r"~(?![01])", raw):
                raise SourceError("invalid JSON scalar pointer")
            key = raw.replace("~1", "/").replace("~0", "~")
            current = (
                current[int(key)] if isinstance(current, list) and re.fullmatch(r"0|[1-9][0-9]*", key) else current[key]
            )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise SourceError("JSON scalar pointer cannot be resolved") from exc
    if isinstance(current, bool) or not isinstance(current, (int, float, str)):
        raise SourceError("JSON scalar pointer must select a finite number or decimal string")
    from decimal import Decimal, InvalidOperation

    try:
        number = Decimal(str(current))
        if not number.is_finite() or len(str(current)) > 64 or abs(number.as_tuple().exponent) > 100:
            raise InvalidOperation()
    except InvalidOperation as exc:
        raise SourceError("JSON scalar is not a bounded finite decimal") from exc
    return str(current)


def _extract(spec: SourceSpec, normalized: str, document: object | None) -> list[dict]:
    excerpts = []
    for requested in spec.excerpts:
        quote = _text(requested["quote"])
        locator = requested["locator"]
        if document is not None and locator.startswith('samsung_scalar:') and spec.type == 'primary':
            haystack = _scalar_pointer(document, '/metrics/' + locator.removeprefix('samsung_scalar:'))
        elif document is not None and locator.startswith("json_scalar:") and spec.type != "community":
            haystack = _scalar_pointer(document, locator[len("json_scalar:") :])
        elif document is not None and locator.startswith("json_html:") and spec.type == "community":
            haystack = _pointer(document, locator[len("json_html:") :], community=True, html=True)
        elif document is not None and locator.startswith('json_text:') and spec.type != 'community':
            haystack = _text(_pointer(document, locator[len('json_text:') :]))
        elif document is not None and locator.startswith("/"):
            haystack = _pointer(document, locator, community=spec.type == "community")
        else:
            if spec.type == "community" and document is not None:
                raise SourceError(
                    "community JSON requires an explicit body/text JSON pointer, not a whole-document search"
                )
            haystack = normalized
        if quote not in haystack:
            excerpts.append(
                {
                    "id": requested["id"],
                    "quote": "",
                    "locator": locator,
                    "definition": requested["definition"],
                    "match_status": "missing",
                }
            )
        else:
            excerpts.append(
                {
                    "id": requested["id"],
                    "quote": quote,
                    "locator": locator,
                    "definition": requested["definition"],
                    "match_status": "matched",
                }
            )
    return excerpts


def _path(store: str | Path, source_id: str, snapshot_id: str) -> Path:
    if (
        not isinstance(source_id, str)
        or not _ID.fullmatch(source_id)
        or not isinstance(snapshot_id, str)
        or not _HASH.fullmatch(snapshot_id)
    ):
        raise SourceError("invalid snapshot reference")
    root = Path(store).resolve()
    path = root / source_id / f"{snapshot_id}.json"
    if not path.resolve().is_relative_to(root):
        raise SourceError("snapshot path must remain inside its store")
    return path


def _snapshot(
    spec: SourceSpec,
    store: str | Path,
    *,
    status: str,
    retrieved_at: str,
    raw_hash: str | None,
    normalized_hash: str | None,
    payload: dict,
    diagnostics: list[str],
    http: dict,
    policy: dict,
) -> Snapshot:
    source = json.loads(_json_bytes(asdict(spec)))
    # Quote selectors are configuration, not retrieved evidence. They belong
    # in metadata for replay auditing even if no match was found.
    envelope = {
        "schema_version": "source-snapshot-v1",
        "source_id": spec.id,
        "status": status,
        "source": source,
        "retrieved_at": retrieved_at,
        "raw_sha256": raw_hash,
        "normalized_sha256": normalized_hash,
        "payload_sha256": _sha(_json_bytes(payload)),
        "payload": payload,
        "diagnostics": diagnostics,
        "http": http,
        "policy": policy,
    }
    snapshot_id = _sha(_json_bytes(envelope))
    record = {**envelope, "snapshot_id": snapshot_id}
    path = _path(store, spec.id, snapshot_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = _json_bytes(record) + b"\n"
    if path.exists():
        if path.read_bytes() != encoded:
            raise SourceError("existing snapshot differs; immutable source snapshots are never overwritten")
    else:
        with path.open("xb") as handle:
            handle.write(encoded)
    return Snapshot(
        spec.id,
        snapshot_id,
        status,
        source,
        retrieved_at,
        raw_hash,
        normalized_hash,
        envelope["payload_sha256"],
        payload,
        tuple(diagnostics),
        http,
        policy,
    )


def acquire(
    spec: SourceSpec, store: str | Path, *, fetcher: Fetcher | None = None, now: datetime | None = None
) -> Snapshot:
    """Acquire exactly one reviewed source; failures become pinned diagnostics.

    Inject ``fetcher(url, timeout, max_bytes) -> FetchResponse`` for deterministic
    tests. It receives robots.txt requests too. No crawl, login, cookie jar,
    redirects, automatic fallback provider or model call is performed.
    """
    _validate(spec)
    instant = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(instant, datetime) or instant.tzinfo is None:
        raise SourceError("acquisition time must be timezone-aware")
    instant = instant.astimezone(timezone.utc)
    retrieved_at = instant.isoformat().replace("+00:00", "Z")
    perform = fetcher if fetcher is not None else _fetch_http
    status = "unavailable"
    diagnostics: list[str] = []
    http: dict = {}
    policy = {
        "url": spec.policy_url,
        "review_note": spec.policy_note,
        "access_method": spec.access_method,
        "robots": "not_checked",
    }
    payload: dict = {"retention": spec.retention, "excerpts": []}
    raw_hash = normalized_hash = None
    stage = "policy"
    try:
        _access_policy(spec.url, spec.access_method, perform, retrieved_at, policy)
        stage = "fetch"
        response = _response(perform, spec.url, MAX_BYTES)
        http = {
            "status": response.status,
            "final_url": response.final_url or spec.url,
            "content_type": response.content_type,
            "headers": {
                key.lower(): value
                for key, value in response.headers.items()
                if key.lower() in {"etag", "last-modified", "content-type"}
            },
        }
        if response.status != 200:
            raise SourceError(f"source returned HTTP {response.status}")
        raw_hash = _sha(response.body)
        stage = "parse"
        normalized, document = _normalize(response.body, response.content_type, spec.content_type, spec.url)
        if not normalized:
            raise SourceError("source has no usable text")
        normalized_hash = _sha(normalized.encode("utf-8"))
        if spec.retention == "full":
            payload["raw_base64"] = base64.b64encode(response.body).decode("ascii")
            payload["normalized_text"] = normalized
        stage = "excerpt"
        payload["excerpts"] = _extract(spec, normalized, document)
        missing = [excerpt["id"] for excerpt in payload["excerpts"] if excerpt["match_status"] != "matched"]
        if missing:
            raise SourceError(
                f"selected excerpts are absent; source changed or selectors are wrong: {', '.join(missing)}"
            )
        if spec.retention == "excerpt":
            diagnostics.append(
                "Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document."
            )
        if document is None:
            diagnostics.append(
                "Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities."
            )
        status = "available"
    except (TimeoutError, socket.timeout) as exc:
        status = "timeout"
        diagnostics.append(f"{stage}: request timed out")
    except urllib.error.URLError as exc:
        status = (
            "timeout"
            if isinstance(exc.reason, (TimeoutError, socket.timeout))
            else ("policy_blocked" if stage == "policy" else "unavailable")
        )
        diagnostics.append(f"{stage}: request failed ({type(exc.reason).__name__})")
    except (SourceError, OSError, ValueError, RecursionError) as exc:
        status = {"policy": "policy_blocked", "fetch": "unavailable", "parse": "parse_error", "excerpt": "changed"}[
            stage
        ]
        diagnostics.append(f"{stage}: {exc}")
    if now is None:
        # Real availability cannot precede the completed fetch/parse. A supplied
        # test clock denotes that completed instant and stays deterministic.
        retrieved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return _snapshot(
        spec,
        store,
        status=status,
        retrieved_at=retrieved_at,
        raw_hash=raw_hash,
        normalized_hash=normalized_hash,
        payload=payload,
        diagnostics=diagnostics,
        http=http,
        policy=policy,
    )


def load_snapshot(store: str | Path, source_id: str, snapshot_id: str) -> Snapshot:
    """Replay an explicitly pinned snapshot, without any network activity.

    All retained payload bytes and envelope metadata are hash-checked. When
    copyright/privacy policy retained only excerpts, discarded original bytes
    cannot be rehashed; their recorded acquisition digest is provenance only.
    """
    path = _path(store, source_id, snapshot_id)
    try:
        if path.stat().st_size > MAX_BYTES * 5:
            raise SourceError("snapshot exceeds the replay size limit")
        record = _parse_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise SourceError("snapshot is unavailable or unreadable") from exc
    required = {
        "schema_version",
        "source_id",
        "snapshot_id",
        "status",
        "source",
        "retrieved_at",
        "raw_sha256",
        "normalized_sha256",
        "payload_sha256",
        "payload",
        "diagnostics",
        "http",
        "policy",
    }
    if not isinstance(record, dict) or set(record) != required or record["schema_version"] != "source-snapshot-v1":
        raise SourceError("snapshot contract is invalid")
    if record["source_id"] != source_id or record["snapshot_id"] != snapshot_id:
        raise SourceError("snapshot identity does not match its pinned reference")
    envelope = {key: value for key, value in record.items() if key != "snapshot_id"}
    if _sha(_json_bytes(envelope)) != snapshot_id or _sha(_json_bytes(record["payload"])) != record["payload_sha256"]:
        raise SourceError("snapshot metadata or retained payload checksum mismatch")
    for key in ("raw_sha256", "normalized_sha256", "payload_sha256"):
        if record[key] is not None and (not isinstance(record[key], str) or not _HASH.fullmatch(record[key])):
            raise SourceError("snapshot contains an invalid content checksum")
    source = record["source"]
    try:
        spec = SourceSpec(**source)
        _validate(spec)
    except (TypeError, AttributeError) as exc:
        raise SourceError("snapshot source metadata is invalid") from exc
    if spec.id != source_id:
        raise SourceError("snapshot source metadata has a mismatched identity")
    _time(record["retrieved_at"])
    payload = record["payload"]
    if payload.get("retention") != spec.retention:
        raise SourceError("snapshot retention and source policy disagree")
    if spec.retention == "full" and "raw_base64" in payload:
        try:
            raw = base64.b64decode(payload["raw_base64"], validate=True)
            normalized = payload["normalized_text"]
        except (KeyError, ValueError) as exc:
            raise SourceError("full snapshot content is missing or malformed") from exc
        if (
            _sha(raw) != record["raw_sha256"]
            or not isinstance(normalized, str)
            or _sha(normalized.encode("utf-8")) != record["normalized_sha256"]
        ):
            raise SourceError("full snapshot content checksum mismatch")
        recalculated, document = _normalize(raw, record["http"]["content_type"], spec.content_type, spec.url)
        if recalculated != normalized:
            raise SourceError("full snapshot excerpts or normalization disagree with raw content")
        if payload["excerpts"]:
            if _extract(spec, normalized, document) != payload["excerpts"]:
                raise SourceError("full snapshot selected excerpts disagree with raw content")
    elif spec.retention == "excerpt":
        if set(payload) != {"retention", "excerpts"}:
            raise SourceError("excerpt-only snapshots must not contain whole source content")
    if record["status"] == "available":
        retained = payload.get("excerpts")
        if not isinstance(retained, list) or len(retained) != len(spec.excerpts):
            raise SourceError("available snapshot is missing selected excerpts")
        for requested, excerpt in zip(spec.excerpts, retained):
            expected = {
                "id": requested["id"],
                "quote": _text(requested["quote"]),
                "locator": requested["locator"],
                "definition": requested["definition"],
                "match_status": "matched",
            }
            if excerpt != expected:
                raise SourceError("retained excerpt does not match the pinned selector")
        if record["raw_sha256"] is None or record["normalized_sha256"] is None:
            raise SourceError("available snapshot has no acquisition content hashes")
    return Snapshot(
        source_id,
        snapshot_id,
        record["status"],
        source,
        record["retrieved_at"],
        record["raw_sha256"],
        record["normalized_sha256"],
        record["payload_sha256"],
        payload,
        tuple(record["diagnostics"]),
        record["http"],
        record["policy"],
    )


def freshness(snapshot: Snapshot, as_of: str | datetime) -> dict:
    """Assess age without replacing unknown publication with retrieval time."""
    at = _time(as_of) if isinstance(as_of, str) else as_of
    if not isinstance(at, datetime) or at.tzinfo is None:
        raise SourceError("freshness comparison requires a timezone-aware as_of")
    at = at.astimezone(timezone.utc)
    dates = {key: _time(snapshot.source.get(key)) for key in ("published_at", "observed_at", "valid_as_of")}
    available = [value for value in dates.values() if value is not None]
    if any(value > at for value in available):
        return {
            "status": "future",
            "basis": None,
            "age_days": None,
            "reason": "source date is later than the research cutoff",
        }
    basis = next((key for key in ("valid_as_of", "observed_at", "published_at") if dates[key] is not None), None)
    if basis is None:
        return {
            "status": "unknown",
            "basis": None,
            "age_days": None,
            "reason": "publication, observation and valid-as-of dates are unknown; retrieval is not publication",
        }
    age_days = (at - dates[basis]).total_seconds() / 86400
    stale = age_days > snapshot.source["max_age_days"]
    return {
        "status": "stale" if stale else "fresh",
        "basis": basis,
        "age_days": age_days,
        "reason": f"age assessed against source-specific {snapshot.source['max_age_days']}-day limit; not a truth score",
    }
