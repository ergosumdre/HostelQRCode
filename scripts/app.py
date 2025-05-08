import gradio as gr
import time
import pandas as pd
import re
import qrcode
from PIL import Image
from gradio.inputs import Image as PyPNGImage
from PIL import Image
import ftplib
from io import BytesIO
import random
import string
import datetime
import pytz
import paramiko
import sys
import shutil



# Linux Path
guest_list_path = "/home/ubuntu/qrCode/v2/data/cleaned_guest_list.csv"
door_codes_path = "/home/ubuntu/qrCode/data/doorCodes.csv"
qrCode_path = "/home/ubuntu/qrCode/v2/data/qrCode.png"
checkin_html_path = "/home/ubuntu/qrCode/v2/data/checkin_details.html"
activity_logs_path = "/home/ubuntu/qrCode/v2/data/activity_logs.txt"


def GuestCodes(guest_list_path, door_codes_path):
    doorCodes = pd.read_csv(door_codes_path, dtype={'Passcode': str})
    df = pd.read_csv(guest_list_path)
    df = df.rename(columns={'room_number': 'bed_number'})
    df['room_number'] = df['bed_number'].str[:-2]
    doorCodes = doorCodes.rename(columns={'Room': 'room_number', 'Passcode': 'access_code'})
    doorCodes['room_number'] = doorCodes['room_number'].astype(str)
    df['room_number'] = df['room_number'].astype(str)
    df = pd.merge(df, doorCodes, on='room_number')
    return df

def getCurrentGuest(masterlist, bed_number):
    df = masterlist
    filtered_df = df[df['bed_number'].str.contains(bed_number)]
    if filtered_df['bed_number'].duplicated().any():
        # there are two of the same bed_number, filter on check_out_date
        est = pytz.timezone('US/Eastern')
        current_date = datetime.datetime.now(est).strftime('%Y-%m-%d %H:%M:%S')
        filtered_df = filtered_df[(pd.to_datetime(filtered_df['check_in_date']) <= current_date) & (pd.to_datetime(filtered_df['check_out_date']) >= current_date)]
        return filtered_df
    return filtered_df


def getGuestDetails(currentGuest):
    name = currentGuest['Customer'].values[0]
    room = currentGuest['room_number'].values[0]
    bed_number = currentGuest['bed_number'].str[-1:].values[0]
    room_code = currentGuest['access_code'].values[0]
    bed_locker = currentGuest['bed_number'].str[-1:].values[0]
    checkoutDate = currentGuest['check_out_date'].values[0]
    checkoutDate = datetime.datetime.strptime(checkoutDate, "%Y-%m-%d %H:%M:%S")
    checkoutDate = checkoutDate.strftime("%m/%d/%Y")
    balance = currentGuest['Balance including preauthorizations'].values[0]
    return name, room, room_code, bed_number, checkoutDate, balance

