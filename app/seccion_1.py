from flask import Blueprint, render_template, request, send_file, url_for
import os, json, csv
import matlab.engine
import pandas as pd
import numpy as np

# Crear el blueprint
blueprint = Blueprint('seccion_1', __name__)

# Iniciar el motor de MATLAB
eng = matlab.engine.start_matlab()

# Rutas base
dir_actual = os.path.dirname(os.path.abspath(__file__))
dir_matlab = os.path.join(os.path.dirname(dir_actual), 'matlab')
dir_tables = os.path.join(dir_actual, 'tables')

# Añadir el directorio MATLAB al path
if os.path.exists(dir_matlab):
    eng.addpath(dir_matlab)
    print(f"Ruta añadida correctamente: {dir_matlab}")
else:
    print(f"La ruta de MATLAB no existe: {dir_matlab}")

eng.addpath(dir_matlab)

# Método del punto fijo
@blueprint.route('/punto_fijo', methods=['GET', 'POST'])
def punto_fijo():
    if request.method == 'POST':
        f = str(request.form['f'])
        g = str(request.form['g'])
        x = float(request.form['x'].replace(',', '.'))
        tol = float(request.form['tol'].replace(',', '.'))
        niter = int(request.form['niter'])
        tipe = str(request.form['tipe'])
        
        [r, N, xn, fm, E] = eng.pf(f, g, x, tol, niter, tipe, nargout=5)
        N, xn, fm, E = list(N[0]), list(xn[0]), list(fm[0]), list(E[0])
        length = len(N)
        
        df = pd.read_csv(os.path.join(dir_tables, 'tabla_pf.csv'))
        df = df.astype(str)
        data = df.to_dict(orient='records')
        df.to_excel(os.path.join(dir_tables, 'tabla_pf.xlsx'), index=False)
        
        imagen_path = os.path.join('static', 'grafica_pf.png')
        return render_template('Seccion_1/resultado_pf.html', r=r, N=N, xn=xn, fm=fm, E=E, length=length, data=data, imagen_path=imagen_path)
    
    return render_template('Seccion_1/formulario_pf.html')

@blueprint.route('/pf/descargar', methods=['POST'])
def descargar_archivo_pf():
    archivo_path = os.path.join(dir_tables, 'tabla_pf.xlsx')
    return send_file(archivo_path, as_attachment=True)

# Ruta para el método de bisección
@blueprint.route('/biseccion', methods=['GET', 'POST'])
def biseccion():
    if request.method == 'POST':
        # Obtener datos del formulario
        f = str(request.form['f'])
        xi = float(request.form['xi'].replace(',', '.'))
        xs = float(request.form['xs'].replace(',', '.'))
        tol = float(request.form['tol'].replace(',', '.'))
        niter = int(request.form['niter'])
        tipe = str(request.form['tipe'])

        try:
            # Ejecutar la función de MATLAB
            [r, N, xn, fm, E] = eng.biseccion(f, xi, xs, tol, niter, tipe, nargout=5)

            # Convertir resultados en listas
            if len(N) != 0:
                N, xn, fm, E = list(N[0]), list(xn[0]), list(fm[0]), list(E[0])
            else:
                N, xn, fm, E = [], [], [], []

            length = len(N)

            # Leer y procesar la tabla de resultados
            tabla_path = os.path.join(dir_tables, 'tabla_biseccion.csv')
            if os.path.exists(tabla_path):
                df = pd.read_csv(tabla_path)
                df = df.astype(str)
                data = df.to_dict(orient='records')
            else:
                data = []

            # Procesar la ruta de la gráfica
            imagen_path = os.path.join(dir_actual, 'static', 'grafica_biseccion.png')
            if not os.path.exists(imagen_path):
                imagen_path = None
            else:
                imagen_path = url_for('static', filename='grafica_biseccion.png')

            # Renderizar resultados
            return render_template(
                'Seccion_1/resultado_biseccion.html',
                r=r, N=N, xn=xn, fm=fm, E=E,
                length=length, data=data,
                imagen_path=imagen_path
            )

        except Exception as e:
            print(f"Error en MATLAB: {e}")
            return f"Error en la ejecución de MATLAB: {e}"

    # Renderizar formulario
    return render_template('Seccion_1/formulario_biseccion.html')

