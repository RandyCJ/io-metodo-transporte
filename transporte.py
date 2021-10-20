import sys 
import os
from sympy import *
from sympy.solvers.solveset import linsolve
from itertools import chain
import copy
import sympy

asignaciones_resueltas = []

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
                lista_datos = list(map(Rational, lista_datos))
                
                if contador == 0:    
                    oferta = lista_datos
                elif contador == 1:
                    demanda = lista_datos
                else:
                    matriz.append([lista_datos, [0 for x in range(0, len(lista_datos))], ["-" for x in range(0, len(lista_datos))]])
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
    nombre_archivo += "_solucion.txt"
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
    nombre_archivo += "_solucion.txt"
    try:
        with open(nombre_archivo,"w") as archivo:
            archivo.write("")

        archivo.close()
    except:
        print("\nNo se pudo crear o abrir el archivo\n")

def escribir_matriz_costos(matriz, nombre_archivo):
    """ Escribe en el archivo la matriz de costos
            E: la matriz, el nombre del archivo
            S: N/A
    """
    matriz_costos = obtener_tipo_matriz(matriz, 0)
    matriz_texto = matriz_a_texto(matriz_costos)
    escribir_archivo(nombre_archivo, "Matriz de costos")
    escribir_archivo(nombre_archivo, matriz_texto)

def escribir_entrante_saliente(v_entrante, v_saliente, nombre_archivo):
    """ Escribe en el archivo la variable entrante y saliente
            E: recibe una tupla con las posiciones de la entrante y saliente, y el nombre del archivo
            S: N/A
    """

    entrante = "Variable entrante: U" + str(v_entrante[1] + 1) + "V" + str(v_entrante[2] + 1)
    saliente = "Variable saliente: U" + str(v_saliente[1] + 1) + "V" + str(v_saliente[2] + 1)

    if v_entrante[0] == 0:
        saliente += "\nHay solucion multiple"
    escribir_archivo(nombre_archivo, entrante + "\n" + saliente)

def escribir_matriz_indices(matriz, variables, nombre_archivo):
    """ Escribe en el archivo la matriz de indices
            E: recibe la matriz, las variables y el nombre del archivo
            S: N/A
    """
    matriz_indices = obtener_tipo_matriz(matriz, 2)
    
    i = 0
    while i < len(matriz_indices):
        matriz_indices[i] = ["U" + str(i+1) + " = " + str(variables[0][i])] + matriz_indices[i]
        i += 1

    variables[1] = [" "] + variables[1]

    i = 1
    while i < len(variables[1]):
        variables[1][i] = "V" + str(i) + " = " + str(variables[1][i])
        i += 1
    
    matriz_indices = [variables[1]] + matriz_indices
    
    matriz_texto = matriz_a_texto(matriz_indices)
    escribir_archivo(nombre_archivo, "Matriz de indices")
    escribir_archivo(nombre_archivo, matriz_texto)

def escribir_matriz_solucion(matriz, nombre_archivo):
    """ Escribe la matriz de asignacion y el costo
            E: recibe la matriz y el nombre del archivo
            S: N/A
    """
    matriz_asignacion = obtener_tipo_matriz(matriz, 1)
    matriz_texto = matriz_a_texto(matriz_asignacion)
    escribir_archivo(nombre_archivo, "Matriz de asignacion")
    escribir_archivo(nombre_archivo, matriz_texto)
    escribir_archivo(nombre_archivo, "Costo total: " + str(obtener_costo_total(matriz)))

def obtener_tipo_matriz(matriz, tipo):
    """ Obtiene la matriz deseada, sea de costos o indicadores
            E: recibe la matriz y el tipo de matriz que quiere recibir
            S: retorna la matriz deseada
        con 0: matriz de costos
        con 1: matriz de asignaciones
        con 2: matriz de indices
    """
    encabezado = []
    nueva_matriz = []
    encabezado.append(" ")
    i = 0
    if tipo != 2:
        while i < len(matriz[0][0]):
            encabezado.append("D" + str(i+1))
            i += 1
    if tipo == 0:
        encabezado.append("Oferta")
    if tipo != 2:
        nueva_matriz.append(encabezado)

    i = 0
    fila = []
    for matrices in matriz[:-1]:
        if tipo != 2:
            fila.append("O" + str(i+1))
        fila += matrices[tipo]
        if tipo == 0:
            fila.append(matrices[-1])
        nueva_matriz.append(fila)
        fila = []
        i += 1
    
    if tipo == 0:
        demanda = ["Demanda"]
        demanda += matriz[-1] + [" "]
        nueva_matriz.append(demanda)

    return nueva_matriz

