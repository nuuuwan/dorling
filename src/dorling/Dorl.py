import math

from utils import Log, xmlx

_ = xmlx._  # HACK! This needs to be fixed.

SVG_WIDTH, SVG_HEIGHT = 450, 800
RADIUS = 45
PADDING = RADIUS * 2
MAX_EPOCHS = 1_000

STYLE_SHAPE = dict(fill_opacity=0.5, stroke='black', stroke_width=5)

log = Log('Dorl')


class Dorl:
    def __init__(self, config: list[dict]):
        self.config = config
        self.transformed_config = Dorl.pack(
            Dorl.transform(self.config, self.get_t())
        )

    @staticmethod
    def pack(config: list[dict]) -> list[dict]:
        EPSILON = 0.001
        for i in range(MAX_EPOCHS):
            log.debug(f'epoch {i}')
            did_pack = False
            for d1 in config:
                x1, y1 = d1['centroid']
                for d2 in config:
                    if d1 is d2:
                        continue
                    x2, y2 = d2['centroid']
                    dx, dy = x2 - x1, y2 - y1
                    dis = (dx**2 + dy**2) ** 0.5
                    if dis > RADIUS * 2:
                        continue

                    # pack
                    d1['centroid'] = (x1 - dx * EPSILON, y1 - dy * EPSILON)
                    d2['centroid'] = (x2 + dx * EPSILON, y2 + dy * EPSILON)
                    did_pack = True
            if not did_pack:
                break
        return config

    @staticmethod
    def transform(config: list[dict], t):
        return list(
            map(
                lambda d: dict(
                    name=d['name'],
                    centroid=t(*d['centroid']),
                    color=d['color'],
                ),
                config,
            )
        )

    def get_t(self):
        min_lat, min_lng = 180, 180
        max_lat, max_lng = -180, -180
        for d in self.config:
            lat, lng = d['centroid']
            min_lat = min(min_lat, lat)
            min_lng = min(min_lng, lng)
            max_lat = max(max_lat, lat)
            max_lng = max(max_lng, lng)

        lng_span = max_lng - min_lng
        lat_span = max_lat - min_lat

        def t(lat, lng):
            px, py = (lng - min_lng) / lng_span, (lat - min_lat) / lat_span
            return int(px * (SVG_WIDTH - PADDING * 2) + PADDING), int(
                (1 - py) * (SVG_HEIGHT - PADDING * 2) + PADDING
            )

        return t

    @staticmethod
    def render_circle(x, y, r, color):
        return _(
            'circle',
            None,
            dict(
                cx=x,
                cy=y,
                r=r,
                fill=color,
            )
            | STYLE_SHAPE,
        )

    @staticmethod
    def render_polygon(x, y, r, color, n):
        d_list = []
        for i in range(n):
            x1, y1 = x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(
                2 * math.pi * i / n
            )
            cmd = 'M' if i == 0 else 'L'
            d_list.append(f'{cmd}{x1},{y1}')

        d_list.append('Z')

        return _(
            'path',
            None,
            dict(
                d=' '.join(d_list),
                fill=color,
            )
            | STYLE_SHAPE,
        )

    @staticmethod
    def render_shape(x, y, r, color):
        return Dorl.render_polygon(x, y, r, color, 6)

    def render_node(self, d):
        x, y = d['centroid']
        return _(
            'g',
            [
                Dorl.render_shape(x, y, RADIUS, d['color']),
                _(
                    'text',
                    d['name'],
                    dict(
                        x=x,
                        y=y,
                        stroke='none',
                        fill='black',
                        text_anchor="middle",
                        dominant_baseline="middle",
                        font_family="sans-serif",
                        font_size=10,
                    ),
                ),
            ],
            dict(id="node-" + d['name']),
        )

    def render_inner(self):
        return list(
            map(
                self.render_node,
                self.transformed_config,
            )
        )

    def write(self, path: str):
        svg = _(
            'svg',
            self.render_inner(),
            dict(width=SVG_WIDTH, height=SVG_HEIGHT),
        )
        svg.store(path)
