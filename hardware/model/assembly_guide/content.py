"""One source for the printable PDF and the workspace assembly instructions."""
PAGES=[]
def page(title,subtitle):
    p={'title':title,'subtitle':subtitle,'blocks':[]};PAGES.append(p);return p['blocks']
def p(b,text):b.append(('p',text))
def h(b,text):b.append(('h',text))
def steps(b,items):b.append(('steps',items))
def table(b,heads,rows,widths):b.append(('table',heads,rows,widths))
def image(b,path,height,caption):b.append(('image',path,height,caption))
def note(b,text):b.append(('note',text))
def code(b,text):b.append(('code',text))

b=page('Start here','Movie Time | Final assembly and wiring | Checked 8 September 2026')
p(b,'This guide covers the cute lid, reinforced single PETG spring and revised buttons for your measured switches: <b>6 x 6 x 4 mm bodies, with 1 mm high, 3.5 mm diameter actuators</b>. The final player uses 14 screws. Assemble the lid fittings first, then the electronics, case deck and outer shell.')
note(b,'<b>Screw correction:</b> use <b>M2 x 14</b> for the button holder. The previously listed M2 x 16 reaches the bottom of its blind hole. You can reuse M2 x 16 with a <b>2 mm spacer under each head</b>, outside diameter no more than 4 mm. The other listed screw lengths still fit.')
h(b,'Parts to have ready')
table(b,['Print project','What it contains'],[
['01_Spring_PETG.3mf','Reinforced spring with its integral mounting block'],
['02_Cute_Lid_PLA.3mf','Cute lid, spring bosses and button openings'],
['03_Base_PLA.3mf','Electronics base'],
['04_Deck_and_Hardware_PLA.3mf','Case deck, revised button holder, rear plate and LED lens'],
['05_Buttons_PLA.3mf','Revised play, pause and stop caps with narrow pins']], [215,296])
p(b,'A full build needs only these five projects. Upgrading an earlier print? Keep your existing caps: <b>optional/Holder_Reach_Fix_PLA.3mf</b> contains the new holder and matching rear plate. It moves the switch seats 0.8 mm forward for the measured 3.0 mm unpressed and 3.5 mm pressed recesses. Use 100% scale and the supplied print orientations.')
h(b,'Sort the screws into five groups')
table(b,['Code','Qty','Screw','Joins'],[
['A','4','M3 x 25, pan head','Base to lid, from underneath'],
['B','4','M3 x 8, 90-degree countersunk','Case deck to base, from above'],
['C','2','M2 x 14, pan head','Button holder to lid, from inside'],
['D','2','M2 x 6, pan head','Rear retaining plate to button holder'],
['E','2','M2 x 12, pan head','Spring mounting block to lid']], [40,38,196,237])
p(b,'Use ordinary metric machine screws, without nuts or heat-set inserts. For pan heads, measure length <b>from underneath the head to the tip</b>. For countersunk screws, the 8 mm length <b>includes the head</b>. Keep washers out of the stack except for the stated C spacer option.')
p(b,'Also prepare: three kit switches, one 10 kΩ resistor, your original D1 mini / PN532 / WS2812 pixel / passive buzzer, thin flexible wire, heat-shrink, small cable ties, thin foam tape, four rubber feet about 3 mm high, a matching hand screwdriver, soldering tools and a multimeter. Disconnect USB while soldering or moving wires.')

b=page('Where the screws go','Match the letters to the screw bags on page 1')
image(b,'output/final_version/preview/screw_locations.png',390,'Hole positions use the current model. The underside views mirror left and right; keep the front edge toward you.')
table(b,['Code','How to insert it'],[
['A','Through the four base holes from below, upward into the lid posts.'],
['B','From the smooth top of the deck, downward into the base pillars.'],
['C','Through the two vertical holder holes from inside the open lid, toward the roof.'],
['D','Through the rear plate, toward the front panel. These screws run horizontally.'],
['E','Through the spring block from inside the lid, toward the roof.']], [40,471])
p(b,'Choose M2 pan heads no more than <b>4 mm</b> across. The A screws need pan heads no more than <b>6 mm</b> across. The deck has <b>6.4 mm diameter, 90-degree countersinks</b>; use heads that seat flush or below the surface. Check the head drawing if buying a different screw style.')
p(b,'Start each screw straight and turn it gently by hand. These holes form threads in the plastic. Tighten only until the part is secure. If resistance rises before the head seats, back out and check alignment, debris and length. Do not force a screw into the bottom of a blind hole.')

