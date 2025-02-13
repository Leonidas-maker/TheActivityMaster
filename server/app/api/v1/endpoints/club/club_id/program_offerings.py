from fastapi import APIRouter
import uuid


# Router for club sessions endpoints
router = APIRouter()

###########################################################################
############################ Program Offerings ############################
###########################################################################
@router.get("", tags=["Club - Program"])
async def get_programs_v1(club_id: uuid.UUID):
    pass


@router.post("", tags=["Club - Program"])
async def create_program_v1(club_id: uuid.UUID):
    pass


@router.get("/{program_id}", tags=["Club - Program"])
async def get_program_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


@router.put("/{program_id}", tags=["Club - Program"])
async def update_program_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


@router.delete("/{program_id}", tags=["Club - Program"])
async def delete_program_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


# ======================================================== #
# ======================= Sessions ======================= #
# ======================================================== #
@router.get("/{program_id}/sessions", tags=["Club - Program - Session"])
async def get_program_sessions_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


@router.post("/{program_id}/sessions", tags=["Club - Program - Session"])
async def create_session_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


@router.get("/{program_id}/sessions/{session_id}", tags=["Club - Program - Session"])
async def get_session_v1(club_id: uuid.UUID, program_id: uuid.UUID, session_id: uuid.UUID):
    pass


@router.put("/{program_id}/sessions/{session_id}", tags=["Club - Program - Session"])
async def update_session_v1(club_id: uuid.UUID, program_id: uuid.UUID, session_id: uuid.UUID):
    pass


@router.delete("/{program_id}/sessions/{session_id}", tags=["Club - Program - Session"])
async def delete_session_v1(club_id: uuid.UUID, program_id: uuid.UUID, session_id: uuid.UUID):
    pass


# ======================================================== #
# =================== SessionOccurrence ================== #
# ======================================================== #
@router.get("/{program_id}/sessions/{session_id}/occurrences", tags=["Club - Program - Session Occurrence"])
async def get_occurrences_v1(club_id: uuid.UUID, session_id: uuid.UUID):
    pass


@router.put(
    "/{program_id}/sessions/{session_id}/occurrences/{occurrence_id}", tags=["Club - Program - Session Occurrence"]
)
async def update_occurrence_v1(club_id: uuid.UUID, session_id: uuid.UUID, occurrence_id: uuid.UUID):
    pass


@router.delete(
    "/{program_id}/sessions/{session_id}/occurrences/{occurrence_id}", tags=["Club - Program - Session Occurrence"]
)
async def delete_occurrence_v1(club_id: uuid.UUID, session_id: uuid.UUID, occurrence_id: uuid.UUID):
    pass