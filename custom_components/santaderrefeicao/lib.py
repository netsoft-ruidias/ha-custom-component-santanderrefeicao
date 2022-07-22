"""LIB to Santader Refeicao."""
from typing import Dict
from html.parser import HTMLParser

def parseSessionState(html: str) -> Dict[str, str]:
    # <section>
    index = html.find('<section class="form-container">')
    section = html[index:]
    index = section.find('</section>') + 10
    section = section[0:index]

    # <input username>
    index = section.find('<input type="text"')
    usernameDiv = section[index:]
    index = usernameDiv.find('>') + 1
    usernameDiv = usernameDiv[0:index]
    
    index = usernameDiv.find('id=') + 4
    usernameId = usernameDiv[index:]
    index = usernameId.find('"')
    usernameId = usernameId[0:index]

    # <input password>
    index = section.find('<input type="password"')
    passwordDiv = section[index:]
    index = passwordDiv.find('>') + 1
    passwordDiv = passwordDiv[0:index]

    index = passwordDiv.find('id=') + 4
    passwordId = passwordDiv[index:]
    index = passwordId.find('"')
    passwordId = passwordId[0:index]

    return {
        "username": usernameId,
        "password": passwordId
    }
    
def parseOGCToken(text: str) -> str:
    if (text.find('OGC_TOKEN:') == 0):
        return text[10:]
    else:
        return ""

def parseCardDetails(html: str) -> Dict[str, str]:
    # <section>
    index = html.find('<div class="balance-container">')
    section = html[index:]
    index = section.find('</section>')
    section = section[0:index]

    # <card_ref>
    pattern = '<p class="balance-value">'
    index = section.find(pattern) + len(pattern)
    section = section[index:]
    index = section.find('</p>')
    cardRef = section[0:index]

    # <gross_balance>
    pattern = '<p class="balance-value">'
    index = section.find(pattern, index) + len(pattern)
    section = section[index:]
    index = section.find('</p>')
    grossBalance = section[0:index]

    # <net_balance>
    pattern = '<p class="balance-value text-green">'
    index = section.find(pattern, index) + len(pattern)
    section = section[index:]
    index = section.find('</p>')
    netBalance = section[0:index]

    return {
        'cardRef': cardRef,
        'grossBalance': grossBalance,
        'netBalance': netBalance
    }

def _getValue(html: str, start: str, end: str, startIndex: int = 0) -> str:
    index = html.find(start, startIndex) 
    if (index >= 0):
        index = index + len(start)
        result = html[index:]
        index = result.find(end)
        return html[0:index]
    else:
        return ""