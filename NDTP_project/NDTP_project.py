# -*- coding: cp1251 -*-
import telebot
import lyricsgenius
import json


with open ("keys.json", 'r') as file:
    keys = json.load(file)


bot = telebot.TeleBot(keys['telebot'])
genius = lyricsgenius.Genius(keys['genius'])
types = telebot.types

main_menu_keyboard = types.ReplyKeyboardMarkup(True)
main_menu_keyboard.row('Поиск', 'Избранное')
main_menu_keyboard.row('Обратная связь')

search_keyboard = types.ReplyKeyboardMarkup(True)
search_keyboard.row('Песню по названию', 'Песню по отрывку текста')
search_keyboard.row('Альбом', 'Исполнителя')
search_keyboard.row('В меню')

search_window_keyboard = types.ReplyKeyboardMarkup(True)
search_window_keyboard.row('В меню', 'К окну поиска')

contact_keyboard = types.ReplyKeyboardMarkup(True)
contact_keyboard.row('В меню')

favourites_keyboard = types.ReplyKeyboardMarkup(True)
favourites_keyboard.row('Любимые треки')
favourites_keyboard.row('Любимые исполнители')
favourites_keyboard.row('Любимые альбомы')
favourites_keyboard.row('В меню')


def purify_lyrics(lyrics):
    lyrics = lyrics.replace('You might also like', '')
    lyrics = lyrics.replace('Embed', '')
    while lyrics[-1].isdigit():
        lyrics = lyrics[:-1]
    return lyrics


def reply_to_user(request, type):
    text = request.text.capitalize()
    if all([text != 'В меню', text != 'К окну поиска']):
        bot.send_message(request.chat.id,'Вот что мне удалось найти',
        reply_markup=create_result_keyboard(search(text, type)['names'],search(text, type)['ids'], type))
    else:
        handle_text(request)


def search(request, type):
    match type:
        case 'song':
            data = genius.search_songs(request, per_page=10)
            hits = data['hits']
            key = 'full_title'
        case 'lyrics':
            data = genius.search_lyrics(request, per_page=10)
            hits = data['sections'][0]['hits']
            key = 'full_title'
        case 'artist':
            data = genius.search_artists(request, per_page=10)
            hits = data['sections'][0]['hits']
            key = 'name'
        case 'album':
            data = genius.search_albums(request, per_page=10)
            hits = data['sections'][0]['hits']
            key = 'full_title'
    
    results = {'names':[],'ids':[]}
    for hit in hits:
        results['names'].append(hit['result'][key])
        results['ids'].append(hit['result']['id'])
    return results


def create_result_keyboard(results, result_ids, searched_item):
    result_keyboard = types.InlineKeyboardMarkup()
    for i in range(len(results)):
        result_button = types.InlineKeyboardButton(text=results[i], callback_data = f'nav\\{result_ids[i]}\\{searched_item}')
        result_keyboard.add(result_button)
    return result_keyboard


def create_nav_keyboard(song):
    nav_keyboard = types.InlineKeyboardMarkup()

    album_button = types.InlineKeyboardButton(text='Перейти к альбому',
    callback_data=f"nav\\{song['album']['id']}\\album")
    artist_button = types.InlineKeyboardButton(text='Перейти к исполнителю',
    callback_data=f"nav\\{song['album']['artist']['id']}\\artist")

    nav_keyboard.add(album_button, artist_button)

    return nav_keyboard


def create_favs(id, type):
    add_keyboard = types.InlineKeyboardMarkup()
    add_button = types.InlineKeyboardButton(text = 'Добавить/удалить в избранное',
    callback_data=f'fav\\{id}\\{type}')
    add_keyboard.add(add_button)
    return add_keyboard


@bot.message_handler(commands=['start'])
def start_command_reply(message):
    bot.send_message(message.chat.id, 'Текст про то, что умеет этот бот', reply_markup=main_menu_keyboard)


