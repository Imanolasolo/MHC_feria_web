import streamlit as st
from streamlit_option_menu import option_menu
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI 
from htmlTemplates import css, bot_template, user_template
import os
import urllib.parse

# Configuración de la página
st.set_page_config(
    page_title="Manta Hospital Center",
    page_icon="🏥",
    layout="wide"
)

# Function to extract text from a PDF file
def get_pdf_text(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text = ""
    # Iterate through each page and extract text
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to split the extracted text into manageable chunks for processing
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Function to generate a vector store using the text chunks
def get_vector_store(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPEN_AI_APIKEY"])
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Function to create a conversational chain using the vector store
def get_conversation_chain(vector_store):
    llm = ChatOpenAI(openai_api_key=st.secrets["OPEN_AI_APIKEY"])
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory
    )
    return conversation_chain

# Function to handle user input and generate responses
def handle_user_input(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    # Display the conversation history
    for i, msg in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", msg.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", msg.content), unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_of_bin_file('MHC_.jpg')

st.markdown(
    f"""
    <style>
    .stApp {{
        background: url('data:image/jpeg;base64,{img_base64}') no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

selected = option_menu(
    menu_title='Manta Hospital Center',
    options=["Inicio", "¿Quienes somos?", "¿Qué hacemos?", "Interactúa con nosotros"],  # Opciones del menú
    icons=["house", "info-circle", "envelope"],  # Iconos para las opciones
    menu_icon="cast",  # Icono del menú
    default_index=0,  # Opción seleccionada por defecto
    orientation="horizontal",  # Menú horizontal
)

if selected == "Inicio":
    st.title("Bienvenidos a MHC")
    st.subheader("Tu salud es nuestra misión, tu bienestar es nuestro compromiso.")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info ('Innovación en cada latido, cuidado en cada paso.')
        st.info('Transformando la salud de la comunidad, un paciente a la vez.')
        st.info('Tu salud, nuestra prioridad, siempre.')
    with col2:
        st.image('Edificio_hospital.jpg', width=300)

elif selected == "¿Quienes somos?":
        st.title("Misión y Visión", help=('MHC, compromiso y profesionalidad'))
        st.info("Dedicados a la excelencia en salud desde [año de fundación], en el Manta Hospital Center estamos comprometidos con el bienestar de nuestra comunidad.")
        col1, col2, col3 = st.columns (3)
        with col1:
             st.info('Misión: Ofrecer atención médica integral y de calidad.')
             st.image('calidad_hospital.jpg', width=300, use_column_width='auto')
        with col2:
             st.info('Visión: Ser líderes en el cuidado de la salud en nuestra región.')
             st.image('pasion_salud.jpg', use_column_width='auto')
        with col3:
             st.info('Valores: Compromiso, integridad, y empatía con nuestros pacientes.')
             st.image('compromiso_salud.jpg',use_column_width='auto')
elif selected == "¿Qué hacemos?":
    st.title("Servicios MHC")
    col1, col2 = st.columns(2)

# Colocar la lista de servicios en la primera columna
    with col1:
        st.subheader("Nuestros Servicios")
        servicios = [
            "Emergencias 24/7",
            "Consultas Externas",
            "Hospitalización",
            "Unidad de Cuidados Intensivos (UCI)",
            "Quirófanos",
            "Laboratorio Clínico",
            "Imagenología",
            "Cardiología",
            "Pediatría",
            "Ginecología y Obstetricia",
            "Traumatología",
            "Cirugía General",
            "Fisioterapia y Rehabilitación",
            "Dermatología",
            "Endocrinología",
            "Gastroenterología",
            "Neurología",
            "Nutrición y Dietética",
            "Odontología",
            "Psicología",
            "Psiquiatría",
    ]
        for servicio in servicios:
            st.write("- " + servicio)

    # Colocar el video en la segunda columna
    with col2:
        st.subheader("Conozca más sobre Manta Hospital Center")
         # Ruta local del archivo de video
        video_path = "MHC_video_pres_1.mp4"
        
        # Mostrar el video
        # Ajustar el tamaño del video utilizando un contenedor con CSS personalizado
        st.markdown(
            f"""
            <style>
            .video-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
            }}
            video {{
                width: 80%;  /* Ajusta el porcentaje para cambiar el tamaño */
                height: auto;
            }}
            </style>
            <div class="video-container">
                <video controls>
                    <source src="data:video/mp4;base64,{base64.b64encode(open(video_path, 'rb').read()).decode()}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """,
            unsafe_allow_html=True
        )
        

elif selected == "Interactúa con nosotros":
    st.title("Comunícate con nosotros")
    st.success('Queremos conocerte, que formes parte de la familia MHC, anímate y contacta o interactúa con nosotros en nuestras redes o nuestra novedosa asistente virtual Macy!')
    col1, col2, col3 = st.columns(3)

    with col1:
         with st.form(key='contact_form'):
            contact_reason = st.selectbox("Razón de contacto:", ["Hospitalización", "Cirugía", "Consulta médica", "Información general"])
            contact_info = st.text_input("Su info de contacto (WhatsApp o email):")
            message = st.text_area("Su mensaje:")
        
            submit_button = st.form_submit_button(label='Enviar')
        
            if submit_button:
                if contact_info and message:
                    try:
                        # Configurar y enviar el correo electrónico
                        email_recipient = "jjusturi@gmail.com"  # Reemplaza con el correo de destino
                        email_subject = f"Contact Form Submission: {contact_reason}"
                        email_body = f"Razón: {contact_reason}\nContacto: {contact_info}\nMensaje: {message}"
                
                        msg = MIMEMultipart()
                        msg['From'] = contact_info
                        msg['To'] = email_recipient
                        msg['Subject'] = email_subject
                        msg.attach(MIMEText(email_body, 'plain'))
                
                        # Configurar el servidor SMTP
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(st.secrets["smtp"]["username"], st.secrets["smtp"]["password"])
                        server.sendmail(contact_info, email_recipient, msg.as_string())
                        server.quit()
                
                        st.success("¡Tu mensaje ha sido enviado exitosamente!")
                    except Exception as e:
                        st.error(f"Error al enviar el mensaje: {e}")
            else:
                st.warning("Por favor, completa toda la información antes de enviar el formulario.")

    with col2:
        st.info("¿Quieres saber más sobre Manta Hospital Center y nuestros servicios? ¡Estamos aquí para ayudarte!")
        whatsapp_link = "https://wa.me/593993513082?text=Quiero%20más%20información%20sobre%20MHC%20y%20sus%20servicios."
        if st.button("Contáctanos por WhatsApp"):
            js = f"window.open('{whatsapp_link}')"
            st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button>Quiero más información</button></a>', unsafe_allow_html=True)

    with col3:
        # Section for interacting with the AI chatbot
        st.info("Chatea con nosotros, queremos saber de ti!")
        st.success("No importa el idioma, somos multiculturales!")

    # Process the PDF file to be used as context for the chatbot
        pdf_path = os.path.join(os.getcwd(), "Base_conocimiento_MHC1.pdf")
        pdf_text = get_pdf_text(pdf_path)
        text_chunks = get_text_chunks(pdf_text)
        vector_store = get_vector_store(text_chunks)
        conversation_chain = get_conversation_chain(vector_store)

    # Store the conversation chain and history in session state
        st.session_state.conversation = conversation_chain
        st.session_state.chat_history = []

    # Input box for user questions
        user_question = st.text_input("Hola soy Macy, tu asistente del MHC, en que te puedo ayudar?")
        if user_question:
            handle_user_input(user_question)

                