b=page('Fit the buttons','Three caps, one holder and one rear retaining plate')
image(b,'output/final_version/preview/button_fit_section.png',285,'The existing pin is 3 mm in diameter and 2.8 mm long. The new holder moves the switches forward; its matching rear plate secures them.')
steps(b,[
'Dry-fit the switches in the holder. Each body sits in a 6.2 x 6.2 mm pocket, 4 mm deep, with its actuator facing the circular guide. Orient the legs to match the relief slots. Remove the switches again before soldering so the iron cannot soften the PLA.',
'Identify each switch’s two electrical contact groups with a multimeter, then solder and insulate the wires as on page 7. Let the switches cool, refit them and feed the wires through the rear plate slots.',
'Fit the revised rear retaining plate with <b>two D screws: M2 x 6</b>, from the rear toward the front. It holds the bodies against the pocket shoulders. The slight pocket clearance is intentional; the plate is needed to stop the switches falling out.',
'Put the lid upside down on a soft surface. Insert the caps from inside through the large front holes. Their flanges stay inside and the small keys point toward the roof. From the outside, the order is <b>play, pause, stop</b>.',
'Place the holder behind the caps and guide each narrow pin into its opening. Align its two vertical holes with the lid posts. Fit <b>two C screws: M2 x 14</b>, or M2 x 16 with a 2 mm spacer under each head.',
'Check each cap clicks and returns freely. The front faces project 1.4 mm in the model. The measured recesses imply 0.5 mm actuator travel. After moving the switch seats, predicted free play is 0.1 mm and the cap stop remains at 0.7 mm. Check click and return on the new print.'
])

b=page('Fit the PETG spring','The reinforced free-ended leaf mounts directly to the lid')
steps(b,[
'Keep the lid upside down. Locate the two spring bosses immediately behind the button holder. The spring’s flat block face sits against those bosses.',
'Orient the leaf so it curves into the case opening, away from the wiring bay. Its free end points toward the back of the player and remains loose. The straight fixed guard separates its movement from the wires.',
'Insert <b>two E screws: M2 x 12</b> through the 8 mm block from inside the lid, into the bosses. Tighten gently. The nominal stack gives 4 mm of thread engagement and 0.7 mm before the blind-hole bottom.',
'Leave the entire bending space open. Do not glue the leaf, restrain its free end or install any of the older sliders and tail guides.'
])
image(b,'output/final_version/preview/single_leaf_motion.png',295,'The free leaf moves beside the case. Loaded shapes shown here are calculations, not measured print behaviour.')
h(b,'If you use the existing test fixture')
p(b,'The two M2 x 12 screws hold the spring beneath the small PLA bridge. The bridge uses <b>one M2 x 16 screw</b> to the test bed. That bridge and its screw are <b>fixture-only</b>; the finished lid replaces them. This fixture screw is not the C screw corrected on page 1.')
p(b,'Test DVD and Blu-ray insertion, return and left alignment. Check that the reinforced joint remains intact and the tip stays clear of the right guard. The previous leaf aligned the cases; the latest joint’s printed durability still needs your test.')

