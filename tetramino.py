###########################################
#                                         #
#               Tetraminos                #
#        INFO-106 : Projet d'info.        #
#        Projet : Decembre 2023           #
#        Auteur : Clément Potier          #
#        Matricule : 000540561            #
#                                         #
###########################################

__author__ = "Potier Clément, mat.000540561"

import sys,os
from enum import Enum
from getkey import getkey

POSITION_INDEX = 0
COLOR_INDEX = 1
GAP_INDEX = 2
FIRST_ELEMENT = 0
X_INDEX = 0
Y_INDEX = 1
RED = 31
GREEN = 32
INITIAL_GAP = (0,0)
Cote = Enum("Cote",["HAUT","GAUCHE","DROITE","BAS"])


def clear_screen():
    if os.name == "posix" :
        os.system("clear")
    else:
        os.system("cls")
        
def get_w_and_h(grid):
    return (len(grid[FIRST_ELEMENT])-2)//3,(len(grid)-2)//3

def get_colored_text(text,color):
    return f"\x1b[{color}m{text}\x1b[0m"

def square_side(i,j,w,h):
    side = None
    if i == h and j >= w+1 and j <= 2*w:
        side = Cote.HAUT
    elif i > h and i < 2*h+1 and j == w:
        side = Cote.GAUCHE
    elif i > h and i < 2*h+1 and j == 2*w+1:
        side = Cote.DROITE
    elif i == 2*h+1 and j >= w+1 and j <= 2*w:
        side = Cote.BAS
    return side

def place_square(grid):
    w,h = get_w_and_h(grid)
    for i in range(3*h+2):
        for j in range(3*w+2):
            side = square_side(i,j,w,h)
            match side :
                case Cote.HAUT :
                    grid[i][j] = "--"
                case Cote.GAUCHE :
                    grid[i][j] = " |"
                case Cote.DROITE :
                    grid[i][j] = "| "
                case Cote.BAS :
                    grid[i][j] = "--"
                case _ :
                    None

def create_grid(w,h):
    grid = [["  " for _ in range(3*w+2)] for _ in range(3*h+2)]
    place_square(grid)
    return grid

def import_card(file_path):
    with open(file_path,'r',encoding="utf-8") as file :
        first_line = file.readline()
        shapes_lines = file.readlines()
    size = first_line.strip().split(",")
    w,h = int(size[0]),int(size[1])
    shapes = []
    for line in shapes_lines :
        coordinates, color = line.strip().split(";;")
        coordinates = coordinates.strip().split(";")
        positions = [(int(coo[1]),int(coo[4])) for coo in coordinates]
        shapes.append([positions,color,INITIAL_GAP])
    return ((w,h),shapes)

def empty_grid(grid):
    for i in range(len(grid)):
        for j in range(len(grid[FIRST_ELEMENT])):
            if not "|" in grid[i][j] and not "-" in grid[i][j]:
                grid[i][j] = "  "
    place_square(grid)

def place_tetraminos(tetraminos,grid):
    empty_grid(grid)
    nb_shapes = 0
    for shape in tetraminos :
        gap_x,gap_y = shape[GAP_INDEX]
        for x,y in shape[POSITION_INDEX] :
            grid[y + gap_y][x + gap_x] = get_colored_text("XX" if grid[y + gap_y][x + gap_x] != "  " else f"{nb_shapes+1} ",shape[COLOR_INDEX])
        nb_shapes += 1
    return grid

