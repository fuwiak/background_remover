#!/usr/bin/env python3
"""
Скрипт для проверки наличия папки "Тест комтех" на Яндекс Диске
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def check_folder_exists(folder_name="Тест комтех"):
    token = os.getenv("YANDEX_DISK_TOKEN")
    
    if not token:
        print("❌ Ошибка: YANDEX_DISK_TOKEN не найден в .env файле")
        return False
    
    print("=" * 60)
    print("Проверка наличия папки на Яндекс Диске")
    print("=" * 60)
    print(f"Ищем папку: {folder_name}\n")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://cloud-api.yandex.net/v1/disk/resources",
                params={"path": "/", "limit": 1000},
                headers={"Authorization": f"OAuth {token}"},
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"❌ Ошибка при получении списка папок: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
            
            data = response.json()
            folders = [
                {"name": item["name"], "path": item["path"]}
                for item in data.get("_embedded", {}).get("items", [])
                if item.get("type") == "dir"
            ]
            
            print(f"📁 Найдено папок в корне: {len(folders)}\n")
            
            # Ищем нужную папку
            found = False
            for folder in folders:
                if folder["name"] == folder_name:
                    found = True
                    print(f"✅ Папка '{folder_name}' НАЙДЕНА!")
                    print(f"   Путь: {folder['path']}")
                    break
            
            if not found:
                print(f"❌ Папка '{folder_name}' НЕ найдена в корневой папке")
                print("\n📋 Список всех папок в корне:")
                for folder in folders:
                    print(f"   - {folder['name']} ({folder['path']})")
            
            return found
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    asyncio.run(check_folder_exists("Тест комтех"))

