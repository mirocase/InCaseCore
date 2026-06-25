import streamlit as st
from datetime import datetime
from pathlib import Path
import zoneinfo
import re
import os

# Vremenska zona za Oslo
oslo_tz = zoneinfo.ZoneInfo("Europe/Oslo")

st.set_page_config(
    page_title="InCase CORE", 
    page_icon="Ikon-lys.png", 
    layout="centered"
)

# --- BEZBEDAN PRIKAZ SLIKA (Nikada ne može da sruši aplikaciju) ---
def bezbedan_prikaz_logotipa(ime_fajla):
    try:
        if os.path.exists(ime_fajla):
            st.image(ime_fajla, use_container_width=True)
    except:
        pass # Ako fajl fali, aplikacija kulira i ne izbacuje nikakvu crvenu grešku

# --- INICIJALIZACIJA PODATAKA ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None

if 'mock_kunde_liste' not in st.session_state:
    st.session_state.mock_kunde_liste = [
        {"leil": "004", "opg": "22", "hnr": "H0104", "navn": "Louise Hestness Matthiessen", "tlf": "+47 913 XX XXX"},
        {"leil": "005", "opg": "22", "hnr": "H0105", "navn": "Gerd Eli Johansen", "tlf": "+47 986 XX XXX"},
        {"leil": "006", "opg": "22", "hnr": "H0201", "navn": "Thomas Rønbeck", "tlf": "+47 969 XX XXX"},
        {"leil": "007", "opg": "22", "hnr": "H0202", "navn": "Dordi Johanne Barlaup", "tlf": "+47 489 XX XXX"},
    ]

users = {
    "allan": {"password": "CoreAllan26!", "name": "Allan Gaupset"},
    "dejan": {"password": "CoreDejan26!", "name": "Dejan Kosanovic"},
    "miroslav": {"password": "CoreMiro26!", "name": "Miroslav Dordevic"}
}

# --- LOGIN PROZOR ---
if not st.session_state.logged_in:
    bezbedan_prikaz_logotipa("Just inCase!.png")
    st.subheader("🔑 Logg inn")
    username = st.text_input("Brukernavn", placeholder="miroslav", key="login_user").lower()
    password = st.text_input("Passord", type="password", placeholder="••••", key="login_pass")
    
    if st.button("Logg inn", type="primary", use_container_width=True):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = users[username]["name"]
            st.rerun()
        else:
            st.error("Feil brukernavn eller passord")
    st.stop()

