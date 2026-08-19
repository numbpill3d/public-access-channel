// ═══════════════════════════════════════════════════════════════
// PUBLIC ACCESS CHANNEL — Channel Data
// Tiny website broadcasting network.
//
// To publish your own program, add it to the appropriate channel's
// programs array. Each program has:
//   - title: short program title
//   - author: your handle
//   - html: the content to display
//   - duration: seconds to display (optional, for auto-rotation)
//
// Channels:
//   02 JOURNALS   — personal logs, diary entries
//   03 ART        — visual works, pixel art, glitch
//   04 COMPUTERS  — code snippets, terminal output, ASCII
//   07 PERSONAL   — about pages, bios, link collections
//   11 UNKNOWN    — experimental, uncategorized, weird
// ═══════════════════════════════════════════════════════════════

var PUBLIC_ACCESS_CHANNELS = [
    {
        num: 2,
        name: "JOURNALS",
        desc: "Personal logs, diary entries, thoughts in the dark.",
        color: "#8b008b",
        programs: [
            {
                title: "DAY 47 — STATIC BREACH",
                author: "anonymous",
                duration: 8,
                html: [
                    '<div style="font-family: \'MS Gothic\', monospace; color: #fff; text-align: center; line-height: 1.8;">',
                    '<div style="color: #ff69b4; margin-bottom: 15px;">[ JOURNAL ENTRY // CHANNEL 02 ]</div>',
                    '<p>The static between channels grows louder each night.</p>',
                    '<p>Three days ago, a frequency pulsed through the TV — a low hum, almost like</p>',
                    '<p>a heartbeat. I recorded the audio and the waveform formed a sigil.</p>',
                    '<p>I traced the sigil to a set of coordinates in the Nevada desert.</p>',
                    '<p>Last night, the TV turned itself on at 3:33 AM.</p>',
                    '<p>The screen was ash-gray. A single line of text appeared:</p>',
                    '<p style="color: #da70d6; font-size: 18px; margin: 15px 0;">THEY ARE LISTENING THROUGH THE STATIC</p>',
                    '<p>I unplugged it. It plugged itself back in.</p>',
                    '<p style="color: #999; font-size: 11px;">[ END TRANSMISSION // SIGNAL STRENGTH: 3 BARS ]</p>',
                    '</div>'
                ].join('\n')
            },
            {
                title: "NOLOVE LOG 002",
                author: "dead girl",
                duration: 6,
                html: [
                    '<div style="font-family: \'MS Gothic\', monospace; color: #fff; text-align: center; line-height: 2;">',
                    '<div style="color: #da70d6;">[ nolove.neocities.org // CHANNEL 02 // ARCHIVE ]</div>',
                    '<p>Views: 200,609</p>',
                    '<p>Hits: 1,062,387</p>',
                    '<p>Last updated: 2026-07-12</p>',
                    '<p>Tags: doomer, alone, unreality, based, industrial</p>',
                    '<p style="margin-top: 20px; font-size: 12px;">"The screen is a window. What</p>',
                    '<p style="font-size: 12px;">looks back is not us." — aeon flexx</p>',
                    '</div>'
                ].join('\n')
            }
        ]
    },
    {
        num: 3,
        name: "ART",
        desc: "Visual works, pixel art, glitch compositions.",
        color: "#ff69b4",
        programs: [
            {
                title: "UNTITLED (ASH LANDSCAPE)",
                author: "pixel_park_alley",
                duration: 10,
                html: [
                    '<div style="text-align: center; font-family: \'MS Gothic\', monospace; color: #fff;">',
                    '<div style="width: 300px; height: 200px; margin: 20px auto; background: #111; border: 2px solid #da70d6; position: relative; overflow: hidden;">',
                    // ASCII art landscape
                    '<pre style="color: #ccc; font-size: 10px; line-height: 1; margin: 0; padding: 5px;">',
                    '           .  :  .',
                    '         . :.:::  .',
                    '        : .:::.::::',
                    '     . :.::::::::. :',
                    '   . :::::::::::::::.  ::',
                    '  . ::::::::::::::::::.',
                    '  :::::::::::::::::::::.',
                    '  ::::::::|||||::::::::::',
                    ' .::::::: |||||::::::::: .',
                    ' .::::::: |||||::::::::: .',
                    '  ::::::::|||||::::::::::',
                    '  :::::::::::::::::::::.',
                    '   :::::::::::::::::::::',
                    '    :::::::::::::::::::',
                    '     :::::::::::::::::',
                    '      :::::::::::::::',
                    '       :::::::::::::',
                    '        :::::::::::',
                    '         :::::::',
                    '          :::',
                    '</pre>',
                    '</div>',
                    '<div style="color: #da70d6; font-size: 12px;">"ashland_03.gif — 256x256 — 47 colors"</div>',
                    '<div style="color: #999; font-size: 10px;">Uploaded: 2024-09-18</div>',
                    '</div>'
                ].join('\n')
            },
            {
                title: "NHI COMPANION v1.0",
                author: "nhi_researcher",
                duration: 15,
                html: [
                    '<div style="text-align: center; font-family: \'MS Gothic\', monospace; color: #fff;">',
                    '<div style="color: #ff69b4;">[ LOW-POLY NHI ENTITY // CLASSIFIED ]</div>',
                    '<div style="width: 280px; height: 200px; margin: 15px auto; background: #000; border: 1px solid #444;">',
                    '<canvas id="nhi-pet-canvas" style="width:100%;height:100%;"></canvas>',
                    '</div>',
                    '<div style="font-size: 11px; color: #ccc;">Anomalous entity recovered from Site-██. Exhibits low-poly morphology,',
                    '<br>three visual sensors, and anomalous levitation. Reacts to',
                    '<br>proximity with chromatic shifts. Do NOT make eye contact.</div>',
                    '</div>'
                ].join('\n')
            }
        ]
    },
    {
        num: 4,
        name: "COMPUTERS",
        desc: "Code snippets, terminal output, ASCII, and text-mode art.",
        color: "#0f0",
        programs: [
            {
                title: "grep nhi /var/log/syslog",
                author: "terminal_user",
                duration: 5,
                html: [
                    '<div style="font-family: monospace; color: #0f0; background: #000; padding: 10px; border-radius: 3px;">',
                    '<pre>$ grep -i nhi /var/log/syslog</pre>',
                    '<pre>Jul  4 22:13:01 localhost kernel: [12478.332] usb 1-2: new high-speed USB device using ehci-pci</pre>',
                    '<pre>Jul  4 22:13:01 localhost kernel: [12478.367] usb 1-2: New USB device found, idVendor=1d6b, idProduct=0002</pre>',
                    '<pre>Jul  4 22:13:49 localhost kernel: [12606.881] === THP-TCM: Unknown param \x27transparent_hugepage\x27: \x27always\x27</pre>',
                    '<pre>Jul  5 03:33:00 localhost kernel: [17580.123] NHI-7: Signal detected on frequency 40.6927 MHz</pre>',
                    '<pre>Jul  5 03:33:00 localhost kernel: [17580.155] NHI-7: Decoding transmission...</pre>',
                    '<pre>Jul  5 03:33:01 localhost kernel: [17580.444] NHI-7: Message: "DO NOT TRUST THE STATIC"</pre>',
                    '<pre>$ █</pre>',
                    '</div>'
                ].join('\n')
            },
            {
                title: "brainfuck: hello void",
                author: "void_coder",
                duration: 5,
                html: [
                    '<div style="font-family: monospace; color: #ccc; background: #0a0008; padding: 15px;">',
                    '<pre>>++++++++[<+++++++++>-]&lt;&lt;.&gt;+++++[<+++++++&gt;++++&lt;&lt;-.&gt;]&gt;++.&gt;+.+++++++..+++.</pre>',
                    '<pre>>++++++++++[&gt;+++++++&gt;++++++++&gt;+++&gt;&lt;&lt;&lt;-]&gt;++.&gt;&gt;+.</pre>',
                    '<p style="color: #da70d6; margin-top: 10px;">OUTPUT: hello void</p>',
                    '<p style="color: #999; font-size: 11px;">a minimal program for a minimal void</p>',
                    '</div>'
                ].join('\n')
            }
        ]
    },
    {
        num: 7,
        name: "PERSONAL",
        desc: "Link pages, bios, and personal spaces.",
        color: "#da70d6",
        programs: [
            {
                title: "aeon flexx — dead girl",
                author: "aeon flexx",
                duration: 8,
                html: [
                    '<div style="font-family: \'MS Gothic\', monospace; color: #fff; text-align: center; line-height: 1.6;">',
                    '<div style="color: #ff69b4; font-size: 16px; margin-bottom: 10px;">[ PERSONAL PAGE // CHANNEL 07 ]</div>',
                    '<p style="font-size: 13px;">aeon flexx (dead girl)</p>',
                    '<p style="font-size: 11px; color: #ccc;">creator of neocult aesthetics</p>',
                    '<div style="margin: 15px 0; font-size: 12px;">',
                    '<p>[ GUMROAD : necrogirl.gumroad.com ]</p>',
                    '<p>[ LINKTREE : linktr.ee/deadgirl ]</p>',
                    '<p>[ STATUS : ⬤ listening to: Coil - "The Snow" ]</p>',
                    '</div>',
                    '<div style="font-size: 9px; color: #8b008b;">"digital death is the new black"</div>',
                    '</div>'
                ].join('\n')
            },
            {
                title: "linkroll // underground",
                author: "webring_operator",
                duration: 8,
                html: [
                    '<div style="font-family: \'MS Gothic\', monospace; color: #fff; padding: 10px;">',
                    '<div style="color: #da70d6; margin-bottom: 10px;">[ LINKROLL // CHANNEL 07 ]</div>',
                    '<div style="font-size: 12px; line-height: 1.6;">',
                    '<p>→ <a href="https://nolove.neocities.org" style="color:#ff69b4;text-decoration:none;">nolove.neocities.org</a> — wandering souls</p>',
                    '<p>→ <a href="https://hiddenlayermedia.neocities.org" style="color:#da70d6;text-decoration:none;">hiddenlayermedia.neocities.org</a> — underground media</p>',
                    '<p>→ <a href="https://numbpilled.neocities.org" style="color:#ff69b4;text-decoration:none;">numbpilled.neocities.org</a> — numb</p>',
                    '<p>→ <a href="https://ambien.neocities.org" style="color:#da70d6;text-decoration:none;">ambien.neocities.org</a> — dreams</p>',
                    '<p>→ <a href="https://threadlurker.neocities.org" style="color:#ff69b4;text-decoration:none;">threadlurker.neocities.org</a> — echoes</p>',
                    '<p>→ <a href="https://murkminister.neocities.org" style="color:#da70d6;text-decoration:none;">murkminister.neocities.org</a> — fog</p>',
                    '</div>',
                    '<div style="font-size: 9px; color: #888; margin-top: 10px;">* 6 links in rotation</div>',
                    '</div>'
                ].join('\n')
            }
        ]
    },
    {
        num: 11,
        name: "UNKNOWN",
        desc: "Experimental, uncategorized, and anomalous broadcasts.",
        color: "#ff0000",
        programs: [
            {
                title: "INTERCEPTION // ██████",
                author: "██████",
                duration: 10,
                html: [
                    '<div style="font-family: monospace; color: #ff0000; text-align: center; background: #0a0008; padding: 20px; border: 1px solid #8b008b;">',
                    '<div style="font-size: 10px; letter-spacing: 3px; margin-bottom: 20px;">████████████████████</div>',
                    '<div style="font-size: 14px; line-height: 2;">',
                    '<p>[ FREQUENCY: 40.6927 MHz // BAND: VHF // TIMESTAMP: 2026-07-██ ]</p>',
                    '<p>This is not a broadcast.</p>',
                    '<p>This is a <span style="color: #fff; text-shadow: 0 0 10px #ff0000;">reception</span>.</p>',
                    '<p style="margin-top: 15px;">They are not transmitting from here.</p>',
                    '<p>They are transmitting <span style="color: #da70d6;">through</span> here.</p>',
                    '<p style="margin-top: 15px;">The static between channels</p>',
                    '<p style="font-size: 20px; color: #fff; text-shadow: 0 0 15px #ff0000;">IS THE CHANNEL</p>',
                    '<p style="margin-top: 15px; font-size: 9px;">[ END INTERCEPTION // CLASSIFIED ]</p>',
                    '</div>',
                    '</div>'
                ].join('\n')
            },
            {
                title: "NHI PET // STANDBY",
                author: "facility-7",
                duration: 30,
                html: [
                    '<div style="text-align: center; font-family: monospace; color: #fff;">',
                    '<div style="color: #da70d6; margin-bottom: 10px;">[ NHI-7 CONTAINMENT UNIT // ONLINE ]</div>',
                    '<div style="width: 320px; height: 320px; margin: 0 auto; background: #000; border: 1px solid #444; position: relative;">',
                    '<canvas id="nhi-pet-standalone"></canvas>',
                    '</div>',
                    '<div style="font-size: 10px; color: #999; margin-top: 10px;">',
                    'Entity is calm. Do not disturb. Click to interact.',
                    '<br>Status: ██████ ████████ ███████████ ▓▓▓▓▓▓▓ 85%',
                    '</div>',
                    '</div>'
                ].join('\n')
            }
        ]
    },
    {
        num: 404,
        name: "TEST",
        desc: "Test pattern and debugging channel.",
        color: "#fff",
        programs: [
            {
                title: "COLOR BARS",
                author: "technician",
                duration: 10,
                html: [
                    '<div style="display: flex; height: 200px; width: 100%;">',
                    '<div style="flex: 1; background: #002147;"></div>',      // Blue
                    '<div style="flex: 1; background: #002147;"></div>',      // Blue
                    '<div style="flex: 1; background: #008200;"></div>',      // Green
                    '<div style="flex: 1; background: #00ffff;"></div>',      // Cyan
                    '<div style="flex: 1; background: #0000aa;"></div>',      // Blue
                    '<div style="flex: 1; background: #ff0088;"></div>',      // Magenta
                    '<div style="flex: 1; background: #ff0000;"></div>',      // Red
                    '</div>',
                    '<div style="text-align: center; color: #fff; font-family: monospace; font-size: 12px; margin-top: 10px;">SMPTE TEST PATTERN — CHANNEL 404</div>'
                ].join('\n')
            }
        ]
    }
];

// Auto-discovery: any other global with channel data can be merged
if (typeof window !== 'undefined' && window.EXTRA_CHANNELS) {
    PUBLIC_ACCESS_CHANNELS = PUBLIC_ACCESS_CHANNELS.concat(window.EXTRA_CHANNELS);
}