def generate_html(guest_name, room, room_code, bed_locker, leave_date):
    html = """

<html lang="en">
   <head>
           <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
    new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    }})(window,document,'script','dataLayer','GTM-WCJ6MM4');</script>
    <!-- End Google Tag Manager -->
      <title>"Nap York Checkin Details</title>
      <meta charset="utf-8">
      <meta name="robots" content="noindex">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <meta name="color-scheme" content="light only">
      <meta name="description" content="Nap York Checkin Details">
      <meta property="og:site_name" content="Nap York Checkin Details">
      <meta property="og:title" content="Nap York Checkin Details">
      <meta property="og:type" content="website">
      <meta property="og:description" content="Nap York Checkin Details">
      <meta property="og:image:type" content="image/jpeg">
      <meta property="og:image:width" content="1280">
      <meta property="og:image:height" content="800">
      <meta property="twitter:card" content="summary_large_image">
      <link href="https://fonts.googleapis.com/css2?display=swap&amp;family=Lexend:ital,wght@0,400;1,400&amp;family=Inter:ital,wght@0,400;1,400" rel="stylesheet" type="text/css">
      <style>a,abbr,acronym,address,applet,article,aside,audio,b,big,blockquote,body,canvas,caption,center,cite,code,dd,del,details,dfn,div,dl,dt,em,embed,fieldset,figcaption,figure,footer,form,h1,h2,h3,h4,h5,h6,header,hgroup,html,i,iframe,img,ins,kbd,label,legend,li,mark,menu,nav,object,ol,output,p,pre,q,ruby,s,samp,section,small,span,strike,strong,sub,summary,sup,table,tbody,td,tfoot,th,thead,time,tr,tt,u,ul,var,video{{margin:0;padding:0;border:0;font-size:100%;font:inherit;vertical-align:baseline}}article,aside,details,figcaption,figure,footer,header,hgroup,menu,nav,section{{display:block}}body{{line-height:1}}ol,ul{{list-style:none}}blockquote,q{{quotes:none}}blockquote:after,blockquote:before,q:after,q:before{{content:'';content:none}}table{{border-collapse:collapse;border-spacing:0}}body{{-webkit-text-size-adjust:none}}mark{{background-color:transparent;color:inherit}}input::-moz-focus-inner{{border:0;padding:0}}input[type=email],input[type=text],select,textarea{{-moz-appearance:none;-webkit-appearance:none;-ms-appearance:none;appearance:none}}*,:after,:before{{box-sizing:border-box}}body{{line-height:1;min-height:var(--viewport-height);min-width:320px;overflow-x:hidden;word-wrap:break-word}}body:before{{content:'';display:block;background-attachment:scroll;height:var(--background-height);left:0;pointer-events:none;position:fixed;top:0;transform:scale(1);width:100vw;z-index:0;background-image:url('data:image/svg+xml;charset=utf8,%3Csvg%20viewBox%3D%220%200%20512%20512%22%20width%3D%22512%22%20height%3D%22512%22%20version%3D%221.1%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%20%3Cfilter%20id%3D%22noise%22%3E%20%3CfeTurbulence%20type%3D%22fractalNoise%22%20baseFrequency%3D%220.875%22%20result%3D%22noise%22%20%2F%3E%20%3CfeColorMatrix%20type%3D%22matrix%22%20values%3D%220.046875%200%200%200%200%200%200.07421875%200%200%200%200%200%200.109375%200%200%200%200%200%200.33984375%200%22%20%2F%3E%20%3C%2Ffilter%3E%20%3Crect%20filter%3D%22url%28%23noise%29%22%20x%3D%220%22%20y%3D%220%22%20width%3D%22512%22%20height%3D%22512%22%20fill%3D%22transparent%22%20opacity%3D%221%22%20%2F%3E%3C%2Fsvg%3E'),radial-gradient(79% 150% at 29% 100%,#419144 83%,rgba(0,0,0,.69) 68%,rgba(0,0,0,.541) 100%),url(assets/images/bg.jpg?v=40546d14);background-size:512px,cover,cover;background-position:center,0 0,center;background-repeat:repeat,repeat,no-repeat;background-color:#fff}}body:after{{background-color:#44436e;content:'';display:block;height:100%;left:0;opacity:0;pointer-events:none;position:fixed;top:0;transform:scale(1);transition:opacity 2s ease-in-out 0s,visibility 2s 0s;visibility:hidden;width:100%;z-index:1}}body.is-loading:after{{opacity:1;visibility:visible}}:root{{--background-height:100vh;--site-language-alignment:left;--site-language-direction:ltr;--site-language-flex-alignment:flex-start;--site-language-indent-left:1;--site-language-indent-right:0;--viewport-height:100vh}}html{{font-size:15pt}}u{{text-decoration:underline}}strong{{color:inherit;font-weight:bolder}}em{{font-style:italic}}code{{background-color:rgba(144,144,144,.25);border-radius:.25em;font-family:'Lucida Console','Courier New',monospace;font-size:.9em;font-weight:400;letter-spacing:0;margin:0 .25em;padding:.25em .5em;text-indent:0}}mark{{background-color:rgba(144,144,144,.25)}}spoiler-text{{-webkit-text-stroke:0;background-color:rgba(32,32,32,.75);text-shadow:none;text-stroke:0;color:transparent;cursor:pointer;transition:color .1s ease-in-out}}spoiler-text.active{{color:#fff;cursor:text}}s{{text-decoration:line-through}}sub{{font-size:smaller;vertical-align:sub}}sup{{font-size:smaller;vertical-align:super}}a{{color:inherit;text-decoration:underline;transition:color .25s ease}}#wrapper{{-webkit-overflow-scrolling:touch;align-items:flex-start;display:flex;flex-direction:column;justify-content:center;min-height:var(--viewport-height);overflow:hidden;position:relative;z-index:2}}#main{{--alignment:var(--site-language-alignment);--flex-alignment:var(--site-language-flex-alignment);--indent-left:var(--site-language-indent-left);--indent-right:var(--site-language-indent-right);--border-radius-tl:0;--border-radius-tr:0;--border-radius-br:0;--border-radius-bl:0;align-items:center;display:flex;flex-grow:0;flex-shrink:0;justify-content:center;max-width:100%;position:relative;text-align:var(--alignment);z-index:1}}#main>.inner{{--padding-horizontal:3rem;--padding-vertical:3rem;--spacing:1.5rem;--width:35rem;border-radius:var(--border-radius-tl) var(--border-radius-tr) var(--border-radius-br) var(--border-radius-bl);max-width:100%;position:relative;width:var(--width);z-index:1;padding:var(--padding-vertical) var(--padding-horizontal)}}#main>.inner>*{{margin-top:var(--spacing);margin-bottom:var(--spacing)}}#main>.inner>:first-child{{margin-top:0!important}}#main>.inner>:last-child{{margin-bottom:0!important}}#main>.inner>.full{{margin-left:calc(var(--padding-horizontal) * -1);max-width:calc(100% + calc(var(--padding-horizontal) * 2) + .4725px);width:calc(100% + calc(var(--padding-horizontal) * 2) + .4725px)}}#main>.inner>.full:first-child{{border-top-left-radius:inherit;border-top-right-radius:inherit;margin-top:calc(var(--padding-vertical) * -1)!important}}#main>.inner>.full:last-child{{border-bottom-left-radius:inherit;border-bottom-right-radius:inherit;margin-bottom:calc(var(--padding-vertical) * -1)!important}}#main>.inner>.full.screen{{border-radius:0!important;max-width:100vw;position:relative;width:100vw;left:0;margin-left:calc(var(--padding-horizontal) * -1);right:auto}}body.is-instant #main,body.is-instant #main>.inner>*,body.is-instant #main>.inner>section>*{{transition:none!important}}body.is-instant:after{{display:none!important;transition:none!important}}.image{{display:block;line-height:0;max-width:100%;position:relative}}.image .frame{{-webkit-backface-visibility:hidden;-webkit-transform:translate3d(0,0,0);display:inline-block;max-width:100%;overflow:hidden;vertical-align:top;width:100%}}.image .frame img{{border-radius:0!important;max-width:100%;vertical-align:top;width:inherit}}.image.full .frame{{display:block}}.image.full:first-child .frame{{border-top-left-radius:inherit;border-top-right-radius:inherit}}.image.full:last-child .frame{{border-bottom-left-radius:inherit;border-bottom-right-radius:inherit}}#image01 .frame{{width:5.5rem;border-radius:100%;border-color:#419144;border-style:solid;border-width:2px;transition:none}}#image01 img{{border-radius:inherit!important;padding:.25rem}}#image01 .frame img{{transition:none}}h1,h2,h3,p{{direction:var(--site-language-direction);position:relative}}h1 span.p,h2 span.p,h3 span.p,p span.p{{display:block;position:relative}}h1 a,h1 code,h1 mark,h1 span[style],h1 spoiler-text,h1 strong,h2 a,h2 code,h2 mark,h2 span[style],h2 spoiler-text,h2 strong,h3 a,h3 code,h3 mark,h3 span[style],h3 spoiler-text,h3 strong,p a,p code,p mark,p span[style],p spoiler-text,p strong{{-webkit-text-fill-color:currentcolor}}#text02{{color:#fff;font-family:Lexend,sans-serif;font-size:3.5em;line-height:1.125;font-weight:400}}#text02 a{{text-decoration:underline}}#text02 a:hover{{text-decoration:none}}#text02 span.p:nth-child(n+2){{margin-top:1rem}}#text03{{color:rgba(255,255,255,.588);font-family:Inter,sans-serif;font-size:1em;line-height:1.75;font-weight:400}}#text03 strong{{color:#fff}}#text03 a{{color:#aa94ff;text-decoration:underline}}#text03 a:hover{{color:#d9cfff}}#text03 span.p:nth-child(n+2){{margin-top:1rem}}#text01{{color:rgba(255,255,255,.588);font-family:Inter,sans-serif;font-size:1em;line-height:1.75;font-weight:400}}#text01 strong{{color:#fff}}#text01 a{{color:#aa94ff;text-decoration:underline}}#text01 a:hover{{color:#d9cfff}}#text01 span.p:nth-child(n+2){{margin-top:1rem}}hr{{border:0;padding:0;position:relative;width:100%}}hr:before{{content:'';display:inline-block;max-width:100%;vertical-align:middle}}hr.style1:not(:first-child){{margin-top:2rem!important}}hr.style1:not(:last-child){{margin-bottom:2rem!important}}hr.style1:before{{width:100%;border-top:solid 2px rgba(255,255,255,.031);height:2px;margin-top:-1px}}.icons{{display:flex;flex-wrap:wrap;justify-content:var(--flex-alignment);letter-spacing:0;padding:0}}.icons li{{position:relative;z-index:1}}.icons li a{{align-items:center;display:flex;justify-content:center}}.icons li a svg{{display:block;position:relative}}.icons li a+svg{{display:block;height:100%;left:0;pointer-events:none;position:absolute;top:0;width:100%;z-index:-1}}.icons li a .label{{display:none}}#icons01{{justify-content:center;font-size:2.875em;gap:.75rem}}#icons01 li a{{border-radius:.875rem;height:1em;width:1em;transition:color .25s ease,background-color .25s ease,border-color .25s ease}}#icons01 li a svg{{height:100%;width:100%;transition:fill .25s ease}}#icons01 a svg{{fill:rgba(255,255,255,.588)}}#icons01 li a+svg{{transition:fill .25s ease,stroke .25s ease}}.buttons{{cursor:default;display:flex;justify-content:var(--flex-alignment);letter-spacing:0;padding:0}}.buttons li{{max-width:100%}}.buttons li a{{align-items:center;justify-content:center;max-width:100%;text-align:center;text-decoration:none;vertical-align:middle;white-space:nowrap}}#buttons02{{gap:.75rem;flex-direction:row;flex-wrap:wrap}}#buttons02 li a{{display:inline-flex;width:20.625rem;height:4rem;line-height:4rem;padding:0 .5rem;vertical-align:middle;font-family:Inter,sans-serif;font-size:1em;font-weight:400;border-radius:.875rem;transition:color .25s ease,background-color .25s ease,border-color .25s ease}}#buttons02 li a svg{{display:block;fill:#fff;flex-grow:0;flex-shrink:0;height:100%;min-width:16px;width:1em;margin-left:-.125em;margin-right:calc(.5em + 0rem);transition:fill .25s ease}}#buttons02 li a .label{{direction:var(--site-language-direction);overflow:hidden}}#buttons02 .button{{color:#fff;border:solid 2px #419144}}#buttons01{{gap:.75rem;flex-direction:row;flex-wrap:wrap}}#buttons01 li a{{display:inline-flex;width:20.625rem;height:4rem;line-height:4rem;padding:0 .5rem;vertical-align:middle;font-family:Inter,sans-serif;font-size:1em;font-weight:400;border-radius:.875rem;transition:color .25s ease,background-color .25s ease,border-color .25s ease}}#buttons01 li a svg{{display:block;fill:#fff;flex-grow:0;flex-shrink:0;height:100%;min-width:16px;width:1em;margin-left:-.125em;margin-right:calc(.5em + 0rem);transition:fill .25s ease}}#buttons01 li a .label{{direction:var(--site-language-direction);overflow:hidden}}#buttons01 .button{{color:#fff;border:solid 2px #419144}}.container{{position:relative}}.container>.wrapper{{vertical-align:top;position:relative;max-width:100%;border-radius:inherit}}.container>.wrapper>.inner{{vertical-align:top;position:relative;max-width:100%;border-radius:inherit;text-align:var(--alignment)}}#main .container.full:first-child>.wrapper{{border-top-left-radius:inherit;border-top-right-radius:inherit}}#main .container.full:last-child>.wrapper{{border-bottom-left-radius:inherit;border-bottom-right-radius:inherit}}#main .container.full:first-child>.wrapper>.inner{{border-top-left-radius:inherit;border-top-right-radius:inherit}}#main .container.full:last-child>.wrapper>.inner{{border-bottom-left-radius:inherit;border-bottom-right-radius:inherit}}#container01{{display:flex;width:100%;align-items:center;justify-content:flex-start;background-image:url('data:image/svg+xml;charset=utf8,%3Csvg%20viewBox%3D%220%200%20512%20512%22%20width%3D%22512%22%20height%3D%22512%22%20version%3D%221.1%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%20%3Cfilter%20id%3D%22noise%22%3E%20%3CfeTurbulence%20type%3D%22fractalNoise%22%20baseFrequency%3D%220.875%22%20result%3D%22noise%22%20%2F%3E%20%3CfeColorMatrix%20type%3D%22matrix%22%20values%3D%220.1015625%200%200%200%200%200%200.09375%200%200%200%200%200%200.12890625%200%200%200%200%200%200.56640625%200%22%20%2F%3E%20%3C%2Ffilter%3E%20%3Crect%20filter%3D%22url%28%23noise%29%22%20x%3D%220%22%20y%3D%220%22%20width%3D%22512%22%20height%3D%22512%22%20fill%3D%22transparent%22%20opacity%3D%221%22%20%2F%3E%3C%2Fsvg%3E'),linear-gradient(296deg,#000 32%,#303342 100%);background-size:512px,cover;background-position:center,0 0;background-repeat:repeat,repeat;box-shadow:0 4.25rem 6.75rem 1.125rem rgba(48,51,66,.49);border-radius:2rem}}#container01>.wrapper>.inner{{--gutters:2rem;--padding-horizontal:3.5rem;--padding-vertical:4rem;padding:var(--padding-vertical) var(--padding-horizontal)}}#container01>.wrapper{{max-width:var(--width);width:100%}}#container01.default>.wrapper>.inner>*{{margin-bottom:var(--spacing);margin-top:var(--spacing)}}#container01.default>.wrapper>.inner>:first-child{{margin-top:0!important}}#container01.default>.wrapper>.inner>:last-child{{margin-bottom:0!important}}#container01.columns>.wrapper>.inner{{flex-wrap:wrap;display:flex;align-items:flex-start}}#container01.columns>.wrapper>.inner>*{{flex-grow:0;flex-shrink:0;max-width:100%;text-align:var(--alignment);padding:0 0 0 var(--gutters)}}#container01.columns>.wrapper>.inner>*>*{{margin-bottom:var(--spacing);margin-top:var(--spacing)}}#container01.columns>.wrapper>.inner>*>:first-child{{margin-top:0!important}}#container01.columns>.wrapper>.inner>*>:last-child{{margin-bottom:0!important}}#container01.columns>.wrapper>.inner>:first-child{{margin-left:calc(var(--gutters) * -1)}}#container01.default>.wrapper>.inner>.full{{margin-left:calc(var(--padding-horizontal) * -1);max-width:none!important;width:calc(100% + (var(--padding-horizontal) * 2) + .4725px)}}#container01.default>.wrapper>.inner>.full:first-child{{margin-top:calc(var(--padding-vertical) * -1)!important;border-top-left-radius:inherit;border-top-right-radius:inherit}}#container01.default>.wrapper>.inner>.full:last-child{{margin-bottom:calc(var(--padding-vertical) * -1)!important;border-bottom-left-radius:inherit;border-bottom-right-radius:inherit}}#container01.columns>.wrapper>.inner>div>.full{{margin-left:calc(var(--gutters) * -.5);max-width:none!important;width:calc(100% + var(--gutters) + .4725px)}}#container01.columns>.wrapper>.inner>div:first-child>.full{{margin-left:calc(var(--padding-horizontal) * -1);width:calc(100% + var(--padding-horizontal) + calc(var(--gutters) * .5) + .4725px)}}#container01.columns>.wrapper>.inner>div:last-child>.full{{width:calc(100% + var(--padding-horizontal) + calc(var(--gutters) * .5) + .4725px)}}#container01.columns>.wrapper>.inner>div>.full:first-child{{margin-top:calc(var(--padding-vertical) * -1)!important}}#container01.columns>.wrapper>.inner>div>.full:last-child{{margin-bottom:calc(var(--padding-vertical) * -1)!important}}#container01.columns>.wrapper>.inner>div:first-child,#container01.columns>.wrapper>.inner>div:first-child>.full:first-child{{border-top-left-radius:inherit}}#container01.columns>.wrapper>.inner>div:last-child,#container01.columns>.wrapper>.inner>div:last-child>.full:first-child{{border-top-right-radius:inherit}}#container01.columns>.wrapper>.inner>.full{{align-self:stretch}}#container01.columns>.wrapper>.inner>.full:first-child{{border-bottom-left-radius:inherit;border-top-left-radius:inherit}}#container01.columns>.wrapper>.inner>.full:last-child{{border-bottom-right-radius:inherit;border-top-right-radius:inherit}}#container01.columns>.wrapper>.inner>.full>.full:first-child:last-child{{border-radius:inherit;height:calc(100% + (var(--padding-vertical) * 2))}}#container01.columns>.wrapper>.inner>.full>.full:first-child:last-child>*{{border-radius:inherit;height:100%;position:absolute;width:100%}}.icc-credits{{display:block;opacity:1!important;position:relative;transition-delay:0s!important}}.icc-credits span{{border-radius:24px;cursor:pointer;display:inline-block;font-family:Arial,sans-serif;font-size:12px;letter-spacing:0;line-height:1;position:relative;text-decoration:none;width:auto}}.icc-credits span a{{display:inline-block;padding:.5em .375em;position:relative;text-decoration:none;transition:color .25s ease,transform .25s ease;z-index:1}}.icc-credits span a:before{{content:'( ';opacity:1;transition:opacity .25s ease}}.icc-credits span a:after{{content:' )';opacity:1;transition:opacity .25s ease}}.icc-credits span::after{{background-image:linear-gradient(30deg,#a464a1 15%,#3b5dad 85%);border-radius:inherit;box-shadow:0 .25em 1.25em 0 rgba(0,0,0,.25);content:'';display:block;height:calc(100% + 2px);left:-1px;opacity:0;pointer-events:none;position:absolute;top:-1px;transition:opacity .25s ease,box-shadow .25s ease,transform .25s ease;width:calc(100% + 2px)}}.icc-credits span:hover{{text-transform:none!important}}.icc-credits span:hover a{{color:#fff!important;transform:scale(1.1) translateY(-.05rem)}}.icc-credits span:hover a:before{{opacity:0}}.icc-credits span:hover a:after{{opacity:0}}.icc-credits span:hover::after{{opacity:1;transform:scale(1.1) translateY(-.05rem)}}#credits span{{background-color:rgba(80,80,80,.5);color:rgba(224,224,224,.75);margin-top:1.5rem!important}}#credits span a:before{{opacity:0}}#credits span a:after{{opacity:0}}@media (max-width:1680px){{html{{font-size:11pt}}}}@media (max-width:1280px){{html{{font-size:11pt}}}}@media (max-width:980px){{html{{font-size:9pt}}}}@media (max-width:736px){{html{{font-size:13pt}}#main>.inner{{--padding-horizontal:1rem;--padding-vertical:1rem;--spacing:1.5rem}}#image01 .frame{{width:5.5rem}}#text02{{letter-spacing:0;width:100%;font-size:2.5em;line-height:1.125}}#text03{{letter-spacing:0;width:100%;font-size:1em;line-height:1.75}}#text01{{letter-spacing:0;width:100%;font-size:1em;line-height:1.75}}hr.style1:not(:first-child){{margin-top:1.5rem!important}}hr.style1:not(:last-child){{margin-bottom:1.5rem!important}}#icons01{{font-size:2.875em;gap:.75rem}}#buttons02{{gap:.75rem}}#buttons02 li a{{letter-spacing:0;font-size:1em}}#buttons02 li a svg{{width:1em}}#buttons01{{gap:.75rem}}#buttons01 li a{{letter-spacing:0;font-size:1em}}#buttons01 li a svg{{width:1em}}#container01{{--alignment:center;--flex-alignment:center;--indent-left:1;--indent-right:1}}#container01>.wrapper>.inner{{--gutters:2rem;--padding-horizontal:2rem;--padding-vertical:3rem}}#container01.columns>.wrapper>.inner{{flex-direction:column!important;flex-wrap:nowrap!important}}#container01.columns>.wrapper>.inner>span{{height:0;margin-top:calc(var(--gutters) * -1);pointer-events:none;visibility:hidden}}#container01.columns>.wrapper>.inner>:first-child{{margin-left:0!important;padding-top:0!important}}#container01.columns>.wrapper>.inner>*{{padding:calc(var(--gutters) * .5) 0!important}}#container01.columns>.wrapper>.inner>:last-child{{padding-bottom:0!important}}#container01.columns>.wrapper>.inner>div>.full{{margin-left:calc(var(--padding-horizontal) * -1);width:calc(100% + (var(--padding-horizontal) * 2) + .4725px)}}#container01.columns>.wrapper>.inner>div:first-of-type>.full{{margin-left:calc(var(--padding-horizontal) * -1);width:calc(100% + (var(--padding-horizontal) * 2) + .4725px)}}#container01.columns>.wrapper>.inner>div:last-of-type>.full{{margin-left:calc(var(--padding-horizontal) * -1);width:calc(100% + (var(--padding-horizontal) * 2) + .4725px)}}#container01.columns>.wrapper>.inner>div>.full:first-child{{margin-top:calc(var(--gutters) * -.5)!important}}#container01.columns>.wrapper>.inner>div>.full:last-child{{margin-bottom:calc(var(--gutters) * -.5)!important}}#container01.columns>.wrapper>.inner>div:first-of-type>.full:first-child{{margin-top:calc(var(--padding-vertical) * -1)!important}}#container01.columns>.wrapper>.inner>div:last-of-type>.full:last-child{{margin-bottom:calc(var(--padding-vertical) * -1)!important}}#container01.columns>.wrapper>.inner>div:first-of-type,#container01.columns>.wrapper>.inner>div:first-of-type>.full:first-child{{border-top-left-radius:inherit;border-top-right-radius:inherit}}#container01.columns>.wrapper>.inner>div:last-of-type,#container01.columns>.wrapper>.inner>div:last-of-type>.full:last-child{{border-bottom-left-radius:inherit;border-bottom-right-radius:inherit}}#container01.columns>.wrapper>.inner>div:first-of-type,#container01.columns>.wrapper>.inner>div:first-of-type>.full:last-child{{border-bottom-left-radius:0!important}}#container01.columns>.wrapper>.inner>div:last-of-type,#container01.columns>.wrapper>.inner>div:last-of-type>.full:first-child{{border-top-right-radius:0!important}}#container01.columns>.wrapper>.inner>.full>.full:first-child:last-child{{height:auto}}#container01.columns>.wrapper>.inner>.full>.full:first-child:last-child>*{{height:auto;position:relative;width:auto}}}}@media (max-width:480px){{#main>.inner{{--spacing:1.3125rem}}#buttons02{{flex-direction:column;flex-wrap:nowrap}}#buttons02 li a{{max-width:32rem;width:100%}}#buttons01{{flex-direction:column;flex-wrap:nowrap}}#buttons01 li a{{max-width:32rem;width:100%}}}}@media (max-width:360px){{#main>.inner{{--padding-horizontal:0.75rem;--padding-vertical:0.75rem;--spacing:1.125rem}}#text02{{font-size:2.5em}}#text03{{font-size:1em}}#text01{{font-size:1em}}#icons01{{gap:.5625rem}}#buttons02{{gap:.5625rem}}#buttons01{{gap:.5625rem}}#container01>.wrapper>.inner{{--gutters:1.5rem;--padding-horizontal:1.5rem;--padding-vertical:2.25rem}}}}</style>
      <noscript>
         <style>body{{overflow:auto!important}}body:after{{display:none!important}}#main>.inner{{opacity:1!important}}</style>
      </noscript>
      <style></style>
   </head>
   <body class="is-ready" data-new-gr-c-s-check-loaded="14.1111.0" data-gr-ext-installed="">
   <!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
      <svg xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 40 40" display="none" width="0" height="0">
         <symbol id="icon-85976685de3e4af37529a1ce5d57d2a7" viewBox="0 0 40 40">
            <path d="M20,7c4.2,0,4.7,0,6.3,0.1c1.5,0.1,2.3,0.3,3,0.5C30,8,30.5,8.3,31.1,8.9c0.5,0.5,0.9,1.1,1.2,1.8c0.2,0.5,0.5,1.4,0.5,3 C33,15.3,33,15.8,33,20s0,4.7-0.1,6.3c-0.1,1.5-0.3,2.3-0.5,3c-0.3,0.7-0.6,1.2-1.2,1.8c-0.5,0.5-1.1,0.9-1.8,1.2 c-0.5,0.2-1.4,0.5-3,0.5C24.7,33,24.2,33,20,33s-4.7,0-6.3-0.1c-1.5-0.1-2.3-0.3-3-0.5C10,32,9.5,31.7,8.9,31.1 C8.4,30.6,8,30,7.7,29.3c-0.2-0.5-0.5-1.4-0.5-3C7,24.7,7,24.2,7,20s0-4.7,0.1-6.3c0.1-1.5,0.3-2.3,0.5-3C8,10,8.3,9.5,8.9,8.9 C9.4,8.4,10,8,10.7,7.7c0.5-0.2,1.4-0.5,3-0.5C15.3,7.1,15.8,7,20,7z M20,4.3c-4.3,0-4.8,0-6.5,0.1c-1.6,0-2.8,0.3-3.8,0.7 C8.7,5.5,7.8,6,6.9,6.9C6,7.8,5.5,8.7,5.1,9.7c-0.4,1-0.6,2.1-0.7,3.8c-0.1,1.7-0.1,2.2-0.1,6.5s0,4.8,0.1,6.5 c0,1.6,0.3,2.8,0.7,3.8c0.4,1,0.9,1.9,1.8,2.8c0.9,0.9,1.7,1.4,2.8,1.8c1,0.4,2.1,0.6,3.8,0.7c1.6,0.1,2.2,0.1,6.5,0.1 s4.8,0,6.5-0.1c1.6-0.1,2.9-0.3,3.8-0.7c1-0.4,1.9-0.9,2.8-1.8c0.9-0.9,1.4-1.7,1.8-2.8c0.4-1,0.6-2.1,0.7-3.8 c0.1-1.6,0.1-2.2,0.1-6.5s0-4.8-0.1-6.5c-0.1-1.6-0.3-2.9-0.7-3.8c-0.4-1-0.9-1.9-1.8-2.8c-0.9-0.9-1.7-1.4-2.8-1.8 c-1-0.4-2.1-0.6-3.8-0.7C24.8,4.3,24.3,4.3,20,4.3L20,4.3L20,4.3z"></path>
            <path d="M20,11.9c-4.5,0-8.1,3.7-8.1,8.1s3.7,8.1,8.1,8.1s8.1-3.7,8.1-8.1S24.5,11.9,20,11.9z M20,25.2c-2.9,0-5.2-2.3-5.2-5.2 s2.3-5.2,5.2-5.2s5.2,2.3,5.2,5.2S22.9,25.2,20,25.2z"></path>
            <path d="M30.6,11.6c0,1-0.8,1.9-1.9,1.9c-1,0-1.9-0.8-1.9-1.9s0.8-1.9,1.9-1.9C29.8,9.7,30.6,10.5,30.6,11.6z"></path>
         </symbol>
         <symbol id="icon-0c4db87eff374f0f1ef47f8f043f0132" viewBox="0 0 40 40">
            <path d="M36.3,10.2c-1,1.3-2.1,2.5-3.4,3.5c0,0.2,0,0.4,0,1c0,1.7-0.2,3.6-0.9,5.3c-0.6,1.7-1.2,3.5-2.4,5.1 c-1.1,1.5-2.3,3.1-3.7,4.3c-1.4,1.2-3.3,2.3-5.3,3c-2.1,0.8-4.2,1.2-6.6,1.2c-3.6,0-7-1-10.2-3c0.4,0,1.1,0.1,1.5,0.1 c3.1,0,5.9-1,8.2-2.9c-1.4,0-2.7-0.4-3.8-1.3c-1.2-1-1.9-2-2.2-3.3c0.4,0.1,1,0.1,1.2,0.1c0.6,0,1.2-0.1,1.7-0.2 c-1.4-0.3-2.7-1.1-3.7-2.3s-1.4-2.6-1.4-4.2v-0.1c1,0.6,2,0.9,3,0.9c-1-0.6-1.5-1.3-2.2-2.4c-0.6-1-0.9-2.1-0.9-3.3s0.3-2.3,1-3.4 c1.5,2.1,3.6,3.6,6,4.9s4.9,2,7.6,2.1c-0.1-0.6-0.1-1.1-0.1-1.4c0-1.8,0.8-3.5,2-4.7c1.2-1.2,2.9-2,4.7-2c2,0,3.6,0.8,4.8,2.1 c1.4-0.3,2.9-0.9,4.2-1.5c-0.4,1.5-1.4,2.7-2.9,3.6C33.8,11.2,35.1,10.9,36.3,10.2L36.3,10.2z"></path>
         </symbol>
         <symbol id="icon-a1eb5cac0cee3b05a40d856c98ce14a5" viewBox="0 0 40 40">
            <path d="M27.2,4.7v4.9h-2.9c-1.1,0-1.8,0.2-2.1,0.6c-0.4,0.5-0.6,1.1-0.6,2v3.5H27l-0.7,5.4h-4.7v14H16v-14h-4.7v-5.4H16v-4.1 c0-2.3,0.6-4.1,1.9-5.3s2.9-1.9,5.2-1.9C24.8,4.4,26.2,4.5,27.2,4.7L27.2,4.7z"></path>
         </symbol>
         <symbol id="icon-021973a1bb185878b41e1ef48ed6bbaa" viewBox="0 0 40 40">
            <path d="M35.7,13c-1.6-2-3.8-3.5-6.5-4.7c-2.8-1.1-5.8-1.7-9-1.7c-2.4,0-4.8,0.3-7,1C10.9,8.2,9,9.2,7.4,10.3 c-1.6,1.2-2.9,2.5-3.8,4.1c-1,1.6-1.4,3.3-1.4,5c0,2,0.6,3.9,1.8,5.7c1.2,1.8,2.9,3.2,5,4.4c-0.1,0.5-0.3,1-0.5,1.5 c-0.2,0.5-0.4,0.9-0.5,1.2c-0.2,0.3-0.4,0.7-0.7,1c-0.3,0.4-0.5,0.6-0.6,0.8c-0.1,0.2-0.4,0.4-0.7,0.8c-0.3,0.4-0.5,0.6-0.6,0.7 c0,0-0.1,0.1-0.2,0.2C5,35.8,5,35.8,5,35.8L4.8,36c-0.1,0.1-0.1,0.2-0.1,0.2c0,0,0,0.1,0,0.2c0,0.1,0,0.2,0,0.2v0 c0.1,0.2,0.2,0.4,0.4,0.6c0.2,0.1,0.4,0.2,0.6,0.2C6.6,37.3,7.3,37.2,8,37c3.5-0.9,6.6-2.5,9.2-4.9c1,0.1,2,0.2,2.9,0.2 c3.3,0,6.3-0.6,9-1.7c2.8-1.1,4.9-2.7,6.5-4.7c1.6-2,2.4-4.1,2.4-6.5C38.1,17.1,37.3,14.9,35.7,13z"></path>
         </symbol>
         <symbol id="icon-59c45c646c93a770c2b114cf72c44f8e" viewBox="0 0 40 40">
            <path d="M32.4,32.6h-5.1v-5.1h5.1V32.6z M26.2,32.6h-5.7v-5.1h5.7V32.6z M32.4,26.3h-5.1v-5.7h5.1V26.3z M26.2,26.3h-5.7v-5.7h5.7 V26.3z M32.4,19.6h-5.1v-5.1h5.1V19.6z M19.4,32.6h-5.7v-5.1h5.7V32.6z M26.2,19.6h-5.7v-5.1h5.7V19.6z M12.6,32.6H7.6v-5.1h5.1 V32.6z M19.4,26.3h-5.7v-5.7h5.7V26.3z M25.7,11.1V6c0-0.2,0.1-0.3,0.2-0.4c0.1-0.1,0.2-0.2,0.4-0.2h1.1c0.2,0,0.3,0.1,0.4,0.2 c0.1,0.1,0.2,0.2,0.2,0.4v5.1c0,0.2-0.1,0.3-0.2,0.4c-0.1,0.1-0.2,0.2-0.4,0.2h-1.1c-0.2,0-0.3-0.1-0.4-0.2 C25.7,11.4,25.7,11.2,25.7,11.1z M12.6,26.3H7.6v-5.7h5.1V26.3z M19.4,19.6h-5.7v-5.1h5.7V19.6z M12.6,19.6H7.6v-5.1h5.1V19.6z M12.1,11.1V6c0-0.2,0.1-0.3,0.2-0.4c0.1-0.1,0.2-0.2,0.4-0.2h1.1c0.2,0,0.3,0.1,0.4,0.2c0.1,0.1,0.2,0.2,0.2,0.4v5.1 c0,0.2-0.1,0.3-0.2,0.4c-0.1,0.1-0.2,0.2-0.4,0.2h-1.1c-0.2,0-0.3-0.1-0.4-0.2C12.1,11.4,12.1,11.2,12.1,11.1z M5.3,9.9v22.6 c0,0.6,0.2,1.1,0.7,1.6c0.4,0.4,1,0.7,1.6,0.7h24.9c0.6,0,1.1-0.2,1.6-0.7c0.4-0.4,0.7-1,0.7-1.6V9.9c0-0.6-0.2-1.1-0.7-1.6 c-0.4-0.4-1-0.7-1.6-0.7h-2.3V6c0-0.8-0.3-1.4-0.8-2s-1.2-0.8-2-0.8h-1.1c-0.8,0-1.4,0.3-2,0.8c-0.6,0.6-0.8,1.2-0.8,2v1.7h-6.8V6 c0-0.8-0.3-1.4-0.8-2s-1.2-0.8-2-0.8h-1.1c-0.8,0-1.4,0.3-2,0.8c-0.6,0.6-0.8,1.2-0.8,2v1.7H7.6C6.9,7.7,6.4,7.9,6,8.3 C5.5,8.8,5.3,9.3,5.3,9.9z"></path>
         </symbol>
      </svg>
      <div id="wrapper">
         <div id="main">
            <div class="inner">
               <div id="container01" class="container default" style="opacity:1;transform:none">
                  <div class="wrapper">
                     <div class="inner" data-onvisible-trigger="1">
                        <div id="image01" class="image" style="opacity:1"><span class="frame"><img src="https://www.dredyson.com/wp-content/uploads/2023/06/image01.png" alt=""></span></div>
                        <h1 id="text02" style="opacity:1;transform:none">{}</h1>
                        <p id="text03" style="opacity:1">
                           <span class="p">Room: <strong>{}</strong><br>Access code: <strong>{}</strong> &#10004;&#65039;<br>Bed &amp; Locker Number: <strong>{}</strong><br>Checkout date: {} before 10am</span></p>
                        <p id="text01" style="opacity:1">For assistance, please use the chatbot below or speak to your Dream Manager downstairs.</p>
                        <hr id="divider02" class="style1 full">
                        <ul id="icons01" class="icons">
                           <li>
                              <a class="n01" href="https://www.instagram.com/napyork/" aria-label="Instagram">
                                 <svg>
                                    <use xlink:href="#icon-85976685de3e4af37529a1ce5d57d2a7"></use>
                                 </svg>
                                 <span class="label">Instagram</span>
                              </a>
                           </li>
                           <li>
                              <a class="n02" href="https://twitter.com/napyork" aria-label="Twitter">
                                 <svg>
                                    <use xlink:href="#icon-0c4db87eff374f0f1ef47f8f043f0132"></use>
                                 </svg>
                                 <span class="label">Twitter</span>
                              </a>
                           </li>
                           <li>
                              <a class="n03" href="https://www.facebook.com/napyorkers/" aria-label="Facebook">
                                 <svg>
                                    <use xlink:href="#icon-a1eb5cac0cee3b05a40d856c98ce14a5"></use>
                                 </svg>
                                 <span class="label">Facebook</span>
                              </a>
                           </li>
                        </ul>
                        <hr id="divider01" class="style1 full">
                        <ul id="buttons01" class="buttons">
                        <!-- 
                           <li>
                              <a href="https://www.napyork.com" class="button n01">
                                 <svg>
                                    <use xlink:href="#icon-59c45c646c93a770c2b114cf72c44f8e"></use>
                                 </svg>
                                 <span class="label">Book a tour</span>
                              </a>
                           </li>
                           -->
                        </ul>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </div>
      <script>(function() {{var on = addEventListener,off = removeEventListener,$ = function(q) {{ return document.querySelector(q) }},$$ = function(q) {{ return document.querySelectorAll(q) }},$body = document.body,$inner = $('.inner'),client = (function() {{var o = {{browser: 'other',browserVersion: 0,os: 'other',osVersion: 0,mobile: false,canUse: null,flags: {{lsdUnits: false,}},}},ua = navigator.userAgent,a, i;a = [['firefox',/Firefox\/([0-9\.]+)/],['edge',/Edge\/([0-9\.]+)/],['safari',/Version\/([0-9\.]+).+Safari/],['chrome',/Chrome\/([0-9\.]+)/],['chrome',/CriOS\/([0-9\.]+)/],['ie',/Trident\/.+rv:([0-9]+)/]];for (i=0; i < a.length; i++) {{if (ua.match(a[i][1])) {{o.browser = a[i][0];o.browserVersion = parseFloat(RegExp.$1);break;}}}}a = [['ios',/([0-9_]+) like Mac OS X/,function(v) {{ return v.replace('_', '.').replace('_', ''); }}],['ios',/CPU like Mac OS X/,function(v) {{ return 0 }}],['ios',/iPad; CPU/,function(v) {{ return 0 }}],['android',/Android ([0-9\.]+)/,null],['mac',/Macintosh.+Mac OS X ([0-9_]+)/,function(v) {{ return v.replace('_', '.').replace('_', ''); }}],['windows',/Windows NT ([0-9\.]+)/,null],['undefined',/Undefined/,null]];for (i=0; i < a.length; i++) {{if (ua.match(a[i][1])) {{o.os = a[i][0];o.osVersion = parseFloat( a[i][2] ? (a[i][2])(RegExp.$1) : RegExp.$1 );break;}}}}if (o.os == 'mac'&& ('ontouchstart' in window)&& ((screen.width == 1024 && screen.height == 1366)|| (screen.width == 834 && screen.height == 1112)|| (screen.width == 810 && screen.height == 1080)|| (screen.width == 768 && screen.height == 1024)))o.os = 'ios';o.mobile = (o.os == 'android' || o.os == 'ios');var _canUse = document.createElement('div');o.canUse = function(property, value) {{var style;style = _canUse.style;if (!(property in style))return false;if (typeof value !== 'undefined') {{style[property] = value;if (style[property] == '')return false;}}return true;}};o.flags.lsdUnits = o.canUse('width', '100dvw');return o;}}()),trigger = function(t) {{dispatchEvent(new Event(t));}},cssRules = function(selectorText) {{var ss = document.styleSheets,a = [],f = function(s) {{var r = s.cssRules,i;for (i=0; i < r.length; i++) {{if (r[i] instanceof CSSMediaRule && matchMedia(r[i].conditionText).matches)(f)(r[i]); else if (r[i] instanceof CSSStyleRule && r[i].selectorText == selectorText)a.push(r[i]);}}}},x, i;for (i=0; i < ss.length; i++)f(ss[i]);return a;}},thisHash = function() {{var h = location.hash ? location.hash.substring(1) : null,a;if (!h)return null;if (h.match(/\?/)) {{a = h.split('?');h = a[0];history.replaceState(undefined, undefined, '#' + h);window.location.search = a[1];}}if (h.length > 0&& !h.match(/^[a-zA-Z]/))h = 'x' + h;if (typeof h == 'string')h = h.toLowerCase();return h;}},scrollToElement = function(e, style, duration) {{var y, cy, dy,start, easing, offset, f;if (!e)y = 0; else {{offset = (e.dataset.scrollOffset ? parseInt(e.dataset.scrollOffset) : 0) * parseFloat(getComputedStyle(document.documentElement).fontSize);switch (e.dataset.scrollBehavior ? e.dataset.scrollBehavior : 'default') {{case 'default':default:y = e.offsetTop + offset;break;case 'center':if (e.offsetHeight < window.innerHeight)y = e.offsetTop - ((window.innerHeight - e.offsetHeight) / 2) + offset; else y = e.offsetTop - offset;break;case 'previous':if (e.previousElementSibling)y = e.previousElementSibling.offsetTop + e.previousElementSibling.offsetHeight + offset; else y = e.offsetTop + offset;break;}}}}if (!style)style = 'smooth';if (!duration)duration = 750;if (style == 'instant') {{window.scrollTo(0, y);return;}}start = Date.now();cy = window.scrollY;dy = y - cy;switch (style) {{case 'linear':easing = function (t) {{ return t }};break;case 'smooth':easing = function (t) {{ return t<.5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1 }};break;}}f = function() {{var t = Date.now() - start;if (t >= duration)window.scroll(0, y); else {{window.scroll(0, cy + (dy * easing(t / duration)));requestAnimationFrame(f);}}}};f();}},scrollToTop = function() {{scrollToElement(null);}},loadElements = function(parent) {{var a, e, x, i;a = parent.querySelectorAll('iframe[data-src]:not([data-src=""])');for (i=0; i < a.length; i++) {{a[i].contentWindow.location.replace(a[i].dataset.src);a[i].dataset.initialSrc = a[i].dataset.src;a[i].dataset.src = '';}}a = parent.querySelectorAll('video[autoplay]');for (i=0; i < a.length; i++) {{if (a[i].paused)a[i].play();}}e = parent.querySelector('[data-autofocus="1"]');x = e ? e.tagName : null;switch (x) {{case 'FORM':e = e.querySelector('.field input, .field select, .field textarea');if (e)e.focus();break;default:break;}}}},unloadElements = function(parent) {{var a, e, x, i;a = parent.querySelectorAll('iframe[data-src=""]');for (i=0; i < a.length; i++) {{if (a[i].dataset.srcUnload === '0')continue;if ('initialSrc' in a[i].dataset)a[i].dataset.src = a[i].dataset.initialSrc; else a[i].dataset.src = a[i].src;a[i].contentWindow.location.replace('about:blank');}}a = parent.querySelectorAll('video');for (i=0; i < a.length; i++) {{if (!a[i].paused)a[i].pause();}}e = $(':focus');if (e)e.blur();}};window._scrollToTop = scrollToTop;var thisUrl = function() {{return window.location.href.replace(window.location.search, '').replace(/#$/, '');}};var getVar = function(name) {{var a = window.location.search.substring(1).split('&'),b, k;for (k in a) {{b = a[k].split('=');if (b[0] == name)return b[1];}}return null;}};var errors = {{handle: function(handler) {{window.onerror = function(message, url, line, column, error) {{(handler)(error.message);return true;}};}},unhandle: function() {{window.onerror = null;}}}};var loadHandler = function() {{setTimeout(function() {{$body.classList.remove('is-loading');$body.classList.add('is-playing');setTimeout(function() {{$body.classList.remove('is-playing');$body.classList.add('is-ready');}}, 2000);}}, 100);}};on('load', loadHandler);loadElements(document.body);var style, sheet, rule;style = document.createElement('style');style.appendChild(document.createTextNode(''));document.head.appendChild(style);sheet = style.sheet;if (client.mobile) {{(function() {{if (client.flags.lsdUnits) {{document.documentElement.style.setProperty('--viewport-height', '100svh');document.documentElement.style.setProperty('--background-height', '100dvh');}} else {{var f = function() {{document.documentElement.style.setProperty('--viewport-height', window.innerHeight + 'px');document.documentElement.style.setProperty('--background-height', (window.innerHeight + 250) + 'px');}};on('load', f);on('orientationchange', function() {{setTimeout(function() {{(f)();}}, 100);}});}}}})();}}if (client.os == 'android') {{(function() {{sheet.insertRule('body::after {{ }}', 0);rule = sheet.cssRules[0];var f = function() {{rule.style.cssText = 'height: ' + (Math.max(screen.width, screen.height)) + 'px';}};on('load', f);on('orientationchange', f);on('touchmove', f);}})();$body.classList.add('is-touch');}} else if (client.os == 'ios') {{if (client.osVersion <= 11)(function() {{sheet.insertRule('body::after {{ }}', 0);rule = sheet.cssRules[0];rule.style.cssText = '-webkit-transform: scale(1.0)';}})();if (client.osVersion <= 11)(function() {{sheet.insertRule('body.ios-focus-fix::before {{ }}', 0);rule = sheet.cssRules[0];rule.style.cssText = 'height: calc(100% + 60px)';on('focus', function(event) {{$body.classList.add('ios-focus-fix');}}, true);on('blur', function(event) {{$body.classList.remove('ios-focus-fix');}}, true);}})();$body.classList.add('is-touch');}}var scrollEvents = {{items: [],add: function(o) {{this.items.push({{element: o.element,triggerElement: (('triggerElement' in o && o.triggerElement) ? o.triggerElement : o.element),enter: ('enter' in o ? o.enter : null),leave: ('leave' in o ? o.leave : null),mode: ('mode' in o ? o.mode : 3),offset: ('offset' in o ? o.offset : 0),initialState: ('initialState' in o ? o.initialState : null),state: false,}});}},handler: function() {{var height, top, bottom, scrollPad;if (client.os == 'ios') {{height = document.documentElement.clientHeight;top = document.body.scrollTop + window.scrollY;bottom = top + height;scrollPad = 125;}} else {{height = document.documentElement.clientHeight;top = document.documentElement.scrollTop;bottom = top + height;scrollPad = 0;}}scrollEvents.items.forEach(function(item) {{var bcr, elementTop, elementBottom, state, a, b;if (!item.enter&& !item.leave)return true;if (!item.triggerElement)return true;if (item.triggerElement.offsetParent === null) {{if (item.state == true&& item.leave) {{item.state = false;(item.leave).apply(item.element);if (!item.enter)item.leave = null;}}return true;}}bcr = item.triggerElement.getBoundingClientRect();elementTop = top + Math.floor(bcr.top);elementBottom = elementTop + bcr.height;if (item.initialState !== null) {{state = item.initialState;item.initialState = null;}} else {{switch (item.mode) {{case 1:default:state = (bottom > (elementTop - item.offset) && top < (elementBottom + item.offset));break;case 2:a = (top + (height * 0.5));state = (a > (elementTop - item.offset) && a < (elementBottom + item.offset));break;case 3:a = top + (height * 0.25);if (a - (height * 0.375) <= 0)a = 0;b = top + (height * 0.75);if (b + (height * 0.375) >= document.body.scrollHeight - scrollPad)b = document.body.scrollHeight + scrollPad;state = (b > (elementTop - item.offset) && a < (elementBottom + item.offset));break;}}}}if (state != item.state) {{item.state = state;if (item.state) {{if (item.enter) {{(item.enter).apply(item.element);if (!item.leave)item.enter = null;}}}} else {{if (item.leave) {{(item.leave).apply(item.element);if (!item.enter)item.leave = null;}}}}}}}});}},init: function() {{on('load', this.handler);on('resize', this.handler);on('scroll', this.handler);(this.handler)();}}}};scrollEvents.init();var onvisible = {{effects: {{'blur-in': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'filter ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity) {{this.style.opacity = 0;this.style.filter = 'blur(' + (0.25 * intensity) + 'rem)';}},play: function() {{this.style.opacity = 1;this.style.filter = 'none';}},}},'zoom-in': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transform = 'scale(' + (1 - ((alt ? 0.25 : 0.05) * intensity)) + ')';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'zoom-out': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transform = 'scale(' + (1 + ((alt ? 0.25 : 0.05) * intensity)) + ')';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'slide-left': {{transition: function (speed, delay) {{return 'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function() {{this.style.transform = 'translateX(100vw)';}},play: function() {{this.style.transform = 'none';}},}},'slide-right': {{transition: function (speed, delay) {{return 'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function() {{this.style.transform = 'translateX(-100vw)';}},play: function() {{this.style.transform = 'none';}},}},'flip-forward': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transformOrigin = '50% 50%';this.style.transform = 'perspective(1000px) rotateX(' + ((alt ? 45 : 15) * intensity) + 'deg)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'flip-backward': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transformOrigin = '50% 50%';this.style.transform = 'perspective(1000px) rotateX(' + ((alt ? -45 : -15) * intensity) + 'deg)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'flip-left': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transformOrigin = '50% 50%';this.style.transform = 'perspective(1000px) rotateY(' + ((alt ? 45 : 15) * intensity) + 'deg)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'flip-right': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transformOrigin = '50% 50%';this.style.transform = 'perspective(1000px) rotateY(' + ((alt ? -45 : -15) * intensity) + 'deg)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'tilt-left': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transform = 'rotate(' + ((alt ? 45 : 5) * intensity) + 'deg)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'tilt-right': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity, alt) {{this.style.opacity = 0;this.style.transform = 'rotate(' + ((alt ? -45 : -5) * intensity) + 'deg)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'fade-right': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity) {{this.style.opacity = 0;this.style.transform = 'translateX(' + (-1.5 * intensity) + 'rem)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'fade-left': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity) {{this.style.opacity = 0;this.style.transform = 'translateX(' + (1.5 * intensity) + 'rem)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'fade-down': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity) {{this.style.opacity = 0;this.style.transform = 'translateY(' + (-1.5 * intensity) + 'rem)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'fade-up': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity) {{this.style.opacity = 0;this.style.transform = 'translateY(' + (1.5 * intensity) + 'rem)';}},play: function() {{this.style.opacity = 1;this.style.transform = 'none';}},}},'fade-in': {{transition: function (speed, delay) {{return 'opacity ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function() {{this.style.opacity = 0;}},play: function() {{this.style.opacity = 1;}},}},'fade-in-background': {{custom: true,transition: function (speed, delay) {{this.style.setProperty('--onvisible-speed', speed + 's');if (delay)this.style.setProperty('--onvisible-delay', delay + 's');}},rewind: function() {{this.style.removeProperty('--onvisible-background-color');}},play: function() {{this.style.setProperty('--onvisible-background-color', 'rgba(0,0,0,0.001)');}},}},'zoom-in-image': {{target: 'img',transition: function (speed, delay) {{return 'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function() {{this.style.transform = 'scale(1)';}},play: function(intensity) {{this.style.transform = 'scale(' + (1 + (0.1 * intensity)) + ')';}},}},'zoom-out-image': {{target: 'img',transition: function (speed, delay) {{return 'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity) {{this.style.transform = 'scale(' + (1 + (0.1 * intensity)) + ')';}},play: function() {{this.style.transform = 'none';}},}},'focus-image': {{target: 'img',transition: function (speed, delay) {{return 'transform ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '') + ', ' +'filter ' + speed + 's ease' + (delay ? ' ' + delay + 's' : '');}},rewind: function(intensity) {{this.style.transform = 'scale(' + (1 + (0.05 * intensity)) + ')';this.style.filter = 'blur(' + (0.25 * intensity) + 'rem)';}},play: function(intensity) {{this.style.transform = 'none';this.style.filter = 'none';}},}},}},add: function(selector, settings) {{var style = settings.style in this.effects ? settings.style : 'fade',speed = parseInt('speed' in settings ? settings.speed : 1000) / 1000,intensity = ((parseInt('intensity' in settings ? settings.intensity : 5) / 10) * 1.75) + 0.25,delay = parseInt('delay' in settings ? settings.delay : 0) / 1000,replay = 'replay' in settings ? settings.replay : false,stagger = 'stagger' in settings ? (parseInt(settings.stagger) > -125 ? (parseInt(settings.stagger) / 1000) : false) : false,staggerOrder = 'staggerOrder' in settings ? settings.staggerOrder : 'default',state = 'state' in settings ? settings.state : null,effect = this.effects[style];if ('CARRD_DISABLE_ANIMATION' in window) {{if (style == 'fade-in-background')$$(selector).forEach(function(e) {{e.style.setProperty('--onvisible-background-color', 'rgba(0,0,0,0.001)');}});return;}}$$(selector).forEach(function(e) {{var children = (stagger !== false) ? e.querySelectorAll(':scope > li, :scope ul > li') : null,enter = function(staggerDelay=0) {{var _this = this,transitionOrig;if (effect.target)_this = this.querySelector(effect.target);if (!effect.custom) {{transitionOrig = _this.style.transition;_this.style.setProperty('backface-visibility', 'hidden');_this.style.transition = effect.transition(speed, delay + staggerDelay);}} else effect.transition.apply(_this, [speed, delay + staggerDelay]);effect.play.apply(_this, [intensity, !!children]);if (!effect.custom)setTimeout(function() {{_this.style.removeProperty('backface-visibility');_this.style.transition = transitionOrig;}}, (speed + delay + staggerDelay) * 1000 * 2);}},leave = function() {{var _this = this,transitionOrig;if (effect.target)_this = this.querySelector(effect.target);if (!effect.custom) {{transitionOrig = _this.style.transition;_this.style.setProperty('backface-visibility', 'hidden');_this.style.transition = effect.transition(speed);}} else effect.transition.apply(_this, [speed]);effect.rewind.apply(_this, [intensity, !!children]);if (!effect.custom)setTimeout(function() {{_this.style.removeProperty('backface-visibility');_this.style.transition = transitionOrig;}}, speed * 1000 * 2);}},targetElement, triggerElement;if (effect.target)targetElement = e.querySelector(effect.target); else targetElement = e;if (children)children.forEach(function(targetElement) {{effect.rewind.apply(targetElement, [intensity, true]);}}); else effect.rewind.apply(targetElement, [intensity]);triggerElement = e;if (e.parentNode) {{if (e.parentNode.dataset.onvisibleTrigger)triggerElement = e.parentNode; else if (e.parentNode.parentNode) {{if (e.parentNode.parentNode.dataset.onvisibleTrigger)triggerElement = e.parentNode.parentNode;}}}}scrollEvents.add({{element: e,triggerElement: triggerElement,initialState: state,enter: children ? function() {{var staggerDelay = 0,childHandler = function(e) {{enter.apply(e, [staggerDelay]);staggerDelay += stagger;}},a;if (staggerOrder == 'default') {{children.forEach(childHandler);}} else {{a = Array.from(children);switch (staggerOrder) {{case 'reverse':a.reverse();break;case 'random':a.sort(function() {{return Math.random() - 0.5;}});break;}}a.forEach(childHandler);}}}} : enter,leave: (replay ? (children ? function() {{children.forEach(function(e) {{leave.apply(e);}});}} : leave) : null),}});}});}},}};onvisible.add('#image01', {{ style: 'fade-in', speed: 1000, intensity: 10, delay: 0, staggerOrder: '', replay: false }});onvisible.add('#text02', {{ style: 'fade-left', speed: 1000, intensity: 0, delay: 0, staggerOrder: '', replay: false }});onvisible.add('#text03', {{ style: 'fade-in', speed: 1000, intensity: 0, delay: 0, staggerOrder: '', replay: false }});onvisible.add('#text01', {{ style: 'fade-in', speed: 1000, intensity: 0, delay: 0, staggerOrder: '', replay: false }});onvisible.add('#container01', {{ style: 'fade-right', speed: 1000, intensity: 10, delay: 0, staggerOrder: '', replay: false }});}})();</script>
      <script>
  window.intercomSettings = {{
    api_base: "https://api-iam.intercom.io",
    app_id: "cuc8cct2"
  }};
    </script>

    <script>
    // We pre-filled your app ID in the widget URL: 'https://widget.intercom.io/widget/XXXXX'
    (function(){{var w=window;var ic=w.Intercom;if(typeof ic==="function"){{ic('reattach_activator');ic('update',w.intercomSettings);}}else{{var d=document;var i=function(){{i.c(arguments);}};i.q=[];i.c=function(args){{i.q.push(args);}};w.Intercom=i;var l=function(){{var s=d.createElement('script');s.type='text/javascript';s.async=true;s.src='https://widget.intercom.io/widget/cuc8cct2';var x=d.getElementsByTagName('script')[0];x.parentNode.insertBefore(s,x);}};if(document.readyState==='complete'){{l();}}else if(w.attachEvent){{w.attachEvent('onload',l);}}else{{w.addEventListener('load',l,false);}}}}}})();
    </script>
   </body>
</html>


    """.format(guest_name, room, room_code, bed_locker, leave_date)
    return html



