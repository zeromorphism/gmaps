
import warnings

import ipywidgets as widgets
from traitlets import (Unicode, CUnicode, default, Int, Bool,
                       List, Tuple, Float, Instance, validate,
                       observe, Enum, Dict, HasTraits)

import gmaps.geotraitlets as geotraitlets

DEFAULT_CENTER = (46.2, 6.1)
DEFAULT_BOUNDS = [(46.2, 6.1), (47.2, 7.1)]

_default_configuration = {"api_key": None}

def configure(api_key=None):
    """
    Configure access to the GoogleMaps API.

    :param api_key: String denoting the key to use when accessing Google maps, or
        None to not pass an API key.
    """
    configuration = {"api_key": api_key}
    global _default_configuration
    _default_configuration = configuration


class ConfigurationMixin(HasTraits):
    configuration = Dict(
        traits={"api_key": Unicode(allow_none=True)}).tag(sync=True)

    @default("configuration")
    def _config_default(self):
        return _default_configuration


class InvalidPointException(Exception):
    pass

class DirectionsServiceException(RuntimeError):
    pass


class Map(widgets.DOMWidget, ConfigurationMixin):
    """
    Base map class

    Instances of this act as a base map on which you can add
    additional layers.

    :Examples:

    >>> m = gmaps.Map()
    >>> m.add_layer(gmaps.Heatmap(data=data))
    """
    _view_name = Unicode("PlainmapView").tag(sync=True)
    _view_module = Unicode("jupyter-gmaps").tag(sync=True)
    _model_name = Unicode("PlainmapModel").tag(sync=True)
    _model_module = Unicode("jupyter-gmaps").tag(sync=True)
    layers = Tuple(trait=Instance(widgets.Widget)).tag(sync=True, **widgets.widget_serialization)
    data_bounds = List(DEFAULT_BOUNDS).tag(sync=True)

    def add_layer(self, layer):
        self.layers = tuple([l for l in self.layers] + [layer])

    @default("layout")
    def _default_layout(self):
        return widgets.Layout(height='400px', align_self='stretch')

    @observe("layers")
    def _calc_bounds(self, change):
        layers = change["new"]
        bounds_list = [layer.data_bounds for layer in layers if layer.has_bounds]
        if bounds_list:
            min_latitude = min(bounds[0][0] for bounds in bounds_list)
            min_longitude = min(bounds[0][1] for bounds in bounds_list)
            max_latitude = min(bounds[1][0] for bounds in bounds_list)
            max_longitude = min(bounds[1][1] for bounds in bounds_list)
            self.data_bounds = [(min_latitude, min_longitude), (max_latitude, max_longitude)]

class Directions(widgets.Widget):
    """
    Directions layer.

    Add this to a ``Map`` instance to draw directions.

    By default, the directions are requested with the DRIVING option.

    Data is a list of lat,lon tuples. The first point of the list is passed as
    the origin of the itinerary; the last point is passed as the destination of
    the itinerary. Other points are passed in order as a list of waypoints.

    To set the parameters, pass them to the constructor:
    >>> directions_layer = gmaps.Directions(data=data)

    Examples:
    >>> m = gmaps.Map()
    >>> data = [(48.85341, 2.3488), (50.85045, 4.34878), (52.37403, 4.88969)]
    >>> directions_layer = gmaps.Directions(data=data)
    >>> m.add_layer(directions_layer)

    An TraitError is raised if you try to pass less than two points:
    >>> directions_layer = gmaps.Directions(data=[(50.0, 4.0])
    Traceback (most recent call last):
        ...
    TraitError: The 'data' trait of a Directions instance must be of length 2 <= L <= 9223372036854775807, but a value of [[50.0, 4.0]] was specified.

    There is a limitation in the number of waypoints allowed by Google. If it
    fails to return directions, a DirectionsServiceException is raised.
    >>> directions_layer = gmaps.Directions(data=data*10)
    Traceback (most recent call last):
        ...
    DirectionsServiceException: No directions returned: MAX WAYPOINTS EXCEEDED

    """
    has_bounds = True
    _view_name = Unicode("DirectionsLayerView").tag(sync=True)
    _view_module = Unicode("jupyter-gmaps").tag(sync=True)
    _model_name = Unicode("DirectionsLayerModel").tag(sync=True)
    _model_module = Unicode("jupyter-gmaps").tag(sync=True)

    data = List(minlen=2).tag(sync=True)
    data_bounds = List().tag(sync=True)

    layer_status = CUnicode().tag(sync=True)

    @validate("data")
    def _validate_data(self, proposal):
        assert (len(proposal["value"]) >= 2), "A direction requires at least two points"
        for point in proposal["value"]:
            if not geotraitlets.is_valid_point(point):
                raise InvalidPointException(
                    "{} is not a valid latitude, longitude pair".format(point))
        return proposal["value"]

    @observe("data")
    def _calc_bounds(self, change):
        data = change["new"]
        min_latitude = min(row[0] for row in data)
        min_longitude = min(row[1] for row in data)
        max_latitude = max(row[0] for row in data)
        max_longitude = max(row[1] for row in data)
        self.data_bounds = [(min_latitude, min_longitude), (max_latitude, max_longitude)]

    @observe("layer_status")
    def _handle_layer_status(self, change):
        if change["new"] != "OK":
            raise DirectionsServiceException("No directions returned: " + change["new"])


