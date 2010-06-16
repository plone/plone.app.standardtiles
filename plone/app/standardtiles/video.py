from zope import schema

import re

from plone.directives import form as directivesform
from plone.tiles import PersistentTile


class IVideoTile(directivesform.Schema):
    """Video tile
    """

    youtubeURL = schema.TextLine(title=u"Youtube URL", required=True)


class VideoTile(PersistentTile):
    """A tile that displays a youtube movie. Purely as a proof of concept and to showcase possibilities of Deco
    """

    def __call__(self):
        youtubeURL = self.data.get('youtubeURL')
        youtubeID = re.split('v=([A-Za-z00-9_\-]+)', youtubeURL)[1]

        # Not for production use - this should be in a template!
        return '<html><body><object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/%s&hl=en_GB&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%s&hl=en_GB&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object></body></html>' % (youtubeID, youtubeID)