b=page('Mount the electronics','Work in the open base before fitting the case deck')
image(b,'output/final_version/preview/electronics_placement.png',300,'Placement map, viewed from above. Dashed lines suggest wire routes below the deck; they do not identify individual electrical nets.')
steps(b,[
'<b>PN532:</b> set the red board on the four pads in the left bay, flatter antenna side up toward the case and components down. Keep components off the pads. Use nylon ties through the nearby slots; no metal screw is needed beside the antenna.',
'<b>D1 mini:</b> place it between the rails in the rear right bay, USB socket toward the rear opening. Secure it with a tie and thin foam tape where needed. Keep the USB plug and cable strain relief accessible.',
'<b>Buzzer:</b> place the original passive buzzer over the bottom sound grille, sound opening toward the grille. Fix it with a small amount of foam tape or a tie, leaving the sound holes clear.',
'<b>LED:</b> insert the small lens from inside the front wall so its flange stays inside. Position the WS2812 pixel behind it. Secure and insulate the pixel with tape, keeping its light path clear. White or translucent PLA works best for the lens.',
'Use low soldered wire connections rather than tall plug-in headers under the deck. Route the PN532 wires through the rear tunnel and across the back channel. Keep the button harness on the electronics side of the spring guard. Leave 30-40 mm of slack so the lid can be lifted.'
])
p(b,'The deck must sit on its supports without pressing on boards, solder joints or wiring. Board clone outlines vary: use the pads and ties as a mounting allowance, and check the actual fit before tightening them.')

b=page('Wire the original reader','Use the D1 mini’s printed pin labels, not header position numbers')
p(b,'Movie Time keeps the original tagreader connections. The mapping below was checked against adonno’s schematic and matches movie-player.yaml. The original red PN532 board is powered from 5V; the D1 mini’s signal pins use 3.3V logic. [1-3]')
table(b,['D1 mini connection','Connect to','Detail'],[
['5V','PN532 VCC','Original red PN532 module'],
['G / GND','PN532 GND','Common ground'],
['D1 / GPIO5','PN532 SCL','I²C clock'],
['D2 / GPIO4','PN532 SDA','I²C data'],
['5V','WS2812 5V / VDD','Pixel power'],
['G / GND','WS2812 GND / VSS','Pixel ground'],
['D8 / GPIO15','WS2812 DIN / DI','Use the data input end, not DOUT'],
['D7 / GPIO13','Original passive buzzer +','Keep the original buzzer type'],
['G / GND','Buzzer -','Common ground']], [133,155,223])
h(b,'Set the PN532 to I²C')
p(b,'On the original board, set <b>switch 1 ON and switch 2 OFF</b>. Use the four connections marked SCL, SDA, VCC and GND. The project does not need separate IRQ or RST wires. [1]')
h(b,'Make the connections')
steps(b,[
'Unplug USB. Read the labels on both boards before soldering; clone layouts can place the same pins in different positions.',
'Join the grounds together. Make neat, insulated branches for the shared 5V supply to the PN532 and pixel. Keep bare joints and loose strands away from neighbouring pads.',
'Connect SCL, SDA, pixel DIN and buzzer + as in the table. Label both ends of any wires that will be hidden under the deck.',
'Inspect the solder joints and check for accidental shorts before applying USB power. Test the reader, buzzer and LED with the firmware (page 8) while the deck is still off.'
])
note(b,'The button circuit uses <b>3.3V logic</b>. The 10 kΩ pull-up goes to 3V3, the switches close to GND, and their signal wires go to D0, D5 and D6 as on page 7. Never put 5V onto those inputs. Power the reader through its existing USB connection. [3]')
p(b,'Sources: [1] <link href="https://github.com/adonno/tagreader">adonno/tagreader</link>; [2] <link href="https://github.com/adonno/tagreader/blob/master/Schematics/tag_reader_schematics_v3.2.png">original wiring schematic</link>; [3] <link href="https://www.wemos.cc/en/latest/d1/d1_mini.html">WEMOS pin and voltage documentation</link>.')

