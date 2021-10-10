import sys 
import os

def leer_archivo(nombre_archivo):
    """ Función encargada de leer el archivo, también guarda todos los datos en un diccionario de datos
            E: string con el nombre del archivo
            S: el diccionario de datos con los datos ya guardados
    """
    contador = 0 
    oferta = []
    demanda = []
    matriz = []
    
    try:
        with open(nombre_archivo,"r") as archivo:
            for linea in archivo:
                lista_datos = linea.split(",")
                lista_datos[-1] = lista_datos[-1].replace("\n", "")
                lista_datos = list(map(int, lista_datos))
                
                if contador == 0:    
                    oferta = lista_datos
                elif contador == 1:
                    demanda = lista_datos
                else:
                    matriz.append([lista_datos, [0 for x in range(0, len(lista_datos))], ["" for x in range(0, len(lista_datos))]])
                contador += 1
        archivo.close()        
    except:
        print("\nEl archivo no se pudo abrir o no existe\n")
        quit()
    
    matriz.append(demanda)#se agrega a la matriz la demanda 
    i = 0
    for linea in matriz[:-1]: #se agregan las ofertas
        linea.append(oferta[i])
        i += 1
    
    sum_oferta = 0
    for num in oferta:
        sum_oferta += num
    
    sum_demanda = 0
    for num in demanda:
        sum_demanda += num

    return [matriz, [sum_demanda, sum_oferta]]

def escribir_archivo(nombre_archivo, texto):
    """ Función encargada de escribir texto en un archivo
            E: recibe la ruta del archivo y el texto a escribir
            S: N/A
    """
    nombre_archivo = str(nombre_archivo).replace(".txt", "")
    nombre_archivo += "_solution.txt"
    try:
        with open(nombre_archivo,"a") as archivo:
            archivo.write(texto + os.linesep)

    except:
        print("\nNo se pudo crear o abrir el archivo\n")
    
    archivo.close()

def limpiar_archivo_solucion(nombre_archivo):
    """ Limpia el archivo en caso de que tenga algo escrito
            E: ruta del archivo
            S: N/A
    """
    nombre_archivo= str(nombre_archivo).replace(".txt", "")
    nombre_archivo += "_solution.txt"
    try:
        with open(nombre_archivo,"w") as archivo:
            archivo.write("")

        archivo.close()
    except:
        print("\nNo se pudo crear o abrir el archivo\n")

def escribir_matriz_costos(matriz, nombre_archivo):
    matriz_costos = obtener_matriz_costos(matriz)
    matriz_texto = matriz_a_texto(matriz_costos)
    escribir_archivo(nombre_archivo, "Matriz de costos")
    escribir_archivo(nombre_archivo, matriz_texto)

def obtener_matriz_costos(matriz):
    """Retorna una matriz de las 3 que almacena la variable matriz
        con 0: matriz de costos
        con 1: matriz de asignaciones
        con 2: matriz de indices
        E: la matriz, el tipo de matriz deseado
        S: la matriz deseada
        """
    encabezado = []
    nueva_matriz = []
    encabezado.append(" ")
    i = 0
    while i < len(matriz[0][0]):
        encabezado.append("D" + str(i+1))
        i += 1
    encabezado.append("Oferta")
    nueva_matriz.append(encabezado)

    i = 0
    fila = []
    for matrices in matriz[:-1]:
        fila.append("O" + str(i+1))
        fila += matrices[0]
        fila.append(matrices[-1])
        nueva_matriz.append(fila)
        fila = []
        i += 1
    
    demanda = ["Demanda"]
    demanda += matriz[-1] + [" "]
    nueva_matriz.append(demanda)

    return nueva_matriz

def obtener_matriz_asignaciones(matriz):
    """Retorna una matriz de las 3 que almacena la variable matriz
        con 0: matriz de costos
        con 1: matriz de asignaciones
        con 2: matriz de indices
        E: la matriz, el tipo de matriz deseado
        S: la matriz deseada
        """
    encabezado = []
    nueva_matriz = []
    encabezado.append(" ")
    i = 0
    while i < len(matriz[0][0]):
        encabezado.append("D" + str(i+1))
        i += 1
    nueva_matriz.append(encabezado)

    i = 0
    fila = []
    for matrices in matriz[:-1]:
        fila.append("O" + str(i+1))
        fila += matrices[1]
        nueva_matriz.append(fila)
        fila = []
        i += 1

    return nueva_matriz

def matriz_a_texto(matriz):
        """ Convierte la matriz en un string legible e imprimible
            E: N/A
            S: string de la matriz
        """
        linea_string = [[str(casilla) for casilla in linea ] for linea in matriz]
        lista_posicion = [max(map(len, columna)) for columna in zip(*linea_string)]
        cambia_formato = '\t\t'.join('{{:{}}}'.format(x) for x in lista_posicion)
        tabla = [cambia_formato.format(*linea) for linea in linea_string]

        return "\n".join(tabla)

