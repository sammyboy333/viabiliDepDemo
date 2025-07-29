import streamlit as st

def login_screen():
    """Display login screen with Google authentication button"""
    # Center the login panel
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(144, 238, 144, 0.3), rgba(25, 25, 112, 0.3));
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid rgba(25, 25, 112, 0.2);
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        ">
        """, unsafe_allow_html=True)
        
        st.header("Viabili ✅")
        st.subheader("Primer paso para analizar viabilidad")
        st.button("Iniciar sesión con Google", on_click=st.login, key="login_button")
        
        st.markdown("</div>", unsafe_allow_html=True)

def require_auth():
    """Check if user is authenticated and show login if not"""
    if not st.user.is_logged_in:
        login_screen()
        st.stop()
    
    # Silently check email domain
    email = getattr(st.user, "email", None)
    if not (isinstance(email, str) and email.endswith("@prima.ai")):
        st.error("Acceso denegado. Por favor, contacta a tu administrador.")
        st.button("Cerrar sesión", on_click=st.logout, key="access_denied_logout")
        st.stop()

def show_user_info(hide_welcome=False):
    """Display user information and logout option"""
    if not hide_welcome:
        st.header(f"¡Bienvenido, {st.user.name}!")

def show_user_sidebar():
    """Display user details and logout in sidebar"""
    with st.sidebar:
        st.markdown("---")  # Separator line
        st.write("**Información del Usuario:**")
        st.write(f"Nombre: {st.user.name}")
        st.write(f"Email: {st.user.email}")
        st.button("Cerrar sesión", on_click=st.logout, key="sidebar_logout")
