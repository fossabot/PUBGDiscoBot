import time
from PIL import Image, ImageDraw, ImageFont, ImageOps

def render_stats(map_name, mode, position, teammates, rosters_count):
  
    if(map_name == 'Desert_Main'):
        map_name = 'Miramar_Main'

    image = Image.open('img/{}.png'.format(map_name))
    userIcon = Image.open('img/user.png', mode='r')
    draw = ImageDraw.Draw(image)

    map_name = map_name[:-5]
    if(map_name == 'Savage'):
        map_name = 'Sanhok'

    #Count user icons
    iconsCount = 4 if 'squad' in mode else len(teammates)

    #Fonts
    title_style = ImageFont.truetype("fonts/MyriadPro-Bold.otf", 10)
    fontRegular = ImageFont.truetype("fonts/MyriadPro-Regular.otf", 22)
    fontBold = ImageFont.truetype("fonts/MyriadPro-Bold.otf", 20)
    fontPosition = ImageFont.truetype("fonts/MyriadPro-Bold.otf", 15)

    #Sizes
    player_margin = 49
    icon_padding = 89
    metric_margin = 36
    metric_padding = 185

    #Colors
    white = (252, 255, 255, 255)
    grey = (208, 225, 229, 255)
    orange = (255, 169, 20, 255)
    playerColors = [(253, 204, 9, 255), (207,207,207,255), (207,155,104,255), (75,124,207,255)]

    #Position
    winText = 'TOP-' + str(position)
    draw.text((547, 11), winText, fill=white, font=fontPosition)

    #Mode icons 
    for i in range(iconsCount):
        image.paste(userIcon, (icon_padding , 9), userIcon)
        icon_padding += 15

    #Sort mates by kills count
    teammates.sort(key=lambda x:x.kills, reverse=True)

    metrics = ['DAMAGE', 'KILLS', 'ASSISTS', 'REVIVES', 'LONGEST', 'HS', 'DISTANCE']
    _metric_padding = metric_padding
    for index, metric in enumerate(metrics):
        draw.text((_metric_padding, metric_margin), metric, font=title_style, fill=white)        
        _metric_padding += title_style.getsize(metric)[0] + 28

    max_values = [
        round(max([x.damage_dealt for x in teammates])),
        max([x.kills for x in teammates]),
        max([x.assists for x in teammates]),
        max([x.revives for x in teammates]),
        round(max([x.longest_kill for x in teammates])),
        max([x.headshot_kills for x in teammates]),
        round(max([x.ride_distance + x.swim_distance + x.walk_distance for x in teammates])),
    ]

    for index, mate in enumerate(teammates):
        damage = round(mate.damage_dealt)
        longest = round(mate.longest_kill)
        distance = round(mate.ride_distance + mate.swim_distance + mate.walk_distance)
        values = [damage, mate.kills, mate.assists, mate.revives, longest, mate.headshot_kills, distance]

        draw.ellipse((10, player_margin + 5, 18, player_margin + 5 + 8), fill=playerColors[index])
        draw.text((24, player_margin), mate.name.upper()[:12], fill=white, font=fontBold)
        
        _metric_padding = metric_padding
        for index, metric in enumerate(metrics):
            metric_fill = white
            if values[index] == max_values[index]:
                metric_fill = orange
            draw.text((_metric_padding, player_margin), str(values[index]), fill=metric_fill, font=fontBold)
            _metric_padding += title_style.getsize(metric)[0] + 28

        player_margin += 24

    area = (0, 0, 615, player_margin + 3)
    image = image.crop(area)

    imageName = '{}-{}-{}.png'.format(time.time(), map_name, position)
    image.save(imageName)
    return imageName