def obtener_matriz_indices_IC(indices_IC):
    """ Crea una matriz con encabezado y los indices IC
            E: recibe la matriz con los indicadores IC
            S: retorna la matriz creada con los encabezados y los indices IC
    """
    #O y D para la tabla de indices
    encabezado = [" "]
    for n in range(0, len(indices_IC[0])):
        encabezado.append("D" + str(n+1))
    for n in range(0, len(indices_IC)):
        indices_IC[n] = ["O" + str(n+1)] + indices_IC[n]
    indices_IC = [encabezado] + indices_IC
    return indices_IC

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
    """ Calcula el costo mínimo de la matriz de asignaciones recibida
            E: la matriz
            S: retorna el costo minimo
    """
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
    """ Equilibra la matriz añadiendo fila o columna con ceros para cuando la demanda y oferta no sean iguales
            E: recibe la matriz a equilibrar
            S: retorna la matriz ya equilibrada
    """
    diferencia = matriz[1][0] - matriz[1][1]

    if diferencia == 0:
        return matriz[0]
    
    if diferencia > 0: #si la demanda es mayor que la oferta
        ofertas = matriz[0].pop(-1)
        largo_costos = len(matriz[0][0][0])
        matriz[0].append([[Rational(0) for x in range(0, largo_costos)], [0 for x in range(0, largo_costos)], ["" for x in range(0, largo_costos)], abs(diferencia)])
        matriz[0].append(ofertas)
    else:
        for listas in matriz[0][:-1]:
            for lista in listas[:-1]:
                if lista[0] == "-":
                    lista.append("-")
                else:
                    lista.append(Rational(0))
        matriz[0][-1].append(abs(diferencia))
    return matriz[0]

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
        matriz[i][-1] = Rational(0)
        matriz[-1][j] -= oferta    
    else:
        matriz[i][1][j] = demanda
        matriz[i][-1] -= demanda
        matriz[-1][j] = Rational(0)

    j2 = j
    if matriz[i][-1] == 0: #si la oferta es 0, se ponen todos los ceros de esa fila como -
        j = 0
        while j < len(matriz[0][0]):
            if matriz[i][1][j] == 0:
                matriz[i][1][j] = "-"
            j += 1
    if matriz[-1][j2] == 0: #si la demanda es 0, se ponen todos los de esa columna como -
        i = 0
        while i < len(matriz)-1:
            if matriz[i][1][j2] == 0:
                matriz[i][1][j2] = "-"
            i += 1
    return matriz

def encontrar_noroeste(matriz):
    """ Encuentra la posicion de la siguiente casilla a asignar por metodo noroeste
            E: recibe la matriz
            S: retorna la posicion donde se debe asignar, 0 si ya todo fue asignado
    """
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