def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str



def upload_html(file_path, sftp_host, sftp_port, sftp_username, sftp_password, sftp_directory):
    transport = paramiko.Transport((sftp_host, sftp_port))
    transport.connect(username=sftp_username, password=sftp_password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        sftp.put(file_path, f'{sftp_directory}')
        print('File uploaded successfully.')
    except Exception as e:
        print(f'File upload failed: {str(e)}')
    sftp.close()
    transport.close()



def bell():
    sys.stdout.write('\r\a')
    sys.stdout.flush()

# def generateQRCode(bed_number):
#     rollingGuestList = GuestCodes(guest_list_path, door_codes_path)
#     currentGuest_df = getCurrentGuest(rollingGuestList, bed_number)
#     currentGuestName = currentGuest_df['Customer'].values[0]
#     html_info = getGuestDetails(currentGuest_df)
#     if html_info[5] > 0:
#         bell()
#         raise gr.Error("Please take care of balance")
#     html = generate_html(html_info[0],# name, 
#                      html_info[1],# room, 
#                      html_info[2], # room code
#                      html_info[3], # bed and locker number
#                      html_info[4])# checkout date
#     with open(checkin_html_path, "w") as file:
#         file.write(html)
#     
#     url_string = generate_random_string(10)
#         with open(f'/var/www/html/{url_string}.html', "w") as file:
#             file.write(html)
# #    upload_html(server = "XXXXXXX", 
# #            username = "XXXXXX", 
# #            password = "XXXXXXX", 
# #            local_file_path = checkin_html_path, 
# #            remote_file_path = f"{url_string}.html")
#     upload_html(file_path = checkin_html_path,
#                 sftp_host = "XXXXXX", 
#                 sftp_port = 22, 
#                 sftp_username = "XXXXXXXX", 
#                 sftp_password = "XXXXXXX", 
#                 sftp_directory = f"{url_string}.html")# 

#     qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
#     qr.add_data(f"http://XX.XXX.XXX.XX/{url_string}.html")
#     qrLink = f"http://XX.XXX.XXX.XX/{url_string}.html"
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")
#     img.save(qrCode_path)
#     qrCode = Image.open(qrCode_path)
#     current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#     with open(f'{activity_logs_path}', 'a') as f:
#             print(f'Timestamp: {current_timestamp}, URL String: {qrLink},  Bed number: {bed_number},  Guest Name: {currentGuestName}', file=f)
#     return qrCode, qrLink, currentGuestName



def generateQRCode(bed_number):
    rollingGuestList = GuestCodes(guest_list_path, door_codes_path)
    currentGuest_df = getCurrentGuest(rollingGuestList, bed_number)
    currentGuestName = currentGuest_df['Customer'].values[0]
    html_info = getGuestDetails(currentGuest_df)
    if html_info[5] > 1:
        bell()
        raise gr.Error("Please take care of balance")
    html = generate_html(html_info[0], # name
                         html_info[1], # room
                         html_info[2], # room code
                         html_info[3], # bed and locker number
                         html_info[4]) # checkout date
    with open(checkin_html_path, "w") as file:
        file.write(html)

    url_string = generate_random_string(10)
    with open(f'/home/ubuntu/qrCode/v2/webpages/{url_string}.html', "w") as file:
        file.write(html)

    webpage_path = f'/home/ubuntu/qrCode/v2/webpages/{url_string}.html'
    webpage_destination_path = f'/var/www/html/{url_string}.html'
    shutil.copy(webpage_path, webpage_destination_path)


    # upload_html(server="XXXXX",
    #             username="XXXXX",
    #             password="XXXXX",
    #             local_file_path=checkin_html_path,
    #             remote_file_path=f"{url_string}.html")

    upload_html(file_path=checkin_html_path,
                sftp_host="XXXXX",
                sftp_port=22,
                sftp_username="XXXXXX",
                sftp_password="XXXXX",
                sftp_directory=f"{url_string}.html")

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(f"http://XXXXX.com/{url_string}.html?utm_source=qrCodeCheckin&utm_medium=in_person&utm_campaign=iPad")
    qrLink = f"http://XXXXXX.com/{url_string}.html"
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qrCode_path)
    qrCode = Image.open(qrCode_path)
    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(f'{activity_logs_path}', 'a') as f:
        print(f'Timestamp: {current_timestamp}, URL String: {qrLink},  Bed number: {bed_number},  Guest Name: {currentGuestName}', file=f)
    return qrCode, qrLink, currentGuestName



with gr.Blocks() as demo:
    with gr.Row():
        with gr.Row():
            with gr.Row():
                with gr.Column():
                    room_number = gr.Textbox(placeholder="Example: 201-1", label = "Enter Room & Bed Number")
                    greet_btn = gr.Button("submit")
                    with gr.Accordion(label = "Connect to Wifi", open = False):
                        gr.Markdown('<a href="www.qr-code-generator.com/solutions/wifi-qr-code/" border="0" style="cursor:default" rel="nofollow"><img src="https://chart.googleapis.com/chart?cht=qr&chl=WIFI%3AT%3AWPA%3BS%3ANap%20York%3BP%3Anapyorker%3BH%3A%3B%3B&chs=180x180&choe=UTF-8&chld=L|2"></a>')
        with gr.Row():
            with gr.Column():
                #output = gr.Image(type="pil")
                output = [gr.Image(type="pil"), 
                          gr.Textbox(label = "QR Link"),
                          gr.Textbox(label = "Guest Name")]

    greet_btn.click(fn=generateQRCode, inputs=room_number, outputs=output)

demo.launch(server_name="0.0.0.0", auth=("XXXX", "XXXXX"))
