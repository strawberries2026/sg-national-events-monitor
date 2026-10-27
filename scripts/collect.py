"""Collect public announcement headlines from official Singapore government newsrooms."""
import json, re, urllib.request
from datetime import datetime as dt
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

SOURCES = [
 ("MHA", "Ministries", "https://www.mha.gov.sg/media-room/newsroom/"),
 ("MOF", "Ministries", "https://www.mof.gov.sg/news-resources/newsroom/"),
 ("MFA", "Ministries", "https://www.mfa.gov.sg/newsroom/"),
 ("MINDEF", "Ministries", "https://www.mindef.gov.sg/news-and-events/latest-releases/"),
 ("METI", "Ministries", "https://www.meti.gov.sg/newsroom/"),
 ("PMO", "Leadership", "https://www.pmo.gov.sg/newsroom/"),
 ("Istana", "Leadership", "https://www.istana.gov.sg/newsroom/"),
]
class Links(HTMLParser):
 def __init__(self):
  super().__init__(); self.href=None; self.text=[]; self.links=[]
 def handle_starttag(self, tag, attrs):
  if tag=="a": self.href=dict(attrs).get("href"); self.text=[]
 def handle_data(self, data):
  if self.href is not None: self.text.append(data)
 def handle_endtag(self,tag):
  if tag=="a" and self.href:
   self.links.append((" ".join(" ".join(self.text).split()),self.href))
   self.href=None;self.text=[]
def main():
 path=Path("data/events.json")
 old=json.loads(path.read_text()) if path.exists() else {}
 collected=[]; errors=[]
 for name,cat,url in SOURCES:
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"SGNationalEventsMonitor/1.0 (public announcements; GitHub Actions)"})
   with urllib.request.urlopen(req,timeout=20) as resp:
    html=resp.read(2_000_000).decode("utf-8","replace")
   p=Links();p.feed(html);seen=set()
   for title,href in p.links:
    full=urljoin(url,href)
    parsed=urlparse(full)
    if parsed.scheme!="https" or parsed.netloc not in ("www.mha.gov.sg","mha.gov.sg","www.mof.gov.sg","mof.gov.sg","www.mfa.gov.sg","mfa.gov.sg","www.mindef.gov.sg","mindef.gov.sg","www.meti.gov.sg","meti.gov.sg","www.pmo.gov.sg","pmo.gov.sg","www.istana.gov.sg","istana.gov.sg"):continue
    if len(title)<35 or len(title)>260 or full in seen:continue
    if not any(word in full.lower() for word in ("/newsroom/","/media-room/","/press-releases/","/speeches/","/news-and-events/")):continue
    if full.rstrip("/")==url.rstrip("/"):continue
    seen.add(full)
    match=re.match(r"^\s*(\d{1,2}\s+[A-Za-z]+\s+20\d{2})(?:\s+\1)?\s+",title)
    published=None
    if match:
     try: published=dt.strptime(match.group(1),"%d %B %Y").date().isoformat()
     except ValueError: pass
     title=title[match.end():].strip()
    title=re.sub(r"\s+(Speeches|Press Releases|News Releases|Statements)\s*$","",title).strip()
    collected.append({"category":cat,"agency":name,"title":title,"source_url":full,"type":"Published announcement","published_date":published,"date":None,"time_sgt":None})
    if len(seen)>=35:break
  except Exception as e:errors.append(name+": "+str(e)[:160])
 if not collected:
  print("No validated links collected; preserving existing feed",errors)
  return
 unique={e["source_url"]:e for e in collected}
 previous={e.get("source_url") for e in old.get("events",[]) if e.get("source_url")}
 for item in unique.values(): item["is_new"]=bool(previous) and item["source_url"] not in previous
 result={"updated_at":datetime.now(timezone.utc).isoformat(),"events":list(unique.values()),"errors":errors,"note":"Published announcements only; no future event date inferred."}
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("Saved",len(unique),"announcements",errors)
if __name__=="__main__":main()
