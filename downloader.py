import os
import subprocess
import platform
import sys
import json
import logging
from art import tprint

class Downloader:
    def __init__(self):
        self.url_input = ""
        self.choice_p = ""
        self.choice = ""

        self.os_base = platform.system()
        self.os_detailed = self._get_os()
        self.config_file = "config.json"

        # Загружаем сохраненные пути или устанавливаем дефолтные
        self._load_config()

        self._check_and_create_paths(self.Music_path)
        self._check_and_create_paths(self.Video_path)

    def _get_os(self):
        if self.os_base == "Linux":
            try:
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=")[1].strip().strip('"')
            except:
                if os.path.exists("/data/data/com.termux"):
                    return "Android (Termux)"
                return "Linux"
        return self.os_base

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.Music_path = data.get("Music_path")
                    self.Video_path = data.get("Video_path")
                    if self.Music_path and self.Video_path:
                        return
            except Exception as e:
                logging.warning(f"Ошибка чтения конфига: {e}")

        # Дефолтные пути, если конфига нет
        if os.path.exists("/data/data/com.termux"):
            self.Music_path = "/sdcard/Download/music_video/music"
            self.Video_path = "/sdcard/Download/music_video/video"
        elif self.os_base == "Windows":
            self.Music_path = r"C:\Users\ARTIOM\Music"
            self.Video_path = r"C:\Users\ARTIOM\Videos"
        else:
            self.Music_path = os.path.expanduser("~/Downloads")
            self.Video_path = os.path.expanduser("~/Downloads")
        
        self._save_config()

    def _save_config(self):
        try:
            data = {
                "Music_path": self.Music_path,
                "Video_path": self.Video_path
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.warning(f"Ошибка сохранения конфига: {e}")

    def _check_and_create_paths(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        except Exception as e:
            logging.warning(f"Ошибка проверки пути {path}: {e}")

    def _get_binary_path(self, binary_name):
        if hasattr(sys, '_MEIPASS'):
            ext = ".exe" if self.os_base == "Windows" else ""
            local_path = os.path.join(sys._MEIPASS, f"{binary_name}{ext}")
            if os.path.exists(local_path):
                return local_path
        return binary_name

    def _ask_yes_no(self, question, default_no=True):
        prompt = " [y/N]: " if default_no else " [Y/n]: "
        ans = input(question + prompt).strip().lower()
        if not ans:
            return False if default_no else True
        return ans in ['y', 'yes', 'д', 'да']

    def _change_paths_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 50)
        print("НАСТРОЙКА ДИРЕКТОРИЙ СОХРАНЕНИЯ")
        print("=" * 50)
        print(f"1. Изменить папку МУЗЫКИ (Сейчас: {self.Music_path})")
        print(f"2. Изменить папку ВИДЕО (Сейчас: {self.Video_path})")
        print("3. Назад в главное меню")
        print("=" * 50)
        ch = input("Выберите пункт: ").strip()
        if ch == "1":
            new_path = input("Введите новый абсолютный путь для музыки: ").strip()
            if new_path:
                self.Music_path = os.path.abspath(os.path.expanduser(new_path))
                self._check_and_create_paths(self.Music_path)
                self._save_config()
        elif ch == "2":
            new_path = input("Введите новый абсолютный путь для видео: ").strip()
            if new_path:
                self.Video_path = os.path.abspath(os.path.expanduser(new_path))
                self._check_and_create_paths(self.Video_path)
                self._save_config()

    def _show_downloaded_music(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 50)
        print("СПИСОК СКАЧАННОЙ МУЗЫКИ")
        print("=" * 50)
        if os.path.exists(self.Music_path):
            files = [f for f in os.listdir(self.Music_path) if f.endswith('.mp3')]
            if files:
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file}")
            else:
                print("В папке музыки пока нет MP3 файлов.")
        else:
            print("Папка музыки не найдена или к ней нет доступа.")
        print("=" * 50)
        input("Нажмите Enter, чтобы вернуться в меню...")

    def _build_command(self, is_video, is_playlist, target_path, url):
        out_template = os.path.join(target_path, "%(title)s.%(ext)s")
        archive_path = os.path.join(target_path, ".downloaded_archive.txt")

        if is_playlist and self._ask_yes_no("Создать отдельную папку для этого плейлиста?"):
            out_template = os.path.join(target_path, "%(playlist_title)s", "%(title)s.%(ext)s")

        yt_dlp_bin = self._get_binary_path("yt-dlp")

        if is_video:
            cmd = [
                yt_dlp_bin,
                "-f", "bv*[height<=1080]+ba/b[height<=1080]",
                "--no-warnings",
                "--download-archive", archive_path,
                "-o", out_template
            ]
        else:
            cmd = [
                yt_dlp_bin,
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--no-warnings",
                "--download-archive", archive_path,
                "-o", out_template
            ]

        if hasattr(sys, '_MEIPASS'):
            ffmpeg_dir = sys._MEIPASS
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])

        cmd.append("--yes-playlist" if is_playlist else "--no-playlist")
        cmd.append(url)
        return cmd

    def start_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            tprint("MUSIC - VIDEO", font="small")

            print(f"OS: {self.os_detailed}")
            print(f"MUSIC DIR: {self.Music_path}")
            print(f"VIDEO DIR: {self.Video_path}")
            print("=" * 60)

            print("Введите:")
            print("1 - целый плейлист")
            print("2 - просто один файл")
            print("3 - Настроить папки сохранения")
            print("4 - Список скачанной музыки")
            print("5 - exit")
            self.choice_p = input("Ваш выбор: ").strip()

            if self.choice_p == "5":
                break
            if self.choice_p == "4":
                self._show_downloaded_music()
                continue
            if self.choice_p == "3":
                self._change_paths_menu()
                continue
            if self.choice_p not in ["1", "2"]:
                print("Ошибка: введите корректный пункт меню. Нажмите Enter...")
                input()
                continue

            print("\nВведите:")
            print("1 - Видео")
            print("2 - музыка")
            print("3 - exit")
            self.choice = input("Ваш выбор: ").strip()

            if self.choice == "3":
                break
            if self.choice not in ["1", "2"]:
                print("Ошибка: введите корректный пункт меню. Нажмите Enter...")
                input()
                continue

            is_video = (self.choice == "1")
            is_playlist = (self.choice_p == "1")
            target_dir = self.Video_path if is_video else self.Music_path
            media_type = "видео" if is_video else "музыку"

            self.url_input = input(f"\nВведите ссылку на {media_type}: ").strip()
            if not self.url_input:
                print("Ошибка: ссылка не может быть пустой!")
                input()
                continue

            cmd = self._build_command(is_video, is_playlist, target_dir, self.url_input)

            print(f"\nПередаю управление утилите yt-dlp...")
            try:
                result = subprocess.run(cmd)
                if result.returncode == 0:
                    print(f"\nЗагрузка завершена успешно!")
                else:
                    print("\nЗагрузка завершилась с ошибкой на стороне yt-dlp.")
            except Exception as e:
                logging.error(f"Критическая ошибка вызова subprocess: {e}")

            print("\nНажмите Enter, чтобы вернуться в меню...")
            input()

if __name__ == "__main__":
    downloader = Downloader()
    downloader.start_menu()
