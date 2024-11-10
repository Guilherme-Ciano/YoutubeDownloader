import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from io import BytesIO
from pytubefix import YouTube
from moviepy.editor import *
import requests
import tempfile
import os

# Diretório temporário para arquivos baixados
temp_dir = tempfile.mkdtemp()

# Função para formatar e validar a URL para o formato completo
def formatar_url(url):
    # Se for uma URL curta (https://youtu.be/...), converte para o formato completo
    if url.startswith("https://youtu.be/"):
        video_id = url.split("/")[-1]
        url = f"https://www.youtube.com/watch?v={video_id}"
    # Verifica se a URL está no formato do YouTube
    if not url.startswith("https://www.youtube.com/watch?v="):
        raise ValueError("URL inválida. Por favor, insira uma URL válida do YouTube.")
    return url

# Função para buscar a miniatura automaticamente
def fetch_thumbnail(event=None):
    url = url_entry.get()
    if not url:
        messagebox.showerror("Erro", "Insira uma URL do YouTube")
        return

    try:
        # Formata e valida a URL para o formato completo, se necessário
        url = formatar_url(url)
        global yt
        yt = YouTube(url)
        thumbnail_url = yt.thumbnail_url

        # Baixar e exibir a miniatura
        response = requests.get(thumbnail_url)
        response.raise_for_status()  # Garante que o download foi bem-sucedido
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((160, 90), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        thumbnail_label.config(image=img_tk)
        thumbnail_label.image = img_tk  # Manter referência da imagem
        download_button.config(state=tk.NORMAL)

    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível carregar a miniatura: {e}")

# Função para baixar e converter o áudio
def download_audio():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Erro", "Insira uma URL do YouTube")
        return

    try:
        # Formata e valida a URL para o formato completo, se necessário
        url = formatar_url(url)
        download_button.config(state=tk.DISABLED, text="Baixando...")
        
        # Baixar o vídeo do YouTube
        yt.streams.get_lowest_resolution().download(output_path=temp_dir, filename="temp_video.mp4")
        video_file_path = os.path.join(temp_dir, "temp_video.mp4")

        print("chegou aqui")
        
        # Converter para MP3
        audio_file_path = os.path.join(temp_dir, "audio.mp3")
        video_clip = AudioFileClip(video_file_path)
        video_clip.write_audiofile(audio_file_path, codec="mp3")
        video_clip.close()
        
        # Apagar o vídeo temporário
        os.remove(video_file_path)

        # Escolher o local de download
        save_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
        if save_path:
            os.rename(audio_file_path, save_path)
            messagebox.showinfo("Sucesso", f"Áudio baixado com sucesso em {save_path}")
        else:
            os.remove(audio_file_path)

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    finally:
        download_button.config(state=tk.NORMAL, text="Baixar Áudio MP3")

        url_entry.delete(0, tk.END)  # Limpa o campo de URL
        thumbnail_label.config(image='')  # Limpa a miniatura
        thumbnail_label.image = None  # Limpa a referência da imagem

# Configuração da janela principal
root = tk.Tk()
root.title("YouTube para MP3")
root.geometry("420x350")
root.configure(bg="#282C34")

# Estilos
FONT = ("Arial", 12)
BG_COLOR = "#282C34"
FG_COLOR = "#ABB2BF"
BUTTON_BG = "#61AFEF"
BUTTON_FG = "#FFFFFF"
ENTRY_BG = "#3B4048"
ENTRY_FG = "#ABB2BF"

# Label para o título
title_label = tk.Label(root, text="Conversor YouTube para MP3", font=("Arial", 16, "bold"), bg=BG_COLOR, fg="#E06C75")
title_label.pack(pady=10)

# Frame para o campo de entrada
input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(pady=5)

url_label = tk.Label(input_frame, text="URL do vídeo no YouTube:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

url_entry = tk.Entry(input_frame, width=40, font=FONT, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
url_entry.grid(row=1, column=0, padx=5, pady=5)
url_entry.bind("<Return>", fetch_thumbnail)  # Busca automática ao pressionar Enter

# Botão para buscar miniatura (oculto)
thumbnail_button = tk.Button(input_frame, text="Buscar Miniatura", command=fetch_thumbnail, font=FONT)

# Exibição da miniatura
thumbnail_label = tk.Label(root, bg=BG_COLOR)
thumbnail_label.pack(pady=10)

# Botão para baixar o áudio
download_button = tk.Button(root, text="Baixar Áudio MP3", font=FONT, bg=BUTTON_BG, fg=BUTTON_FG, command=download_audio, state=tk.DISABLED)
download_button.pack(pady=10)

# Limpeza do diretório temporário ao fechar a aplicação
def on_closing():
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
