import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Configuración básica de la página
st.set_page_config(page_title="Generador de Artes Deportivos", layout="centered")

# --- FUNCIONES DE AYUDA ---

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
    num = ''.join(filter(str.isdigit, numero))
    if len(num) == 10:
        return f"{num[:3]} {num[3:6]} {num[6:]}"
    return numero

def generar_arte(datos):
    try:
        base = Image.open("flyer_futbol.png").convert("RGBA")
        draw = ImageDraw.Draw(base)
    except OSError:
        st.error("❌ No se encontró flyer_futbol.png. Asegúrate de que esté en la misma carpeta.")
        return None
    
    try:
        # Cargamos las fuentes estáticas (para la parte de abajo)
        font_bold = ImageFont.truetype("Canaro-Bold.ttf", 40)
        font_medium = ImageFont.truetype("Canaro-Medium.ttf", 38)
    except OSError:
        st.error("❌ No se encontraron los archivos .ttf.")
        return None

    # --- DIBUJAR CANTÓN Y RECUADRO CON TAMAÑO DINÁMICO ---
    texto_canton = f"CANTÓN {datos['canton']}"
    
    # 1. Ajustes base del cuadro
    alto_cuadro = 66
    padding_lateral = 60
    ancho_maximo_cuadro = int(1080 * 0.4) # 4/10 del flyer (432px)
    ancho_maximo_texto = ancho_maximo_cuadro - padding_lateral
    
    # 2. Lógica para reducir la fuente si es muy grande
    font_size = 45 # Tamaño inicial
    try:
        font_canton = ImageFont.truetype("Canaro-Black.ttf", font_size)
    except OSError:
        st.error("❌ No se encontró Canaro-Black.ttf.")
        return None
        
    ancho_texto = int(draw.textlength(texto_canton, font=font_canton))
    
    # Mientras el texto sea más grande que el máximo permitido, bajamos el tamaño
    while ancho_texto > ancho_maximo_texto and font_size > 15:
        font_size -= 1
        font_canton = ImageFont.truetype("Canaro-Black.ttf", font_size)
        ancho_texto = int(draw.textlength(texto_canton, font=font_canton))

    # Calculamos el ancho final del cuadro
    ancho_cuadro = ancho_texto + padding_lateral
    
    # 3. Dibujar el recuadro
    try:
        recuadro = Image.open("recuadro_transparente.png").convert("RGBA")
        recuadro = recuadro.resize((ancho_cuadro, alto_cuadro))
        
        pos_y_cuadro = 470 
        # A 45px del borde derecho del flyer (1080 - ancho_cuadro - 45)
        pos_x_cuadro = 1080 - ancho_cuadro - 45 
        base.paste(recuadro, (pos_x_cuadro, pos_y_cuadro), recuadro)
        
        # 4. Dibujar el texto centrado
        pos_x_texto = pos_x_cuadro + (padding_lateral // 2)
        # Centrado vertical dinámico basado en el tamaño de la fuente actual
        pos_y_texto = pos_y_cuadro + (alto_cuadro - font_size) // 2
        draw.text((pos_x_texto, pos_y_texto), texto_canton, font=font_canton, fill="white")
    except OSError:
        st.error("❌ No se encontró recuadro_transparente.png")

    # --- DIBUJAR DATOS INFERIORES ---
    
    # --- IZQUIERDA (CELULAR Y NOMBRE) ---
    x_izq = 190  
    # Bajado 7px (Antes 1240, ahora 1247)
    y_izq_fila_1 = 1247
    celular_formateado = formatear_celular(datos['celular'])
    draw.text((x_izq, y_izq_fila_1), celular_formateado, font=font_bold, fill="white")

    # Bajado 7px (Antes 1285, ahora 1292)
    y_izq_fila_2 = 1292
    draw.text((x_izq, y_izq_fila_2), datos['nombre'], font=font_medium, fill="white")

    # --- DERECHA (TIPO Y NOMBRE LUGAR) ---
    x_der = 722
    
    # Lógica para mayúsculas/minúsculas de Comunidad/Liga/GAD
    if datos['tipo_lugar'] == "GAD":
        tipo_lugar_str = "GAD"
    elif datos['tipo_lugar'] == "LIGA":
        tipo_lugar_str = "Liga"
    else:
        tipo_lugar_str = "Comunidad"
        
    # Bajado 18px (Antes 1205, ahora 1223)
    y_der_fila_1 = 1223
    draw.text((x_der, y_der_fila_1), tipo_lugar_str, font=font_bold, fill="white")
    
    # Bajado 18px (Antes 1245, ahora 1263)
    y_der_fila_2 = 1263
    draw.text((x_der, y_der_fila_2), datos['nombre_lugar'], font=font_bold, fill="white")

    return base

# --- APLICAR FONDO AZUL ---
set_png_as_page_bg("fondo_azul.png")

# --- GESTIÓN DE PÁGINAS ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 1
if 'imagen_generada' not in st.session_state:
    st.session_state.imagen_generada = None

# --- PÁGINA 1: FORMULARIO ---
if st.session_state.pagina == 1:
    
    try:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("logo_arriba.png", use_container_width=True)
    except:
        pass 

    st.markdown("<h2 style='text-align: center; color: white;'>Generador de Artes</h2>", unsafe_allow_html=True)
    
    with st.container():
        col_img, col_form = st.columns([1, 2])
        
        with col_img:
            try:
                st.image("flyer_firma.png", use_container_width=True)
            except:
                st.write("(Imagen flyer_firma no encontrada)")
                
        with col_form:
            st.markdown("""<style>div[data-baseweb="input"] > div {color: white !important;}</style>""", unsafe_allow_html=True)
            
            nombre = st.text_input("Nombre y Apellido del Entrenador")
            celular = st.text_input("Número de Celular (10 dígitos)", max_chars=10)
            canton = st.text_input("Cantón")
            
            st.markdown("<p style='color: white;'>Seleccione tipo:</p>", unsafe_allow_html=True)
            tipo_lugar = st.radio("Tipo Lugar Label (Oculto)", ["Comunidad", "GAD", "LIGA"], horizontal=True, label_visibility="collapsed")
            nombre_lugar = st.text_input(f"Nombre del lugar (Ej: Sarayunga)")
            
            if st.button("Generar Arte 🎨", type="primary", use_container_width=True):
                if not nombre or not celular or not canton or not nombre_lugar:
                    st.warning("⚠️ Por favor, completa todos los campos antes de generar el arte.")
                elif len(''.join(filter(str.isdigit, celular))) != 10:
                    st.warning("⚠️ El número de celular debe tener exactamente 10 números.")
                else:
                    datos = {
                        "nombre": nombre.title(), 
                        "celular": celular,
                        "canton": canton.upper(), 
                        "tipo_lugar": tipo_lugar.upper(),
                        "nombre_lugar": nombre_lugar.title() 
                    }
                    
                    img = generar_arte(datos)
                    if img:
                        st.session_state.imagen_generada = img
                        st.session_state.pagina = 2
                        st.rerun()

# --- PÁGINA 2: RESULTADO ---
elif st.session_state.pagina == 2:
    st.markdown("<h2 style='text-align: center; color: white;'>¡Arte Generado Exitosamente! 🎉</h2>", unsafe_allow_html=True)
    
    if st.session_state.imagen_generada:
        st.image(st.session_state.imagen_generada, use_container_width=True)
        
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
                st.session_state.imagen_generada = None
                st.rerun()
