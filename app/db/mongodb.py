import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from app.models.mask import Mask
from app.models.thermogram import Thermogram

load_dotenv()


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        self.db = self.client[os.getenv("MONGODB_DB_NAME")]
        # Создаем индексы
        await self.db.thermograms.create_index("date_time", unique=True)
        await self.db.masks.create_index("date_time", unique=True)

    async def save_thermogram(self, thermogram: Thermogram) -> None:
        """Сохраняет термограмму в БД, возвращает ID"""
        data = thermogram.to_dict()
        await self.db.thermograms.replace_one({"date_time": data["date_time"]}, data, upsert=True)
        print("сохранил термограмму")
        return

    async def get_thermogram(self, thermogram_id: str) -> Optional[Thermogram]:
        """Загружает термограмму по ID"""
        data = await self.db.thermograms.find_one({"_id": ObjectId(thermogram_id)})
        return Thermogram.from_dict(data) if data else None

    async def get_closest_thermogram(self, target_time: datetime) -> Optional[Thermogram]:
        """
        Находит термограмму, ближайшую к указанному времени
        Возвращает ThermogramInDB с бинарными данными
        """
        prev_thermo = await self.db.thermograms.find_one(
            {"date_time": {"$lte": target_time}}, sort=[("date_time", DESCENDING)]
        )

        next_thermo = await self.db.thermograms.find_one(
            {"date_time": {"$gte": target_time}}, sort=[("date_time", ASCENDING)]
        )

        if prev_thermo and next_thermo:
            prev_diff = (target_time - prev_thermo["date_time"]).total_seconds()
            next_diff = (next_thermo["date_time"] - target_time).total_seconds()
            closest = prev_thermo if prev_diff < next_diff else next_thermo
        else:
            closest = prev_thermo or next_thermo
        return Thermogram.from_dict(closest)

    async def get_all_thermogram_times(self) -> List[datetime]:
        """
        Возвращает список всех времен термограмм в базе
        """
        cursor = self.db.thermograms.find({}, {"date_time": 1}).sort("date_time", ASCENDING)

        return [doc["date_time"] async for doc in cursor]

    async def save_mask(self, mask: Mask) -> None:
        """Сохраняет маску в БД, возвращает ID"""
        data = mask.to_dict()
        await self.db.masks.replace_one({"date_time": data["date_time"]}, data, upsert=True)
        print("сохранил маску")

    async def get_mask(self, mask_id: str) -> Optional[Mask]:
        """Загружает маску по ID"""
        data = await self.db.masks.find_one({"_id": ObjectId(mask_id)})
        return Mask.from_dict(data) if data else None

    async def get_closest_mask(self, target_time: datetime) -> Optional[Mask]:
        """
        Находит термограмму, ближайшую к указанному времени
        Возвращает ThermogramInDB с бинарными данными
        """
        prev_thermo = await self.db.masks.find_one(
            {"date_time": {"$lte": target_time}}, sort=[("date_time", DESCENDING)]
        )

        next_thermo = await self.db.masks.find_one(
            {"date_time": {"$gte": target_time}}, sort=[("date_time", ASCENDING)]
        )

        if prev_thermo and next_thermo:
            prev_diff = (target_time - prev_thermo["date_time"]).total_seconds()
            next_diff = (next_thermo["date_time"] - target_time).total_seconds()
            closest = prev_thermo if prev_diff < next_diff else next_thermo
        else:
            closest = prev_thermo or next_thermo
        return Mask.from_dict(closest)

    async def get_all_mask_times(self) -> List[datetime]:
        """
        Возвращает список всех времен термограмм в базе
        """
        cursor = self.db.masks.find({}, {"date_time": 1}).sort("date_time", ASCENDING)

        return [doc["date_time"] async for doc in cursor]


mongodb = MongoDB()
