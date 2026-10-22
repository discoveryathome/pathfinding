from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True)
 page=browser.new_page(viewport={'width':1200,'height':1200},color_scheme='light')
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((ROOT/'visuals/pathfinding.html').as_uri());page.wait_for_function('window.pilotState !== undefined')
 assert page.locator('#case option').count()==8
 for i in range(8):
  page.select_option('#case',str(i))
  for option in page.locator('#method option').all():
   page.select_option('#method',option.get_attribute('value'))
   page.locator('#step').evaluate('(e)=>{e.value=e.max;e.dispatchEvent(new Event("input"))}')
   state=page.evaluate('window.pilotState');n=int(page.locator('#agent').get_attribute('max'))+1
   assert state['arrived']==n,(i,state,n)
 page.select_option('#case','5');page.select_option('#method','Selected repair · seed 17')
 page.locator('#step').evaluate('(e)=>{e.value=20;e.dispatchEvent(new Event("input"))}')
 page.locator('#agent').evaluate('(e)=>{e.value=8;e.dispatchEvent(new Event("input"))}')
 assert page.evaluate('window.pilotState.step')==20
 page.screenshot(path=str(ROOT/'visuals/preview.png'),full_page=True)
 page.click('#play');page.wait_for_function('window.pilotState.step > 20');page.click('#play')
 page.click('#reset');assert page.evaluate('window.pilotState.step')==0
 page.set_viewport_size({'width':390,'height':844});page.emulate_media(color_scheme='dark');page.screenshot(path=str(ROOT/'visuals/preview-mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 assert not errors,errors
 browser.close()
(ROOT/'results/visual-check.json').write_text(json.dumps({'cases':8,'plans':32,'all_endpoints_verified_in_view':True,'play_pause_reset_slider':True,'mobile_no_horizontal_overflow':True,'javascript_errors':errors},indent=2)+'\n')
print('PASS: 32 plan views; play/pause, reset, sliders, mobile layout; no JS errors')
