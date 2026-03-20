---
name: dev-backend-patterns
description: 后端架构模式、API 设计、数据库优化和服务器端最佳实践，适用于 Python、FastAPI 和异步后端开发
---

# 后端开发模式（Python 版）

后端架构模式和最佳实践，用于构建可扩展的 Python 服务端应用。

## 何时使用

- 设计 REST 或 GraphQL API 端点
- 实现 repository、service 或 controller 层
- 优化数据库查询（N+1、索引、连接池）
- 添加缓存（Redis、内存缓存、HTTP 缓存头）
- 设置后台任务或异步处理
- 构建 API 的错误处理和验证结构
- 构建中间件（认证、日志、限流）

## 技术栈

- **Web 框架**: FastAPI（异步、类型安全、自动生成文档）
- **数据库 ORM**: SQLAlchemy 2.0（支持异步会话）
- **数据验证**: Pydantic（FastAPI 内置）
- **缓存**: Redis（redis-py）
- **认证**: PyJWT
- **日志**: structlog 或标准 logging

## API 设计模式

### RESTful API 结构

```python
# ✅ 基于资源的 URL 设计
# GET    /api/markets                 # 列出资源
# GET    /api/markets/{id}            # 获取单个资源
# POST   /api/markets                 # 创建资源
# PUT    /api/markets/{id}            # 替换资源
# PATCH  /api/markets/{id}            # 更新资源
# DELETE /api/markets/{id}            # 删除资源

# ✅ 使用查询参数进行过滤、排序、分页
# GET /api/markets?status=active&sort=volume&limit=20&offset=0
```

### 项目结构

```
app/
├── __init__.py
├── main.py                 # FastAPI 应用入口
├── api/
│   ├── __init__.py
│   ├── deps.py             # 依赖注入（数据库会话、认证）
│   └── v1/
│       ├── __init__.py
│       └── markets.py      # API 路由
├── core/
│   ├── __init__.py
│   ├── config.py           # 配置管理（Pydantic Settings）
│   ├── exceptions.py       # 自定义异常
│   └── security.py         # 认证与安全工具
├── db/
│   ├── __init__.py
│   ├── base.py             # SQLAlchemy 基类
│   ├── session.py          # 数据库会话管理
│   └── models/
│       ├── __init__.py
│       └── market.py       # 数据模型
├── repositories/
│   ├── __init__.py
│   ├── base.py             # Repository 基类
│   └── market.py           # Market Repository
├── services/
│   ├── __init__.py
│   └── market.py           # Market Service
├── schemas/
│   ├── __init__.py
│   └── market.py           # Pydantic 模型（DTO）
└── middleware/
    ├── __init__.py
    ├── auth.py             # 认证中间件
    └── rate_limit.py       # 限流中间件
```

### Repository 模式

```python
# app/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    @abstractmethod
    async def find_all(self, filters: dict = None) -> List[ModelType]:
        pass

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def create(self, data: CreateSchemaType) -> ModelType:
        pass

    @abstractmethod
    async def update(self, id: str, data: UpdateSchemaType) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass


# app/repositories/market.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.db.models.market import Market
from app.repositories.base import BaseRepository
from app.schemas.market import MarketCreate, MarketUpdate, MarketFilters


class MarketRepository(BaseRepository[Market, MarketCreate, MarketUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Market)
        self.db = db

    async def find_all(self, filters: MarketFilters = None) -> List[Market]:
        query = select(Market)

        if filters:
            if filters.status:
                query = query.where(Market.status == filters.status)
            if filters.limit:
                query = query.limit(filters.limit)
            if filters.offset:
                query = query.offset(filters.offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_by_id(self, id: str) -> Optional[Market]:
        query = select(Market).where(Market.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: MarketCreate) -> Market:
        db_market = Market(**data.model_dump())
        self.db.add(db_market)
        await self.db.commit()
        await self.db.refresh(db_market)
        return db_market

    async def update(self, id: str, data: MarketUpdate) -> Optional[Market]:
        db_market = await self.find_by_id(id)
        if not db_market:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_market, field, value)

        await self.db.commit()
        await self.db.refresh(db_market)
        return db_market

    async def delete(self, id: str) -> bool:
        db_market = await self.find_by_id(id)
        if not db_market:
            return False

        await self.db.delete(db_market)
        await self.db.commit()
        return True

    async def find_by_ids(self, ids: List[str]) -> List[Market]:
        query = select(Market).where(Market.id.in_(ids))
        result = await self.db.execute(query)
        return result.scalars().all()


# 依赖注入函数
async def get_market_repository(
    db: AsyncSession = Depends(get_db_session)
) -> MarketRepository:
    return MarketRepository(db)
```