# Ruta para descargar el archivo de resultados
@blueprint.route('/biseccion/descargar', methods=['POST'])
def descargar_archivo_biseccion():
    archivo_path = os.path.join(dir_tables, 'tabla_biseccion.xlsx')
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True)
    else:
        return "Archivo no encontrado", 404


#Método de raíces múltiples
@blueprint.route('/multiple_roots', methods=['GET', 'POST'])
def multiple_roots():
    if request.method == 'POST':
        fn = str(request.form['fn'])
        xi = float(request.form['xi'].replace(',', '.'))
        tol = float(request.form['tol'].replace(',', '.'))
        k = int(request.form['k'])
        et = str(request.form['et'])

        eng.addpath(dir_matlab)
        # Asume que multiple_roots retorna los valores necesarios o guarda los resultados en un archivo CSV
        [xi, errores, resultado] = eng.raices_multiples(fn, xi, tol, k, et, nargout=3)  # Ejecuta el cálculo en MATLAB
        
        # Lee los resultados de un archivo CSV
        df = pd.read_csv(os.path.join(dir_tables, 'multiple_roots_results.csv'))
        df = df.astype(str)
        data = df.to_dict(orient='records')
        df.to_excel(os.path.join(dir_tables, 'multiple_roots_results.xlsx'), index=False)

        imagen_path = os.path.join('static', 'grafica_multiple_roots.png')

        return render_template('Seccion_1/resultado_raicesm.html', data=data, imagen_path=imagen_path, resultado=resultado)
    
    return render_template('Seccion_1/formulario_raicesm.html')

@blueprint.route('/rm/descargar', methods=['POST'])
def descargar_archivo_raicesm():
    archivo_path = os.path.join(dir_tables, 'multiple_roots_results.xlsx')
    return send_file(archivo_path, as_attachment=True)


#Método de la secante
@blueprint.route('/secante', methods=['GET', 'POST'])
def secante():
    if request.method == 'POST':
        f= str(request.form['f']) 
        x0 = float(request.form['x0'].replace(',', '.'))
        x1 = float(request.form['x1'].replace(',', '.'))  
        tol = float(request.form['tol'].replace(',', '.'))
        Terror = str(request.form['Terror'])
        niter = int(request.form['niter'])
        
        eng.addpath(dir_matlab)

        respuesta = eng.secante(f, x0, x1, tol, niter, Terror)
        df = pd.read_csv(os.path.join(dir_tables,'tabla_secante.csv'))
        df = df.astype(str)
        data = df.to_dict(orient='records')

        # Lee el archivo CSV
        df = pd.read_csv(os.path.join(dir_tables,'tabla_secante.csv'))
        # Escribe los datos en un nuevo archivo Excel
        df.to_excel(os.path.join(dir_tables,'tabla_secante.xlsx'), index=False) 

        #Gráfica
        imagen_path = os.path.join('static','grafica_secante.png')  # Ruta de la imagen
        return render_template('Seccion_1/resultado_secante.html',respuesta=respuesta, data=data,imagen_path=imagen_path)
        
    return render_template('Seccion_1/formulario_secante.html')

@blueprint.route('/secante/descargar', methods=['POST'])
def descargar_archivo():
    # Ruta del archivo que se va a descargar
    archivo_path = 'tables/tabla_secante.xlsx'

    # Enviar el archivo al cliente para descargar
    return send_file(archivo_path, as_attachment=True)


