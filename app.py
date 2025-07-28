import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime

# Cargar hoja de estilos local
def local_css(file_name):
    with open(file_name) as f:
        st.sidebar.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Usa tu propio archivo CSS si lo tienes (opcional)
# local_css("style.css")

# Diccionario con empresas organizadas por región y sector
empresas_por_sector_y_region = {
    "América del Norte": {
        "Tecnología": {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corp.",
            "GOOGL": "Alphabet Inc.",
            "NVDA": "NVIDIA Corp.",
            "AMD": "Advanced Micro Devices"
        },
        "Automoción": {
            "TSLA": "Tesla Inc.",
            "GM": "General Motors",
            "F": "Ford Motor Company"
        },
        "Finanzas": {
            "JPM": "JPMorgan Chase & Co.",
            "BAC": "Bank of America",
            "GS": "Goldman Sachs Group Inc."
        },
        "Energía": {
            "XOM": "Exxon Mobil",
            "CVX": "Chevron Corp.",
            "NEE": "NextEra Energy"
        }
    },
    "Europa": {
        "Tecnología": {
            "SAP.DE": "SAP SE (Alemania)",
            "ASML.AS": "ASML Holding (Países Bajos)",
            "ADYEN.AS": "Adyen (Países Bajos)"
        },
        "Automoción": {
            "VOW3.DE": "Volkswagen AG (Alemania)",
            "BMW.DE": "BMW AG (Alemania)",
            "STLA.MI": "Stellantis (Italia/Francia)"
        },
        "Finanzas": {
            "HSBA.L": "HSBC Holdings (Reino Unido)",
            "BNP.PA": "BNP Paribas (Francia)",
            "SAN.MC": "Banco Santander (España)"
        },
        "Energía": {
            "ENEL.MI": "Enel SpA (Italia)",
            "ORSTED.CO": "Ørsted A/S (Dinamarca)",
            "SHEL.L": "Shell plc (Reino Unido)"
        }
    },
    "Asia": {
        "Tecnología": {
            "TSMC": "Taiwan Semiconductor Manufacturing",
            "BABA": "Alibaba Group (China)",
            "JD": "JD.com (China)",
            "SONY": "Sony Group Corp (Japón)"
        },
        "Automoción": {
            "BYDDF": "BYD Co. (China)",
            "NIO": "NIO Inc. (China)",
            "TM": "Toyota Motor Corp (Japón)"
        },
        "Finanzas": {
            "IDCBY": "Industrial & Commercial Bank of China (ICBC)",
            "MFG": "Mizuho Financial Group (Japón)"
        },
        "Energía": {
            "PTR": "PetroChina",
            "CEO": "CNOOC Ltd."
        }
    }
}

# Diccionarios auxiliares
metricas = {
    "marketCap": "Capitalización de mercado",
    "trailingPE": "PER (últimos 12 meses)",
    "forwardPE": "PER estimado",
    "priceToBook": "Precio/Valor contable",
    "dividendYield": "Rentabilidad por dividendo",
    "returnOnEquity": "ROE (%)",
    "debtToEquity": "Deuda / Capital",
}

info_empresa = {
    "Nombre": "longName",
    "País": "country",
    "Sector": "sector",
    "Industria": "industry",
    "Empleados": "fullTimeEmployees"
}

def formatear_valor(valor):
    if valor is None or not isinstance(valor, (int, float)):
        return "No disponible"
    unidades = ["", "K", "M", "B", "T"]
    i = 0
    while abs(valor) >= 1000 and i < len(unidades) - 1:
        valor /= 1000.0
        i += 1
    return f"{valor:.2f}{unidades[i]}"

def main():
    st.sidebar.subheader("📊 Configuración de comparación")

    region = st.sidebar.selectbox("🌍 Región", list(empresas_por_sector_y_region.keys()))
    sector = st.sidebar.selectbox("🏭 Sector", list(empresas_por_sector_y_region[region].keys()))
    disponibles = empresas_por_sector_y_region[region][sector]

    tickers = st.sidebar.multiselect(
        "🏢 Selecciona empresas",
        options=list(disponibles.keys()),
        format_func=lambda x: f"{disponibles[x]} ({x})"
    )

    

    periodo = st.sidebar.selectbox(
        "Período para gráfico histórico",
        ["1mo", "3mo", "6mo", "1y", "5y", "max"],
        index=2
    )

    

    st.title("📈 Análisis Financiero Comparativo")

    if tickers:
        datos = yf.download(tickers, period=periodo, auto_adjust=False, progress=False, group_by="ticker")

        st.subheader("📉 Precio Ajustado (Adj Close)")
        precios = pd.DataFrame({t: datos[t]["Adj Close"] for t in tickers})
        st.line_chart(precios)

        st.subheader("📊 Volumen de Negociación")
        volumen = pd.DataFrame({t: datos[t]["Volume"] for t in tickers})
        st.line_chart(volumen)

            # Tabla comparativa de ratios clave
        st.subheader("📋 Comparativa de Ratios Financieros")

        tabla_ratios = []
        for t in tickers:
            try:
                info = yf.Ticker(t).info
                fila = {"Ticker": t}
                for clave, nombre in metricas.items():
                    valor = info.get(clave, None)
                    if clave == "dividendYield" and isinstance(valor, float):
                        valor = f"{valor * 100:.2f}%"
                    elif isinstance(valor, (int, float)):
                        valor = f"{valor:,.2f}"
                    elif valor is None:
                        valor = "No disponible"
                    fila[nombre] = valor
                tabla_ratios.append(fila)
            except Exception as e:
                st.warning(f"No se pudo obtener info para {t}: {e}")

        if tabla_ratios:
            df_ratios = pd.DataFrame(tabla_ratios)
            st.dataframe(df_ratios.set_index("Ticker"))
        else:
            st.write("No hay datos disponibles para mostrar la tabla comparativa.")


        for t in tickers:
            st.markdown(f"## 📌 {t} — {disponibles[t]}")
            try:
                info = yf.Ticker(t).info
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Ratios clave")
                    for clave, nombre in metricas.items():
                        valor = info.get(clave, "No disponible")
                        if clave == "dividendYield" and isinstance(valor, float):
                            valor = f"{valor * 100:.2f}%"
                        elif isinstance(valor, (float, int)):
                            valor = f"{valor:,.2f}"
                        st.write(f"**{nombre}:** {valor}")
                with col2:
                    st.subheader("Información general")
                    for campo, clave in info_empresa.items():
                        st.write(f"**{campo}:** {info.get(clave, 'No disponible')}")
                    st.write("**Capitalización formateada:**", formatear_valor(info.get("marketCap")))
            except Exception as e:
                st.error(f"Error al mostrar {t}: {e}")
    else:
        st.info("Selecciona al menos una empresa para ver el análisis.")

if __name__ == "__main__":
    main()