### Service 层模式

```python
# app/services/market.py
from typing import List
from app.repositories.market import MarketRepository
from app.schemas.market import Market, MarketCreate, MarketSearchResult


class MarketService:
    def __init__(self, market_repo: MarketRepository):
        self.market_repo = market_repo

    async def search_markets(self, query: str, limit: int = 10) -> List[Market]:
        """基于向量相似度搜索市场"""
        # 业务逻辑
        embedding = await generate_embedding(query)
        results = await self._vector_search(embedding, limit)

        # 获取完整数据
        market_ids = [r.id for r in results]
        markets = await self.market_repo.find_by_ids(market_ids)

        # 按相似度排序
        score_map = {r.id: r.score for r in results}
        markets.sort(key=lambda m: score_map.get(m.id, 0), reverse=True)

        return markets

    async def _vector_search(self, embedding: List[float], limit: int) -> List[MarketSearchResult]:
        """向量搜索实现（示例）"""
        # 集成 pgvector 或专门的向量数据库
        pass

    async def create_market_with_validation(self, data: MarketCreate) -> Market:
        """带业务验证的市场创建"""
        # 业务规则验证
        if data.end_date < datetime.now(timezone.utc):
            raise BusinessLogicError("End date must be in the future")

        # 检查重复
        existing = await self.market_repo.find_by_name(data.name)
        if existing:
            raise DuplicateError(f"Market with name '{data.name}' already exists")

        return await self.market_repo.create(data)


# 依赖注入
async def get_market_service(
    repo: MarketRepository = Depends(get_market_repository)
) -> MarketService:
    return MarketService(repo)
```

### API 路由（Controller）

```python
# app/api/v1/markets.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from app.schemas.market import (
    Market, MarketCreate, MarketUpdate, MarketFilters, MarketListResponse
)
from app.services.market import MarketService, get_market_service
from app.api.deps import get_current_user, require_permissions

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=MarketListResponse)
async def list_markets(
    filters: MarketFilters = Depends(),
    service: MarketService = Depends(get_market_service),
    current_user = Depends(get_current_user)
):
    """列出所有市场，支持过滤和分页"""
    markets = await service.find_all(filters)
    total = await service.count(filters)

    return MarketListResponse(
        data=markets,
        meta={"total": total, "limit": filters.limit, "offset": filters.offset}
    )


@router.get("/{market_id}", response_model=Market)
async def get_market(
    market_id: str,
    service: MarketService = Depends(get_market_service),
    current_user = Depends(get_current_user)
):
    """获取单个市场详情"""
    market = await service.find_by_id(market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.post("", response_model=Market, status_code=status.HTTP_201_CREATED)
async def create_market(
    data: MarketCreate,
    service: MarketService = Depends(get_market_service),
    current_user = Depends(require_permissions(["markets:create"]))
):
    """创建新市场"""
    return await service.create_market_with_validation(data)


@router.patch("/{market_id}", response_model=Market)
async def update_market(
    market_id: str,
    data: MarketUpdate,
    service: MarketService = Depends(get_market_service),
    current_user = Depends(require_permissions(["markets:update"]))
):
    """更新市场（部分更新）"""
    market = await service.update(market_id, data)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.delete("/{market_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_market(
    market_id: str,
    service: MarketService = Depends(get_market_service),
    current_user = Depends(require_permissions(["markets:delete"]))
):
    """删除市场"""
    success = await service.delete(market_id)
    if not success:
        raise HTTPException(status_code=404, detail="Market not found")
    return None


@router.get("/search", response_model=List[Market])
async def search_markets(
    q: str = Query(..., min_length=1, description="搜索查询"),
    limit: int = Query(10, ge=1, le=100),
    service: MarketService = Depends(get_market_service)
):
    """语义搜索市场"""
    return await service.search_markets(q, limit)
```