def encontrar_vogel(matriz):
    """Encuentra la posicion a asignar con el metodo vogel
        E: la matriz
        S: una lista con la posicion de la casilla a asignar
    """
    diferencias = []
    tmp = []
    i = 0
    j = 0
    #diferencias de las filas
    for matrices in matriz[:-1]:
        for valor in matrices[1]:
            if valor == 0:# si esta sin asignar se guarda el valor de la de costos
                tmp.append(matrices[0][j])
            j += 1
        if len(tmp) > 1:
            tmp.sort()
            diferencias.append((abs(tmp[0] - tmp[1]), i, 0))
        elif len(tmp) == 1:
            diferencias.append((-1, i, 0))
        i += 1
        j = 0
        tmp = []

    #diferencias de las columnas
    tmp = []
    i = 0
    j = 0
    while j < len(matriz[0][0]):
        while i < len(matriz)-1:
            if matriz[i][1][j] == 0:# si esta sin asignar se guarda el valor de la de costos
                tmp.append(matriz[i][0][j])
            i += 1
        if len(tmp) > 1:
            tmp.sort()
            diferencias.append((abs(tmp[0] - tmp[1]), j, 1))
        elif len(tmp) == 1:
            diferencias.append((-1, j, 1))
        tmp = []
        i = 0
        j += 1
    
    if len(diferencias) == 0:
        return 0

    diferencias.sort(reverse=True)
    mayor = diferencias[0]

    if mayor[0] != -1:
        tmp = []
        indice = 0
        if mayor[2] == 0: # si el mayor se encuentra en las filas
            for n in range(0, len(matriz[0][0])):
                if matriz[mayor[1]][1][n] == 0:
                    tmp.append(matriz[mayor[1]][0][n])
            tmp.sort()
            indice = matriz[mayor[1]][0].index(tmp[0])
            return [mayor[1], indice]
        else: #si el mayor se encuentra en las columnas
            for n in range(0, len(matriz)-1):
                if matriz[n][1][mayor[1]] == 0:
                    tmp.append(matriz[n][0][mayor[1]])
            tmp.sort()
            for n in range(0, len(matriz)-1):
                 if matriz[n][0][mayor[1]] == tmp[0]:
                     indice = n
            return [indice, mayor[1]]
    else:
        mayor2 = diferencias[1]
        if mayor[2] == 0:
            return [mayor[1], mayor2[1]]
        else:
            return [mayor2[1], mayor[1]]

def vogel(matriz):
    """ Encuentra la solución inicial por el método de Vogel
        E: la matriz con los costos, demandas y ofertas
    """
    i = encontrar_vogel(matriz)
    while i != 0:
        j = i[1]
        i = i[0]

        matriz = asignar_oferta_demanda(matriz, i, j)
        i = encontrar_vogel(matriz)
    return matriz

def mayor_costo_x_fila(matriz):
    """ Calcula la casilla con más costo por fila
            E: recibe la matriz 
            S: retorna una lista con el numero mayor de cada fila
    """
    mayores_fila = []
    for m in matriz[:-1]:
        tmp = copy.deepcopy(m[0])
        tmp.sort(reverse=True)
        for valor in tmp:
            mayores_fila.append(valor)
            break
    return mayores_fila

def mayor_costo_x_columna(matriz):
    """ Calcula la casilla con más costo por columna
            E: recibe la matriz 
            S: retorna una lista con el numero mayor de cada columna
    """

    i = 1
    j = 0
    mayores_columna = []
    while j < len(matriz[0][0]):
        mayor = matriz[0][0][j]
        while i < len(matriz)-1:
            if matriz[i][0][j] > mayor:
                mayor = matriz[i][0][j]
            i += 1
        mayores_columna.append(mayor)
        j += 1
        i = 1
    return mayores_columna

def calcular_IC(matriz, mayores_fila, mayores_columna):
    """ Calcula el IC para el metodo Russell
            E: recibe la matriz, y dos listas con los mayores por fila y columna
            S: retorna una lista con la matriz de IC y una lista con los indices solos
    """
    largo_filas = len(matriz)-1
    largo_columnas = len(matriz[0][0])
    i = 0
    j = 0
    matriz_IC = [[0 for x in range(0, largo_columnas)] for x in range(0, largo_filas)]
    indices_IC = [[0 for x in range(0, largo_columnas)] for x in range(0, largo_filas)]

    while i < largo_filas:
        while j < largo_columnas:
            matriz_IC[i][j] = (mayores_fila[i] + mayores_columna[j] - matriz[i][0][j], matriz[i][0][j], (i, j))
            indices_IC[i][j] = mayores_fila[i] + mayores_columna[j] - matriz[i][0][j]
            j += 1
        i += 1
        j = 0

    return [matriz_IC, indices_IC]

