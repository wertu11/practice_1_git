#!/usr/bin/env python3
"""
Приложение для хранения заметок на Python
Консольное приложение с CRUD операциями для управления заметками
"""

import json
import os
from datetime import datetime
from typing import Optional


class Note:
    """Класс представляющий одну заметку"""
    
    def __init__(self, title: str, content: str, note_id: Optional[int] = None):
        self.id = note_id
        self.title = title
        self.content = content
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
    
    def to_dict(self) -> dict:
        """Преобразует заметку в словарь"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Создает заметку из словаря"""
        note = cls(data["title"], data["content"], data.get("id"))
        note.created_at = data.get("created_at", note.created_at)
        note.updated_at = data.get("updated_at", note.updated_at)
        return note


class NoteStorage:
    """Класс для хранения и управления заметками"""
    
    def __init__(self, storage_file: str = "notes.json"):
        self.storage_file = storage_file
        self.notes: list[Note] = []
        self._load_notes()
    
    def _load_notes(self) -> None:
        """Загружает заметки из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.notes = [Note.from_dict(note_data) for note_data in data]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке заметок: {e}")
                self.notes = []
    
    def _save_notes(self) -> None:
        """Сохраняет заметки в файл"""
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump([note.to_dict() for note in self.notes], f, 
                         ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка при сохранении заметок: {e}")
    
    def _get_next_id(self) -> int:
        """Получает следующий доступный ID для заметки"""
        if not self.notes:
            return 1
        return max(note.id for note in self.notes) + 1
    
    def create_note(self, title: str, content: str) -> Note:
        """Создает новую заметку"""
        note = Note(title, content, self._get_next_id())
        self.notes.append(note)
        self._save_notes()
        return note
    
    def get_note(self, note_id: int) -> Optional[Note]:
        """Получает заметку по ID"""
        for note in self.notes:
            if note.id == note_id:
                return note
        return None
    
    def get_all_notes(self) -> list[Note]:
        """Получает все заметки"""
        return self.notes
    
    def update_note(self, note_id: int, title: Optional[str] = None, 
                   content: Optional[str] = None) -> Optional[Note]:
        """Обновляет заметку"""
        note = self.get_note(note_id)
        if note:
            if title:
                note.title = title
            if content:
                note.content = content
            note.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_notes()
        return note
    
    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку"""
        note = self.get_note(note_id)
        if note:
            self.notes.remove(note)
            self._save_notes()
            return True
        return False
    
    def search_notes(self, query: str) -> list[Note]:
        """Ищет заметки по заголовку или содержанию"""
        query_lower = query.lower()
        return [
            note for note in self.notes 
            if query_lower in note.title.lower() or query_lower in note.content.lower()
        ]


class NoteApp:
    """Основное приложение для работы с заметками"""
    
    def __init__(self):
        self.storage = NoteStorage()
    
    def display_menu(self) -> None:
        """Отображает главное меню"""
        print("\n" + "=" * 50)
        print("       ПРИЛОЖЕНИЕ ДЛЯ ХРАНЕНИЯ ЗАМЕТОК")
        print("=" * 50)
        print("1. Показать все заметки")
        print("2. Создать новую заметку")
        print("3. Просмотреть заметку")
        print("4. Редактировать заметку")
        print("5. Удалить заметку")
        print("6. Поиск заметок")
        print("7. Выход")
        print("=" * 50)
    
    def display_note(self, note: Note) -> None:
        """Отображает информацию о заметке"""
        print(f"\nID: {note.id}")
        print(f"Заголовок: {note.title}")
        print(f"Содержание: {note.content}")
        print(f"Создана: {note.created_at}")
        print(f"Обновлена: {note.updated_at}")
    
    def show_all_notes(self) -> None:
        """Показывает все заметки"""
        notes = self.storage.get_all_notes()
        if not notes:
            print("\nЗаметок пока нет.")
            return
        
        print(f"\nВсего заметок: {len(notes)}")
        print("-" * 50)
        for note in notes:
            print(f"[{note.id}] {note.title} ({note.created_at})")
    
    def create_new_note(self) -> None:
        """Создает новую заметку"""
        print("\n--- Создание новой заметки ---")
        title = input("Введите заголовок: ").strip()
        if not title:
            print("Заголовок не может быть пустым!")
            return
        
        content = input("Введите содержание: ").strip()
        
        note = self.storage.create_note(title, content)
        print(f"\nЗаметка создана успешно! ID: {note.id}")
    
    def view_note(self) -> None:
        """Просматривает заметку"""
        try:
            note_id = int(input("\nВведите ID заметки: "))
            note = self.storage.get_note(note_id)
            if note:
                self.display_note(note)
            else:
                print("Заметка с таким ID не найдена.")
        except ValueError:
            print("Некорректный ID!")
    
    def edit_note(self) -> None:
        """Редактирует заметку"""
        try:
            note_id = int(input("\nВведите ID заметки для редактирования: "))
            note = self.storage.get_note(note_id)
            
            if not note:
                print("Заметка с таким ID не найдена.")
                return
            
            print(f"\nРедактирование заметки #{note_id}")
            print(f"Текущий заголовок: {note.title}")
            new_title = input("Новый заголовок (оставьте пустым, чтобы не менять): ").strip()
            
            print(f"Текущее содержание: {note.content}")
            new_content = input("Новое содержание (оставьте пустым, чтобы не менять): ").strip()
            
            if new_title or new_content:
                self.storage.update_note(note_id, new_title if new_title else None,
                                        new_content if new_content else None)
                print("Заметка обновлена!")
            else:
                print("Изменений не внесено.")
        except ValueError:
            print("Некорректный ID!")
    
    def delete_note(self) -> None:
        """Удаляет заметку"""
        try:
            note_id = int(input("\nВведите ID заметки для удаления: "))
            note = self.storage.get_note(note_id)
            
            if not note:
                print("Заметка с таким ID не найдена.")
                return
            
            confirm = input(f"Вы уверены, что хотите удалить заметку '{note.title}'? (y/n): ")
            if confirm.lower() == 'y':
                self.storage.delete_note(note_id)
                print("Заметка удалена!")
            else:
                print("Удаление отменено.")
        except ValueError:
            print("Некорректный ID!")
    
    def search_notes(self) -> None:
        """Ищет заметки"""
        query = input("\nВведите поисковый запрос: ").strip()
        if not query:
            print("Поисковый запрос не может быть пустым!")
            return
        
        results = self.storage.search_notes(query)
        if not results:
            print("Ничего не найдено.")
            return
        
        print(f"\nНайдено заметок: {len(results)}")
        print("-" * 50)
        for note in results:
            print(f"[{note.id}] {note.title} ({note.created_at})")
    
    def run(self) -> None:
        """Запускает приложение"""
        print("\nДобро пожаловать в приложение для хранения заметок!")
        
        while True:
            self.display_menu()
            choice = input("Выберите действие (1-7): ").strip()
            
            if choice == "1":
                self.show_all_notes()
            elif choice == "2":
                self.create_new_note()
            elif choice == "3":
                self.view_note()
            elif choice == "4":
                self.edit_note()
            elif choice == "5":
                self.delete_note()
            elif choice == "6":
                self.search_notes()
            elif choice == "7":
                print("\nДо свидания!")
                break
            else:
                print("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    app = NoteApp()
    app.run()
