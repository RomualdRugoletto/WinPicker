# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Static data for the Kaomoji and Symbols tabs."""
import unicodedata

from .i18n import _

VS15 = "\ufe0e"  # text presentation selector
TEXT_NOTE = _("Inserted as plain text, never as a color emoji (adds U+FE0E)")

KAOMOJI = [
    (_("Happy"), ["(◕‿◕)", "(＾▽＾)", "(´• ω •`)", "ヽ(・∀・)ﾉ", "(✿◠‿◠)", "(⌒‿⌒)", "＼(^o^)／", "(≧◡≦)", "ᕕ( ᐛ )ᕗ", "(•̀ᴗ•́)و ̑̑"]),
    (_("Love"), ["(♡μ_μ)", "(´∀｀)♡", "(｡♥‿♥｡)", "(づ￣ ³￣)づ", "♡(ˆ⌣ˆԅ)", "(˘³˘)♥"]),
    (_("Sad"), ["(╥﹏╥)", "(ಥ﹏ಥ)", "(._.)", "(´；ω；`)", "(っ˘̩╭╮˘̩)っ", "(｡•́︿•̀｡)"]),
    (_("Angry"), ["(╯°□°）╯︵ ┻━┻", "(ノಠ益ಠ)ノ彡┻━┻", "(ಠ_ಠ)", "(｀Д´)", "ಠ╭╮ಠ", "┬─┬ノ( º _ ºノ)"]),
    (_("Misc"), ["¯\\_(ツ)_/¯", "( ͡° ͜ʖ ͡°)", "(⊙_☉)", "ʕ•ᴥ•ʔ", "(=^･ω･^=)", "(☞ﾟヮﾟ)☞", "(¬‿¬)", "(•_•) ( •_•)>⌐■-■ (⌐■_■)", "(*_*)", "(°ロ°) !"]),
]

