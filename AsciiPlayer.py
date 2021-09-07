from os import name, system, path, remove, rmdir
from PIL import Image
from pygame import mixer
from threading import Thread
import moviepy.editor as mp
import cv2 as cv
import progressbar
import fpstimer
import sys


class AsciiPlayer:
    def __init__(self, path) -> None:
        self.preparar_directorios()
        self._path = path
        self._ascii_frames = []
        self._height = 60
        self._width = 170

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width

    @classmethod
    def preparar_directorios(cls):
        if name == 'nt':
            system('mkdir ' + path.join('files', 'output'))
        else:
            system('mkdir files')
            system('mkdir files/output')

    def verificar_archivos(self, ruta: str) -> bool:
        try:
            with open(ruta, 'r'):
                return True
        except Exception:
            return False

    def convertir_audio(self) -> None:
        if self.verificar_archivos(path.join("files", "audio.wav")):
            sys.stdout.write('El archivo de audio ya existe')
        else:
            audio = mp.VideoFileClip(self._path)
            audio.audio.write_audiofile(
                path.join("files", "audio.wav"), bitrate='320k')

    def contar_frames(self) -> int:
        video = cv.VideoCapture(self._path)
        nFrames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
        return nFrames

    def obtener_fps(self) -> float:
        video = cv.VideoCapture(self._path)
        fps = float(video.get(cv.CAP_PROP_FPS))
        return fps

    def obtener_frames(self) -> None:
        capturas = cv.VideoCapture(self._path)
        nFrame = 0
        sys.stdout.write(f'Extrayendo los frames de: {self._path}\n')
        progreso = progressbar.ProgressBar(max_value=self.contar_frames())
        progreso.start()
        while(True):
            success, frame = capturas.read()
            if success:
                """ if self.verificar_archivos(f'./files/output/frame_{nFrame}.jpg') == False:
                    cv.imwrite(f'./files/output/frame_{nFrame}.jpg', frame) """
                if self.verificar_archivos(path.join('files', 'output', 'frame_%s.jpg' % nFrame)) == False:
                    cv.imwrite(path.join('files', 'output',
                               'frame_%s.jpg' % nFrame), frame)
            else:
                break
            nFrame += 1

            progreso.update(nFrame)

        progreso.finish()
        capturas.release()

    def obtener_ascii(self) -> None:
        if self.verificar_archivos(path.join('files', 'frames.txt')):
            return
        ASCII_CHARS = [' ', ':', '!', '*', '%', '$', 'S', 'O', '&', '#', '@']

        sys.stdout.write(f'Escribiendo el archivo ASCII\n')
        progreso = progressbar.ProgressBar(max_value=self.contar_frames())
        progreso.start()
        for i in range(self.contar_frames()):
            try:
                frame = Image.open('./files/output/frame_%s.jpg' % i)
                frame = frame.resize(size=[self._width, self._height])

                frame = frame.convert('L')
                pixel_data = frame.getdata()

                new_pixel = ''.join(ASCII_CHARS[pixel//25]for pixel in pixel_data)

                count_pixels = len(new_pixel)
                img_ascii = [new_pixel[index: index + self._width]for index in range(0, count_pixels, self._width)]
                img_ascii = '\n'.join(img_ascii)

                self._ascii_frames.append(img_ascii)

                try:
                    with open(path.join("files", "frames.txt"), 'a') as txt:
                        txt.write(img_ascii)
                        txt.write('\n')
                except Exception as e:
                    sys.stdout.write(f'Ocurrio un error al abrir el archivo: {e}')

                progreso.update(i)

            except Exception as e:
                sys.stdout.write(
                    f'Ocurrio un error al formar la imagen ASCII: {e}')
        progreso.finish()

    def recuperar_txt(self) -> None:
        self._ascii_frames = [[]*k for k in range(self.contar_frames())]
        try:
            with open(path.join("files", "frames.txt"), 'r') as frames:
                for i in range(self.contar_frames()):
                    tmp = ''.join(frames.readline() for i in range(60))
                    self._ascii_frames[i] = tmp
        except Exception as e:
            sys.stdout.write(f'Ocurrio un error al abrir el archivo: {e}')

    def preparar_archivos(self):
        self.convertir_audio()
        if self.verificar_archivos(path.join("files", "frames.txt")):
            self.recuperar_txt()
        else:
            self.obtener_frames()
            self.obtener_ascii()

    def eliminar_archivos(self):
        try:
            remove(path.join('files', 'audio.wav'))
            remove(path.join('files', 'frames.txt'))
            for i in range(self.contar_frames()):
                remove(path.join('files', 'output', 'frame_%s.jpg' % (i)))
            rmdir(path.join('files', 'output'))
            rmdir('files')
        except Exception as e:
            sys.stdout.write(f'Error al eliminar los archivos: {e}')

    def reproducir_cancion(self) -> None:
        mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
        mixer.init()
        mixer.music.load(path.join("files", "audio.wav"))
        mixer.music.play()

    def reproducir_frames(self) -> None:
        system('mode %s, %s' % (self._width, self._height))
        timer = fpstimer.FPSTimer(self.obtener_fps())
        for i in range(self.contar_frames()):
            sys.stdout.write(self._ascii_frames[i])
            timer.sleep()

    def player(self) -> None:
        audio = Thread(target=self.reproducir_cancion())
        txt = Thread(target=self.reproducir_frames())

        audio.start()
        txt.start()

        txt.join()
        audio.join()


def main():
    system('cls' if name == 'nt' else 'clear')
    while True:
        print('ASCII Video Player'.center(50, '='))
        ruta = input(
            "Ingresa la ruta del archivo (Preferiblemente en root):").strip()
        if ruta == '':
            ruta = 'bad_apple.mp4'
        try:
            with open(ruta, 'r'):
                video = AsciiPlayer(ruta)
                break
        except Exception as e:
            print(f'Ocurrio un error: {e}')
            input()

    while True:
        system('cls' if name == 'nt' else 'clear')
        print('ASCII Video Player'.center(50, '='))
        print(f'Archivo abierto: {ruta}')
        print('[1] Preparar archivos')
        print('[2] Reproducir')
        print('[3] Eliminar archivos')
        print('[4] Opciones avanzadas')
        print('[5] Salir')
        opcion = input('>')

        if opcion == '1':
            print('Ingresa la ruta del archivo: ')
            video.preparar_archivos()

        elif opcion == '2':
            if video.verificar_archivos(path.join('files', 'frames.txt')) and video.verificar_archivos(path.join('files', 'audio.wav')):
                video.recuperar_txt()
                video.player()

        elif opcion == '3':
            print('¿Eliminar archivos? [y/n]')
            opcion = input()
            if opcion == 'y' or opcion == 'Y':
                video.eliminar_archivos()
            elif opcion == 'n' or opcion == 'N':
                pass
            else:
                print('No valido')

        elif opcion == '4':
            print('Opciones avanzadas')
            print(f'[1] Cambiar Alto (Por defecto: {video.height})')
            print(f'[2] Cambiar Ancho (Por defectoL {video.width})')
            print('[3] Regresar')
            opcion2 = input()
            if opcion2 == '1':
                video.height = int(input('Nuevo alto: '))
            elif opcion2 == '2':
                video.width = int(input('Nuevo ancho: '))
            elif opcion2 == '3':
                pass
            else:
                print('Opcion invalida')
            print('Se removera el archivo de texto, vuelve a preparar los archivos')
            try:
                remove(path.join('files', 'frames.txt'))
            except Exception as e:
                print(f'Error: {e}')
        elif opcion == '5':
            break
        else:
            print('Opcion invalida!')


if __name__ == '__main__':
    main()
    #ruta = str('./bad_apple.mp4')
    #ruta = str('./lagtrain.mp4')
    #BadApple = AsciiPlayer(ruta)
    #BadApple.width = 220

    # BadApple.convertir_audio()
    # BadApple.obtener_frames()
    # BadApple.obtener_ascii()
    # BadApple.recuperar_txt()

    # BadApple.player()