def encontrar_russell(matriz, matriz_IC):
    """ Encuentra la siguiente casilla a asignar mediante russell
            E: recibe la matriz y la matriz de indicadores, que va actualizando
            S: retorna la posicion de la casilla a asignar, y la matriz IC actualizada
    """
    
    if len(matriz_IC) == 0:
            return [0, []]
    mayor, costo, pos = matriz_IC[0]

    while matriz[pos[0]][1][pos[1]] == "-": #si el mayor elegido ya esta asignado se continua eligiendo
        matriz_IC.pop(0)
        if len(matriz_IC) == 0:
            return [0, []]
        mayor, costo, pos = matriz_IC[0]

    matriz_IC.pop(0)
    return [[pos[0], pos[1]], matriz_IC]

def russell(matriz):
    """ realiza las iteraciones de russell hasta que todo esté asignado
            E: recibe la matriz 
            S: retorna la matriz el metodo russell terminado
    """

    mayores_filas = mayor_costo_x_fila(matriz)
    mayores_columnas = mayor_costo_x_columna(matriz)

    matriz_IC, indices_IC = calcular_IC(matriz, mayores_filas, mayores_columnas)
    matriz_IC = list(chain.from_iterable(matriz_IC))
    matriz_IC.sort(key = lambda x: x[1], reverse=False)
    matriz_IC.sort(key = lambda x: x[0], reverse=True)
    i, matriz_IC = encontrar_russell(matriz, matriz_IC)
    
    while i != 0:
        matriz = asignar_oferta_demanda(matriz, i[0], i[1])
        i, matriz_IC = encontrar_russell(matriz, matriz_IC)
    
    return [matriz, indices_IC]

def verificar_optimalidad(matriz):
    """ revisa si la matriz es óptima en la matriz de indicadores
            E: recibe la matriz 
            S: retorna 0 si ya es óptima, retorna la variable entrante de la siguiente iteración si no es óptima
    """
    i = 0
    j = 0
    variables_mejorables = []

    while i < len(matriz)-1:
        while j < len(matriz[0][0]):
            valor = matriz[i][2][j]
            if isinstance(valor, sympy.Basic):
                if valor >= 0:
                    variables_mejorables.append((valor, i, j))
            j += 1
        j = 0
        i += 1
    
    variables_mejorables.sort(reverse=True)
    if len(variables_mejorables) >= 1:
        return variables_mejorables[0]
    return 0

def mas_asignados_fila_columna(matriz):
    """ Calcula la fila o columna que tenga más asignados, para calcular las U y V
            E: recibe la matriz 
            S: retorna la fila o columna con mayor asignados
    """
    
    #primero sacamos la cantidad de asignados por fila
    i = 0
    j = 0
    cuenta = 0
    asignados = []
    while i < len(matriz)-1:
        while j < len(matriz[0][0]):
            if isinstance(matriz[i][1][j], sympy.Basic):
                if matriz[i][1][j] >= 0:
                    cuenta += 1
            j += 1
        asignados.append((cuenta, i, 0)) #el cero indica que es una fila
        j = 0
        i += 1
        cuenta = 0
    
    #ahora sacamos cantidad de asignados por columna
    i = 0
    j = 0
    cuenta = 0
    while j < len(matriz[0][0]):
        while i < len(matriz) - 1:
            if isinstance(matriz[i][1][j], sympy.Basic):
                if matriz[i][1][j] >= 0:
                    cuenta += 1
            i += 1
        asignados.append((cuenta, j, 1)) # el uno indica que es una columna
        i = 0
        j += 1
        cuenta = 0

    asignados.sort(reverse=True)
    return asignados[0]

