import aiohttp
import asyncio
import nest_asyncio
import requests
import random, time
from sqlalchemy import create_engine
from sqlalchemy.sql import text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
from decouple import config
from bs4 import BeautifulSoup

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{config('MYSQL_USER')}:{config('MYSQL_PASS')}@{config('MYSQL_HOST')}/{config('MYSQL_DB')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

nest_asyncio.apply()
def format_link(link):
    return f'https://bwf.tournamentsoftware.com/sport/{link}'

def format_player_link(link):
    return f"https://bwf.tournamentsoftware.com/player-profile/{link}"

def format_date(date):
    vals = date.split('/')
    return f"{vals[2]}-{vals[0]}-{vals[1]}"

def format_image_link(link):
    return link[len("background-image: url(//"):-1]

async def grab_player_info(player, session):
    
    player['country'] = None
    player['date of birth'] = None
    player['play r or l'] = None
    player['height'] = None
    player['img link'] = None

    async with session.get(format_player_link(player['id'])) as resp:
        html_text = await resp.text()
        soup = BeautifulSoup(html_text, 'lxml')

        name = soup.find('h2', class_='media__title media__title--large')
        if name:
            name = name.find('span', class_='nav-link__value').text
            name = name.upper().strip()
            index = name.find('n')
            if index != -1:
                name = name[:index]
            player['name'] = name

        img = soup.find('div', class_='profile-icon__img-inner')
        if img:
            link_dirty = img.get('style')
            link_clean = format_image_link(link_dirty)
            player['img link'] = link_clean

        country = soup.find('div', class_='media__content-subinfo')
        if country:
            country = country.find('span', class_='nav-link__value').text
            country = country.upper().strip()
            player['country'] = country

        detail_section = soup.find('dl', class_='list list--flex list--bordered')
        if detail_section:
            detail_section = detail_section.findAll('div', class_='list__item')

            for detail in detail_section:
                section = detail.find('dt', class_='list__label').text.lower().strip()
                value = detail.find('span', class_='nav-link__value').text.strip()

                if section == 'date of birth':
                    value = format_date(value)
                elif section == 'play r or l':
                    value = 'R' if value == 'Right handed' else 'L'
                elif section == 'height':
                    splitter = value.split(' ')
                    value = splitter[0]
                else:
                    continue

                player[section] = value

    return player
    
async def test(test_data):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*[grab_player_info(player=player, session=session) for player in test_data], return_exceptions=True)

if __name__ == "__main__":
    req = requests.get("https://api.badminton-api.com/player/search?limit=15000")
    test_data = req.json()['data']

    batch_size = 50
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def UPDATE_PLAYER_ROW_QUERY(pid, imgLink):
        return text(f"UPDATE `player` SET imgLink = '{imgLink}' WHERE `id` = '{pid}';")

    for i in range(0, len(test_data), batch_size):
        print(f"running for batch {i}-{i+batch_size-1}")
        xd = None
        
        if i + batch_size < len(test_data):
            xd = asyncio.run(test(test_data[i:i+batch_size]))
        else:
            xd = asyncio.run(test(test_data[i:]))

        if xd:
            with engine.connect() as conn:
                for x in xd:
                    statement = UPDATE_PLAYER_ROW_QUERY(x['id'], x['img link'])
                    conn.execute(statement)
        else:
            print(f"no results for range {i}-{i+batch_size}")
        print(f"done for batch {i}-{i+batch_size-1}!\n\n")
        time.sleep(5 + random.randint(0, 20))
    