#Método de regla falsa
@blueprint.route('/rf', methods=['GET', 'POST'])
def reglaFalsa():
    if request.method == 'POST':
        f= str(request.form['f']) 
        x0 = float(request.form['x0'].replace(',', '.'))
        x1 = float(request.form['x1'].replace(',', '.'))  
        tol = float(request.form['tol'].replace(',', '.'))
        Terror = str(request.form['Terror'])
        niter = int(request.form['niter'])
        
        eng.addpath(dir_matlab)

        respuesta = eng.rf(f, x0, x1, tol, niter, Terror)
        print(respuesta[0])
        df = pd.read_csv(os.path.join(dir_tables,'tabla_reglaFalsa.csv'))
        df = df.astype(str)
        data = df.to_dict(orient='records')

        # Lee el archivo CSV
        df = pd.read_csv(os.path.join(dir_tables,'tabla_reglaFalsa.csv'))
        # Escribe los datos en un nuevo archivo Excel
        df.to_excel(os.path.join(dir_tables,'tabla_reglaFalsa.xlsx'), index=False) 

        #Gráfica
        imagen_path = os.path.join('static','grafica_reglaFalsa.png')  # Ruta de la imagen
        return render_template('Seccion_1/resultado_reglaFalsa.html',respuesta=respuesta, data=data,imagen_path=imagen_path)
        
    return render_template('Seccion_1/formulario_reglaFalsa.html')

@blueprint.route('/rf/descargar', methods=['POST'])
def descargar_archivorf():
    # Ruta del archivo que se va a descargar
    archivo_path = 'tables/tabla_reglaFalsa.xlsx'

    # Enviar el archivo al cliente para descargar
    return send_file(archivo_path, as_attachment=True)

#Método de newton
@blueprint.route('/newton', methods=['GET', 'POST'])
def newton():
    if request.method == 'POST':
        try:
            # Inicializar el motor de MATLAB
            eng = matlab.engine.start_matlab()
            
            # Verificar que el directorio de MATLAB existe
            if not os.path.exists(dir_matlab):
                raise Exception(f"El directorio de MATLAB no existe: {dir_matlab}")
            
            # Agregar el path y verificar
            eng.addpath(dir_matlab)
            
            # Obtener los datos del formulario
            f = str(request.form['f']) 
            x = float(request.form['x'].replace(',', '.'))  
            tol = float(request.form['tol'].replace(',', '.'))
            niter = int(request.form['niter'])
            et = str(request.form['et'])

            # Llamar a la función de MATLAB
            try:
                [r, N, xn, fm, dfm, E, c] = eng.newton(f, x, tol, niter, et, nargout=7)
            except Exception as e:
                eng.quit()
                return f"Error en MATLAB: {str(e)}", 400

            # Procesar resultados
            N, xn, fm, dfm, E = list(N[0]), list(xn[0]), list(fm[0]), list(dfm[0]), list(E[0])
            length = len(N)

            # Leer y procesar el CSV
            df = pd.read_csv(os.path.join(dir_tables, 'tabla_newton.csv'))
            df = df.astype(str)
            data = df.to_dict(orient='records')
            df.to_excel(os.path.join(dir_tables, 'tabla_newton.xlsx'), index=False)

            eng.quit()  # Cerrar el motor de MATLAB

            return render_template(
                'Seccion_1/resultado_newton.html',
                r=r, N=N, xn=xn, fm=fm, dfm=dfm, E=E,
                length=length, data=data,
                imagen_path='../static/grafica_newton.png',
                c=c, niter=niter
            )
            
        except Exception as e:
            return f"Error: {str(e)}", 400
            
    return render_template('Seccion_1/formulario_newton.html')

@blueprint.route('/newton/descargar', methods=['POST'])
def descargar_archivo_newton():
    # Ruta del archivo que se va a descargar
    archivo_path = 'tables/tabla_newton.xlsx'

    # Enviar el archivo al cliente para descargar
    return send_file(archivo_path, as_attachment=True)