def resolver_variables(matriz, mejor_linea):
    """ Resuelve las variables U y V
            E: recibe la matriz y la mejor fila o columna
            S: retorna dos listas con las variables resueltas en orden de U y V
    """
    # se crean las variables V de las filas
    variables_lineas = []
    for n in range(0, len(matriz)-1):
        variables_lineas.append(Symbol("U" + str(n+1)))

    # se crean las variables U de las columnas
    variables_columnas = []
    for n in range(0, len(matriz[0][0])):
        variables_columnas.append(Symbol("V" + str(n+1)))

    if mejor_linea[2] == 0:
        variables_lineas[mejor_linea[1]] = 0
    else:
        variables_columnas[mejor_linea[1]] = 0
    
    ecuaciones = []
    i = 0
    j = 0
    while i < len(matriz)-1:
        while j < len(matriz[0][0]):
            if isinstance(matriz[i][1][j], sympy.Basic):
                if matriz[i][1][j] >= 0:
                    ecuacion = variables_lineas[i] + variables_columnas[j] - matriz[i][0][j]
                    ecuaciones.append(ecuacion)
            j += 1
        i += 1
        j = 0
    tupla_variables = tuple(variables_lineas) + tuple(variables_columnas)
    variables_resueltas = linsolve(ecuaciones, tupla_variables)

    #ahora guardamos en las lista los valores obtenidos
    i = 0
    while i < len(variables_lineas):
        variables_lineas[i] = variables_resueltas.args[0][i]
        i += 1
    j = 0
    while j < len(variables_columnas):
        variables_columnas[j] = variables_resueltas.args[0][i]
        i += 1
        j += 1

    return [variables_lineas, variables_columnas]

def calcular_indices(matriz, variables_u, variables_v):
    """ Calcula los indicadores para ver si es optima
            E: recibe la matriz 
            S: retorna una lista con el numero mayor de cada fila
    """

    i = 0
    j = 0
    while i < len(matriz)-1:
        while j < len(matriz[0][0]):
            if type(matriz[i][1][j]) == str:
                matriz[i][2][j] = Rational(variables_u[i]) + Rational(variables_v[j]) - matriz[i][0][j]
            j += 1
        i += 1
        j = 0
    return matriz

def mejorar_solucion(matriz):
    """ Resuelve las variables y calcula los indicadores
            E: recibe la matriz 
            S: retorna la matriz actualizada y las variables resueltas
    """
    mejor_fila_columna = mas_asignados_fila_columna(matriz)
    variables_resueltas = resolver_variables(matriz, mejor_fila_columna)
    matriz = calcular_indices(matriz, variables_resueltas[0], variables_resueltas[1])
    return [matriz, variables_resueltas]

def obtener_variable_saliente(ciclo_asignacion):
    """ Determina que casilla es la variable saliente
            E: recibe el ciclo de asignacion, que es una lista de tuplas
            S: retorna la variable saliente, que es una tupla con la asignacion y la posicion de la casilla
    """
    i = 3
    variable_saliente = ciclo_asignacion[1]
    while i < len(ciclo_asignacion):
        if ciclo_asignacion[i][0] < variable_saliente[0]:
            variable_saliente = ciclo_asignacion[i]
        i += 2
    
    return variable_saliente

def encontrar_ciclo_asignacion(matriz, variable_entrante):
    """ Encuentra el ciclo de asignacion, eliminando filas y columnas
            E: recibe la matriz y la variable entrante
            S: retorna el ciclo de asignacion, que es una lista de tuplas con las asignacion y las posiciones de
                las casillas dentro del ciclo
    """

    largo_filas = len(matriz)-1
    largo_columnas = len(matriz[0][0])

    matriz_asignaciones = [[0 for x in range(0, largo_columnas)] for x in range(0, largo_filas)]
    matriz_asignaciones[variable_entrante[1]][variable_entrante[2]] = (-1, variable_entrante[1], variable_entrante[2]) #guardo la entrante
    i = 0
    j = 0

    #hago una copia de las asignaciones, pero guardando las posiciones
    #para asi cuando empiece a eliminar filas y columnas, no perder los indices
    while i < largo_filas:
        while j < largo_columnas:
            if isinstance(matriz[i][1][j], sympy.Basic):
                if matriz[i][1][j] >= 0:
                    matriz_asignaciones[i][j] = (matriz[i][1][j], i, j)
            j += 1
        i += 1
        j = 0
    bandera = True #cada vez que se elimina una fila o columna se coloca en True, cuando ya no hace mas termina
    while bandera: #mientras se haya eliminado una fila o columna
        bandera = False
        #se revisa las filas hasta que encuentre una con una asignacion, o no lo encuentre
        i = 0
        j = 0
        cuenta = 0
        while i < len(matriz_asignaciones):
            while j < len(matriz_asignaciones[0]):
                if type(matriz_asignaciones[i][j]) == tuple:
                    if matriz_asignaciones[i][j][1] != variable_entrante[1]:
                        cuenta += 1
                    else:
                        cuenta = 0
                        break
                j += 1
            if cuenta == 1:
                matriz_asignaciones.pop(i)
                bandera = True
                break
            i += 1
            j = 0
            cuenta = 0

        i = 0
        j = 0
        cuenta = 0
        #ahora vamos con las columnas
        while j < len(matriz_asignaciones[0]):
            while i < len(matriz_asignaciones):
                if type(matriz_asignaciones[i][j]) == tuple:
                    if matriz_asignaciones[i][j][2] != variable_entrante[2]:
                        cuenta += 1
                    else:
                        cuenta = 0
                        break
                i += 1
            if cuenta == 1:
                for linea in matriz_asignaciones:
                    linea.pop(j)
                bandera = True
                break
            j += 1
            i = 0
            cuenta = 0
    lista_asignaciones = ordenar_ciclo(matriz_asignaciones)
    return lista_asignaciones