## 数据库模式

### SQLAlchemy 模型定义

```python
# app/db/models/market.py
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import enum


class MarketStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    status: Mapped[MarketStatus] = mapped_column(
        Enum(MarketStatus),
        default=MarketStatus.ACTIVE,
        nullable=False,
        index=True
    )
    volume: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=0)
    creator_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Market(id={self.id}, name={self.name})>"
```

### 查询优化

```python
# ✅ 好：只选择需要的列（使用 defer / load_only）
from sqlalchemy.orm import load_only

query = select(Market).options(
    load_only(Market.id, Market.name, Market.status, Market.volume)
).where(
    Market.status == MarketStatus.ACTIVE
).order_by(
    Market.volume.desc()
).limit(10)

# ✅ 好：使用 joinedload 预加载关联数据
from sqlalchemy.orm import joinedload

query = select(Market).options(
    joinedload(Market.creator),
    joinedload(Market.positions)
).where(Market.id == market_id)

# ❌ 坏：选择所有列（N+1 问题）
# 默认情况下 SQLAlchemy 会延迟加载关联对象
# 在循环中访问关联属性会导致 N+1 查询
```

### N+1 查询问题预防

```python
# ❌ 坏：N+1 查询问题
markets = await market_repo.find_all()
for market in markets:
    # 每次访问 creator 都会触发一次数据库查询
    print(market.creator.name)  # N 次额外查询

# ✅ 好：使用 selectinload 批量预加载
from sqlalchemy.orm import selectinload

query = select(Market).options(
    selectinload(Market.creator)
).where(Market.status == MarketStatus.ACTIVE)

result = await db.execute(query)
markets = result.scalars().all()

for market in markets:
    print(market.creator.name)  # 不会触发额外查询

# ✅ 好：手动批量获取（更灵活的场景）
markets = await market_repo.find_all()
creator_ids = [m.creator_id for m in markets]

# 一次性获取所有创建者
creators_query = select(User).where(User.id.in_(creator_ids))
result = await db.execute(creators_query)
creators = result.scalars().all()
creator_map = {c.id: c for c in creators}

for market in markets:
    market.creator = creator_map.get(market.creator_id)
```

### 事务模式

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境打印 SQL
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # 自动检测断开的连接
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不过期对象
    autocommit=False,
    autoflush=False
)


# 依赖注入函数
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 显式事务管理
async def create_market_with_position(
    db: AsyncSession,
    market_data: MarketCreate,
    position_data: PositionCreate
) -> tuple[Market, Position]:
    """在同一事务中创建市场和持仓"""
    try:
        # 创建市场
        market = Market(**market_data.model_dump())
        db.add(market)
        await db.flush()  # 获取 market.id 而不提交

        # 创建持仓
        position = Position(
            market_id=market.id,
            **position_data.model_dump()
        )
        db.add(position)

        await db.commit()
        await db.refresh(market)
        await db.refresh(position)

        return market, position
    except Exception:
        await db.rollback()
        raise


# 使用上下文管理器
from contextlib import asynccontextmanager

@asynccontextmanager
async def transaction(db: AsyncSession):
    """事务上下文管理器"""
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise


# 使用示例
async def complex_operation(db: AsyncSession):
    async with transaction(db):
        market = await market_repo.create(db, data)
        position = await position_repo.create(db, position_data)
        await user_repo.update_balance(db, user_id, -amount)
        # 如果任何步骤失败，全部回滚
