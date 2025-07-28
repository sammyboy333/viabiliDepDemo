import base64
from typing import Dict
import pandas as pd
import streamlit as st
from my_apis.ichigo_api import Ichigo
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from scripts.mps_finder import MPsFinder
from googleapiclient.discovery import Resource
from scripts.raw_mats_finder import RawMatFinder
from scripts.crm_salesforce import SalesforceCRM
from scripts.sku_matching import SkuMatcher
from scripts.fortacero_matcher import FortaceroMatcher
from scripts.collado_matcher import ColladoMatcher
from scripts.collado_controller import Collado

def open_styles(location='templates/style.css'):
    
    st.set_page_config(
        layout='wide', 
        initial_sidebar_state='expanded',
        page_title='Spikes',
        page_icon="https://cdn.prod.website-files.com/640617b2f45b42597a76b590/6679b53c57f0356096fe4b48_logo-footer.svg"
    )

    with open(location) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_fortacero_matcher() -> FortaceroMatcher:
    if 'fortacero_matcher' not in st.session_state or st.session_state.fortacero_matcher is None:
        matcher = load_matcher()
        fortacero_matcher = FortaceroMatcher(
            matcher=matcher,
            sheets_credentials='./templates/sheets_credentials.json',
            sheets_token='./templates/sheets_token.json',
            fortacero_cookies='./templates/fortacero_cookies.json'
        )
        st.session_state.fortacero_matcher = fortacero_matcher
    else:
        fortacero_matcher = st.session_state.fortacero_matcher
    return fortacero_matcher

def load_collado_matcher() -> ColladoMatcher:
    if 'collado_matcher' not in st.session_state or st.session_state.collado_matcher is None:
        matcher = load_matcher()
        collado_matcher = ColladoMatcher(
            matcher=matcher,
            collado=Collado(), # Without any input it will read environment variables
            sheets_credentials='./templates/sheets_credentials.json',
            sheets_token='./templates/sheets_token.json'
        )
        st.session_state.collado_matcher = collado_matcher
    else:
        collado_matcher = st.session_state.collado_matcher
    return collado_matcher
    
def display_user_picture():
    user_info : dict = st.session_state.user_info
    col_image, col_name = st.sidebar.columns((.15,.9))
    col_image.markdown(f'''
        <img src="{user_info['picture']}" style="border-radius:15%;">
    ''', unsafe_allow_html=True)
    col_name.markdown(f'''
        <p style="font-size:20px; vertical-align: text-top;"><b>{user_info['given_name']}</b></p>
    ''', unsafe_allow_html=True)

def add_description_to_page(text:str):
    st.sidebar.write(f'''
        <p class="paragraph" align="left">
            {text}
        </p>''',
    unsafe_allow_html=True)

def get_sheet_names(file):
    '''
    Función para sacar los nombres de las sheets en un excel file.

    :param file: bytes o path.
    :return: lista con los nombres
    '''
    return None
    return xl.load_workbook(file).sheetnames

def user_is_verified() -> bool:
    '''
    Esta función revisa que las credenciales ya estén cargadas
    '''
    if 'automations' not in st.session_state or st.session_state.automations is None:
        add_description_to_page('Para poder actualizar los campos disponibles, <b>carga tus credenciales primero</b>')
        st.error('Your credentials are not loaded yet')
        return False
    return True
    
def load_crm(load_raw_materials:bool=False, load_manufacturing:bool=False) -> SalesforceCRM:
    '''
    Solo llamar esta función si automations ya está cargada en session state
    '''
    automations = st.session_state.automations
    if 'crm' not in st.session_state or st.session_state.crm is None:
        # Construimos el crm
        new_crm = SalesforceCRM(
            sfc=automations.get_salesforce_connection(),
            load_raw_materials=load_raw_materials,
            load_manufacturing=load_manufacturing
        )
        st.session_state.crm = new_crm
        return new_crm
    else:
        return st.session_state.crm
    
