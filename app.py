

import pandas as pd
import yfinance as yf
import streamlit as st

st.set_page_config(page_title="Análisis Financiero", layout="centered")

st.title("🚀 ¡Bienvenido a mi app de análisis financiero!")
st.write("Aquí puedes analizar acciones y ETFs utilizando datos de Yahoo Finance.")

# Campo para escribir ticker
ticker_input = st.text_input("Introduce el ticker de la empresa (ej. AAPL, TSLA, MSFT):", "AAPL")

# Función para formatear valores grandes
def formatear_valor(valor):
    if valor is None or not isinstance(valor, (int, float)):
        return "No disponible"
    
    unidades = ["", "K", "M", "B", "T"]
    i = 0
    while abs(valor) >= 1000 and i < len(unidades) - 1:
        valor /= 1000.0
        i += 1
    return f"{valor:.2f}{unidades[i]}"

# Solo muestra análisis si se ha introducido un ticker
if ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        info = ticker.info

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Ratios clave")
            metricas = {
                "marketCap": "Capitalización de mercado",
                "trailingPE": "PER (últimos 12 meses)",
                "forwardPE": "PER estimado",
                "pegRatio": "PEG Ratio",
                "priceToBook": "Precio/Valor contable",
                "dividendYield": "Rentabilidad por dividendo",
                "returnOnEquity": "ROE (%)",
                "debtToEquity": "Deuda / Capital",
            }

            for clave, nombre in metricas.items():
                valor = info.get(clave, "No disponible")
                if clave == "dividendYield" and isinstance(valor, float):
                    valor = f"{valor * 100:.2f}%"
                elif isinstance(valor, (float, int)):
                    valor = f"{valor:,.2f}"
                st.write(f"**{nombre}:** {valor}")

        with col2:
            st.subheader("📌 Información general")
            empresa_info = {
                "Nombre": info.get("longName", "No disponible"),
                "País": info.get("country", "No disponible"),
                "Sector": info.get("sector", "No disponible"),
                "Industria": info.get("industry", "No disponible"),
                "Empleados": info.get("fullTimeEmployees", "No disponible")
            }
            for campo, valor in empresa_info.items():
                st.write(f"**{campo}:** {valor}")
                
        # Selector de período para el gráfico
        periodo = st.selectbox(
            "Selecciona período del gráfico histórico:",
            ["1mo", "3mo", "6mo", "1y", "5y", "10y", "max"],
            index=2
        )

        historial = ticker.history(period=periodo)

        st.markdown("---")
        st.subheader("📈 Evolución del precio")

        if not historial.empty:
            st.line_chart(historial["Close"])
        else:
            st.warning("No se encontraron datos históricos para este ticker.")

        st.write("**Capitalización formateada:**", formatear_valor(info.get("marketCap")))

    except Exception as e:
        st.error(f"Error al obtener los datos: {e}")



        


