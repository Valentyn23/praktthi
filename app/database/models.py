from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import Integer, String, Boolean, Text, Float, DateTime
from sqlalchemy import Column
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    balance = Column(Float, default=0.0)
    phone = Column(String(20), nullable=True)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_tg = Column(Integer, nullable=True)  # telegram id of owner; nullable for public

class SecuritySystem(Base):
    __tablename__ = "security_systems"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cameras_count = Column(Integer, nullable=False)  # кількість камер
    coverage_area = Column(Integer, nullable=False)  # площа покриття (м²)
    price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    features = Column(Text, nullable=True)  # особливості (JSON string)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_tg_id = Column(Integer, nullable=False)
    system_id = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # pending, paid, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def seed_systems():
    """Додати початкові дані для систем відеоспостереження"""
    async with async_session() as session:
        from sqlalchemy import select
        # Перевірка чи є вже дані
        result = await session.execute(select(SecuritySystem))
        if result.scalars().first():
            return  # Дані вже є
            
        systems = [
            SecuritySystem(
                name="Базовий комплект для квартири",
                description="2 камери для невеликої квартири",
                cameras_count=2,
                coverage_area=50,
                price=150.0,
                features="HD якість, нічне бачення, мобільний додаток"
            ),
            SecuritySystem(
                name="Стандарт для будинку",
                description="4 камери для приватного будинку",
                cameras_count=4,
                coverage_area=150,
                price=350.0,
                features="Full HD, нічне бачення, датчик руху, запис на хмару"
            ),
            SecuritySystem(
                name="Розширена система",
                description="8 камер для великого будинку або офісу",
                cameras_count=8,
                coverage_area=300,
                price=700.0,
                features="4K якість, нічне бачення, розпізнавання облич, 30 днів запису"
            ),
            SecuritySystem(
                name="Професійна система",
                description="16 камер для великих об'єктів",
                cameras_count=16,
                coverage_area=600,
                price=1500.0,
                features="4K якість, PTZ камери, розпізнавання номерів, інтеграція з сигналізацією"
            ),
            SecuritySystem(
                name="Міні-комплект",
                description="1 камера для контролю входу",
                cameras_count=1,
                coverage_area=20,
                price=80.0,
                features="HD якість, WiFi, мобільний додаток"
            ),
        ]
        session.add_all(systems)
        await session.commit()