# (title, navigation bar icon, characters separated by spaces)
SYMBOLS = [
    (_("Punctuation"), "«", "« » “ ” ‘ ’ „ ‚ ‹ › … — – ‒ ― ‐ • ‣ ◦ · ¡ ¿ ‽ ⸘ ¦ ‖ § ¶ † ‡ ′ ″ ‴ ‰ ‱ ※ ⁂ ⁎ ⁑ ⁄ ‾ ¨ ´ ˆ ˜ ¸ ⁓ 〃 ⸮"),
    (_("Accented letters"), "É",
     "à â ä á ã å æ ç é è ê ë í ì î ï ñ ó ò ô ö õ ø œ ú ù û ü ý ÿ ß "
     "À Â Ä Á Ã Å Æ Ç É È Ê Ë Í Ì Î Ï Ñ Ó Ò Ô Ö Õ Ø Œ Ú Ù Û Ü Ý Ÿ "
     "ā ă ą ć č ď đ ē ė ę ě ğ ı ł ń ň ő ř ś ş š ť ţ ū ů ű ź ż ž ð þ "
     "Ā Ă Ą Ć Č Ď Đ Ē Ė Ę Ě Ğ İ Ł Ń Ň Ő Ř Ś Ş Š Ť Ţ Ū Ů Ű Ź Ż Ž Ð Þ ẞ"),
    (_("Currencies"), "€", "€ $ £ ¥ ¢ ₿ ₹ ₽ ₩ ₺ ₴ ₪ ฿ ₫ ₦ ₱ ₲ ₵ ₸ ₼ ₾ ₡ ₭ ₮ ₨ ₣ ₤ ₧ ₳ ₠ ৳ ៛ ﷼ ¤"),
    (_("Math"), "±",
     "± ∓ × ÷ ⋅ ∘ ∗ ≠ ≈ ≃ ≅ ≡ ≢ ≜ ≝ ∼ ≤ ≥ ≪ ≫ ≺ ≻ ∞ √ ∛ ∜ ∑ ∏ ∐ ∫ ∬ ∭ ∮ ∂ ∆ ∇ "
     "∈ ∉ ∋ ∌ ∩ ∪ ⊂ ⊃ ⊄ ⊅ ⊆ ⊇ ∅ ∁ ∀ ∃ ∄ ¬ ∧ ∨ ⊻ ⊕ ⊗ ⊖ ⊙ ⊢ ⊨ ⊤ ⊥ ∴ ∵ ∝ ∠ ∡ ∥ ∦ "
     "⌈ ⌉ ⌊ ⌋ ⟨ ⟩ ⟦ ⟧ ℕ ℤ ℚ ℝ ℂ ℙ ℵ ℏ ℘ ∎"),
    (_("Fractions and numbers"), "½",
     "½ ⅓ ⅔ ¼ ¾ ⅕ ⅖ ⅗ ⅘ ⅙ ⅚ ⅐ ⅛ ⅜ ⅝ ⅞ ⅑ ⅒ ↉ ⅟ "
     "Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ Ⅵ Ⅶ Ⅷ Ⅸ Ⅹ Ⅺ Ⅻ Ⅼ Ⅽ Ⅾ Ⅿ ⅰ ⅱ ⅲ ⅳ ⅴ ⅵ ⅶ ⅷ ⅸ ⅹ "
     "⓪ ① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩ ⑪ ⑫ ⑬ ⑭ ⑮ ⑯ ⑰ ⑱ ⑲ ⑳ ❶ ❷ ❸ ❹ ❺ ❻ ❼ ❽ ❾ ❿"),
    (_("Superscripts and subscripts"), "x²",
     "⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻ ⁼ ⁽ ⁾ ᵃ ᵇ ᶜ ᵈ ᵉ ᶠ ᵍ ʰ ⁱ ʲ ᵏ ˡ ᵐ ⁿ ᵒ ᵖ ʳ ˢ ᵗ ᵘ ᵛ ʷ ˣ ʸ ᶻ ª º "
     "ᴬ ᴮ ᴰ ᴱ ᴳ ᴴ ᴵ ᴶ ᴷ ᴸ ᴹ ᴺ ᴼ ᴾ ᴿ ᵀ ᵁ ⱽ ᵂ "
     "₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉ ₊ ₋ ₌ ₍ ₎ ₐ ₑ ₕ ᵢ ⱼ ₖ ₗ ₘ ₙ ₒ ₚ ᵣ ₛ ₜ ᵤ ᵥ ₓ"),
    (_("Arrows"), "→",
     "← → ↑ ↓ ↔ ↕ ↖ ↗ ↘ ↙ ⇐ ⇒ ⇑ ⇓ ⇔ ⇕ ⇖ ⇗ ⇘ ⇙ ⟵ ⟶ ⟷ ⟸ ⟹ ⟺ ↤ ↦ ⟻ ⟼ "
     "⇠ ⇢ ⇡ ⇣ ⇦ ⇨ ⇩ ⬅ ➡ ⬆ ⬇ ⬈ ⬉ ⬊ ⬋ ➜ ➔ ➝ ➞ ➤ ➢ ⇄ ⇆ ⇅ ⇵ ⇉ ⇇ ⇈ ⇊ ↞ ↠ ↟ ↡ "
     "↩ ↪ ↰ ↱ ↲ ↳ ↴ ↵ ⤴ ⤵ ↺ ↻ ⟲ ⟳ ↜ ↝ ⇜ ⇝ ↯"),
    (_("Greek"), "Ω",
     "α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ ς τ υ φ χ ψ ω ϑ ϕ ϖ ϵ "
     "Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω"),
    (_("Geometric shapes"), "■",
     "● ○ ◉ ◎ ◌ ◍ ◐ ◑ ◒ ◓ ◔ ◕ ◖ ◗ ⬤ ◯ ■ □ ▪ ▫ ▢ ▣ ▤ ▥ ▦ ▧ ▨ ▩ ◼ ◻ ◆ ◇ ◈ ❖ ◊ "
     "▲ △ ▴ ▵ ▼ ▽ ▾ ▿ ► ◄ ▶ ◀ ▷ ◁ ▸ ◂ ▹ ◃ ◢ ◣ ◤ ◥ ⬟ ⬠ ⬡ ⬢ ⬣"),
    (_("Checkmarks, stars and dingbats"), "✓",
     "✓ ✔ ✗ ✘ ☐ ☑ ☒ ⊠ ★ ☆ ✦ ✧ ✩ ✪ ✫ ✬ ✭ ✮ ✯ ✰ ✱ ✲ ✳ ✴ ✵ ✶ ✷ ✸ ✹ ✺ ✻ ✼ ✽ ❋ "
     "✿ ❀ ❁ ❃ ❄ ❅ ❆ ❇ ❈ ❉ ✚ ✛ ✜ ✝ ✞ ✟ ✠ ✡ ❤ ❥ ❦ ❧ ☙ ✂ ✄ ✆ ✉ ✍ ✎ ✏ ✐ ✑ ✒ ☛ ☞ ☜ ☝ ☟ ✌"),
    (_("Box drawing"), "┼",
     "─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ━ ┃ ┏ ┓ ┗ ┛ ┣ ┫ ┳ ┻ ╋ ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬ "
     "╭ ╮ ╯ ╰ ╱ ╲ ╳ ┄ ┆ ┈ ┊ ╌ ╎ █ ▓ ▒ ░ ▀ ▄ ▌ ▐ ▁ ▂ ▃ ▅ ▆ ▇ ▉ ▊ ▋ ▍ ▎ ▏"),
    (_("Technical and keyboard"), "⌘",
     "⌘ ⌥ ⇧ ⌃ ⇪ ⌫ ⌦ ⎋ ⏎ ⇥ ⇤ ␣ ⌨ ⏏ ⎇ ⎈ ⌂ ⌀ ⌖ ⌕ ⏻ ⏼ ⏽ ⭘ ⏸ ⏹ ⏺ ⏯ ⏮ ⏭ ⏪ ⏩ "
     "⌚ ⌛ ⏳ ⏰ ⏱ ⏲ ⧖ ⧗ ⚙ ⚠ ⚡ ⌁ ⏚ ␀ ␉ ␊ ␍ ⍰ ⎌"),
    (_("Units and letterlike"), "℃",
     "© ® ™ ℠ ℗ № ℃ ℉ ° µ ℮ ℅ ℆ ℀ ℁ ℓ ℡ ℹ ℞ ℔ ℥ ⅍ "
     "㎡ ㎥ ㎠ ㎤ ㎎ ㎏ ㎍ ㎖ ㎗ ㎘ ㎜ ㎝ ㎞ ㏄ ㎐ ㎑ ㎒ ㎓ ㎾ ㎽ ㏈"),
    (_("Miscellaneous"), "☀",
     "☀ ☁ ☂ ☃ ☄ ☾ ☽ ☼ ☉ ☎ ☏ ⚐ ⚑ ☢ ☣ ☮ ☯ ☸ ☺ ☹ ☻ ☠ ⚓ ⚔ ⚖ ⚗ ⚛ ⚕ ♻ ♲ ♿ "
     "♀ ♂ ⚥ ⚢ ⚣ ⚤ ⚧ ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓ ☿ ♁ ♃ ♄ ♅ ♆ ♇"),
    (_("Games and music"), "♠",
     "♠ ♣ ♥ ♦ ♤ ♧ ♡ ♢ ♔ ♕ ♖ ♗ ♘ ♙ ♚ ♛ ♜ ♝ ♞ ♟ ⚀ ⚁ ⚂ ⚃ ⚄ ⚅ "
     "♩ ♪ ♫ ♬ ♭ ♮ ♯ 𝄞 𝄢"),
]


def as_text(char: str, emoji_chars: set[str]) -> str:
    """Characters that also exist as emoji get the text presentation selector, so that
    neither GTK nor the target application draws them as color emoji."""
    return char + VS15 if char in emoji_chars else char


def symbol_sections(emoji_chars: set[str]):
    """[(title, [(text, search keywords, tooltip)], navigation bar icon)].
    emoji_chars: every character that has an emoji form, without variation selector."""
    sections = []
    for title, icon, chars in SYMBOLS:
        items = []
        for c in chars.split():
            try:
                name = unicodedata.name(c)
            except ValueError:
                name = ""
            text = as_text(c, emoji_chars)
            tooltip = name.capitalize() + ("\n" + TEXT_NOTE if text != c else "")  # "BLACK STAR" -> "Black star"
            items.append((text, f"{title} {name}", tooltip))
        sections.append((title, items, as_text(icon, emoji_chars)))
    return sections


def kaomoji_sections():
    return [(title, [(k, title) for k in items]) for title, items in KAOMOJI]
