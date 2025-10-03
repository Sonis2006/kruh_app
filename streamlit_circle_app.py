"""
Streamlit aplikace: "Kružnice z bodů"

Soubor: streamlit_circle_app.py
Popis: Interaktivní webová aplikace pro vykreslení kružnice a bodů na ní.
Funkce:
 - Vstup: střed (x,y), poloměr, počet bodů, barva bodů, jednotka os
 - Vykreslení kružnice a bodů (s číselnými hodnotami os a jednotkami)
 - Informace o autorovi (uživatel vyplní) a o asistovi/technologiích v samostatném okně (expander)
 - Generování PDF s obrázkem, parametry úlohy, jménem autora a kontaktem

Požadavky (vytvořte soubor requirements.txt):
streamlit
numpy
matplotlib
reportlab

Spuštění:
1) pip install -r requirements.txt
2) streamlit run streamlit_circle_app.py

Poznámka: Do PDF se vloží snímek grafu (.png) a textové údaje.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
import os
from math import cos, sin, pi
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Kružnice z bodů", layout="wide")

st.title("Kružnice z bodů — Streamlit aplikace")

# --- Uživatelská nastavení ---
col1, col2 = st.columns(2)
with col1:
    st.header("Parametry kružnice")
    cx = st.number_input("Střed - x", value=0.0, format="%.6f")
    cy = st.number_input("Střed - y", value=0.0, format="%.6f")
    radius = st.number_input("Poloměr (>=0)", value=1.0, min_value=0.0, format="%.6f")
    n_points = st.number_input("Počet bodů na kružnici", min_value=1, value=12, step=1)
    unit = st.text_input("Jednotka osy (např. m)", value="m")

with col2:
    st.header("Vzhled")
    color = st.color_picker("Barva bodů", value="#ff0000")
    point_size = st.slider("Velikost bodů", 1, 20, 6)
    show_grid = st.checkbox("Zobrazit mřížku", value=True)
    show_labels = st.checkbox("Zobrazit legendu a popisky", value=True)

st.markdown("---")

# --- Výpočet bodů na kružnici ---
angles = np.linspace(0, 2*pi, int(n_points), endpoint=False)
xs = cx + radius * np.cos(angles)
ys = cy + radius * np.sin(angles)

# --- Vykreslení pomocí Matplotlib ---
fig, ax = plt.subplots(figsize=(6,6))
# kružnice
theta = np.linspace(0, 2*pi, 400)
ax.plot(cx + radius*np.cos(theta), cy + radius*np.sin(theta), linestyle='-', linewidth=1)
# body
ax.scatter(xs, ys, s=point_size**2, color=color, label=f'{int(n_points)} bodů')
# střed
ax.scatter([cx], [cy], s=(point_size*1.5)**2, color='black', marker='+', label='střed')

# grafika os
ax.set_aspect('equal', adjustable='datalim')
# nastavení rozsahu s trochou okraje
pad = max(0.1*radius, 0.1)
ax.set_xlim(cx - radius - pad, cx + radius + pad)
ax.set_ylim(cy - radius - pad, cy + radius + pad)

# mřížka, popisky, legenda
if show_grid:
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
if show_labels:
    ax.set_xlabel(f"x [{unit}]")
    ax.set_ylabel(f"y [{unit}]")
    ax.legend()

# vykreslit čísla u os (ticks jsou číselné hodnoty)
ax.tick_params(axis='both', which='major', labelsize=10)

# zakreslení indexů bodů (číslování)
for i, (xv, yv) in enumerate(zip(xs, ys), start=1):
    ax.text(xv, yv, str(i), fontsize=9, ha='left', va='bottom')

# zobrazit graf v appce
st.pyplot(fig)

# --- Zobrazení tabulky souřadnic ---
import pandas as pd
coords = pd.DataFrame({'index': np.arange(1, int(n_points)+1), 'x': np.round(xs, 6), 'y': np.round(ys, 6), 'unit_x': [unit]*len(xs), 'unit_y':[unit]*len(ys)})
st.subheader('Seznam souřadnic bodů')
st.dataframe(coords)

st.markdown("---")

# --- Info o aplikaci / asistentovi / technologiích ---
with st.expander("Informace o aplikaci a použitých technologiích", expanded=False):
    st.markdown("**Popis:** Aplikace vykreslí kružnici a rozloží na ní zadaný počet bodů. Uživatel zadá střed, poloměr, počet bodů a barvu bodů. Výstup obsahuje graf, číselné souřadnice a možnost vygenerovat PDF s parametry.\n")
    st.markdown("**Použité technologie:** Streamlit, NumPy, Matplotlib, ReportLab (pro export do PDF).\n")
    st.markdown("**Asistent:** GPT-5 Thinking mini.\n")
    st.markdown("**Poznámka:** Do PDF se vloží snímek aktuálního grafu a parametry úlohy. Pole pro jméno autora a kontakt můžete vyplnit níže před tiskem.\n")

# --- Informace o autorovi tisku (uživatel vyplní) ---
st.subheader('Údaje pro tisk / PDF')
author_name = st.text_input('Jméno autora (pro PDF)', value='')
author_contact = st.text_input('Kontakt autora (email/telefon)', value='')
additional_notes = st.text_area('Další poznámky (objeví se v PDF)', value='')

# --- Funkce pro export do PDF ---

def generate_pdf(fig, params: dict, author_name: str, author_contact: str, notes: str) -> bytes:
    """Vytvoří PDF dokument (bytes) obsahující obrázek grafu a parametry."""
    # uložíme fig do PNG v paměti
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    # nadpis
    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, height - 50, 'Kružnice z bodů - Výstup')

    # metadata
    c.setFont('Helvetica', 10)
    y = height - 80
    for k, v in params.items():
        c.drawString(40, y, f"{k}: {v}")
        y -= 14

    if author_name:
        c.drawString(40, y, f"Tiskl: {author_name}")
        y -= 14
    if author_contact:
        c.drawString(40, y, f"Kontakt: {author_contact}")
        y -= 14
    if notes:
        c.drawString(40, y, f"Poznámky: {notes}")
        y -= 14

    # vložíme obrázek
    try:
        img = ImageReader(img_buffer)
        # obrázek umístit dole, ponechat prostor nahoře pro text
        img_max_width = width - 80
        img_max_height = y - 40
        # získat rozměry obrázku
        iw, ih = img.getSize()
        scale = min(img_max_width / iw, img_max_height / ih, 1.0)
        iw_scaled = iw * scale
        ih_scaled = ih * scale
        x_img = 40
        y_img = y - ih_scaled - 10
        c.drawImage(img, x_img, y_img, width=iw_scaled, height=ih_scaled)
    except Exception as e:
        c.drawString(40, y - 20, f"Chyba při vkládání obrázku: {e}")

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.read()

# --- Tlačítko pro generování PDF ---
params = {
    'Střed x': cx,
    'Střed y': cy,
    'Poloměr': radius,
    'Počet bodů': int(n_points),
    'Barva bodů': color,
    'Jednotka': unit
}

if st.button('Generovat PDF s parametry a grafem'):
    try:
        pdf_bytes = generate_pdf(fig, params, author_name, author_contact, additional_notes)
        st.success('PDF vygenerováno — připraveno ke stažení')
        st.download_button(label='Stáhnout PDF', data=pdf_bytes, file_name='kruznice_vystup.pdf', mime='application/pdf')
    except Exception as e:
        st.error(f'Chyba při generování PDF: {e}')

st.markdown("---")
st.caption("Aplikaci můžete uložit do repozitáře GitHub jako soubor streamlit_circle_app.py. Přidejte requirements.txt se závislostmi: streamlit, numpy, matplotlib, reportlab.")
