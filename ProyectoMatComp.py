from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)


def permutar(lista):
    if len(lista) <= 1:
        return [lista]
    resultado = []
    for i in range(len(lista)):
        actual = lista[i]
        resto = lista[:i] + lista[i+1:]
        for p in permutar(resto):
            resultado.append([actual] + p)
    return resultado

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    n = data.get('n')
    nombres_nodos = data.get('nombres')
    modo = data.get('modo') 
    pesos_manuales = data.get('pesos', {})

    
    if not (5 <= n <= 10):
        return jsonify({'error': 'La cantidad de nodos debe estar entre 5 y 10.'}), 400

    matriz = [[0 for _ in range(n)] for _ in range(n)]

    if modo == 'aleatorio':
        for i in range(n):
            for j in range(i + 1, n):
                peso = random.randint(10, 150)
                matriz[i][j] = peso
                matriz[j][i] = peso
    else:
        for i in range(n):
            for j in range(i + 1, n):
                clave = f"{i}_{j}"
                peso = float(pesos_manuales.get(clave, 10))
                matriz[i][j] = peso
                matriz[j][i] = peso

   
    nodos = list(range(n))
    nodo_inicial = nodos[0]
    otros_nodos = nodos[1:]

    mejor_distancia = float('inf')
    mejores_rutas = []
    historial_evaluaciones = []
    rutas_vistas = set()

    permutaciones = permutar(otros_nodos)

    for perm in permutaciones:
        ruta_actual = [nodo_inicial] + list(perm) + [nodo_inicial]
        
        cuerpo = tuple(perm)
        cuerpo_inverso = tuple(reversed(perm))
        
        if cuerpo in rutas_vistas or cuerpo_inverso in rutas_vistas:
            continue
        
        rutas_vistas.add(cuerpo)

        distancia_actual = 0
        for k in range(len(ruta_actual) - 1):
            origen = ruta_actual[k]
            destino = ruta_actual[k+1]
            distancia_actual += matriz[origen][destino]

        ruta_nombres = [nombres_nodos[idx] for idx in ruta_actual]
        
        historial_evaluaciones.append({
            'ciclo': " -> ".join(ruta_nombres),
            'distancia': distancia_actual,
            'costo': distancia_actual
        })

        if distancia_actual < mejor_distancia:
            mejor_distancia = distancia_actual
            mejores_rutas = [ruta_actual]
        elif distancia_actual == mejor_distancia:
            mejores_rutas.append(ruta_actual)

    contador_ciclos_unicos = len(historial_evaluaciones)
    
    rutas_optimas_texto = []
    for r in mejores_rutas:
        nombres_r = [nombres_nodos[idx] for idx in r]
        rutas_optimas_texto.append(" -> ".join(nombres_r))

    return jsonify({
        'ciclos_totales': contador_ciclos_unicos,
        'distancia_minima': mejor_distancia,
        'cantidad_optimas': len(rutas_optimas_texto),
        'rutas_optimas': rutas_optimas_texto,
        'ruta_optima': rutas_optimas_texto[0] if rutas_optimas_texto else "",
        'historial': historial_evaluaciones,
        'matriz': matriz
    })

if __name__ == '__main__':
    app.run(debug=True)