import os
import subprocess
import platform
import sys
import logging
from art import tprint

class Downloader:
    def __init__(self):
        self.url_input = ""
        self.choice_p = ""
        self.choice = ""
        
        self.os_base = platform.system()
        self.os_detailed = self._get_os()

        if self.os_base == "Windows":
            self.Music_path = r"C:\Users\ARTIOM\Music"
            self.Video_path = r"C:\Users\ARTIOM\Videos"
        elif self.os_base == "Linux":
            if os.path.exists("/data/data/com.termux"):
                self.Music_path = os.path.expanduser("~/storage/shared/Download")
                self.Video_path = os.path.expanduser("~/storage/shared/Download")
            else:
                self.Music_path = os.path.expanduser("~/Downloads")
                self.Video_path = os.path.expanduser("~/Downloads")
        else:
            self.Music_path = os.getcwd()
            self.Video_path = os.getcwd()

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
        elif ch == "2":
            new_path = input("Введите новый абсолютный путь для видео: ").strip()
            if new_path:
                self.Video_path = os.path.abspath(os.path.expanduser(new_path))
                self._check_and_create_paths(self.Video_path)

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

        # Добавляем --ffmpeg-location только если запущено из скомпилированного .exe на Windows
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
            print("4 - exit")
            self.choice_p = input("Ваш выбор: ").strip()
            
            if self.choice_p == "4":
                break
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
