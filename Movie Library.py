import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Файл для сохранения фильмов
MOVIES_FILE = "movies.json"


class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("800x600")
        
        # Загрузка фильмов
        self.movies = self.load_movies()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Отображение фильмов
        self.refresh_table()
    
    def create_widgets(self):
        # Рамка для добавления фильма
        add_frame = tk.LabelFrame(self.root, text="Добавить фильм", padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поля ввода
        tk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = tk.Entry(add_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Жанр:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.genre_entry = tk.Entry(add_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(add_frame, text="Год:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.year_entry = tk.Entry(add_frame, width=10)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.rating_entry = tk.Entry(add_frame, width=10)
        self.rating_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = tk.Button(add_frame, text="Добавить фильм", command=self.add_movie, bg="lightgreen")
        self.add_btn.grid(row=0, column=4, rowspan=2, padx=20, pady=5)
        
        # Рамка для фильтрации
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Жанр:").pack(side=tk.LEFT, padx=5)
        self.filter_genre = tk.Entry(filter_frame, width=20)
        self.filter_genre.pack(side=tk.LEFT, padx=5)
        self.filter_genre.bind("<KeyRelease>", lambda e: self.filter_movies())
        
        tk.Label(filter_frame, text="Год:").pack(side=tk.LEFT, padx=5)
        self.filter_year = tk.Entry(filter_frame, width=10)
        self.filter_year.pack(side=tk.LEFT, padx=5)
        self.filter_year.bind("<KeyRelease>", lambda e: self.filter_movies())
        
        self.reset_btn = tk.Button(filter_frame, text="Сбросить", command=self.reset_filters)
        self.reset_btn.pack(side=tk.LEFT, padx=20)
        
        # Рамка для списка фильмов
        list_frame = tk.LabelFrame(self.root, text="Список фильмов", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Настройка заголовков
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Название", width=250)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=80, anchor="center")
        self.tree.column("Рейтинг", width=80, anchor="center")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка удаления
        self.delete_btn = tk.Button(self.root, text="Удалить выбранный фильм", command=self.delete_movie, bg="lightcoral")
        self.delete_btn.pack(pady=10)
        
        # Статусная строка
        self.status = tk.Label(self.root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def add_movie(self):
        """Добавление фильма"""
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()
        
        # Проверка названия
        if not title:
            messagebox.showwarning("Ошибка", "Введите название фильма!")
            return
        
        # Проверка жанра
        if not genre:
            messagebox.showwarning("Ошибка", "Введите жанр!")
            return
        
        # Проверка года
        if not year:
            messagebox.showwarning("Ошибка", "Введите год выпуска!")
            return
        
        try:
            year = int(year)
            if year < 1888 or year > 2026:
                messagebox.showwarning("Ошибка", "Год должен быть от 1888 до 2026!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Год должен быть числом!")
            return
        
        # Проверка рейтинга
        if not rating:
            messagebox.showwarning("Ошибка", "Введите рейтинг!")
            return
        
        try:
            rating = float(rating)
            if rating < 0 or rating > 10:
                messagebox.showwarning("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Рейтинг должен быть числом!")
            return
        
        # Проверка на дубликат
        for m in self.movies:
            if m["title"].lower() == title.lower():
                messagebox.showwarning("Ошибка", "Такой фильм уже есть!")
                return
        
        # Добавление
        movie = {
            "title": title,
            "genre": genre,
            "year": year,
            "rating": rating
        }
        
        self.movies.append(movie)
        self.save_movies()
        self.refresh_table()
        self.clear_inputs()
        
        self.status.config(text=f"Добавлен: {title}")
        self.root.after(2000, lambda: self.status.config(text="Готов"))
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления!")
            return
        
        # Получаем название
        values = self.tree.item(selected[0])["values"]
        title = values[0]
        
        # Подтверждение
        if messagebox.askyesno("Подтверждение", f"Удалить фильм '{title}'?"):
            self.movies = [m for m in self.movies if m["title"] != title]
            self.save_movies()
            self.refresh_table()
            self.status.config(text=f"Удален: {title}")
            self.root.after(2000, lambda: self.status.config(text="Готов"))
    
    def filter_movies(self):
        """Фильтрация фильмов"""
        genre_filter = self.filter_genre.get().strip().lower()
        year_filter = self.filter_year.get().strip()
        
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Применяем фильтры
        filtered = self.movies.copy()
        
        if genre_filter:
            filtered = [m for m in filtered if genre_filter in m["genre"].lower()]
        
        if year_filter:
            try:
                year_int = int(year_filter)
                filtered = [m for m in filtered if m["year"] == year_int]
            except:
                pass
        
        # Отображаем
        for movie in filtered:
            self.tree.insert("", tk.END, values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))
        
        # Обновляем статус
        if genre_filter or year_filter:
            self.status.config(text=f"Показано: {len(filtered)} из {len(self.movies)}")
        else:
            self.status.config(text="Готов")
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_genre.delete(0, tk.END)
        self.filter_year.delete(0, tk.END)
        self.refresh_table()
        self.status.config(text="Фильтры сброшены")
        self.root.after(2000, lambda: self.status.config(text="Готов"))
    
    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение
        for movie in self.movies:
            self.tree.insert("", tk.END, values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))
    
    def clear_inputs(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        self.title_entry.focus()
    
    def load_movies(self):
        """Загрузка из JSON"""
        if os.path.exists(MOVIES_FILE):
            try:
                with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_movies(self):
        """Сохранение в JSON"""
        try:
            with open(MOVIES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")


# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()