# Mixin for options common to both heatmap and weighted heatmaps.
class _HeatmapOptionsMixin(HasTraits):
    """
    :param max_intensity:
        Strictly positive floating point number indicating the numeric value
        that corresponds to the hottest colour in the heatmap gradient. Any
        density of points greater than that value will just get mapped to
        the hottest colour. Setting this value can be useful when your data
        is sharply peaked. It is also useful if you find that your heatmap
        disappears as you zoom in.
    :type max_intensity: float, optional

    :param point_radius:
        Number of pixels for each point passed in the data. This determines the
        "radius of influence" of each data point.
    :type point_radius: int, optional

    :param dissipating:
        Whether the radius of influence of each point changes as you zoom in
        or out. If `dissipating` is True, the radius of influence of each
        point increases as you zoom out and decreases as you zoom in. If
        False, the radius of influence remains the same. Defaults to True.
    :type dissipating: bool, optional

    :param opacity:
        The opacity of the heatmap layer. Defaults to 0.6.
    :type opacity: float, optional

    :param gradient:
        The color gradient for the heatmap. This must be specified as a list
        of colors. Google Maps then interpolates linearly between those
        colors.
        Colors can be specified as a simple string, e.g. 'blue',
        as an RGB tuple, e.g. (100, 0, 0), or as an RGBA tuple, e.g.
        (100, 0, 0, 0.5).
    :type gradient: list of colors, optional
    """
    max_intensity = Float(default_value=None, allow_none=True).tag(sync=True)
    point_radius = Float(default_value=None, allow_none=True).tag(sync=True)
    dissipating = Bool(default_value=True).tag(sync=True)
    opacity = Float(default_value=0.6, min=0.0, max=1.0).tag(sync=True)
    gradient = List(trait=geotraitlets.ColorAlpha(), allow_none=True, minlen=1).tag(sync=True)

    @default("gradient")
    def _default_gradient(self):
        return None


