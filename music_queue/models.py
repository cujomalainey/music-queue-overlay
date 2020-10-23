from music_queue import db

class YTVideo(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    found_at = db.Column(db.DateTime)
    pickle = db.Column(db.PickleType(), nullable=True)

    def __repr__(self):
        return '<Video: {}>'.format(self.title)

class ResultCache(db.Model):
    id = db.Column(db.String(240), primary_key=True)
    pickle = db.Column(db.Text)

    def __repr__(self):
        return '<cache: {}>'.format(self.id)
