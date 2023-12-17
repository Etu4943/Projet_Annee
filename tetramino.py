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
COMMANDS_COLOR = "38;5;152"
CHOOSE_NUMBER_COLOR = "38;5;226"
Cote = Enum("Cote",["HAUT","GAUCHE","DROITE","BAS"])


def clear_screen():
    if os.name == "posix" :
        os.system("clear")
    else:
        os.system("cls")
        
def get_w_and_h(grid):
    """
    Input :
        grid : matrice du plateau de jeu
    Return :
        Renvoie la longueur et la largeur d'origine
    """
    return (len(grid[FIRST_ELEMENT])-2)//3,(len(grid)-2)//3

def is_game_canceled(move):
    """
    Input :
        move : Un input
    Return :
        Renvoie un booleen en fonction de si le joueur à choisi d'arreter la partie
    """
    return move == "x" or move == 120

def get_colored_text(text,color):
    """
    Input :
        text : Un message texte
        color : Le code couleur désiré
    Return :
        Renvoie une le message texte formatée avec la couleur
    """
    return f"\x1b[{color}m{text}\x1b[0m"

def square_side(i,j,w,h):
    """
    Input :
        i, j : Les coordonées x,y d'où on se trouve sur la matrice
        w, h : longuer et largeur d'origine du plateau de jeu
    Return :
        Renvoie, si on est dessus, le coté du rectangle central sur lequel on est, via une énumération
    """
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
    """
    Input :
        grid : matrice du plateau de jeu
    Fonctionnement :
        Rajoute le rectangle central à la grille vierge
    Return :
        None
    """
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
    """
    Input :
        w, h : Longueur et largeur d'origine du plateau
    Return :
        Renvoie une matrice w x h composée de "  "
    """
    grid = [["  " for _ in range(3*w+2)] for _ in range(3*h+2)]
    place_square(grid)
    return grid

def import_card(file_path):
    """
    Input :
        file_path : chaine de caractère désignant le chemin d'accès de la carte de jeu
    return :
        (w,h) : Tuple contenant la longeur et la largeur d'origine (première ligne du fichier)
        shapes : Liste de tetramino composée de telle sorte : [positions, couleur, déplacement]
    """
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
    """
    Input :
        grid : matrice du plateau de jeu
    Fonctionnement :
        Vide la grille de tout élément si ce n'est le rectangle central
    Return :
        none
    """
    for i in range(len(grid)):
        for j in range(len(grid[FIRST_ELEMENT])):
            if not "|" in grid[i][j] and not "-" in grid[i][j]:
                grid[i][j] = "  "
    place_square(grid)

def place_tetraminos(tetraminos,grid):
    """
    Input :
        tetraminos : Liste comprenant tout les tetraminos
        grid : matrice du plateau de jeu
    Return :
        Renvoie la grille une fois modifiée après avoir placé les tetraminos
    """
    empty_grid(grid)
    nb_shapes = 0
    for shape in tetraminos :
        gap_x,gap_y = shape[GAP_INDEX]
        for x,y in shape[POSITION_INDEX] :
            grid[y + gap_y][x + gap_x] = get_colored_text("XX" if grid[y + gap_y][x + gap_x] != "  " else f"{nb_shapes+1} ",shape[COLOR_INDEX])
        nb_shapes += 1
    return grid

def setup_tetraminos(tetraminos,grid):
    """
    Input :
        tetraminos : Liste comprenant tout les tetraminos
        grid : matrice du plateau de jeu
    Return :
        grid : la grille modifiée via place_tetraminos()
        tetraminos : la liste de tetraminos
    """
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
    """
    Input :
        tetramino : Un tetramino de type [positions, couleur, déplacement]
        clockwise = True : Une booléen désignant si la forme doit tourner dans le sens horaire ou non
    Return :
        Renvoie la forme une fois tournée
    """
    for i in range(len(tetramino[POSITION_INDEX])):
        x,y = tetramino[POSITION_INDEX][i][X_INDEX],tetramino[POSITION_INDEX][i][Y_INDEX]
        tetramino[POSITION_INDEX][i] = (-y,x) if clockwise else (y,-x)
    return tetramino

def remove_num(text):
    """
    Input :
        text : Une chaine de caractère formatée avec une couleur
    Return :
        Renvoie la chaine de caractère ayant remplacée le numéro par des espaces
    """
    if "XX" not in text:
        index = text.find(" ") - 1
        text = list(text)
        text[index] = " "
    return ''.join(text)