# --- BOČNA NAVIGACIJA (ČIST FABRIČKI STREAMLIT BEZ HAKOVANJA BOJA) ---
with st.sidebar:
    # Prikazujemo logo u meniju potpuno bezbedno
    bezbedan_prikaz_logotipa("ICS-utenbord-lys@2x.png")
    
    st.write(f"👤 Logget inn: **{st.session_state.current_user}**")
    st.markdown("---")
    
    izbor_stranice = st.sidebar.radio(
        "Hovedmeny:",
        ["👤 Min Side", "📋 Kunde Liste (KL)", "⏱️ Reg. Tid"]
    )
    
    st.markdown("---")
    if st.button("🚪 Logg ut", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- STRANICA: MIN SIDE ---
if izbor_stranice == "👤 Min Side":
    st.markdown(f"<h2>Velkommen, {st.session_state.current_user} 👋</h2>", unsafe_allow_html=True)
    st.write("Dette er ditt personlige dashbord.")

# --- STRANICA: KUNDE LISTE (KL) ---
elif izbor_stranice == "📋 Kunde Liste (KL)":
    st.markdown("<h2 style='color: #FF8C00;'>📋 Kunde Liste & Installasjon</h2>", unsafe_allow_html=True)
    
    projekat = st.selectbox("Velg aktivt prosjekt:", ["", "0114-KI-PLAN V2.0 (Markveien)"])
    
    if projekat:
        liste_imena = [f"{k['hnr']} - {k['navn']}" for k in st.session_state.mock_kunde_liste]
        izabrani_k_str = st.selectbox("Velg leilighet / kunde:", [""] + liste_imena)
        
        if izabrani_k_str:
            hnr_izbor = izabrani_k_str.split(" - ")[0]
            kunde_data = next(k for k in st.session_state.mock_kunde_liste if k["hnr"] == hnr_izbor)
            
            # Jednostavan i čist prikaz podataka o korisniku
            st.info(f"""
            👤 **Navn:** {kunde_data['navn']}  
            📍 **Adresse:** Oppgang {kunde_data['opg']}, Leil LNR {kunde_data['leil']}  
            🔑 **H-nummer:** {kunde_data['hnr']}  
            📞 **Tlf:** {kunde_data['tlf']}
            """)
            
            st.markdown("---")
            st.markdown("### 🚦 Status på arbeid")
            status = st.radio(
                "Velg endelig status for kunden:",
                ["🟢 U (Utført)", "🔴 IH (Ikke Hjemme - Uvarslet)", "🟡 VIH (Varslet Ikke Hjemme)"]
            )
            
            if status == "🟢 U (Utført)":
                st.success("🟢 Status 'U' valgt: Sene felt, fotodokumentasjon og signatur er påkrevd.")
                
                mac_input = st.text_input("⌨️ MAC-adresse", placeholder="AA:BB:CC:DD:EE:FF").upper().strip()
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    sw_port = st.text_input("🔌 Switch Port", placeholder="Port 12")
                with col_p2:
                    odf_port = st.text_input("🎛️ ODF Port", placeholder="ODF 05")
                    
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    tx_1310 = st.text_input("📉 Demping 1310 nm (TX)", placeholder="-7.25")
                with col_m2:
                    rx_1550 = st.text_input("📉 Demping 1550 nm (RX)", placeholder="-7.33")
                
                st.markdown("#### 📸 Fotodokumentasjon")
                bilde_mac = st.file_uploader("Ta bilde av MAC-etiketten", type=["jpg", "jpeg", "png"], key="cam_mac")
                
                st.markdown("#### ✍️ Kunde Signatur")
                bilde_signatur = st.file_uploader("Ta bilde av kundens signatur", type=["jpg", "jpeg", "png"], key="cam_sig")
                k_navn_signatur = st.text_input("Skriv inn kundens fulle navn:", placeholder="Fullt navn")
                
                error_found = False
                mac_pattern = re.compile(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$')
                if mac_input:
                    if not mac_pattern.match(mac_input):
                        st.error("❌ UGYLDIG MAC-ADRESSE!")
                        error_found = True
                else:
                    error_found = True
                    
                if not bilde_mac or not bilde_signatur or not sw_port or not odf_port or not tx_1310 or not rx_1550:
                    error_found = True
                
                if st.button("🚀 LAGRE OG LUKK POSAO", type="primary", disabled=error_found, use_container_width=True):
                    st.success(f"🎉 Installasjon fullført!")
                    st.balloons()
            
            elif status == "🔴 IH (Ikke Hjemme - Uvarslet)":
                st.error("🔴 Status 'IH' valgt: Logges som bomtur uvarslet.")
                kommentar_ih = st.text_area("Skriv kort kommentar:")
                if st.button("Lagre status 'IH'", type="primary", use_container_width=True, disabled=not kommentar_ih):
                    st.error("🚨 Avvik registrert.")
                    
            elif status == "🟡 VIH (Varslet Ikke Hjemme)":
                st.warning("🟡 Status 'VIH' valgt: Ny avtale må gjøres.")
                kommentar_vih = st.text_input("Ny avtale / Årsak:")
                if st.button("Lagre status 'VIH'", type="primary", use_container_width=True, disabled=not kommentar_vih):
                    st.warning("⚠️ Kansellering registrert.")

# --- STRANICA: REGISTRER TID ---
elif izbor_stranice == "⏱️ Reg. Tid":
    st.subheader("Registrer Arbeidstid")
    if st.button("▶️ START TIMER", disabled=(st.session_state.timer_start is not None)):
        st.session_state.timer_start = datetime.now(oslo_tz)
        st.rerun()
    if st.button("⏹️ STOPP & LAGRE", disabled=(st.session_state.timer_start is None)):
        st.session_state.timer_start = None
        st.success("Tid lagret!")
        st.rerun()