```

## 缓存策略

### Redis 缓存层

```python
# app/core/cache.py
import json
import redis.asyncio as redis
from typing import Optional, Any, TypeVar
from functools import wraps
from app.core.config import settings

T = TypeVar("T")


class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: int = 300  # 默认 5 分钟
    ) -> None:
        await self.client.setex(key, expire, value)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def get_json(self, key: str) -> Optional[dict]:
        data = await self.get(key)
        return json.loads(data) if data else None

    async def set_json(
        self,
        key: str,
        value: Any,
        expire: int = 300
    ) -> None:
        await self.set(key, json.dumps(value), expire)


# 依赖注入
cache = RedisCache()

async def get_cache() -> RedisCache:
    return cache
```

### Cache-Aside 模式

```python
# app/repositories/cached_market.py
from typing import Optional
import json
from app.repositories.market import MarketRepository
from app.core.cache import RedisCache
from app.db.models.market import Market


class CachedMarketRepository(MarketRepository):
    def __init__(self, db, cache: RedisCache):
        super().__init__(db)
        self.cache = cache
        self.cache_ttl = 300  # 5 分钟

    async def find_by_id(self, id: str) -> Optional[Market]:
        cache_key = f"market:{id}"

        # 先检查缓存
        cached = await self.cache.get(cache_key)
        if cached:
            data = json.loads(cached)
            return Market(**data)

        # 缓存未命中 - 从数据库获取
        market = await super().find_by_id(id)

        if market:
            # 写入缓存
            await self.cache.set_json(
                cache_key,
                self._market_to_dict(market),
                self.cache_ttl
            )

        return market

    async def invalidate_cache(self, id: str) -> None:
        await self.cache.delete(f"market:{id}")
        # 清除列表缓存
        await self.cache.delete("markets:list:*")

    def _market_to_dict(self, market: Market) -> dict:
        return {
            "id": market.id,
            "name": market.name,
            "description": market.description,
            "status": market.status.value,
            "volume": str(market.volume),
            "creator_id": market.creator_id,
            "end_date": market.end_date.isoformat(),
            "created_at": market.created_at.isoformat(),
            "updated_at": market.updated_at.isoformat()
        }


# 装饰器模式缓存
def cached(prefix: str, ttl: int = 300):
    """方法结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 生成缓存键
            cache_key = f"{prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # 检查缓存
            cached_value = await self.cache.get_json(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行方法
            result = await func(self, *args, **kwargs)

            # 写入缓存
            if result is not None:
                await self.cache.set_json(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


# 使用示例
class MarketService:
    def __init__(self, repo: MarketRepository, cache: RedisCache):
        self.repo = repo
        self.cache = cache

    @cached(prefix="markets", ttl=600)
    async def get_popular_markets(self, limit: int = 10) -> List[dict]:
        # 复杂查询逻辑
        markets = await self.repo.find_popular(limit)
        return [m.to_dict() for m in markets]
```

## 错误处理模式

### 自定义异常体系

```python
# app/core/exceptions.py
from fastapi import HTTPException, status


class AppException(Exception):
    """基础应用异常"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class BusinessLogicError(AppException):
    """业务逻辑错误（400）"""
    pass


class NotFoundError(AppException):
    """资源不存在（404）"""
    pass


class DuplicateError(AppException):
    """资源重复（409）"""
    pass


class AuthenticationError(AppException):
    """认证失败（401）"""
    pass


class AuthorizationError(AppException):
    """权限不足（403）"""
    pass