b=page('Wire the three buttons','Four wires go to the lid: ground, play, pause and stop')
image(b,'output/preview/button_wiring.png',295,'Place the 10 kΩ resistor near the D1 mini: between 3V3 and the D0/stop signal junction. It is not in series with the switch.')
table(b,['Control','Signal side','Other side'],[
['Play','D5 / GPIO14','GND'],['Pause','D6 / GPIO12','GND'],['Stop','D0 / GPIO16','GND'],
['Stop pull-up','One end of 10 kΩ to 3V3','Other end to D0, shared with stop']], [90,190,231])
p(b,'A four-leg tactile switch has two internally joined groups. With USB disconnected and the switch loose, find a pair of legs that reads open when released and near zero ohms when pressed. Use that pair, one wire on each group. Do not choose two legs that are permanently connected, and do not infer the groups from appearance alone.')
p(b,'D5 and D6 get internal pull-ups from the supplied software. <b>D0 has no internal pull-up</b>, so stop needs the external 10 kΩ. Its software uses polling because GPIO16 does not support GPIO interrupts. [4,5]')
p(b,'Your kit resistor can be 1/8 W or 1/4 W. Typical 10 kΩ markings are <b>brown-black-orange-gold</b> (four bands) or <b>brown-black-black-red-brown</b> (five bands). Measure it loose to confirm roughly 10,000 Ω. Resistors have no polarity. [6]')
p(b,'After soldering, insulate the joints and tie the four-wire harness away from the spring. Check every switch still changes between open and closed before attaching it to the D1 mini.')

b=page('Install the firmware','movie-player.yaml runs the reader and buttons; Home Assistant starts the movie in Kodi')
steps(b,[
'Put <b>movie-player.yaml</b> and <b>movie_reader.h</b> from the top of the repository together in your ESPHome configuration folder. Merge the four entries from <b>secrets.example.yaml</b> into your secrets.yaml. Keep a copy of any previous device YAML for rollback.',
'This one file already includes the reader, LED, buzzer and all three buttons. <b>Do not add the older movie_buttons.yaml package or an upstream tagreader package</b> alongside it.',
'Compile with ESPHome <b>2026.8.2</b> and install over a micro-USB data cable; later updates can use OTA. Add or reconnect the reader in Home Assistant’s ESPHome integration. It does not need the “Allow the device to perform Home Assistant actions” option.',
'With the deck still off, check that <b>Reader Healthy</b> is on, <b>Selected Tag</b> changes when a tagged case goes in and clears after removal, and <b>Play Button</b>, <b>Pause Button</b> and <b>Stop Button</b> each change off, on, off. <b>Test LED</b> and <b>Test Buzzer</b> check the feedback parts.',
'Import <b>blueprints/MovieTimeKodi.yaml</b>, create the <b>Movie Time Active Tag</b> text helper and map each tag to a Kodi movie, as described in the setup guide. [7,8]'
])
table(b,['Physical input','Firmware entity','What Kodi does'],[
['Play','Play Button','Resumes when paused; starts the inserted case again after Stop'],
['Pause','Pause Button','Pauses; pressing again does not resume'],
['Stop','Stop Button','Stops, keeping the case selected for Play'],
['Case removed','Selected Tag clears','Stops after about 1.5-2 seconds']], [103,128,280])
h(b,'If a button clicks but nothing happens')
p(b,'Watch that button’s entity in Home Assistant. If it does not change, check the input wiring; Stop also needs its 10 kΩ pull-up to 3V3. If it changes but Kodi does not respond, check the blueprint’s entity choices, Kodi availability and the automation trace. [7,8]')
note(b,'Installation, movie mapping and the full session checks are in the <link href="https://github.com/rendyhd/movie-time/blob/main/docs/movie-time-setup.md">Movie Time setup guide</link>. The firmware is tested with ESPHome <b>2026.8.2</b> / ESP8266 Arduino 3.1.2. Compilation and simulated Home Assistant tests do not replace the physical checks in this guide.')

