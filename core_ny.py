@@ -2,63 +2,50 @@
from datetime import datetime
from pathlib import Path
import zoneinfo
import re

# Postavljanje vremenske zone za Oslo da sat ne bi žurio
# Postavljanje vremenske zone za Oslo
oslo_tz = zoneinfo.ZoneInfo("Europe/Oslo")

st.set_page_config(page_title="InCase CORE", layout="centered")

logo_path = Path("logo.png")

# Moderniji i čistiji CSS stilovi (prilagođeni za mobilni telefon)
# CSS Stilovi optimizovani za mobilni telefon i jasne statuse
st.markdown("""
<style>
    .core-title {color: #FF8C00; font-size: 42px; font-weight: 900; letter-spacing: 5px; text-align: center; margin-bottom: 20px;}
    .login-box {background-color: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #eee;}
    .core-title {color: #FF8C00; font-size: 38px; font-weight: 900; letter-spacing: 4px; text-align: center; margin-bottom: 25px;}
    
    /* Stil za kružić koji se vrti */
    .spinner-container {display: flex; align-items: center; gap: 12px; background-color: #f0f7f4; border-left: 5px solid #00FF88; padding: 15px; border-radius: 4px; margin-top: 15px; margin-bottom: 15px;}
    /* Kontejneri za statuse sa terena */
    .status-u {background-color: #f0f7f4; border-left: 5px solid #00FF88; padding: 15px; border-radius: 4px; margin-bottom: 15px;}
    .status-ih {background-color: #fff5f5; border-left: 5px solid #FF4B4B; padding: 15px; border-radius: 4px; margin-bottom: 15px;}
    .status-vih {background-color: #fffde7; border-left: 5px solid #FBC02D; padding: 15px; border-radius: 4px; margin-bottom: 15px;}
    
    /* Krug koji se vrti na tajmeru */
    .spinner-container {display: flex; align-items: center; gap: 12px; background-color: #f0f7f4; border-left: 5px solid #00FF88; padding: 15px; border-radius: 4px; margin-top: 15px;}
    .loader-circle {border: 3px solid #f3f3f3; border-top: 3px solid #00FF88; border-radius: 50%; width: 22px; height: 22px; animation: spin 1s linear infinite;}
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

# Definisjon av alle aktiviteter
aktiviteter_mal = {
    "Dynamisk Plan": "Planlegging av arbeid og organisasjon",
    "HM": "Henting av materialer og utstyr for montering Fase 1",
    "HU": "Henting av utstyr for montering og aktivering Fase 2",
    "MN": "Montering av NODE",
    "BorDK": "Boring av hull (standard)",
    "BorHK": "Boring av hull for core-kabler",
    "MSW": "Montering av switch",
    "MP": "Montering av paneler og ODF",
    "MSS": "Skapmontering og kabelforberedelse",
    "Skjøting": "Splising av kabler",
    "FV": "Montering av plastkanaler, rør og fylling av hull",
    "Rengjøring": "Rengjøring etter arbeid"
}

# --- SIKKER INITIALISERING AV MINNE (v8) ---
# --- INICIJALIZACIJA PODATAKA ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None

if 'v8_projects' not in st.session_state:
    st.session_state.v8_projects = {
        "Markveien 56": {"allocated_hours": 40.0, "status": "Aktiv", "activities": {k: 0 for k in aktiviteter_mal}},
        "Projekt B": {"allocated_hours": 20.0, "status": "Aktiv", "activities": {k: 0 for k in aktiviteter_mal}},
        "Projekt C": {"allocated_hours": 15.0, "status": "Aktiv", "activities": {k: 0 for k in aktiviteter_mal}},
        "Glomma Bru": {"allocated_hours": 60.0, "status": "Aktiv", "activities": {k: 0 for k in aktiviteter_mal}}
    }

if 'v8_time_logs' not in st.session_state:
    st.session_state.v8_time_logs = []

# --- SVI RADNICI UBAČENI U SISTEM SA JAKIM ŠIFRAMA ---
# Baza kupaca izvučena direktno iz tvoje KI Liste (Primeri za test)
if 'mock_kunde_liste' not in st.session_state:
    st.session_state.mock_kunde_liste = [
        {"leil": "004", "opg": "22", "hnr": "H0104", "navn": "Louise Hestness Matthiessen", "tlf": "+47 913 XX XXX", "status": "Venter"},
        {"leil": "005", "opg": "22", "hnr": "H0105", "navn": "Gerd Eli Johansen", "tlf": "+47 986 XX XXX", "status": "Venter"},
        {"leil": "006", "opg": "22", "hnr": "H0201", "navn": "Thomas Rønbeck", "tlf": "+47 969 XX XXX", "status": "Venter"},
        {"leil": "007", "opg": "22", "hnr": "H0202", "navn": "Dordi Johanne Barlaup", "tlf": "+47 489 XX XXX", "status": "Venter"},
    ]

users = {
    "allan": {"password": "CoreAllan26!", "name": "Allan Gaupset"},
    "dejan": {"password": "CoreDejan26!", "name": "Dejan Kosanovic"},
@@ -68,12 +55,11 @@
    "miroslav": {"password": "CoreMiro26!", "name": "Miroslav Dordevic"}
}

# --- INNLØGGINGSSYSTEM ---
# --- LOGGING SYSTEM ---
if not st.session_state.logged_in:
    st.markdown("<div class='core-title'>InCase CORE</div>", unsafe_allow_html=True)
    st.subheader("🔑 Logg inn")
    
    username = st.text_input("Brukernavn (f.eks. fornavn)", placeholder="miroslav", key="login_user").lower()
    username = st.text_input("Brukernavn", placeholder="miroslav", key="login_user").lower()
    password = st.text_input("Passord", type="password", placeholder="••••", key="login_pass")

    if st.button("Logg inn", type="primary", use_container_width=True):
@@ -85,234 +71,147 @@
            st.error("Feil brukernavn eller passord")
    st.stop()

# --- BOČNA NAVIGACIJA (HAMBURGER MENI NA TELEFONU) ---
# --- BOČNA NAVIGACIJA (HAMBURGER MENI) ---
with st.sidebar:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("<h2 style='color: #FF8C00; text-align: center;'>InCase CORE</h2>", unsafe_allow_html=True)

    st.write(f"👤 Ulogget: **{st.session_state.current_user}**")
    st.write(f"👤 Logget inn: **{st.session_state.current_user}**")
    st.markdown("---")

    # Izbor stranica iz bočnog menija
    izbor_stranice = st.radio(
    izbor_stranice = st.sidebar.radio(
        "Hovedmeny:",
        [
            "👤 Min Side", 
            "📋 Reg. Aktivitet", 
            "⏱️ Reg. Tid",
            "📊 Prosjekter", 
            "✅ Historikk", 
            "👥 Brukere"
        ]
        ["👤 Min Side", "📋 Kunde Liste (KL)", "⏱️ Reg. Tid", "👥 Brukere"]
    )

    st.markdown("---")
    if st.button("🚪 Logg ut", use_container_width=True, type="secondary"):
    if st.button("🚪 Logg ut", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.timer_start = None
        st.rerun()

# --- PRIKAZ STRANICA NA OSNOVU IZBORA IZ MENIJA ---

# STRANICA 1: MIN SIDE
# --- STRANICA 1: MIN SIDE ---
if izbor_stranice == "👤 Min Side":
    st.markdown(f"<h2 style='color: #333;'>Velkommen, {st.session_state.current_user} 👋</h2>", unsafe_allow_html=True)
    st.write("Dette er ditt personlige dashbord for timeføring.")
    
    idag = datetime.now(oslo_tz).strftime("%Y-%m-%d")
    
    mine_timer_idag = sum(float(l["vanlig_tid"]) + float(l["overtid"]) for l in st.session_state.v8_time_logs if l["bruker"] == st.session_state.current_user and l["dato"] == idag)
    mitt_overtid_idag = sum(float(l["overtid"]) for l in st.session_state.v8_time_logs if l["bruker"] == st.session_state.current_user and l["dato"] == idag)
    st.markdown(f"<h2>Velkommen, {st.session_state.current_user} 👋</h2>", unsafe_allow_html=True)
    st.write("Dette er ditt personlige dashbord.")
    st.info("Bruk menyen øverst til venstre for å navigere til Kunde Listen (KL) eller registrere timer.")

# --- STRANICA 2: KUNDE LISTE (KL) ---
elif izbor_stranice == "📋 Kunde Liste (KL)":
    st.markdown("<h2 style='color: #FF8C00;'>📋 Kunde Liste & Installasjon</h2>", unsafe_allow_html=True)
    st.write("Fase 2 - Installasjon direkte hos kunde.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("Totalt jobbet i dag", f"{round(mine_timer_idag, 2)} t")
    with col_t2:
        st.metric("Herav overtid i dag", f"{round(mitt_overtid_idag, 2)} t")
    
    st.markdown("### Mine siste registreringer i dag")
    mine_logger_idag = [l for l in st.session_state.v8_time_logs if l["bruker"] == st.session_state.current_user and l["dato"] == idag]
    
    if not mine_logger_idag:
        st.info("Ingen timer registrert i dag ennå.")
    else:
        for log in mine_logger_idag:
            st.write(f"🏢 **{log['prosjekt']}** | {log['timer']} t totalt (Overtid: {log['overtid']} t)")

# STRANICA 2: REGISTRER AKTIVITET
elif izbor_stranice == "📋 Reg. Aktivitet":
    st.subheader("Registrer Aktivitet og Fremdrift")
    aktivne_opcije = [p for p, data in st.session_state.v8_projects.items() if data["status"] == "Aktiv"]
    izabrani_prosjekt = st.selectbox("Velg prosjekt", [""] + aktivne_opcije, index=0, key="sb_akt_projekt")
    projekat = st.selectbox("Velg aktivt prosjekt:", ["", "0114-KI-PLAN V2.0 (Markveien)"])

    if izabrani_prosjekt == "":
        st.info("💡 Vennligst velg et prosjekt fra menyen over for å starte.")
    else:
        st.markdown(f"### Aktiviteter for **{izabrani_prosjekt}**")
        st.write("Angi prosent fullført for hver oppgave:")
        
        trenutne_aktivnosti = st.session_state.v8_projects[izabrani_prosjekt]["activities"]
        novi_unosi = {}
        
        for akt, beskrivelse in aktiviteter_mal.items():
            st.markdown(f"**{akt}** — {beskrivelse}")
            prethodna_vrednost = trenutne_aktivnosti.get(akt, 0)
            novi_unosi[akt] = st.slider(
                "Prosent fullført (%)", 0, 100, int(prethodna_vrednost), key=f"sld_{izabrani_prosjekt}_{akt}"
            )
            st.markdown("---")
        
        if st.button("LAGRE AKTIVITET FOR PROSJEKT", type="primary", use_container_width=True):
            st.session_state.v8_projects[izabrani_prosjekt]["activities"] = novi_unosi
            st.success(f"✅ Daglig rapport lagret for prosjekt **{izabrani_prosjekt}**!")
            st.rerun()

# STRANICA 3: REGISTRER TID (KULTURNI SAT SA KRUŽIĆEM)
elif izbor_stranice == "⏱️ Reg. Tid":
    st.subheader("Registrer Arbeidstid")
    projekti_tid = [p for p, data in st.session_state.v8_projects.items() if data["status"] == "Aktiv"]
    izabrani_prosjekt_tid = st.selectbox("Velg prosjekt", [""] + projekti_tid, index=0, key="sb_tid_projekt")
    faza = st.selectbox("Fase", ["Fase 1", "Fase 2", "Annet"])

    if izabrani_prosjekt_tid == "":
        st.info("💡 Vennligst velg et prosjekt for å registrere tid.")
    else:
        st.markdown("#### Alternativ 1: Bruk stoppeklokke")
        col_start, col_stop = st.columns(2)
    if projekat:
        liste_imena = [f"{k['hnr']} - {k['navn']}" for k in st.session_state.mock_kunde_liste]
        izabrani_k_str = st.selectbox("Velg leilighet / kunde:", [""] + liste_imena)

        with col_start:
            # Dugme se gasi ako je već pokrenuto
            if st.button("▶️ START TIMER", use_container_width=True, disabled=(st.session_state.timer_start is not None)):
                st.session_state.timer_start = datetime.now(oslo_tz)
                st.rerun()
                    
        with col_stop:
            # Dugme se gasi ako tajmer nije ni pokrenut
            if st.button("⏹️ STOPP & LAGRE", use_container_width=True, disabled=(st.session_state.timer_start is None)):
                if st.session_state.timer_start is not None:
                    duration = datetime.now(oslo_tz) - st.session_state.timer_start
                    hours_spent = round(duration.total_seconds() / 3600, 2)
                    if hours_spent == 0:
                        hours_spent = round((duration.total_seconds() / 60) / 60, 2)
                    
                    idag = datetime.now(oslo_tz).strftime("%Y-%m-%d")
                    allerede_jobbet = sum(float(log.get("timer", 0)) for log in st.session_state.v8_time_logs if log["bruker"] == st.session_state.current_user and log["dato"] == idag)
                    
                    if allerede_jobbet + hours_spent > 8.0:
                        vanlig_tid = max(0.0, 8.0 - allerede_jobbet)
                        overtid = hours_spent - vanlig_tid
                    else:
                        vanlig_tid = hours_spent
                        overtid = 0.0
                    
                    log = {"prosjekt": izabrani_prosjekt_tid, "bruker": st.session_state.current_user, "dato": idag, "timer": round(hours_spent, 2), "vanlig_tid": round(vanlig_tid, 2), "overtid": round(overtid, 2), "fase": faza}
                    st.session_state.v8_time_logs.append(log)
                    st.success(f"✅ Lagret: {round(hours_spent, 2)} timer")
                    st.session_state.timer_start = None
                    st.rerun()

        # NOVI IZGLED AKTIVNOG SATA: Čist tekst i krug koji se vrti
        if st.session_state.timer_start:
            start_str = st.session_state.timer_start.strftime("%H:%M")
        if izabrani_k_str:
            hnr_izbor = izabrani_k_str.split(" - ")[0]
            kunde_data = next(k for k in st.session_state.mock_kunde_liste if k["hnr"] == hnr_izbor)
            
            st.markdown("""<style>.kundeboks {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 20px;}</style>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="spinner-container">
                <div class="loader-circle"></div>
                <div style="color: #1e3a2f; font-weight: 500; font-size: 15px;">
                    🟢 Tidsregistrering er aktiv... <br>
                    <span style="font-size: 13px; color: #555; font-weight: normal;">Arbeidet startet kl. {start_str}</span>
                </div>
            <div class="kundeboks">
                <span style="color: #777; font-size: 12px; font-weight: bold;">VERIFIKASJON AV KUNDE:</span><br>
                <span style="font-size: 20px; font-weight: bold; color: #111;">👤 {kunde_data['navn']}</span><br>
                <span style="font-size: 15px; color: #333;">📍 <b>Adresse:</b> Oppgang {kunde_data['opg']}, Leil LNR {kunde_data['leil']}</span><br>
                <span style="font-size: 16px; color: #FF8C00;">🔑 <b>H-nummer:</b> {kunde_data['hnr']}</span><br>
                <span style="font-size: 14px; color: #555;">📞 <b>Tlf:</b> {kunde_data['tlf']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Alternativ 2: Manuell registrering")
        manuelle_timer = str(st.text_input("Antall timer (f.eks. 7.5)", placeholder="7.5", key="manuell_inn")).replace(",", ".")
        
        if st.button("Lagre manuelle timer", type="secondary", use_container_width=True):
            if manuelle_timer:
                try:
                    t_float = float(manuelle_timer)
                    idag = datetime.now(oslo_tz).strftime("%Y-%m-%d")
                    allerede_jobbet = sum(float(log.get("timer", 0)) for log in st.session_state.v8_time_logs if log["bruker"] == st.session_state.current_user and log["dato"] == idag)
                    
                    if allerede_jobbet + t_float > 8.0:
                        vanlig_tid = max(0.0, 8.0 - allerede_jobbet)
                        overtid = t_float - vanlig_tid
                    else:
                        vanlig_tid = t_float
                        overtid = 0.0
                    
                    log = {"prosjekt": izabrani_prosjekt_tid, "bruker": st.session_state.current_user, "dato": idag, "timer": round(t_float, 2), "vanlig_tid": round(vanlig_tid, 2), "overtid": round(overtid, 2), "fase": faza}
                    st.session_state.v8_time_logs.append(log)
                    st.success(f"✅ Registrert {t_float} timer")
                    st.rerun()
                except ValueError:
                    st.error("Ugyldig tall format.")

# STRANICA 4: PROSJEKTER
elif izbor_stranice == "📊 Prosjekter":
    st.subheader("📊 Oversikt over Aktive Prosjekter og Produktivitet")
    aktive_p = {k: v for k, v in st.session_state.v8_projects.items() if v["status"] == "Aktiv"}
    
    if not aktive_p:
        st.info("Ingen aktive prosjekter akkurat nå.")
    else:
        for p_navn, p_data in aktive_p.items():
            brukte_timer = sum(float(log.get("timer", 0)) for log in st.session_state.v8_time_logs if log["prosjekt"] == p_navn)
            overtid_timer = sum(float(log.get("overtid", 0)) for log in st.session_state.v8_time_logs if log["prosjekt"] == p_navn)

            sve_aktivnosti = p_data.get("activities", {k: 0 for k in aktiviteter_mal})
            ukupni_progres = sum(sve_aktivnosti.values()) / len(sve_aktivnosti)
            
            if brukte_timer > 0:
                forventet_tid_hittil = (p_data['allocated_hours'] * ukupni_progres) / 100
                produktivitet_procent = (forventet_tid_hittil / brukte_timer) * 100
                produktivitet_str = f"{round(produktivitet_procent, 1)}%"
            else:
                produktivitet_str = "0%"
            
            st.markdown(f"<h3 style='color: #FF8C00;'>🏢 {p_navn}</h3>", unsafe_allow_html=True)
            
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.metric("Stipulert Tid", f"{p_data['allocated_hours']} t")
            with col_p2:
                st.metric("Faktisk Brukt Tid", f"{round(brukte_timer, 2)} t")
            with col_p3:
                st.metric("Produktivitet", produktivitet_str)
            st.markdown("---")

            st.write(f"**Total gjenomsnittlig fremdrift:** {round(ukupni_progres, 1)}%")
            st.progress(ukupni_progres / 100)
            st.caption(f"⏱️ *Herav automatisert overtid:* {round(overtid_timer, 2)} t (Beregnet for lønn i Google Sheets)")
            st.markdown("### 🚦 Status på arbeid")
            status = st.radio(
                "Velg endelig status for kunden:",
                ["🟢 U (Utført)", "🔴 IH (Ikke Hjemme - Uvarslet)", "🟡 VIH (Varslet Ikke Hjemme)"],
                index=0
            )

            with st.expander("Se detaljert status per aktivitet"):
                for akt_ime, procenat in sve_aktivnosti.items():
                    st.write(f"• {akt_ime}: **{procenat}%**")
            if status == "🟢 U (Utført)":
                st.markdown("<div class='status-u'>🟢 <b>Status 'U' valgt:</b> Alle tekniske felt, fotodokumentasjon og signatur er påkrevd.</div>", unsafe_allow_html=True)

            st.markdown("---")

# STRANICA 5: HISTORIKK
elif izbor_stranice == "✅ Historikk":
    st.subheader("✅ Fullførte Prosjekter (Historikk)")
    st.info("Historikk over fullførte prosjekter basert på avsluttede ordre.")
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
                k_navn_signatur = st.text_input("Skriv inn kundens fulle navn for digital signering:", placeholder="Fullt navn")
                
                error_found = False
                mac_pattern = re.compile(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$')
                if mac_input:
                    if not mac_pattern.match(mac_input):
                        st.error("❌ UGYLDIG MAC-ADRESSE! Formatet må være nøyaktig AA:BB:CC:DD:EE:FF (12 tegn).")
                        error_found = True
                else:
                    error_found = True
                    
                if not bilde_mac:
                    st.warning("⚠️ Fotodokumentasjon av MAC-adresse mangler.")
                    error_found = True
                if not bilde_signatur and not k_navn_signatur:
                    st.warning("⚠️ Kundens signatur mangler.")
                    error_found = True
                if not sw_port or not odf_port or not tx_1310 or not rx_1550:
                    st.warning("⚠️ Alle tekniske målinger og porter må fylles ut.")
                    error_found = True
                
                if st.button("🚀 LAGRE OG LUKK POSAO", type="primary", disabled=error_found, use_container_width=True):
                    st.success(f"🎉 Installasjon fullført for {kunde_data['navn']}! Lagret i kolone AI, BY, CA, CC, CG, CI.")
                    st.balloons()
            
            elif status == "🔴 IH (Ikke Hjemme - Uvarslet)":
                st.markdown("<div class='status-ih'>🔴 <b>Status 'IH' valgt:</b> Kunden var ikke hjemme (Uvarslet). Logges som bomtur.</div>", unsafe_allow_html=True)
                kommentar_ih = st.text_area("Skriv kort kommentar:")
                if st.button("Lagre status 'IH'", type="primary", use_container_width=True, disabled=not kommentar_ih):
                    st.error("🚨 Avvik registrert i Excel: Kunden var ikke hjemme.")
                    
            elif status == "🟡 VIH (Varslet Ikke Hjemme)":
                st.markdown("<div class='status-vih'>🟡 <b>Status 'VIH' valgt:</b> Kunden har varslet på forhånd. Ny avtale må gjøres.</div>", unsafe_allow_html=True)
                kommentar_vih = st.text_input("Ny avtale / Årsak:")
                if st.button("Lagre status 'VIH'", type="primary", use_container_width=True, disabled=not kommentar_vih):
                    st.warning("⚠️ Kansellering registrert i Excel: Kunden har varslet.")

# STRANICA 6: BRUKERE
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
    st.subheader("👥 Brukere og Kontaktinformasjon")
    kontakti = [
        ("Allan Gaupset", "+47 986 84 808", "allan@incase.no"),
        ("Dejan Kosanovic", "+47 969 49 938", "dejan@incase.no"),
        ("Aleksander Gaupset", "+47 913 72 639", "aleksanderg@incase.no"),
        ("Bojan Jovanovic", "+47 489 91 273", "bojan@incase.no"),
        ("Ervin Lasko", "+47 966 70 015", "ervin@incase.no"),
        ("Miroslav Dordevic", "+47 920 57 886", "miroslav@incase.no")
    ]
    for ime, tel, mail in kontakti:
        st.markdown(f"**{ime}**")
        st.write(f"📞 {tel} | ✉️ {mail}")
        st.markdown("---")

st.caption("InCase CORE v4.1 - Min Side Pilot")
    st.subheader("👥 Brukere")
    st.write("Kontaktinformasjon til montører.")