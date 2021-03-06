from __future__ import absolute_import

from six import iteritems
from collections import OrderedDict

from .models import glyphs, markers
from .mixins import FillProps, LineProps

def _glyph_function(glyphclass, dsnames, argnames, docstring, xfields=["x"], yfields=["y"]):

    def func(document_or_plot, *args, **kwargs):
        # Note: We want to reuse the glyph functions by attaching them the Plot
        # class. Imports are here to prevent circular imports.
        from .plotting_helpers import (
            _match_data_params, _update_plot_data_ranges,
            _materialize_colors_and_alpha, _get_legend,
            _make_legend, _get_select_tool
        )
        from .models import ColumnDataSource, GlyphRenderer, Plot, ServerDataSource
        source = kwargs.pop('source', None)
        if isinstance(source, ServerDataSource):
            datasource = ColumnDataSource()
            serversource = source
        elif source is None:
            datasource = ColumnDataSource()
            serversource = None
        else:
            datasource = source
            serversource = None

        legend_name = kwargs.pop("legend", None)

        from .document import Document
        document = None
        plot = None
        if isinstance(document_or_plot, Plot):
            plot = document_or_plot
            # TODO (bev) this seems like it should be here but invalid kwargs
            # currently get through (see also below)
            # plot.update(**kwargs)
        elif isinstance(document_or_plot, Document):
            document = document_or_plot
            if document.curplot() is not None and document._hold:
                plot = document.curplot()
                # plot.update(**kwargs)
            else:
                plot = document.figure(**kwargs)
        else:
            raise ValueError("expected document or plot object for first argument")

        name = kwargs.pop('name', None)
        if name:
            plot._id = name

        select_tool = _get_select_tool(plot)

        # Process the glyph dataspec parameters
        glyph_params = _match_data_params(dsnames, glyphclass,
                                          datasource, serversource,
                                          args, _materialize_colors_and_alpha(kwargs))

        x_data_fields = []
        for xx in xfields:
            if not isinstance(glyph_params[xx], dict): continue
            if glyph_params[xx]['units'] == 'data': x_data_fields.append(glyph_params[xx]['field'])
        y_data_fields = []
        for yy in yfields:
            if not isinstance(glyph_params[yy], dict): continue
            if glyph_params[yy]['units'] == 'data': y_data_fields.append(glyph_params[yy]['field'])

        _update_plot_data_ranges(plot, datasource, x_data_fields, y_data_fields)
        kwargs.update(glyph_params)

        glyph_props = glyphclass.properties() | set(argnames)
        glyph_kwargs = dict((key, value) for (key, value) in iteritems(kwargs) if key in glyph_props)
        glyph = glyphclass(**glyph_kwargs)

        nonselection_glyph_params = _materialize_colors_and_alpha(kwargs, prefix='nonselection_', default_alpha=0.1)
        nonselection_glyph = glyph.clone()

        if isinstance(nonselection_glyph, FillProps):
            nonselection_glyph.fill_color = nonselection_glyph_params['fill_color']
            nonselection_glyph.fill_alpha = nonselection_glyph_params['fill_alpha']

        if isinstance(nonselection_glyph, LineProps):
            nonselection_glyph.line_color = nonselection_glyph_params['line_color']
            nonselection_glyph.line_alpha = nonselection_glyph_params['line_alpha']

        glyph_renderer = GlyphRenderer(
            data_source=datasource,
            server_data_source=serversource,
            glyph=glyph,
            nonselection_glyph=nonselection_glyph,
            name=name)

        # TODO (bev) hacky, fix up when glyphspecs are simplified/removed
        if 'x_range_name' in kwargs:
            glyph_renderer.x_range_name = kwargs['x_range_name']
        if 'y_range_name' in kwargs:
            glyph_renderer.y_range_name = kwargs['y_range_name']

        if legend_name:
            legend = _get_legend(plot)
            if not legend:
                legend = _make_legend(plot)
            legends = OrderedDict(legend.legends)
            legends.setdefault(legend_name, []).append(glyph_renderer)
            legend.legends = list(legends.items())

        if select_tool :
            select_tool.renderers.append(glyph_renderer)
            select_tool._dirty = True

        plot.renderers.append(glyph_renderer)
        plot._dirty = True
        if document and document.autoadd:
            document.add(plot)
        return plot
    func.__name__ = glyphclass.__view_model__
    func.__doc__ = docstring
    return func

