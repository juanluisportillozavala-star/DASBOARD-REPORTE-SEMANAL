import streamlit as st
from PIL import Image

# =====================================================
# CONFIGURACIÓN DE LA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Sistema Gerencial Liderza",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# ESTILOS
# =====================================================

st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
    max-width:1200px;
}

.titulo{
    font-size:40px;
    font-weight:bold;
    color:#0B2D5B;
    text-align:center;
}

.subtitulo{
    font-size:18px;
    color:gray;
    text-align:center;
}

.caja{
    background:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0px 0px 12px rgba(0,0,0,.12);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGO
# =====================================================

try:
    logo = Image.open("assets/logo.png")
    st.image(logo, width=250)
except:
    pass

# =====================================================
# TÍTULO
# =====================================================

st.markdown(
    '<p class="titulo">Sistema Gerencial Liderza</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitulo">Dashboard Empresarial</p>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# DESCRIPCIÓN
# =====================================================

st.info("""
Bienvenido al Sistema Gerencial de Liderza.

Este sistema permitirá analizar:

- 📊 Ventas
- 💰 Ingresos
- 💳 Cartera
- 📦 Inventario
- 🚚 Saldo Proveedor

Seleccione los archivos necesarios para comenzar.
""")

st.write("")

# =====================================================
# CARGA DE ARCHIVOS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    catalogo = st.file_uploader(
        "📁 Catálogo",
        type=["xlsx"]
    )

with col2:

    bd = st.file_uploader(
        "📊 Base de Datos de Ventas",
        type=["xlsx"]
    )

st.write("")

# =====================================================
# VALIDACIÓN
# =====================================================

if catalogo is not None:
    st.success("✅ Catálogo cargado")

if bd is not None:
    st.success("✅ Base de datos cargada")

st.write("")

# =====================================================
# BOTÓN
# =====================================================

if catalogo is not None and bd is not None:

    if st.button("🚀 Ingresar al Sistema", use_container_width=True):

        st.success("Versión 1.0 cargada correctamente.")

        st.balloons()

else:

    st.warning("Seleccione ambos archivos para continuar.")

# =====================================================
# PIE
# =====================================================

st.divider()

st.caption("Versión 1.0")