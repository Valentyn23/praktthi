from .models import async_session, User, Task, SecuritySystem, Order
from sqlalchemy import select, desc

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

async def update_user_phone(tg_id: int, phone: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return None
        user.phone = phone
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

# Security Systems
async def get_all_systems():
    async with async_session() as session:
        result = await session.execute(select(SecuritySystem))
        return result.scalars().all()

async def get_systems_by_params(min_cameras: int = 0, min_area: int = 0, max_price: float = 999999):
    async with async_session() as session:
        result = await session.execute(
            select(SecuritySystem)
            .where(SecuritySystem.cameras_count >= min_cameras)
            .where(SecuritySystem.coverage_area >= min_area)
            .where(SecuritySystem.price <= max_price)
        )
        return result.scalars().all()

async def get_system_by_id(system_id: int):
    async with async_session() as session:
        return await session.get(SecuritySystem, system_id)

# Orders
async def create_order(user_tg_id: int, system_id: int, phone: str, total_price: float):
    async with async_session() as session:
        order = Order(
            user_tg_id=user_tg_id,
            system_id=system_id,
            phone=phone,
            total_price=total_price,
            status="paid"
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

async def get_user_orders(user_tg_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.user_tg_id == user_tg_id)
            .order_by(desc(Order.created_at))
        )
        return result.scalars().all()

async def get_order_by_id(order_id: int):
    async with async_session() as session:
        return await session.get(Order, order_id)
