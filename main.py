import youtube_dl, random
from podgen import Podcast, Episode, Media
import pickle, slugify, os
from flask import Flask, request, send_from_directory, jsonify
app = Flask(__name__, static_url_path='')

unicode = str

def save():
    pickle.dump(playlists, open("playlists.save","wb"))
def load():
    playlists = pickle.load(open("playlists.save",'rb'))
    return playlists
class Video:
    def __init__(self,json):
        self.json = json
        self.formats = json["formats"]

    def get_format(self,format_ext):

        for format in self.formats:
            if format["ext"] == format_ext:
                return format["url"]

        return ''

    def get_basic(self,format="m4a"):
        data = {}
        data['title'] = self.json["title"]
        data['url'] = self.get_format(format)
        data['description'] = self.json['description']
        data['id'] = self.json['id']
        data['picture'] = self.json['thumbnail']
        return data
class Playlist:
    def __init__(self,url):
        self.videos = []
        self.url = url
        self.title = ''
        self.author = ''
    def update(self):
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        ydl.add_default_info_extractors()
        result = ydl.extract_info(self.url,download=False)
        for video in result["entries"]:
            self.videos.append(Video(video))
        print(result.keys())
        self.title = result["title"]
        self.author = result["uploader"]
    def gen_rss(self):
        p = Podcast(
           name=self.title,
           description="Podcast generated by Kaporos69",
           website="http://example.org/animals-alphabetically",
           explicit=False,
        )
        for video in self.videos:
            details = video.get_basic()
            p.episodes.append(Episode(
                title=details["title"],
                media=Media.create_from_server_response(details["url"]),
                summary=details["description"],
                image=details["picture"],
                id=details["id"]
            ))
        link = "rss/"+slugify.slugify(self.title)
        p.rss_file(link, minimize=True)
        return "/"+link


playlists = load()



@app.route("/generate")
def generate():

    list = request.args.get("list")
    if list == None:
        return "Missing list", 400
    playlists[list] = Playlist("https://www.youtube.com/playlist?list="+list)
    playlists[list].update()
    playlist_url = playlists[list].gen_rss()
    return jsonify({'url': "https://youtuberss-maker.herokuapp.com"+playlist_url})



@app.route('/rss/<path:path>')
def send_js(path):
    return send_from_directory('rss', path)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=os.getenv("PORT",default=5000))


# Add all the available extractors


#video = Video(result)
#print(video)

#print(video.get_basic())



"""
p = Playlist("https://www.youtube.com/playlist?list=PL7nvRKw4OSme4FmspNiqfMoBaZWXzB39l")
p.update()
url = p.gen_rss()
print(url)
"""
#playlists.append(p)
#print(p.videos[0].get_basic())
