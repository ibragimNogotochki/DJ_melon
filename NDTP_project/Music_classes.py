from Config import genius

class Song:

    def __init__(self, id):
        data = genius.song(id)['song']
        self.title = data['title']
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
        self.title = data['name']
        self.artist_id = data['artist']['id']
        self.id = id


    def get_artist(self):
        return Artist(self.artist_id)


    def get_track_list(self):
        pass


class Artist:

    def __init__(self, id):
        self.name = genius.artist['artist']['name']
        self.id = id


    def get_discography(self, id):
        pass
