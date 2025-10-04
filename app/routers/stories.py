from fastapi import APIRouter, Depends, HTTPException
from pymysql.connections import Connection

from app.database import core as db_core
from app.database import schemas

story_router = APIRouter(
    prefix="/stories",
    tags=["Stories API"]
)

@story_router.post("/", response_model=schemas.Story, description="새로운 AI 캐릭터(스토리)를 생성합니다.")
async def create_new_story(
    story_data: schemas.StoryCreate,
    db_conn: Connection = Depends(db_core.get_db_connection)
):
    """
    사용자로부터 제목, 프롬프트 등의 정보를 받아 새로운 AI 캐릭터를 DB에 저장합니다.
    """
    new_story = await db_core.create_story(db_conn, story_data)
    if not new_story:
        raise HTTPException(status_code=500, detail="스토리 생성에 실패했습니다.")
    return new_story


@story_router.get("/", response_model=list[schemas.Story], description="모든 AI 캐릭터(스토리) 목록을 조회합니다.")
async def get_all_stories_list(db_conn: Connection = Depends(db_core.get_db_connection)):
    """
    DB에 저장된 모든 스토리 목록을 반환합니다.
    """
    stories = await db_core.get_all_stories(db_conn)
    return stories


@story_router.get("/{story_id}", response_model=schemas.Story, description="특정 AI 캐릭터(스토리)의 상세 정보를 조회합니다.")
async def get_story_details(story_id: int, db_conn: Connection = Depends(db_core.get_db_connection)):
    """
    주어진 story_id에 해당하는 스토리의 상세 정보를 반환합니다.
    """
    story = await db_core.get_story_by_id(db_conn, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="해당 스토리를 찾을 수 없습니다.")
    return story


@story_router.delete("/{story_id}", description="AI 캐릭터(스토리)를 삭제합니다.")
async def delete_story(
    story_id: int,
    user_info: schemas.UserSessionCreate, # 삭제를 요청한 사용자 ID를 받기 위해 재활용
    db_conn: Connection = Depends(db_core.get_db_connection)
):
    """
    스토리를 삭제합니다. 단, 해당 스토리를 생성한 사용자만 삭제할 수 있습니다.
    """
    story = await db_core.get_story_by_id(db_conn, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="삭제할 스토리를 찾을 수 없습니다.")
    
    # 스토리를 만든 사람과 삭제를 요청한 사람이 같은지 확인
    if story['creator_id'] != user_info.user_id:
        raise HTTPException(status_code=403, detail="스토리를 삭제할 권한이 없습니다.")
        
    success = await db_core.delete_story_by_id(db_conn, story_id)
    if not success:
        raise HTTPException(status_code=500, detail="스토리 삭제에 실패했습니다.")
    
    return {"message": f"Story ID {story_id}가 성공적으로 삭제되었습니다."}