@bot.callback_query_handler(func = lambda call: True)
def handle_callback(call):
    data = call.data
    operation = data[:data.find('\\')]
    id = data[data.find('\\') + 1:data.rfind('\\')]
    item_type = data[data.rfind('\\')+1:]
    chat_id = call.message.chat.id

    match operation:
        case 'nav':
            match item_type:
               case 'artist':
                    albums = genius.artist_albums(id)['albums']
                    photo_url = genius.artist(id)['artist']['image_url']
                    album_names = []
                    album_ids = []

                    for i in range(len(albums)):
                        album_names.append(albums[i]['name'])
                        album_ids.append(albums[i]['id'])

                    bot.send_photo(chat_id,
                    photo_url,
                    caption=f'Исполнитель {genius.artist(id)["artist"]["name"]}',
                    reply_markup=create_favs(id, 'artists'))
                    bot.send_message(chat_id, 'Дискография', reply_markup=create_result_keyboard(album_names, album_ids, 'album'))
               case 'album':
                    tracks = genius.album_tracks(id)['tracks']
                    cover_art_url = genius.cover_arts(album_id=id)['cover_arts'][0]['image_url']
                    track_names = []
                    track_ids = []
                    for i in range(len(tracks)):
                        track_names.append(tracks[i]['song']['title'])
                        track_ids.append(tracks[i]['song']['id'])
                    bot.send_photo(chat_id,
                    cover_art_url,
                    caption=f'Альбом {genius.album(id)["album"]["name"]}',
                    reply_markup=create_favs(id, 'albums'))
                    bot.send_message(chat_id, 'Трек-лист', reply_markup=create_result_keyboard(track_names, track_ids, 'song'))
               case _:
                    song = genius.song(id)['song']
                    header = f'Текст трека {song["title"]} в исполнении {song["album"]["artist"]["name"]}'
                    bot.send_message(chat_id, header, reply_markup=create_nav_keyboard(song))

                    while True:
                        try:
                            lyrics = genius.lyrics(song_id=id, remove_section_headers=True)
                            break
                        except:
                            pass
                    lyrics = lyrics[lyrics.find(song['title']) + len(song['title']) + 7:]
                    lyrics = purify_lyrics(lyrics)

                    bot.send_message(chat_id, lyrics, reply_markup=create_favs(id, 'songs'))
        case 'fav':
            with open ('favs.json', 'r') as file:
                data = json.load(file)
            if data.get(str(chat_id)) == None:
                data[chat_id] = {'songs':[], 'albums':[], 'artists':[]}
            item_index = -1
            for i in range(len(data[str(chat_id)][item_type])):
                if data[str(chat_id)][item_type][i] == id:
                    item_index = i
            if item_index == -1:
                data[str(chat_id)][item_type].append(id)
            else:
                del data[str(chat_id)][item_type][i]

            with open ('favs.json', 'w') as file:
                json.dump(data, file)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.capitalize()
    id = message.chat.id
    match text:
        case 'Поиск'|'К окну поиска':
            bot.send_message(id,'Что вы хотите найти?', reply_markup=search_keyboard)
        case 'В меню':
            start_command_reply(message)
        case 'Обратная связь':
            bot.send_message(id,'Разработчик бота: @Pcpszc', reply_markup=contact_keyboard)
        case 'Песню по названию':
            bot_message = bot.send_message(id, 'Введите название песни', reply_markup=search_window_keyboard)
            bot.register_next_step_handler(bot_message, reply_to_user, 'song')
        case 'Песню по отрывку текста':
            bot_message = bot.send_message(id, 'Введите сторчку из песни', reply_markup=search_window_keyboard)
            bot.register_next_step_handler(bot_message, reply_to_user, 'lyrics')
        case 'Альбом':
            bot_message = bot.send_message(id, 'Введите название альбома', reply_markup=search_window_keyboard)
            bot.register_next_step_handler(bot_message, reply_to_user, 'album')        
        case 'Исполнителя':
            bot_message = bot.send_message(id, 'Введите имя исполнителя или название группы', reply_markup=search_window_keyboard)
            bot.register_next_step_handler(bot_message, reply_to_user, 'artist')
        case 'Избранное':
            bot.send_message(id, 'Ваш список избранного', reply_markup=favourites_keyboard)
        case 'Любимые треки':
            with open ('favs.json') as file:
                song_ids = json.load(file)[str(id)]['songs']
            song_names = []
            for song_id in song_ids:
                song_names.append(genius.song(song_id)['song']['full_title'])
            bot.send_message(id,'Ваши избранные треки:',
            reply_markup = create_result_keyboard(song_names,song_ids, 'song'))
        case 'Любимые альбомы':
            with open ('favs.json') as file:
                album_ids = json.load(file)[str(id)]['albums']
            album_names = []
            for album_id in album_ids:
                album_names.append(genius.album(album_id)['album']['name'])
            bot.send_message(id,'Ваши избранные альбомы:',
            reply_markup = create_result_keyboard(album_names,album_ids, 'album'))
        case 'Любимые исполнители':
            with open ('favs.json') as file:
                artist_ids = json.load(file)[str(id)]['artists']
            artist_names = []
            for artist_id in artist_ids:
                artist_names.append(genius.artist(artist_id)['artist']['name'])
            bot.send_message(id,'Ваши избранные исполнители:',
            reply_markup = create_result_keyboard(artist_names, artist_ids, 'artist'))
        case _:
            bot.send_message(id, 'Даже не знаю, что ответить')


bot.polling()
