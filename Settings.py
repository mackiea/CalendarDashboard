import xml.etree.ElementTree as Xml

from pygame import Color


class Settings:
    class ColourPair:
        def __init__(self, foreground: str, background: str):
            colour = foreground.split(",")
            self.foreground = Color(int(colour[0]), int(colour[1]), int(colour[2]))
            colour = background.split(",")
            self.background = Color(int(colour[0]), int(colour[1]), int(colour[2]))

    def __init__(self):
        settings = Xml.parse('settings.xml')
        root = settings.getroot()
        resolutions = root.find("RESOLUTIONS")
        selected_resolution = resolutions.find("SELECTED").text
        for resolution in resolutions.findall("RESOLUTION"):
            if resolution.get("NAME") == selected_resolution:
                w = resolution.get("WIDTH")
                assert w is not None
                self.width = int(w)
                h = resolution.get("HEIGHT")
                assert h is not None
                self.height = int(h)
                break

        colours = root.find("COLOURS")
        colour = colours.find("BACKGROUND").text.split(",")
        self.background_colour = Color(int(colour[0]), int(colour[1]), int(colour[2]))
        self.column_colours = []
        for column in colours.find("COLUMNS").findall("COLUMN"):
            foreground = column.get("FOREGROUND")
            assert foreground is not None
            background = column.get("BACKGROUND")
            assert background is not None
            self.column_colours.append(self.ColourPair(foreground, background))
        colour = colours.find("TODAY").text.split(",")
        self.today_colour = Color(int(colour[0]), int(colour[1]), int(colour[2]))
        colour = colours.find("TEXT").text.split(",")
        self.text_colour = Color(int(colour[0]), int(colour[1]), int(colour[2]))
        colour = colours.find("ALLDAY").text.split(",")
        self.allday_colour = Color(int(colour[0]), int(colour[1]), int(colour[2]))

        self.source_name = root.find("SOURCE").get("NAME")