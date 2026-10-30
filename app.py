import os
import sqlite3
import base64
import html
from contextlib import closing
from datetime import date, datetime, time

import pandas as pd
import psycopg
import streamlit as st

st.set_page_config(page_title="MAICO | Gestión de clientes", page_icon="🦻", layout="wide")

st.sidebar.markdown("""
<div style="width:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:12px 4px 22px;">
  <svg viewBox="0 0 320 190" role="img" aria-label="MAICO de México" style="width:100%;max-width:260px;height:auto;">
    <path d="M92 8 Q160 -8 228 8 L228 100 Q160 128 92 100 Z" fill="#064675"/>
    <path d="M92 72 C116 72 119 31 140 31 S164 91 184 91 S210 31 228 31" fill="none" stroke="white" stroke-width="13" stroke-linecap="round"/>
    <text x="160" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="57" font-weight="600" letter-spacing="1" fill="#064675">MAICO</text>
    <text x="160" y="180" text-anchor="middle" font-family="Arial,sans-serif" font-size="25" font-style="italic" fill="#888888" stroke="#064675" stroke-width="1.8" stroke-linejoin="round" paint-order="stroke fill">de México</text>
  </svg>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<style>
:root { --maico-blue:#173A8A; --maico-deep:#102D67; }
[data-testid="stSidebar"] { background:#D1D5DB !important; border-right:1px solid #B7C0CC; }
[data-testid="stSidebar"] * { color:#1F2937 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { color:#1F2937 !important; }
[data-testid="stSidebar"] input[type="radio"] { accent-color:#173A8A !important; }
[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child { border:2px solid #173A8A !important; }
[data-testid="stSidebar"] [data-baseweb="radio"] input:checked + div,
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] > div:first-child { background:#173A8A !important; border-color:#173A8A !important; }
[data-testid="stSidebar"] [aria-checked="true"] { background:rgba(23,58,138,.10) !important; border-radius:9px; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], section.main, section.main > div { background:#173A8A !important; }
[data-testid="stHeader"] { background:#173A8A !important; box-shadow:none !important; border:0 !important; }
@media (max-width: 768px) { [data-testid="stHeader"] { background:#173A8A !important; box-shadow:none !important; border:0 !important; } }
.block-container { padding:2rem clamp(1rem, 3vw, 3rem) 3rem; max-width:1500px; }
h1,h2,h3,p,label,[data-testid="stMarkdownContainer"],[data-testid="stCaptionContainer"] { color:#FFFFFF !important; }
[data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"],
div[data-testid="stDataFrame"], [data-testid="stTable"] {
 background:transparent !important;
 background-color:transparent !important;
 border:1px solid rgba(255,255,255,.24) !important;
 border-radius:12px !important;
 padding:10px !important;
 box-shadow:none !important;
}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"] { color:#FFFFFF !important; }
[data-testid="stDataFrame"] [data-testid="stDataFrameResizable"],
[data-testid="stDataFrame"] iframe { background:transparent !important; }
[data-testid="stForm"] [data-testid="stVerticalBlock"],
[data-testid="stExpander"] details,
[data-testid="stMetric"] > div { background:transparent !important; }
.stButton > button, [data-testid="stFormSubmitButton"] > button { background:#D1D5DB !important; color:#173A8A !important; border:1px solid #D1D5DB !important; border-radius:9px !important; font-weight:700; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { background:#FFFFFF !important; color:#102D67 !important; }
input,textarea,[data-baseweb="select"] > div { border-radius:8px !important; }
.top-brand { display:flex; align-items:center; justify-content:flex-end; width:100%; margin:0 0 12px; position:relative; transform:translateY(70px); z-index:2; pointer-events:none; }
.top-brand-logo { display:block; width:174px; max-width:100%; height:auto; padding:5px 9px; background:#FFFFFF; border:1px solid #D1D5DB; border-radius:8px; box-sizing:border-box; }
.top-brand-logo svg { display:block; width:100%; height:auto; }
.legal-footer { margin-top:3.5rem; padding:22px 10px 10px; border-top:1px solid rgba(255,255,255,.24); text-align:center; color:#D1D5DB; font:italic 13px/1.65 Arial,sans-serif; }
.demo-warning { margin:0 0 1rem; padding:10px 14px; border:1px solid rgba(255,255,255,.35); border-radius:9px; background:rgba(255,255,255,.10); color:#FFFFFF; font-size:13px; }
@media (max-width: 768px) { .demo-warning { display:none !important; } }
@media (max-width: 768px) {
  .block-container { padding:1rem .75rem 2rem !important; }
  .top-brand { margin:0 0 8px !important; transform:none !important; }
  .top-brand-logo { width:118px; padding:3px 6px; }
  [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; gap:.65rem !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width:100% !important; width:100% !important; flex:1 1 100% !important; }
  [data-testid="stDataFrame"] { overflow-x:auto !important; }
  [data-testid="stDataFrame"] iframe { max-width:100% !important; }
  .legal-footer { font-size:10px; padding:18px 4px 8px; }
}
</style>
""", unsafe_allow_html=True)


