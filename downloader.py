import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from pytube import YouTube
from pytubefix.cli import on_progress
from slugify import slugify  # pip install python-slugify
import os
from pathlib import Path
import subprocess
import sys
import threading

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader do zelflas")
        self.root.geometry("500x200")

        tk.Label(root, text="URL do vídeo:").pack(pady=5)
        self.entry_url = tk.Entry(root, width=60)
        self.entry_url.pack()

        tk.Label(root, text="Pasta destino:").pack(pady=5)
        frame_destino = tk.Frame(root)
        self.entry_destino = tk.Entry(frame_destino, width=45)
        self.entry_destino.pack(side=tk.LEFT, padx=5)
        btn_destino = tk.Button(frame_destino, text="Escolher", command=self.escolher_pasta)
        btn_destino.pack(side=tk.LEFT)
        frame_destino.pack()

        self.btn_download = tk.Button(root, text="Baixar Vídeo", command=self.iniciar_download)
        self.btn_download.pack(pady=20)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack()

        # Define pasta padrão Vídeos do usuário
        self.entry_destino.insert(0, str(Path.home() / "Videos"))

    def escolher_pasta(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_destino.delete(0, tk.END)
            self.entry_destino.insert(0, folder)

    def iniciar_download(self):
        url = self.entry_url.get().strip()
        destino = Path(self.entry_destino.get().strip())

        if not url:
            messagebox.showerror("Erro", "Digite a URL do vídeo.")
            return
        if not destino.exists():
            messagebox.showerror("Erro", "A pasta destino não existe.")
            return

        self.btn_download.config(state=tk.DISABLED)
        self.status_label.config(text="Obtendo informações do vídeo...")

        # Download em thread pra não travar GUI
        threading.Thread(target=self.baixar_video, args=(url, destino), daemon=True).start()

    def baixar_video(self, url, destino):
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
        except Exception as e:
            self.mostrar_erro(f"Erro ao acessar o vídeo:\n{e}")
            return

        try:
            video_streams = yt.streams.filter(
                adaptive=True, only_video=True, file_extension='mp4'
            ).order_by('resolution').desc()

            resolucoes = []
            for stream in video_streams:
                r = stream.resolution
                if r and r not in resolucoes:
                    resolucoes.append(r)

            if not resolucoes:
                self.mostrar_erro("Nenhuma resolução disponível.")
                return

            # Pergunta a resolução via diálogo simples na GUI
            resolucao_escolhida = self.escolher_resolucao(resolucoes)
            if not resolucao_escolhida:
                self.mostrar_erro("Nenhuma resolução escolhida.")
                return

            video_stream = yt.streams.filter(
                res=resolucao_escolhida, only_video=True, file_extension='mp4'
            ).first()
            audio_stream = yt.streams.filter(
                only_audio=True, file_extension='mp4'
            ).order_by('abr').desc().first()

            if not video_stream or not audio_stream:
                self.mostrar_erro("Streams de vídeo ou áudio não encontrados.")
                return

            safe_title = slugify(yt.title)
            video_path = destino / f"{yt.video_id}_video.mp4"
            audio_path = destino / f"{yt.video_id}_audio.mp4"
            output_path = destino / f"{safe_title}_{resolucao_escolhida}.mp4"

            self.atualizar_status(f"Baixando vídeo ({resolucao_escolhida})...")
            video_stream.download(output_path=destino, filename=video_path.name)

            self.atualizar_status("Baixando áudio...")
            audio_stream.download(output_path=destino, filename=audio_path.name)

            if not video_path.exists() or video_path.stat().st_size == 0:
                self.mostrar_erro("Vídeo não foi baixado corretamente.")
                return
            if not audio_path.exists() or audio_path.stat().st_size == 0:
                self.mostrar_erro("Áudio não foi baixado corretamente.")
                return

            self.atualizar_status("Mesclando vídeo e áudio com FFmpeg...")

            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                str(output_path)
            ]

            proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode != 0:
                self.mostrar_erro("Erro ao mesclar vídeo e áudio com FFmpeg.")
                return

            # Remove arquivos temporários
            video_path.unlink()
            audio_path.unlink()

            self.atualizar_status(f"✅ Vídeo final salvo em:\n{output_path}")
        except Exception as e:
            self.mostrar_erro(f"Erro inesperado:\n{e}")
        finally:
            self.btn_download.config(state=tk.NORMAL)

    def escolher_resolucao(self, resolucoes):
        # Diálogo simples para escolher resolução (último argumento: title)
        escolha = simpledialog.askstring(
            "Escolha a resolução",
            "Resoluções disponíveis:\n" + "\n".join(f"{i+1} - {r}" for i, r in enumerate(resolucoes)) + "\n\nDigite o número da resolução desejada:",
            parent=self.root
        )
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(resolucoes):
                return resolucoes[idx]
        except:
            pass
        return None

    def mostrar_erro(self, msg):
        self.atualizar_status("")
        messagebox.showerror("Erro", msg)
        self.btn_download.config(state=tk.NORMAL)

    def atualizar_status(self, msg):
        self.status_label.config(text=msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