# FastAPI 全局异常处理器
# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理应用自定义异常"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, BusinessLogicError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DuplicateError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": exc.message,
            "code": exc.code
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    # 记录详细错误日志
    import traceback
    logger.error(
        f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}",
        extra={"path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )


# 在 Service 中使用
class MarketService:
    async def get_market(self, market_id: str) -> Market:
        market = await self.repo.find_by_id(market_id)
        if not market:
            raise NotFoundError(f"Market with id '{market_id}' not found")
        return market
```

### 指数退避重试

```python
# app/core/retry.py
import asyncio
import random
from functools import wraps
from typing import Callable, TypeVar, Tuple

T = TypeVar("T")


class RetryExhaustedError(Exception):
    """重试次数耗尽"""
    pass


async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[type, ...] = (Exception,)
) -> T:
    """
    带指数退避的重试

    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exponential_base: 指数基数
        jitter: 是否添加随机抖动
        retryable_exceptions: 可重试的异常类型
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as e:
            last_exception = e

            if attempt == max_retries:
                raise RetryExhaustedError(
                    f"Failed after {max_retries} retries"
                ) from e

            # 计算延迟：base * (exponential_base ^ attempt)
            delay = min(
                base_delay * (exponential_base ** attempt),
                max_delay
            )

            if jitter:
                # 添加 ±25% 的随机抖动
                delay *= random.uniform(0.75, 1.25)

            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s..."
            )
            await asyncio.sleep(delay)

    raise last_exception


# 装饰器版本
def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: Tuple[type, ...] = (Exception,)
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                base_delay=base_delay,
                retryable_exceptions=retryable_exceptions
            )
        return wrapper
    return decorator


# 使用示例
class ExternalAPIClient:
    @retry(
        max_retries=3,
        base_delay=1.0,
        retryable_exceptions=(aiohttp.ClientError, asyncio.TimeoutError)
    )
    async def fetch_data(self, url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                response.raise_for_status()
                return await response.json()

    # 或者使用函数式调用
    async def fetch_with_retry(self, url: str) -> dict:
        return await retry_with_backoff(
            lambda: self._fetch(url),
            max_retries=5,
            base_delay=0.5,
            retryable_exceptions=(aiohttp.ClientError,)
        )
```

## 认证与授权

### JWT Token 验证

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建 JWT 访问令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> Optional[dict]:
    """解码并验证 JWT 令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前认证用户"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # 从数据库获取用户
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def require_permissions(required_permissions: list[str]):
    """权限检查依赖工厂"""
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # 检查用户是否有所有必需权限
        user_permissions = set(current_user.permissions or [])

        if not all(p in user_permissions for p in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return permission_checker
```

### 基于角色的访问控制（RBAC）

```python
# app/core/rbac.py
from enum import Enum
from typing import List, Set
from functools import wraps


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


# 角色权限映射
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN},
    Role.MODERATOR: {Permission.READ, Permission.WRITE, Permission.DELETE},
    Role.USER: {Permission.READ, Permission.WRITE}
}


def has_permission(user_role: Role, permission: Permission) -> bool:
    """检查角色是否有权限"""
    return permission in ROLE_PERMISSIONS.get(user_role, set())


def require_permission(permission: Permission):
    """权限要求装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# FastAPI 依赖版本
async def check_permission(
    permission: Permission,
    current_user: User = Depends(get_current_user)
) -> User:
    if not has_permission(current_user.role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


# 路由使用示例
@router.delete("/{market_id}", dependencies=[Depends(require_permission(Permission.DELETE))])
async def delete_market(market_id: str, current_user: User = Depends(get_current_user)):
    """删除市场 - 需要 delete 权限"""
    pass


# 多权限检查
async def require_any_permission(
    permissions: List[Permission],
    current_user: User = Depends(get_current_user)
) -> User:
    user_perms = ROLE_PERMISSIONS.get(current_user.role, set())
    if not any(p in user_perms for p in permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of {permissions} required"
        )
    return current_user
```

## 限流

### 简单内存限流器

```python
# app/middleware/rate_limit.py
import time
from typing import Dict, List
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """内存限流器（适合单实例，多实例请用 Redis）"""

    def __init__(self):
        # {identifier: [timestamp1, timestamp2, ...]}
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """检查是否允许请求"""
        now = time.time()
        window_start = now - window_seconds

        # 获取该标识符的请求历史
        requests = self.requests.get(identifier, [])

        # 清理窗口外的旧请求
        recent_requests = [t for t in requests if t > window_start]

        if len(recent_requests) >= max_requests:
            return False

        # 记录当前请求
        recent_requests.append(now)
        self.requests[identifier] = recent_requests

        return True

    def get_remaining(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> int:
        """获取剩余请求数"""
        now = time.time()
        window_start = now - window_seconds
        requests = self.requests.get(identifier, [])
        recent_requests = [t for t in requests if t > window_start]
        return max(0, max_requests - len(recent_requests))


# 创建全局限流器实例
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        key_func=None
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_func = key_func or self._default_key_func

    @staticmethod
    def _default_key_func(request: Request) -> str:
        """默认使用 IP 地址作为标识"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        identifier = self.key_func(request)

        if not rate_limiter.is_allowed(
            identifier,
            self.max_requests,
            self.window_seconds
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(self.window_seconds)}
            )

        response = await call_next(request)

        # 添加限流头信息
        remaining = rate_limiter.get_remaining(
            identifier,
            self.max_requests,
            self.window_seconds
        )
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response


