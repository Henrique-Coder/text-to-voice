from base64 import b64decode
from os import system as cmd, remove, path, makedirs, environ
from time import sleep
from tkinter import Tk, filedialog

from colorama import init as color_init, Fore as cFore
from gtts import gTTS
from mutagen.mp3 import MP3
from pygame import init as pyg_init, mixer as pyg_mixer, quit as pyg_quit
from yaml import safe_load

from main_assets import default_settings, favicon_ico_base64, explorer_ico_base64


# Limpa a tela do terminal
cmd('cls || clear')

# Habilita cores no terminal
color_init(autoreset=True)

# Cria a pasta do programa caso ela não exista
userprofile_name = environ['userprofile']
app_dir = f'{userprofile_name}\\AppData\Local\\Text-to-Voice'
makedirs(f'{app_dir}\\assets', exist_ok=True)

# Cria o arquivo de configurações caso ele não exista
if not path.exists('settings.yaml'):
    with open('settings.yaml', 'w') as f:
        f.write(default_settings)

# Cria o(s) arquivo(s) de icone(s) caso ele(s) não exista(m)
favicon_ico = f'{app_dir}\\favicon.ico'
if not path.exists(favicon_ico):
    with open(favicon_ico, 'wb') as f:
        favicon_ico_bytes = b64decode(favicon_ico_base64)
        f.write(favicon_ico_bytes)

explorer_ico = f'{app_dir}\\assets\\explorer.ico'
if not path.exists(explorer_ico):
    with open(explorer_ico, 'wb') as f:
        explorer_icon_bytes = b64decode(explorer_ico_base64)
        f.write(explorer_icon_bytes)

# Carrega as configurações do arquivo YAML
with open('settings.yaml', 'r') as f:
    settings = safe_load(f)

# Configurações de saída de arquivo
output_settings = settings['output_file']
language = output_settings.get('language', 'pt-br')
voice_region = output_settings.get('voice_region', 'com.br')
audio_speed = output_settings.get('audio_speed', 1.0)
audio_bitrate = output_settings.get('audio_bitrate', 128)

# Configurações de reprodução automática
autoplay_settings = settings['autoplay_on_finish']
autoplay_mode = autoplay_settings.get('mode', True)
autoplay_delay = autoplay_settings.get('autoplay_on_finish_delay', 1)

# Configurações de exclusão do arquivo de áudio
delete_settings = settings['delete_audiofile_on_finish']
delete_mode = delete_settings.get('mode', False)
delete_delay = delete_settings.get('delete_on_finish_delay', 2)

# Inicializa a janela Tkinter e oculta-a
root = Tk()
root.withdraw()

# Define o ícone da janela
root.iconbitmap(explorer_ico)

# Abre uma janela de diálogo para selecionar o arquivo de entrada
file_path = filedialog.askopenfilename(title='Selecione um arquivo de texto para criar um áudio',
                                       filetypes=[('Arquivo de Texto', '*.txt')])

# Obtém o diretório do arquivo de entrada selecionado
dir_path, file_name = path.split(file_path)
file_name_without_extension = path.splitext(file_name)[0]

# Lê o conteúdo do arquivo de entrada selecionado
with open(file_path, 'r') as f:
    text = f.read()

# Cria o objeto gTTS
tts = gTTS(text, lang=language, tld=voice_region, slow=False)

# Define o nome do arquivo de saída final e salva o arquivo de áudio
original_file = path.join(dir_path, f'{file_name_without_extension}_default.mp3')
output_file = path.join(dir_path, f'{file_name_without_extension}_speed-{audio_speed}x.mp3')
tts.save(original_file)

# Acelera o áudio caso a velocidade seja diferente de 1x
if audio_speed not in [1, 1.0, 1.00]:
    cmd(f'ffmpeg -y -i {original_file} -vn -filter:a "atempo={audio_speed}" -codec:a libmp3lame -b:a {audio_bitrate}k -map_metadata -1 -preset ultrafast {output_file} -hide_banner -loglevel quiet')
    remove(original_file)

# Reproduz o áudio com o pygame caso o modo de reprodução automática esteja ativado
if autoplay_mode:
    # Setando a variável output_file para original_file caso a velocidade seja 1x
    if audio_speed in [1, 1.0, 1.00, 1.000]:
        output_file = original_file

    # Inicializa a biblioteca pygame, carrega o arquivo de áudio e reproduz o áudio com um delay
    pyg_init()
    pyg_mixer.music.load(output_file)
    sleep(autoplay_delay)
    pyg_mixer.music.play()

    # Define a posição inicial da reprodução do áudio
    start_pos = pyg_mixer.music.get_pos()

    # Obtém a duração do áudio em segundos
    audio = MP3(output_file)
    duration_in_secs = int(audio.info.length)

    # Espera a reprodução completa do áudio e finaliza a biblioteca pygame
    while pyg_mixer.music.get_busy():
        current_pos = pyg_mixer.music.get_pos()
        print(f'{cFore.LIGHTWHITE_EX}A reprodução finalizará em {cFore.LIGHTYELLOW_EX}{duration_in_secs - round((current_pos - start_pos) / 1000)}' + f' {cFore.LIGHTWHITE_EX}segundo(s)', end='\r')
        sleep(1)

    # Finaliza a biblioteca pygame
    pyg_quit()

    # Exclui o arquivo de audio caso o modo de exclusao esteja ativado
    if delete_mode:
        sleep(delete_delay)
        remove(output_file)

# Finaliza o programa
exit()
