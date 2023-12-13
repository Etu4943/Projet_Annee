import sys,os
from os import name as OS_NAME
from enum import Enum
from getkey import getkey

 
POSITION_INDEX = 0
COLOR_INDEX = 1
GAP_INDEX = 2
FIRST_ELEMENT = 0
X_INDEX = 0
Y_INDEX = 1
CLEAR_SCREEN = os.system("clear")
EXPECTED_MOVE = ["i","k","j","l","o","u","v"]
CLEAR_COMMAND = 'cls' if OS_NAME=='nt' else 'clear'
RED = 31
GREEN = 32
Cote = Enum("Cote",["HAUT","GAUCHE","DROITE","BAS"])


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
        board = file.readline()
        doc = file.readlines()
    size = board.strip().split(",")
    w,h = int(size[0]),int(size[1])
    shapes = []
    for line in doc :
        shape = []
        positions = []
        elements = line.strip().split(";")
        i = 0 
        while elements[i] != "":
            coordinate = elements[i][1:-1].strip().split(",")
            x,y = int(coordinate[X_INDEX]),int(coordinate[Y_INDEX])
            positions.append((x,y))
            i += 1
        shape.append(positions)
        shape.append(";".join([i for i in elements[-3:]]))
        shape.append((0,0))
        shapes.append(shape)
        
    return ((w,h),shapes)

def empty_grid(grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if not "|" in grid[i][j] and not "-" in grid[i][j]:
                grid[i][j] = "  "
    place_square(grid)

def place_tetraminos(tetraminos,grid):
    w,h = get_w_and_h(grid)
    empty_grid(grid)
    nb_shapes = 0
    for shape in tetraminos :
        for x,y in shape[POSITION_INDEX] :
            x,y = y + shape[GAP_INDEX][Y_INDEX],x + shape[GAP_INDEX][X_INDEX] #Inversion de l'axe x et y
            if(grid[x][y] != "  "):
                grid[x][y] = get_colored_text("XX",shape[COLOR_INDEX])
            else:
                grid[x][y] = get_colored_text(f"{nb_shapes+1} ",shape[COLOR_INDEX])
        nb_shapes += 1
    return grid

def setup_tetraminos(tetraminos,grid):
    w,h = get_w_and_h(grid)
    nb_shapes = 0
    for shape in tetraminos :
        if nb_shapes < 4 :
            x,y = (nb_shapes // 3)*(h+1),(nb_shapes % 3)*(w+1)
        elif nb_shapes == 4 :
            x,y = (nb_shapes // 3)*(h+1),2*(w+1)
        else :
            x,y = ((nb_shapes+1) // 3)*(h+1),((nb_shapes-2) % 3)*(w+1)
        shape[GAP_INDEX] = (y,x)
        nb_shapes += 1
    grid = place_tetraminos(tetraminos,grid)
    return grid,tetraminos



def rotate_tetramino(tetramino,clockwise = True):
    for i in range(len(tetramino[POSITION_INDEX])):
        x,y = tetramino[POSITION_INDEX][i][X_INDEX],tetramino[POSITION_INDEX][i][Y_INDEX]
        tetramino[POSITION_INDEX][i] = (-y,x) if clockwise else (y,-x)
    return tetramino
def remove_num(str):
    if "XX" not in str:
        index = str.find(" ") - 1
        str = list(str)
        str[index] = " "
    return ''.join(str)
def print_grid(grid, no_number):
    os.system(CLEAR_COMMAND)
    print("--" * (len(grid[0])+1))
    for i in range(len(grid)) :
        print("|",end="")
        for j in range(len(grid[0])):
            if not no_number and "\x1b" in grid[i][j]:
                str = remove_num(grid[i][j])
                print(str, end="")
            else :
                print(grid[i][j],end="")
        print("|")
    print("--" * (len(grid[0])+1))

def check_move(tetramino, grid):
    is_valid = True
    for x,y in tetramino[POSITION_INDEX] :
        x += tetramino[GAP_INDEX][X_INDEX]
        y += tetramino[GAP_INDEX][Y_INDEX]
        if "XX" in grid[y][x] :
            is_valid = False
    
    return is_valid


def check_win(grid):
    win = True
    w,h = get_w_and_h(grid)
    somme = 0
    for i in range(len(grid)) :
        for j in range(len(grid[0])):
            if (j > w and j < 2*w+1 and i > h and i < 2*h+1) and grid[i][j] != "  ":
                somme += 1             
    return somme == w*h

def is_int(choice):
    try:
        answer = int(choice)
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

def get_extreme_locations(tetramino):
    positions = tetramino[0]
    min_x_value = min(elem[0] for elem in positions)
    max_x_value = max(elem[0] for elem in positions)
    min_y_value = min(elem[1] for elem in positions)
    max_y_value = max(elem[1] for elem in positions)
    return min_x_value, max_x_value, min_y_value, max_y_value

def is_out_of_bounds(tetramino,grid):
    is_out = False
    gap = tetramino[GAP_INDEX]
    for x,y in tetramino[POSITION_INDEX] :
        if not (0 <= x + gap[0] < len(grid[0])) or not (0 <= y + gap[1] < (len(grid))):
            is_out = True
    return is_out

def make_move(tetraminos,shape,grid):
    tetramino = tetraminos[shape-1]
    print(f"Vous jouez avec la pièce {get_colored_text(f'n° {shape}',tetramino[COLOR_INDEX])} - (v pour verouiller l'emplacement)")
    move = getkey()
    placed = False
    bad_emplacement = False
    while not placed :
        gap = x,y = tetramino[GAP_INDEX]
        match move[0] :
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
                if is_out_of_bounds(tetramino,grid):
                    rotate_tetramino(tetramino,False)
            case 'u' | 117:
                rotate_tetramino(tetramino,False)
                if is_out_of_bounds(tetramino,grid):
                    rotate_tetramino(tetramino)
            case 'v' | 118 :
                if check_move(tetramino,grid) :
                    placed = True
                else :
                    bad_emplacement = True
            case "x" | 120:
                return "x"

        min_x,max_x,min_y,max_y = get_extreme_locations(tetramino)
        if (0 <= min_x + gap[X_INDEX] and max_x + gap[X_INDEX] < len(grid[X_INDEX])) and (0 <= min_y + gap[Y_INDEX] and max_y + gap[Y_INDEX] < len(grid) ):
            tetramino[GAP_INDEX] = gap
            place_tetraminos(tetraminos,grid)
            print_grid(grid,False)
            print(f"Vous jouez avec la pièce {get_colored_text(f'n° {shape}',tetramino[COLOR_INDEX])} - (v pour verouiller l'emplacement)")
            if bad_emplacement :
                print(get_colored_text("Verouillage impossible. Emplacement non valide.",RED))
                bad_emplacement = False
        if not placed :
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
if __name__ == "__main__":
    main()