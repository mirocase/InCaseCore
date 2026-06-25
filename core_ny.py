import streamlit as st
from datetime import datetime
from pathlib import Path
import zoneinfo
import re

# Vremenska zona za Oslo
oslo_tz = zoneinfo.ZoneInfo("Europe/Oslo")

# 1. POSTAVLJANJE VAŠEG KOLESNOG IKONA NA VRH TAB-A PRETRAŽIVAČA
st.set_page_config(
    page_title="InCase CORE", 
    page_icon="Ikon-lys.png", 
    layout="centered"
)

# Definisanje putanja do novih fabričkih logotipa
logo_login = Path("Just inCase!.png")
logo_sidebar = Path("ICS-utenbord-lys@2x.png")

# CSS Stilovi za moderan izgled i jasne statuse
st.markdown("""
<style>
    /* Kontejneri za statuse sa terena */
    .status-u {background-color: #f0f7f4; border-left: 5px solid #00FF88; padding: 15px; border-radius: 4px; margin-bottom: 15px;}
    .status-ih {background-color: #fff5f5; border-left: 5px solid #FF4B4B; padding: 15px; border-radius: 4px; margin-bottom: 15px;}
    .status-vih {background-color: #fffde7; border-left: 5px solid #FBC02D; padding: 15px; border-radius: 4px; margin-bottom: 15px;}
    
    /* Krug koji se vrti na tajmeru */
    .spinner-container {display: flex; align-items: center; gap: 12px; background-color: #f0f7f4; border-left: 5px solid #00FF88; padding: 15px; border-radius: 4px; margin-top: 15px;}
    .loader-circle {border: 3px solid #f3f3f3; border-top: 3px solid #00FF88; border-radius: 50%; width: 22px; height: 22px; animation: spin 1s linear infinite;}
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Okvir za lepe podatke o kupcu */
    .kundeboks {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# --- INICIJALIZACIJA PODATAKA ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'v8_time_logs' not in st.session_state:
    st.session_state.v8_time_logs = []

# Baza kupaca izvučena direktno iz tvoje KI Liste
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
    "aleksander": {"password": "CoreAleks26!", "name": "Aleksander Gaupset"},
    "bojan": {"password": "CoreBojan26!", "name": "Bojan Jovanovic"},
    "ervin": {"password": "CoreErvin26!", "name": "Ervin Lasko"},
    "miroslav": {"password": "CoreMiro26!", "name": "Miroslav Dordevic"}
}

# --- LOGIN PROZOR SA NOVIM LOGO BANEROM ---
if not st.session_state.logged_in:
    if logo_login.exists():
        st.image(str(logo_login), use_container_width=True)
    else:
        st.markdown("<h1 style='color: #FF8C00; text-align: center;'>InCase CORE</h1>", unsafe_allow_html=True)
        
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

# --- BOČNA NAVIGACIJA SA FABRIČKIM LOGO-OM ---
with st.sidebar:
    if logo_sidebar.exists():
        st.image(str(logo_sidebar), use_container_width=True)
    else:
        st.markdown("<h2 style='color: #FF8C00; text-align: center;'>InCase System</h2>", unsafe_allow_html=True)
        
    st.write(f"👤 Logget inn: **{st.session_state.current_user}**")
    st.markdown("---")
    
    izbor_stranice = st.sidebar.radio(
        "Hovedmeny:",
        ["👤 Min Side", "📋 Kunde Liste (KL)", "⏱️ Reg. Tid", "👥 Brukere"]
    )
    
    st.markdown("---")
    if st.button("🚪 Logg ut", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- STRANICA 1: MIN SIDE ---
if izbor_stranice == "👤 Min Side":
    st.markdown(f"<h2>Velkommen, {st.session_state.current_user} 👋</h2>", unsafe_allow_html=True)
    st.write("Dette er ditt personlige dashbord.")
    st.info("Bruk menyen øverst til venstre for å navigere til Kunde Listen (KL) eller registrere timer.")

# --- STRANICA 2: KUNDE LISTE (KL) - MAKSIMALNA PRECIZNOST ---
elif izbor_stranice == "📋 Kunde Liste (KL)":
    st.markdown("<h2 style='color: #FF8C00;'>📋 Kunde Liste & Installasjon</h2>", unsafe_allow_html=True)
    st.write("Fase 2 - Installasjon direkte hos kunde (Koblet til KI liste).")
    
    projekat = st.selectbox("Velg aktivt prosjekt:", ["", "0114-KI-PLAN V2.0 (Markveien)"])
    
    if projekat:
        liste_imena = [f"{k['hnr']} - {k['navn']}" for k in st.session_state.mock_kunde_liste]
        izabrani_k_str = st.selectbox("Velg leilighet / kunde:", [""] + liste_imena)
        
        if izabrani_k_str:
            hnr_izbor = izabrani_k_str.split(" - ")[0]
            kunde_data = next(k for k in st.session_state.mock_kunde_liste if k["hnr"] == hnr_izbor)
            
            st.markdown(f"""
            <div class="kundeboks">
                <span style="color: #777; font-size: 11px; font-weight: bold;">VERIFIKASJON AV KUNDE:</span><br>
                <span style="font-size: 20px; font-weight: bold; color: #111;">👤 {kunde_data['navn']}</span><br>
                <span style="font-size: 15px; color: #333;">📍 <b>Adresse:</b> Oppgang {kunde_data['opg']}, Leil LNR {kunde_data['leil']}</span><br>
                <span style="font-size: 16px; color: #FF8C00;">🔑 <b>H-nummer:</b> {kunde_data['hnr']}</span><br>
                <span style="font-size: 14px; color: #555;">📞 <b>Tlf:</b> {kunde_data['tlf']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 🚦 Status på arbeid")
            status = st.radio(
                "Velg endelig status for kunden:",
                ["🟢 U (Utført)", "🔴 IH (Ikke Hjemme - Uvarslet)", "🟡 VIH (Varslet Ikke Hjemme)"],
                index=0
            )
            
            # 🟢 STATUS UTFERT (Zatvaranje posla sa proverama)
            if status == "🟢 U (Utført)":
                st.markdown("<div class='status-u'>🟢 <b>Status 'U' valgt:</b> Alle tekniske felt, fotodokumentasjon og signatur er påkrevd.</div>", unsafe_allow_html=True)
                
                mac_input = st.text_input("⌨️ MAC-adresse (Nøyaktig format)", placeholder="AA:BB:CC:DD:EE:FF").upper().strip()
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    sw_port = st.text_input("🔌 Switch Port (Kolone CG)", placeholder="Port 12")
                with col_p2:
                    odf_port = st.text_input("🎛️ ODF Port (Kolone CI)", placeholder="ODF 05")
                    
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    tx_1310 = st.text_input("📉 Demping 1310 nm (TX - Kolone BY)", placeholder="-7.25")
                with col_m2:
                    rx_1550 = st.text_input("📉 Demping 1550 nm (RX - Kolone CA)", placeholder="-7.33")
                
                st.markdown("#### 📸 Fotodokumentasjon (Obligatorisk)")
                bilde_mac = st.file_uploader("Ta bilde av MAC-etiketten på utstyret", type=["jpg", "jpeg", "png"], key="cam_mac")
                
                st.markdown("#### ✍️ Kunde Signatur (Obligatorisk)")
                bilde_signatur = st.file_uploader("Ta bilde av kundens fysiske signatur (eller signert skjema)", type=["jpg", "jpeg", "png"], key="cam_sig")
                k_navn_signatur = st.text_input("Skriv inn kundens fulle navn for digital verifikasjon:", placeholder="Fullt navn")
                
                error_found = False
                mac_pattern = re.compile(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$')
                if mac_input:
                    if not mac_pattern.match(mac_input):
                        st.error("❌ UGYLDIG MAC-ADRESSE! Formatet må være nøyaktig AA:BB:CC:DD:EE:FF (12 tegn).")
                        error_found = True
                else:
                    error_found = True
                    
                if not bilde_mac or not bilde_signatur or not sw_port or not odf_port or not tx_1310 or not rx_1550:
                    error_found = True
                
                if st.button("🚀 LAGRE OG LUKK POSAO", type="primary", disabled=error_found, use_container_width=True):
                    st.success(f"🎉 Installasjon fullført! Data sendt til tabell kolone AI, BY, CA, CC, CG, CI.")
                    # SMS SIMULACIJA (Poruka sa Google Review Linkom)
                    st.info(f"📲 Automatisert SMS sendt til {kunde_data['tlf']}: 'Takk for at du valgte InCase! Gi oss gjerne din tilbakemelding på Google...'")
                    st.balloons()
            
            # 🔴 STATUS IH (Nije kući - uvarslet)
            elif status == "🔴 IH (Ikke Hjemme - Uvarslet)":
                st.markdown("<div class='status-ih'>🔴 <b>Status 'IH' valgt:</b> Kunden var ikke hjemme (Uvarslet). Logges som bomtur.</div>", unsafe_allow_html=True)
                kommentar_ih = st.text_area("Skriv kort kommentar:")
                if st.button("Lagre status 'IH'", type="primary", use_container_width=True, disabled=not kommentar_ih):
                    st.error("🚨 Avvik registrert uvarslet i Excel.")
                    
            # 🟡 STATUS VIH (Otkazano na vreme)
            elif status == "🟡 VIH (Varslet Ikke Hjemme)":
                st.markdown("<div class='status-vih'>🟡 <b>Status 'VIH' valgt:</b> Kunden har varslet på forhånd. Ny avtale må gjøres.</div>", unsafe_allow_html=True)
                kommentar_vih = st.text_input("Ny avtale / Årsak:")
                if st.button("Lagre status 'VIH'", type="primary", use_container_width=True, disabled=not kommentar_vih):
                    st.warning("⚠️ Kansellering registrert varslet i Excel.")

# --- STRANICA 3: REGISTRER TID ---
elif izbor_stranice == "⏱️ Reg. Tid":
    st.subheader("Registrer Arbeidstid")
    if st.button("▶️ START TIMER", disabled=(st.session_state.timer_start is not None)):
        st.session_state.timer_start = datetime.now(oslo_tz)
        st.rerun()
    if st.button("⏹️ STOPP & LAGRE", disabled=(st.session_state.timer_start is None)):
        st.session_state.timer_start = None
        st.success("Tid lagret!")
        st.rerun()
        
    if st.session_state.timer_start:
        start_str = st.session_state.timer_start.strftime("%H:%M")
        st.markdown(f"""
        <div class="spinner-container">
            <div class="loader-circle"></div>
            <div style="color: #1e3a2f; font-weight: 500;">🟢 Tidsregistrering er aktiv... (Startet kl. {start_str})</div>
        </div>
        """, unsafe_allow_html=True)

# --- STRANICA 4: BRUKERE ---
elif izbor_stranice == "👥 Brukere":
    st.subheader("👥 Brukere")
    st.write("Kontaktinformasjon til montører.")