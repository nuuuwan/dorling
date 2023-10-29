import math

from utils import Log, xmlx

_ = xmlx._  # HACK! This needs to be fixed.

SVG_WIDTH, SVG_HEIGHT = 1600, 900
RADIUS = 20
PADDING = RADIUS * 4
MAX_EPOCHS = 10_000

STYLE_SHAPE = dict(fill_opacity=0.5, stroke='white', stroke_width=3)
N_POLYGON = 6
log = Log('Dorl')


class Dorl:
    def __init__(self, config: list[dict]):
        self.config = config
        self.transformed_config = Dorl.unpack(
            Dorl.transform(self.config, self.get_t())
        )

    @staticmethod
    def norm(x, y):
        x = max(PADDING, min(SVG_WIDTH - PADDING, x))
        y = max(PADDING, min(SVG_HEIGHT - PADDING, y))
        return x, y

    @staticmethod
    def unpack(config: list[dict]) -> list[dict]:
        EPSILON = 0.01
        n_config = len(config)
        for i in range(0, MAX_EPOCHS):
            n_unpack = 0
            for i1 in range(0, n_config - 1):
                d1 = config[i1]
                x1, y1 = d1['centroid']
                for i2 in range(i1 + 1, n_config):
                    d2 = config[i2]
                    x2, y2 = d2['centroid']
                    dx, dy = x2 - x1, y2 - y1
                    dis = (dx**2 + dy**2) ** 0.5
                    if dis > RADIUS * 2:
                        continue

                    # unpack
                    d1['centroid'] = Dorl.norm(
                        x1 - dx * EPSILON, y1 - dy * EPSILON
                    )
                    d2['centroid'] = Dorl.norm(
                        x2 + dx * EPSILON, y2 + dy * EPSILON
                    )
                    n_unpack += 1

            log.debug(f'{i=}, {n_unpack=}')
            if n_unpack == 0:
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
            x = int(px * (SVG_WIDTH - PADDING * 2) + PADDING)
            y = int((1 - py) * (SVG_HEIGHT - PADDING * 2) + PADDING)
            nx, ny = Dorl.norm(x, y)
            return nx, ny

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
        OFFSET = 1.0 / 2
        for i in range(n):
            theta = math.pi * (2 * (i / n) + OFFSET)
            x1 = x + r * math.cos(theta)
            y1 = y + r * math.sin(theta)
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
        return Dorl.render_polygon(x, y, r, color, N_POLYGON)

    def render_node(self, d):
        x, y = d['centroid']
        label = d['name']
        return _(
            'g',
            [
                Dorl.render_shape(x, y, RADIUS, d['color']),
                _(
                    'text',
                    label,
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