def obtener_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            url = st.secrets.get("DATABASE_URL")
        except Exception:
            url = None
    return url

DATABASE_URL = obtener_url()
MODO_DEMO = not bool(DATABASE_URL)
DB_LOCAL = "maico_demo.db"

def conectar():
    if MODO_DEMO:
        con = sqlite3.connect(DB_LOCAL, check_same_thread=False)
        con.execute("PRAGMA foreign_keys = ON")
        return con
    return psycopg.connect(DATABASE_URL)

def inicializar():
    with closing(conectar()) as con:
        cur = con.cursor()
        if MODO_DEMO:
            cur.execute("""CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL, telefono TEXT, correo TEXT, direccion TEXT,
                notas TEXT, creado TEXT NOT NULL
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS estudios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
                fecha TEXT NOT NULL, tipo TEXT NOT NULL, resultado TEXT, observaciones TEXT
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
                fecha TEXT NOT NULL, hora TEXT NOT NULL, motivo TEXT,
                estado TEXT NOT NULL DEFAULT 'Pendiente', notas TEXT
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS archivos_estudio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudio_id INTEGER NOT NULL REFERENCES estudios(id) ON DELETE CASCADE,
                nombre TEXT NOT NULL, mime TEXT NOT NULL, contenido BLOB NOT NULL,
                creado TEXT NOT NULL
            )""")
        else:
            cur.execute("""CREATE TABLE IF NOT EXISTS clientes (
                id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                nombre TEXT NOT NULL, telefono TEXT, correo TEXT, direccion TEXT,
                notas TEXT, creado TEXT NOT NULL
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS estudios (
                id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                cliente_id BIGINT NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
                fecha TEXT NOT NULL, tipo TEXT NOT NULL, resultado TEXT, observaciones TEXT
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS citas (
                id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                cliente_id BIGINT NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
                fecha TEXT NOT NULL, hora TEXT NOT NULL, motivo TEXT,
                estado TEXT NOT NULL DEFAULT 'Pendiente', notas TEXT
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS archivos_estudio (
                id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                estudio_id BIGINT NOT NULL REFERENCES estudios(id) ON DELETE CASCADE,
                nombre TEXT NOT NULL, mime TEXT NOT NULL, contenido BYTEA NOT NULL,
                creado TEXT NOT NULL
            )""")
        con.commit()

def consultar(sql, params=()):
    with closing(conectar()) as con:
        if MODO_DEMO:
            return pd.read_sql_query(sql, con, params=params)
        with con.cursor() as cur:
            cur.execute(sql.replace("?", "%s"), params)
            filas = cur.fetchall()
            columnas = [d.name for d in cur.description] if cur.description else []
            return pd.DataFrame(filas, columns=columnas)

def ejecutar(sql, params=()):
    with closing(conectar()) as con:
        cur = con.cursor()
        if MODO_DEMO:
            cur.execute(sql, params)
            nuevo_id = cur.lastrowid
        else:
            cur.execute(sql.replace("?", "%s"), params)
            nuevo_id = None
            if sql.lstrip().upper().startswith("INSERT"):
                cur.execute("SELECT LASTVAL()")
                nuevo_id = cur.fetchone()[0]
        con.commit()
        return nuevo_id

try:
    inicializar()
except Exception as exc:
    st.error("No fue posible iniciar la base de datos. Revisa la conexión y la configuración.")
    st.exception(exc)
    st.stop()

