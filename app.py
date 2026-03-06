import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Configuración básica de la página
st.set_page_config(page_title="Generador de Artes Deportivos", layout="centered")

# --- FUNCIONES DE AYUDA ---

# Función robusta para poner fondo con base64 (soluciona el problema de lectura)
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except OSError:
        return None

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    if bin_str:
        page_bg_img = '''
        <style>
        .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)

def formatear_celular(numero):
    # Asegura que solo haya números y formatea a: 096 888 6718
    num = ''.join(filter(str.isdigit, numero))
    if len(num) == 10:
        return f"{num[:3]} {num[3:6]} {num[6:]}"
    return numero

def generar_arte(datos):
    # 1. Cargar la imagen base
    try:
        base = Image.open("flyer_futbol.png").convert("RGBA")
        draw = ImageDraw.Draw(base)
    except OSError:
        st.error("❌ No se encontró flyer_futbol.png. Asegúrate de que esté en la misma carpeta.")
        return None
    
    # 2. Cargar las fuentes (Asegúrate de que los nombres de los archivos coincidan)
    try:
        font_canton = ImageFont.truetype("Canaro-Black.ttf", 45) # Tamaño aproximado
        font_bold = ImageFont.truetype("Canaro-Bold.ttf", 40)
        font_medium = ImageFont.truetype("Canaro-Medium.ttf", 38)
    except OSError:
        st.error("❌ No se encontraron los archivos .ttf. Asegúrate de que estén en la misma carpeta.")
        return None

    # --- DIBUJAR CANTÓN Y RECUADRO CON NUEVAS COORDENADAS ---
    texto_canton = f"CANTÓN {datos['canton']}"
    # Calcular el ancho del texto para redimensionar el recuadro
    ancho_texto = int(draw.textlength(texto_canton, font=font_canton))
    padding_lateral = 60 # Espacio a los lados del texto dentro del cuadro
    ancho_cuadro = ancho_texto + padding_lateral
    alto_cuadro = 66
    
    # Cargar y redimensionar el recuadro transparente
    try:
        recuadro = Image.open("recuadro_transparente.png").convert("RGBA")
        recuadro = recuadro.resize((ancho_cuadro, alto_cuadro))
        
        # --- NUEVAS COORDENADAS RECUADRO ---
        # 45px más a la derecha y 20px abajo.
        # Anterior y_cuadro era 450. Nueva 450+20 = 470
        pos_y_cuadro = 470 
        
        # Anterior x_cuadro era (1080 - ancho_cuadro - 50). 
        # Para mover 45px a la derecha, reducimos el margen derecho de 50 a 5.
        pos_x_cuadro = 1080 - ancho_cuadro - 5
        base.paste(recuadro, (pos_x_cuadro, pos_y_cuadro), recuadro)
        
        # Posición del texto centrada horizontalmente
        pos_x_texto = pos_x_cuadro + (padding_lateral // 2)
        # --- AJUSTE CENTRADO VERTICAL REAL ---
        # Alto cuadro es 66. Fuente 45. Margen superior = (66-45)/2 = 10.5. Usaremos 10.
        pos_y_texto = pos_y_cuadro + 10 
        draw.text((pos_x_texto, pos_y_texto), texto_canton, font=font_canton, fill="white")
    except OSError:
        st.error("❌ No se encontró recuadro_transparente.png")

    # --- DIBUJAR DATOS INFERIORES CON NUEVAS COORDENADAS ---
    x_izq = 190  # Alineación izquierda
    
    # --- NUEVAS COORDENADAS IZQUIERDA (CELULAR Y NOMBRE) ---
    # Celular: Bajar 70px. Anterior y_fila_1 = 1170. Nueva = 1170+70 = 1240.
    y_izq_fila_1 = 1240
    celular_formateado = formatear_celular(datos['celular'])
    draw.text((x_izq, y_izq_fila_1), celular_formateado, font=font_bold, fill="white")

    # Nombre: Separación reducida a 6/10 de la actual.
    # Separación anterior era 1225 - 1170 = 55.
    # Nueva separación = 55 * 0.6 = 33.
    # Nueva y_izq_fila_2 = y_izq_fila_1 + 33 = 1240 + 33 = 1273.
    y_izq_fila_2 = 1273
    draw.text((x_izq, y_izq_fila_2), datos['nombre'], font=font_medium, fill="white")

    # --- NUEVAS COORDENADAS DERECHA (TIPO Y NOMBRE LUGAR) ---
    # Mover 82px a la derecha y 60px más abajo.
    # Anterior x_der = 660. Nueva 660+82 = 742.
    x_der = 742
    
    # Anterior y_fila_1 = 1170. Nueva y_der_fila_1 = 1170+60 = 1230.
    y_der_fila_1 = 1230
    draw.text((x_der, y_der_fila_1), datos['tipo_lugar'], font=font_bold, fill="white")
    
    # Anterior y_fila_2 = 1225. Nueva y_der_fila_2 = 1225+60 = 1285.
    y_der_fila_2 = 1285
    draw.text((x_der, y_der_fila_2), datos['nombre_lugar'], font=font_bold, fill="white")

    return base

# --- GESTIÓN DE PÁGINAS ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 1
if 'imagen_generada' not in st.session_state:
    st.session_state.imagen_generada = None

# --- PÁGINA 1: FORMULARIO ---
if st.session_state.pagina == 1:
    # --- FONDO AZUL ROBUSTO ---
    # Lo ponemos dentro de la página 1 para que solo aparezca allí
    set_png_as_page_bg("fondo_azul.png")
    
    # Mostrar logo principal centrado
    try:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("logo_arriba.png", use_container_width=True)
    except:
        pass # Si no carga el logo, no detiene la app

    st.markdown("<h2 style='text-align: center; color: white;'>Generador de Artes</h2>", unsafe_allow_html=True)
    
    # Formulario
    with st.container():
        # Tratamos de simular el layout con flyer firma a la izquierda
        col_img, col_form = st.columns([1, 2])
        
        with col_img:
            try:
                st.image("flyer_firma.png", use_container_width=True)
            except:
                st.write("(Imagen flyer_firma no encontrada)")
                
        with col_form:
            # Estilo para los labels del formulario para que se lean sobre el azul
            st.markdown("""<style>div[data-baseweb="input"] > div {color: white !important;}</style>""", unsafe_allow_html=True)
            
            nombre = st.text_input("Nombre y Apellido del Entrenador")
            celular = st.text_input("Número de Celular (10 dígitos)", max_chars=10)
            canton = st.text_input("Cantón")
            
            # --- AGREGADO "LIGA" A LAS OPCIONES ---
            st.markdown("<p style='color: white;'>Seleccione tipo:</p>", unsafe_allow_html=True)
            tipo_lugar = st.radio("Tipo Lugar Label (Oculto)", ["Comunidad", "GAD", "LIGA"], horizontal=True, label_visibility="collapsed")
            nombre_lugar = st.text_input(f"Nombre de la {tipo_lugar} (Ej: Sarayunga)")
            
            if st.button("Generar Arte 🎨", type="primary", use_container_width=True):
                # Validaciones
                if not nombre or not celular or not canton or not nombre_lugar:
                    st.warning("⚠️ Por favor, completa todos los campos antes de generar el arte.")
                elif len(''.join(filter(str.isdigit, celular))) != 10:
                    st.warning("⚠️ El número de celular debe tener exactamente 10 números.")
                else:
                    # Guardar datos procesados
                    datos = {
                        "nombre": nombre.title(), # Cada inicio en mayúscula
                        "celular": celular,
                        "canton": canton.upper(), # Todo en mayúscula
                        "tipo_lugar": tipo_lugar,
                        "nombre_lugar": nombre_lugar.title() # Cada inicio en mayúscula
                    }
                    
                    # Generar imagen
                    img = generar_arte(datos)
                    if img:
                        st.session_state.imagen_generada = img
                        st.session_state.pagina = 2
                        st.rerun()

# --- PÁGINA 2: RESULTADO ---
elif st.session_state.pagina == 2:
    st.markdown("<h2 style='text-align: center;'>¡Arte Generado Exitosamente! 🎉</h2>", unsafe_allow_html=True)
    
    # Mostrar la imagen
    if st.session_state.imagen_generada:
        st.image(st.session_state.imagen_generada, use_container_width=True)
        
        # Preparar imagen para descarga
        buf = io.BytesIO()
        st.session_state.imagen_generada.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Descargar Flyer",
                data=byte_im,
                file_name="flyer_entrenamiento.png",
                mime="image/png",
                use_container_width=True
            )
        with col2:
            if st.button("⬅️ Volver y crear otro", use_container_width=True):
                st.session_state.pagina = 1
                # Limpiar imagen anterior al volver
                st.session_state.imagen_generada = None
                st.rerun()
