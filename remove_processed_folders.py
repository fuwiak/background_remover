#!/usr/bin/env python3
"""
Скрипт для удаления папок с окончанием "_Обработанный" из папки "Тест комтех" на Яндекс Диске
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def remove_processed_folders():
    """
    Удаляет все папки с окончанием "_Обработанный" из папки "Тест комтех"
    """
    token = os.getenv("YANDEX_DISK_TOKEN")
    
    if not token:
        print("❌ Ошибка: YANDEX_DISK_TOKEN не найден в .env файле")
        print("   Установите токен в файле .env или в переменных окружения")
        return False
    
    print("=" * 60)
    print("Удаление папок '_Обработанный' из 'Тест комтех'")
    print("=" * 60)
    
    base_folder = "/Тест комтех"
    suffix = "_Обработанный"
    
    async with httpx.AsyncClient() as client:
        try:
            # Получаем список папок в "Тест комтех"
            print(f"\n🔍 Поиск папок в '{base_folder}'...")
            response = await client.get(
                "https://cloud-api.yandex.net/v1/disk/resources",
                params={"path": base_folder, "limit": 1000},
                headers={"Authorization": f"OAuth {token}"},
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"❌ Ошибка при получении списка папок: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
            
            data = response.json()
            items = data.get("_embedded", {}).get("items", [])
            
            # Фильтруем только папки, заканчивающиеся на "_Обработанный"
            folders_to_delete = []
            for item in items:
                if item.get("type") == "dir":
                    folder_name = item.get("name", "")
                    if folder_name.endswith(suffix):
                        folders_to_delete.append({
                            "name": folder_name,
                            "path": item.get("path", "")
                        })
            
            if not folders_to_delete:
                print(f"✅ Папки с окончанием '{suffix}' не найдены в '{base_folder}'")
                return True
            
            print(f"\n📁 Найдено папок для удаления: {len(folders_to_delete)}")
            for folder in folders_to_delete:
                print(f"   - {folder['name']} ({folder['path']})")
            
            # Подтверждение
            print(f"\n⚠️  ВНИМАНИЕ: Будет удалено {len(folders_to_delete)} папок!")
            confirm = input("Продолжить? (yes/no): ").strip().lower()
            
            if confirm not in ['yes', 'y', 'да', 'д']:
                print("❌ Удаление отменено")
                return False
            
            # Удаляем папки
            deleted_count = 0
            failed_count = 0
            
            for folder in folders_to_delete:
                try:
                    print(f"\n🗑️  Удаление: {folder['name']}...")
                    delete_response = await client.delete(
                        "https://cloud-api.yandex.net/v1/disk/resources",
                        params={"path": folder['path'], "permanently": "true"},
                        headers={"Authorization": f"OAuth {token}"},
                        timeout=30.0
                    )
                    
                    if delete_response.status_code in [204, 202]:
                        print(f"   ✅ Удалено: {folder['name']}")
                        deleted_count += 1
                    else:
                        error_text = delete_response.text
                        print(f"   ❌ Ошибка при удалении {folder['name']}: {delete_response.status_code}")
                        print(f"      Ответ: {error_text}")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"   ❌ Ошибка при удалении {folder['name']}: {str(e)}")
                    failed_count += 1
            
            # Итоги
            print("\n" + "=" * 60)
            print("Итоги удаления:")
            print(f"   ✅ Успешно удалено: {deleted_count}")
            if failed_count > 0:
                print(f"   ❌ Ошибок: {failed_count}")
            print("=" * 60)
            
            return failed_count == 0
            
        except httpx.RequestError as e:
            print(f"❌ Ошибка сети: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    success = asyncio.run(remove_processed_folders())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Готово!")
    else:
        print("❌ Завершено с ошибками")
    print("=" * 60)
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()

