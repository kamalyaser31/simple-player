# Simple Audio Player

Funkcemi nadupaný, přístupný desktopový audio a multimediální přehrávač pro Windows vytvořený v Pythonu a wxPythonu. Je navržen s důrazem na přístupnost z klávesnice a podporu odečítačů obrazovky.

**Verze:** 1.0.1
**Autor:** Kamal Yaser
**Repozitář:** [GitHub](https://github.com/kamalyaser31/simple-player)

---

## Funkce

* **Široká podpora formátů:** Přehrává všechny běžné zvukové a video soubory.
* **Integrace s YouTube:** Vyhledávání, přehrávání a stahování videí a playlistů z YouTube.
* **Pokročilé zpracování zvuku:** Zahrnuje odstraňování ticha, normalizaci zvuku a převod do mono.
* **Plná přístupnost z klávesnice:** Vše lze ovládat pomocí klávesnice.
* **Podpora odečítačů obrazovky:** Funguje s JAWSem, NVDA a dalšími odečítači obrazovky.
* **Možnosti přizpůsobení:** Lze měnit klávesové zkratky, jazyk (angličtina/arabština) a další nastavení.

---

## Systémové požadavky

* **Operační systém:** Windows 7 SP1 nebo novější (doporučena Windows 10+)
* **RAM:** Minimálně 256 MB
* **Místo na disku:** 200 MB pro instalaci
* **Zvukové zařízení:** Funkční zařízení pro zvukový výstup

---

## Podporované formáty

* **Audio:** AAC, AIFF, ALAC, FLAC, M4A, MP3, OGG, OPUS, WAV, WMA
* **Video:** 3GP, AVI, FLV, M2TS, M4V, MKV, MOV, MPEG, MP4, MPG, TS, WebM, WMV

---

## Instalace

### Instalační program pro Windows (doporučeno)

1. Stáhněte si nejnovější soubor `SimpleAudioPlayerSetup.exe` ze stránky [Releases](https://github.com/kamalyaser31/simple-player/releases).
2. Spusťte instalační program a postupujte podle pokynů na obrazovce.

### Přenosná verze

1. Stáhněte si přenosný ZIP soubor ze stránky [Releases](https://github.com/kamalyaser31/simple-player/releases).
2. Rozbalte ZIP soubor do libovolné složky.
3. Spusťte `SimpleAudioPlayer.exe`.

---

## Použití

Podrobné pokyny najdete v [úplné uživatelské příručce](player/docs/en/userguide.html).

### Základní přehrávání

* **Otevření souboru:** Přejděte na `Soubor > Otevřít soubor` nebo stiskněte `Ctrl+O`.
* **Přehrát/Pozastavit:** Stiskněte `Mezerník`.
* **Navigace:** K posunu použijte šipky `Vpravo` a `Vlevo`.
* **Hlasitost:** K úpravě hlasitosti použijte šipky `Nahoru` a `Dolů`.

---

## Vývoj

Pokud chcete do projektu přispět, můžete jej sestavit ze zdrojového kódu.

### Struktura projektu

```
simple-player/
├── player/                    # Hlavní adresář aplikace
│   ├── app.py                # Vstupní bod aplikace
│   ├── SimpleAudioPlayer.py   # Vstupní bod GUI
│   ├── requirements.txt       # Závislosti Pythonu
│   ├── SimpleAudioPlayer.spec # Konfigurace PyInstalleru
│   ├── simple_audio_player.iss # Konfigurace Inno Setup
│   │
│   ├── core/                 # Základní funkce
│   │   ├── controller.py     # Hlavní řadič aplikace
│   │   ├── mpv_engine.py     # Jádro přehrávání médií
│   │   ├── keyboard_handler.py # Globální vstup z klávesnice
│   │   ├── media_library.py  # Procházení/indexace souborů
│   │   └── player/           # Implementace přehrávače
│   │
│   ├── config/               # Správa konfigurace
│   │   ├── constants.py      # Konstanty aplikace
│   │   ├── settings_manager.py # Ukládání nastavení
│   │   ├── shortcuts.py      # Klávesové zkratky
│   │   ├── localization.py   # Podpora i18n
│   │   └── file_associations.py # Registrace souborů ve Windows
│   │
│   ├── ui/                   # Uživatelské rozhraní
│   │   ├── main_frame.py     # Hlavní okno
│   │   ├── mainwin/          # Komponenty hlavního okna
│   │   ├── dialogs.py        # Dialogová okna UI
│   │   ├── settings_dialog.py # Okno nastavení
│   │   └── prefs/            # Panely nastavení
│   │
│   ├── app_actions/          # Akce aplikace
│   │   ├── playback_actions.py # Ovládání přehrávání
│   │   ├── file_actions.py   # Operace se soubory
│   │   ├── device_actions.py # Správa zvukových zařízení
│   │   └── help_actions.py   # Nápověda/dokumentace
│   │
│   ├── youtube/              # Integrace s YouTube
│   │   ├── search.py         # Funkce vyhledávání
│   │   ├── download.py       # Funkce stahování
│   │   ├── flow.py           # Workflow pro YouTube
│   │   └── components.py     # Správa komponent
│   │
│   ├── playlist/             # Správa playlistů
│   │   ├── state.py          # Stav playlistu
│   │   └── state/            # Moduly stavu playlistu
│   │
│   ├── helpers/              # Pomocné funkce
│   │   ├── utils.py          # Běžné pomocné funkce
│   │   ├── file_helpers.py   # Operace se soubory
│   │   └── clipboard_utils.py # Práce se schránkou
│   │
│   ├── locale/               # Lokalizační soubory
│   │   └── ar/, en/          # Jazykové adresáře
│   │
│   ├── docs/                 # Dokumentace
│   │   └── en/, ar/          # Adresáře s dokumentací v jednotlivých jazycích
│   │
│   └── sounds/               # Zvukové soubory
│       └── speaker_test.wav  # Testovací zvukový soubor
```

### Závislosti

| Balíček              | Účel                               |
| -------------------- | ---------------------------------- |
| `wxPython`           | Framework pro GUI                  |
| `python-libmpv`      | Přehrávání médií                   |
| `pynput`             | Globální zpracování klávesnice     |
| `appGuard`           | Zajištění jediné spuštěné instance |
| `accessible_output3` | Integrace s odečítači obrazovky    |
| `py-yt-search`       | Vyhledávání na YouTube             |
| `winsdk`             | Integrace s Windows SDK            |

### Sestavení ze zdrojového kódu

#### Předpoklady

* Python 3.7 nebo vyšší
* Git

#### Kroky

1. **Naklonování repozitáře**

   ```powershell
   git clone https://github.com/kamalyaser31/simple-player.git
   cd simple-player/player
   ```

2. **Instalace závislostí**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Spuštění aplikace**

   ```powershell
   python SimpleAudioPlayer.py
   ```

---

## Licence

Tento projekt je licencován pod licencí MIT. Podrobnosti najdete v souboru `LICENSE`.

---

## Podpora

Pokud potřebujete pomoc, máte nápady nebo chcete nahlásit chybu, použijte některý z následujících kanálů:

* **Hlášení problémů:** [GitHub Issues](https://github.com/kamalyaser31/simple-player/issues)
* **Podpora e-mailem:** [kamalyaser31@gmail.com](mailto:kamalyaser31@gmail.com)
* **Telegram:** [@kamalyaser31](https://t.me/kamalyaser31)

---

## Často kladené otázky

**Otázka: Je Simple Audio Player zdarma?**
Odpověď: Ano, je zdarma a má otevřený zdrojový kód.

**Otázka: Mohu jej používat na Macu nebo Linuxu?**
Odpověď: V současnosti je určen pouze pro Windows.

**Otázka: Mohu si přizpůsobit klávesové zkratky?**
Odpověď: Ano, všechny zkratky si můžete přizpůsobit v `Nastavení > Klávesové zkratky`.
