from flask import Flask, jsonify, request, session
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'urbanfood_secret_key_2026'

# Configuración CORS para React (puertos 3000 y 3001)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"], supports_credentials=True)

# ==================== CONFIGURACIÓN DE BASE DE DATOS ====================
def get_db():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializar la base de datos con tablas y datos por defecto"""
    conn = get_db()
    c = conn.cursor()
    
    # --- Tabla de usuarios ---
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 rol TEXT NOT NULL,
                 nombre TEXT)''')
    
    # --- Tabla de productos ---
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 codigo TEXT UNIQUE NOT NULL,
                 nombre TEXT NOT NULL,
                 precio INTEGER NOT NULL,
                 categoria TEXT)''')
    
    # --- Tabla de ventas ---
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
                 FOREIGN KEY (producto_id) REFERENCES productos(id),
                 FOREIGN KEY (vendedor_id) REFERENCES usuarios(id))''')
    
    # --- Insertar usuarios por defecto ---
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        usuarios = [
            ('admin', 'admin123', 'admin', 'Administrador'),
            ('vendedor1', 'vende123', 'vendedor', 'Vendedor 1'),
            ('vendedor2', 'vende456', 'vendedor', 'Vendedor 2')
        ]
        c.executemany("INSERT INTO usuarios (username, password, rol, nombre) VALUES (?, ?, ?, ?)", usuarios)
        print("✅ Usuarios por defecto creados")
    
    # --- Insertar productos del menú ---
    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] == 0:
        productos = [
            # Hamburguesas
            ('MINIH', 'Mini H', 5500, 'hamburguesa'),
            ('HSINT', 'H Sin T', 10000, 'hamburguesa'),
            ('HCONT', 'H Cont', 11000, 'hamburguesa'),
            ('HDOBLE', 'H Doble', 18000, 'hamburguesa'),
            # Perros
            ('PSINT', 'P Sin T', 8000, 'perro'),
            ('PCONT', 'P Cont', 9000, 'perro'),
            # Bebidas
            ('COCA', 'Coca-Cola', 3000, 'bebida'),
            ('CUATRO', 'Cuatro', 3000, 'bebida'),
            ('JUGOS', 'Jugos', 2000, 'bebida'),
            ('TE', 'Té', 2000, 'bebida'),
            ('AGUA', 'Agua', 2000, 'bebida'),
            # Adicionales
            ('AQUESO', 'A Queso', 1000, 'adicional'),
            ('ATOCINO', 'A Tocino', 1000, 'adicional')
        ]
        c.executemany("INSERT INTO productos (codigo, nombre, precio, categoria) VALUES (?, ?, ?, ?)", productos)
        print("✅ Productos del menú creados")
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/api/test', methods=['GET'])
def api_test():
    return jsonify({'message': 'API funcionando', 'status': 'ok'})

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db()
        user = conn.execute(
            "SELECT id, username, rol, nombre FROM usuarios WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['rol'] = user['rol']
            session['nombre'] = user['nombre']
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'rol': user['rol'],
                    'nombre': user['nombre']
                }
            })
        
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session', methods=['GET'])
def api_session():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'rol': session['rol'],
                'nombre': session['nombre']
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# ==================== RUTAS DE PRODUCTOS ====================

@app.route('/api/productos', methods=['GET'])
def api_productos():
    """Obtener todos los productos activos"""
    conn = get_db()
    productos = conn.execute("""
        SELECT id, codigo, nombre, precio, categoria 
        FROM productos 
        ORDER BY 
            CASE categoria 
                WHEN 'hamburguesa' THEN 1
                WHEN 'perro' THEN 2
                WHEN 'bebida' THEN 3
                WHEN 'adicional' THEN 4
                ELSE 5
            END, nombre
    """).fetchall()
    conn.close()
    return jsonify([dict(p) for p in productos])

# ==================== RUTAS DE VENTAS ====================

@app.route('/api/ventas', methods=['POST'])
def api_registrar_venta():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        data = request.json
        productos = data.get('productos', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')
        
        if not productos:
            return jsonify({'error': 'No hay productos en la venta'}), 400
        
        conn = get_db()
        total_general = 0
        venta_ids = []
        
        for item in productos:
            producto_id = item['producto_id']
            cantidad = item['cantidad']
            precio = item['precio']
            total = precio * cantidad
            total_general += total
            
            cursor = conn.execute("""
                INSERT INTO ventas 
                (producto_id, cantidad, precio_unitario, total, vendedor_id, estado, pago)
                VALUES (?, ?, ?, ?, ?, 'pendiente', ?)
            """, (producto_id, cantidad, precio, total, session['user_id'], metodo_pago))
            
            venta_ids.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'venta_id': venta_ids[0] if venta_ids else None,
            'total': total_general,
            'cantidad_productos': len(productos)
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== RUTAS DE ADMINISTRADOR ====================

@app.route('/api/estadisticas', methods=['GET'])
def api_estadisticas():
    if 'user_id' not in session or session['rol'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        conn = get_db()
        hoy = datetime.now().date().isoformat()
        
        # Ventas hoy
        ventas_hoy = conn.execute(
            "SELECT COALESCE(SUM(total), 0) FROM ventas WHERE DATE(fecha) = ?", (hoy,)
        ).fetchone()[0]
        
        # Ventas semana
        ventas_semana = conn.execute(
            "SELECT COALESCE(SUM(total), 0) FROM ventas WHERE DATE(fecha) >= DATE('now', '-7 days')"
        ).fetchone()[0]
        
        # Ventas mes
        ventas_mes = conn.execute(
            "SELECT COALESCE(SUM(total), 0) FROM ventas WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')"
        ).fetchone()[0]
        
        # Ventas totales
        ventas_totales = conn.execute(
            "SELECT COALESCE(SUM(total), 0) FROM ventas"
        ).fetchone()[0]
        
        # Últimas ventas
        ultimas_ventas = conn.execute("""
            SELECT v.id, p.nombre, v.cantidad, v.total, u.nombre as vendedor, v.estado, v.fecha
            FROM ventas v 
            JOIN productos p ON v.producto_id = p.id 
            JOIN usuarios u ON v.vendedor_id = u.id 
            ORDER BY v.fecha DESC LIMIT 10
        """).fetchall()
        
        conn.close()
        
        return jsonify({
            'ventas_hoy': ventas_hoy,
            'ventas_semana': ventas_semana,
            'ventas_mes': ventas_mes,
            'ventas_totales': ventas_totales,
            'ultimas_ventas': [dict(v) for v in ultimas_ventas],
            'ventas_por_vendedor': [],
            'top_productos': []
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== INICIALIZACIÓN ====================

if __name__ == '__main__':
    init_db()
    print("\n" + "=" * 60)
    print("🚀 SERVIDOR FLASK - URBAN FOOD")
    print("=" * 60)
    print("📡 API URL: http://localhost:5000")
    print("\n🔑 Credenciales de prueba:")
    print("   👑 Admin:     admin / admin123")
    print("   👤 Vendedor 1: vendedor1 / vende123")
    print("   👤 Vendedor 2: vendedor2 / vende456")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5000)