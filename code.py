#Purpose: Timer for polo
#import microcontroller
import time
import board
import digitalio
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix

# --- entradas y salidas setup ---
campana = digitalio.DigitalInOut(board.LED) #LED, A1, A2, A3, A4
campana.direction = digitalio.Direction.OUTPUT
arriba = digitalio.DigitalInOut(board.BUTTON_UP)
arriba.direction = digitalio.Direction.INPUT
arriba.pull = digitalio.Pull.UP
abajo = digitalio.DigitalInOut(board.BUTTON_DOWN)
abajo.direction = digitalio.Direction.INPUT
abajo.pull = digitalio.Pull.UP
btn_pausa = digitalio.DigitalInOut(board.A1)
btn_pausa.direction = digitalio.Direction.INPUT
btn_pausa.pull = digitalio.Pull.UP

BLINK =     True #parpadeo de los dos puntos
DEBUG =     False
PRUEBAS =   True #mas rapido para probar
WIDTH   =   64*3 #leds de todas las matrices en uso
HEIGHT  =   32*3 #leds de todas las matrices en uso

if not DEBUG:
    #font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf") #1*32x64
    #font = bitmap_font.load_font("/Roboto-Regular-78.bdf")         #4*32x64
    font = bitmap_font.load_font("/UbuntuMono-Regular-89.bdf")      #9*32x64

else:
    font = terminalio.FONT

if PRUEBAS:
    timer_etapa1	= 5 #segundos
    timer_etapa2 	= 4
    timer_etapa3 	= 3
else:
    # set the timer length por etapa
    timer_etapa1	= 60*7 #segundos
    timer_etapa2 	= 30
    timer_etapa3 	= 60*3

# --- Display setup ---
matrix = Matrix(width=WIDTH,height=HEIGHT,tile_rows=3, rotation=180, color_order='RGB')

display = matrix.display

# --- Drawing setup ---
group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red      R
color[2] = 0x00FF00  # verde    G
color[3] = 0x0000FF  # azul     B

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.root_group = group
clock_label = Label(font)
clock_label.color = color[0]   #en negro para que no se vea nada
clock_label.text = "0:00" #aca lo que va a aparece para que lo centre
bbx, bby, bbwidth, bbh = clock_label.bounding_box
clock_label.x = round(display.width / 2 - bbwidth / 2)
clock_label.y = display.height // 2 - 5 #correccion minima en y
group.append(clock_label)

def update_time(remaining_time, etapa, pausa):
    now = time.localtime()  # Get the time values we need
    # calculate remaining time in second
    seconds = remaining_time % 60
    minutes = remaining_time // 60

    if BLINK:
        colon = ":" if now[5] % 2 else "\u0020" #los segundos...
    else:
        colon = ":"
    
    clock_label.text = "{minutes:01d}{colon}{seconds:02d}".format(
        minutes=minutes, seconds=seconds, colon=colon)

    if etapa == 1:
        clock_label.color = color[1]
    elif etapa == 2:
        clock_label.color = color[2]
    elif etapa == 3:
        clock_label.color = color[3]
    
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
        print("Label x: {} y: {}".format(clock_label.x, clock_label.y))

    # decrement remaining time
    remaining_time -= 1
    if pausa == True:
        remaining_time += 1
    if remaining_time < 0:
        if etapa == 1:
            remaining_time = timer_etapa1
            etapa = 2
            campana.value = True
            time.sleep(2)
            campana.value = False
        elif etapa == 2:
            remaining_time = timer_etapa2
            etapa = 3
            campana.value = True
            time.sleep(2)
            campana.value = False
        else:
            remaining_time = timer_etapa3
            etapa = 1
            campana.value = True
            time.sleep(2)
            campana.value = False
    return remaining_time, etapa

def main():
    remaining_time = timer_etapa1 #parte en la etapa 1
    etapa = 2 #siguiente etapa
    pausa = False #para el boton de pausa

    while True:
        if not btn_pausa.value:
            pausa = not pausa
        #else:
        #    pausa = False
        if not arriba.value and abajo.value:
            #print("arriba")
            remaining_time += 5
        elif not abajo.value and arriba.value:
            #print("abajo")
            remaining_time -= 5
        elif not arriba.value and not abajo.value: #arriba y abajo al mismo tiempo = reset
            remaining_time = timer_etapa1
            etapa = 2

        remaining_time, etapa = update_time(remaining_time, etapa, pausa)
        #print("tempCpu: {:.0f} ℃".format(microcontroller.cpu.temperature))
        #print("cronoPolo on M4")
        time.sleep(1.0) #cuento segundos

if __name__ == "__main__":
    main()