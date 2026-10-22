from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];errors=[];views=0
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1200,'height':1200},color_scheme='light')
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'visuals/round2.html').as_uri())
    page.wait_for_function('window.pilotState !== undefined')
    assert page.locator('#case option').count()==12
    for i in range(12):
        page.select_option('#case',str(i))
        for option in page.locator('#method option').all():
            page.select_option('#method',option.get_attribute('value'))
            page.locator('#step').evaluate('(e)=>{e.value=e.max;e.dispatchEvent(new Event("input"))}')
            assert page.evaluate('window.pilotState.arrived')==int(page.locator('#agent').get_attribute('max'))+1
            views+=1
    page.select_option('#case','7');page.select_option('#method','Current archive best')
    page.locator('#step').evaluate('(e)=>{e.value=20;e.dispatchEvent(new Event("input"))}')
    page.screenshot(path=str(ROOT/'visuals/round2-preview.png'),full_page=True)
    page.click('#play');page.wait_for_function('window.pilotState.step > 20');page.click('#play')
    page.click('#reset');assert page.evaluate('window.pilotState.step')==0
    page.set_viewport_size({'width':390,'height':844});page.emulate_media(color_scheme='dark')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(ROOT/'visuals/round2-preview-mobile.png'),full_page=True)
    assert not errors,errors
    browser.close()
(ROOT/'research/round2/visual-check.json').write_text(json.dumps({'cases':12,'views':views,'passed':True,'javascript_errors':errors},indent=2)+'\n')
print('PASS',views,'views; endpoints, playback and mobile layout')
