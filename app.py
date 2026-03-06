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
        st.error("❌ No se encontró flyer_futbol.png.")
        return None
    
    try:
        font_bold = ImageFont.truetype("Canaro-Bold.ttf", 40)
        font_medium = ImageFont.truetype("Canaro-Medium.ttf", 38)
    except OSError:
        st.error("❌ No se encontraron los archivos .ttf.")
        return None

    # --- DIBUJAR CANTÓN Y RECUADRO ---
    texto_canton = f"CANTÓN {datos['canton']}"
    
    alto_cuadro = 66
    padding_lateral = 60
    ancho_maximo_cuadro = int(1080 * 0.4) 
    ancho_maximo_texto = ancho_maximo_cuadro - padding_lateral
    
    font_size = 45 
    try:
        font_canton = ImageFont.truetype("Canaro-Black.ttf", font_size)
    except OSError:
        st.error("❌ No se encontró Canaro-Black.ttf.")
        return None
        
    ancho_texto = int(draw.textlength(texto_canton, font=font_canton))
    
    while ancho_texto > ancho_maximo_texto and font_size > 15:
        font_size -= 1
        font_canton = ImageFont.truetype("Canaro-Black.ttf", font_size)
        ancho_texto = int(draw.textlength(texto_canton, font=font_canton))

    ancho_cuadro = ancho_texto + padding_lateral
    
    try:
        recuadro = Image.open("recuadro_transparente.png").convert("RGBA")
        recuadro = recuadro.resize((ancho_cuadro, alto_cuadro))
        
        pos_y_cuadro = 470 
        pos_x_cuadro = 1080 - ancho_cuadro - 45 
        base.paste(recuadro, (pos_x_cuadro, pos_y_cuadro), recuadro)
        
        pos_x_texto = pos_x_cuadro + (padding_lateral // 2)
        pos_y_texto = pos_y_cuadro + (alto_cuadro - font_size) // 2
        draw.text((pos_x_texto, pos_y_texto), texto_canton, font=font_canton, fill="white")
    except OSError:
        st.error("❌ No se encontró recuadro_transparente.png")

    # --- DIBUJAR DATOS INFERIORES ---
    
    # --- IZQUIERDA (CELULAR Y NOMBRE) ---
    x_izq = 190  
    y_izq_fila_1 = 1247
    celular_formateado = formatear_celular(datos['celular'])
    draw.text((x_izq, y_izq_fila_1), celular_formateado, font=font_bold, fill="white")

    y_izq_fila_2 = 1292
    draw.text((x_izq, y_izq_fila_2), datos['nombre'], font=font_medium, fill="white")

    # --- DERECHA (TIPO Y NOMBRE LUGAR CON SALTO DE LÍNEA INTELIGENTE) ---
    x_der = 722
    # El ancho máximo permitido es el ancho total (1080) menos la posición de inicio (722) menos el margen derecho (45)
    max_ancho_der = 1080 - x_der - 45 # Equivale a 313px
    
    if datos['tipo_lugar'] == "GAD":
        tipo_lugar_str = "GAD"
    elif datos['tipo_lugar'] == "LIGA":
        tipo_lugar_str = "Liga"
    else:
        tipo_lugar_str = "Comunidad"
        
    # Lógica para dividir el nombre de la comunidad en líneas si es muy largo
    palabras = datos['nombre_lugar'].split()
    lineas_lugar = []
    linea_actual = ""

    for palabra in palabras:
        # Probamos cómo quedaría la línea si le sumamos la palabra actual
        prueba_linea = f"{linea_actual} {palabra}".strip()
        ancho_prueba = int(draw.textlength(prueba_linea, font=font_bold))
        
        if ancho_prueba <= max_ancho_der:
            # Si cabe, la añadimos a la línea actual
            linea_actual = prueba_linea
        else:
            # Si no cabe, guardamos la línea que teníamos y empezamos una nueva
            if linea_actual:
                lineas_lugar.append(linea_actual)
            linea_actual = palabra
            
    if linea_actual: # Guardar la última línea que se estaba armando
        lineas_lugar.append(linea_actual)

    # Calcular cuánto debemos subir los textos si hay más de 1 línea
    # Si ocupa 2 líneas, subimos todo 40px (altura de la letra aprox)
    ajuste_y = (len(lineas_lugar) - 1) * 40

    # Dibujar "Comunidad / GAD / Liga" con el ajuste
    y_der_fila_1 = 1223 - ajuste_y
    draw.text((x_der, y_der_fila_1), tipo_lugar_str, font=font_bold, fill="white")
    
    # Dibujar el nombre de la comunidad (línea por línea)
    y_der_fila_2 = 1263 - ajuste_y
    for linea in lineas_lugar:
        draw.text((x_der, y_der_fila_2), linea, font=font_bold, fill="white")
        y_der_fila_2 += 40 # Bajamos 40px para la siguiente línea de texto

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
