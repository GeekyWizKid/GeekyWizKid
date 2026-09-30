"""Generate a 31-day activity graph from GitHub's contribution calendar."""
import datetime as dt
import html
import json
from pathlib import Path
import subprocess

end = dt.datetime.now(dt.timezone.utc)
start = end - dt.timedelta(days=30)
query = '''query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) { contributionsCollection(from:$from,to:$to) {
    contributionCalendar { weeks { contributionDays { date contributionCount } } }
  } }
}'''
result = subprocess.run([
    'gh', 'api', 'graphql', '-f', f'query={query}',
    '-f', 'login=GeekyWizKid', '-f', f'from={start.strftime("%Y-%m-%dT00:00:00Z")}',
    '-f', f'to={end.strftime("%Y-%m-%dT%H:%M:%SZ")}',
], check=True, capture_output=True, text=True)
data = json.loads(result.stdout)
if data.get('errors'):
    raise RuntimeError('GitHub returned GraphQL errors')
weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
counts = {d['date']: d['contributionCount'] for w in weeks for d in w['contributionDays']}
days = [(start.date() + dt.timedelta(days=i)).isoformat() for i in range(31)]
values = [counts[d] for d in days]
maximum = max(max(values), 1)
points = [(55 + i * 27, 205 - value / maximum * 130) for i, value in enumerate(values)]
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="270" viewBox="0 0 920 270" role="img" aria-labelledby="title desc">',
       '<title id="title">GeekyWizKid GitHub activity</title>',
       f'<desc id="desc">Daily GitHub contributions from {days[0]} to {days[-1]}. Total: {sum(values)}. Updated {end.strftime("%Y-%m-%d %H:%M UTC")}.</desc>',
       '<rect width="920" height="270" rx="10" fill="#0d1117"/>',
       '<g font-family="Arial,sans-serif" fill="#c9d1d9">',
       '<text x="30" y="35" font-size="20">GitHub Activity · Last 31 Days</text>',
       f'<text x="30" y="57" font-size="12" fill="#8b949e">{sum(values)} contributions · Updated {end.strftime("%Y-%m-%d UTC")}</text>']
for fraction in (0, .5, 1):
    y = 205 - fraction * 130
    svg.append(f'<path d="M55 {y} H865" stroke="#21262d"/><text x="18" y="{y+4}" font-size="11">{maximum*fraction:g}</text>')
svg.append('<polyline fill="none" stroke="#39d353" stroke-width="2.5" points="' + ' '.join(f'{x},{y:.2f}' for x,y in points) + '"/>')
for date,value,(x,y) in zip(days,values,points):
    svg.append(f'<circle cx="{x}" cy="{y:.2f}" r="3" fill="#39d353"><title>{html.escape(date)}: {value} contributions</title></circle>')
for i in (0, 7, 14, 21, 30):
    svg.append(f'<text x="{points[i][0]}" y="235" text-anchor="middle" font-size="11">{days[i][5:]}</text>')
svg.append('</g></svg>')
Path('assets').mkdir(exist_ok=True)
Path('assets/activity.svg').write_text('\n'.join(svg) + '\n')
print(f'Generated graph with {len(values)} days and {sum(values)} contributions')
