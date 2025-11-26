from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class RepositoryProtocol(ABC, Generic[T]):
    """Base repository contract."""

    @abstractmethod
    async def add(self, obj: T) -> T:
        ...

    @abstractmethod
    async def get(self, **kwargs) -> T | None:
        ...