annular_wedge = _glyph_function(glyphs.AnnularWedge, ("x", "y", "inner_radius", "outer_radius", "start_angle", "end_angle"), ("direction",),
""" The `annular_wedge` glyph renders annular wedges centered at `x`, `y`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    inner_radius (str or list[float]) : values or field names of inner radii
    outer_radius (str or list[float]) : values or field names of outer radii
    start_angle (str or list[float]) : values or field names of starting angles
    end_angle (str or list[float]) : values or field names of ending angles
    direction ("clock" or "anticlock", optional): direction to turn between starting and ending angles, defaults to "anticlock"

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

annulus = _glyph_function(glyphs.Annulus, ("x", "y" ,"inner_radius", "outer_radius"), (),
""" The `annulus` glyph renders annuli centered at `x`, `y`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    inner_radius (str or list[float]) : values or field names of inner radii
    outer_radius (str or list[float]) : values or field names of outer radii

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

arc = _glyph_function(glyphs.Arc, ("x", "y", "radius" ,"start_angle", "end_angle"), ("direction",),
""" The `arc` glyph renders circular arcs centered at `x`, `y`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    radius (str or list[float]) : values or field names of arc radii
    start_angle (str or list[float]) : values or field names of starting angles
    end_angle (str or list[float]) : values or field names of ending angles
    direction ("clock" or "anticlock", optional): direction to turn between starting and ending angles, defaults to "anticlock"

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

asterisk = _glyph_function(markers.Asterisk, ("x", "y"), (),
""" The `asterisk` glyph is a marker that renders asterisks at `x`, `y` with size `size`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

bezier = _glyph_function(glyphs.Bezier, ("x0", "y0", "x1", "y1", "cx0", "cy0", "cx1", "cy1"), (),
""" The bezier glyph displays Bezier curves with the given starting, ending, and control points.

Args:
    plot (Plot) : a plot to add this glyph to
    x0 (str or list[float]) : values or field names of starting `x` coordinates
    y0 (str or list[float]) : values or field names of starting `y` coordinates
    x1 (str or list[float]) : values or field names of ending `x` coordinates
    y1 (str or list[float]) : values or field names of ending `y` coordinates
    cx0 (str or list[float]) : values or field names of first control point `x` coordinates
    cy0 (str or list[float]) : values or field names of first control point `y` coordinates
    cx1 (str or list[float]) : values or field names of second control point `x` coordinates
    cy1 (str or list[float]) : values or field names of second control point `y` coordinates

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Returns:
    plot
""",
    xfields=['x0', 'x1'], yfields=['y0', 'y1'])

circle = _glyph_function(markers.Circle, ("x", "y"), (),
""" The `circle` glyph is a marker that renders circles at `x`, `y` with size `size`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float], optional) : values or field names of sizes in screen units
    radius (str  or list[float], optional): values or field names of radii

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot

Notes:
    Only one of `size` or `radius` should be provided. Note that `radius` defaults to data units.
"""
)

circle_cross = _glyph_function(markers.CircleCross, ("x", "y"), (),
""" The `circle_cross` glyph is a marker that renders circles together with a crossbar (+) at `x`, `y` with size `size` or `radius`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

circle_x = _glyph_function(markers.CircleX, ("x", "y"), (),
""" The `circle_x` glyph is a marker that renders circles together with a "X" glyph at `x`, `y` with size `size`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

cross = _glyph_function(markers.Cross, ("x", "y"), (),
""" The `cross` glyph is a marker that renders crossbars (+) at `x`, `y` with size `size`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

diamond = _glyph_function(markers.Diamond, ("x", "y"), (),
""" The `diamond` glyph is a marker that renders diamonds at `x`, `y` with size `size` or `radius`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

diamond_cross = _glyph_function(markers.DiamondCross, ("x", "y"), (),
""" The `diamond_cross` glyph is a marker that renders diamonds together with a crossbar (+) at `x`, `y` with size `size` or `radius`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

image = _glyph_function(glyphs.Image, ("image", "x", "y", "dw", "dh"), ('palette', 'reserve_color', 'reserve_val', 'color_mapper', 'dilate'),
""" The image glyph takes each image as a two-dimensional array of scalar data.

A palette (string name of a built-in palette, currently) must also be supplied to use for color-mapping the scalar image.

Args:
    plot (Plot) : a plot to add this glyph to
    image (str or 2D array_like of float) : value or field names of scalar image data
    x (str or list[float]) : values or field names of lower left `x` coordinates
    y (str or list[float]) : values or field names of lower left `y` coordinates
    dw (str or list[float]) : values or field names of image width distances
    dh (str or list[float]) : values or field names of image height distances
    palette (str or list[str]) : values or field names of palettes to use for color-mapping (see :ref:`bokeh_dot_palettes` for more details)
    colorMapper (LinearColorMapper) : a LinearColorMapper instance
    dilate (bool, optional) : whether to dilate pixel distance computations when drawing, defaults to False

Returns:
    plot

Notes:
    setting `dilate` to True will cause pixel distances (e.g., for `dw` and `dh`) to
    be rounded up, always.
"""
)

image_rgba = _glyph_function(glyphs.ImageRGBA, ("image", "x", "y", "dw", "dh"), ("dilate",),
""" The image_rgba glyph takes each ``image`` as a two-dimensional array of RGBA values (encoded
as 32-bit integers).

Args:
    plot (Plot) : a plot to add this glyph to
    image (str or 2D array_like of uint32) : value or field names of RGBA image data
    x (str or list[float]) : values or field names of lower left `x` coordinates
    y (str or list[float]) : values or field names of lower left `y` coordinates
    dw (str or list[float]) : values or field names of image width distances
    dh (str or list[float]) : values or field names of image height distances
    dilate (bool, optional) : whether to dilate pixel distance computations when drawing, defaults to False

Returns:
    plot

Notes:
    setting `dilate` to True will cause pixel distances (e.g., for `dw` and `dh`) to
    be rounded up, always.
"""
)

image_url = _glyph_function(glyphs.ImageURL, ("url", "x", "y", "angle"), (),
"""The image_url glyph takes a urls for images to display.

Args:
    plot (Plot) : a plot to add this glyph to
    url (str) : value of RGBA image data
    x (str or list[float]) : values or field names of upper left `x` coordinates
    y (str or list[float]) : values or field names of upper left `y` coordinates
    angle (float) : angle to rotate image by

Returns:
    plot
"""
)

inverted_triangle = _glyph_function(markers.InvertedTriangle, ("x", "y"), (),
""" The `inverted_triangle` glyph is a marker that renders upside-down triangles at `x`, `y` with size `size` or `radius`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

line = _glyph_function(glyphs.Line, ("x", "y"), (),
""" The line glyph displays a single line that connects several points given by the arrays of coordinates `x` and `y`.

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of line `x` coordinates
    y (str or list[float]) : values or field names of line `y` coordinates

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

multi_line = _glyph_function(glyphs.MultiLine, ("xs", "ys"), (),
""" The multi_line glyph displays lines, each with points given by the arrays of coordinates that are the elements of xs and ys.

Args:
    plot (Plot) : a plot to add this glyph to
    xs (str or list[list[float]]): values or field names of lines `x` coordinates
    ys (str or list[list[float]]): values or field names of lines `y` coordinates

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

.. note:: For this glyph, the data is not simply an array of scalars, it is really an "array of arrays".

Returns:
    plot

""",
    xfields=["xs"], yfields=["ys"],
)

oval = _glyph_function(glyphs.Oval, ("x", "y", "width", "height"), (),
""" The oval glyph displays ovals centered on the given coordinates with the given dimensions and angle.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    width (str or list[float]) : values or field names of widths
    height (str or list[float]) : values or field names of heights
    angle (str or list[float], optional) : values or field names of rotation angles, defaults to 0

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

patch = _glyph_function(glyphs.Patch, ("x", "y"), (),
""" The patch glyph displays a single polygonal patch that connects several points given by the arrays of coordinates `x` and `y`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of patch `x` coordinates
    y (str or list[float]) : values or field names of patch `y` coordinates

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

patches = _glyph_function(glyphs.Patches, ("xs", "ys"), (),
""" The patches glyph displays several patches, each with points given by the arrays of coordinates that are the elements of xs and ys.

Args:
    plot (Plot) : a plot to add this glyph to
    xs (str or list[list[float]]): values or field names of patches `x` coordinates
    ys (str or list[list[float]]): values or field names of patches `y` coordinates

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

.. note:: For this glyph, the data is not simply an array of scalars, it is really an "array of arrays".

Returns:
    plot

""",
    xfields=["xs"], yfields=["ys"],
)

quad = _glyph_function(glyphs.Quad, ("left", "right", "top", "bottom"), (),
""" The quad glyph displays axis-aligned rectangles with the given dimensions.

Args:
    plot (Plot) : a plot to add this glyph to
    left (str or list[float]) : values or field names of left edges
    right (str or list[float]) : values or field names of right edges
    top (str or list[float]) : values or field names of top edges
    bottom (str or list[float]) : values or field names of bottom edges

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot
""",
    xfields=["left", "right"], yfields=["top", "bottom"])

quadratic = _glyph_function(glyphs.Quadratic, ("x0", "y0", "x1", "y1", "cx", "cy"), (),
""" The quadratic glyph displays quadratic curves with the given starting, ending, and control points.

Args:
    plot (Plot) : a plot to add this glyph to
    x0 (str or list[float]) : values or field names of starting `x` coordinates
    y0 (str or list[float]) : values or field names of starting `y` coordinates
    x1 (str or list[float]) : values or field names of ending `x` coordinates
    y1 (str or list[float]) : values or field names of ending `y` coordinates
    cx (str or list[float]) : values or field names of control point `x` coordinates
    cy (str or list[float]) : values or field names of control point `y` coordinates

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Returns:
    plot (Plot) : a plot to add this glyph to
    plot
""",
    xfields=["x0", "x1"], yfields=["y0", "y1"])

ray = _glyph_function(glyphs.Ray, ("x", "y", "length", "angle"), (),
""" The ray glyph displays line segments starting at the given coordinate and extending the given length at the given angle.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    length (str or list[float]) : values or field names of ray lengths in screen units
    angle (str or list[float]) : values or field names of ray angles

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Returns:
    plot
"""
)

rect = _glyph_function(glyphs.Rect, ("x", "y", "width", "height"), ("dilate",),
""" The rect glyph displays rectangles centered on the given coordinates with the given dimensions and angle.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    width (str or list[float]) : values or field names of widths
    height (str or list[float]) : values or field names of heights
    angle (str or list[float], optional) : values or field names of rotation angles, defaults to 0
    dilate (bool, optional) : whether to dilate pixel distance computations when drawing, defaults to False

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Returns:
    plot

Notes:
    setting `dilate` to True will cause pixel distances (e.g., for `width` and `height`) to
    be rounded up, always.

"""
)

segment = _glyph_function(glyphs.Segment, ("x0", "y0", "x1", "y1"), (),
""" The segment glyph displays line segments with the given starting and ending coordinates.

Args:
    plot (Plot) : a plot to add this glyph to
    x0 (str or list[float]) : values or field names of starting `x` coordinates
    y0 (str or list[float]) : values or field names of starting `y` coordinates
    x1 (str or list[float]) : values or field names of ending `x` coordinates
    y1 (str or list[float]) : values or field names of ending `y` coordinates

In addition the the parameters specific to this glyph, :ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Returns:
    plot
""",
    xfields=["x0", "x1"], yfields=["y0", "y1"])

square = _glyph_function(markers.Square, ("x", "y"), (),
""" The `square` glyph is a marker that renders squares at `x`, `y` with size `size`.

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

Returns:
    plot
"""
)

square_cross = _glyph_function(markers.SquareCross, ("x", "y"), (),
""" The `square_cross` glyph is a marker that renders squares together with a crossbar (+) at `x`, `y` with size `size`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

In addition the the parameters specific to this glyph, :ref:`userguide_objects_line_properties` and
:ref:`userguide_objects_fill_properties` are also accepted as keyword parameters.

Returns:
    plot
"""
)

square_x = _glyph_function(markers.SquareX, ("x", "y"), (),
""" The `square_x` glyph is a marker that renders squares together with "X" glyphs at `x`, `y` with size `size`.

In addition the the parameters specific to this glyph, :ref:`userguide_objects_line_properties` and
:ref:`userguide_objects_fill_properties` are also accepted as keyword parameters.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

Returns:
    plot
"""
)

text = _glyph_function(glyphs.Text, ("x", "y", "text", "angle"), (),
""" The text glyph displays text at the given coordinates rotated by the given angle.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of text `x` coordinates
    y (str or list[float]) : values or field names of text `y` coordinates
    text (str or list[text]): values or field names of texts
    angle (str or list[float], optional) : values or field names of text angles, defaults to 0

In addition the the parameters specific to this glyph, :ref:`userguide_objects_text_properties`
are also accepted as keyword parameters.

.. note:: The location and angle of the text relative to the `x`, `y` coordinates is indicated by the alignment and baseline text properties.

Returns:
    plot
"""
)

triangle = _glyph_function(markers.Triangle, ("x", "y"), (),
""" The `triangle` glyph is a marker that renders triangles at `x`, `y` with size `size`.

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties` and :ref:`userguide_objects_fill_properties`
are also accepted as keyword parameters.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

Returns:
    plot
"""
)

wedge = _glyph_function(glyphs.Wedge, ("x", "y", "radius", "start_angle", "end_angle"), ("direction",),
""" The `wedge` glyph renders circular wedges centered at `x`, `y`.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    radius (str or list[float]) : values or field names of wedge radii
    start_angle (str or list[float]) : values or field names of starting angles
    end_angle (str or list[float]) : values or field names of ending angles
    direction ("clock" or "anticlock", optional): direction to turn between starting and ending angles, defaults to "anticlock"

In addition the the parameters specific to this glyph, :ref:`userguide_objects_line_properties` and
:ref:`userguide_objects_fill_properties` are also accepted as keyword parameters.

Returns:
    plot
"""
)

x = _glyph_function(markers.X, ("x", "y"), (),
""" The `x` glyph is a marker that renders "x" glyphs at `x`, `y` with size `size`.

In addition the the parameters specific to this glyph,
:ref:`userguide_objects_line_properties`
are also accepted as keyword parameters.

Args:
    plot (Plot) : a plot to add this glyph to
    x (str or list[float]) : values or field names of center `x` coordinates
    y (str or list[float]) : values or field names of center `y` coordinates
    size (str or list[float]) : values or field names of sizes in screen units

Returns:
    plot
"""
)
