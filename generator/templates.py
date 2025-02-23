APP_INFO_TEMPLATE = '''{
    "targetPlatforms": $target_platforms, 
    "displayName": "$display_name", 
    "name": "$name", 
    "messageKeys": {
        "dummy": 10000
    }, 
    "companyName": "$author", 
    "enableMultiJS": true, 
    "versionLabel": "1.0", 
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
                "file": "images/background.png"
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

DATA_DICT = {
    'name': 'DATA',
    'type': 'raw',
}