def setup_tetraminos(tetraminos,grid):
    w,h = get_w_and_h(grid)
    for shape in tetraminos :
        nb_shapes = tetraminos.index(shape)
        if nb_shapes == 4 :
            x,y = (nb_shapes // 3)*(h+1),2*(w+1)
        else :
            x,y = ((nb_shapes+ ( 1 if nb_shapes > 4 else 0) ) // 3)*(h+1),((nb_shapes - (2 if nb_shapes > 4 else 0)) % 3)*(w+1)
        shape[GAP_INDEX] = (y,x)
        
    grid = place_tetraminos(tetraminos,grid)
    return grid,tetraminos



def rotate_tetramino(tetramino,clockwise = True):
    for i in range(len(tetramino[POSITION_INDEX])):
        x,y = tetramino[POSITION_INDEX][i][X_INDEX],tetramino[POSITION_INDEX][i][Y_INDEX]
        tetramino[POSITION_INDEX][i] = (-y,x) if clockwise else (y,-x)
    return tetramino

def remove_num(text):
    if "XX" not in text:
        index = text.find(" ") - 1
        text = list(text)
        text[index] = " "
    return ''.join(text)

def print_dashed_line(length):
    print("--" * length)

def print_commands():
    cmd =f"""
 ╔═══╗   {get_colored_text("↑",95)}   ╔═══╗
 ║ U ║ ╔═══╗ ║ O ║
 ╚═══╝ ║ {get_colored_text("i",95)} ║ ╚═══╝
   ╔═══╬═══╬═══╗
 {get_colored_text("←",92)} ║ {get_colored_text("j",92)} ║ {get_colored_text("k",93)} ║ {get_colored_text("l",96)} ║ {get_colored_text("→",96)}
   ╚═══╩═══╩═══╝
         {get_colored_text("↓",93)}
    """
    print(cmd)

def print_grid(grid, no_number):
    clear_screen()
    print_dashed_line(len(grid[FIRST_ELEMENT])+1)
    for i in range(len(grid)) :
        print("|",end="")
        for j in range(len(grid[FIRST_ELEMENT])):
            if not no_number and "\x1b" in grid[i][j]:
                str = remove_num(grid[i][j])
                print(str, end="")
            else :
                print(grid[i][j],end="")
        print("|")
    print_dashed_line(len(grid[FIRST_ELEMENT])+1)

def check_move(tetramino, grid):
    is_valid = True
    for x,y in tetramino[POSITION_INDEX] :
        x += tetramino[GAP_INDEX][X_INDEX]
        y += tetramino[GAP_INDEX][Y_INDEX]
        if "XX" in grid[y][x] :
            is_valid = False
    
    return is_valid


def check_win(grid):
    w,h = get_w_and_h(grid)
    somme = 0
    for i in range(len(grid)) :
        for j in range(len(grid[FIRST_ELEMENT])):
            if (j > w and j < 2*w+1 and i > h and i < 2*h+1) and grid[i][j] != "  ":
                somme += 1             
    return somme == w * h

def is_int(choice):
    try:
        int(choice)
        is_ok = True
    except :
        is_ok = False
    return is_ok

def choose_shape(nb_shapes):
    print("Veuillez choisir une pièce : ")
    choice = getkey()
    while  not is_int(choice) or int(choice) < 1 or int(choice) > nb_shapes :
        choice = getkey()
    return int(choice)

def is_out_of_bounds(tetramino,gap,grid):
    is_out = False
    for x,y in tetramino[POSITION_INDEX] :
        if not (0 <= x + gap[X_INDEX] < len(grid[FIRST_ELEMENT])) or not (0 <= y + gap[Y_INDEX] < (len(grid))):
            is_out = True
    return is_out

def make_move(tetraminos,shape,grid):
    tetramino = tetraminos[shape-1]
    print(f"Vous jouez avec la pièce {get_colored_text(f'n° {shape}',tetramino[COLOR_INDEX])} - (v pour verouiller l'emplacement)")
    print_commands()
    move = getkey()
    placed = False
    bad_emplacement = False
    
    while not placed :
        gap = x,y = tetramino[GAP_INDEX]
        match move[FIRST_ELEMENT] :
            case 'i' | 105 :
                gap = (x,y-1)
            case 'k' | 107:
                gap = (x,y+1)
            case 'j' | 106:
                gap = (x-1,y)
            case 'l' | 108:
                gap = (x+1,y)
            case 'o' | 111:
                rotate_tetramino(tetramino)
                if is_out_of_bounds(tetramino,gap,grid):
                    rotate_tetramino(tetramino,False)
            case 'u' | 117:
                rotate_tetramino(tetramino,False)
                if is_out_of_bounds(tetramino,gap,grid):
                    rotate_tetramino(tetramino)
            case 'v' | 118 :
                if check_move(tetramino,grid) :
                    placed = True
                else :
                    bad_emplacement = True
            case "x" | 120:
                return "x"
            case _ :
                None

        if not is_out_of_bounds(tetramino,gap,grid):
            tetramino[GAP_INDEX] = gap
            place_tetraminos(tetraminos,grid)
            print_grid(grid,False)
            print(f"Vous jouez avec la pièce {get_colored_text(f'n° {shape}',tetramino[COLOR_INDEX])} - (v pour verouiller l'emplacement)")
            if bad_emplacement :
                print(get_colored_text("Verouillage impossible. Emplacement non valide.",RED))
                bad_emplacement = False
        if not placed :
            print_commands()
            move = getkey()
    return None

def tour(grid,tetraminos,nb_pieces,is_first_round=False):
    print_grid(grid, True)
    if not is_first_round :
        print(get_colored_text("Vous avez vérouillé l'emplacement.",GREEN))
    shape = choose_shape(nb_pieces)
    print_grid(grid,False)
    move = make_move(tetraminos,shape,grid)
    return move

def main():
    carte = sys.argv[1]
    size, tetraminos = import_card(carte)
    grid = create_grid(*size)
    nb_pieces = len(tetraminos)
    setup_tetraminos(tetraminos,grid)
    
    move = tour(grid,tetraminos,nb_pieces,True)
    while not check_win(grid) and move != "x" :
        move = tour(grid,tetraminos,nb_pieces)
    
    print(get_colored_text("Vous avez résolu l'énigme du Tetramino. Félicitations !",GREEN))

if __name__ == "__main__":
    main()