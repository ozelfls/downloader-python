# Downloader do Zelflas

Aplicativo desktop simples para baixar vídeos do YouTube em diferentes resoluções, com download separado de vídeo e áudio e posterior mesclagem usando FFmpeg.

---

## Funcionalidades

- Baixa vídeos do YouTube a partir da URL fornecida.
- Permite escolher a pasta destino para salvar o vídeo.
- Lista as resoluções de vídeo disponíveis para escolha.
- Faz download separado do vídeo e do áudio.
- Mescla vídeo e áudio usando FFmpeg.
- Interface gráfica intuitiva com Tkinter.
- Barra de status e mensagens de erro amigáveis.

---

## Requisitos

- Python 3.6 ou superior
- [pytube](https://pytube.io/en/latest/)
- [pytubefix](https://github.com/ipeirotis/pytube-fix) (para callback de progresso)
- [python-slugify](https://github.com/un33k/python-slugify)
- [FFmpeg](https://ffmpeg.org/) (deve estar instalado e disponível no PATH do sistema)
- Tkinter (normalmente já vem com Python)
