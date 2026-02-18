from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for, Response, send_file
import sqlite3
from datetime import datetime, date
import os
import io
import socket
import qrcode

app = Flask(__name__)
app.secret_key = 'urbanfood_secret_key_2026'

# ==================== FUNCIONES AUXILIARES ====================
def get_local_ip():
    """Obtener la IP local automáticamente"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ==================== BASE DE DATOS ====================
def init_db():
    """Inicializar la base de datos con tablas y datos básicos"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Tabla de usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 rol TEXT NOT NULL,
                 nombre TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabla de productos (según tu menú)
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 codigo TEXT UNIQUE NOT NULL,
                 nombre TEXT NOT NULL,
                 precio INTEGER NOT NULL,
                 categoria TEXT,
                 activo INTEGER DEFAULT 1)''')
    
    # Tabla de ventas
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 producto_id INTEGER,
                 cantidad INTEGER NOT NULL,
                 precio_unitario INTEGER NOT NULL,
                 total INTEGER NOT NULL,
                 vendedor_id INTEGER,
                 estado TEXT DEFAULT 'pendiente',
                 pago TEXT DEFAULT 'efectivo',
                 comanda_impresa INTEGER DEFAULT 0,
                 FOREIGN KEY (producto_id) REFERENCES productos(id),
                 FOREIGN KEY (vendedor_id) REFERENCES usuarios(id))''')
    
    # Tabla de gastos
    c.execute('''CREATE TABLE IF NOT EXISTS gastos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 concepto TEXT NOT NULL,
                 monto INTEGER NOT NULL,
                 tipo TEXT,
                 responsable_id INTEGER)''')
    
    # Insertar usuarios por defecto (SI NO EXISTEN)
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        usuarios_iniciales = [
            ('admin', 'admin123', 'admin', 'Administrador Principal'),
            ('vendedor1', 'vende123', 'vendedor', 'Vendedor 1'),
            ('vendedor2', 'vende456', 'vendedor', 'Vendedor 2')
        ]
        c.executemany("INSERT INTO usuarios (username, password, rol, nombre) VALUES (?, ?, ?, ?)", usuarios_iniciales)
    
    # Insertar productos del menú (SI NO EXISTEN)
    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] == 0:
        productos = [
            # Código, Nombre, Precio, Categoría
            ('MINIH', 'Mini H', 5500, 'hamburguesa'),
            ('HSINT', 'H Sin T', 10000, 'hamburguesa'),
            ('HCONT', 'H Cont', 11000, 'hamburguesa'),
            ('HDOBLE', 'H Doble', 18000, 'hamburguesa'),
            ('PSINT', 'P Sin T', 8000, 'perro'),
            ('PCONT', 'P Cont', 9000, 'perro'),
            ('COCA', 'Coca-Cola', 3000, 'bebida'),
            ('CUATRO', 'Cuatro', 3000, 'bebida'),
            ('JUGOS', 'Jugos', 2000, 'bebida'),
            ('TE', 'Té', 2000, 'bebida'),
            ('AGUA', 'Agua', 2000, 'bebida'),
            ('AQUESO', 'A Queso', 1000, 'adicional'),
            ('ATOCINO', 'A Tocino', 1000, 'adicional')
        ]
        c.executemany("INSERT INTO productos (codigo, nombre, precio, categoria) VALUES (?, ?, ?, ?)", productos)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