st.markdown("""
<div class="top-brand" aria-label="MAICO de México">
  <div class="top-brand-logo">
    <svg viewBox="0 0 320 190" role="img" aria-label="MAICO de México">
      <path d="M92 8 Q160 -8 228 8 L228 100 Q160 128 92 100 Z" fill="#064675"/>
      <path d="M92 72 C116 72 119 31 140 31 S164 91 184 91 S210 31 228 31" fill="none" stroke="white" stroke-width="13" stroke-linecap="round"/>
      <text x="160" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="57" font-weight="600" letter-spacing="1" fill="#064675">MAICO</text>
      <text x="160" y="180" text-anchor="middle" font-family="Arial,sans-serif" font-size="25" font-style="italic" fill="#888888" stroke="#064675" stroke-width="1.8" stroke-linejoin="round" paint-order="stroke fill">de México</text>
    </svg>
  </div>
""", unsafe_allow_html=True)

st.title("MAICO")
st.caption("Gestión de clientes, estudios y citas")
if MODO_DEMO:
    st.markdown("""
    <div class="demo-warning">SISTEMA DE PRUEBA: los registros se guardan temporalmente en el archivo local de la aplicación. Configura PostgreSQL para conservarlos de forma permanente.</div>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("Panel", ["Panel", "Clientes", "Estudios", "Citas", "Buscar"])
clientes = consultar("SELECT id AS KEY, nombre, telefono, correo FROM clientes ORDER BY nombre")

if menu == "Panel":
    a, b, c = st.columns(3)
    a.metric("Clientes registrados", int(consultar("SELECT COUNT(*) n FROM clientes").iloc[0,0]))
    b.metric("Estudios registrados", int(consultar("SELECT COUNT(*) n FROM estudios").iloc[0,0]))
    c.metric("Citas registradas", int(consultar("SELECT COUNT(*) n FROM citas").iloc[0,0]))
    st.subheader("Citas registradas")
    citas = consultar("""SELECT c.id AS KEY, cl.nombre AS Cliente, c.fecha AS Fecha, c.hora AS Hora,
        c.motivo AS Motivo, c.estado AS Estado
        FROM citas c JOIN clientes cl ON cl.id=c.cliente_id
        ORDER BY c.fecha, c.hora""")
    st.dataframe(citas, use_container_width=True, hide_index=True)
    st.subheader("Clientes recientes")
    st.dataframe(consultar("SELECT id AS KEY, nombre, telefono, correo FROM clientes ORDER BY id DESC LIMIT 8"),
                 use_container_width=True, hide_index=True)

elif menu == "Clientes":
    st.subheader("Registrar cliente")
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre completo *")
        col1, col2 = st.columns(2)
        telefono = col1.text_input("Teléfono")
        correo = col2.text_input("Correo electrónico")
        direccion = st.text_area("Dirección")
        notas = st.text_area("Notas")
        guardar = st.form_submit_button("Guardar cliente", type="primary")
        if guardar:
            if not nombre.strip():
                st.error("Escribe el nombre del cliente.")
            else:
                ejecutar("INSERT INTO clientes(nombre,telefono,correo,direccion,notas,creado) VALUES(?,?,?,?,?,?)",
                         (nombre.strip(), telefono.strip(), correo.strip(), direccion.strip(), notas.strip(), datetime.now().isoformat(timespec="seconds")))
                st.success("Cliente guardado.")
                st.rerun()
    st.subheader("Directorio de clientes")
    st.dataframe(consultar("SELECT id AS KEY, nombre, telefono, correo, direccion, notas FROM clientes ORDER BY nombre"),
                 use_container_width=True, hide_index=True)
    if not clientes.empty:
        with st.expander("Editar o eliminar cliente"):
            elegido = st.selectbox("Cliente", clientes.itertuples(index=False), format_func=lambda x: f"{x.nombre} · KEY {x.id}")
            datos = consultar("SELECT nombre,telefono,correo,direccion,notas FROM clientes WHERE id=?", (int(elegido.id),)).iloc[0]
            with st.form("editar_cliente"):
                n = st.text_input("Nombre", datos["nombre"])
                t = st.text_input("Teléfono", datos["telefono"] or "")
                e = st.text_input("Correo", datos["correo"] or "")
                d = st.text_area("Dirección", datos["direccion"] or "")
                no = st.text_area("Notas", datos["notas"] or "")
                x1, x2 = st.columns(2)
                actualizar = x1.form_submit_button("Guardar cambios")
                eliminar = x2.form_submit_button("Eliminar cliente")
                if actualizar:
                    ejecutar("UPDATE clientes SET nombre=?,telefono=?,correo=?,direccion=?,notas=? WHERE id=?",
                             (n.strip(),t.strip(),e.strip(),d.strip(),no.strip(),int(elegido.id)))
                    st.success("Cambios guardados.")
                    st.rerun()
                if eliminar:
                    ejecutar("DELETE FROM clientes WHERE id=?", (int(elegido.id),))
                    st.success("Cliente eliminado junto con sus registros.")
                    st.rerun()

elif menu == "Estudios":
    st.subheader("Registrar estudio")
    if clientes.empty:
        st.info("Primero registra un cliente.")
    else:
        with st.form("nuevo_estudio", clear_on_submit=True):
            cli = st.selectbox("Cliente", clientes.itertuples(index=False), format_func=lambda x: x.nombre)
            fecha = st.date_input("Fecha del estudio", value=date.today())
            tipo = st.selectbox("Tipo de estudio", ["Audiometría", "Logoaudiometría", "Impedanciometría", "Timpanometría", "Emisiones otoacústicas", "Potenciales evocados", "Otro"])
            resultado = st.text_area("Resultados")
            observaciones = st.text_area("Observaciones")
            archivos = st.file_uploader(
                "Adjuntar archivos del estudio",
                type=["pdf", "png", "jpg", "jpeg", "webp", "doc", "docx", "xls", "xlsx", "csv"],
                accept_multiple_files=True,
                help="Adjunta audiometrías, informes, fotografías y documentos. Máximo 15 MB por archivo."
            )
            guardar = st.form_submit_button("Guardar estudio", type="primary")
            if guardar:
                estudio_id = ejecutar("INSERT INTO estudios(cliente_id,fecha,tipo,resultado,observaciones) VALUES(?,?,?,?,?)",
                         (int(cli.id), fecha.isoformat(), tipo.strip(), resultado.strip(), observaciones.strip()))
                for archivo in archivos or []:
                    if archivo.size > 15 * 1024 * 1024:
                        st.warning("Se omitió " + archivo.name + ": supera 15 MB.")
                        continue
                    ejecutar(
                        "INSERT INTO archivos_estudio(estudio_id,nombre,mime,contenido,creado) VALUES(?,?,?,?,?)",
                        (int(estudio_id), archivo.name, archivo.type or "application/octet-stream",
                         archivo.getvalue(), datetime.now().isoformat(timespec="seconds"))
                    )
                st.success("Estudio y archivos guardados.")
                st.rerun()
    st.subheader("Historial de estudios")
    estudios = consultar("""SELECT e.id AS KEY, cl.nombre AS Cliente, e.fecha AS Fecha, e.tipo AS Estudio,
        e.resultado AS Resultados, e.observaciones AS Observaciones
        FROM estudios e JOIN clientes cl ON cl.id=e.cliente_id ORDER BY e.fecha DESC, e.id DESC""")
    st.dataframe(estudios, use_container_width=True, hide_index=True)
    if not estudios.empty:
        st.markdown("**Archivos y vistas previas**")
        estudio_sel = st.selectbox(
            "Selecciona el estudio",
            estudios.itertuples(index=False),
            format_func=lambda x: f"{x.Fecha} · {x.Cliente} · {x.Estudio}",
            key="estudio_archivos"
        )
        adjuntos = consultar(
            "SELECT id,nombre,mime,contenido FROM archivos_estudio WHERE estudio_id=? ORDER BY id",
            (int(estudio_sel.id),)
        )
        if adjuntos.empty:
            st.info("Este estudio todavía no tiene archivos adjuntos.")
        else:
            for adj in adjuntos.itertuples(index=False):
                contenido = bytes(adj.contenido)
                mime = adj.mime or "application/octet-stream"
                st.markdown("**" + html.escape(adj.nombre) + "**")
                st.download_button(
                    "Abrir / descargar archivo", data=contenido, file_name=adj.nombre,
                    mime=mime, key="descargar_archivo_" + str(adj.id), use_container_width=True
                )
                if mime.startswith("image/"):
                    st.image(contenido, caption=adj.nombre, use_container_width=True)
                elif mime == "application/pdf":
                    pdf_b64 = base64.b64encode(contenido).decode("ascii")
                    st.markdown(
                        '<iframe title="' + html.escape(adj.nombre) + '" src="data:application/pdf;base64,' + pdf_b64 +
                        '" style="width:100%;height: min(75vh, 850px);border:0;border-radius:8px;"></iframe>',
                        unsafe_allow_html=True
                    )

elif menu == "Citas":
    st.subheader("Agendar cita")
    if clientes.empty:
        st.info("Primero registra un cliente.")
    else:
        with st.form("nueva_cita", clear_on_submit=True):
            cli = st.selectbox("Cliente", clientes.itertuples(index=False), format_func=lambda x: x.nombre)
            col1, col2 = st.columns(2)
            fecha = col1.date_input("Fecha", value=date.today())
            hora = col2.time_input("Hora", value=time(10,0), step=900)
            motivo = st.text_input("Motivo de la cita")
            estado = st.selectbox("Estado", ["Pendiente", "Confirmada", "Atendida", "Cancelada"])
            notas = st.text_area("Notas")
            guardar = st.form_submit_button("Guardar cita", type="primary")
            if guardar:
                ejecutar("INSERT INTO citas(cliente_id,fecha,hora,motivo,estado,notas) VALUES(?,?,?,?,?,?)",
                         (int(cli.id), fecha.isoformat(), hora.strftime("%H:%M"), motivo.strip(), estado, notas.strip()))
                st.success("Cita guardada.")
                st.rerun()
    st.subheader("Agenda")
    agenda = consultar("""SELECT c.id AS KEY, cl.nombre AS Cliente, cl.telefono AS Teléfono,
        c.fecha AS Fecha, c.hora AS Hora, c.motivo AS Motivo, c.estado AS Estado, c.notas AS Notas
        FROM citas c JOIN clientes cl ON cl.id=c.cliente_id ORDER BY c.fecha, c.hora""")
    st.dataframe(agenda, use_container_width=True, hide_index=True)
    if not agenda.empty:
        with st.expander("Modificar estado o eliminar cita"):
            cita = st.selectbox("Cita", agenda.itertuples(index=False),
                                format_func=lambda x: f"{x.Fecha} {x.Hora} · {x.Cliente} · {x.Motivo}")
            estado_nuevo = st.selectbox("Estado", ["Pendiente", "Confirmada", "Atendida", "Cancelada"],
                                        index=["Pendiente", "Confirmada", "Atendida", "Cancelada"].index(cita.Estado))
            z1,z2 = st.columns(2)
            if z1.button("Actualizar estado"):
                ejecutar("UPDATE citas SET estado=? WHERE id=?", (estado_nuevo, int(cita.id)))
                st.success("Estado actualizado.")
                st.rerun()
            if z2.button("Eliminar cita"):
                ejecutar("DELETE FROM citas WHERE id=?", (int(cita.id),))
                st.success("Cita eliminada.")
                st.rerun()

elif menu == "Buscar":
    st.subheader("Buscar información")
    termino = st.text_input("Nombre o teléfono del cliente")
    if termino.strip():
        patron = f"%{termino.strip()}%"
        encontrados = consultar("SELECT id,nombre,telefono,correo,direccion,notas FROM clientes WHERE nombre LIKE ? OR telefono LIKE ? ORDER BY nombre", (patron,patron))
        st.dataframe(encontrados, use_container_width=True, hide_index=True)
        if not encontrados.empty:
            ids = tuple(int(x) for x in encontrados["id"].tolist())
            marcas = ",".join("?" for _ in ids)
            st.markdown("**Estudios**")
            st.dataframe(consultar(f"""SELECT cl.nombre AS Cliente,e.fecha AS Fecha,e.tipo AS Estudio,e.resultado AS Resultados,e.observaciones AS Observaciones
                FROM estudios e JOIN clientes cl ON cl.id=e.cliente_id WHERE e.cliente_id IN ({marcas}) ORDER BY e.fecha DESC""", ids),
                use_container_width=True, hide_index=True)
            st.markdown("**Citas**")
            st.dataframe(consultar(f"""SELECT cl.nombre AS Cliente,c.fecha AS Fecha,c.hora AS Hora,c.motivo AS Motivo,c.estado AS Estado,c.notas AS Notas
                FROM citas c JOIN clientes cl ON cl.id=c.cliente_id WHERE c.cliente_id IN ({marcas}) ORDER BY c.fecha,c.hora""", ids),
                use_container_width=True, hide_index=True)

st.markdown("""
<div class="legal-footer">
  Initial code and all additional changes are property and registered by<br>
  Juan Enrique Cabello Vargas, PhD &amp; MSc.<br>
  Conceptualized and created by<br>
  Juan Enrique Cabello Vargas, PhD &amp; MSc.<br>
  All rights reserved.<br>
  Pax et Bonum.
</div>
""", unsafe_allow_html=True)