def ordenar_ciclo(asignaciones):
    """ Ordena el ciclo de asignacion para que este en orden de sumar, restar, sumar, etc...
            E: recibe el ciclo de asignaciones
            S: retorna el ciclo ordenado
    """
    asignaciones = list(chain.from_iterable(asignaciones))
    asignaciones = [x for x in asignaciones if x != 0] #elimino los ceros
    asignaciones.sort()
    
    orden_asignacion = [asignaciones[0]]
    asignaciones.pop(0)

    i = 0
    casilla = orden_asignacion[0][1] #se iguala a la fila donde esta la entrante
    buscar_fila = True
    while len(asignaciones) != 0:
        while i < len(asignaciones):
            if buscar_fila:
                if asignaciones[i][1] == casilla:
                    orden_asignacion.append(asignaciones[i])
                    casilla = asignaciones[i][2]
                    asignaciones.pop(i)
                    i -= 1
                    buscar_fila = False
            else:
                if asignaciones[i][2] == casilla:
                    orden_asignacion.append(asignaciones[i])
                    casilla = asignaciones[i][1]
                    asignaciones.pop(i)
                    i -= 1
                    buscar_fila = True
            i += 1
        i = 0
    return orden_asignacion

def cambiar_asignacion(matriz, variable_saliente, ciclo_asignacion):
    """ cambia las asignaciones en el ciclo de asignacion
            E: recibe la matriz, la variable saliente y el ciclo de asignacion
            S: retorna la matriz ya actualizada
    """
    valor_asignacion = variable_saliente[0]
    matriz[ciclo_asignacion[0][1]][1][ciclo_asignacion[0][2]] = 0 #se coloca un cero en la entrante
    
    contador = 0
    while contador < len(ciclo_asignacion):
        v, i, j = ciclo_asignacion[contador]
        if contador % 2 == 0:
            matriz[i][1][j] += valor_asignacion
        else:
            matriz[i][1][j] -= valor_asignacion
        contador += 1
        
    #se coloca la saliente como "-"
    matriz[variable_saliente[1]][1][variable_saliente[2]] = "-"
    
    return matriz

def es_degenerada(matriz):
    """ Determina si una solucion inicial es degenerada
        osea que la cantidad de asignaciones sea menor a la suma de filas + columnas - 1
            E: recibe la matriz 
            S: True si es degenerada, False si no
    """
    asignaciones_requeridas = len(matriz)-1 + len(matriz[0][0]) - 1
    cuenta = 0
    for m in matriz[:-1]:
        for valor in m[1]:
            if isinstance(valor, sympy.Basic):
                cuenta += 1
    return cuenta != asignaciones_requeridas

def limpiar_indices(matriz):
    """ Limpia la matriz de indicadores para la siguiente iteración
            E: recibe la matriz 
            S: retorna la matriz actualizada
    """
    i = 0
    j = 0
    while i < len(matriz)-1:
        while j < len(matriz[0][0]):
            matriz[i][2][j] = "-"
            j += 1
        i += 1
        j = 0
    
    return matriz

