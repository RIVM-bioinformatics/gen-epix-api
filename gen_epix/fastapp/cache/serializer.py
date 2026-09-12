"""Conversion of payloads to and from their stored representation.

A serializer decides both the wire format of a cached value and its copy
semantics. `IdentitySerializer` stores live objects and is the fastest choice
for a process-local cache, `DeepCopySerializer` protects callers from mutating
cached state, and the byte-oriented serializers prepare values for a shared
store. `CompressingSerializer`, `SigningSerializer` and `EncryptingSerializer`
wrap any byte-oriented serializer to add size, integrity and confidentiality
handling.
"""

import copy
import hmac
import json
import pickle
import zlib
from abc import ABC, abstractmethod
from typing import Any

from gen_epix.fastapp.cache.exc import CantDeserializeError, SerializationError

_UNCOMPRESSED = b"\x00"
_COMPRESSED = b"\x01"
_DIGEST_SIZE = 32


class Serializer(ABC):
    """Encapsulates converting payloads between their live and stored representations.

    Implementations must be symmetric: `loads` applied to the output of `dumps`
    returns an equal value. A subclass raises `CantDeserializeError` rather than
    a generic error when a stored value belongs to an incompatible release, so
    that a region can treat it as a miss and regenerate it.
    """

    @abstractmethod
    def dumps(self, value: Any) -> Any:
        """Return the stored representation of `value`.

        Args:
            value: The payload handed to the cache.

        Raises:
            SerializationError: If the payload cannot be represented.
        """

    @abstractmethod
    def loads(self, stored: Any) -> Any:
        """Return the payload represented by `stored`.

        Args:
            stored: A value previously produced by `dumps`.

        Raises:
            CantDeserializeError: If the stored value cannot be read by this
                implementation and should be regenerated.
        """


class IdentitySerializer(Serializer):
    """Encapsulates storing live object references without conversion.

    This is the cheapest option for an in-process region, but callers share the
    cached object: mutating a returned value corrupts the cache. Use
    `DeepCopySerializer` when callers cannot be trusted to treat results as
    immutable.
    """

    def dumps(self, value: Any) -> Any:
        """See base method."""
        return value

    def loads(self, stored: Any) -> Any:
        """See base method."""
        return stored


class DeepCopySerializer(Serializer):
    """Encapsulates storing and return independent deep copies of every payload.

    Copying on both write and read gives an in-process region the same isolation
    that a serializing remote store provides, at the cost of the copy.
    """

    def dumps(self, value: Any) -> Any:
        """Return an independent deep copy of `value`.

        Args:
            value: The payload handed to the cache.

        Returns:
            A copy that later mutations of `value` cannot reach.

        Raises:
            SerializationError: If the payload cannot be deep copied.
        """
        try:
            return copy.deepcopy(value)
        except Exception as exception:
            raise SerializationError(f"Cannot deep copy payload: {exception}") from (
                exception
            )

    def loads(self, stored: Any) -> Any:
        """Return an independent deep copy of the stored payload.

        Args:
            stored: A copy previously produced by `dumps`.

        Returns:
            A copy the caller may mutate freely.

        Raises:
            CantDeserializeError: If the stored payload cannot be deep copied.
        """
        try:
            return copy.deepcopy(stored)
        except Exception as exception:
            raise CantDeserializeError(str(exception)) from exception