class Heatmap(widgets.Widget, _HeatmapOptionsMixin):
    __doc__ = """
    Heatmap layer.

    Add this to a ``Map`` instance to draw a heatmap. A heatmap shows
    the density of points in or near a particular area.

    To set the parameters, pass them to the constructor or set them
    on the heatmap object after construction::

    >>> heatmap_layer = gmaps.Heatmap(data=data, max_intensity=10)

    or::

    >>> heatmap_layer = gmaps.Heatmap()
    >>> heatmap_layer.data = data
    >>> heatmap_layer.max_intensity = 10

    :Examples:

    >>> m = gmaps.Map()
    >>> data = [(46.1, 5.2), (46.2, 5.3), (46.3, 5.4)]
    >>> heatmap_layer = gmaps.Heatmap(data=data)
    >>> heatmap_layer.max_intensity = 2
    >>> heatmap_layer.point_radius = 3
    >>> heatmap_layer.gradient = ['white', 'gray']
    >>> m.add_layer(heatmap_layer)

    :param data: List of (latitude, longitude) pairs denoting a single
        point. Latitudes
        are expressed as a float between -90 (corresponding to 90 degrees south)
        and +90 (corresponding to 90 degrees north). Longitudes are expressed
        as a float between -180 (corresponding to 180 degrees west) and 180
        (corresponding to 180 degrees east).
    :type data: list of tuples

    """ + _HeatmapOptionsMixin.__doc__
    has_bounds = True
    _view_name = Unicode("SimpleHeatmapLayerView").tag(sync=True)
    _view_module = Unicode("jupyter-gmaps").tag(sync=True)
    _model_name = Unicode("SimpleHeatmapLayerModel").tag(sync=True)
    _model_module = Unicode("jupyter-gmaps").tag(sync=True)

    data = List().tag(sync=True)
    data_bounds = List().tag(sync=True)

    @validate("data")
    def _validate_data(self, proposal):
        for point in proposal["value"]:
            if not geotraitlets.is_valid_point(point):
                raise InvalidPointException(
                    "{} is not a valid latitude, longitude pair".format(point))
        return proposal["value"]

    @observe("data")
    def _calc_bounds(self, change):
        data = change["new"]
        min_latitude = min(row[0] for row in data)
        min_longitude = min(row[1] for row in data)
        max_latitude = max(row[0] for row in data)
        max_longitude = max(row[1] for row in data)
        self.data_bounds = [(min_latitude, min_longitude), (max_latitude, max_longitude)]


class WeightedHeatmap(widgets.Widget, _HeatmapOptionsMixin):
    __doc__ = """
    Heatmap with weighted points.

    Add this layer to a ``Map`` instance to draw a heatmap. Unlike the plain
    Heatmap layer, which assumes that all points should have equal weight,
    this layer lets you specifiy different weights for points.

    :Examples:

    >>> m = gmaps.Map()
    # triples representing `latitude, longitude, weight`:
    >>> data = [(46.1, 5.2, 0.5), (46.2, 5.3, 0.2), (46.3, 5.4, 0.8)]
    >>> heatmap_layer = gmaps.Heatmap(data=data)
    >>> heatmap_layer.max_intensity = 2
    >>> m.add_layer(heatmap_layer)

    :param data: List of (latitude, longitude, weight) triples for a single
        point. Latitudes are expressed as a float between -90 (corresponding to
        90 degrees south) and +90 (corresponding to 90 degrees north).
        Longitudes are expressed as a float between -180
        (corresponding to 180 degrees west) and +180 (corresponding to
        180 degrees east). Weights must be non-negative.
    :type data: list of tuples

    """ + _HeatmapOptionsMixin.__doc__
    has_bounds = True
    _view_name = Unicode("WeightedHeatmapLayerView").tag(sync=True)
    _view_module = Unicode("jupyter-gmaps").tag(sync=True)
    _model_name = Unicode("WeightedHeatmapLayerModel").tag(sync=True)
    _model_module = Unicode("jupyter-gmaps").tag(sync=True)

    data = List().tag(sync=True)
    data_bounds = List().tag(sync=True)

    @validate("data")
    def _validate_data(self, proposal):
        for point in proposal["value"]:
            if not geotraitlets.is_valid_point(point[:2]):
                raise InvalidPointException(
                    "{} is not a valid latitude, longitude pair".format(point))
            # check weight
        return proposal["value"]

    @observe("data")
    def _calc_bounds(self, change):
        data = change["new"]
        min_latitude = min(row[0] for row in data)
        min_longitude = min(row[1] for row in data)
        max_latitude = max(row[0] for row in data)
        max_longitude = max(row[1] for row in data)
        self.data_bounds = [(min_latitude, min_longitude), (max_latitude, max_longitude)]