def obtener_solucion(metodo_sol_inicial, ruta_archivo):
    """ Obtiene la solución de el archivo, realiza las iteraciones hasta solución optima
            E: recibe un entero que indica el metodo inicial y la ruta del archivo
            S: N/A
    """
    global asignaciones_resueltas
    matriz = leer_archivo(ruta_archivo)
    matriz = equilibrar_matriz(matriz)

    limpiar_archivo_solucion(ruta_archivo)
    escribir_matriz_costos(matriz, ruta_archivo)

    if metodo_sol_inicial == '1':
        matriz = esquina_noroeste(matriz)
        escribir_archivo(ruta_archivo, "\nMetodo Inicial: Esquina noroeste")
    elif metodo_sol_inicial == '2':
        matriz = vogel(matriz)
        escribir_archivo(ruta_archivo, "\nMetodo Inicial: Vogel")
    elif metodo_sol_inicial == '3':
        matriz, matriz_IC = russell(matriz)
        escribir_archivo(ruta_archivo, "\nMetodo Inicial: Russell")
        escribir_archivo(ruta_archivo, "Matriz de Indice de Costos")
        matriz_IC = obtener_matriz_indices_IC(matriz_IC)
        escribir_archivo(ruta_archivo, matriz_a_texto(matriz_IC))
    else:
        print("El metodo ingresado no es valido")
        quit()

    escribir_matriz_solucion(matriz, ruta_archivo) #matriz de asignacion inicial
    if es_degenerada(matriz):
        escribir_archivo(ruta_archivo, "No se puede continuar porque la solucion inicial es degenerada")
        print("Solucion inicial degenerada, no se puede resolver")
        quit()
    matriz, variables_resueltas = mejorar_solucion(matriz)
    escribir_matriz_indices(matriz, variables_resueltas, ruta_archivo)
    variable_entrante = verificar_optimalidad(matriz)
    matriz = limpiar_indices(matriz)
    iteracion = 1
    while variable_entrante != 0:
        variables_mejoradas = []
        ciclo_asignacion = encontrar_ciclo_asignacion(matriz, variable_entrante)
        variable_saliente = obtener_variable_saliente(ciclo_asignacion)
        escribir_entrante_saliente(variable_entrante, variable_saliente, ruta_archivo)
        matriz = cambiar_asignacion(matriz, variable_saliente, ciclo_asignacion)
        m_asig_actual = obtener_tipo_matriz(matriz, 1)
        if m_asig_actual not in asignaciones_resueltas:
            asignaciones_resueltas.append(m_asig_actual)
        else:
            escribir_archivo(ruta_archivo, "Pero la siguiente iteracion ya fue resuelta, por lo que termina aqui")
            break
        if variable_entrante[0] != 0:
            escribir_archivo(ruta_archivo, "Iteracion " + str(iteracion))
        else:
            escribir_archivo(ruta_archivo, "Iteracion extra")
        escribir_matriz_solucion(matriz, ruta_archivo)
        matriz, variables_resueltas = mejorar_solucion(matriz)
        escribir_matriz_indices(matriz, variables_resueltas, ruta_archivo)
        variable_entrante = verificar_optimalidad(matriz)
        matriz = limpiar_indices(matriz)
        iteracion += 1

    escribir_archivo(ruta_archivo, "Se encontro la optimalidad\nCosto minimo total: " + str(obtener_costo_total(matriz)))
    print("Costo minimo total: " + str(obtener_costo_total(matriz)))

def imprimir_ayuda():
    """ Imprime en consola una ayuda para correr el programa en caso de que se ejecute mal
            E: N/A
            S: N/A
    """
    print("Debe ejecutar el programa ingresando dos parámetros por consola")
    print("\nEl primero es un número indicando el método para la solución inicial")
    print("1. Esquina Noroeste")
    print("2. Vogel")
    print("3. Russell")
    print("\nEl segundo parámetro debe contener la ruta del archivo con el problema, el cual debe tener la siguiente estructura")
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