class PickleSerializer(Serializer):
    """Encapsulates storing payloads as pickled bytes.

    Pickle accepts arbitrary Python objects but grants code execution to anyone
    who can write to the store. Wrap it in `SigningSerializer` whenever the
    store is shared or reachable beyond the application process.

    Attributes:
        protocol: The pickle protocol used when writing.
    """

    def __init__(self, protocol: int = pickle.HIGHEST_PROTOCOL):
        """Initialize a PickleSerializer instance."""
        self.protocol = protocol

    def dumps(self, value: Any) -> bytes:
        """Return `value` as pickled bytes.

        Args:
            value: The payload handed to the cache.

        Returns:
            The pickled representation.

        Raises:
            SerializationError: If the payload is not picklable.
        """
        try:
            return pickle.dumps(value, protocol=self.protocol)
        except Exception as exception:
            raise SerializationError(f"Cannot pickle payload: {exception}") from (
                exception
            )

    def loads(self, stored: Any) -> Any:
        """Return the payload unpickled from `stored`.

        Args:
            stored: Bytes previously produced by `dumps`.

        Returns:
            The reconstructed payload.

        Raises:
            CantDeserializeError: If the bytes were written by an incompatible
                release or are otherwise unreadable.
        """
        try:
            return pickle.loads(stored)
        except Exception as exception:
            raise CantDeserializeError(str(exception)) from exception


class JsonSerializer(Serializer):
    """Encapsulates storing payloads as UTF-8 encoded JSON.

    JSON is safe to read from an untrusted store and readable in a cache dump,
    but it only accepts JSON-compatible payloads and loses tuple and set types.
    """

    def dumps(self, value: Any) -> bytes:
        """Return `value` as compact UTF-8 encoded JSON.

        Args:
            value: The payload handed to the cache.

        Returns:
            The encoded representation.

        Raises:
            SerializationError: If the payload is not JSON serializable.
        """
        try:
            return json.dumps(value, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError) as exception:
            raise SerializationError(f"Cannot encode payload: {exception}") from (
                exception
            )

    def loads(self, stored: Any) -> Any:
        """Return the payload decoded from JSON bytes.

        Args:
            stored: Bytes previously produced by `dumps`.

        Returns:
            The decoded payload, with tuples and sets rendered as lists.

        Raises:
            CantDeserializeError: If the bytes are not valid JSON.
        """
        try:
            return json.loads(bytes(stored).decode("utf-8"))
        except (TypeError, ValueError, UnicodeDecodeError) as exception:
            raise CantDeserializeError(str(exception)) from exception


class CompressingSerializer(Serializer):
    """Encapsulates compressing large payloads produced by a byte-oriented serializer.

    A single leading flag byte records whether the body was compressed, so short
    values pay no compression cost and both forms remain readable.

    Attributes:
        inner: The serializer producing the uncompressed bytes.
        threshold: Minimum body size in bytes before compression is attempted.
        level: zlib compression level.
    """

    def __init__(
        self,
        inner: Serializer,
        threshold: int = 1024,
        level: int = 6,
    ):
        """Initialize a CompressingSerializer instance."""
        self.inner = inner
        self.threshold = threshold
        self.level = level

    def dumps(self, value: Any) -> bytes:
        """See base method.

        Raises:
            SerializationError: If the wrapped serializer does not produce
                bytes.
        """
        body = _as_bytes(self.inner.dumps(value))
        if len(body) < self.threshold:
            return _UNCOMPRESSED + body
        return _COMPRESSED + zlib.compress(body, self.level)

    def loads(self, stored: Any) -> Any:
        """Return the payload of a possibly compressed body.

        Args:
            stored: Bytes previously produced by `dumps`.

        Returns:
            The payload produced by the wrapped serializer.

        Raises:
            CantDeserializeError: If the flag byte is missing or unknown, or if
                the compressed body is corrupt.
        """
        data = bytes(stored)
        if not data:
            raise CantDeserializeError("Empty compressed payload")
        flag, body = data[:1], data[1:]
        if flag == _UNCOMPRESSED:
            return self.inner.loads(body)
        if flag != _COMPRESSED:
            raise CantDeserializeError("Unknown compression flag")
        try:
            return self.inner.loads(zlib.decompress(body))
        except zlib.error as exception:
            raise CantDeserializeError(str(exception)) from exception


