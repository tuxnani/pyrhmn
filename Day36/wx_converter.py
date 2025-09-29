# -*- coding: utf-8 -*-

TELUGU_VOWELS = {
    'అ': 'a', 'ఆ': 'A', 'ఇ': 'i', 'ఈ': 'I', 'ఉ': 'u', 'ఊ': 'U',
    'ఎ': 'eV', 'ఏ': 'e', 'ఐ': 'E', 'ఒ': 'oV', 'ఓ': 'o', 'ఔ': 'O',
    'ఋ': 'q'
}

TELUGU_SIGNS = {
    'ం': 'M', 'ః': 'H', 'ఁ': 'z'
}

TELUGU_CONSONANTS = {
    'క': 'ka', 'ఖ': 'Ka', 'గ': 'ga', 'ఘ': 'Ga', 'ఙ': 'fa',
    'చ': 'ca', 'ఛ': 'Ca', 'జ': 'ja', 'ఝ': 'Ja', 'ఞ': 'Fa',
    'ట': 'ta', 'ఠ': 'Ta', 'డ': 'da', 'ఢ': 'Da', 'ణ': 'Na',
    'త': 'wa', 'థ': 'Wa', 'ద': 'xa', 'ధ': 'Xa', 'న': 'na',
    'ప': 'pa', 'ఫ': 'Pa', 'బ': 'ba', 'భ': 'Ba', 'మ': 'ma',
    'య': 'ya', 'ర': 'ra', 'ఱ': 'rYa', 'ల': 'la', 'ళ': 'lYa',
    'వ': 'va', 'శ': 'Sa', 'ష': 'Ra', 'స': 'sa', 'హ': 'ha'
}

VOWEL_SIGNS = {
    'ా': 'A', 'ి': 'i', 'ీ': 'I', 'ు': 'u', 'ూ': 'U',
    'ె': 'eV', 'ే': 'e', 'ై': 'E', 'ొ': 'oV', 'ో': 'o', 'ౌ': 'O',
    'ృ': 'q'
}

DIGITS = {
    '౦': '0', '౧': '1', '౨': '2', '౩': '3', '౪': '4',
    '౫': '5', '౬': '6', '౭': '7', '౮': '8', '౯': '9'
}

# Reverse mappings for WX -> Telugu
WX_TO_VOWEL = {v: k for k, v in TELUGU_VOWELS.items()}
WX_TO_SIGN = {v: k for k, v in TELUGU_SIGNS.items()}
WX_TO_CONS = {v: k for k, v in TELUGU_CONSONANTS.items()}
WX_TO_DIGIT = {v: k for k, v in DIGITS.items()}


def to_wx(text):
    """Convert Telugu Unicode string to WX notation."""
    result = []
    for ch in text:
        if ch in TELUGU_VOWELS:
            result.append(TELUGU_VOWELS[ch])
        elif ch in TELUGU_CONSONANTS:
            result.append(TELUGU_CONSONANTS[ch])
        elif ch in VOWEL_SIGNS:
            result.append(VOWEL_SIGNS[ch])
        elif ch in TELUGU_SIGNS:
            result.append(TELUGU_SIGNS[ch])
        elif ch == '్':
            # virama - remove inherent 'a'
            if result and result[-1].endswith('a'):
                result[-1] = result[-1][:-1]
        elif ch in DIGITS:
            result.append(DIGITS[ch])
        else:
            result.append(ch)
    return ''.join(result)


def to_telugu(wx):
    """Convert WX notation string to Telugu Unicode."""
    # Process longest matches first
    sorted_keys = sorted(list(WX_TO_CONS.keys()) + list(WX_TO_VOWEL.keys()) +
                         list(WX_TO_SIGN.keys()), key=len, reverse=True)
    result = ''
    i = 0
    while i < len(wx):
        matched = False
        for key in sorted_keys:
            if wx.startswith(key, i):
                if key in WX_TO_CONS:
                    result += WX_TO_CONS[key]
                elif key in WX_TO_VOWEL:
                    result += WX_TO_VOWEL[key]
                elif key in WX_TO_SIGN:
                    result += WX_TO_SIGN[key]
                matched = True
                i += len(key)
                break
        if not matched:
            # Try single chars like digits
            if wx[i] in WX_TO_DIGIT:
                result += WX_TO_DIGIT[wx[i]]
            else:
                result += wx[i]
            i += 1
    return result


# Quick test
if __name__ == "__main__":
    telugu_text = "దక్షిణమధ్య"
    wx_text = to_wx(telugu_text)
    print("Telugu → WX:", wx_text)

    back_to_telugu = to_telugu(wx_text)
    print("WX → Telugu:", back_to_telugu)
