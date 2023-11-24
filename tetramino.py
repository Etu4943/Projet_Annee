import sys

def create_grid(w,h):
    grid = []
    for i in range(3*h+2):
        line = []
        for j in range(3*w+2):
                if i == h and j >= w+1 and j <= 2*w:
                    line.append("--")
                elif i > h and i < 2*h+1 and j == w:
                    line.append(" |")
                elif i > h and i < 2*h+1 and j == 2*w+1:
                    line.append("| ")
                elif i == 2*h+1 and j >= w+1 and j <= 2*w:
                    line.append("--")
                else :
                    line.append("  ")
        grid.append(line)
    return grid

def import_card(file_path):
    
    with open(file_path,'r',encoding="utf-8") as file :
        board = file.readline()
        doc = file.readlines()
    size = board.strip().split(",")
    w,h = int(size[0]),int(size[1])
    shapes = []
    for line in doc :
        shape = {}
        shape["position"] = set()
        elements = line.strip().split(";")
        i = 0 
        while elements[i] != "":
            positions = elements[i][1:-1].strip().split(",")
            x,y = int(positions[0]),int(positions[1])
            shape["position"].add((x,y))
            i += 1
        shape["color"] = ";".join([i for i in elements[-3:]])
        shapes.append(shape)
    return ((w,h),shapes)

def setup_tetraminos(tetraminos,grid):
    """
    \x1b[’ + code_couleur + ’m’ + texte + ’\x1b[0m
    """
    h,w = (len(grid)-2)//3,(len(grid[0])-2)//3
    nb_shapes = 0
    for shape in tetraminos :
        new_pos = set()
        for pos in shape["position"]:
            x,y = pos[0],pos[1]
            if nb_shapes < 4 :
                x,y = pos[0] + (nb_shapes // 3)*(h+1),pos[1] + (nb_shapes % 3)*(w+1)
            elif nb_shapes == 4 :
                x,y = pos[0] + (nb_shapes // 3)*(h+1),pos[1] + 2*(w+1)
            else :
                x,y = pos[0] + ((nb_shapes+1) // 3)*(h+1),pos[1] + ((nb_shapes-2) % 3)*(w+1)
            new_pos.add((x,y))
            grid[x][y] = f"\x1b[{shape['color']}m{nb_shapes+1} \x1b[0m"
        shape["position"] = new_pos
        nb_shapes += 1
    
    

def display_grid(grid):
    for i in range(len(grid)) : 
        for j in range(len(grid[0])):
            print(grid[i][j],end="")
        print()

def main():
    carte = sys.argv[1]
    size, tetraminos = import_card(carte)
    grid = create_grid(*size)
    setup_tetraminos(tetraminos,grid)
    display_grid(grid)

if __name__ == "__main__":
    main()