# ==================== RUTAS PRINCIPALES ====================
@app.route('/')
def index():
    """Página principal - Redirige al login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('login.html')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, username, rol, nombre FROM usuarios WHERE username=? AND password=?", 
                  (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            # Guardar datos en sesión
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['rol'] = user[2]
            session['nombre'] = user[3]
            
            # Redirigir según el rol
            if user[2] == 'admin':
                flash(f'¡Bienvenido Administrador {user[3]}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash(f'¡Bienvenido Vendedor {user[3]}!', 'success')
                return redirect(url_for('vendedor_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    # Obtener IP para mostrar en login
    local_ip = get_local_ip()
    return render_template('login.html', local_ip=local_ip)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

# ==================== RUTAS DEL VENDEDOR ====================
@app.route('/vendedor')
def vendedor_dashboard():
    """Panel del vendedor con menú interactivo"""
    if 'user_id' not in session or session['rol'] != 'vendedor':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Obtener productos organizados por categoría
    c.execute("""
        SELECT id, codigo, nombre, precio, categoria 
        FROM productos 
        WHERE activo = 1 
        ORDER BY 
            CASE categoria 
                WHEN 'hamburguesa' THEN 1
                WHEN 'perro' THEN 2
                WHEN 'bebida' THEN 3
                WHEN 'adicional' THEN 4
                ELSE 5
            END, nombre
    """)
    productos = c.fetchall()
    
    conn.close()
    
    return render_template('vendedor.html', 
                         productos=productos,
                         nombre=session.get('nombre'))

# ==================== APIs PARA VENTAS COMPLETAS ====================
@app.route('/api/registrar_venta_completa', methods=['POST'])
def registrar_venta_completa():
    """API para registrar una venta completa con múltiples productos"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        data = request.json
        productos = data.get('productos', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')
        
        if not productos:
            return jsonify({'error': 'No hay productos en el pedido'}), 400
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        venta_ids = []
        total_general = 0
        
        # Registrar cada producto como una venta separada
        for item in productos:
            producto_id = item['producto_id']
            cantidad = item['cantidad']
            precio = item['precio']
            total = precio * cantidad
            total_general += total
            
            # Insertar venta
            c.execute('''INSERT INTO ventas 
                         (producto_id, cantidad, precio_unitario, total, vendedor_id, estado, pago) 
                         VALUES (?, ?, ?, ?, ?, 'pendiente', ?)''',
                      (producto_id, cantidad, precio, total, session['user_id'], metodo_pago))
            
            venta_ids.append(c.lastrowid)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'venta_id': venta_ids[0] if venta_ids else None,
            'total': total_general,
            'cantidad_productos': len(productos)
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/registrar_venta', methods=['POST'])
def registrar_venta():
    """API para registrar una nueva venta (simple)"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        data = request.json
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Obtener precio del producto
        c.execute("SELECT precio FROM productos WHERE id = ?", (producto_id,))
        producto = c.fetchone()
        
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        precio_unitario = producto[0]
        total = precio_unitario * cantidad
        
        # Insertar venta
        c.execute('''INSERT INTO ventas 
                     (producto_id, cantidad, precio_unitario, total, vendedor_id, estado, pago) 
                     VALUES (?, ?, ?, ?, ?, 'pendiente', 'efectivo')''',
                  (producto_id, cantidad, precio_unitario, total, session['user_id']))
        
        venta_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'venta_id': venta_id,
            'total': total
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cambiar_estado_venta/<int:venta_id>', methods=['POST'])
def cambiar_estado_venta(venta_id):
    """Cambiar estado de una venta (pendiente → listo)"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.json
    nuevo_estado = data.get('estado', 'listo')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Verificar que la venta pertenezca al vendedor (si es vendedor)
    if session['rol'] == 'vendedor':
        c.execute("SELECT vendedor_id FROM ventas WHERE id = ?", (venta_id,))
        venta = c.fetchone()
        if not venta or venta[0] != session['user_id']:
            conn.close()
            return jsonify({'error': 'No autorizado'}), 403
    
    c.execute("UPDATE ventas SET estado = ? WHERE id = ?", (nuevo_estado, venta_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ==================== RUTAS DEL ADMINISTRADOR ====================
@app.route('/admin')
def admin_dashboard():
    """Panel principal del administrador"""
    if 'user_id' not in session or session['rol'] != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Estadísticas del día
    hoy = date.today().isoformat()
    
    # Total ventas del día
    c.execute("SELECT SUM(total) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
    total_ventas = c.fetchone()[0] or 0
    
    # Cantidad de ventas del día
    c.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
    cantidad_ventas = c.fetchone()[0]
    
    # Ventas por vendedor
    c.execute('''SELECT u.nombre, COUNT(v.id) as ventas, SUM(v.total) as total 
                 FROM ventas v 
                 JOIN usuarios u ON v.vendedor_id = u.id 
                 WHERE DATE(v.fecha) = ? 
                 GROUP BY v.vendedor_id''', (hoy,))
    ventas_por_vendedor = c.fetchall()
    
    # Últimas ventas
    c.execute('''SELECT v.id, p.nombre, v.cantidad, v.total, u.nombre, v.estado, 
                        strftime("%%H:%%M", v.fecha) as hora
                 FROM ventas v 
                 JOIN productos p ON v.producto_id = p.id 
                 JOIN usuarios u ON v.vendedor_id = u.id 
                 ORDER BY v.fecha DESC LIMIT 10''')
    ultimas_ventas = c.fetchall()
    
    # Productos más vendidos hoy
    c.execute('''SELECT p.nombre, SUM(v.cantidad) as total_vendido
                 FROM ventas v 
                 JOIN productos p ON v.producto_id = p.id 
                 WHERE DATE(v.fecha) = ?
                 GROUP BY v.producto_id 
                 ORDER BY total_vendido DESC LIMIT 5''', (hoy,))
    top_productos = c.fetchall()
    
    conn.close()
    
    # Obtener IP para QR
    local_ip = get_local_ip()
    
    return render_template('admin.html',
                         total_ventas=total_ventas,
                         cantidad_ventas=cantidad_ventas,
                         ventas_por_vendedor=ventas_por_vendedor,
                         ultimas_ventas=ultimas_ventas,
                         top_productos=top_productos,
                         nombre=session.get('nombre'),
                         local_ip=local_ip)

# ==================== APIs PARA ESTADÍSTICAS ====================
@app.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """API para obtener estadísticas para el dashboard del admin"""
    if 'user_id' not in session or session['rol'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Ventas de hoy
        hoy = date.today().isoformat()
        c.execute("SELECT SUM(total) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
        ventas_hoy = c.fetchone()[0] or 0
        
        # Ventas de la semana (últimos 7 días)
        c.execute("SELECT SUM(total) FROM ventas WHERE DATE(fecha) >= DATE('now', '-7 days')")
        ventas_semana = c.fetchone()[0] or 0
        
        # Ventas del mes actual
        c.execute("SELECT SUM(total) FROM ventas WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')")
        ventas_mes = c.fetchone()[0] or 0
        
        # Total de ventas (todos los tiempos)
        c.execute("SELECT SUM(total) FROM ventas")
        ventas_totales = c.fetchone()[0] or 0
        
        # Ventas por día (últimos 7 días)
        c.execute("""
            SELECT DATE(fecha) as dia, COALESCE(SUM(total), 0) as total
            FROM ventas 
            WHERE DATE(fecha) >= DATE('now', '-7 days')
            GROUP BY DATE(fecha)
            ORDER BY dia
        """)
        ventas_por_dia = c.fetchall()
        
        # Productos más vendidos (top 5)
        c.execute("""
            SELECT p.nombre, SUM(v.cantidad) as cantidad, SUM(v.total) as total
            FROM ventas v 
            JOIN productos p ON v.producto_id = p.id 
            GROUP BY v.producto_id 
            ORDER BY cantidad DESC 
            LIMIT 5
        """)
        top_productos = c.fetchall()
        
        # Métodos de pago más usados
        c.execute("""
            SELECT pago, COUNT(*) as cantidad, SUM(total) as total
            FROM ventas 
            GROUP BY pago 
            ORDER BY cantidad DESC
        """)
        metodos_pago = c.fetchall()
        
        # Vendedores con más ventas
        c.execute("""
            SELECT u.nombre, COUNT(v.id) as ventas, SUM(v.total) as total
            FROM ventas v 
            JOIN usuarios u ON v.vendedor_id = u.id 
            GROUP BY v.vendedor_id 
            ORDER BY total DESC
            LIMIT 5
        """)
        top_vendedores = c.fetchall()
        
        conn.close()
        
        # Formatear respuesta JSON
        return jsonify({
            'ventas_hoy': ventas_hoy,
            'ventas_semana': ventas_semana,
            'ventas_mes': ventas_mes,
            'ventas_totales': ventas_totales,
            'ventas_por_dia': [
                {'dia': str(row[0]), 'total': row[1]} 
                for row in ventas_por_dia
            ],
            'top_productos': [
                {'nombre': row[0], 'cantidad': row[1], 'total': row[2]} 
                for row in top_productos
            ],
            'metodos_pago': [
                {'pago': row[0], 'cantidad': row[1], 'total': row[2]} 
                for row in metodos_pago
            ],
            'top_vendedores': [
                {'nombre': row[0], 'ventas': row[1], 'total': row[2]} 
                for row in top_vendedores
            ]
        })
        
    except Exception as e:
        print(f"❌ Error en /api/estadisticas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ventas_detalladas', methods=['GET'])
def obtener_ventas_detalladas():
    """API para obtener ventas detalladas con filtros"""
    if 'user_id' not in session or session['rol'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        fecha_inicio = request.args.get('fecha_inicio', date.today().isoformat())
        fecha_fin = request.args.get('fecha_fin', date.today().isoformat())
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                v.id,
                p.nombre as producto,
                v.cantidad,
                v.precio_unitario,
                v.total,
                u.nombre as vendedor,
                v.pago,
                v.estado,
                strftime('%Y-%m-%d %H:%M', v.fecha) as fecha
            FROM ventas v 
            JOIN productos p ON v.producto_id = p.id 
            JOIN usuarios u ON v.vendedor_id = u.id 
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            ORDER BY v.fecha DESC
        """, (fecha_inicio, fecha_fin))
        
        ventas = c.fetchall()
        conn.close()
        
        return jsonify({
            'ventas': [
                {
                    'id': row[0],
                    'producto': row[1],
                    'cantidad': row[2],
                    'precio_unitario': row[3],
                    'total': row[4],
                    'vendedor': row[5],
                    'pago': row[6],
                    'estado': row[7],
                    'fecha': row[8]
                } for row in ventas
            ]
        })
        
    except Exception as e:
        print(f"❌ Error en /api/ventas_detalladas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exportar_excel', methods=['GET'])
def exportar_excel():
    """Exportar ventas a CSV (simulando Excel)"""
    if 'user_id' not in session or session['rol'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        fecha_inicio = request.args.get('fecha_inicio', date.today().isoformat())
        fecha_fin = request.args.get('fecha_fin', date.today().isoformat())
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                v.id,
                p.nombre,
                v.cantidad,
                v.precio_unitario,
                v.total,
                u.nombre,
                v.pago,
                v.estado,
                v.fecha
            FROM ventas v 
            JOIN productos p ON v.producto_id = p.id 
            JOIN usuarios u ON v.vendedor_id = u.id 
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            ORDER BY v.fecha DESC
        """, (fecha_inicio, fecha_fin))
        
        ventas = c.fetchall()
        conn.close()
        
        # Crear CSV simple
        output = io.StringIO()
        
        # Encabezados
        output.write("ID,Producto,Cantidad,Precio Unitario,Total,Vendedor,Método Pago,Estado,Fecha\n")
        
        # Datos
        for row in ventas:
            # Convertir cada campo a string y escapar comas
            row_data = []
            for field in row:
                if field is None:
                    row_data.append("")
                else:
                    field_str = str(field)
                    # Si el campo contiene comas, ponerlo entre comillas
                    if ',' in field_str or '"' in field_str:
                        field_str = field_str.replace('"', '""')
                        field_str = f'"{field_str}"'
                    row_data.append(field_str)
            
            output.write(",".join(row_data) + "\n")
        
        output.seek(0)
        
        # Crear respuesta con headers para descarga
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=ventas_{fecha_inicio}_{fecha_fin}.csv"
            }
        )
        
    except Exception as e:
        print(f"❌ Error en /api/exportar_excel: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== CÓDIGO QR ====================
@app.route('/qr')
def generate_qrcode():
    """Generar código QR con la URL de acceso"""
    try:
        local_ip = get_local_ip()
        url = f"http://{local_ip}:5000"
        
        # Crear QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar en memoria
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return send_file(img_bytes, mimetype='image/png')
        
    except Exception as e:
        print(f"Error generando QR: {e}")
        return "Error generando QR", 500

@app.route('/qr_page')
def qr_page():
    """Página para mostrar el código QR"""
    local_ip = get_local_ip()
    url = f"http://{local_ip}:5000"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Code - Urban Food</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: #f5f5f5; 
            }}
            .container {{ 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                display: inline-block; 
            }}
            h1 {{ color: #2E7D32; }}
            .url {{ 
                background: #e8f5e9; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 20px 0; 
                font-family: monospace; 
            }}
            .instructions {{ 
                text-align: left; 
                margin-top: 20px; 
                background: #f9f9f9; 
                padding: 15px; 
                border-radius: 5px; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍔 FRESCA Urban Food</h1>
            <h2>Escanea para acceder</h2>
            
            <div class="url">
                <strong>URL:</strong> {url}
            </div>
            
            <img src="/qr" alt="QR Code" style="width: 300px; height: 300px;">
            
            <div class="instructions">
                <h3>📱 Instrucciones:</h3>
                <ol>
                    <li>Conecta tu dispositivo al <strong>mismo WiFi</strong> que esta computadora</li>
                    <li>Abre la cámara o app de QR en tu celular/tablet</li>
                    <li>Escanea este código QR</li>
                    <li>¡Listo! Accederás automáticamente al sistema</li>
                </ol>
                
                <p><strong>Credenciales:</strong></p>
                <ul>
                    <li>👑 Admin: <code>admin</code> / <code>admin123</code></li>
                    <li>👤 Vendedor: <code>vendedor1</code> / <code>vende123</code></li>
                </ul>
            </div>
            
            <p style="margin-top: 20px;">
                <a href="/">← Volver al inicio</a>
            </p>
        </div>
    </body>
    </html>
    """

# ==================== EJECUCIÓN ====================
if __name__ == '__main__':
    # Crear carpeta de templates si no existe
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Inicializar base de datos
    init_db()
    
    # Obtener IP local
    local_ip = get_local_ip()
    
    print("=" * 70)
    print("🚀 SERVIDOR URBAN FOOD - CON CÓDIGO QR")
    print("=" * 70)
    print("📡 Tu IP local es:", local_ip)
    print("")
    print("🌐 URLS de acceso:")
    print(f"   📍 En ESTA computadora:  http://localhost:5000")
    print(f"   📱 En CELULAR/Tablet:    http://{local_ip}:5000")
    print(f"   📲 Código QR:            http://localhost:5000/qr_page")
    print("")
    print("🔑 Credenciales de prueba:")
    print("   👑 Administrador:  usuario=admin      contraseña=admin123")
    print("   👤 Vendedor 1:     usuario=vendedor1  contraseña=vende123")
    print("   👤 Vendedor 2:     usuario=vendedor2  contraseña=vende456")
    print("")
    print("📁 Archivos necesarios en carpeta 'templates':")
    print("   ✅ login.html     (Interfaz de login)")
    print("   ✅ vendedor.html  (Panel del vendedor)")
    print("   ✅ admin.html     (Panel del administrador)")
    print("")
    print("⚠️  IMPORTANTE PARA ACCESO MULTIDISPOSITIVO:")
    print("   1. Todos deben estar en la MISMA RED WiFi")
    print("   2. Usa el QR o la IP mostrada arriba")
    print("   3. Para detener: Presiona CTRL+C")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)