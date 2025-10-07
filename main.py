import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Path ke file Excel
EXCEL_PATH = r"C:\Users\jarie\OneDrive\Desktop\Personal\SCHOOL\MATERI KULIAH\REKAYASA PERANGKAT LUNAK (0065) IDE\TUGAS\keuangan.xlsx"

# Load atau buat file Excel
def load_data():
    if os.path.exists(EXCEL_PATH):
        return pd.read_excel(EXCEL_PATH)
    else:
        df = pd.DataFrame(columns=["Tanggal", "Pemasukan", "Pengeluaran", "Deskripsi", "Jumlah"])
        df.to_excel(EXCEL_PATH, index=False)
        return df

# Simpan data
def save_data(df):
    df.to_excel(EXCEL_PATH, index=False)

# Hapus data
def delete_row(index):
    df = load_data()
    df.drop(index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_data(df)

# CSS untuk menyembunyikan "Press Enter to submit"
st.markdown("""
    <style>
    div[data-testid="stForm"] div[role="alert"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Keuangan Pribadi", layout="wide")
st.title("💰 Aplikasi Pencatatan Keuangan Pribadi")

tab1, tab2, tab3 = st.tabs(["➕ Input Transaksi", "📊 Grafik Laporan", "✏️ Edit & Hapus"])

# TAB 1 – INPUT
with tab1:
    st.subheader("Form Input Transaksi")
    with st.form("form_input", clear_on_submit=True):
        tanggal = st.date_input("Tanggal")
        pemasukan = st.selectbox("Pemasukan", ["", "Gaji", "Bonus", "Hasil Usaha", "Others"])
        pengeluaran = st.selectbox("Pengeluaran", ["", "Makanan", "Belanja", "Transportasi", "Hiburan", "Others"])
        deskripsi = st.text_input("Deskripsi")
        jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0)
        submit = st.form_submit_button("✅ Simpan")

        if submit:
            df = load_data()
            new_row = {
                "Tanggal": tanggal,
                "Pemasukan": pemasukan if pemasukan else None,
                "Pengeluaran": pengeluaran if pengeluaran else None,
                "Deskripsi": deskripsi,
                "Jumlah": jumlah
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Transaksi berhasil disimpan!")

# TAB 2 – GRAFIK
with tab2:
    st.subheader("📅 Laporan Bulanan")
    df = load_data()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    bulan = st.selectbox("Pilih Bulan", sorted(df["Tanggal"].dt.month.unique()))
    tahun = st.selectbox("Pilih Tahun", sorted(df["Tanggal"].dt.year.unique()))
    laporan = df[(df["Tanggal"].dt.month == bulan) & (df["Tanggal"].dt.year == tahun)]

    if not laporan.empty:
        total_pemasukan = laporan[laporan["Pemasukan"].notna()]["Jumlah"].sum()
        total_pengeluaran = laporan[laporan["Pengeluaran"].notna()]["Jumlah"].sum()
        saldo = total_pemasukan - total_pengeluaran

        col1, col2, col3 = st.columns(3)
        col1.metric("Pemasukan", f"Rp {total_pemasukan:,.0f}")
        col2.metric("Pengeluaran", f"Rp {total_pengeluaran:,.0f}")
        col3.metric("Saldo", f"Rp {saldo:,.0f}")

        st.markdown("#### 🧁 Pie Chart Detail")
        pie_data = laporan.groupby(laporan["Pemasukan"].fillna(laporan["Pengeluaran"]))["Jumlah"].sum()
        if pie_data.sum() > 0:
            fig1, ax1 = plt.subplots()
            ax1.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%')
            st.pyplot(fig1)
        else:
            st.info("Tidak ada data untuk pie chart.")

        st.markdown("#### 📊 Bar Chart Bulanan")
        df["Bulan"] = df["Tanggal"].dt.strftime("%b")
        df["Jenis"] = df.apply(lambda x: "Pemasukan" if pd.notna(x["Pemasukan"]) else "Pengeluaran", axis=1)
        bar_data = df.groupby(["Bulan", "Jenis"])["Jumlah"].sum().unstack().fillna(0)
        st.bar_chart(bar_data)
    else:
        st.warning("Tidak ada data untuk bulan dan tahun yang dipilih.")

# TAB 3 – EDIT & DELETE
with tab3:
    st.subheader("✏️ Edit / 🗑️ Hapus Transaksi")
    df = load_data()
    df["Label"] = df["Tanggal"].astype(str) + " | " + df["Pemasukan"].fillna("").astype(str) + df["Pengeluaran"].fillna("").astype(str) + " | " + df["Deskripsi"]
    selected_label = st.selectbox("Pilih Transaksi", df["Label"])
    filtered = df[df["Label"] == selected_label]
    if not filtered.empty:
        selected_index = filtered.index[0]
        row = df.iloc[selected_index]
    # lanjutkan form edit...
    else:
        st.warning("Transaksi tidak ditemukan. Mungkin sudah dihapus atau label tidak cocok.")

    row = df.iloc[selected_index]

    with st.form("edit_form"):
        tanggal_edit = st.date_input("Tanggal", value=row["Tanggal"])
        pemasukan_edit = st.selectbox("Pemasukan", ["", "Gaji", "Bonus", "Hasil Usaha", "Others"], index=["", "Gaji", "Bonus", "Hasil Usaha", "Others"].index(str(row["Pemasukan"])) if pd.notna(row["Pemasukan"]) else 0)
        pengeluaran_edit = st.selectbox("Pengeluaran", ["", "Makanan", "Belanja", "Transportasi", "Hiburan", "Others"], index=["", "Makanan", "Belanja", "Transportasi", "Hiburan", "Others"].index(str(row["Pengeluaran"])) if pd.notna(row["Pengeluaran"]) else 0)
        deskripsi_edit = st.text_input("Deskripsi", value=row["Deskripsi"])
        jumlah_edit = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, value=float(row["Jumlah"]))
        col_edit, col_delete = st.columns(2)
        update = col_edit.form_submit_button("💾 Update")
        delete = col_delete.form_submit_button("🗑️ Hapus")

        if update:
            df.at[selected_index, "Tanggal"] = tanggal_edit
            df.at[selected_index, "Pemasukan"] = pemasukan_edit if pemasukan_edit else None
            df.at[selected_index, "Pengeluaran"] = pengeluaran_edit if pengeluaran_edit else None
            df.at[selected_index, "Deskripsi"] = deskripsi_edit
            df.at[selected_index, "Jumlah"] = jumlah_edit
            save_data(df)
            st.success("Transaksi berhasil diperbarui!")

        if delete:
            delete_row(selected_index)
            st.success("Transaksi berhasil dihapus!")
