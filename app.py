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
    
    # 2. Cargar las fuentes
    try:
        font_canton = ImageFont.truetype("Canaro-Black.ttf", 45) 
        font_bold = ImageFont.truetype("Canaro-Bold.ttf", 40)
        font_medium = ImageFont.truetype("Canaro-Medium.ttf", 38)
    except OSError:
        st.error("❌ No se encontraron los archivos .ttf. Asegúrate de que estén en la misma carpeta.")
        return None

    # --- DIBUJAR CANTÓN Y RECUADRO ---
    texto_canton = f"CANTÓN {datos['canton']}"
    ancho_texto = int(draw.textlength(texto_canton, font=font_canton))
    padding_lateral = 60 
    ancho_cuadro = ancho_texto + padding_lateral
    alto_cuadro = 66
    
    try:
        recuadro = Image.open("recuadro_transparente.png").convert("RGBA")
        recuadro = recuadro.resize((ancho_cuadro, alto_cuadro))
        
        pos_y_cuadro = 470 
        pos_x_cuadro = 1080 - ancho_cuadro - 5
        base.paste(recuadro, (pos_x_cuadro, pos_y_cuadro), recuadro)
        
        pos_x_texto = pos_x_cuadro + (padding_lateral // 2)
        pos_y_texto = pos_y_cuadro + 10 
        draw.text((pos_x_texto, pos_y_texto), texto_canton, font=font_canton, fill="white")
    except OSError:
        st.error("❌ No se encontró recuadro_transparente.png")

    # --- DIBUJAR DATOS INFERIORES ---
    
    # --- IZQUIERDA (CELULAR Y NOMBRE) ---
    x_izq = 190  
    y_izq_fila_1 = 1240
    celular_formateado = formatear_celular(datos['celular'])
    draw.text((x_izq, y_izq_fila_1), celular_formateado, font=font_bold, fill="white")

    # Separado un poquito más (le sumé 12px más a la separación)
    y_izq_fila_2 = 1285
    draw.text((x_izq, y_izq_fila_2), datos['nombre'], font=font_medium, fill="white")

    # --- DERECHA (TIPO Y NOMBRE LUGAR) ---
    # Movido 20px a la izquierda (Antes 742, ahora 722)
    x_der = 722
    
    # Subido 25px (Antes 1230, ahora 1205)
    y_der_fila_1 = 1205
    draw.text((x_der, y_der_fila_1), datos['tipo_lugar'], font=font_bold, fill="white")
    
    # Juntos un poco más (Separación reducida de 55 a 40px) -> 1205 + 40 = 1245
    y_der_fila_2 = 1245
    draw.text((x_der, y_der_fila_2), datos['nombre_lugar'], font=font_bold, fill="white")

    return base

# --- APLICAR FONDO AZUL A TODA LA APP ---
# Al ponerlo aquí, afecta tanto a la página 1 como a la 2
set_png_as_page_bg("fondo_azul.png")

# --- GESTIÓN DE PÁGINAS ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 1
if 'imagen_generada' not in st.session_state:
    st.session_state.imagen_generada = None

# --- PÁGINA 1: FORMULARIO ---
if st.session_state.pagina == 1:
    
    # Mostrar logo principal centrado
    try:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("logo_arriba.png", use_container_width=True)
    except:
        pass 

    st.markdown("<h2 style='text-align: center; color: white;'>Generador de Artes</h2>", unsafe_allow_html=True)
    
    # Formulario
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
                        "nombre": nombre.title(), 
                        "celular": celular,
                        "canton": canton.upper(), 
                        "tipo_lugar": tipo_lugar.upper(), # Aseguramos que GAD/LIGA/COMUNIDAD salga en mayúsculas si hace falta
                        "nombre_lugar": nombre_lugar.title() 
                    }
                    
                    # Generar imagen
                    img = generar_arte(datos)
                    if img:
                        st.session_state.imagen_generada = img
                        st.session_state.pagina = 2
                        st.rerun()

# --- PÁGINA 2: RESULTADO ---
elif st.session_state.pagina == 2:
    # Título en blanco para que se vea sobre el fondo azul
    st.markdown("<h2 style='text-align: center; color: white;'>¡Arte Generado Exitosamente! 🎉</h2>", unsafe_allow_html=True)
    
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
                st.session_state.imagen_generada = None
                st.rerun()
