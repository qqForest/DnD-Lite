"""API endpoints для системы сохранения сессий."""

import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.player import Player
from app.schemas.persistence import (
    ExportRequest,
    ExportResponse,
    ImportRequest,
    ImportResponse,
    ValidationRequest,
    ValidationResponse,
)
from app.services.persistence import (
    export_session,
    import_session,
    validate_import_data,
)
from app.core.auth import get_current_player

router = APIRouter()




@router.post("/session/export", response_model=ExportResponse)
def export_session_endpoint(
    request: ExportRequest = ExportRequest(),
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db),
):
    """Экспортировать текущую сессию в JSON.

    Только для GM.
    """
    if not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can perform this action")

    try:
        data = export_session(
            db=db,
            session_id=current_player.session_id,
            include_combat=request.include_combat,
        )
        return ExportResponse(success=True, data=data)
    except Exception as e:
        return ExportResponse(success=False, error=str(e))


@router.post("/session/export/download")
def export_session_download(
    request: ExportRequest = ExportRequest(),
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db),
):
    """Скачать экспорт сессии как JSON файл.

    Только для GM.
    """
    if not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can perform this action")

    try:
        data = export_session(
            db=db,
            session_id=current_player.session_id,
            include_combat=request.include_combat,
        )

        session_code = data["session_info"]["code"]
        filename = f"dnd_session_{session_code}.json"

        json_content = json.dumps(data, ensure_ascii=False, indent=2)

        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/import", response_model=ImportResponse)
def import_session_endpoint(
    request: ImportRequest,
    db: DBSession = Depends(get_db),
):
    """Импортировать сессию из JSON.

    Создаёт новую сессию с новыми токенами.
    Не требует авторизации.
    """
    try:
        result = import_session(
            db=db,
            data=request.data,
            new_session_code=request.new_session_code,
        )

        return ImportResponse(
            success=result.success,
            session_id=result.session_id,
            session_code=result.session_code,
            gm_token=result.gm_token,
            player_tokens=result.player_tokens,
            entity_counts=result.entity_counts,
            warnings=result.warnings,
            errors=result.errors,
        )
    except Exception as e:
        return ImportResponse(
            success=False,
            errors=[str(e)],
        )


@router.post("/session/validate", response_model=ValidationResponse)
def validate_session_endpoint(
    request: ValidationRequest,
    db: DBSession = Depends(get_db),
):
    """Валидировать данные импорта без создания записей.

    Не требует авторизации.
    """
    try:
        result = validate_import_data(request.data)

        return ValidationResponse(
            is_valid=result.is_valid,
            format_version=result.format_version,
            entity_counts=result.entity_counts,
            warnings=result.warnings,
            errors=result.errors,
        )
    except Exception as e:
        return ValidationResponse(
            is_valid=False,
            format_version="unknown",
            errors=[str(e)],
        )
