from .models import async_session, User, Task
from sqlalchemy import select

async def get_or_create_user(tg_id: int, name: str | None = None):
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not result:
            user = User(tg_id=tg_id, name=name or "")
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        return result

async def get_user_by_tg(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def update_balance(tg_id: int, new_balance: float):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return None
        user.balance = new_balance
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# Tasks CRUD for webapp
async def create_task(title: str, description: str, owner_tg: int | None = None):
    async with async_session() as session:
        task = Task(title=title, description=description, owner_tg=owner_tg)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

async def get_tasks(owner_tg: int | None = None):
    async with async_session() as session:
        if owner_tg is None:
            res = await session.execute(select(Task))
        else:
            res = await session.execute(select(Task).where(Task.owner_tg == owner_tg))
        return res.scalars().all()

async def get_task_by_id(task_id: int):
    async with async_session() as session:
        return await session.get(Task, task_id)

async def delete_task(task_id: int):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if task:
            await session.delete(task)
            await session.commit()
            return True
        return False

async def update_task(task_id: int, title: str, description: str):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            return None
        task.title = title
        task.description = description
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