b=page('Fit the deck, test and close','B screws for the deck, then A screws for the outer shell')
steps(b,[
'Unplug USB. Set the deck over the electronics, <b>smooth side up and reinforcing ribs down</b>. The thin antenna area goes over the PN532. Make sure the deck rests flat without trapping wires.',
'Fit <b>four B screws: M3 x 8, 90-degree countersunk</b>, from the top. Their heads must finish flush or recessed so they cannot scratch a case. Do not substitute pan heads here.',
'For a 135 mm-deep case, view it with the front cover up and spine toward you. The tag centre is <b>26 mm from that left short edge and 104 mm from the spine</b>. Temporarily place the sticker on the underside/back-cover side directly beneath that point. Keep the case against the left guide.'
])
image(b,'output/preview/tag_placement.png',245,'The sticker is on the underside of the case. The left-edge distance is corrected to 26 mm for the final left guide.')
steps(b,[
'Set the completed lid on the base without the A screws, with wires clear of the spring. Reconnect USB and test DVD and Blu-ray cases, including any disc and sleeve you intend to keep. Confirm reads, left alignment and all three controls. Fix stickers permanently only after testing each case format.',
'Unplug USB and make the final wire check. Seat the lid with the rear alignment pins engaged, the spring clear and the harness tucked into the right bay. The lid should meet the base without screw force.',
'Fit <b>four A screws: M3 x 25 pan head</b>, through the base from underneath. Start all four loosely, then snug them evenly. Add four rubber feet about 3 mm high, clear of the sound grille and screw access. Reconnect USB and repeat the functional check with the shell closed.'
])

b=page('Final checks and reference','Use this page beside the assembled player')
table(b,['Check','What you should see'],[
['Buttons','All three caps click, release freely and trigger the intended action.'],
['Case movement','DVD and Blu-ray cases reach the rear stop; the spring returns after removal.'],
['Spring attachment','No cracking at the reinforced joint; the free end stays clear of wires.'],
['Deck and shell','Deck heads are flush, no trapped wire, lid seats evenly and feet are stable.'],
['NFC','Each selected case reads reliably through the closed player.'],
['Before handing it over','Lid secured, internal parts inaccessible, USB lead kept out of the loading slot.']], [109,402])
h(b,'Quick troubleshooting')
table(b,['Symptom','Check first'],[
['Switch falls out','Fit the revised rear retaining plate with the two D screws.'],
['Cap cannot reach the switch','Use the revised cap with a full-length 3 mm pin and its matching holder.'],
['Cap sticks / stays pressed','Check its key and guide alignment, burrs, switch seating and free play. Do not force it.'],
['Stop input floats or triggers alone','Check the 10 kΩ connection from D0 to 3V3 and the common ground.'],
['No NFC read','Check PN532 mode, SCL/SDA, antenna facing up and sticker position; retest without the case.'],
['Screw tightens before the part seats','Check length and alignment. C uses 14 mm, or 16 mm plus a 2 mm spacer.']], [147,364])
h(b,'What was double-checked')
p(b,'The released CAD was checked for all 14 nominal screw envelopes, unrelated-part clearance and blind-hole margins. Button body retention, pin travel and current part clearances were checked; the supplied A1 plates are sliced. Wiring was checked against the original project and official pin documentation. Printed tolerances, spring fatigue, switch travel, NFC read range and child operating force still require the physical checks above.')
h(b,'Primary references')
p(b,'[1] <link href="https://github.com/adonno/tagreader">Tagreader project and PN532 mode</link> · [2] <link href="https://github.com/adonno/tagreader/blob/master/Schematics/tag_reader_schematics_v3.2.png">Original wiring schematic</link> · [3] <link href="https://www.wemos.cc/en/latest/d1/d1_mini.html">WEMOS D1 mini</link>')
p(b,'[4] <link href="https://esphome.io/components/esp8266/">ESPHome ESP8266 pin restrictions</link> · [5] <link href="https://arduino-esp8266.readthedocs.io/en/3.0.0/reference.html">ESP8266 GPIO interrupts</link> · [6] <link href="https://www.vishay.com/docs/20143/colorcod.pdf">Vishay resistor colour code</link>')
p(b,'[7] <link href="https://github.com/rendyhd/movie-time/blob/main/docs/movie-time-setup.md">Movie Time setup guide</link> · [8] <link href="https://www.home-assistant.io/integrations/kodi/">Home Assistant Kodi integration</link>. CAD and hardware records: hardware/output/final_version/validation/assembly_audit.json.')
