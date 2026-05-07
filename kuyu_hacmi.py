import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import re

class KapsamliSondajHesaplayici:
    def __init__(self, root):
        self.root = root
        self.root.title("Profesyonel Sondaj Hesaplayıcı (bbl)")
        
        # Ana pencere arka plan rengi
        self.bg_color = "#F0F4F8"
        self.root.configure(bg=self.bg_color)
        
        try:
            self.root.state('zoomed')
        except:
            try:
                self.root.attributes('-zoomed', True)
            except:
                self.root.geometry("{0}x{1}+0+0".format(
                    self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.root.minsize(1050, 700)

        self._setup_styles()

        self.vcmd = (self.root.register(self._validate_numeric), '%d', '%P')

        self.statik_klasoru = "Statik_Kuyular"
        self.dinamik_klasoru = "Dinamik_Kuyular"
        os.makedirs(self.statik_klasoru, exist_ok=True)
        os.makedirs(self.dinamik_klasoru, exist_ok=True)

        self.static_mode_active = False
        self.dynamic_mode_active = False
        self.aktif_statik_kuyu = None
        self.aktif_dinamik_kuyu = None

        self.static_data_changed = False
        self.dynamic_data_changed = False

        self.casing_verileri = {
            "20 inç (ID: 19.124)": 19.124, "13 3/8 inç (ID: 12.615)": 12.615,
            "13 3/8 inç (ID: 12.415)": 12.415, "9 5/8 inç (ID: 8.835)": 8.835,
            "9 5/8 inç (ID: 8.681)": 8.681, "7 inç (ID: 6.276)": 6.276,
            "5 1/2 inç (ID: 4.892)": 4.892, "18 5/8 inç (ID: 17.755)": 17.755,
            "16 inç (ID: 15.000)": 15.0, "11 3/4 inç (ID: 10.880)": 10.88,
            "10 3/4 inç (ID: 9.850)": 9.85, "8 5/8 inç (ID: 7.825)": 7.825,
            "6 5/8 inç (ID: 5.875)": 5.875, "4 1/2 inç (ID: 3.920)": 3.92,
            "3 1/2 inç (ID: 2.922)": 2.922, "2 7/8 inç (ID: 2.441)": 2.441,
        }
        self.matkap_verileri = {
            "26 inç": 26.0, "17 1/2 inç": 17.5, "12 1/4 inç": 12.25,
            "8 1/2 inç": 8.5, "6 1/8 inç": 6.125, "20 inç": 20.0,
            "14 3/4 inç": 14.75, "9 7/8 inç": 9.875, "7 7/8 inç": 7.875,
            "5 7/8 inç": 5.875, "4 3/4 inç": 4.75, "3 7/8 inç": 3.875,
        }

        self.delik_secenekleri = [f"{k} (Matkap)" for k in self.matkap_verileri.keys()]
        for c_id in sorted(set(self.casing_verileri.values()), reverse=True):
            self.delik_secenekleri.append(f"{c_id} inç (Önceki Casing ID)")

        self.db_dc = {
            "9 1/2\" DC (ID: 3.000\")": (9.5, 3.0), "8\" DC (ID: 2.812\")": (8.0, 2.812),
            "6 1/2\" DC (ID: 2.812\")": (6.5, 2.812), "4 3/4\" DC (ID: 2.250\")": (4.75, 2.25),
            "3 1/8\" DC (ID: 1.250\")": (3.125, 1.25), "11\" DC (ID: 3.000\")": (11.0, 3.0),
            "7 1/4\" DC (ID: 2.8125\")": (7.25, 2.8125), "6 3/4\" DC (ID: 2.8125\")": (6.75, 2.8125),
            "6 1/4\" DC (ID: 2.8125\")": (6.25, 2.8125), "5 3/4\" DC (ID: 2.8125\")": (5.75, 2.8125),
            "3 1/2\" DC (ID: 1.500\")": (3.5, 1.5),
        }
        self.db_hwdp = {
            "5 1/2\" HWDP (ID: 3.250\")": (5.5, 3.25), "5\" HWDP (ID: 3.000\")": (5.0, 3.0),
            "4 1/2\" HWDP (ID: 2.750\")": (4.5, 2.75), "3 1/2\" HWDP (ID: 2.250\")": (3.5, 2.25),
            "6 5/8\" HWDP (ID: 4.500\")": (6.625, 4.5), "4\" HWDP (ID: 2.5625\")": (4.0, 2.5625),
        }
        self.db_dp = {
            "5 1/2\" DP (ID: 4.778\")": (5.5, 4.778), "5\" DP (ID: 4.276\")": (5.0, 4.276),
            "4 1/2\" DP (ID: 3.826\")": (4.5, 3.826), "4\" DP (ID: 3.340\")": (4.0, 3.340),
            "3 1/2\" DP (ID: 2.764\")": (3.5, 2.764), "2 7/8\" DP (ID: 2.151\")": (2.875, 2.151),
            "2 3/8\" DP (ID: 1.995\")": (2.375, 1.995), "6 5/8\" DP (ID: 5.965\")": (6.625, 5.965),
        }
        self.liner_olculeri = ["4", "4 1/2", "5", "5 1/2", "5 3/4", "6", "6 1/4", "6 1/2", "6 3/4", "7", "7 1/4", "7 1/2"]
        self.stroke_olculeri = ["8", "9", "10", "11", "12", "14"]

        self.tab1_eleman_listesi = []
        self.tab2_casing_listesi = []
        self.tab2_dizi_listesi = []

        self.t_ic = 0.0
        self.t_ann = 0.0
        self.t_metal = 0.0
        self.stb_min = 0.0
        self.bu_min = 0.0
        self.total_min = 0.0

        self.footer_frame = ttk.Frame(self.root, style="Card.TFrame")
        self.footer_frame.pack(side="bottom", fill="x")
        ttk.Label(self.footer_frame, text="Developed by Vahap Sevgili", 
                  font=("Segoe UI", 8, "italic"), foreground="#A0AEC0", background="#FFFFFF").pack(side="right", padx=15, pady=3)

        self.goster_yeni_baslangic()

    # ---------- STİL VE TEMA YAPILANDIRMASI ----------
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        font_base = ('Segoe UI', 10)
        font_bold = ('Segoe UI', 10, 'bold')
        font_h1 = ('Segoe UI', 24, 'bold')

        c_bg = self.bg_color
        c_card = "#FFFFFF"
        c_text = "#2D3748"
        c_accent = "#3182CE"
        c_accent_hover = "#2B6CB0"
        c_border = "#E2E8F0"
        c_success = "#38A169"

        style.configure('TFrame', background=c_bg)
        style.configure('Card.TFrame', background=c_card)
        
        style.configure('TLabel', background=c_bg, foreground=c_text, font=font_base)
        style.configure('Card.TLabel', background=c_card, foreground=c_text, font=font_base)
        style.configure('Title.TLabel', background=c_bg, foreground=c_accent, font=font_h1)
        style.configure('Success.TLabel', background=c_card, foreground=c_success, font=font_bold)
        
        style.configure('TLabelframe', background=c_card, borderwidth=1, bordercolor=c_border)
        style.configure('TLabelframe.Label', background=c_card, foreground=c_accent, font=('Segoe UI', 11, 'bold'))

        style.configure('TCheckbutton', background=c_card, foreground=c_text, font=font_base)

        style.configure('TButton', font=font_base, padding=5, background="#EDF2F7", foreground=c_text, borderwidth=0)
        style.map('TButton', background=[('active', '#E2E8F0')])

        style.configure('Primary.TButton', font=font_bold, padding=6, background=c_accent, foreground="white", borderwidth=0)
        style.map('Primary.TButton', background=[('active', c_accent_hover)])

        style.configure('TEntry', padding=4, fieldbackground=c_card, bordercolor=c_border)
        style.configure('TCombobox', padding=4, fieldbackground=c_card)

        style.configure('Treeview', font=('Segoe UI', 9), rowheight=24, background=c_card, fieldbackground=c_card, borderwidth=0)
        style.map('Treeview', background=[('selected', '#BEE3F8')], foreground=[('selected', c_text)])
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background="#EDF2F7", foreground=c_text, borderwidth=1)

        style.configure('TNotebook', background=c_card, borderwidth=0)
        style.configure('TNotebook.Tab', font=font_base, padding=[10, 4], background="#EDF2F7", foreground=c_text)
        style.map('TNotebook.Tab', background=[('selected', c_card)], foreground=[('selected', c_accent)])

    # ---------- MOUSE TEKERLEĞİ İLE KAYDIRMA YARDIMCISI ----------
    def _apply_mouse_scroll(self, parent_widget, canvas):
        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _bind_all_children(widget):
            # Tabloların kendi scroll barları olduğu için onların üzerinde ana ekranı kaydırmıyoruz
            if widget.winfo_class() not in ('Treeview', 'Scrollbar', 'Listbox', 'TCombobox'):
                widget.bind("<MouseWheel>", _on_wheel, add="+")
            for child in widget.winfo_children():
                _bind_all_children(child)
        
        _bind_all_children(parent_widget)

    # ---------- YENİ BAŞLANGIÇ EKRANI ----------
    def goster_yeni_baslangic(self):
        if hasattr(self, 'mode_frame'):
            self.mode_frame.destroy()
        self.startup_frame = ttk.Frame(self.root)
        self.startup_frame.pack(fill="both", expand=True)
        
        inner = ttk.Frame(self.startup_frame, style="Card.TFrame")
        inner.place(relx=0.5, rely=0.5, anchor="center", width=500, height=350)
        
        ttk.Label(inner, text="Profesyonel\nSondaj Hesaplayıcı", style="Title.TLabel", 
                  background="#FFFFFF", justify="center").pack(pady=(40, 30))
        
        ttk.Button(inner, text="Statik Kuyu Hacmi (Dizayn & Çimento)",
                   command=self.baslat_statik_mod, style="Primary.TButton", width=35).pack(pady=10)
        ttk.Button(inner, text="Dinamik Annüler ve Dizi İçi Hacim",
                   command=self.baslat_dinamik_mod, style="Primary.TButton", width=35).pack(pady=10)

    def baslat_statik_mod(self):
        self.startup_frame.destroy()
        self.static_mode_active = True
        self.dynamic_mode_active = False
        self.aktif_statik_kuyu = None
        self.static_data_changed = False
        self.tab1_eleman_listesi = []
        self.mode_frame = ttk.Frame(self.root)
        self.mode_frame.pack(fill="both", expand=True)
        self._build_static_mode(self.mode_frame)

    def baslat_dinamik_mod(self):
        self.startup_frame.destroy()
        self.dynamic_mode_active = True
        self.static_mode_active = False
        self.aktif_dinamik_kuyu = None
        self.dynamic_data_changed = False
        self.tab2_casing_listesi = []
        self.tab2_dizi_listesi = []
        self.t_ic = self.t_ann = self.t_metal = 0.0
        self.mode_frame = ttk.Frame(self.root)
        self.mode_frame.pack(fill="both", expand=True)
        self._build_dynamic_mode(self.mode_frame)

    def ana_menuye_don(self):
        self.static_mode_active = False
        self.dynamic_mode_active = False
        self.mode_frame.destroy()
        self.goster_yeni_baslangic()

    # ---------- STATİK MOD ARAYÜZÜ ----------
    def _build_static_mode(self, parent):
        main = ttk.Frame(parent, style="Card.TFrame")
        main.pack(fill="both", expand=True)

        # 1. EN ALT PANEL - Her zaman görünür kalması için İLK EKLENİR
        kayit_frame = ttk.Frame(main, padding=(15, 10), style="TFrame")
        kayit_frame.pack(side="bottom", fill="x")
        
        durum = f"Açık Dosya: {self.aktif_statik_kuyu}" if self.aktif_statik_kuyu else "Durum: Kaydedilmemiş"
        self.statik_lbl_durum = ttk.Label(kayit_frame, text=durum, style="Success.TLabel", background="#F0F4F8")
        self.statik_lbl_durum.pack(side="left")
        
        self.statik_btn_kaydet = ttk.Button(kayit_frame, text="Kaydet", state="disabled", command=self.statik_kaydet, style="Primary.TButton")
        self.statik_btn_kaydet.pack(side="right", padx=5)
        ttk.Button(kayit_frame, text="Farklı Kaydet", command=self.statik_farkli_kaydet).pack(side="right", padx=5)
        ttk.Button(kayit_frame, text="Kayıtlı Aç", command=self.statik_yukle_dialog).pack(side="right", padx=5)
        ttk.Button(kayit_frame, text="Anasayfaya Dön", command=self.static_return_to_home).pack(side="left", padx=20)

        # 2. İÇERİK BÖLÜMÜ - Kaydırılabilir Canvas Yapısı
        wrapper = ttk.Frame(main, style="Card.TFrame")
        wrapper.pack(side="top", fill="both", expand=True)
        
        canvas = tk.Canvas(wrapper, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        
        content_frame = ttk.Frame(canvas, style="Card.TFrame", padding=15)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # İçerik elemanları grid ile ekleniyor
        content_frame.grid_columnconfigure(0, weight=1)

        gen_f = ttk.LabelFrame(content_frame, text="1. Kuyu ve Section Bilgisi", padding=10)
        gen_f.grid(row=0, column=0, sticky="ew", pady=(0,10))
        ttk.Label(gen_f, text="Toplam Derinlik (TD) (m):", style="Card.TLabel").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.tab1_td_entry = ttk.Entry(gen_f, width=15, validate='key', validatecommand=self.vcmd)
        self.tab1_td_entry.grid(row=0, column=1, padx=5, pady=2)
        self.tab1_td_entry.bind('<KeyRelease>', lambda e: [self.tab1_toplam_guncelle(), self._mark_static_changed()])

        girdi_frame = ttk.LabelFrame(content_frame, text="2. Operasyon Senaryosu ve Hacim Girdileri", padding=10)
        girdi_frame.grid(row=1, column=0, sticky="ew", pady=(0,10))
        for col in range(4): girdi_frame.columnconfigure(col, weight=1)

        ttk.Label(girdi_frame, text="Operasyon Türü:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        self.tab1_tur_var = tk.StringVar(value="Çimentolu Casing")
        tur_combo = ttk.Combobox(girdi_frame, textvariable=self.tab1_tur_var,
                                 values=["Çimentolu Casing", "Çimentolu Liner", "Filtreli Casing/Liner"], state="readonly", width=25)
        tur_combo.grid(row=0, column=1, padx=5, sticky="w")
        tur_combo.bind('<<ComboboxSelected>>', self.tab1_tur_degisti)

        ttk.Label(girdi_frame, text="Kuyu / Matkap Çapı:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.tab1_delik_secim = ttk.Combobox(girdi_frame, values=self.delik_secenekleri, width=25)
        self.tab1_delik_secim.grid(row=1, column=1, padx=5, sticky="w")

        ttk.Label(girdi_frame, text="Açık Kuyu Washout (%):", style="Card.TLabel").grid(row=1, column=2, sticky="w", pady=5, padx=10)
        self.tab1_washout = ttk.Entry(girdi_frame, width=12, validate='key', validatecommand=self.vcmd)
        self.tab1_washout.insert(0, "0")
        self.tab1_washout.grid(row=1, column=3, padx=5, sticky="w")

        ttk.Label(girdi_frame, text="İndirilen Casing Çapı:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        self.tab1_cap_secim = ttk.Combobox(girdi_frame, values=list(self.casing_verileri.keys()), state="readonly", width=25)
        self.tab1_cap_secim.grid(row=2, column=1, padx=5, sticky="w")

        ttk.Label(girdi_frame, text="Önceki Casing ID (Lap için):", style="Card.TLabel").grid(row=2, column=2, sticky="w", pady=5, padx=10)
        self.tab1_prev_id = ttk.Combobox(girdi_frame, values=list(set(self.casing_verileri.values())), width=12)
        self.tab1_prev_id.grid(row=2, column=3, padx=5, sticky="w")

        ttk.Label(girdi_frame, text="Üst / Pabuç Derinliği (m):", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        der_frame = ttk.Frame(girdi_frame, style="Card.TFrame")
        der_frame.grid(row=3, column=1, sticky="w")
        self.tab1_ust = ttk.Entry(der_frame, width=10, validate='key', validatecommand=self.vcmd)
        self.tab1_ust.insert(0, "0")
        self.tab1_ust.pack(side="left")
        ttk.Label(der_frame, text=" / ", style="Card.TLabel").pack(side="left")
        self.tab1_alt = ttk.Entry(der_frame, width=10, validate='key', validatecommand=self.vcmd)
        self.tab1_alt.pack(side="left")

        ttk.Label(girdi_frame, text="Yaka (Float Collar) Derinliği (m):", style="Card.TLabel").grid(row=3, column=2, sticky="w", pady=5, padx=10)
        self.tab1_fc = ttk.Entry(girdi_frame, width=12, validate='key', validatecommand=self.vcmd)
        self.tab1_fc.grid(row=3, column=3, padx=5, sticky="w")

        ttk.Label(girdi_frame, text="TOC (Çimento Üstü) (m):", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=5)
        self.tab1_toc = ttk.Entry(girdi_frame, width=12, validate='key', validatecommand=self.vcmd)
        self.tab1_toc.grid(row=4, column=1, padx=5, sticky="w")
        
        ttk.Label(girdi_frame, text="Önceki Pabuç (Lap Üstü) (m):", style="Card.TLabel").grid(row=4, column=2, sticky="w", pady=5, padx=10)
        self.tab1_prev_shoe = ttk.Entry(girdi_frame, width=12, validate='key', validatecommand=self.vcmd)
        self.tab1_prev_shoe.grid(row=4, column=3, padx=5, sticky="w")

        ttk.Button(girdi_frame, text="Operasyonu Ekle ve Hesapla", command=self.tab1_ekle, style="Primary.TButton").grid(row=5, column=0, columnspan=4, pady=(10, 0))

        # Tablo
        self.tab1_tablo = ttk.Treeview(content_frame, columns=("tur","c","u","a","toc","cim","st","disp"), show="headings", height=5)
        self.tab1_tablo.tag_configure('oddrow', background="#F7FAFC")
        self.tab1_tablo.tag_configure('evenrow', background="#FFFFFF")

        basliklar = ["Tür", "Çap", "Üst (m)", "Pabuç (m)", "TOC (m)", "Toplam Çimento (bbl)", "Shoe Track (bbl)", "Displacement (bbl)"]
        for c, h in zip(self.tab1_tablo["columns"], basliklar):
            self.tab1_tablo.heading(c, text=h)
            self.tab1_tablo.column(c, anchor="center", width=100)
        self.tab1_tablo.grid(row=2, column=0, sticky="nsew", pady=5)

        alt_panel = ttk.Frame(content_frame, style="Card.TFrame", padding=(0, 5))
        alt_panel.grid(row=3, column=0, sticky="ew")
        ttk.Button(alt_panel, text="Seçili Operasyonu Sil", command=self.tab1_sil).pack(side="left")
        
        sag = ttk.Frame(alt_panel, style="Card.TFrame")
        sag.pack(side="right")
        self.lbl_toplam_cimento = ttk.Label(sag, text="Gereken Toplam Çimento: 0.00 bbl", font=("Segoe UI", 11, "bold"), foreground="#C53030", background="#FFFFFF")
        self.lbl_toplam_cimento.pack(anchor="e", pady=1)
        self.lbl_shoe_track = ttk.Label(sag, text="Shoe Track Hacmi: 0.00 bbl", foreground="#718096", background="#FFFFFF")
        self.lbl_shoe_track.pack(anchor="e")
        self.lbl_displacement = ttk.Label(sag, text="Displacement (Sıyırma) Sıvısı: 0.00 bbl", font=("Segoe UI", 11, "bold"), foreground="#2B6CB0", background="#FFFFFF")
        self.lbl_displacement.pack(anchor="e", pady=1)
        self.lbl_toplam_statik = ttk.Label(sag, text="Tüm Kuyu Metal Hariç Statik Sıvı Hacmi: 0.00 bbl", style="Card.TLabel")
        self.lbl_toplam_statik.pack(anchor="e", pady=1)

        # Fare tekerleğiyle kaydırmayı aktif et
        self._apply_mouse_scroll(content_frame, canvas)
        self._apply_mouse_scroll(canvas, canvas)

    def tab1_tur_degisti(self, event=None):
        tur = self.tab1_tur_var.get()
        if "Liner" in tur:
            self.tab1_ust.config(state="normal")
            self.tab1_ust.delete(0, tk.END)
        else:
            self.tab1_ust.config(state="normal")
            self.tab1_ust.delete(0, tk.END)
            self.tab1_ust.insert(0, "0")
            self.tab1_ust.config(state="disabled")

        if "Filtreli" in tur:
            self.tab1_toc.delete(0, tk.END)
            self.tab1_toc.config(state="disabled")
            self.tab1_washout.delete(0, tk.END)
            self.tab1_washout.insert(0, "0")
            self.tab1_washout.config(state="disabled")
            self.tab1_fc.delete(0, tk.END)
            self.tab1_fc.config(state="disabled")
        else:
            self.tab1_toc.config(state="normal")
            self.tab1_washout.config(state="normal")
            self.tab1_fc.config(state="normal")

    def tab1_ekle(self):
        try:
            tur = self.tab1_tur_var.get()
            secim = self.tab1_cap_secim.get()
            u = float(self.tab1_ust.get() if self.tab1_ust.get() else 0.0)
            a = float(self.tab1_alt.get())
            delik_str = self.tab1_delik_secim.get()
            prev_id_str = self.tab1_prev_id.get()
            prev_shoe_str = self.tab1_prev_shoe.get()
            
            id_val = self.casing_verileri[secim]
            od_val = self.parse_inch(secim)
            delik_val = self.parse_inch(delik_str) if delik_str else od_val
            prev_id = float(prev_id_str) if prev_id_str else delik_val
            prev_shoe = float(prev_shoe_str) if prev_shoe_str else 0.0

            if u >= a:
                messagebox.showwarning("Hata", "Pabuç derinliği, üst derinlikten büyük olmalıdır.")
                return

            cimento_hacmi = 0.0
            shoe_track_hacmi = 0.0
            displacement_hacmi = 0.0
            statik_sivi = ((id_val ** 2) / 1029.4) * (a - u) * 3.28084 

            if "Filtreli" not in tur:
                fc = float(self.tab1_fc.get() if self.tab1_fc.get() else a)
                toc = float(self.tab1_toc.get() if self.tab1_toc.get() else u)
                washout = float(self.tab1_washout.get() if self.tab1_washout.get() else 0.0) / 100.0

                oh_top = max(prev_shoe, toc)
                if a > oh_top:
                    cimento_hacmi += ((delik_val**2 - od_val**2)/1029.4) * (a - oh_top) * 3.28084 * (1 + washout)
                
                if toc < prev_shoe:
                    lap_bottom = min(a, prev_shoe)
                    cimento_hacmi += ((prev_id**2 - od_val**2)/1029.4) * (lap_bottom - toc) * 3.28084
                
                if fc < a:
                    shoe_track_hacmi = ((id_val**2)/1029.4) * (a - fc) * 3.28084
                    cimento_hacmi += shoe_track_hacmi
                
                displacement_hacmi = ((id_val**2)/1029.4) * (fc - u) * 3.28084

            else:
                arkasi_akiskan = ((delik_val**2 - od_val**2)/1029.4) * (a - u) * 3.28084
                statik_sivi += arkasi_akiskan
                toc = "-"

            item = {
                "tur": tur, "isim": secim.split('(')[0].strip(),
                "od": od_val, "id": id_val, "delik": delik_val,
                "ust": u, "alt": a, "toc": toc,
                "cim": cimento_hacmi, "st": shoe_track_hacmi, 
                "disp": displacement_hacmi, "statik": statik_sivi
            }
            self.tab1_eleman_listesi.append(item)
            self.tab1_tabloyu_ciz()
            self._mark_static_changed()

        except ValueError:
            messagebox.showerror("Veri Hatası", "Lütfen gerekli tüm derinlik ve çap verilerini eksiksiz girin.")
        except KeyError:
            messagebox.showerror("Seçim Hatası", "Lütfen geçerli bir çap seçin.")

    def tab1_tabloyu_ciz(self):
        for i in self.tab1_tablo.get_children():
            self.tab1_tablo.delete(i)
        for index, el in enumerate(self.tab1_eleman_listesi):
            toc_text = f"{el['toc']:.1f}" if el['toc'] != "-" else "-"
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tab1_tablo.insert("", "end", values=(
                el['tur'], el['isim'], f"{el['ust']:.1f}", f"{el['alt']:.1f}", toc_text,
                f"{el['cim']:.2f}", f"{el['st']:.2f}", f"{el['disp']:.2f}"
            ), tags=(tag,))
        self.tab1_toplam_guncelle()

    def tab1_sil(self):
        sel = self.tab1_tablo.selection()
        if sel:
            idx = self.tab1_tablo.index(sel[0])
            self.tab1_eleman_listesi.pop(idx)
            self.tab1_tabloyu_ciz()
            self._mark_static_changed()

    def tab1_toplam_guncelle(self):
        if not self.tab1_eleman_listesi:
            self.lbl_toplam_cimento.config(text="Gereken Toplam Çimento: 0.00 bbl")
            self.lbl_shoe_track.config(text="Shoe Track Hacmi: 0.00 bbl")
            self.lbl_displacement.config(text="Displacement (Sıyırma) Sıvısı: 0.00 bbl")
            self.lbl_toplam_statik.config(text="Tüm Kuyu Metal Hariç Statik Sıvı Hacmi: 0.00 bbl")
            return
        
        cim_toplam = sum(el['cim'] for el in self.tab1_eleman_listesi)
        st_toplam = sum(el['st'] for el in self.tab1_eleman_listesi)
        disp_toplam = sum(el['disp'] for el in self.tab1_eleman_listesi)
        statik_toplam = sum(el['statik'] for el in self.tab1_eleman_listesi)

        self.lbl_toplam_cimento.config(text=f"Gereken Toplam Çimento: {cim_toplam:.2f} bbl")
        self.lbl_shoe_track.config(text=f"Shoe Track Hacmi: {st_toplam:.2f} bbl")
        self.lbl_displacement.config(text=f"Displacement (Sıyırma) Sıvısı: {disp_toplam:.2f} bbl")
        self.lbl_toplam_statik.config(text=f"Tüm Kuyu Metal Hariç Statik Sıvı Hacmi: {statik_toplam:.2f} bbl")

    def statik_verileri_paketle(self):
        return {"tab1_td": self.tab1_td_entry.get(), "tab1_listesi": self.tab1_eleman_listesi}

    def statik_kaydet(self):
        if not self.aktif_statik_kuyu:
            self.statik_farkli_kaydet()
            return
        yol = os.path.join(self.statik_klasoru, f"{self.aktif_statik_kuyu}.json")
        try:
            with open(yol, "w", encoding="utf-8") as f:
                json.dump(self.statik_verileri_paketle(), f, indent=4)
            self.static_data_changed = False
            self.statik_btn_kaydet.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydedilemedi:\n{e}")

    def statik_farkli_kaydet(self):
        ad = simpledialog.askstring("Kuyu Kaydet", "Projeye/Kuyuya isim verin:")
        if not ad: return
        yol = os.path.join(self.statik_klasoru, f"{ad}.json")
        if os.path.exists(yol):
            if not messagebox.askyesno("Uyarı", "Bu isimde bir kayıt zaten var. Üzerine yazılsın mı?"): return
        self.aktif_statik_kuyu = ad
        self.statik_lbl_durum.config(text=f"Açık Dosya: {ad}", foreground="#38A169")
        self.statik_kaydet()

    def statik_yukle_dialog(self):
        top = tk.Toplevel(self.root)
        top.title("Kayıtlı Kuyular")
        top.geometry("400x500")
        top.configure(bg=self.bg_color)
        top.transient(self.root); top.grab_set()
        
        ttk.Label(top, text="Kayıtlı Projeler (Statik)", style="Title.TLabel", font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        list_frame = ttk.Frame(top, style="Card.TFrame", padding=10)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        liste = tk.Listbox(list_frame, font=("Segoe UI", 11), borderwidth=0, highlightthickness=0, selectbackground="#3182CE")
        liste.pack(fill="both", expand=True)
        
        def doldur():
            liste.delete(0, tk.END)
            for dosya in os.listdir(self.statik_klasoru):
                if dosya.endswith(".json"): liste.insert("end", dosya[:-5])
        doldur()
        
        btn_frame = ttk.Frame(top, style="TFrame")
        btn_frame.pack(pady=15)
        btn_yukle = ttk.Button(btn_frame, text="Yükle", state="disabled", style="Primary.TButton")
        btn_yukle.pack(side="left", padx=5)
        btn_sil = ttk.Button(btn_frame, text="Kalıcı Olarak Sil", state="disabled")
        btn_sil.pack(side="left", padx=5)
        
        def on_select(event):
            state = "normal" if liste.curselection() else "disabled"
            btn_yukle.config(state=state); btn_sil.config(state=state)
        liste.bind('<<ListboxSelect>>', on_select)
        
        def yukle():
            sec = liste.curselection()
            if sec:
                ad = liste.get(sec[0]); self._statik_yukle(ad); top.destroy()
        def sil():
            sec = liste.curselection()
            if sec:
                ad = liste.get(sec[0])
                if messagebox.askyesno("Silme Onayı", "Seçili kuyuya ait tüm veriler kalıcı olarak silinecek. Emin misiniz?"):
                    if self._delete_well_file(self.statik_klasoru, ad):
                        if self.aktif_statik_kuyu == ad:
                            self.aktif_statik_kuyu = None
                            self.statik_lbl_durum.config(text="Durum: Kaydedilmemiş", foreground="#2D3748")
                            self.statik_btn_kaydet.config(state="disabled")
                        doldur()
                        if not liste.get(0, tk.END): btn_yukle.config(state="disabled"); btn_sil.config(state="disabled")
        btn_yukle.config(command=yukle); btn_sil.config(command=sil)

    def _statik_yukle(self, ad):
        yol = os.path.join(self.statik_klasoru, f"{ad}.json")
        try:
            with open(yol, "r", encoding="utf-8") as f: data = json.load(f)
        except Exception as e:
            messagebox.showerror("Hata", f"Okunamadı:\n{e}"); return
        self.aktif_statik_kuyu = ad
        self.statik_lbl_durum.config(text=f"Açık Dosya: {ad}", foreground="#38A169")
        self.tab1_td_entry.delete(0, tk.END); self.tab1_td_entry.insert(0, data.get("tab1_td", ""))
        self.tab1_eleman_listesi = data.get("tab1_listesi", [])
        self.tab1_tabloyu_ciz()
        self.static_data_changed = False
        self.statik_btn_kaydet.config(state="disabled")

    # ---------- DİNAMİK MOD ARAYÜZÜ ----------
    def _build_dynamic_mode(self, parent):
        main_area = ttk.Frame(parent, style="Card.TFrame")
        main_area.pack(fill="both", expand=True)

        # 1. EN ALT PANEL - İLK EKLENİR
        kayit_frame = ttk.Frame(main_area, padding=(15, 10), style="TFrame")
        kayit_frame.pack(side="bottom", fill="x")
        
        durum = f"Açık Dosya: {self.aktif_dinamik_kuyu}" if self.aktif_dinamik_kuyu else "Durum: Kaydedilmemiş"
        self.dinamik_lbl_durum = ttk.Label(kayit_frame, text=durum, style="Success.TLabel", background="#F0F4F8")
        self.dinamik_lbl_durum.pack(side="left")
        
        self.dinamik_btn_kaydet = ttk.Button(kayit_frame, text="Kaydet", state="disabled", command=self.dinamik_kaydet, style="Primary.TButton")
        self.dinamik_btn_kaydet.pack(side="right", padx=5)
        ttk.Button(kayit_frame, text="Farklı Kaydet", command=self.dinamik_farkli_kaydet).pack(side="right", padx=5)
        ttk.Button(kayit_frame, text="Kayıtlı Aç", command=self.dinamik_yukle_dialog).pack(side="right", padx=5)
        ttk.Button(kayit_frame, text="Anasayfaya Dön", command=self.dynamic_return_to_home).pack(side="left", padx=20)

        # 2. İÇERİK BÖLÜMÜ - Kaydırılabilir
        wrapper = ttk.Frame(main_area, style="Card.TFrame")
        wrapper.pack(side="top", fill="both", expand=True)
        
        canvas = tk.Canvas(wrapper, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        
        content_frame = ttk.Frame(canvas, style="Card.TFrame", padding=15)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content_frame.grid_columnconfigure(0, weight=1)

        ust_panel = ttk.Frame(content_frame, style="Card.TFrame")
        ust_panel.grid(row=0, column=0, sticky="ew", pady=(0,10))
        ust_panel.columnconfigure(0, weight=1)
        ust_panel.columnconfigure(1, weight=2)

        kuyu_f = ttk.LabelFrame(ust_panel, text="1. Kuyu Derinliği", padding=8)
        kuyu_f.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        ttk.Label(kuyu_f, text="Matkap:", style="Card.TLabel").grid(row=0, column=0, pady=2, sticky="w")
        self.tab2_matkap_combo = ttk.Combobox(kuyu_f, values=list(self.matkap_verileri.keys()), state="readonly", width=14)
        self.tab2_matkap_combo.grid(row=0, column=1, pady=2, padx=5)
        self.tab2_matkap_combo.bind('<<ComboboxSelected>>', lambda e: [self.tab2_yeniden_hesapla(), self._mark_dynamic_changed()])
        ttk.Label(kuyu_f, text="TD (m):", style="Card.TLabel").grid(row=1, column=0, pady=2, sticky="w")
        self.tab2_td_entry = ttk.Entry(kuyu_f, width=14, validate='key', validatecommand=self.vcmd)
        self.tab2_td_entry.grid(row=1, column=1, pady=2, padx=5)
        self.tab2_td_entry.bind('<KeyRelease>', lambda e: [self.tab2_yeniden_hesapla(), self._mark_dynamic_changed()])

        cas_f = ttk.LabelFrame(ust_panel, text="2. Casing Dizaynı", padding=8)
        cas_f.grid(row=0, column=1, sticky="nsew")
        self.tab2_casing_combo = ttk.Combobox(cas_f, values=list(self.casing_verileri.keys()), state="readonly", width=28)
        self.tab2_casing_combo.grid(row=0, column=0, columnspan=2, pady=2, padx=5, sticky="w")
        self.tab2_cas_filtre_var = tk.BooleanVar()
        ttk.Checkbutton(cas_f, text="Filtreli", variable=self.tab2_cas_filtre_var).grid(row=0, column=2, pady=2, padx=5)
        alt_cas = ttk.Frame(cas_f, style="Card.TFrame")
        alt_cas.grid(row=1, column=0, columnspan=3, pady=2, sticky="w")
        ttk.Label(alt_cas, text="Üst/Alt: ", style="Card.TLabel").pack(side="left")
        self.tab2_casing_ust = ttk.Entry(alt_cas, width=8, validate='key', validatecommand=self.vcmd)
        self.tab2_casing_ust.pack(side="left", padx=2)
        self.tab2_casing_alt = ttk.Entry(alt_cas, width=8, validate='key', validatecommand=self.vcmd)
        self.tab2_casing_alt.pack(side="left", padx=2)
        ttk.Button(alt_cas, text="Ekle", command=self.tab2_casing_ekle, style="Primary.TButton").pack(side="left", padx=15)

        casing_frame = ttk.Frame(content_frame, style="Card.TFrame")
        casing_frame.grid(row=1, column=0, sticky="ew", pady=(0,10))
        casing_frame.columnconfigure(0, weight=1)
        self.tab2_casing_tablo = ttk.Treeview(casing_frame, columns=("c","od","id","u","a","s"), show="headings", height=3)
        self.tab2_casing_tablo.tag_configure('oddrow', background="#F7FAFC")
        self.tab2_casing_tablo.tag_configure('evenrow', background="#FFFFFF")

        cas_headings = ["Casing", "Dış Çap (inç)", "İç Çap (inç)", "Üst", "Alt", "Durum"]
        for col, head in zip(self.tab2_casing_tablo["columns"], cas_headings):
            self.tab2_casing_tablo.heading(col, text=head)
            self.tab2_casing_tablo.column(col, anchor="center", width=85, minwidth=70)
        self.tab2_casing_tablo.column("c", width=130, minwidth=100)
        self.tab2_casing_tablo.grid(row=0, column=0, sticky="nsew")
        ttk.Button(casing_frame, text="Sil", command=self.tab2_casing_sil).grid(row=0, column=1, padx=10)

        dizi_f = ttk.LabelFrame(content_frame, text="3. BHA (Dizi) Düzenle", padding=10)
        dizi_f.grid(row=2, column=0, sticky="nsew", pady=5)
        dizi_f.grid_columnconfigure(0, weight=1)

        cekmece_tab = ttk.Notebook(dizi_f)
        cekmece_tab.grid(row=0, column=0, sticky="ew", pady=(0,5))

        def cekmece_olustur(parent, db, func):
            frame = ttk.Frame(parent, padding=8, style="Card.TFrame")
            combo = ttk.Combobox(frame, values=list(db.keys()), state="readonly", width=40)
            combo.pack(side="left", padx=5)
            ttk.Label(frame, text="Uzunluk (m):", style="Card.TLabel").pack(side="left", padx=(15, 5))
            ent = ttk.Entry(frame, width=10, validate='key', validatecommand=self.vcmd)
            ent.pack(side="left", padx=5)
            ttk.Button(frame, text="Ekle", command=lambda: func(combo, ent, db), style="Primary.TButton").pack(side="left", padx=20)
            return frame

        self.cekmece_dc = cekmece_olustur(cekmece_tab, self.db_dc, self.tab2_dizi_ekle_universal)
        self.cekmece_hwdp = cekmece_olustur(cekmece_tab, self.db_hwdp, self.tab2_dizi_ekle_universal)
        self.cekmece_dp = cekmece_olustur(cekmece_tab, self.db_dp, self.tab2_dizi_ekle_universal)
        cekmece_tab.add(self.cekmece_dc, text="Drill Collars (DC)")
        cekmece_tab.add(self.cekmece_hwdp, text="Heavy Weight (HWDP)")
        cekmece_tab.add(self.cekmece_dp, text="Drill Pipe (DP)")

        self.yuzeye_kalan_label = ttk.Label(dizi_f, text="Kalan Mesafe: -", font=("Segoe UI", 11, "bold"), foreground="#3182CE", background="#FFFFFF")
        self.yuzeye_kalan_label.grid(row=0, column=1, sticky="e", padx=10)

        dizi_tablo_frame = ttk.Frame(dizi_f, style="Card.TFrame")
        dizi_tablo_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        dizi_tablo_frame.grid_columnconfigure(0, weight=1)

        self.tab2_dizi_tablo = ttk.Treeview(dizi_tablo_frame, columns=("e","od","id","d","ic","metal"), show="headings", height=4)
        self.tab2_dizi_tablo.tag_configure('oddrow', background="#F7FAFC")
        self.tab2_dizi_tablo.tag_configure('evenrow', background="#FFFFFF")

        dizi_headings = ["Eleman", "Dış Çap (inç)", "İç Çap (inç)", "Derinlik Aralığı (m)", "Dizi İçi (bbl)", "Taşırma (bbl)"]
        for col, head in zip(self.tab2_dizi_tablo["columns"], dizi_headings):
            self.tab2_dizi_tablo.heading(col, text=head)
            self.tab2_dizi_tablo.column(col, width=90, minwidth=70, anchor="center")
        self.tab2_dizi_tablo.column("e", width=220, minwidth=150)
        self.tab2_dizi_tablo.grid(row=0, column=0, sticky="nsew")
        ttk.Button(dizi_tablo_frame, text="Sil", command=self.tab2_dizi_sil).grid(row=0, column=1, padx=10, sticky="n")

        self.dinamik_metal_label = ttk.Label(dizi_f, text="Toplam Taşırma Hacmi: 0.00 bbl", font=("Segoe UI", 10, "bold"), foreground="#718096", background="#FFFFFF")
        self.dinamik_metal_label.grid(row=1, column=1, sticky="se", padx=10, pady=5)

        sonuc_f = ttk.Frame(content_frame, style="Card.TFrame", padding=(0, 2))
        sonuc_f.grid(row=3, column=0, sticky="ew")
        self.tab2_sonuc_label = ttk.Label(sonuc_f, text="Dizi İçi: 0.00 bbl | Dinamik Kuyu Hacmi: 0.00 bbl", font=("Segoe UI", 14, "bold"), background="#FFFFFF", foreground="#2D3748")
        self.tab2_sonuc_label.pack(side="right")

        self._build_pump_panel(content_frame)
        
        # Fare tekerleğiyle kaydırmayı aktif et
        self._apply_mouse_scroll(content_frame, canvas)
        self._apply_mouse_scroll(canvas, canvas)

    def _build_pump_panel(self, parent):
        pompa_f = ttk.LabelFrame(parent, text="4. Çamur Pompa Bilgileri ve Sirkülasyon Süreleri", padding=10)
        pompa_f.grid(row=4, column=0, sticky="ew", pady=(5, 0))
        for i in range(6):
            pompa_f.columnconfigure(i, weight=1)

        basliklar = ["Pompa", "Liner (inç)", "Stroke (inç)", "Verim (%)", "Hız (SPM)"]
        for col, baslik in enumerate(basliklar):
            ttk.Label(pompa_f, text=baslik, font=("Segoe UI", 10, "bold"), background="#FFFFFF").grid(row=0, column=col, padx=5, pady=(0, 5))

        self.pompalar = []
        for i in range(4):
            var_aktif = tk.BooleanVar(value=(True if i == 0 else False))
            chk = ttk.Checkbutton(pompa_f, text=f"Pompa {i+1}", variable=var_aktif, command=self.sirkulasyon_hesapla)
            chk.grid(row=i+1, column=0, sticky="w", padx=5, pady=2)

            cmb_liner = ttk.Combobox(pompa_f, values=self.liner_olculeri, width=10)
            cmb_liner.set("6")
            cmb_liner.grid(row=i+1, column=1, padx=5, pady=2, sticky="ew")
            cmb_liner.bind('<<ComboboxSelected>>', lambda e: self.sirkulasyon_hesapla())

            cmb_stroke = ttk.Combobox(pompa_f, values=self.stroke_olculeri, width=10)
            cmb_stroke.set("11")
            cmb_stroke.grid(row=i+1, column=2, padx=5, pady=2, sticky="ew")
            cmb_stroke.bind('<<ComboboxSelected>>', lambda e: self.sirkulasyon_hesapla())

            ent_verim = ttk.Entry(pompa_f, width=10, validate='key', validatecommand=self.vcmd)
            ent_verim.insert(0, "97")
            ent_verim.grid(row=i+1, column=3, padx=5, pady=2, sticky="ew")
            ent_verim.bind('<KeyRelease>', lambda e: self.sirkulasyon_hesapla())

            ent_spm = ttk.Entry(pompa_f, width=10, validate='key', validatecommand=self.vcmd)
            ent_spm.insert(0, "120" if i == 0 else "0")
            ent_spm.grid(row=i+1, column=4, padx=5, pady=2, sticky="ew")
            ent_spm.bind('<KeyRelease>', lambda e: self.sirkulasyon_hesapla())

            self.pompalar.append({
                "aktif": var_aktif, "liner": cmb_liner, "stroke": cmb_stroke,
                "verim": ent_verim, "spm": ent_spm
            })

        sonuc_paneli = ttk.Frame(pompa_f, style="Card.TFrame")
        sonuc_paneli.grid(row=1, column=5, rowspan=4, sticky="nsew", padx=20)
        self.sure_stb_label = ttk.Label(sonuc_paneli, text="Yüzeyden Matkaba: 0.0 dk", background="#FFFFFF")
        self.sure_stb_label.pack(anchor="w")
        self.sure_bu_label = ttk.Label(sonuc_paneli, text="Bottom-Up (Ucundan Yüzeye): 0.0 dk", font=("Segoe UI", 10, "bold"), foreground="#C53030", background="#FFFFFF")
        self.sure_bu_label.pack(anchor="w", pady=4)
        self.sure_tot_label = ttk.Label(sonuc_paneli, text="Tam Sirkülasyon: 0.0 dk", font=("Segoe UI", 10, "bold"), foreground="#2B6CB0", background="#FFFFFF")
        self.sure_tot_label.pack(anchor="w")

    # ---------- DEĞİŞİKLİK TAKİBİ VE DİYALOGLAR ----------
    def _mark_static_changed(self, *args):
        if self.static_mode_active:
            self.static_data_changed = True
            if hasattr(self, 'statik_btn_kaydet'):
                self.statik_btn_kaydet.config(state="normal")

    def _mark_dynamic_changed(self, *args):
        if self.dynamic_mode_active:
            self.dynamic_data_changed = True
            if hasattr(self, 'dinamik_btn_kaydet'):
                self.dinamik_btn_kaydet.config(state="normal")

    def _show_save_discard_dialog(self, mode_name):
        dialog = tk.Toplevel(self.root)
        dialog.title("Kaydedilmemiş Değişiklikler")
        dialog.geometry("450x180")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Developed by Vahap Sevgili", font=("Segoe UI", 8, "italic"), foreground="#A0AEC0", background=self.bg_color).pack(side="bottom", anchor="e", padx=10, pady=5)

        msg = f"{mode_name} modunda kaydedilmemiş değişiklikler var.\nNe yapmak istersiniz?"
        ttk.Label(dialog, text=msg, font=('Segoe UI', 11), background=self.bg_color, justify="center").pack(pady=25)
        
        result = tk.StringVar(value="")
        def save_and_close(): result.set("save"); dialog.destroy()
        def discard_and_close(): result.set("discard"); dialog.destroy()
        
        btn_frame = ttk.Frame(dialog, style="TFrame")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Değişiklikleri Kaydet", command=save_and_close, style="Primary.TButton").pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Son Değişiklikleri Sil", command=discard_and_close).pack(side="left", padx=10)
        dialog.wait_window()
        return result.get()

    def static_return_to_home(self):
        if self.static_data_changed:
            action = self._show_save_discard_dialog("Statik Kuyu Hacmi (Dizayn)")
            if action == "save":
                if self.aktif_statik_kuyu: self.statik_kaydet()
                else: self.statik_farkli_kaydet()
            elif action == "discard": pass
            else: return
        self.ana_menuye_don()

    def dynamic_return_to_home(self):
        if self.dynamic_data_changed:
            action = self._show_save_discard_dialog("Dinamik Annüler ve Dizi İçi Hacim")
            if action == "save":
                if self.aktif_dinamik_kuyu: self.dinamik_kaydet()
                else: self.dinamik_farkli_kaydet()
            elif action == "discard": pass
            else: return
        self.ana_menuye_don()

    # ---------- ORTAK YARDIMCI FONKSİYONLAR ----------
    def _validate_numeric(self, action, value_if_allowed):
        if action == '1':
            if value_if_allowed == "" or value_if_allowed == ".": return True
            try:
                float(value_if_allowed)
                if re.search(r'[^0-9.]+', value_if_allowed): return False
                return True
            except ValueError:
                self.root.bell()
                return False
        return True

    def parse_inch(self, val):
        val = str(val).split('(')[0].strip()
        val = re.sub(r'[^\d\s/]', '', val).strip()
        if not val: return 0.0
        if " " in val:
            parts = val.split()
            whole = float(parts[0])
            frac = parts[1].split('/')
            return whole + float(frac[0]) / float(frac[1])
        elif "/" in val:
            frac = val.split('/')
            return float(frac[0]) / float(frac[1])
        return float(val)

    def _metal_volume(self, od, id_in, length_m):
        if length_m <= 0 or od <= id_in: return 0.0
        return ((od**2 - id_in**2) / 1029.4) * (length_m * 3.28084)

    def _delete_well_file(self, klasor, ad):
        yol = os.path.join(klasor, f"{ad}.json")
        try:
            if os.path.exists(yol):
                os.remove(yol)
                return True
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya silinemedi:\n{str(e)}")
        return False

    def _compute_wellbore_capacity(self, td, casing_list, bit_size):
        boundaries = set([0.0, td])
        for cas in casing_list:
            boundaries.add(cas['u']); boundaries.add(cas['a'])
        sorted_b = sorted(boundaries)
        total = 0.0
        for i in range(len(sorted_b) - 1):
            top = sorted_b[i]
            bottom = sorted_b[i + 1]
            if bottom <= 0.0 or top >= td: continue
            top = max(top, 0.0); bottom = min(bottom, td)
            if bottom <= top: continue
            length_m = bottom - top
            mid = (top + bottom) / 2.0
            hole_diam = None
            min_id = float('inf')
            for cas in casing_list:
                if cas['u'] <= mid <= cas['a'] and cas['id'] < min_id:
                    min_id = cas['id']; hole_diam = cas['id']
            if hole_diam is None: hole_diam = bit_size
            total += ((hole_diam ** 2) / 1029.4) * (length_m * 3.28084)
        return total

    # ---------- DİNAMİK HESAPLAMA FONKSİYONLARI ----------
    def _dynamic_annulus_for_pipe(self, p_ust, p_alt, od, casing_list, bit_size, td):
        ann_v = 0.0
        boundaries = set([p_ust, p_alt, td])
        for cas in casing_list:
            if cas['u'] < p_alt and cas['a'] > p_ust:
                boundaries.add(max(p_ust, cas['u'])); boundaries.add(min(p_alt, cas['a']))
        sorted_b = sorted(boundaries)
        for i in range(len(sorted_b)-1):
            seg_top, seg_bottom = sorted_b[i], sorted_b[i+1]
            if seg_top >= p_alt or seg_bottom <= p_ust: continue
            seg_top = max(seg_top, p_ust); seg_bottom = min(seg_bottom, p_alt)
            if seg_bottom <= seg_top: continue
            mid = (seg_top + seg_bottom)/2.0
            hole_diam = None; min_id = float('inf')
            for cas in casing_list:
                if cas['u'] <= mid <= cas['a'] and cas['id'] < min_id:
                    min_id = cas['id']; hole_diam = cas['id']
            if hole_diam is None: hole_diam = bit_size
            length_m = seg_bottom - seg_top
            ann_v += ((hole_diam**2 - od**2)/1029.4) * (length_m * 3.28084)
        return ann_v

    def sirkulasyon_hesapla(self):
        total_flow = 0.0
        try:
            for p in self.pompalar:
                if not p["aktif"].get(): continue
                l, s, v, spm = p["liner"].get(), p["stroke"].get(), p["verim"].get(), p["spm"].get()
                if not all([l,s,v,spm]): continue
                liner = self.parse_inch(l); stroke = self.parse_inch(s)
                verim = float(v)/100.0; spm = float(spm)
                total_flow += (0.0002428 * (liner**2) * stroke * verim) * spm
            if total_flow > 0:
                self.stb_min = self.t_ic / total_flow
                self.bu_min = self.t_ann / total_flow
                self.total_min = self.stb_min + self.bu_min
                self.sure_stb_label.config(text=f"Yüzeyden Matkaba: {self.stb_min:.1f} dk")
                self.sure_bu_label.config(text=f"Bottom-Up (Ucundan Yüzeye): {self.bu_min:.1f} dk")
                self.sure_tot_label.config(text=f"Tam Sirkülasyon: {self.total_min:.1f} dk")
            else:
                self.stb_min = self.bu_min = self.total_min = 0.0
                self.sure_stb_label.config(text="Yüzeyden Matkaba: - dk")
                self.sure_bu_label.config(text="Bottom-Up (Ucundan Yüzeye): - dk")
                self.sure_tot_label.config(text="Tam Sirkülasyon: - dk")
        except ValueError: pass
        self._mark_dynamic_changed()

    def tab2_casing_ekle(self):
        try:
            c = self.tab2_casing_combo.get()
            u = float(self.tab2_casing_ust.get())
            a = float(self.tab2_casing_alt.get())
            self.tab2_casing_listesi.append({
                "id": self.casing_verileri[c], "u": u, "a": a,
                "filt": self.tab2_cas_filtre_var.get(), "name": c
            })
            self.tab2_casing_listesi.sort(key=lambda x: x['u'])
            self.tab2_yeniden_ciz_casing()
            self.tab2_yeniden_hesapla()
            self._mark_dynamic_changed()
        except: messagebox.showerror("Hata", "Geçerli casing bilgilerini girin.")

    def tab2_yeniden_ciz_casing(self):
        for i in self.tab2_casing_tablo.get_children(): self.tab2_casing_tablo.delete(i)
        for index, c in enumerate(self.tab2_casing_listesi):
            stat = "Filtreli" if c["filt"] else "Çimentolu"
            od_val = self.parse_inch(c["name"].split('(')[0].strip())
            id_val = c["id"]
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tab2_casing_tablo.insert("", "end", values=(
                c["name"].split('(')[0], f"{od_val:.4g}", f"{id_val:.4g}", c["u"], c["a"], stat
            ), tags=(tag,))

    def tab2_casing_sil(self):
        sel = self.tab2_casing_tablo.selection()
        if sel:
            self.tab2_casing_listesi.pop(self.tab2_casing_tablo.index(sel[0]))
            self.tab2_yeniden_ciz_casing()
            self.tab2_yeniden_hesapla()
            self._mark_dynamic_changed()

    def tab2_dizi_ekle_universal(self, combo, entry, db):
        try:
            name = combo.get(); boy = float(entry.get())
            if name:
                self.tab2_dizi_listesi.append({"name": name, "boy": boy, "db": db})
                self.tab2_yeniden_hesapla()
                entry.delete(0, tk.END)
                self._mark_dynamic_changed()
        except: messagebox.showerror("Hata", "Geçerli bir isim ve uzunluk girin.")

    def tab2_dizi_sil(self):
        sel = self.tab2_dizi_tablo.selection()
        if sel:
            idx = self.tab2_dizi_tablo.index(sel[0])
            self.tab2_dizi_listesi.pop(len(self.tab2_dizi_listesi)-1 - idx)
            self.tab2_yeniden_hesapla()
            self._mark_dynamic_changed()

    def tab2_yeniden_hesapla(self):
        try:
            td_str = self.tab2_td_entry.get()
            if not td_str: return
            td = float(td_str)
            bit_size = self.matkap_verileri[self.tab2_matkap_combo.get()]
            for i in self.tab2_dizi_tablo.get_children(): self.tab2_dizi_tablo.delete(i)

            if not self.tab2_dizi_listesi:
                self.t_ic = 0.0
                self.t_ann = self._compute_wellbore_capacity(td, self.tab2_casing_listesi, bit_size)
                self.t_metal = 0.0
                self.tab2_sonuc_label.config(text=f"Dizi İçi: 0.00 bbl | Dinamik Kuyu Hacmi: {self.t_ann:.2f} bbl")
                self.dinamik_metal_label.config(text="Toplam Taşırma Hacmi: 0.00 bbl")
                self.yuzeye_kalan_label.config(text=f"Kalan Mesafe: {round(td, 1)} m")
                self.sirkulasyon_hesapla()
                return

            current_m, self.t_ic, self.t_ann, self.t_metal = 0.0, 0.0, 0.0, 0.0
            rows = []
            for pipe in self.tab2_dizi_listesi:
                od, id_in = pipe["db"][pipe["name"]]
                boy = pipe["boy"]
                p_alt = td - current_m
                p_ust = td - current_m - boy
                ic_v = ((id_in**2)/1029.4) * (boy * 3.28084)
                ann_v = self._dynamic_annulus_for_pipe(p_ust, p_alt, od, self.tab2_casing_listesi, bit_size, td)
                metal_v = self._metal_volume(od, id_in, boy)
                self.t_ic += ic_v; self.t_ann += ann_v; self.t_metal += metal_v
                rows.append((pipe["name"].split('(')[0], f"{od:.4g}", f"{id_in:.4g}",
                             f"{round(p_alt,1)}-{round(p_ust,1)}", f"{ic_v:.2f}", f"{metal_v:.2f}"))
                current_m += boy
            
            for idx, r in enumerate(reversed(rows)): 
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tab2_dizi_tablo.insert("", "end", values=r, tags=(tag,))
                
            self.tab2_sonuc_label.config(text=f"Dizi İçi: {self.t_ic:.2f} bbl | Dinamik Kuyu Hacmi: {self.t_ann:.2f} bbl")
            self.dinamik_metal_label.config(text=f"Toplam Taşırma Hacmi: {self.t_metal:.2f} bbl")
            self.yuzeye_kalan_label.config(text=f"Kalan Mesafe: {max(0, round(td - current_m, 1))} m")
            self.sirkulasyon_hesapla()
        except: pass

    # ---------- DİNAMİK KAYIT / YÜKLEME / SİLME ----------
    def dinamik_verileri_paketle(self):
        data = {
            "matkap": self.tab2_matkap_combo.get(), "td": self.tab2_td_entry.get(),
            "casing_listesi": self.tab2_casing_listesi, "dizi_listesi": self.tab2_dizi_listesi, "pompalar": []
        }
        for p in self.pompalar:
            data["pompalar"].append({
                "aktif": p["aktif"].get(), "liner": p["liner"].get(), "stroke": p["stroke"].get(),
                "verim": p["verim"].get(), "spm": p["spm"].get()
            })
        return data

    def dinamik_kaydet(self):
        if not self.aktif_dinamik_kuyu: self.dinamik_farkli_kaydet(); return
        yol = os.path.join(self.dinamik_klasoru, f"{self.aktif_dinamik_kuyu}.json")
        try:
            with open(yol, "w", encoding="utf-8") as f: json.dump(self.dinamik_verileri_paketle(), f, indent=4)
            self.dynamic_data_changed = False
            self.dinamik_btn_kaydet.config(state="disabled")
        except Exception as e: messagebox.showerror("Hata", f"Kaydedilemedi:\n{e}")

    def dinamik_farkli_kaydet(self):
        ad = simpledialog.askstring("Kuyu Kaydet", "Projeye/Kuyuya isim verin:")
        if not ad: return
        yol = os.path.join(self.dinamik_klasoru, f"{ad}.json")
        if os.path.exists(yol):
            if not messagebox.askyesno("Uyarı", "Bu isimde bir kayıt zaten var. Üzerine yazılsın mı?"): return
        self.aktif_dinamik_kuyu = ad
        self.dinamik_lbl_durum.config(text=f"Açık Dosya: {ad}", foreground="#38A169")
        self.dinamik_kaydet()

    def dinamik_yukle_dialog(self):
        top = tk.Toplevel(self.root)
        top.title("Kayıtlı Kuyular")
        top.geometry("400x500")
        top.configure(bg=self.bg_color)
        top.transient(self.root); top.grab_set()
        
        ttk.Label(top, text="Kayıtlı Projeler (Dinamik)", style="Title.TLabel", font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        list_frame = ttk.Frame(top, style="Card.TFrame", padding=10)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        liste = tk.Listbox(list_frame, font=("Segoe UI", 11), borderwidth=0, highlightthickness=0, selectbackground="#3182CE")
        liste.pack(fill="both", expand=True)
        
        def doldur():
            liste.delete(0, tk.END)
            for dosya in os.listdir(self.dinamik_klasoru):
                if dosya.endswith(".json"): liste.insert("end", dosya[:-5])
        doldur()
        
        btn_frame = ttk.Frame(top, style="TFrame")
        btn_frame.pack(pady=15)
        btn_yukle = ttk.Button(btn_frame, text="Yükle", state="disabled", style="Primary.TButton")
        btn_yukle.pack(side="left", padx=5)
        btn_sil = ttk.Button(btn_frame, text="Kalıcı Olarak Sil", state="disabled")
        btn_sil.pack(side="left", padx=5)
        
        def on_select(event):
            state = "normal" if liste.curselection() else "disabled"
            btn_yukle.config(state=state); btn_sil.config(state=state)
        liste.bind('<<ListboxSelect>>', on_select)
        
        def yukle():
            sec = liste.curselection()
            if sec:
                ad = liste.get(sec[0]); self._dinamik_yukle(ad); top.destroy()
        def sil():
            sec = liste.curselection()
            if sec:
                ad = liste.get(sec[0])
                if messagebox.askyesno("Silme Onayı", "Seçili kuyuya ait tüm veriler kalıcı olarak silinecek. Emin misiniz?"):
                    if self._delete_well_file(self.dinamik_klasoru, ad):
                        if self.aktif_dinamik_kuyu == ad:
                            self.aktif_dinamik_kuyu = None
                            self.dinamik_lbl_durum.config(text="Durum: Kaydedilmemiş", foreground="#2D3748")
                            self.dinamik_btn_kaydet.config(state="disabled")
                        doldur()
                        if not liste.get(0, tk.END):
                            btn_yukle.config(state="disabled"); btn_sil.config(state="disabled")
        btn_yukle.config(command=yukle); btn_sil.config(command=sil)

    def _dinamik_yukle(self, ad):
        yol = os.path.join(self.dinamik_klasoru, f"{ad}.json")
        try:
            with open(yol, "r", encoding="utf-8") as f: data = json.load(f)
        except Exception as e: messagebox.showerror("Hata", f"Okunamadı:\n{e}"); return
        self.aktif_dinamik_kuyu = ad
        self.dinamik_lbl_durum.config(text=f"Açık Dosya: {ad}", foreground="#38A169")
        self.tab2_matkap_combo.set(data.get("matkap",""))
        self.tab2_td_entry.delete(0, tk.END); self.tab2_td_entry.insert(0, data.get("td",""))
        self.tab2_casing_listesi = data.get("casing_listesi", [])
        self.tab2_yeniden_ciz_casing()
        self.tab2_dizi_listesi = data.get("dizi_listesi", [])
        pompalar_data = data.get("pompalar", [])
        for i, p_data in enumerate(pompalar_data):
            if i < len(self.pompalar):
                self.pompalar[i]["aktif"].set(p_data["aktif"])
                self.pompalar[i]["liner"].set(p_data["liner"])
                self.pompalar[i]["stroke"].set(p_data["stroke"])
                self.pompalar[i]["verim"].delete(0, tk.END); self.pompalar[i]["verim"].insert(0, p_data["verim"])
                self.pompalar[i]["spm"].delete(0, tk.END); self.pompalar[i]["spm"].insert(0, p_data["spm"])
        self.tab2_yeniden_hesapla()
        self.dynamic_data_changed = False
        self.dinamik_btn_kaydet.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    KapsamliSondajHesaplayici(root)
    root.mainloop()