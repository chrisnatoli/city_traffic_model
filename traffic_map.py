from traffic_components import *
from PIL import Image, ImageDraw



class CannotMapError(Exception): pass



class TrafficMap:

    def __init__(self, network):
        if network.lattice is None:
            raise CannotMapError(
                'The StreetNetwork given is not a square lattice.')
        else:
            self.network = network

    def draw(self):
        width = 600
        height = 600
        padding = 20
        street_width = 10

        block_width = int(( width - 2*padding
                            - street_width * len(self.network.lattice[0]))
                          / (len(self.network.lattice[0])) - 1)
        block_height = int(( height - 2*padding
                             - street_width * len(self.network.lattice))
                           / (len(self.network.lattice)) - 1)
        
        img = Image.new('RGB', (width, height), 'white')

        draw = ImageDraw.Draw(img)
        draw.line((0,0)+(width, height), fill=128)

        img.show()


