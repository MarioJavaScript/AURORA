import os
from datetime import date

import pymysql
from flask import Flask, flash, redirect, render_template, request, url_for
from pymysql.cursors import DictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('DB_PASSWORD', 'local-dev-only')
app.config['APP_NAME'] = os.environ.get('APP_NAME', 'Inventario Tecnológico — Centinela SOC')


def connection():
    return pymysql.connect(host=os.environ.get('DB_HOST', 'db'), user=os.environ['DB_USER'],
                           password=os.environ['DB_PASSWORD'], database=os.environ['DB_NAME'],
                           charset='utf8mb4', cursorclass=DictCursor, autocommit=True)


def query(sql, params=(), one=False):
    with connection() as db:
        with db.cursor() as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                return cursor.fetchone() if one else cursor.fetchall()
            return cursor.lastrowid


def catalogs():
    return query('SELECT id, nombre FROM tipos ORDER BY id'), query('SELECT id, nombre FROM estados ORDER BY id')


def equipment(equipment_id):
    return query('SELECT * FROM equipos WHERE id = %s', (equipment_id,), one=True)


def validate(form, tipos, estados, current_id=None):
    fields = ('clave', 'marca', 'modelo', 'numero_serie', 'ubicacion', 'cliente', 'fecha_alta', 'notas')
    data = {key: form.get(key, '').strip() for key in fields}
    errors = []
    limits = {'clave': 30, 'marca': 80, 'modelo': 100, 'numero_serie': 100,
              'ubicacion': 150, 'cliente': 150}
    for key in ('clave', 'marca', 'modelo', 'numero_serie', 'ubicacion', 'fecha_alta'):
        if not data[key]:
            errors.append(f'El campo {key.replace("_", " ")} es obligatorio.')
    for key, limit in limits.items():
        if len(data[key]) > limit:
            errors.append(f'El campo {key.replace("_", " ")} admite máximo {limit} caracteres.')
    try:
        data['tipo_id'] = int(form.get('tipo_id', ''))
        if data['tipo_id'] not in {item['id'] for item in tipos}:
            raise ValueError
    except ValueError:
        errors.append('Selecciona un tipo válido.')
    try:
        data['estado_id'] = int(form.get('estado_id', ''))
        if data['estado_id'] not in {item['id'] for item in estados}:
            raise ValueError
    except ValueError:
        errors.append('Selecciona un estado válido.')
    try:
        date.fromisoformat(data['fecha_alta'])
    except ValueError:
        errors.append('Indica una fecha de alta válida.')
    if data['clave'] and query('SELECT id FROM equipos WHERE clave = %s AND id <> %s',
                               (data['clave'], current_id or 0), one=True):
        errors.append('La clave ya existe.')
    data['cliente'] = data['cliente'] or None
    data['notas'] = data['notas'] or None
    return data, errors


@app.get('/salud')
def salud():
    try:
        query('SELECT 1', one=True)
        return 'OK', 200
    except pymysql.MySQLError:
        return 'Base de datos no disponible', 503


@app.get('/')
def inicio():
    estados = query('SELECT e.nombre, COUNT(q.id) AS total FROM estados e LEFT JOIN equipos q ON q.estado_id = e.id GROUP BY e.id, e.nombre ORDER BY e.id')
    tipos = query('SELECT t.nombre, COUNT(q.id) AS total FROM tipos t LEFT JOIN equipos q ON q.tipo_id = t.id GROUP BY t.id, t.nombre ORDER BY t.id')
    total = query('SELECT COUNT(*) AS total FROM equipos', one=True)['total']
    return render_template('index.html', estados=estados, tipos=tipos, total=total)


@app.get('/equipos')
def lista():
    tipos, estados = catalogs()
    tipo = request.args.get('tipo', '', type=str)
    estado = request.args.get('estado', '', type=str)
    buscar = request.args.get('buscar', '', type=str).strip()
    tipo_id = int(tipo) if tipo.isdigit() else None
    estado_id = int(estado) if estado.isdigit() else None
    pattern = f'%{buscar}%'
    rows = query('''SELECT q.*, t.nombre AS tipo, e.nombre AS estado
                    FROM equipos q JOIN tipos t ON t.id=q.tipo_id JOIN estados e ON e.id=q.estado_id
                    WHERE (%s IS NULL OR q.tipo_id=%s) AND (%s IS NULL OR q.estado_id=%s)
                    AND (q.clave LIKE %s OR q.modelo LIKE %s)
                    ORDER BY q.clave''', (tipo_id, tipo_id, estado_id, estado_id, pattern, pattern))
    return render_template('list.html', rows=rows, tipos=tipos, estados=estados,
                           selected_tipo=tipo_id, selected_estado=estado_id, buscar=buscar)


@app.route('/equipos/nuevo', methods=['GET', 'POST'])
def nuevo():
    tipos, estados = catalogs()
    data = {'fecha_alta': date.today().isoformat()}
    errors = []
    if request.method == 'POST':
        data, errors = validate(request.form, tipos, estados)
        if not errors:
            query('''INSERT INTO equipos (clave,tipo_id,marca,modelo,numero_serie,estado_id,ubicacion,cliente,fecha_alta,notas)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                  tuple(data[k] for k in ('clave','tipo_id','marca','modelo','numero_serie','estado_id','ubicacion','cliente','fecha_alta','notas')))
            flash('Equipo agregado correctamente.')
            return redirect(url_for('lista'))
    return render_template('form.html', title='Agregar equipo', data=data, tipos=tipos, estados=estados, errors=errors)


@app.route('/equipos/<int:equipment_id>/editar', methods=['GET', 'POST'])
def editar(equipment_id):
    original = equipment(equipment_id)
    if not original:
        return 'Equipo no encontrado', 404
    tipos, estados = catalogs()
    data, errors = original, []
    if request.method == 'POST':
        data, errors = validate(request.form, tipos, estados, equipment_id)
        if not errors:
            query('''UPDATE equipos SET clave=%s,tipo_id=%s,marca=%s,modelo=%s,numero_serie=%s,
                     estado_id=%s,ubicacion=%s,cliente=%s,fecha_alta=%s,notas=%s WHERE id=%s''',
                  tuple(data[k] for k in ('clave','tipo_id','marca','modelo','numero_serie','estado_id','ubicacion','cliente','fecha_alta','notas')) + (equipment_id,))
            flash('Equipo actualizado correctamente.')
            return redirect(url_for('lista'))
    return render_template('form.html', title='Editar equipo', data=data, tipos=tipos, estados=estados, errors=errors)


@app.post('/equipos/<int:equipment_id>/eliminar')
def eliminar(equipment_id):
    if not equipment(equipment_id):
        return 'Equipo no encontrado', 404
    query('DELETE FROM equipos WHERE id=%s', (equipment_id,))
    flash('Equipo eliminado.')
    return redirect(url_for('lista'))


@app.post('/equipos/<int:equipment_id>/estado')
def cambiar_estado(equipment_id):
    if not equipment(equipment_id):
        return 'Equipo no encontrado', 404
    try:
        estado_id = int(request.form.get('estado_id', ''))
    except ValueError:
        estado_id = 0
    if not query('SELECT id FROM estados WHERE id=%s', (estado_id,), one=True):
        flash('Selecciona un estado válido.')
    else:
        query('UPDATE equipos SET estado_id=%s WHERE id=%s', (estado_id, equipment_id))
        flash('Estado actualizado.')
    return redirect(url_for('lista'))