def obtener_costo_total(matriz):

    i = 0
    total = 0
    for matrices in matriz[:-1]:
        for valor in matrices[1]:
            if valor != "-":
                total += valor * matrices[0][i]
            i += 1
        i = 0
    return total

def equilibrar_matriz(matriz):
    diferencia = matriz[1][0] - matriz[1][1]

    if diferencia == 0:
        return matriz[0]
    
    if diferencia > 0: #si la demanda es mayor que la oferta
        ofertas = matriz[0].pop(-1)
        largo_costos = len(matriz[0][0][0])
        matriz[0].append([[0 for x in range(0, largo_costos)], [0 for x in range(0, largo_costos)], ["" for x in range(0, largo_costos)], abs(diferencia)])
        matriz[0].append(ofertas)
    else:
        for listas in matriz[0][:-1]:
            for lista in listas[:-1]:
                if lista[0] == "":
                    lista.append("")
                else:
                    lista.append(0)
        matriz[0][-1].append(abs(diferencia))
    return matriz[0]

def encontrar_noroeste(matriz):
    i = 0
    j = 0
    for fila in matriz[:-1]:
        for columna in fila[1]:
            if columna == 0:
                return [i, j]
            j += 1
        i += 1
        j = 0    
    return 0

def asignar_oferta_demanda(matriz, i, j):
    """ Asigna la oferta o demanda a la casilla seleccionada, hace las restas en el menor
        y coloca '-' (Sin Asignar) a las casillas donde ya no es posible asignar
        E: la matriz, la posicion de la casilla a asignar
        S: la matriz con la asignacion ya hecha
    """

    oferta = matriz[i][-1]
    demanda = matriz[-1][j]

    #se asigna 
    if oferta < demanda:
        matriz[i][1][j] = oferta
        matriz[i][-1] = 0
        matriz[-1][j] -= oferta    
    else:
        matriz[i][1][j] = demanda
        matriz[i][-1] -= demanda
        matriz[-1][j] = 0
    
    j2 = j

    if matriz[i][-1] == 0: #si la oferta es 0, se ponen todos los de esa fila como NA
        j += 1
        while j < len(matriz[0][0]):
            matriz[i][1][j] = "-"
            j += 1
    if matriz[-1][j2] == 0: #si la demanda es 0, se ponen todos los de esa columna como NA
        i += 1
        while i < len(matriz)-1:
            matriz[i][1][j2] = "-"
            i += 1

    return matriz

def esquina_noroeste(matriz):
    """ Encuentra la solución inicial por el método de la esquina noroeste
        E: la matriz con los costos, demandas y ofertas
    """
    i = encontrar_noroeste(matriz)
    while i != 0:
        j = i[1]
        i = i[0]

        matriz = asignar_oferta_demanda(matriz, i, j)
        i = encontrar_noroeste(matriz)
    return matriz

def obtener_solucion(metodo_sol_inicial, ruta_archivo):
    matriz = leer_archivo(ruta_archivo)
    matriz = equilibrar_matriz(matriz)

    limpiar_archivo_solucion(ruta_archivo)
    escribir_matriz_costos(matriz, ruta_archivo)

    #print("Matriz despues de equilibrar: " + str(matriz))

    if metodo_sol_inicial == '1':
        matriz = esquina_noroeste(matriz)
        matriz_asig = obtener_matriz_asignaciones(matriz)
        escribir_archivo(ruta_archivo, "\nMetodo Inicial: Esquina noroeste")
        escribir_archivo(ruta_archivo, matriz_a_texto(matriz_asig))
        escribir_archivo(ruta_archivo, "Costo total: " + str(obtener_costo_total(matriz)))
        
        
    elif metodo_sol_inicial == 2:
        #Vogel
        pass
    elif metodo_sol_inicial == 3:
        #Russel
        pass
    else:
        print("El metodo ingresado no es valido")
        quit()


def imprimir_ayuda():
    """ Imprime en consola una ayuda para correr el programa
            E: N/A
            S: N/A
    """
    print("Debe ejecutar el programa ingresando dos parámetros por consola")
    print("El primero es un número indicando el método para la solución inicial")
    print("1. Esquina Noroeste")
    print("2. Vogel")
    print("3. Russel")
    print("El segundo parámetro debe contener la ruta del archivo con el programa, el cual debe tener la siguiente estructura")
    print("10,15\n5,5,10\n3,2,8\n7,8,9")
    print("Siendo la primera fila para la oferta, la segunda para la demanda, y las siguientes los costos")

def principal(args):
    """ Función encargada de la ejecución del programa
            E: recibe los argumento ingresados por consola
            S: N/A
    """

    if len(args) != 3:
        imprimir_ayuda()
    else:
        obtener_solucion(args[1], args[2])
        return

principal(sys.argv)