import sys

POSITION_INDEX = 0
COLOR_INDEX = 1
GAP_INDEX = 2

def get_w_and_h(grid):
    return (len(grid[0])-2)//3,(len(grid)-2)//3

def place_square(grid):
    w,h = get_w_and_h(grid)
    for i in range(3*h+2):
        for j in range(3*w+2):
            if i == h and j >= w+1 and j <= 2*w:
                grid[i][j] = "--"
            elif i > h and i < 2*h+1 and j == w:
                grid[i][j] = " |"
            elif i > h and i < 2*h+1 and j == 2*w+1:
                grid[i][j] = "| "
            elif i == 2*h+1 and j >= w+1 and j <= 2*w:
                grid[i][j] = "--"

def center_corner(grid):
    w,h = get_w_and_h(grid)
    
    

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
            x,y = int(coordinate[0]),int(coordinate[1])
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
            x,y = y + shape[GAP_INDEX][1],x + shape[GAP_INDEX][0] #Inversion de l'axe x et y
            if(grid[x][y] != "  "):
                grid[x][y] = f"\x1b[{shape[COLOR_INDEX]}mXX\x1b[0m"
            else:
                grid[x][y] = f"\x1b[{shape[COLOR_INDEX]}m{nb_shapes+1} \x1b[0m"
        nb_shapes += 1
    return grid

def setup_tetraminos(tetraminos,grid):
    """
    \x1b[’ + code_couleur + ’m’ + texte + ’\x1b[0m
    """
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
    if clockwise :
        for i in range(len(tetramino[POSITION_INDEX])):
            x,y = tetramino[POSITION_INDEX][i][0],tetramino[POSITION_INDEX][i][1]
            tetramino[POSITION_INDEX][i] = (-y,x)
    else:
        for i in range(len(tetramino[POSITION_INDEX])):
            x,y = tetramino[POSITION_INDEX][i][0],tetramino[POSITION_INDEX][i][1]
            tetramino[POSITION_INDEX][i] = (y,-x)
    return tetramino
    

def display_grid(grid):
    for i in range(len(grid)) : 
        for j in range(len(grid[0])):
            print(grid[i][j],end="")
        print()

def display_tetra(grid):
    for line in grid :
        print(line)

def check_move(tetramino, grid):
    is_valid = True
    if tetramino[GAP_INDEX] != (0,0) :
        for x,y in tetramino[0]:
            x,y = y + tetramino[GAP_INDEX][1],x + tetramino[GAP_INDEX][0]
            if grid[x][y] != "  ":
                is_valid = False
    return is_valid

def remplire(grid):
    w,h = get_w_and_h(grid)
    tetraminos = []
    shape = []
    pos = []
    for i in range(len(grid)) :
        for j in range(len(grid[0])):
            if (j > w and j < 2*w+1 and i > h and i < 2*h+1) :
                pos.append((j,i))
    shape.append(pos)
    shape.append('0;37;44')
    shape.append((0, 0))
    tetraminos.append(shape)
    place_tetraminos(tetraminos,grid)


def check_win(grid):
    win = True
    w,h = get_w_and_h(grid)
    somme = 0
    for i in range(len(grid)) :
        for j in range(len(grid[0])):
            if (j > w and j < 2*w+1 and i > h and i < 2*h+1) and grid[i][j] != "  ":
                somme += 1             
    return somme == w*h
    

def main():
    carte = sys.argv[1]
    size, tetraminos = import_card(carte)
    grid = create_grid(5,7)
    #setup_tetraminos(tetraminos,grid)
    #display_grid(grid)
    remplire(grid)
    display_grid(grid)
    print(check_win(grid))

if __name__ == "__main__":
    main()