# 基于 Redis 的分布式限流（多实例部署）
import redis.asyncio as redis

class RedisRateLimiter:
    """Redis 分布式限流器"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """使用滑动窗口限流"""
        now = time.time()
        window_start = now - window_seconds

        pipe = self.redis.pipeline()

        # 移除窗口外的旧请求
        pipe.zremrangebyscore(key, 0, window_start)

        # 获取当前窗口内的请求数
        pipe.zcard(key)

        # 添加当前请求
        pipe.zadd(key, {str(now): now})

        # 设置 key 过期时间
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        current_count = results[1]

        return current_count < max_requests


# FastAPI 依赖方式限流
async def rate_limit(
    request: Request,
    max_requests: int = 100,
    window_seconds: int = 60
):
    """依赖函数限流"""
    identifier = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )


# 路由使用
@router.get("/expensive-endpoint", dependencies=[Depends(rate_limit)])
async def expensive_endpoint():
    """受限流保护的端点"""
    pass


# 针对特定操作的严格限流
@router.post("/login")
async def login(
    request: Request,
    _: None = Depends(lambda r: rate_limit(r, max_requests=5, window_seconds=300))
):
    """登录端点 - 更严格的限流（5次/5分钟）"""
    pass
```

## 后台任务与队列

### 简单内存队列

```python
# app/core/queue.py
import asyncio
from typing import TypeVar, Generic, Callable, Any, Dict
from dataclasses import dataclass
from datetime import datetime
import uuid

T = TypeVar("T")


@dataclass
class Job:
    id: str
    type: str
    payload: Dict[str, Any]
    created_at: datetime
    max_retries: int = 3
    retry_count: int = 0


class JobQueue(Generic[T]):
    """简单异步任务队列（内存版）"""

    def __init__(self):
        self._queue: asyncio.Queue[Job] = asyncio.Queue()
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def register_handler(self, job_type: str, handler: Callable):
        """注册任务处理器"""
        self._handlers[job_type] = handler

    async def add(self, job_type: str, payload: Dict[str, Any], max_retries: int = 3) -> str:
        """添加任务到队列"""
        job = Job(
            id=str(uuid.uuid4()),
            type=job_type,
            payload=payload,
            created_at=datetime.utcnow(),
            max_retries=max_retries
        )
        await self._queue.put(job)
        return job.id

    async def start(self):
        """启动队列处理器"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._process_loop())
        logger.info("Job queue started")

    async def stop(self):
        """停止队列处理器"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Job queue stopped")

    async def _process_loop(self):
        """处理循环"""
        while self._running:
            try:
                job = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )
                await self._execute_job(job)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue processing error: {e}")

    async def _execute_job(self, job: Job):
        """执行单个任务"""
        handler = self._handlers.get(job.type)
        if not handler:
            logger.error(f"No handler for job type: {job.type}")
            return

        try:
            await handler(job.payload)
            logger.info(f"Job {job.id} completed successfully")
        except Exception as e:
            job.retry_count += 1
            if job.retry_count < job.max_retries:
                logger.warning(
                    f"Job {job.id} failed (attempt {job.retry_count}), retrying: {e}"
                )
                await self._queue.put(job)
            else:
                logger.error(f"Job {job.id} failed after {job.max_retries} retries: {e}")
                # 可以发送到死信队列


# 使用 Celery 的示例（生产环境推荐）
# app/core/celery.py
from celery import Celery

# 初始化 Celery
celery_app = Celery(
    "app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks.market"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
    worker_prefetch_multiplier=1,  # 公平调度
)


# app/tasks/market.py
from app.core.celery import celery_app


@celery_app.task(bind=True, max_retries=3)
def process_market_data(self, market_id: str):
    """处理市场数据的异步任务"""
    try:
        # 执行耗时操作
        result = expensive_operation(market_id)
        return {"status": "success", "result": result}
    except Exception as exc:
        # 指数退避重试
        retry_in = 60 * (2 ** self.request.retries)  # 1m, 2m, 4m
        raise self.retry(exc=exc, countdown=retry_in)


@celery_app.task
def send_notification(user_id: str, message: str):
    """发送通知的异步任务"""
    # 发送邮件/短信/推送
    pass


# 在 API 中调用
@router.post("/{market_id}/analyze")
async def analyze_market(market_id: str):
    """提交市场分析任务"""
    # 立即返回任务 ID
    task = process_market_data.delay(market_id)
    return {"task_id": task.id, "status": "pending"}
```

## 日志与监控

### 结构化日志配置

```python
# app/core/logging.py
import logging
import sys
from typing import Any, Dict
import json
from datetime import datetime
from contextvars import ContextVar
import uuid

# 请求上下文
request_id_ctx: ContextVar[str] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[str] = ContextVar("user_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON 格式日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加上下文信息
        request_id = request_id_ctx.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = user_id_ctx.get()
        if user_id:
            log_data["user_id"] = user_id

        # 添加额外字段
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # 异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO"):
    """配置日志"""
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有处理器
    root_logger.handlers = []

    # 标准输出处理器
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(stdout_handler)

    # 第三方库日志级别调整
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


class ContextualLogger:
    """带上下文的日志包装器"""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _log(self, level: int, message: str, **kwargs):
        extra = {"extra": kwargs}
        self._logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        if exc_info:
            self._logger.exception(message)
        else:
            self._log(logging.ERROR, message, **kwargs)


# 创建日志实例
logger = ContextualLogger("app")


# FastAPI 中间件自动添加请求上下文
# app/middleware/logging.py
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request_id_ctx.set(request_id)

        # 记录请求开始
        start_time = time.time()
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            client=request.client.host if request.client else None
        )

        try:
            response = await call_next(request)

            # 记录请求完成
            duration = time.time() - start_time
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )

            # 添加请求 ID 到响应头
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                exc_info=True,
                duration_ms=round(duration * 1000, 2)
            )
            raise
        finally:
            # 清理上下文
            request_id_ctx.set(None)
```

### 健康检查与指标

```python
# app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.db.session import engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():
    """就绪检查 - 检查依赖服务"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis()
    }

    all_healthy = all(c["healthy"] for c in checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }


async def check_database() -> dict:
    """检查数据库连接"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"healthy": True}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


# 使用 prometheus_client 暴露指标
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

# 定义指标
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections"
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ACTIVE_CONNECTIONS.inc()
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            ACTIVE_CONNECTIONS.dec()

            # 记录指标
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status_code
            ).inc()

            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)

        return response


# 指标端点
@router.get("/metrics")
async def metrics():
    """Prometheus 指标端点"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

**记住**：Python 后端模式使服务端应用可扩展、可维护。选择适合复杂度的模式，充分利用 FastAPI 的异步特性和类型安全。
