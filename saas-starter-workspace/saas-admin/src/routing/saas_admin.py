"""SaaS admin routes composed from installed RapidKit modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from src.modules.free.auth.core.auth.core import AuthCoreRuntime
from src.modules.free.auth.core.auth.dependencies import get_auth_core_runtime
from src.modules.free.users.users_core.core.users.dependencies import get_users_service
from src.modules.free.users.users_core.core.users.dto import UserDTO, UserUpdateDTO
from src.modules.free.users.users_core.core.users.errors import UserNotFoundError
from src.modules.free.users.users_core.core.users.models import UserStatus
from src.modules.free.users.users_core.core.users.service import UsersService

router = APIRouter(tags=["saas-admin"])


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


@dataclass(slots=True)
class AdminStore:
    subscriptions: list[dict[str, Any]]
    audit_logs: list[dict[str, Any]]


_ADMIN_STORE = AdminStore(
    subscriptions=[
        {
            "id": "sub_1",
            "user_id": "demo_user_1",
            "plan_id": "starter",
            "status": "active",
            "amount_monthly": 19,
            "currency": "usd",
        },
        {
            "id": "sub_2",
            "user_id": "demo_user_2",
            "plan_id": "growth",
            "status": "active",
            "amount_monthly": 79,
            "currency": "usd",
        },
    ],
    audit_logs=[],
)


def _utcnow_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _admin_credentials() -> tuple[str, str]:
    email = os.getenv("SAAS_ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("SAAS_ADMIN_PASSWORD", "AdminPass123!")
    return email, password


def _require_admin_claims(request: Request, auth_runtime: AuthCoreRuntime) -> dict[str, Any]:
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = auth_header.split(" ", 1)[1]
    try:
        claims = auth_runtime.verify_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    roles = claims.get("roles") or []
    if "admin" not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return claims


@router.post("/admin/auth/login")
async def admin_login(
    payload: AdminLoginRequest,
    auth_runtime: AuthCoreRuntime = Depends(get_auth_core_runtime),
) -> dict[str, Any]:
    expected_email, expected_password = _admin_credentials()
    if payload.email != expected_email or payload.password != expected_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials")

    access_token = auth_runtime.issue_token(
        subject=f"admin:{payload.email}",
        scopes=["admin:read", "admin:write", "metrics:read"],
        custom_claims={"roles": ["admin"], "email": str(payload.email)},
    )
    return {"access_token": access_token, "token_type": "bearer", "role": "admin"}


@router.get("/admin/users")
async def admin_list_users(
    request: Request,
    users_service: UsersService = Depends(get_users_service),
    auth_runtime: AuthCoreRuntime = Depends(get_auth_core_runtime),
) -> dict[str, Any]:
    _require_admin_claims(request, auth_runtime)
    users = [UserDTO.from_entity(entity).model_dump(mode="json") for entity in await users_service.list_users()]
    return {"users": users, "count": len(users)}


@router.put("/admin/users/{user_id}/ban")
async def admin_ban_user(
    user_id: str,
    request: Request,
    users_service: UsersService = Depends(get_users_service),
    auth_runtime: AuthCoreRuntime = Depends(get_auth_core_runtime),
) -> dict[str, Any]:
    claims = _require_admin_claims(request, auth_runtime)
    try:
        updated = await users_service.update_user(user_id, UserUpdateDTO(status=UserStatus.DISABLED))
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    _ADMIN_STORE.audit_logs.append(
        {
            "action": "ban_user",
            "target_user_id": user_id,
            "performed_by": claims.get("sub"),
            "at": _utcnow_iso(),
        }
    )
    return {"user": UserDTO.from_entity(updated).model_dump(mode="json"), "status": "banned"}


@router.get("/admin/subscriptions")
async def admin_subscriptions(
    request: Request,
    auth_runtime: AuthCoreRuntime = Depends(get_auth_core_runtime),
) -> dict[str, Any]:
    _require_admin_claims(request, auth_runtime)
    return {"subscriptions": _ADMIN_STORE.subscriptions, "count": len(_ADMIN_STORE.subscriptions)}


@router.get("/admin/metrics/users")
async def admin_users_metrics(
    request: Request,
    users_service: UsersService = Depends(get_users_service),
    auth_runtime: AuthCoreRuntime = Depends(get_auth_core_runtime),
) -> dict[str, Any]:
    _require_admin_claims(request, auth_runtime)
    users = await users_service.list_users()
    total = len(users)
    disabled = len([item for item in users if item.status == UserStatus.DISABLED])
    active = len([item for item in users if item.status == UserStatus.ACTIVE])
    return {"total_users": total, "active_users": active, "disabled_users": disabled}


@router.get("/admin/metrics/revenue")
async def admin_revenue_metrics(
    request: Request,
    auth_runtime: AuthCoreRuntime = Depends(get_auth_core_runtime),
) -> dict[str, Any]:
    _require_admin_claims(request, auth_runtime)
    active = [item for item in _ADMIN_STORE.subscriptions if item.get("status") == "active"]
    monthly_revenue = sum(int(item.get("amount_monthly", 0)) for item in active)
    return {
        "active_subscriptions": len(active),
        "monthly_recurring_revenue": monthly_revenue,
        "currency": "usd",
    }


@router.get("/admin/health")
async def admin_health(
    request: Request,
    auth_runtime: AuthCoreRuntime = Depends(get_auth_core_runtime),
) -> dict[str, Any]:
    _require_admin_claims(request, auth_runtime)
    return {
        "status": "ok",
        "service": "saas-admin",
        "uptime": _utcnow_iso(),
        "audit_events": len(_ADMIN_STORE.audit_logs),
    }


__all__ = ["router"]
