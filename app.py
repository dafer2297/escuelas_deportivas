import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración básica de la página
st.set_page_config(page_title="Generador de Artes Deportivos", layout="centered")

# --- FUNCIONES DE AYUDA ---

def formatear_celular(numero):
    # Asegura que solo haya números y formatea a: 096 888 6718
    num = ''.join(filter(str.isdigit, numero))
    if len(num) == 10:
        return f"{num[:3]} {num[3:6]} {num[6:]}"
    return numero

def generar_arte(datos):
    # 1. Cargar la imagen base
    base = Image.open("flyer_futbol.png").convert("RGBA")
    draw = ImageDraw.Draw(base)
    
    # 2. Cargar las fuentes (Asegúrate de que los nombres de los archivos coincidan)
    try:
        font_canton = ImageFont.truetype("Canaro-Black.ttf", 45) # Tamaño aproximado
        font_bold = ImageFont.truetype("Canaro-Bold.ttf", 40)
        font_medium = ImageFont.truetype("Canaro-Medium.ttf", 38)
    except OSError:
        st.error("❌ No se encontraron los archivos .ttf. Asegúrate de que estén en la misma carpeta.")
        return None

    # --- DIBUJAR CANTÓN Y RECUADRO ---
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
        
        # Posición del recuadro (Alineado a la derecha, ajusta 'y' si es necesario)
        pos_x_cuadro = 1080 - ancho_cuadro - 50 # 50px de margen derecho
        pos_y_cuadro = 450 # Ajusta esta altura según veas
        base.paste(recuadro, (pos_x_cuadro, pos_y_cuadro), recuadro)
        
        # Posición del texto centrada dentro del cuadro
        pos_x_texto = pos_x_cuadro + (padding_lateral // 2)
        # Ajuste vertical fino para que quede en el centro de los 66px
        pos_y_texto = pos_y_cuadro + 5 
        draw.text((pos_x_texto, pos_y_texto), texto_canton, font=font_canton, fill="white")
    except OSError:
        st.error("❌ No se encontró recuadro_transparente.png")

    # --- DIBUJAR DATOS INFERIORES ---
    # Coordenadas aproximadas (AJUSTA ESTOS VALORES)
    x_izq = 190  # Alineación izquierda (Celular y Nombre)
    x_der = 660  # Alineación derecha (Comunidad/GAD y Nombre)
    y_fila_1 = 1170 # Altura del celular y tipo de comunidad
    y_fila_2 = 1225 # Altura del nombre del profe y nombre de comunidad

    # Celular y Nombre Profe
    celular_formateado = formatear_celular(datos['celular'])
    draw.text((x_izq, y_fila_1), celular_formateado, font=font_bold, fill="white")
    draw.text((x_izq, y_fila_2), datos['nombre'], font=font_medium, fill="white")

    # Tipo de lugar y Nombre de lugar
    draw.text((x_der, y_fila_1), datos['tipo_lugar'], font=font_bold, fill="white")
    draw.text((x_der, y_fila_2), datos['nombre_lugar'], font=font_bold, fill="white")

    return base

# --- GESTIÓN DE PÁGINAS ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 1
if 'imagen_generada' not in st.session_state:
    st.session_state.imagen_generada = None

# --- PÁGINA 1: FORMULARIO ---
if st.session_state.pagina == 1:
    # CSS para el fondo azul y centrar logos (Opcional, mejora visual)
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("fondo_azul.png");
            background-size: cover;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
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
            nombre = st.text_input("Nombre y Apellido del Entrenador")
            celular = st.text_input("Número de Celular (10 dígitos)", max_chars=10)
            canton = st.text_input("Cantón")
            
            tipo_lugar = st.radio("Seleccione tipo:", ["Comunidad", "GAD"], horizontal=True)
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
                st.rerun()
