from music_queue import db

class YTVideo(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    found_at = db.Column(db.DateTime)
    pickle = db.Column(db.PickleType(), nullable=True)

    def __repr__(self):
        return '<Video: {}>'.format(self.title)
