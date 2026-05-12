# AHMAD BAIHAQI HAFID/ 231080200035
# 6B1/ Informatika
# ---

from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

# =========================
# WINDOW
# =========================
root = Tk()
root.title("Deteksi Kesegaran Ikan")
root.geometry("960x720")
root.configure(bg="#F5F5F5")
root.resizable(False, False)

# =========================
# VARIABEL
# =========================
path_gambar = ""
img_tk = None

# =========================
# UPLOAD GAMBAR
# =========================
def upload_gambar():
    global path_gambar, img_tk

    file_path = filedialog.askopenfilename(
        title="Pilih Gambar Ikan",
        filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
    )

    if file_path:
        path_gambar = file_path

        img = Image.open(file_path)
        img = img.resize((380, 240))
        img_tk = ImageTk.PhotoImage(img)

        canvas.delete("all")
        canvas.create_image(190, 120, image=img_tk)

        hasil_label.config(text="Menunggu\nAnalisis...", fg="#333333")
        detail_kiri.config(text="Klik tombol ANALISIS")
        detail_kanan.config(text="")

# =========================
# ANALISIS GAMBAR
# =========================
def analisis_gambar():
    global path_gambar, img_tk

    if path_gambar == "":
        messagebox.showwarning("Peringatan", "Upload gambar terlebih dahulu!")
        return

    img = cv2.imread(path_gambar)
    img = cv2.resize(img, (380, 240))
    tinggi, lebar, _ = img.shape

    # =========================================
    # ROI 1 - AREA MATA (eye region)
    # Posisi: sisi kiri atas gambar
    # Asumsi ikan menghadap ke kiri
    # =========================================
    mata_x1 = 0
    mata_y1 = 0
    mata_x2 = int(lebar * 0.18)   # 0% - 18% lebar
    mata_y2 = int(tinggi * 0.60)  # 0% - 60% tinggi

    area_mata = img[mata_y1:mata_y2, mata_x1:mata_x2]

    # =========================================
    # ROI 2 - AREA INSANG (gill region)
    # Posisi: sisi kiri bawah, setelah area mata
    # =========================================
    insang_x1 = int(lebar * 0.18)  # 18% - 38% lebar
    insang_y1 = 0
    insang_x2 = int(lebar * 0.38)
    insang_y2 = tinggi

    area_insang = img[insang_y1:insang_y2, insang_x1:insang_x2]

    # =========================================
    # GAMBAR ROI DI GAMBAR
    # =========================================
    img_box = img.copy()

    # Kotak ROI Mata (biru)
    cv2.rectangle(img_box,
                  (mata_x1, mata_y1),
                  (mata_x2, mata_y2),
                  (220, 100, 30), 2)

    cv2.putText(img_box, "MATA",
                (mata_x1 + 4, mata_y1 + 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (220, 100, 30), 1)

    # Kotak ROI Insang (hijau)
    cv2.rectangle(img_box,
                  (insang_x1, insang_y1),
                  (insang_x2, insang_y2),
                  (30, 160, 60), 2)

    cv2.putText(img_box, "INSANG",
                (insang_x1 + 4, insang_y1 + 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (30, 160, 60), 1)

    # Tampilkan gambar
    img_rgb = cv2.cvtColor(img_box, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk  = ImageTk.PhotoImage(img_pil)

    canvas.delete("all")
    canvas.create_image(190, 120, image=img_tk)

    # =========================================
    # RGB - RATA-RATA DARI MATA + INSANG
    # =========================================
    rgb_mata   = cv2.cvtColor(area_mata,   cv2.COLOR_BGR2RGB)
    rgb_insang = cv2.cvtColor(area_insang, cv2.COLOR_BGR2RGB)

    # Rata-rata gabungan (bobot sama)
    red   = (np.mean(rgb_mata[:, :, 0]) + np.mean(rgb_insang[:, :, 0])) / 2
    green = (np.mean(rgb_mata[:, :, 1]) + np.mean(rgb_insang[:, :, 1])) / 2
    blue  = (np.mean(rgb_mata[:, :, 2]) + np.mean(rgb_insang[:, :, 2])) / 2

    # Nilai per area untuk ditampilkan
    red_mata    = np.mean(rgb_mata[:, :, 0])
    green_mata  = np.mean(rgb_mata[:, :, 1])
    red_insang  = np.mean(rgb_insang[:, :, 0])
    green_insang= np.mean(rgb_insang[:, :, 1])

    # =========================================
    # HSV - RATA-RATA DARI MATA + INSANG
    # =========================================
    hsv_mata   = cv2.cvtColor(area_mata,   cv2.COLOR_BGR2HSV)
    hsv_insang = cv2.cvtColor(area_insang, cv2.COLOR_BGR2HSV)

    sat_mata    = np.mean(hsv_mata[:, :, 1])
    sat_insang  = np.mean(hsv_insang[:, :, 1])
    bri_mata    = np.mean(hsv_mata[:, :, 2])
    bri_insang  = np.mean(hsv_insang[:, :, 2])

    saturation  = (sat_mata + sat_insang) / 2
    brightness  = (bri_mata + bri_insang) / 2

    # =========================================
    # KLASIFIKASI
    # Kondisi segar:
    # - Mata: warna cerah, R > G (merah kecoklatan)
    # - Insang: merah cerah, saturation tinggi
    # =========================================
    segar_mata   = red_mata > green_mata and sat_mata >= 65 and bri_mata >= 85
    segar_insang = red_insang > green_insang and sat_insang >= 70

    if segar_mata and segar_insang:
        hasil   = "IKAN SEGAR"
        warna   = "green"
        tingkat = "Tingkat kesegaran tinggi"
    elif saturation >= 50:
        hasil   = "KURANG SEGAR"
        warna   = "orange"
        tingkat = "Tingkat kesegaran sedang"
    else:
        hasil   = "TIDAK SEGAR"
        warna   = "red"
        tingkat = "Tingkat kesegaran rendah"

    hasil_label.config(text=f"{hasil}\n({tingkat})", fg=warna)

    # =========================================
    # DETAIL KIRI — nilai RGB & HSV per area
    # =========================================
    kiri_text = (
        "RGB - Mata\n"
        "──────────────\n"
        f"R : {red_mata:.2f}\n"
        f"G : {green_mata:.2f}\n"
        "\n"
        "RGB - Insang\n"
        "──────────────\n"
        f"R : {red_insang:.2f}\n"
        f"G : {green_insang:.2f}\n"
        "\n"
        "HSV (rata-rata)\n"
        "──────────────\n"
        f"Sat  : {saturation:.2f}\n"
        f"Bri  : {brightness:.2f}"
    )

    # =========================================
    # DETAIL KANAN — metode & kesimpulan
    # =========================================
    kanan_text = (
        "METODE\n"
        "──────────────\n"
        "  • RGB\n"
        "  • HSV\n"
        "  • ROI Segmentasi\n"
        "  • Area Mata\n"
        "  • Area Insang\n"
        "\n"
        "KESIMPULAN\n"
        "──────────────\n"
        f"Mata   : {'OK' if segar_mata   else 'Pudar'}\n"
        f"Insang : {'OK' if segar_insang else 'Pudar'}\n"
        f"Sat    : {round(saturation, 2)}\n"
        f"\n→ {hasil}"
    )

    detail_kiri.config(text=kiri_text)
    detail_kanan.config(text=kanan_text)

# =========================
# RESET
# =========================
def reset_aplikasi():
    global path_gambar
    path_gambar = ""

    canvas.delete("all")
    canvas.create_text(
        190, 120,
        text="Preview Gambar",
        font=("Arial", 16),
        fill="#999999"
    )

    hasil_label.config(text="Menunggu\nAnalisis...", fg="#333333")
    detail_kiri.config(text="Belum ada analisis.")
    detail_kanan.config(text="")

# ============================================================
# ====================== LAYOUT UI ==========================
# ============================================================

# =========================
# JUDUL
# =========================
Label(
    root,
    text="SISTEM DETEKSI KESEGARAN IKAN",
    font=("Arial", 20, "bold"),
    bg="#F5F5F5",
    fg="#1A1A1A"
).pack(pady=(16, 2))

Label(
    root,
    text="Pengolahan Citra Digital  •  Analisis Warna Mata & Insang",
    font=("Arial", 9),
    bg="#F5F5F5",
    fg="#888888"
).pack(pady=(0, 10))

Frame(root, bg="#DDDDDD", height=1).pack(fill=X, padx=30)

# =========================
# FRAME UTAMA
# =========================
frame_utama = Frame(root, bg="#F5F5F5")
frame_utama.pack(padx=30, pady=14, fill=BOTH, expand=True)

# ── Kolom Kiri ──────────────────────────────
col_kiri = Frame(frame_utama, bg="#F5F5F5")
col_kiri.pack(side=LEFT, fill=Y)

# Card Preview
card_preview = Frame(col_kiri, bg="white", bd=1, relief="solid")
card_preview.pack(pady=(0, 10))

Label(
    card_preview,
    text="Preview Gambar",
    font=("Arial", 9, "bold"),
    bg="#FAFAFA",
    fg="#555555",
    anchor="w",
    padx=10,
    pady=5
).pack(fill=X)

Frame(card_preview, bg="#EEEEEE", height=1).pack(fill=X)

canvas = Canvas(
    card_preview,
    width=380,
    height=240,
    bg="#ECECEC",
    highlightthickness=0
)
canvas.pack(padx=10, pady=10)

canvas.create_text(
    190, 120,
    text="Preview Gambar",
    font=("Arial", 16),
    fill="#999999"
)

# Legenda ROI
legenda = Frame(card_preview, bg="white")
legenda.pack(fill=X, padx=10, pady=(0, 8))

Frame(legenda, bg="#1460DC", width=12, height=12).pack(side=LEFT)
Label(legenda, text=" Mata", font=("Arial", 8), bg="white", fg="#555555").pack(side=LEFT)
Label(legenda, text="    ", bg="white").pack(side=LEFT)
Frame(legenda, bg="#1EA03C", width=12, height=12).pack(side=LEFT)
Label(legenda, text=" Insang", font=("Arial", 8), bg="white", fg="#555555").pack(side=LEFT)

# Card Tombol
card_btn = Frame(col_kiri, bg="white", bd=1, relief="solid")
card_btn.pack(fill=X)

btn_row = Frame(card_btn, bg="white")
btn_row.pack(padx=10, pady=10, fill=X)

Button(
    btn_row,
    text="Upload Gambar",
    command=upload_gambar,
    font=("Arial", 9, "bold"),
    bg="#2563EB",
    fg="white",
    activebackground="#1D4ED8",
    activeforeground="white",
    bd=0,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=8
).pack(side=LEFT, expand=True, fill=X, padx=(0, 6))

Button(
    btn_row,
    text="Analisis",
    command=analisis_gambar,
    font=("Arial", 9, "bold"),
    bg="#16A34A",
    fg="white",
    activebackground="#15803D",
    activeforeground="white",
    bd=0,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=8
).pack(side=LEFT, expand=True, fill=X, padx=(0, 6))

Button(
    btn_row,
    text="Reset",
    command=reset_aplikasi,
    font=("Arial", 9, "bold"),
    bg="#DC2626",
    fg="white",
    activebackground="#B91C1C",
    activeforeground="white",
    bd=0,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=8
).pack(side=LEFT, expand=True, fill=X)

# ── Kolom Kanan ─────────────────────────────
col_kanan = Frame(frame_utama, bg="#F5F5F5")
col_kanan.pack(side=LEFT, fill=BOTH, expand=True, padx=(14, 0))

# Card Hasil
card_hasil = Frame(col_kanan, bg="white", bd=1, relief="solid")
card_hasil.pack(fill=X, pady=(0, 10))

Label(
    card_hasil,
    text="Hasil Deteksi",
    font=("Arial", 9, "bold"),
    bg="#FAFAFA",
    fg="#555555",
    anchor="w",
    padx=10,
    pady=5
).pack(fill=X)

Frame(card_hasil, bg="#EEEEEE", height=1).pack(fill=X)

hasil_label = Label(
    card_hasil,
    text="Menunggu\nAnalisis...",
    font=("Arial", 20, "bold"),
    bg="white",
    fg="#333333",
    justify="center",
    pady=18
)
hasil_label.pack(expand=True)

# Card Detail
card_detail = Frame(col_kanan, bg="white", bd=1, relief="solid")
card_detail.pack(fill=BOTH, expand=True)

Label(
    card_detail,
    text="Detail Analisis",
    font=("Arial", 9, "bold"),
    bg="#FAFAFA",
    fg="#555555",
    anchor="w",
    padx=10,
    pady=5
).pack(fill=X)

Frame(card_detail, bg="#EEEEEE", height=1).pack(fill=X)

isi_frame = Frame(card_detail, bg="white")
isi_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

detail_kiri = Label(
    isi_frame,
    text="Belum ada analisis.",
    font=("Consolas", 9),
    bg="white",
    fg="#333333",
    justify=LEFT,
    anchor="nw"
)
detail_kiri.pack(side=LEFT, fill=BOTH, expand=True)

Frame(isi_frame, bg="#DDDDDD", width=1).pack(side=LEFT, fill=Y, padx=8)

detail_kanan = Label(
    isi_frame,
    text="",
    font=("Consolas", 9),
    bg="white",
    fg="#333333",
    justify=LEFT,
    anchor="nw"
)
detail_kanan.pack(side=LEFT, fill=BOTH, expand=True)

# =========================
# FOOTER
# =========================
Frame(root, bg="#DDDDDD", height=1).pack(fill=X, padx=30)

Label(
    root,
    text="Pengolahan Citra Digital  •  RGB  •  HSV  •  ROI Mata & Insang",
    font=("Arial", 8),
    bg="#F5F5F5",
    fg="#AAAAAA"
).pack(pady=8)

# =========================
# MAINLOOP
# =========================
root.mainloop()