def load_matcher() -> SkuMatcher:
    if (
        'matcher' not in st.session_state 
        or st.session_state.matcher is None
    ):
        ichigo = load_ichigo()
        matcher = SkuMatcher(ichigo=ichigo)
        st.session_state.matcher = matcher
    else:
        matcher = st.session_state.matcher
    return matcher
    
def show_errors(errors:list):
    if len(errors) == 0: return
    
    errors_df = pd.DataFrame(errors)[['Index']]
    st.markdown('##### Errores')
    st.dataframe(errors_df, use_container_width=True, hide_index=True)
    
def load_rawmat_finder() -> RawMatFinder:
    if 'rawmat_finder' not in st.session_state or st.session_state.rawmat_finder is None:
        rawmat_finder = RawMatFinder(
            sfc=st.session_state.automations.get_salesforce_connection(), 
            mbc=st.session_state.automations.get_metabase_connection()
        )
        st.session_state.rawmat_finder = rawmat_finder
        return rawmat_finder
    else:
        return st.session_state.rawmat_finder
    
def send_gmail_message(to:str, subject:str, body:str, sender:str=None, file:Dict=None):
    '''
    Esta función envía correos electrónicos usando el gmail del usuario.

    :param to: mail al que se le enviará el correo
    :param subject: subject of mail
    :param body: body of mail; html compatible

    :return: quién sabe
    '''
    def create_message(sender, to, subject, message_text, file:Dict=None):
        '''
        Función auxiliar para crear el encoding del correo de forma adecuada.

        Args:
            sender: sender of mail
            to: recipient of mail
            subject: subject of mail
            message_text: body of mail; html compatible
            file: dictionary with filename and content of file to attach to mail and file type
                {
                    'filename': 'filename.pdf',
                    'content': b'content of file',
                    'subtype': 'pdf'
                }

        Returns:
            dict with raw message
        '''
        msg = MIMEMultipart()
        msg['To'] = to
        msg['From'] = sender
        msg['Subject'] = subject

        msg.attach(MIMEText(message_text, 'html'))
        
        if file is not None:
            attachment = MIMEApplication(file['content'], _subtype=file['subtype'])
            attachment.add_header('Content-Disposition', 'attachment', filename=file['filename'])
            msg.attach(attachment)
            
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return {'raw': raw_message}
    
    service : Resource = st.session_state.gmail_service
    user_info = st.session_state.user_info

    if not sender:
        sender = user_info['email']

    # Honestamente no tengo idea qué es lo que regrese esta función
    a = service.users().messages().send(
        userId=user_info['id'],
        body=create_message(
            sender=sender, 
            to=to,
            subject=subject,
            message_text=body,
            file=file
        )
    ).execute()
    return a


def load_ichigo(
    bearer_token:str=None,
    bearer_token_file:str='templates/bearer_token.txt',
    connect_to:str='ichigo',
    force_reload:bool=False
) -> Ichigo:
    """
    This function loads the connection to Ichigo.
    Right now I still have to give it the location of the
    bearer token, but the idea is that it is able to load
    it by itself when I have an M2M authentication.

    :param bearer_token: the baerer token
    :param bearer_token_file: file with bearer token

    At least one of the parameters has to be different than None

    :return: connection to ichigo or None if connection was not sucessful
    """
    def write_bearer_token():
        bearer_token = st.text_area(
            label='Add your bearer token'
        )
        if st.button('Add token'):
            with open(bearer_token_file, 'w') as f:
                f.write(bearer_token)
                st.rerun()

    if (
        'ichigo' not in st.session_state 
        or st.session_state.ichigo is None 
        or force_reload
    ):
        if bearer_token is None:
            with open(bearer_token_file, 'r') as f:
                bearer_token = f.read().strip()

        try:
            ichigo = Ichigo(
                bearer_token=bearer_token,
                connect_to=connect_to,
                test_connection=True
            )
        except Exception as e:
            st.error(f'Connection to Ichigo was not successful: {e}')
            write_bearer_token()
            return None 
        st.session_state.ichigo = ichigo
    else:
        ichigo : Ichigo = st.session_state.ichigo
    return ichigo

    