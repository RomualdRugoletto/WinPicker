# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Static data for the Kaomoji and Symbols tabs."""
import unicodedata

from .i18n import _

KAOMOJI = [
    (_("Happy"), ["(◕‿◕)", "(＾▽＾)", "(´• ω •`)", "ヽ(・∀・)ﾉ", "(✿◠‿◠)", "(⌒‿⌒)", "＼(^o^)／", "(≧◡≦)", "ᕕ( ᐛ )ᕗ", "(•̀ᴗ•́)و ̑̑"]),
    (_("Love"), ["(♡μ_μ)", "(´∀｀)♡", "(｡♥‿♥｡)", "(づ￣ ³￣)づ", "♡(ˆ⌣ˆԅ)", "(˘³˘)♥"]),
    (_("Sad"), ["(╥﹏╥)", "(ಥ﹏ಥ)", "(._.)", "(´；ω；`)", "(っ˘̩╭╮˘̩)っ", "(｡•́︿•̀｡)"]),
    (_("Angry"), ["(╯°□°）╯︵ ┻━┻", "(ノಠ益ಠ)ノ彡┻━┻", "(ಠ_ಠ)", "(｀Д´)", "ಠ╭╮ಠ", "┬─┬ノ( º _ ºノ)"]),
    (_("Misc"), ["¯\\_(ツ)_/¯", "( ͡° ͜ʖ ͡°)", "(⊙_☉)", "ʕ•ᴥ•ʔ", "(=^･ω･^=)", "(☞ﾟヮﾟ)☞", "(¬‿¬)", "(•_•) ( •_•)>⌐■-■ (⌐■_■)", "(*_*)", "(°ロ°) !"]),
]

SYMBOLS = [
    (_("Punctuation"), "« » “ ” ‘ ’ „ ‹ › … — – • · ¡ ¿ ‽ § ¶ † ‡ ′ ″ ‰ ‱ ※ ⁂ ° № ℃ ℉ © ® ™ ℠"),
    (_("Accented letters"), "À Â Ä Ç É È Ê Ë Î Ï Ô Ö Ù Û Ü Ÿ Œ Æ œ æ ß ñ Ñ ø Ø å Å ã õ ı ğ ş č ř š ž ł"),
    (_("Currencies"), "€ $ £ ¥ ¢ ₿ ₹ ₽ ₩ ₺ ₴ ₪ ฿ ₫ ₦ ₱ ¤"),
    (_("Math"), "± × ÷ ≠ ≈ ≡ ≤ ≥ ∞ √ ∛ ∑ ∏ ∫ ∂ ∆ ∇ ∈ ∉ ∩ ∪ ⊂ ⊃ ⊆ ⊇ ∅ ∀ ∃ ¬ ∧ ∨ ⊕ ∝ ∠ ⊥ ∥ ½ ⅓ ¼ ¾ ‰"),
    (_("Superscripts and subscripts"), "⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻ ⁼ ⁽ ⁾ ⁿ ⁱ ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉ ₊ ₋ ₌ ₍ ₎"),
    (_("Arrows"), "← → ↑ ↓ ↔ ↕ ↖ ↗ ↘ ↙ ⇐ ⇒ ⇑ ⇓ ⇔ ⇕ ↩ ↪ ↺ ↻ ➜ ➔ ⟵ ⟶ ⟷ ⏎ ⇥ ⇤"),
    (_("Greek"), "α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω Γ Δ Θ Λ Ξ Π Σ Φ Ψ Ω"),
    (_("Shapes and misc"), "✓ ✔ ✗ ✘ ★ ☆ ● ○ ◆ ◇ ■ □ ▲ △ ▼ ▽ ► ◄ ♠ ♣ ♥ ♦ ♪ ♫ ☀ ☁ ☂ ☎ ⌘ ⌥ ⇧ ⌫ ⌦ ⎋ ␣"),
]


def symbol_sections():
    """[(title, [(text, unicode name used for search)])]"""
    sections = []
    for title, chars in SYMBOLS:
        items = []
        for c in chars.split():
            try:
                name = unicodedata.name(c)
            except ValueError:
                name = ""
            items.append((c, f"{title} {name}"))
        sections.append((title, items))
    return sections


def kaomoji_sections():
    return [(title, [(k, title) for k in items]) for title, items in KAOMOJI]
