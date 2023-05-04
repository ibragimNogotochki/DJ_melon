from Config import genius

class Song:

    def __init__(self, id):
        data = genius.song(id)['song']
        self.name = data['title']
        self.artist_id = data['album']['artist']['id']
        self.album_id = data['album']['id']
        self.id = id


    def get_artist(self):
        return Artist(self.artist_id)


    def get_album(self):
        return Album(self.album_id)


class Album:
    
    def __init__(self, id):
        data = genius.album(id)['album']
        self.name = data['name']
        self.artist_id = data['artist']['id']
        self.id = id


    def get_artist(self):
        return Artist(self.artist_id)


    def get_track_list(self):
        songs_data = genius.album_tracks(self.id)['tracks']
        track_list = []
        for i in songs_data:
            id = i['id']
            track_list.append(Song(id))
        return track_list


class Artist:

    def __init__(self, id):
        data = genius.album(id)['artist']
        self.name = data['name']
        self.photo_url = data['image_url']
        self.id = id


    def get_discography(self):
        albums_data = genius.artist_albums(id)['albums']
        discography = []
        for i in albums_data:
            id = i[id]
            discography.append(Album(id))
        return discography