class SigningSerializer(Serializer):
    """Encapsulates prepending a keyed digest so that tampered entries are rejected.

    Signing does not hide the payload; it guarantees that only holders of the
    secret can have written it. This is the minimum safeguard for a pickled
    payload in a shared store, because an attacker able to write to the store
    would otherwise achieve code execution on read.

    Attributes:
        inner: The serializer producing the signed bytes.
    """

    def __init__(self, inner: Serializer, secret: bytes):
        """Initialize a SigningSerializer instance.

        Args:
            inner: The serializer producing the bytes to sign.
            secret: Key material for the digest. It must not be empty.

        Raises:
            SerializationError: If `secret` is empty.
        """
        if not secret:
            raise SerializationError("A signing secret must not be empty")
        self.inner = inner
        self._secret = secret

    def dumps(self, value: Any) -> bytes:
        """See base method."""
        body = _as_bytes(self.inner.dumps(value))
        return self._digest(body) + body

    def loads(self, stored: Any) -> Any:
        """Return the payload of a signed body after verifying its digest.

        Args:
            stored: Bytes previously produced by `dumps`.

        Returns:
            The payload produced by the wrapped serializer.

        Raises:
            CantDeserializeError: If the entry is truncated or its digest does
                not match, which indicates tampering or a rotated secret.
        """
        data = bytes(stored)
        if len(data) <= _DIGEST_SIZE:
            raise CantDeserializeError("Signed payload is truncated")
        digest, body = data[:_DIGEST_SIZE], data[_DIGEST_SIZE:]
        if not hmac.compare_digest(digest, self._digest(body)):
            raise CantDeserializeError("Signed payload failed integrity check")
        return self.inner.loads(body)

    def _digest(self, body: bytes) -> bytes:
        """Return the keyed digest of a serialized body."""
        return hmac.digest(self._secret, body, "sha256")


class EncryptingSerializer(Serializer):
    """Encapsulates encrypting payloads before they reach a shared store.

    Use this for regions holding personal or otherwise sensitive data, where
    operators of the cache store must not be able to read cached values.

    Attributes:
        inner: The serializer producing the plaintext bytes.
    """

    def __init__(self, inner: Serializer, cipher: Any):
        """Initialize an EncryptingSerializer instance.

        Args:
            inner: The serializer producing the plaintext bytes.
            cipher: An object exposing `encrypt` and `decrypt` methods over
                bytes, such as `cryptography.fernet.Fernet`.

        Raises:
            SerializationError: If `cipher` lacks the required methods.
        """
        if not (hasattr(cipher, "encrypt") and hasattr(cipher, "decrypt")):
            raise SerializationError("A cipher must provide encrypt and decrypt")
        self.inner = inner
        self._cipher = cipher

    def dumps(self, value: Any) -> bytes:
        """Return the encrypted form of `value`.

        Args:
            value: The payload handed to the cache.

        Returns:
            The ciphertext produced by the configured cipher.

        Raises:
            SerializationError: If encryption fails.
        """
        body = _as_bytes(self.inner.dumps(value))
        try:
            return bytes(self._cipher.encrypt(body))
        except Exception as exception:
            raise SerializationError(f"Cannot encrypt payload: {exception}") from (
                exception
            )

    def loads(self, stored: Any) -> Any:
        """Return the payload of an encrypted body.

        Args:
            stored: Ciphertext previously produced by `dumps`.

        Returns:
            The payload produced by the wrapped serializer.

        Raises:
            CantDeserializeError: If the entry cannot be decrypted, for example
                after a key rotation.
        """
        try:
            plaintext = self._cipher.decrypt(bytes(stored))
        except Exception as exception:
            raise CantDeserializeError(str(exception)) from exception
        return self.inner.loads(plaintext)


def _as_bytes(value: Any) -> bytes:
    """Return `value` as bytes.

    Args:
        value: The output of a wrapped serializer.

    Returns:
        The value as bytes.

    Raises:
        SerializationError: If the wrapped serializer did not produce bytes,
            which means it cannot be combined with a byte-oriented wrapper.
    """
    if isinstance(value, bytes):
        return value
    if isinstance(value, (bytearray, memoryview)):
        return bytes(value)
    raise SerializationError(
        "This serializer must wrap one that produces bytes, "
        f"but it received {type(value).__name__}"
    )