class TaggedRegion(widgets.Widget):
    """
    Tagged region layer for creating custom regions with metadata.

    Add this to a ``Map`` instance to draw custom regions (polygons) with
    associated metadata, tags, and links to external sources like Wikipedia.

    :Examples:

    >>> m = gmaps.Map()
    >>> region = gmaps.TaggedRegion(
    ...     name="Golden Gate Park",
    ...     coordinates=[
    ...         (37.771, -122.511),
    ...         (37.771, -122.453),
    ...         (37.766, -122.453),
    ...         (37.766, -122.511)
    ...     ],
    ...     description="Large urban park in San Francisco",
    ...     tags=["park", "recreation", "landmark"],
    ...     wikipedia_url="https://en.wikipedia.org/wiki/Golden_Gate_Park",
    ...     fill_color="green",
    ...     fill_opacity=0.4
    ... )
    >>> m.add_layer(region)

    :param name: Name of the region
    :type name: str

    :param coordinates: List of (latitude, longitude) pairs defining the polygon
        boundary. Must have at least 3 points.
    :type coordinates: list of tuples

    :param description: Description of the region
    :type description: str, optional

    :param tags: List of tags associated with the region
    :type tags: list of str, optional

    :param data: Dictionary of custom metadata
    :type data: dict, optional

    :param wikipedia_url: URL to Wikipedia or similar source
    :type wikipedia_url: str, optional

    :param fill_color: Color for the polygon fill (CSS color or hex)
    :type fill_color: str, optional

    :param fill_opacity: Opacity of the fill (0.0 to 1.0)
    :type fill_opacity: float, optional

    :param stroke_color: Color for the polygon border
    :type stroke_color: str, optional

    :param stroke_opacity: Opacity of the border (0.0 to 1.0)
    :type stroke_opacity: float, optional

    :param stroke_weight: Width of the border in pixels
    :type stroke_weight: int, optional
    """
    has_bounds = True
    _view_name = Unicode("TaggedRegionLayerView").tag(sync=True)
    _view_module = Unicode("jupyter-gmaps").tag(sync=True)
    _model_name = Unicode("TaggedRegionLayerModel").tag(sync=True)
    _model_module = Unicode("jupyter-gmaps").tag(sync=True)

    name = Unicode("").tag(sync=True)
    coordinates = List(minlen=3).tag(sync=True)
    description = Unicode("").tag(sync=True)
    tags = List(trait=Unicode()).tag(sync=True)
    data = Dict().tag(sync=True)
    wikipedia_url = Unicode("").tag(sync=True)

    fill_color = Unicode("#0000FF").tag(sync=True)
    fill_opacity = Float(default_value=0.35, min=0.0, max=1.0).tag(sync=True)
    stroke_color = Unicode("#0000FF").tag(sync=True)
    stroke_opacity = Float(default_value=0.8, min=0.0, max=1.0).tag(sync=True)
    stroke_weight = Int(default_value=2).tag(sync=True)

    data_bounds = List().tag(sync=True)

    @validate("coordinates")
    def _validate_coordinates(self, proposal):
        coords = proposal["value"]
        if len(coords) < 3:
            raise ValueError("A region requires at least 3 coordinate points")
        for point in coords:
            if not geotraitlets.is_valid_point(point):
                raise InvalidPointException(
                    "{} is not a valid latitude, longitude pair".format(point))
        return coords

    @observe("coordinates")
    def _calc_bounds(self, change):
        data = change["new"]
        if len(data) > 0:
            min_latitude = min(row[0] for row in data)
            min_longitude = min(row[1] for row in data)
            max_latitude = max(row[0] for row in data)
            max_longitude = max(row[1] for row in data)
            self.data_bounds = [(min_latitude, min_longitude), (max_latitude, max_longitude)]

    @default("tags")
    def _default_tags(self):
        return []

    @default("data")
    def _default_data(self):
        return {}


def plainmap():
    warnings.warn(
        "plainmap is deprecated. Prefer the Map class.",
        category=RuntimeWarning)
    return Map()


def heatmap(data):
    warnings.warn(
        "heatmap is deprecated. Prefer combining the Map class "
        "with a Heatmap layer",
        category=RuntimeWarning)
    p = Map()
    heatmap_layer = HeatmapLayer()
    heatmap_layer.data = data
    p.layers = (heatmap_layer, )
    return p
