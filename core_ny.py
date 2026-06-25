import streamlit as st
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="InCase CORE", layout="centered")

logo_path = Path("logo.png")

# CSS-stiler
st.markdown("""
<style>
    .core-text {color: #FF8C00; font-size: 75px; font-weight: 900; letter-spacing: 18px; margin-top: -45px; text-align: center;}
    .start-time {font-size: 24px; font-weight: bold; color: #00FF88; text-align: center; margin-top: 10px;}
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
users = {
    "allan": {"password": "CoreAllan26!", "name": "Allan Gaupset"},
    "dejan": {"password": "CoreDejan26!", "name": "Dejan Kosanovic"},
    "aleksander": {"password": "CoreAleks26!", "name": "Aleksander Gaupset"},
    "bojan": {"password": "CoreBojan26!", "name": "Bojan Jovanovic"},
    "ervin": {"password": "CoreErvin26!", "name": "Ervin Lasko"},
    "miroslav": {"password": "CoreMiro26!", "name": "Miroslav Dordevic"}
}

# --- INNLØGGINGSSYSTEM ---
if not st.session_state.logged_in:
    st.markdown("<h2 class='core-text'>CORE</h2>", unsafe_allow_html=True)
    st.subheader("🔑 Logg inn")
    username = st.text_input("Brukernavn (f.eks. fornavn)", placeholder="miroslav", key="login_user").lower()
    password = st.text_input("Passord", type="password", placeholder="1234", key="login_pass")
    
    if st.button("Logg inn", type="primary"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = users[username]["name"]
            st.rerun()
        else:
            st.error("Feil brukernavn eller passord")
    st.stop()

# --- HOVEDSKJERM ---
col1, col2, col3 = st.columns([1,4,1])
with col2:
    if logo_path.exists():
        st.image(str(logo_path), width=420)
    st.markdown("<h2 class='core-text'>CORE</h2>", unsafe_allow_html=True)

if st.button("🚪 Logg ut"):
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.timer_start = None
    st.rerun()

st.markdown("---")

# Dodat novi Tab 1 "Min Side"
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Min Side", "📋 Reg. Aktivitet", "⏱️ Reg. Tid",
    "📊 Prosjekter", "✅ Historikk", "👥 Brukere"
])

# FANE 1: MIN SIDE (Lični profil radnika sa njegovom statistikom)
with tab1:
    st.subheader(f"Velkommen, {st.session_state.current_user} 👋")
    st.write("Dette er ditt personlige dashbord for timeføring.")
    
    idag = datetime.now().strftime("%Y-%m-%d")
    
    # Računanje samo onih sati koji pripadaju trenutno ulogovanom radniku
    mine_timer_idag = sum(float(l["vanlig_tid"]) + float(l["overtid"]) for l in st.session_state.v8_time_logs if l["bruker"] == st.session_state.current_user and l["dato"] == idag)
    mitt_overtid_idag = sum(float(l["overtid"]) for l in st.session_state.v8_time_logs if l["bruker"] == st.session_state.current_user and l["dato"] == idag)
    
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

# FANE 2: REGISTRER AKTIVITET
with tab2:
    st.subheader("Registrer Aktivitet og Fremdrift")
    aktivne_opcije = [p for p, data in st.session_state.v8_projects.items() if data["status"] == "Aktiv"]
    izabrani_prosjekt = st.selectbox("Velg prosjekt", [""] + aktivne_opcije, index=0, key="sb_akt_projekt")
    
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
        
        if st.button("LAGRE AKTIVITET FOR PROSJEKT", type="primary"):
            st.session_state.v8_projects[izabrani_prosjekt]["activities"] = novi_unosi
            st.success(f"✅ Daglig rapport lagret for prosjekt **{izabrani_prosjekt}**!")
            st.rerun()

# FANE 3: REGISTRER TID
with tab3:
    st.subheader("Registrer Arbeidstid")
    projekti_tid = [p for p, data in st.session_state.v8_projects.items() if data["status"] == "Aktiv"]
    izabrani_prosjekt_tid = st.selectbox("Velg prosjekt", [""] + projekti_tid, index=0, key="sb_tid_projekt")
    faza = st.selectbox("Fase", ["Fase 1", "Fase 2", "Annet"])

    if izabrani_prosjekt_tid == "":
        st.info("💡 Vennligst velg et prosjekt for å registrere tid.")
    else:
        st.markdown("#### Alternativ 1: Bruk stoppeklokke")
        col_start, col_stop = st.columns(2)
        
        with col_start:
            if st.button("▶️ START TIMER", use_container_width=True):
                st.session_state.timer_start = datetime.now()
                st.rerun()
                    
        with col_stop:
            if st.button("⏹️ STOPP & LAGRE", use_container_width=True):
                if st.session_state.timer_start is not None:
                    duration = datetime.now() - st.session_state.timer_start
                    hours_spent = round(duration.total_seconds() / 3600, 2)
                    if hours_spent == 0:
                        hours_spent = round((duration.total_seconds() / 60) / 60, 2)
                    
                    idag = datetime.now().strftime("%Y-%m-%d")
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
                else:
                    st.warning("Timeren er ikke startet ennå.")
                    
        if st.session_state.timer_start:
            start_str = st.session_state.timer_start.strftime("%H:%M:%S")
            st.markdown(f"<div class='start-time'>⏰ Timeren kjører... Startet kl: {start_str}</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Alternativ 2: Manuell registrering")
        manuelle_timer = str(st.text_input("Antall timer (f.eks. 7.5)", placeholder="7.5", key="manuell_inn")).replace(",", ".")
        
        if st.button("Lagre manuelle timer", type="secondary"):
            if manuelle_timer:
                try:
                    t_float = float(manuelle_timer)
                    idag = datetime.now().strftime("%Y-%m-%d")
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

# FANE 4: PROSJEKTER (PRODUKTIVITET)
with tab4:
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
            
            st.write(f"**Total gjennomsnittlig fremdrift:** {round(ukupni_progres, 1)}%")
            st.progress(ukupni_progres / 100)
            st.caption(f"⏱️ *Herav automatisert overtid:* {round(overtid_timer, 2)} t (Beregnet for lønn i Google Sheets)")
            
            with st.expander("Se detaljert status per aktivitet"):
                for akt_ime, procenat in sve_aktivnosti.items():
                    st.write(f"• {akt_ime}: **{procenat}%**")
                
            st.markdown("---")

# FANE 5: HISTORIKK
with tab5:
    st.subheader("✅ Fullførte Prosjekter (Historikk)")
    st.info("Historikk over fullførte prosjekter basert på avsluttede ordre.")

# FANE 6: BRUKERE
with tab6:
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

st.caption("InCase CORE v4.0 - Min Side Pilot")