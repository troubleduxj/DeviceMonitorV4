#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户通知 API v2
提供用户查看和管理自己通知的接口
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Query, Depends
from tortoise.expressions import Q

from app.models.notification import Notification, UserNotification
from app.core.response_formatter_v2 import create_formatter
from app.core.pagination import get_pagination_params, create_pagination_response
from app.log import logger

router = APIRouter(tags=["用户通知"])


@router.get("", summary="获取我的通知")
async def get_my_notifications(
    notification_type: Optional[str] = Query(None, description="通知类型"),
    is_read: Optional[bool] = Query(None, description="是否已读"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    user_id: int = Query(..., description="用户ID"),
    pagination: dict = Depends(get_pagination_params)
):
    """获取当前用户的通知列表"""
    try:
        now = datetime.now()
        
        base_query = Notification.filter(is_published=True).filter(
            Q(expire_time__isnull=True) | Q(expire_time__gt=now)
        )
        
        if notification_type:
            base_query = base_query.filter(notification_type=notification_type)
        if search:
            base_query = base_query.filter(title__icontains=search)
        
        notifications = await base_query.order_by("-publish_time").offset(pagination["offset"]).limit(pagination["limit"])
        total = await base_query.count()
        
        notification_ids = [n.id for n in notifications]
        user_notifications = await UserNotification.filter(
            user_id=user_id, notification_id__in=notification_ids
        ).all()
        
        read_map = {un.notification_id: un for un in user_notifications}

        items = []
        for n in notifications:
            un = read_map.get(n.id)
            if un and un.is_deleted:
                continue
            
            notification_is_read = un.is_read if un else False
            if is_read is not None and notification_is_read != is_read:
                continue
            
            items.append({
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "notification_type": n.notification_type,
                "level": n.level,
                "link_url": n.link_url,
                "publish_time": n.publish_time.isoformat() if n.publish_time else None,
                "is_read": notification_is_read,
                "read_time": un.read_time.isoformat() if un and un.read_time else None,
            })
        
        paginated = create_pagination_response(
            data=items, total=len(items), page=pagination["page"], page_size=pagination["page_size"]
        )
        
        formatter = create_formatter()
        return formatter.success(data=paginated, message="获取通知列表成功")
        
    except Exception as e:
        logger.error(f"获取用户通知失败: {str(e)}", exc_info=True)
        formatter = create_formatter()
        return formatter.error(message="获取通知列表失败")


@router.get("/unread-count", summary="获取未读通知数量")
async def get_unread_count(user_id: int = Query(..., description="用户ID")):
    """获取当前用户的未读通知数量"""
    try:
        now = datetime.now()
        
        total_notifications = await Notification.filter(is_published=True).filter(
            Q(expire_time__isnull=True) | Q(expire_time__gt=now)
        ).count()
        
        read_count = await UserNotification.filter(
            user_id=user_id, is_read=True, is_deleted=False
        ).count()
        
        deleted_count = await UserNotification.filter(
            user_id=user_id, is_deleted=True
        ).count()
        
        unread_count = max(0, total_notifications - read_count - deleted_count)
        
        formatter = create_formatter()
        return formatter.success(
            data={"unread_count": unread_count, "total": total_notifications},
            message="获取未读数量成功"
        )
        
    except Exception as e:
        logger.error(f"获取未读数量失败: {str(e)}", exc_info=True)
        formatter = create_formatter()
        return formatter.error(message="获取未读数量失败")


@router.post("/{notification_id}/read", summary="标记通知已读")
async def mark_as_read(notification_id: int, user_id: int = Query(..., description="用户ID")):
    """标记通知为已读"""
    try:
        notification = await Notification.get_or_none(id=notification_id)
        if not notification:
            formatter = create_formatter()
            return formatter.error(message="通知不存在", code=404)
        
        un, created = await UserNotification.get_or_create(
            user_id=user_id,
            notification_id=notification_id,
            defaults={"is_read": True, "read_time": datetime.now()}
        )
        
        if not created and not un.is_read:
            un.is_read = True
            un.read_time = datetime.now()
            await un.save()
        
        formatter = create_formatter()
        return formatter.success(message="标记已读成功")
        
    except Exception as e:
        logger.error(f"标记已读失败: {str(e)}", exc_info=True)
        formatter = create_formatter()
        return formatter.error(message="标记已读失败")


@router.post("/read-all", summary="全部标记已读")
async def mark_all_as_read(user_id: int = Query(..., description="用户ID")):
    """将所有通知标记为已读"""
    try:
        now = datetime.now()
        
        notifications = await Notification.filter(is_published=True).filter(
            Q(expire_time__isnull=True) | Q(expire_time__gt=now)
        ).all()
        
        for n in notifications:
            un, created = await UserNotification.get_or_create(
                user_id=user_id,
                notification_id=n.id,
                defaults={"is_read": True, "read_time": now}
            )
            
            if not created and not un.is_read:
                un.is_read = True
                un.read_time = now
                await un.save()
        
        formatter = create_formatter()
        return formatter.success(message="全部标记已读成功")
        
    except Exception as e:
        logger.error(f"全部标记已读失败: {str(e)}", exc_info=True)
        formatter = create_formatter()
        return formatter.error(message="全部标记已读失败")


@router.delete("/{notification_id}", summary="删除通知")
async def delete_user_notification(notification_id: int, user_id: int = Query(..., description="用户ID")):
    """删除用户的通知（软删除）"""
    try:
        un, created = await UserNotification.get_or_create(
            user_id=user_id,
            notification_id=notification_id,
            defaults={"is_deleted": True}
        )
        
        if not created:
            un.is_deleted = True
            await un.save()
        
        formatter = create_formatter()
        return formatter.success(message="删除通知成功")
        
    except Exception as e:
        logger.error(f"删除通知失败: {str(e)}", exc_info=True)
        formatter = create_formatter()
        return formatter.error(message="删除通知失败")
