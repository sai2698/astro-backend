import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.user import User
from app.api import deps
from app.core.config import settings
from agora_token_builder import RtcTokenBuilder

router = APIRouter()

@router.get("/{appointment_id}/token")
async def get_agora_token(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    query = select(Appointment).filter(Appointment.id == appointment_id)
    result = await db.execute(query)
    appointment = result.scalars().first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    if current_user.id != appointment.user_id and current_user.id != appointment.astrologer_id:
        raise HTTPException(status_code=403, detail="Not authorized to join this call")
        
    if not appointment.agora_channel:
        raise HTTPException(status_code=400, detail="Appointment does not have an active channel")
        
    # Generate token
    appId = settings.AGORA_APP_ID
    appCertificate = settings.AGORA_APP_CERTIFICATE
    channelName = appointment.agora_channel
    uid = current_user.id
    expirationTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expirationTimeInSeconds
    
    try:
        token = RtcTokenBuilder.buildTokenWithUid(
            appId, appCertificate, channelName, uid, 1, privilegeExpiredTs
        )
        return {"token": token, "channel": channelName, "uid": uid}
    except Exception as e:
        # Catch errors if placeholder creds are used
        return {"token": "mock_token_because_invalid_creds", "channel": channelName, "uid": uid}
