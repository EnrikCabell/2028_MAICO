import os
import base64
from io import BytesIO
import sqlite3
from contextlib import closing
from datetime import date, datetime, time

import pandas as pd
import psycopg
import streamlit as st

st.set_page_config(page_title="MAICO | Gestión de clientes", page_icon="🦻", layout="wide")

st.sidebar.image(
    BytesIO(base64.b64decode("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
dc916n++5eELOVWe4AA46AAAeGZlQw8Wy+zsiuzxfcj3MnxHqHnOV5tW/e6X
z275fsazO1y3kVORfPJvnda95ze7OsIynOMIJuUnsku9nBf8M6f07Hm2Lqx6
te/e+9lreRKTtd9Q0ONWjwdS3vpXSm18rx+ozh9FMXreB5jmvoL3mzrQ9Hij
GNfla1P1Fw8qeHlV319sXzXiu9G7x74ZFELqnvCa3R8+L7hrUPJ2vCtfVm96
9+5969p3c/XMX8acAEVQAAUPFn8nR9J+TMwafiz+To+k/JmYLY+Ja+rzhT+d
v+jX4mpMtwp/O3/Rr8TUmN/W8/EPVcvzLT7bk+vt0YetmGbbe7e7fazR8WXc
sehPt3m/wX5mcN4npjd9uYRlOcYQTlKT2SXezY6RpNen1Kc0pZEl1peHoRUc
MYity55EluqVtH/Z/saozvX41mfoACbYAAAAAAAAZzinMfveJB9vXn+SNGYb
V7nfquRPfdKfRXqXI3idrOr6QyXpmBPUcpVRfRguc5eC/UiGy4fxFjabCTXX
t68vy+4pq8ieZ2puLi04lKqogoxX3+lnsAQWAAAAAAqNa0eGZXK6iKjkRW/L
5fofpLcHZeOWdfOmmns1s13HMJShOM4PaUXun4MteI8RY+o+UgtoXLpe3vKg
vL2I2crfYOSszCqvXy4814PvBV8NSf8Mkt3srXt9SBCzlWlXhScU3+Twa6U+
ds+fqX/qLsyPE1/ldT8mnyqgl7Xz/Q7idrmr6VBoOFKN7b8hr4KUF+L/Iz5s
uH6PIaTU2udm837ez7im76YzPZr2J53ps3Fb2VdeP5r6jGH0Z8zC6rieZahb
Ul1G+lD1M5/O/ju5+vbQczzTUoKT2hb1Jfk/rNofOjcaTl+e6fXa310ujP1o
5/SfruL+JpScTZnkcKOPF9a58/9V2l2zDavl+e6jZYnvCPUh6kcxO13V5EM0
PC2HvKzLkuzqQ/Mz8IynOMILeUnsl4s3mDjRxMOqiPyI7N+L7ze764xme0Pi
Gjy2k2NLnU1Nezt+4xp9DtrjbVOuXwZxcX7T5/ZW6rZ1y7YScX7Dn87+O7i0
4av8lqnk2+VsXH2rmvzNefPsa54+TVcv8AtzUj6BFqUU1zTW6Of0nt3F9OQA
TbADiUlGLlJpRS3bfcBX61qHmGE3F+/WdWHo9PsMX6yZquc8/Nlbz8murWvB
fuQi+c8iWr2vfDxZ5mVXRX2yfN+C72buimGPRCqtbQgtkip4c0/wA3xfObI7
WXLlv3R7vrLonu9reZyBC1XBWfhTq5dNdaD8GTQYafOpRcJOMk1JPZp9zOYy
cJKUW1JPdNdzLzibT/ACdqzK11Z8rNu59z9pRHol7EbOVuNKzln4UbeXTXVm
vBk0xWi5/mGaum9qbOrP0eDNquZHU5VM3sAAZaUPFn8nR9J+TMwafiz+To+k
/JmYLY+Jb+rzhT+dv+jX4mpMtwp/O3/Rr8TUmN/W8/GT4pk3qcF3KpfiymLr
imO2o1y+dV+DZSlM/E9fWt4Xgo6W5d87G/yLgpuF5qWluPfCxr8y5I6+qz4A
A46AAAAAAAAHzy59K6xvvk3959DPnt8XDIti+1Ta+8p/Njbolu0vHkfQ4RUI
RiuxJJHzzfZp+D3PocJKcIyXZJJof0cw7AAmoAAAAAAAAouK4b4dE++Nm31r
9jLmn4rmlh0Q75Wb/Uv3MwWx8S39ajhr4tn9K/wQHDXxbP6V/ggT19anxeNq
KbfYubMBlXPIyrbn8ubkbHWr/N9KvkntKUegvW+RiDf85+ubrvVW7bYVx7Zy
UV7T6DXBV1xhHsikkY/h6jy2rQbXKpOb/BfibI5/S++O4+BR8T4nlcSOTFda
p7S/1f7l4dLa43VTrmt4zTTRiXl61Z189LrhjM8jmSxpPq3Ldf7L9ipyqJYu
TZRPthLb1+k612SqtjZB7Sg1JP0l7OxKeq2Wu5nmmmzcXtZZ1I+3tf1GKLLW
tRWoX1uG6rhBbL0vt/QrTmJyO6vauOG8Ty+e75LqUrdf7PsNcQNFw/M9NrjJ
bTn15+tk8lq9reZyBjOIKPIatY0uViU1+f3o2Zn+K6N6qMhL4MnB+3s/A7i8
pqemZNvomR5xpVEm95RXQfs5GJNHwpf1b8dvsamvwf5G9z0xi+2iABFUKDiX
UPJ1LDrfWsW89u6Ph7S4zMmGHi2X2fBgt9vF9yMJkXzyb53Wvec3uzeM9vWN
XjoT9FwPP81KS96r60/T4L2kBJykoxW7b2SXebfScBYGFGt/8AJLrTfpKb1y
M5nU3sXIyeq61kTzpxxL5Qqh1V0flPvZf6vLK8ylDDqlO2zq7prqrvZlv4Lq
P9rL61+pPEn2ta7+Ov8X1D+7s+tD+L6h/d2fWjt/BdR/tZfWv1H8F1H+1l9a
/Up/qz7eVupZt1cq7cmc4S5OL22ZGJ38F1H+1l9a/U62aTn1VyssxpKMVu3u
uSO9jnKhmr4c1DznG82sfvtK5b98f2Mme+Hkzw8qF9fbB9niu9HNTsM3lb8H
nj3wyaIXVPeE1uj0ILKHiz+To+l/JmYNPxZ/J0fSfkzLlsfEtfV7wp/O3/AE
a/E1JluFP52/6Nfiaknv63n4oOK6HKii9fIk4v2/8AwzJvc/FWZhW0P5ceT8
H3GDnCVc5QmtpRezT7mUxfXGNz31dcMZaqy548nsrlvH/Zfsao+dwlKE4zg3
GUXumu5my0jVa9QpUZNRyIrrQ8fSjO5+tYv4sgATbAAAAAAAADE65Q6NWvW3
Kb6a9v77m2KHijDdmPDKgudXKX+r/f8TeLys6nYy5s+H8tZOmwi316epL8vu
MaS9Mz56dlK2K6UHynHxX6lNTsYzeVugeWNk1ZVMbaZqUJd67j1IKgAAAAAA
VOtavDCrdNMlLIku75HpZ2TrlvFNxHlrI1HycXvGldH295Uhtttt7t9rO9NM
77oVVrec3si8nIlfdajhuqS0vpNcpWNr1cl+QLXGojjY1dMPgwikgQt7VZFH
xXftCjHT7W5v8ABfmZssdev8vq1uz3jXtBezt+8rS2ZyJavtpuFKOjRdkNfD
kor1L/AOmgIWkY/m2l0Vvt6PSfrfMmkdXtVk5AAHHWa4pxOjZXlxXKXUn6+4
z5vc/FjmYVtEvlLk/B9xgpRlCTjJbSi9mvBlsX1xLc9hP0XD881KuLW8Idef
qX7kA1vDWH5DA8vJde57/+Pcd1eRzM7VwACCwQtYx/OdLvgu1R6S9a5k04aT
Wz7GB86LHQb/IatTu9lPeD9vZ9+xEzKXjZl1L+RNperuPOEnCcZx+FFpr2Ho
vuIfK+iA86LVdRXbHsnFSXtIWtah5hhNwfv1nVh6PT7CHF1HxHqHnOV5tXL3
ul89u+X7FOPWemNjzysiFFS3lN7er0l5ORC+6uOGtP8te8uxdSt7Q375ePsN
SeWLjwxcaFFS2jBbL0+k9SFvatJyAAOOgAAHDSa2fNM5AGI1jAeBnSjFe9T6
1b9Hh7CCbfV8BZ+DKCXvketW/T4e0xDTi2mtmuTT7i+L2JanF7w1qHk7Xh2v
qze9fofh7TUHzqMnCSlFtST3TXczcaVnLPwo28vKLqzXgzG5+tZv4ruK/5Oj
6T8mZg0/Fn8nR9J+TMzGLlJRXa3sax8Z19XfCn87f9GvxNSZnSoOjMgsfqub
UZd+6NMT1e3qknIGc4j0ttvNojvy99iv8A9GjDW5yXlLOvnJ2hOVc1OEnGS5
pp7NGh1bh9uUr8BdvOVX6foZ6UZQm4zi4yXamtmi8sqVli5xOJcmpKORXG5L
5W/RkWEOJ8RrrVXRfhsn+ZlRGLlJRXa3scuI7NVrPdNhfMu+yv1HumwvmXfZ
X6mcycaNNUZKTb32e5GMzOa7dWNZ7psL5l32V+o902F8y77K/UzWLj+Wk3Jt
RXged0FXbKCe6T7x457w8rzrU+6bC+Zd9lfqeuLr2Ll5MKK4Wqc+zpRW34mO
JelzlVnQuit/J7v7thcSQmra2lmXRVPo2WxjJdzZ3arvq25TrmtvQ0UmDhzz
bXbc30N95P5z8C9jGMIqMVtFLZJElGI1XTp6dkuOzdUudcvR4eshG/ysarLo
lTfHpQl93pRktS0XIwZOcU7aPnpc160Wzrvqpazz4iYmZkYVnTx7HBvtXan6
0XdHFO0dsnG3fjW/yZnDk1cyuS2NWuJ8Lb/ju+yv1OfdNhfMu+yv1KKGDDod
dvpNdq7iA+TZiZzWrdRrPdNhfMu+yv1Ok+KMVLqU3Sfp2X5mWB3wjnnVxmcR
5V6caIxoi+9c5fWU7bk25Ntvm2+8HauudtihXCU5vsjFbs1JI5ba6Gp4d0t0
Q87vjtZNdSL+SvH1s66RoCplG/NSlNc419qj6X4l+T1rvqN5z+0ABNtl58M5
dk5TlkUuUnu+0V8L5Csi531OCa6SW/YagGvOs+MEtlsADLQAABn9Y0GzIyJZ
GH0elPnODe278UaAHZbPjlnWUw+HMqdyeWlVUnzSlu36ORqoxUIqMUlFLZJd
xyBbb9JOAAOOgAAotV0G3NzpZFNlcFKK3Ut+1EL3L5X9en7/0NUDU1Yz4xE0
zGtxMGui6UZyhuk49m3cVmqaLmahmSt8vUoLlCL35IvgclsvXefjK+5fL/AK
9P3/oWmjaM9OlZZdKM7Zck49iRbA7dWkzIAAy6AAAAAAAAFDqnD88vMlfj2Q
rU+coy37fEvgdls+OWdZX3L5X9en7ydpOk5emZLslfU6pLacVv7GXbaS3fJF
DnZ08qfk691Xvsku2R26tcmZHOvTqzqa6qrV0oT6Teza7NipqwFVKNjvhLZ/
BSaZeY+juUVK+bi38mPcQ87GWLf5OM+kmt+fccmrJx3k71I0arpZUrH2Qj97
Lqc41xcpyUYrvbK7TOjjafO+zkpNv2LkQbbr9RyFGKb3fVh3I46s56tjReyc
5emKO9Go498lGMnGT7FJbbkWvRY9H321t/4or8zGeJf5Ny3W26foA0pGysDG
zFtkUxm+6XY17RgWyuw65z5y22b8diSBQX8LVSe9GROHokukQLNJlp+RHp2x
sbW6SW2xrW1FNt7Jdpm8iyWXlyklu5PaK9BryrnjHgsGeoNU1yjGXwt5dhzP
hnJrg5yyKVGK3b5kzSX/18fTF/gSdYytkseD7ec/yQmrC5lU1VaqrUF3dr8T
19zuTke/RuqSs6yT35HEouL2ktmaN2xxsGM7HyjBL1vY5NWeyyVm7OG76oOV
mVRGPi9zzwsaOLlxlbbG2lPrxjF9b6yc3kalk7dr7l3RROhotfQ69snL0Lkd
urXPGJOJmY1qVdL6G3ZFrY9sjIhjV+Usb6O+3JbmeyaZYuRKty3ceaaLtx89
01KXwpwT9plp2x8+jJs6FbfS232a2JD2SbeyXfuZnHtePlQm+XRlzX4kzUs/
y78jS/e+9r5X7AdMyjR8mx7xlCbfw6lsQMvRqMe1wjmPfbfZ177fUy507Teh
tdeut2xj4es8NWx41W+V6bcrH2PuRqascuZVdTgZWU3VVlV77c30WuR2fC+U
v/AOin7y10SvaFtrXa+iiPqOfK6bqqe1S5Pb5X7Casc8YqLdJdT2eXTJ/4ps
61aapy2syYwXj0Gy8xdJnZBTuk4J9kUuZ3v0Z9tFnsmd86eMR8XhrFlFTsyZ
XRfzOSLKMMHTIbQjCrfwW8n+Z53WR0vCjXW+lZLs38e9ldjY12fdKTk9vlTZ
m212SRZfxjG322s9fRJdGRVkR6VUlJd670V9+jwjQ5VTk5pb7PsZB062VebX
0eyT6LXjucdaMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQdXtd
eG4p7Ob29neQtGpU75WSW6guXrZ764n5Ol9ybPHSMqunp12tR6T3Un2AXRm8
2zy2bZJc+tsvZyLnIz6KqpONsZS25KL35lNgV+Wza4vnz6T9nMCZqb8jiUYy
8N37CFj4+TZHymPGW3ZvF7EvW4vy9cu5x2+89dJy6oUOmyag0903yTAi+baj
4W/b/c6zws2b3nXOT7Ob3LizOxqo7u2L9EXuz0x74ZFKshvs/EBi1eQxq6++
K5+s9QAIGr5HksbycX1rOXs7yJo+P05TukuUV0V6yNnXPJzJOPNJ9GBe4tCx
8eFfelz9YFBh2rHyo2S7Ip8vYe2FRLOzHZZzin0pen0EWUG7nBLeXSaSXrNF
hYyxseMF8Ltk/FgUOa+lnXf7tEzWbNnVQuyMek0QZvp5bb361n5knWItZu77
JRWwHlRjZcodOiM+jLvjLbc9PNtR8Lft/uTdMzKVixqsnGEofOe25Iu1DGqj
v5RTfhF7sCnlg5k5Jzrm2+W7e5f1QVVUYLsikjim2N9MbIfBktyq1LUOm3RS
+r2Sku/wBAEXPdUsybpe8W+b7t+8maRi1yXl5NSknso/NI0NPseDO97ppbxj
4o50vJ8hk9GT6lnJ+vuAvyh1e3p5nR7oRS/MvW0k2+xGa55Wb9JP8AMCze+J
oq25SlH72Q9KpV2YnJbxgul7e4n6xBvBXRXKMlv6iBpeTDHvl5R7Rmtt/AC/
B4zy8eEek7obeh7nXFzK8pzVe/U8e8Cm1O3yudPwh1UXODSqMSuO2za3frZQ
ZcXHLuT7emy/py6J0xmrYJbc03tsB2y7PI4lk/CPL1lHptbszq1819J+w9tT
z45G1VT97T3b8SVpGK6q3dNbSmtkvBAWQAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAA8siiGRS659j7/AqpaLbu+jbBr07l0cAUy0W3ove2G/ctm
StP0+WLbKyyUZNrZbFgAPHJx4ZNTrs9aa7Uyrlot276NsGu7fcukAKaGi2dL
r2wS9CbLTGx4Y1Krr327W33s9QAPO+E50ThXJRlJbJvuO6OQKvE0qdORGy2c
JKPNJeJaAAQMbTvI5c7pyUubcEu7cngAVFWk2wyIzlZBxUt3tvuT8vEhl1qM
m01zUl3EgAUj0bI6WynW147s716LPf322KX+KLc5AiXYtiw1RizUO5uT7iLi
6Q67VO+UZJdkV3+stQAKe7R7HbKVU4KDe6T35FwAPCVVssN1Oa8o4dFy7tyH
haZPHyY22Ti1FckvEsjkDrOEbIOElvGS2aKm3Rp9L3q2PR8JdqLgAUn8Gu/q
V/eWGDgxxOk+m5Slyb7ESwBBztOWVLykJdCzbZ79jIX8Gv/qV/eXRyBXYuk1
1SU7peUku7bkWIOAOQAB//2Q
")),
    use_container_width=True,
)

st.markdown("""
<style>
/* Panel izquierdo: azul rey */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #173A8A 0%, #102B68 100%);
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [aria-checked="true"] {
    background-color: rgba(255,255,255,0.18);
    border-radius: 8px;
}
/* Panel derecho completo: gris */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main,
section.main > div {
    background-color: #D1D5DB !important;
}
[data-testid="stHeader"] {
    background-color: #D1D5DB !important;
}
/* Superficies de contenido */
[data-testid="stMetric"],
[data-testid="stForm"],
[data-testid="stExpander"],
div[data-testid="stDataFrame"] {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    padding: 8px;
}
h1, h2, h3, p, label, [data-testid="stMarkdownContainer"] {
    color: #1F2937;
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

st.title("MAICO")
st.caption("Gestión de clientes, estudios y citas")
if MODO_DEMO:
    st.warning("SISTEMA DE PRUEBA: los registros se guardan temporalmente en el archivo local de la aplicación. Configura PostgreSQL para conservarlos de forma permanente.")

menu = st.sidebar.radio("Panel", ["Panel", "Clientes", "Estudios", "Citas", "Buscar"])
clientes = consultar("SELECT id, nombre, telefono, correo FROM clientes ORDER BY nombre")

if menu == "Panel":
    a, b, c = st.columns(3)
    a.metric("Clientes registrados", int(consultar("SELECT COUNT(*) n FROM clientes").iloc[0,0]))
    b.metric("Estudios registrados", int(consultar("SELECT COUNT(*) n FROM estudios").iloc[0,0]))
    c.metric("Citas registradas", int(consultar("SELECT COUNT(*) n FROM citas").iloc[0,0]))
    st.subheader("Citas registradas")
    citas = consultar("""SELECT c.id, cl.nombre AS Cliente, c.fecha AS Fecha, c.hora AS Hora,
        c.motivo AS Motivo, c.estado AS Estado
        FROM citas c JOIN clientes cl ON cl.id=c.cliente_id
        ORDER BY c.fecha, c.hora""")
    st.dataframe(citas, use_container_width=True, hide_index=True)
    st.subheader("Clientes recientes")
    st.dataframe(consultar("SELECT id, nombre, telefono, correo FROM clientes ORDER BY id DESC LIMIT 8"),
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
    st.dataframe(consultar("SELECT id, nombre, telefono, correo, direccion, notas FROM clientes ORDER BY nombre"),
                 use_container_width=True, hide_index=True)
    if not clientes.empty:
        with st.expander("Editar o eliminar cliente"):
            elegido = st.selectbox("Cliente", clientes.itertuples(index=False), format_func=lambda x: f"{x.nombre} · ID {x.id}")
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
            guardar = st.form_submit_button("Guardar estudio", type="primary")
            if guardar:
                ejecutar("INSERT INTO estudios(cliente_id,fecha,tipo,resultado,observaciones) VALUES(?,?,?,?,?)",
                         (int(cli.id), fecha.isoformat(), tipo.strip(), resultado.strip(), observaciones.strip()))
                st.success("Estudio guardado.")
                st.rerun()
    st.subheader("Historial de estudios")
    estudios = consultar("""SELECT e.id, cl.nombre AS Cliente, e.fecha AS Fecha, e.tipo AS Estudio,
        e.resultado AS Resultados, e.observaciones AS Observaciones
        FROM estudios e JOIN clientes cl ON cl.id=e.cliente_id ORDER BY e.fecha DESC, e.id DESC""")
    st.dataframe(estudios, use_container_width=True, hide_index=True)

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
    agenda = consultar("""SELECT c.id, cl.nombre AS Cliente, cl.telefono AS Teléfono,
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
