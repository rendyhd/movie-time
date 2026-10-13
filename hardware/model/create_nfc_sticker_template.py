"""Make a full-size corner guide for placing a movie-case NFC sticker."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).resolve().parents[1] / "output/pdf/Movie_Time_NFC_Sticker_Template_A4.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

c = canvas.Canvas(str(OUTPUT), pagesize=A4)
c.setTitle("Movie Time - NFC sticker placement template")
c.setAuthor("Movie Time")
c.setFillColor(colors.white)
c.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)

ink = colors.HexColor("#263343")
muted = colors.HexColor("#566576")
blue = colors.HexColor("#16679A")
orange = colors.HexColor("#DD7040")


def label(x, y, text, size=10, color=ink, font="Helvetica"):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x * mm, y * mm, text)


def line(x1, y1, x2, y2, color=ink, width=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)


label(22, 275, "MOVIE TIME", 11, blue, "Helvetica-Bold")
label(22, 264, "NFC sticker starting position", 20, ink, "Helvetica-Bold")
label(22, 251, "Print on A4 at Actual size / 100%. Do not use Fit to page.", 10, muted)

label(22, 233, "1", 15, orange, "Helvetica-Bold")
label(33, 234, "Lay the CLOSED case with its BACK COVER facing up.", 10)
label(33, 228, "The SPINE must be at the TOP, away from you.", 10)
label(22, 216, "2", 15, orange, "Helvetica-Bold")
label(33, 217, "Cut out the rectangle below along its solid border.", 10)
label(33, 211, "Put its bottom-left corner on the case's bottom-left corner.", 10)
label(22, 199, "3", 15, orange, "Helvetica-Bold")
label(33, 200, "Make a tiny hole at the target and mark through it.", 10)
label(33, 194, "Tape the sticker there. If reads fail, move it 5 mm at a time.", 10)

# Cut-out: the corner and target are separated by exactly 26 x 31 mm.
left, bottom, width, height = 28, 82, 90, 96
target_x, target_y = left + 26, bottom + 31
c.setStrokeColor(ink)
c.setLineWidth(0.8)
c.rect(left * mm, bottom * mm, width * mm, height * mm)

# A miniature case orientation diagram belongs to the cut-out and remains clear
# of the actual sticker area.
label(left + 34, bottom + 83, "BACK COVER UP", 9, blue, "Helvetica-Bold")
line(left + 20, bottom + 77, left + 70, bottom + 77, blue, 1)
label(left + 41, bottom + 70, "SPINE", 8, blue, "Helvetica-Bold")
label(left + 34, bottom + 59, "away from you", 8, muted)

# The thin outer circle shows the approximate footprint of a 25 mm sticker.
c.setStrokeColor(colors.HexColor("#C6DCE9"))
c.setLineWidth(0.7)
c.circle(target_x * mm, target_y * mm, 12.5 * mm)
c.setStrokeColor(orange)
c.setLineWidth(1)
c.circle(target_x * mm, target_y * mm, 1.5 * mm)
line(target_x - 8, target_y, target_x - 3, target_y, orange, 0.8)
line(target_x + 3, target_y, target_x + 8, target_y, orange, 0.8)
line(target_x, target_y - 8, target_x, target_y - 3, orange, 0.8)
line(target_x, target_y + 3, target_x, target_y + 8, orange, 0.8)

# Measurement arrows printed on the stencil.
line(left, bottom + 7, target_x, bottom + 7, muted, 0.4)
line(left, bottom + 5, left, bottom + 9, muted, 0.4)
line(target_x, bottom + 5, target_x, bottom + 9, muted, 0.4)
label(left + 9, bottom + 9, "26 mm", 8, muted)
line(left + 7, bottom + 10, left + 7, target_y, muted, 0.4)
line(left + 5, target_y, left + 9, target_y, muted, 0.4)
label(left + 9, target_y - 13, "31 mm", 8, muted)

label(left + 17, bottom + 48, "LEFT EDGE", 8, muted, "Helvetica-Bold")
label(left + 35, bottom + 4, "BOTTOM EDGE", 8, muted, "Helvetica-Bold")

# Side note clarifies how the target relates to the position used in the
# assembly guide when the front cover is up.
label(128, 158, "Nominal centre:", 11, ink, "Helvetica-Bold")
label(128, 149, "2.6 cm from the left edge", 9)
label(128, 142, "3.1 cm from the bottom edge", 9)
label(128, 126, "DVD and Blu-ray cases", 9, muted)
label(128, 119, "use the same corner.", 9, muted)
label(128, 102, "The pale circle shows a", 9, muted)
label(128, 95, "25 mm sticker for scale.", 9, muted)

label(22, 66, "Check the print scale with a ruler:", 10, ink, "Helvetica-Bold")
line(28, 50, 78, 50, blue, 1.2)
line(28, 47, 28, 53, blue, 1.2)
line(78, 47, 78, 53, blue, 1.2)
label(42, 55, "50 mm", 10, blue, "Helvetica-Bold")
label(22, 37, "If this line is not exactly 5 cm, print again at 100% scale.", 9, muted)
label(22, 25, "Fix to the OUTSIDE of the back cover only after 5 reliable insertions.", 9, ink, "Helvetica-Bold")

c.showPage()
c.save()
print(OUTPUT)
