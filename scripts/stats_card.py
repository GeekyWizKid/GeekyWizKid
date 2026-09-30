"""Cache a validated stats SVG so profile visitors do not call a remote API."""
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

url = 'https://github-readme-stats.vercel.app/api?username=GeekyWizKid&show_icons=true&theme=radical&hide_border=true'
target = Path('assets/stats.svg')
try:
    with urllib.request.urlopen(url, timeout=45) as response:
        data = response.read()
    root = ET.fromstring(data)
    description = root.find('{http://www.w3.org/2000/svg}desc')
    if root.tag != '{http://www.w3.org/2000/svg}svg' or description is None or 'Total Stars Earned:' not in ''.join(description.itertext()):
        raise ValueError('Response is not a valid statistics card')
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(data)
    print('Saved validated statistics card')
except Exception as error:
    if not target.exists():
        raise
    print(f'Statistics service unavailable ({type(error).__name__}); retained last valid card')