def print_dashed_line(length):
    """
    Input :
        length : longeur souhaitée
    Fonctionnement :
        Imprime une ligne de "--" de longeur length
    Return :
        None
    """
    print("--" * length)

def print_commands(grid,shape,color,choosing_shape = False):
    """
    Input :
        grid : matrice du plateau de jeu
        shape : Un tetramino
        color : Un code couleur de type ab;cd;ef
        choosing_shape : un booléen signifiant si ce message s'affiche pour le choix d'une pièce ou non
    Fonctionnement :
        Affiche de manière stylisée les commandes disponibles
    Return :
        None
    """
    length = 2*len(grid[FIRST_ELEMENT])
    print(f" ╔══════╗"," " * (length-9-18),f" ╔═══╗   {get_colored_text("↑",COMMANDS_COLOR)}   ╔═══╗",sep="")
    print(f" ║{get_colored_text('CHOOSE',CHOOSE_NUMBER_COLOR)}║" if choosing_shape else f" ║{get_colored_text(f'n° {shape}',color)}  ║"," " * (length-9-18),f" ║ U ║ ╔═══╗ ║ O ║",sep="")
    print(f" ║{get_colored_text('NUMBER',CHOOSE_NUMBER_COLOR)}║" if choosing_shape else " ║      ║"," " * (length-9-18),f" ╚═══╝ ║ {get_colored_text("i",COMMANDS_COLOR)} ║ ╚═══╝",sep="")
    print(f" ║x:quit║"," " * (length-9-18),f"   ╔═══╬═══╬═══╗",sep="")
    print(f" ║v:lock║"," " * (length-9-18),f" {get_colored_text("←",COMMANDS_COLOR)} ║ {get_colored_text("j",COMMANDS_COLOR)} ║ {get_colored_text("k",COMMANDS_COLOR)} ║ {get_colored_text("l",COMMANDS_COLOR)} ║ {get_colored_text("→",COMMANDS_COLOR)}",sep="")
    print(f" ╚══════╝"," " * (length-9-18),f"   ╚═══╩═══╩═══╝",sep="")
    print(" " * (length-9),f"{get_colored_text("↓",COMMANDS_COLOR)}",sep="")

def print_grid(grid, no_number):
    """
    Input :
        grid : matrice du plateau de jeu
        no_number : Booléen selon qu'non veuille les numéros ou non
    Fonctionnement :
        Affiche le plateau de jeu
    Return :
        None
    """
    clear_screen()
    print_dashed_line(len(grid[FIRST_ELEMENT])+1)
    for i in range(len(grid)) :
        print("|",end="")
        for j in range(len(grid[FIRST_ELEMENT])):
            if no_number and "\x1b" in grid[i][j]:
                str = remove_num(grid[i][j])
                print(str, end="")
            else :
                print(grid[i][j],end="")
        print("|")
    print_dashed_line(len(grid[FIRST_ELEMENT])+1)

def check_move(tetramino, grid):
    """
    Input :
        tetramino : Un tetramino de type [positions, couleur, déplacement]
        grid : matrice du plateau de jeu
    Return :
        is_valid : Une valeur booléenne vérifiant que la pièce ne chevauceh rien d'autre
    """
    is_valid = True
    for x,y in tetramino[POSITION_INDEX] :
        x += tetramino[GAP_INDEX][X_INDEX]
        y += tetramino[GAP_INDEX][Y_INDEX]
        if "XX" in grid[y][x] :
            is_valid = False
    
    return is_valid


def check_win(grid):
    """
    Input :
        grid : matrice du plateau de jeu
    Return :
        Renvoie un booléen vérifiant que chaque case comprise dans mon rectangle centrale est remplie
    """
    w,h = get_w_and_h(grid)
    somme = 0
    for i in range(len(grid)) :
        for j in range(len(grid[FIRST_ELEMENT])):
            if (j > w and j < 2*w+1 and i > h and i < 2*h+1) and grid[i][j] != "  ":
                somme += 1             
    return somme == w * h

def is_int(choice):
    """
    Input :
        choice : un input
    Return :
        Renvoie si l'input peut être casté de type int
    """
    try:
        int(choice)
        is_ok = True
    except :
        is_ok = False
    return is_ok

