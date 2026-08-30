export const translations = {
  hu: {
    // Top Bar & Global
    appTitle: 'Arduino Vezérlőpanel',
    appSubtitle: 'Kétlépéses hardver ellenőrző és firmware égető rendszer',
    langSelector: 'Nyelv',

    // Auth - Login
    loginTitle: 'Bejelentkezés',
    usernamePlaceholder: 'Felhasználónév',
    passwordPlaceholder: 'Jelszó',
    loginBtn: 'Belépés',
    noAccountLink: 'Nincs még fiókod? Regisztráció',
    loginSuccess: 'Sikeres belépés!',
    loginFailed: 'Belépés sikertelen! Hibás felhasználónév vagy jelszó.',

    // Auth - Register
    registerTitle: 'Regisztráció',
    registerBtn: 'Regisztráció',
    hasAccountLink: 'Van már fiókod? Bejelentkezés',
    registerSuccess: 'Sikeres regisztráció!',
    registerError: 'Hiba történt a regisztráció során',

    // Dashboard Header & Stepper
    dashTitle: 'Mikrokontroller Vezérlő & Diagnosztika',
    dashSubtitle: 'Kétlépéses hardver ellenőrző és firmware égető rendszer',
    portConnected: 'Port Csatlakoztatva',
    portDisconnected: 'Nincs Kapcsolat',
    btnConnect: 'Csatlakozás (COM Port)',
    btnDisconnect: 'Leválasztás',
    step1: '1. Hardver Kapcsolat',
    step2: '2. Hardver Diagnosztika',
    step3: '3. Target Firmware Flash',

    // Stage 1: Diagnostic HUD
    stage1Title: '⚡ 1. Fázis: Hardver Diagnosztikai HUD',
    badgeIdle: 'Készenlétben',
    badgeRunning: 'Diagnosztika fut...',
    badgeSuccess: 'MINDEN TESZT SIKERES',
    badgeDanger: 'HIBA DETEKTÁLVA',
    btnStartDiag: '🔍 Diagnosztika Indítása',
    btnSimFault: '🧪 Hiba-szimuláció',
    btnSimFaultTitle: 'Szimulál egy sérült pint / alacsony feszültséget a biztonsági reteszelés teszteléséhez',

    // Telemetry Gauges
    ramLabel: 'Szabad RAM (SRAM)',
    vccLabel: 'Tápfeszültség (Vcc)',
    vccSub: '1.1V Bandgap mérés',
    i2cLabel: 'I2C Busz (SDA/SCL)',
    i2cNoDevices: '0 eszköz találva',
    i2cNotScanned: 'Nincs szkennelve',
    i2cDevicesFound: 'Eszközök:',
    clockLabel: 'Rendszer Órajel',
    clockSubOk: 'Stabil (16 MHz)',
    clockSubCalib: 'Timer kalibráció',

    // Pin Matrix
    pinMatrixTitle: 'I/O Pin Épség és Diagnosztikai Mátrix',
    digitalPinsGroup: 'Digitális (D2-D13):',
    analogPinsGroup: 'Analóg (A0-A5):',
    pinStateIdle: 'Inaktív',
    pinStateTesting: 'Teszt...',

    // Diagnostic Banners
    diagPassTitle: 'Hardver ellenőrzés sikeres!',
    diagPassDesc: (checks) => `A mikrokontroller minden belső és külső teszten megfelelt (${checks} sikeres ellenőrzés). A vezérlő készen áll a firmware égetésére.`,
    diagFailTitle: 'Hardverhiba észlelve!',
    diagFailDesc: (failed) => `A diagnosztika hibát detektált (${failed} hiba). A szoftveres reteszelés megakadályozza a sérült áramkörre történő égetést.`,

    // Stage 2: Target Flash & Presets
    stage2Title: '🚀 2. Fázis: Target Firmware Égetés & Vezérlés',
    badgeFlashing: 'Égetés folyamatban...',
    badgeFirmwareRunning: 'Firmware Fut',
    selectedPresetLabel: 'Kiválasztott Preset / Firmware fájl:',
    changeFileBtn: '✕ Fájl csere',
    dropzoneText: 'Kattints ide saját .hex vagy .bin fájl feltöltéséhez',
    presetNameLabel: 'Preset Elnevezése (Mentéshez):',
    presetNamePlaceholder: 'pl. Időjárás Állomás v1.2',
    presetDescLabel: 'Leírás / Célkártya (Opcionális):',
    presetDescPlaceholder: 'pl. Arduino Uno Rev3, I2C Szenzorok',
    btnTwoStageFlash: '⚡ 2-Lépéses Diagnosztika & Flash',
    btnDirectFlash: 'Égetés (Közvetlen)',
    btnSavePreset: '💾 Preset Mentése',
    btnSaving: 'Mentés...',

    // Flashing Messages
    msgSelectHexError: 'Hiba: Válassz vagy tölts be egy .hex firmware fájlt!',
    msgPortError: 'Hiba: Nincs nyitott COM port kapcsolat.',
    msgDiagHaltError: 'Biztonsági leállás: A diagnosztika hibát jelzett, az égetés megszakadt.',
    msgFlashSuccess: 'Sikeres égetés! A target firmware fut a mikrokontrolleren.',
    msgFlashError: 'Hiba történt az égetés során: ',
    msgPresetLoaded: (name) => `Preset betöltve: "${name}"`,
    msgPresetSaved: 'Sikeres mentés! A preset hozzáadva a listához.',
    msgPresetSaveError: 'Hiba történt a preset mentésekor.',
    msgNameRequired: 'Hiba: Adj meg egy nevet a presetnek!',
    msgFileRequired: 'Hiba: Válassz egy .hex fájlt a feltöltéshez!',

    // Serial Monitor
    monitorTitle: 'Valós Idejű Soros Monitor (115200 Baud)',
    btnClearLog: '🗑️ Törlés',
    autoscroll: 'Auto-görgetés',
    consolePlaceholder: 'Csatlakozz a COM porthoz az adatfolyam megtekintéséhez...',
    cmdPlaceholder: 'Parancs küldése (pl. CMD:PING vagy CMD:DIAG_START)...',
    btnSendCmd: 'Küldés',

    // Sidebar & Presets
    userPanelTitle: 'Vezérlőpult',
    userLoggedIn: 'Bejelentkezve',
    btnLogout: 'Kijelentkezés',
    savedPresetsTitle: 'Mentett Presetek',
    presetCountBadge: (count) => `${count} db`,
    hexAttachedTag: '.HEX fájl csatolva',
    btnLoadPreset: 'Betöltés',
    btnLoadedPreset: 'Betöltve ✓',
    emptyPresetsTitle: 'Még nincsenek mentett presetjeid.',
    emptyPresetsSub: 'Tölts fel egy .hex fájlt és mentsd el a bal oldali űrlapon!',

    // Guide Card
    guideTitle: '💡 Kétlépéses Rendszer Működése',
    guidePoint1: '1. Diagnosztika: A tesztelő rutin automatikusan ellenőrzi a szabad memóriát, tápfeszültséget és I/O pineket.',
    guidePoint2: '2. Flash: Ha minden teszt sikeres, a tiszta felhasználói firmware kerül égetésre nulla módosítással.',
    guidePoint3: 'Hardver védelem: Hibás pin vagy túlfeszültség esetén a rendszer leállítja az égetést.'
  },

  en: {
    // Top Bar & Global
    appTitle: 'Arduino Control Panel',
    appSubtitle: 'Two-stage hardware verification and firmware flashing system',
    langSelector: 'Language',

    // Auth - Login
    loginTitle: 'Sign In',
    usernamePlaceholder: 'Username',
    passwordPlaceholder: 'Password',
    loginBtn: 'Sign In',
    noAccountLink: "Don't have an account yet? Register",
    loginSuccess: 'Sign in successful!',
    loginFailed: 'Sign in failed! Invalid username or password.',

    // Auth - Register
    registerTitle: 'Create Account',
    registerBtn: 'Register',
    hasAccountLink: 'Already have an account? Sign In',
    registerSuccess: 'Registration successful!',
    registerError: 'An error occurred during registration',

    // Dashboard Header & Stepper
    dashTitle: 'Microcontroller Controller & Diagnostics',
    dashSubtitle: 'Two-stage hardware verification and firmware flashing system',
    portConnected: 'Port Connected',
    portDisconnected: 'No Connection',
    btnConnect: 'Connect (COM Port)',
    btnDisconnect: 'Disconnect',
    step1: '1. Hardware Connection',
    step2: '2. Hardware Diagnostics',
    step3: '3. Target Firmware Flash',

    // Stage 1: Diagnostic HUD
    stage1Title: '⚡ Stage 1: Hardware Diagnostic HUD',
    badgeIdle: 'Idle',
    badgeRunning: 'Running diagnostics...',
    badgeSuccess: 'ALL CHECKS PASSED',
    badgeDanger: 'FAULT DETECTED',
    btnStartDiag: '🔍 Run Diagnostics',
    btnSimFault: '🧪 Fault Injection',
    btnSimFaultTitle: 'Simulates a faulty pin / undervoltage condition to test safety interlock',

    // Telemetry Gauges
    ramLabel: 'Free RAM (SRAM)',
    vccLabel: 'Supply Voltage (Vcc)',
    vccSub: '1.1V Bandgap measurement',
    i2cLabel: 'I2C Bus (SDA/SCL)',
    i2cNoDevices: '0 devices found',
    i2cNotScanned: 'Not scanned',
    i2cDevicesFound: 'Devices:',
    clockLabel: 'System Clock',
    clockSubOk: 'Stable (16 MHz)',
    clockSubCalib: 'Timer calibration',

    // Pin Matrix
    pinMatrixTitle: 'I/O Pin Integrity & Diagnostic Matrix',
    digitalPinsGroup: 'Digital (D2-D13):',
    analogPinsGroup: 'Analog (A0-A5):',
    pinStateIdle: 'Inactive',
    pinStateTesting: 'Testing...',

    // Diagnostic Banners
    diagPassTitle: 'Hardware Verification Passed!',
    diagPassDesc: (checks) => `The microcontroller passed all internal and external self-tests (${checks} successful checks). The controller is ready for firmware flashing.`,
    diagFailTitle: 'Hardware Fault Detected!',
    diagFailDesc: (failed) => `Diagnostics detected critical errors (${failed} faults). The safety interlock has halted flashing to protect circuitry.`,

    // Stage 2: Target Flash & Presets
    stage2Title: '🚀 Stage 2: Target Firmware Flashing & Control',
    badgeFlashing: 'Flashing in progress...',
    badgeFirmwareRunning: 'Firmware Running',
    selectedPresetLabel: 'Selected Preset / Firmware File:',
    changeFileBtn: '✕ Replace File',
    dropzoneText: 'Click here to upload your .hex or .bin file',
    presetNameLabel: 'Preset Name (For Saving):',
    presetNamePlaceholder: 'e.g. Weather Station v1.2',
    presetDescLabel: 'Description / Target Board (Optional):',
    presetDescPlaceholder: 'e.g. Arduino Uno Rev3, I2C Sensors',
    btnTwoStageFlash: '⚡ 2-Stage Verification & Flash',
    btnDirectFlash: 'Flash (Direct)',
    btnSavePreset: '💾 Save Preset',
    btnSaving: 'Saving...',

    // Flashing Messages
    msgSelectHexError: 'Error: Please select or load a .hex firmware file!',
    msgPortError: 'Error: No active COM port connection.',
    msgDiagHaltError: 'Safety Halt: Diagnostics reported faults, flashing aborted.',
    msgFlashSuccess: 'Flashing successful! Target firmware is active on the microcontroller.',
    msgFlashError: 'An error occurred during flashing: ',
    msgPresetLoaded: (name) => `Preset loaded: "${name}"`,
    msgPresetSaved: 'Saved successfully! Preset added to your library.',
    msgPresetSaveError: 'An error occurred while saving the preset.',
    msgNameRequired: 'Error: Please provide a name for the preset!',
    msgFileRequired: 'Error: Please select a .hex file to upload!',

    // Serial Monitor
    monitorTitle: 'Real-Time Serial Monitor (115200 Baud)',
    btnClearLog: '🗑️ Clear',
    autoscroll: 'Auto-scroll',
    consolePlaceholder: 'Connect to a COM port to inspect the serial data stream...',
    cmdPlaceholder: 'Send command (e.g. CMD:PING or CMD:DIAG_START)...',
    btnSendCmd: 'Send',

    // Sidebar & Presets
    userPanelTitle: 'Dashboard',
    userLoggedIn: 'Signed In',
    btnLogout: 'Sign Out',
    savedPresetsTitle: 'Saved Presets',
    presetCountBadge: (count) => `${count} items`,
    hexAttachedTag: '.HEX file attached',
    btnLoadPreset: 'Load',
    btnLoadedPreset: 'Loaded ✓',
    emptyPresetsTitle: 'No saved presets yet.',
    emptyPresetsSub: 'Upload a .hex file and save it using the form on the left!',

    // Guide Card
    guideTitle: '💡 How the Two-Stage System Works',
    guidePoint1: '1. Diagnostics: The test harness automatically checks free SRAM, supply voltage, and I/O pins.',
    guidePoint2: '2. Flash: Once all self-tests pass, pure user target firmware is flashed with zero modifications.',
    guidePoint3: 'Hardware Protection: If a shorted pin or abnormal voltage is detected, flashing is automatically blocked.'
  }
};
