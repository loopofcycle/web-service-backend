import uuid
from datetime import datetime
from typing import Annotated
from sqlalchemy import select
from sqlalchemy import Column, String, Integer, DateTime, String, Integer, ForeignKey, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import backref, relationship, DeclarativeBase, mapped_column, declared_attr, Mapped
from sqlalchemy.sql import func

# from app.db.engine import get_session


id_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, unique=True)]
id_fk = Annotated[uuid.UUID, mapped_column(nullable=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(
    server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:

        table_name = str()
        table_name += cls.__name__[0].lower()

        for char in cls.__name__[1:]:
            if char.istitle():
                table_name += '_' + char.lower()
            else:
                table_name += char
        
        table_name = (table_name[:-1] + "ie") if str(table_name).endswith('y') else table_name
        table_name += "s" if cls.__name__[-1] != "s" else "es"

        return table_name

    id: Mapped[id_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # @classmethod
    # async def find_all(cls, **filter_by):
    #     async with get_session() as session:
    #         query = select(cls.model).filter_by(**filter_by)
    #         result = await session.execute(query)
    #         return result.scalars().all()


class SpecParamSet(Base):
    name: Mapped[str] = mapped_column(key='name', name='ADSK_Наименование', type_=String(128), unique=False, nullable=True)
    count: Mapped[int] = mapped_column(key='count', name='ADSK_Количество', type_=Integer, unique=False, nullable=True)
    mark: Mapped[str] = mapped_column(key='mark', name='ADSK_Марка', type_=String(128), unique=False, nullable=True)
    code: Mapped[str] = mapped_column(key='code', name='ADSK_Код изделия', type_=String(128), unique=False, nullable=True)
    manufacturer: Mapped[str] = mapped_column(key='manufacturer', name='ADSK_Завод-изготовитель', type_=String(128), unique=False, nullable=True)
    characteristic: Mapped[str] = mapped_column(key='characteristic', name='ADSK_Техническая характеристика', type_=String(128), unique=False, nullable=True)
    unit: Mapped[str] = mapped_column(key='unit', name='ADSK_Единица измерения', type_=String(128), unique=False, nullable=True)
    mass: Mapped[str] = mapped_column(key='mass', name='ADSK_Масса', type_=String(128), unique=False, nullable=True)
    version: Mapped[str] = mapped_column(key='version', name='ADSK_Версия семейства', type_=String(128), unique=False, nullable=True)
    url: Mapped[str] = mapped_column(key='url', name='ADSK_URL документации изделия', type_=String(128), unique=False, nullable=True)
    type_id = mapped_column(Uuid, ForeignKey('family_types.id'), nullable=False)
    type = relationship('FamilyType', backref=backref('spec_param_sets', lazy=True))


class Category(Base):
    name = Column(String(128), unique=False, nullable=False)
    number = Column(String(128), unique=True, nullable=False)
    label = Column(String(128), unique=False, nullable=True)


class FamilyFile(Base):
    title = Column(String(128), unique=False, nullable=False)
    status = Column(String(128), unique=False, nullable=False)
    path = Column(String(512), unique=True, nullable=False)
    version_id = Column(Uuid, unique=False, nullable=True)
    size = Column(Integer, unique=False, nullable=False)
    category_id = Column(Uuid, ForeignKey('categories.id'), nullable=True)
    category = relationship('Category', backref=backref('families', lazy=True))


class FamilyType(Base):
    name = Column(String(128), unique=False, nullable=False)
    file_id = Column(Uuid, ForeignKey('family_files.id'), nullable=False)
    file = relationship('FamilyFile', backref=backref('types', lazy=True))


class Task(Base):
    file_title = Column(String(128), unique=False, nullable=False)
    file_id = Column(Uuid, ForeignKey('family_files.id'), nullable=False)
    file = relationship('FamilyFile', backref=backref('tasks', lazy=True))
    priority = Column(Integer, unique=False, nullable=True)
    queue = Column(String(128), unique=False, nullable=True)
    revit_app = Column(String(128), unique=False, nullable=True)
    status = Column(String(128), unique=False, nullable=True)
    process_pid = Column(Integer, unique=False, nullable=True)
    celery_status = Column(String(128), unique=False, nullable=True)
    celery_task_id = Column(Uuid, unique=False, nullable=True)