def choose_shape(nb_shapes):
    """
    Input :
        nb_Shapes : Le nombre de tetramino dans le jeu
    Return :
        Renvoie le numéro de pièce choisi 
    """
    choice = getkey()
    stop_game = False
    while not is_game_canceled(choice[FIRST_ELEMENT]) and ( not is_int(choice) or int(choice) < 1 or int(choice) > nb_shapes) :
        choice = getkey()
        
    if is_game_canceled(choice[FIRST_ELEMENT]) :
        stop_game = True
        choice = choice[FIRST_ELEMENT]
    else :
        choice = int(choice)
    return choice, stop_game

def is_out_of_bounds(tetramino,gap_x,gap_y,grid):
    """
    Input :
        tetramino : Une pièce de la liste des tetraminos
        gap_X, gap_y : Un déplacement potentiel pour cette pièce
        grid : matrice du plateau de jeu
    Return :
        is_out : Un booléen désignant si la pièce serait hors-borne ou non
    """
    is_out = False
    for x,y in tetramino[POSITION_INDEX] :
        if not (0 <= x + gap_x < len(grid[FIRST_ELEMENT])) or not (0 <= y + gap_y < (len(grid))):
            is_out = True
    return is_out




def make_move(tetraminos,shape,grid):
    """
    Input :
        tetraminos : La liste des tetraminos
        shape : L'indice de la pièce en cours de déplacement
        grid : Matrice du plateau de jeu
    Fonctionnement :
        Demande en boucle les inputs gérant le déplacement jusqu'à ce que la pièce soit placée, ou la partie annulée
    Return :
        Renvoie le dernier input de l'utilisateur en fin de boucle (v si pièce placée, x si partie annulée)
    """
    tetramino = tetraminos[shape-1]
    print_commands(grid,shape,tetramino[COLOR_INDEX])
    move = getkey()[FIRST_ELEMENT]
    placed = False
    bad_emplacement = False
    while not placed and not is_game_canceled(move):
        bad_key = False
        gap = x,y = tetramino[GAP_INDEX]
        match move :
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
                if is_out_of_bounds(tetramino,*gap,grid):
                    rotate_tetramino(tetramino,False)
            case 'u' | 117:
                rotate_tetramino(tetramino,False)
                if is_out_of_bounds(tetramino,*gap,grid):
                    rotate_tetramino(tetramino)
            case 'v' | 118 :
                if check_move(tetramino,grid) :
                    placed = True
                else :
                    bad_emplacement = True
            case _ :
                bad_key = True
        if not is_out_of_bounds(tetramino,*gap,grid) and not bad_key:
            tetramino[GAP_INDEX] = gap
            place_tetraminos(tetraminos,grid)
            print_grid(grid,True)
            print_commands(grid,shape,tetramino[COLOR_INDEX])
            if bad_emplacement :
                print(get_colored_text("Verouillage impossible. Emplacement non valide.",RED))
                bad_emplacement = False
        if not placed :
            move = getkey()[FIRST_ELEMENT]
    return is_game_canceled(move)

def tour(grid,tetraminos,nb_pieces,is_first_round=False):
    """
    Input :
        grid = Matrice du plateau de jeu
        tetraminos : Liste des tetraminos
        is_first_round = False : Booleen si c'est le premier tour de jeu
    Fonctionnement :
        affichage de la grille, demande de la pièce, déplacement
    Return :
        Renvoie si le joueur souhaite continuer ou non
    """
    print_grid(grid, False)
    print_commands(grid,None,None,True)
    if not is_first_round :
        print(get_colored_text("Vous avez vérouillé l'emplacement.",GREEN))
    shape, stop_game = choose_shape(nb_pieces)
    if not stop_game:
        print_grid(grid,True)
        stop_game = make_move(tetraminos,shape,grid)
        
    return stop_game

def main():
    carte = sys.argv[1]
    os.system("MODE 0,50")
    size, tetraminos = import_card(carte)
    grid = create_grid(*size)
    nb_pieces = len(tetraminos)
    setup_tetraminos(tetraminos,grid)
    
    stop_game = tour(grid,tetraminos,nb_pieces,True)
    while not check_win(grid) and not stop_game :
        stop_game = tour(grid,tetraminos,nb_pieces)
    
    end_message = get_colored_text("Partie annulée",RED) if stop_game else get_colored_text("Vous avez résolu l'énigme du Tetramino. Félicitations !",GREEN)
    print(end_message)

if __name__ == "__main__":
    main()