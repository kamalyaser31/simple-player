# Simple Audio Player

Simple Audio Player je desktopový multimediální pøehrávaè pro Windows vytvoøený v Pythonu a wxPythonu.
Projekt se zamìøuje na praktické každodenní pøehrávání, silnou podporu ovládání z klávesnice a dobrou kompatibilitu s odeèítaèi obrazovky.

Je navržen pro uživatele, kteøí chtìjí pøímoèarý pøehrávaè, ale zároveò ocení pokroèilé nástroje, když jsou potøeba: navigaci v souborech a playlistech, práci s YouTube, záložky a oblíbené položky, nahrávání a nastavitelné chování zvuku.

## Funkce

Simple Audio Player podporuje bìžné zvukové a video formáty a zahrnuje:

* Ovládání zamìøené pøedevším na klávesnici s pøizpùsobitelnými zkratkami
* Pøístupné uživatelské rozhraní a chování vstøícné k odeèítaèùm obrazovky
* Pøehrávání souborù a složek a navigaci v playlistech
* Záložky a oblíbené odkazy (video, playlist, kombinované odkazy na YouTube a obecné streamy)
* Vyhledávání na YouTube, pøehrávání a stahování (jakmile jsou k dispozici potøebné komponenty)
* Nahrávání s nastavitelným formátem, bitrate a výstupní složkou
* Ovládání zvuku, jako je normalizace, pøevod do mono, øízení rychlosti a odstraòování ticha
* Podporu zálohování a obnovení nastavení a dat záložek

Aplikace je zamìøena na Windows a integruje se se systémovým chováním, jako jsou akce asociací souborù a ovládání mediálních relací.

## Stažení

Pøedpøipravené verze jsou k dispozici na stránce vydání projektu:

[https://github.com/kamalyaser31/simple-player/releases](https://github.com/kamalyaser31/simple-player/releases)

Mùžete si vybrat buï:

* instalaèní build (`SimpleAudioPlayerSetup.exe`) pro bìžnou instalaci
* pøenosný ZIP build, pokud jej chcete spouštìt bez instalace

Pokud chcete aplikaci jen používat, nejjednodušší cesta je stáhnout ji ze sekce Releases.

## Sestavení ze zdrojového kódu

### Požadavky

Pro lokální vývoj a sestavení:

* Windows
* doporuèen Python 3.11 nebo novìjší
* Git
* podle vašeho prostøedí mùže být pro nìkteré balíèky Pythonu potøeba funkèní C/C++ build prostøedí

### Klonování a spuštìní

```powershell
git clone https://github.com/kamalyaser31/simple-player.git
cd simple-player\player
```

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py SimpleAudioPlayer.py
```

### Sestavení spustitelného souboru

```powershell
py -m PyInstaller SimpleAudioPlayer.spec
```

Vygenerovaný spustitelný soubor je umístìn do standardního výstupního adresáøe PyInstalleru (`dist`).

### Sestavení instalátoru

Repozitáø obsahuje skript pro Inno Setup:

`player/simple_audio_player.iss`

Když potøebujete vytvoøit instalaèní balíèek, zkompilujte tento skript v Inno Setup.

## Poznámky k projektu

Podpora YouTube závisí na komponentách dostupných za bìhu aplikace (napøíklad `yt-dlp`), které si aplikace umí spravovat pomocí vlastního postupu pro stažení a aktualizaci.
Pro pøehrávání lokálních souborù a bìžné funkce pøehrávaèe není žádné zvláštní nastavení YouTube potøeba.

Nastavení aplikace se ukládá do konfiguraèní cesty v uživatelském profilu. Data specifická pro jednotlivé funkce (napøíklad záložky, oblíbené položky a údaje o pozici pøehrávání) jsou uložena v samostatných souborech JSON ve stejném adresáøi s nastavením.

## Pøispívání

Pøíspìvky jsou vítány.

Pokud chcete pøispìt, otevøete prosím nejprve issue pro chyby nebo návrhy funkcí, zejména pokud jde o zmìny chování. Pomùže to udržet jasný smìr implementace ještì pøed code review.

U pull requestù upøednostòujte zamìøené zmìny s jasnì vymezeným rozsahem. Uveïte:

* co se zmìnilo
* proè se to zmìnilo
* jak jste to testovali (ruèní kroky a/nebo automatizované kontroly)

Vyhnìte se prosím nesouvisejícím refaktoringùm v rámci téhož pull requestu, pokud nejsou pro danou funkci nezbytné.

## Kontakt

Máte-li jakékoli dotazy nebo nápady, mùžete nás kontaktovat tìmito zpùsoby:

* E-mail: `kamalyaser31@gmail.com`
* Telegram: [https://t.me/kamalyaser31](https://t.me/kamalyaser31)

Pro hlášení chyb a návrhy funkcí pøejdìte na:

[https://github.com/kamalyaser31/simple-player/issues](https://github.com/kamalyaser31/simple-player/issues)

## Licence

Tento projekt je licencován pod licencí **GNU General Public License, verze 2, nebo (podle vaší volby) jakékoli pozdìjší verze** (GPL-2.0-or-later).

Úplné znìní licence najdete v souboru [LICENSE](LICENSE).