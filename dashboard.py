import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

#Fungsi load dan preprocessing data
def load_and_preprocess_data(file_path):
    """
    Fungsi untuk memuat dan membersihkan data.
    """
    data = pd.read_csv(file_path)
    
    #Mengubah kolom timestamp menjadi datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    return data

#Fungsi untuk filtering data
def filter_data(data, stations=None, start_date=None, end_date=None):
    """
    Fungsi untuk memfilter data berdasarkan stasiun dan rentang tanggal 
    """
    if stations:
        data = data[data['station'].isin(stations)]
    if start_date and end_date:
        data = data[(data['timestamp'] >= pd.to_datetime(start_date))&
                    (data['timestamp'] <= pd.to_datetime(end_date))]
    return data


#Line plot
def time_series_plot(data, kolom_x, kolom_y, kolom_grup=None, freq=None, judul="Distribusi Data", xlabel="Waktu", ylabel="Nilai", agg_func="mean"):
    """
    Fungsi untuk membuat time series plot yang fleksibel untuk parameter apa pun.
    
    Args:
        data (pd.DataFrame): DataFrame yang berisi data.
        kolom_x (str): Kolom untuk sumbu X (biasanya waktu).
        kolom_y (str): Kolom untuk sumbu Y (parameter yang akan diplot, misalnya NO2, PM2.5).
        kolom_grup (str): Kolom untuk mengelompokkan data (misalnya, berdasarkan stasiun).
        judul (str): Judul grafik.
        xlabel (str): Label sumbu X.
        ylabel (str): Label sumbu Y.
    
    Returns:
        fig: Objek figure Matplotlib.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if kolom_grup:
        # Jika ada kolom grup, buat plot terpisah untuk setiap grup
        for grup, grup_data in data.groupby(kolom_grup):
            ax.plot(grup_data[kolom_x], grup_data[kolom_y], label=f"{grup}", alpha=0.7)
    else:
        # Jika tidak ada grup, plot data secara langsung
        ax.plot(data[kolom_x], data[kolom_y], label="Data", alpha=0.7)
    
    ax.set_title(judul)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(title="Grup" if kolom_grup else None)
    ax.grid(True)
    
    return fig

#Load data
data = load_and_preprocess_data("all_tabeldf.csv")

#Judul dashboard
st.header("Dashboard Kualitas Udara")

#Sidebar untuk filter
# Sidebar
st.sidebar.header("Filter Data")
stations = ["Semua Stasiun"] + list(data["station"].unique())  # Tambahkan opsi "Semua Stasiun"
selected_station = st.sidebar.selectbox("Pilih Stasiun:", stations)

start_date = st.sidebar.date_input("Tanggal Mulai", pd.to_datetime(data["timestamp"]).min())
end_date = st.sidebar.date_input("Tanggal Akhir", pd.to_datetime(data["timestamp"]).max())

# Filter data berdasarkan input
# Filter data
if selected_station == "Semua Stasiun":
    filtered_data = data  # Tidak ada filter untuk stasiun
else:
    filtered_data = data[data["station"] == selected_station]


#Summary insight
st.title("Dashboard Kualitas Udara - Insight")
avg_pm25 = filtered_data['PM2.5'].mean()
max_station = filtered_data.groupby(by='station')['PM2.5'].mean().idxmax()
min_station = filtered_data.groupby(by='station')['PM2.5'].mean().idxmin()

st.metric("Rata-rata PM2.5", f"{avg_pm25:.2f} µg/m³")
st.write(f"Stasiun dengan Polusi Tertinggi: **{max_station}**")
st.write(f"Stasiun dengan Polusi Terendah: **{min_station}**")

# Tampilkan grafik heatmap NO2
st.subheader("Polutan Konsentrasi NO2")
fig_no2 = time_series_plot(
    data=data,
    kolom_x="timestamp",
    kolom_y="NO2",
    kolom_grup="station",
    judul="Tren Waktu NO2 di Berbagai Stasiun",
    xlabel="Waktu",
    ylabel="Konsentrasi NO2"
)
st.pyplot(fig_no2)


# Scatter Plot: Parameter Cuaca vs Polusi
st.subheader("Visualisasi Hubungan Parameter Cuaca dengan Tingkat Polusi")
parameter = st.selectbox("Pilih Parameter Cuaca:", ["TEMP", "RAIN", "PRES", "DEWP", "WSPM"])

fig, ax = plt.subplots()
sns.scatterplot(data=filtered_data, x=parameter, y="PM2.5", hue="station", ax=ax)
ax.set_title(f"Hubungan {parameter.capitalize()} dengan PM2.5")
ax.set_xlabel(parameter.capitalize())
ax.set_ylabel("PM2.5")
st.pyplot(fig)

#Menampilkan distribusi konsentrasi PM2.5 di setiap stasiun
st.subheader("Distribusi PM2.5 untuk Semua Stasiun")

if selected_station == "Semua Stasiun":
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=data, x="station", y="PM2.5", ax=ax)
    ax.set_title("Distribusi PM2.5 untuk Semua Stasiun")
    ax.set_xlabel("Stasiun")
    ax.set_ylabel("Konsentrasi PM2.5")
    st.pyplot(fig)

#Menampilkan tren waktu untuk melihat tren polusi berdasarkan waktu
st.subheader("Tren Polusi Berdasarkan Waktu")
time_agg = st.selectbox("Pilih Agregasi Waktu:", ["hour", "day", "month", "year"])
fig3_ = time_series_plot(
    data=filtered_data, 
    kolom_x="timestamp", 
    kolom_y="PM2.5",
    judul=f"Tren Polusi PM2.5 ({time_agg})",
    freq=time_agg,
)
st.pyplot(fig3_)