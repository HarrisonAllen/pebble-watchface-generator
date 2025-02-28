APP_INFO_TEMPLATE = '''{
    "targetPlatforms": $target_platforms, 
    "displayName": "$display_name", 
    "name": "$name", 
    "messageKeys": {
        "dummy": 10000
    }, 
    "companyName": "$author", 
    "enableMultiJS": true, 
    "versionLabel": "$version", 
    "capabilities": [], 
    "sdkVersion": "3", 
    "appKeys": {
        "dummy": 10000
    }, 
    "longName": "$display_name", 
    "shortName": "$display_name", 
    "watchapp": {
        "watchface": true
    }, 
    "resources": {
        "media": [
            {
                "type": "bitmap", 
                "name": "IMAGE_BACKGROUND", 
                "file": "background.png"
            }, 
            {
                "characterRegex": "[0-9:]", 
                "type": "font", 
                "name": "FONT_TIME_52", 
                "file": "font_time.ttf"
            }, 
            {
                "type": "font", 
                "name": "FONT_DATE_32", 
                "file": "font_date.ttf"
            }, 
            {
                "type": "font", 
                "name": "FONT_TEXT_20", 
                "file": "font_text.ttf"
            }, 
            {
                "type": "raw", 
                "name": "DATA", 
                "file": "data.bin"
            }
        ]
    }, 
    "uuid": "$new_uuid"
}'''

BACKGROUND_PNG_DICT = {
    'name': 'IMAGE_BACKGROUND',
    'type': 'png',
}

TIME_FONT_DICT = {
    'name': f'FONT_TIME_PLACEHOLDER',
    'type': 'font',
    'characterRegex': '[0-9:]'
}

DATE_FONT_DICT = {
    'name': f'FONT_DATE_PLACEHOLDER',
    'type': 'font'
}

TEXT_FONT_DICT = {
    'name': f'FONT_TEXT_PLACEHOLDER',
    'type': 'font'
}

DATA_DICT = {
    'name': 'DATA',
    'type': 'raw',
}