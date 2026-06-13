import csv
import io
import os
from functools import wraps

import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "encuesta_tmms"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "postgres"),
}


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def ensure_admin():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE username = 'administrador'")
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)",
                ("administrador", generate_password_hash("año2026")),
            )
            conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated



@app.route("/prueba-preguntas_v1")
def encuesta():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM preguntas ORDER BY numero")
    preguntas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("encuesta.html", preguntas=preguntas)


@app.route("/")
def prueba_preguntas_v2():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM preguntas ORDER BY numero")
    preguntas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("encuesta_v2.html", preguntas=preguntas)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        try:
            conn = get_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if user and check_password_hash(user["password_hash"], password):
                session["user"] = user["username"]
                return redirect(url_for("admin"))
            error = "Usuario o contraseña incorrectos"
        except Exception:
            error = "Error al conectar con la base de datos"
    return render_template("login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("user", None)
    return redirect(url_for("admin_login"))


@app.route("/guardar", methods=["POST"])
def guardar():
    nombre = request.form.get("nombre", "").strip().upper()
    genero = request.form.get("genero", "").strip()
    grado = request.form.get("grado", "").strip()
    seccion = request.form.get("seccion", "").strip()
    seccion = seccion.upper() if seccion else None

    if not nombre or not genero or not grado:
        return redirect(url_for("encuesta") + "?error=1")

    respuestas = []
    for key, value in request.form.items():
        if key.startswith("p_"):
            pregunta_id = int(key.replace("p_", ""))
            respuestas.append((pregunta_id, int(value)))

    if len(respuestas) != 24:
        return redirect(url_for("encuesta") + "?error=1")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO encuestados (nombre, genero, grado, seccion) VALUES (%s, %s, %s, %s) RETURNING id",
        (nombre, genero, grado, seccion),
    )
    encuestado_id = cur.fetchone()[0]

    for pregunta_id, valor in respuestas:
        cur.execute(
            "INSERT INTO respuestas (encuestado_id, pregunta_id, valor) VALUES (%s, %s, %s)",
            (encuestado_id, pregunta_id, valor),
        )

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("completado", encuestado_id=encuestado_id))


@app.route("/completado")
def completado():
    encuestado_id = request.args.get("encuestado_id", type=int)
    nombre = grado = seccion = ""
    if encuestado_id:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT nombre, grado, seccion FROM encuestados WHERE id = %s", (encuestado_id,))
        row = cur.fetchone()
        if row:
            nombre, grado, seccion = row
        cur.close()
        conn.close()
    return render_template("completado.html", nombre=nombre, grado=grado, seccion=seccion)


@app.route("/admin")
@login_required
def admin():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT COUNT(*) AS total FROM encuestados")
    total_encuestados = cur.fetchone()["total"]

    cur.execute("""
        SELECT p.numero, p.texto, p.dimension,
               ROUND(AVG(r.valor)::numeric, 2) AS promedio
        FROM preguntas p
        LEFT JOIN respuestas r ON r.pregunta_id = p.id
        GROUP BY p.id, p.numero, p.texto, p.dimension
        ORDER BY p.numero
    """)
    preguntas = cur.fetchall()

    cur.execute("""
        SELECT p.dimension,
               ROUND(AVG(r.valor)::numeric, 2) AS promedio,
               COUNT(DISTINCT r.encuestado_id) AS total_respuestas
        FROM preguntas p
        LEFT JOIN respuestas r ON r.pregunta_id = p.id
        GROUP BY p.dimension
    """)
    dimensiones = cur.fetchall()

    cur.execute("""
        SELECT e.id, e.nombre, e.genero, e.grado, e.seccion, e.created_at,
               COUNT(r.id) AS total_respuestas
        FROM encuestados e
        LEFT JOIN respuestas r ON r.encuestado_id = e.id
        GROUP BY e.id, e.nombre, e.genero, e.grado, e.seccion, e.created_at
        ORDER BY e.created_at DESC
    """)
    encuestados = cur.fetchall()

    cur.close()
    conn.close()
    return render_template(
        "admin.html",
        total_encuestados=total_encuestados,
        preguntas=preguntas,
        dimensiones=dimensiones,
        encuestados=encuestados,
    )


@app.route("/admin/encuestados")
@login_required
def admin_encuestados():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT e.id, e.nombre, e.genero, e.grado, e.seccion, e.created_at
        FROM encuestados e
        ORDER BY e.created_at DESC
    """)
    encuestados = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin_encuestados.html", encuestados=encuestados)


@app.route("/admin/encuestados/<int:id>/editar", methods=["POST"])
@login_required
def admin_editar_encuestado(id):
    nombre = request.form.get("nombre", "").strip().upper()
    genero = request.form.get("genero", "").strip()
    grado = request.form.get("grado", "").strip()
    seccion = request.form.get("seccion", "").strip()
    seccion = seccion.upper() if seccion else None
    if not nombre or not genero or not grado:
        flash("Todos los campos obligatorios deben estar completos.", "danger")
        return redirect(url_for("admin_encuestados"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE encuestados SET nombre = %s, genero = %s, grado = %s, seccion = %s WHERE id = %s",
        (nombre, genero, grado, seccion, id),
    )
    conn.commit()
    cur.close()
    conn.close()
    flash("Encuestado actualizado correctamente.", "success")
    return redirect(url_for("admin_encuestados"))


@app.route("/admin/exportar-csv")
@login_required
def exportar_csv():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id, numero FROM preguntas ORDER BY numero")
    preguntas = cur.fetchall()
    columnas_preguntas = [f"P{p['numero']}" for p in preguntas]
    pregunta_ids = [p["id"] for p in preguntas]

    cur.execute("""
        SELECT e.id, e.nombre, e.genero, e.grado, e.seccion, e.created_at,
               r.pregunta_id, r.valor
        FROM encuestados e
        LEFT JOIN respuestas r ON r.encuestado_id = e.id
        ORDER BY e.id, r.pregunta_id
    """)
    filas = cur.fetchall()
    cur.close()
    conn.close()

    respuestas_por_encuestado = {}
    encuestados_info = {}
    for f in filas:
        eid = f["id"]
        if eid not in encuestados_info:
            encuestados_info[eid] = {
                "nombre": f["nombre"],
                "genero": f["genero"] or "",
                "grado": f["grado"],
                "seccion": f["seccion"] or "",
                "fecha": f["created_at"].strftime("%Y-%m-%d %H:%M") if f["created_at"] else "",
            }
            respuestas_por_encuestado[eid] = {}
        if f["pregunta_id"] is not None:
            respuestas_por_encuestado[eid][f["pregunta_id"]] = f["valor"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Nombre", "Genero", "Grado", "Seccion", "Fecha"] + columnas_preguntas)

    for eid in sorted(encuestados_info.keys()):
        info = encuestados_info[eid]
        resp = respuestas_por_encuestado[eid]
        fila = [eid, info["nombre"], info["genero"], info["grado"], info["seccion"], info["fecha"]]
        for pid in pregunta_ids:
            fila.append(resp.get(pid, ""))
        writer.writerow(fila)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=respuestas.csv"},
    )


if __name__ == "__main__":
    ensure_admin()
    app.run(debug=True, host="0.0.0.0", port=5000)
