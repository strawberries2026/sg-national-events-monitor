"""Collect public announcement headlines from official Singapore government newsrooms."""
import json, re, urllib.request
from datetime import datetime as dt
from datetime import datetime, timezone, timedelta
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
 collected=[]; errors=[]; successful_sources=[]; announcement_count=0
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
    if len(title)<(15 if name=="PMO" else 35) or len(title)>400 or full in seen:continue
    if not any(word in full.lower() for word in ("/newsroom/","/media-room/","/press-releases/","/speeches/","/news-and-events/")):continue
    if full.rstrip("/")==url.rstrip("/"):continue
    if name=="PMO" and not re.search(r"/newsroom/[^/?#]+/?$",parsed.path):continue
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
   if seen:
    successful_sources.append(name)
    announcement_count+=len(seen)
   else: errors.append(name+": no eligible announcement links found")
  except Exception as e:errors.append(name+": "+str(e)[:160])
 # Extract only future sitting dates explicitly listed on the official Order Paper page.
 try:
  order_url="https://www.parliament.gov.sg/parliamentary-business/order-paper"
  req=urllib.request.Request(order_url,headers={"User-Agent":"SGNationalEventsMonitor/1.0"})
  with urllib.request.urlopen(req,timeout=20) as resp:
   page=resp.read(2_000_000).decode("utf-8","replace")
  class PageText(HTMLParser):
   def __init__(self): super().__init__(); self.parts=[]
   def handle_data(self,data): self.parts.append(data)
  parser=PageText();parser.feed(page)
  content=" ".join(" ".join(parser.parts).split())
  today=(datetime.now(timezone.utc)+timedelta(hours=8)).date()
  future=set()
  for day,month,year in re.findall(r"Sitting on\s+(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})",content,re.I):
   try: sitting=dt.strptime(f"{day} {month} {year}","%d %B %Y").date()
   except ValueError: continue
   if today<=sitting<=today+timedelta(days=180):future.add(sitting)
  for sitting in sorted(future):
   collected.append({"category":"Parliament","agency":"Parliament","title":"Parliament sitting — Order Paper published","source_url":order_url,"type":"Confirmed sitting date (Order Paper)","published_date":None,"date":sitting.isoformat(),"time_sgt":None})
 except Exception as e: errors.append("Parliament Order Paper: "+str(e)[:160])
 # Parliament homepage carries the next sitting announcement, often before an Order Paper exists.
 try:
  home_url="https://www.parliament.gov.sg/"
  req=urllib.request.Request(home_url,headers={"User-Agent":"Mozilla/5.0 (compatible; SGNationalEventsMonitor/1.0)"})
  with urllib.request.urlopen(req,timeout=20) as resp:
   homepage=resp.read(2_000_000).decode("utf-8","replace")
  class HomeText(HTMLParser):
   def __init__(self): super().__init__();self.parts=[];self.skip=0
   def handle_starttag(self,tag,attrs):
    if tag in ("script","style"):self.skip+=1
   def handle_endtag(self,tag):
    if tag in ("script","style") and self.skip:self.skip-=1
   def handle_data(self,data):
    if not self.skip:self.parts.append(data)
  parser=HomeText();parser.feed(homepage)
  content=" ".join(" ".join(parser.parts).split())
  pattern=r"Parliament will be sitting on\\s+(\\d{1,2})\\s+([A-Za-z]+)\\s+(20\\d{2})\\.?(?:\\s+It will commence at\\s+(\\d{1,2})[.:](\\d{2})\\s*(am|pm|noon|midnight)\\.?)?"
  today=(datetime.now(timezone.utc)+timedelta(hours=8)).date()
  for day,month,year,hour,minute,period in re.findall(pattern,content,re.I):
   try:sitting=dt.strptime(f"{day} {month} {year}","%d %B %Y").date()
   except ValueError:continue
   if not(today<=sitting<=today+timedelta(days=180)):continue
   clock=None
   if hour and minute and period:
    h=int(hour)%12
    if period.lower() in ("pm","noon"):h+=12
    clock=f"{h:02d}:{minute}"
   collected.append({"category":"Parliament","agency":"Parliament","title":"Parliament sitting — official homepage announcement","source_url":home_url,"type":"Confirmed sitting date (homepage)","published_date":None,"date":sitting.isoformat(),"time_sgt":clock})
 except Exception as e:errors.append("Parliament homepage: "+str(e)[:160])
 # Preserve the last verified future sitting when Parliament temporarily blocks automated requests.
 today=(datetime.now(timezone.utc)+timedelta(hours=8)).date()
 found_dates={e.get("date") for e in collected if e.get("agency")=="Parliament" and e.get("date")}
 for prior in old.get("events",[]):
  if prior.get("agency")=="Parliament" and prior.get("date") and prior["date"]>=today.isoformat() and prior["date"] not in found_dates:
   collected.append(prior)
 # Remove duplicate Parliament dates while retaining the homepage record if it contains a time.
 sitting_records=[e for e in collected if e.get("agency")=="Parliament" and e.get("date")]
 best={}
 for e in sitting_records:
  date=e["date"]
  if date not in best or (e.get("time_sgt") and not best[date].get("time_sgt")):best[date]=e
 collected=[e for e in collected if not(e.get("agency")=="Parliament" and e.get("date"))]+list(best.values())
 # Parliament references are official resources, not confirmed future sittings.
 parliament_refs = [
  ("Parliament Order Papers and agendas", "https://www.parliament.gov.sg/parliamentary-business/order-paper"),
  ("Parliament sittings and procedures", "https://www.parliament.gov.sg/about-us/parliament-information/sitting-of-parliament"),
 ]
 for title, link in parliament_refs:
  collected.append({"category":"Parliament","agency":"Parliament","title":title,"source_url":link,"type":"Official reference","published_date":None,"date":None,"time_sgt":None})
 if announcement_count==0:
  print("No announcement sources refreshed; preserving existing feed",errors)
  return
 unique={(e["source_url"]+"#"+e["date"] if e.get("date") else e["source_url"]):e for e in collected}
 previous={e.get("source_url") for e in old.get("events",[]) if e.get("source_url")}
 for item in unique.values(): item["is_new"]=bool(previous) and item["source_url"] not in previous
 result={"updated_at":datetime.now(timezone.utc).isoformat(),"events":list(unique.values()),"errors":errors,"source_health":{"successful_sources":successful_sources,"failed_sources":[name for name,_,_ in SOURCES if name not in successful_sources],"successful_count":len(successful_sources),"total_count":len(SOURCES),"announcement_count":announcement_count},"note":"Published announcements only; no future event date inferred."}
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("Saved",len(unique),"announcements",errors)
if __name__=="__main__":main()
