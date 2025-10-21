# Custom Tagged Regions - MVP Documentation

## Overview

The Custom Tagged Regions feature allows you to create interactive polygon regions on Google Maps with rich metadata, tags, and links to external sources like Wikipedia. This MVP provides a powerful way to annotate geographic areas with contextual information.

## Features

### Core Capabilities
- **Custom Polygons**: Draw any shape by defining coordinate boundaries
- **Rich Metadata**: Attach name, description, and custom key-value data to regions
- **Tagging System**: Categorize regions with multiple tags
- **External Links**: Link to Wikipedia or other reference sources
- **Interactive UI**: Click regions to view all associated information
- **Customizable Styling**: Control colors, opacity, and border properties

### Use Cases
- Geographic data visualization and exploration
- Research field study documentation
- Interactive educational geography lessons
- Urban planning and zoning visualization
- Environmental conservation area mapping
- Historical site documentation

## Installation

```bash
# Install the package (after building)
pip install -e .

# Build the JavaScript components
cd js
npm install
npm run build
cd ..
```

## Quick Start

```python
import gmaps

# Configure API key
gmaps.configure(api_key="YOUR_API_KEY")

# Create a map
m = gmaps.Map()

# Create a tagged region
region = gmaps.TaggedRegion(
    name="Golden Gate Park",
    coordinates=[
        (37.771, -122.511),
        (37.771, -122.453),
        (37.766, -122.453),
        (37.766, -122.511)
    ],
    description="Large urban park in San Francisco",
    tags=["park", "recreation", "landmark"],
    wikipedia_url="https://en.wikipedia.org/wiki/Golden_Gate_Park",
    fill_color="green",
    fill_opacity=0.4
)

# Add to map
m.add_layer(region)
m
```

## API Reference

### TaggedRegion Class

#### Required Parameters

- **name** (`str`): Name of the region
- **coordinates** (`list of tuples`): List of (latitude, longitude) pairs defining the polygon boundary. Minimum 3 points required.

#### Optional Parameters

- **description** (`str`, default=""): Text description of the region
- **tags** (`list of str`, default=[]): List of tags for categorization
- **data** (`dict`, default={}): Dictionary of custom metadata key-value pairs
- **wikipedia_url** (`str`, default=""): URL to Wikipedia or similar reference source

#### Styling Parameters

- **fill_color** (`str`, default="#0000FF"): Polygon fill color (CSS color name or hex code)
- **fill_opacity** (`float`, default=0.35): Fill transparency (0.0 = transparent, 1.0 = opaque)
- **stroke_color** (`str`, default="#0000FF"): Border color (CSS color name or hex code)
- **stroke_opacity** (`float`, default=0.8): Border transparency (0.0 = transparent, 1.0 = opaque)
- **stroke_weight** (`int`, default=2): Border width in pixels

## Examples

### Basic Region

```python
park = gmaps.TaggedRegion(
    name="Central Park",
    coordinates=[
        (40.8, -73.96),
        (40.8, -73.95),
        (40.76, -73.95),
        (40.76, -73.96)
    ],
    description="Urban park in Manhattan"
)
```

### Region with Tags and Metadata

```python
tech_hub = gmaps.TaggedRegion(
    name="Silicon Valley",
    coordinates=[
        (37.4, -122.2),
        (37.4, -121.9),
        (37.3, -121.9),
        (37.3, -122.2)
    ],
    description="Global center for technology and innovation",
    tags=["technology", "innovation", "business"],
    data={
        "Founded": "1970s",
        "Famous Companies": "Google, Apple, Facebook",
        "Industry": "Technology & Software"
    },
    wikipedia_url="https://en.wikipedia.org/wiki/Silicon_Valley",
    fill_color="#4285F4",
    fill_opacity=0.35
)
```

### Complex Polygon

```python
# Non-rectangular shape with 6 vertices
city = gmaps.TaggedRegion(
    name="San Francisco",
    coordinates=[
        (37.8, -122.52),
        (37.81, -122.48),
        (37.78, -122.38),
        (37.72, -122.38),
        (37.71, -122.42),
        (37.72, -122.50)
    ],
    description="The City by the Bay",
    tags=["city", "metropolitan", "culture"],
    fill_color="#FF4500",
    fill_opacity=0.3,
    stroke_weight=3
)
```

### Multiple Regions

```python
m = gmaps.Map()

# Add multiple regions to the same map
m.add_layer(region1)
m.add_layer(region2)
m.add_layer(region3)

m
```

## Interactive Features

When a user clicks on a region, an info window displays:
- **Region Name** (as header)
- **Description** (if provided)
- **Tags** (as styled badges)
- **Custom Data** (key-value pairs)
- **Wikipedia Link** (opens in new tab if provided)

## Technical Architecture

### Python Backend (`gmaps/maps.py`)

The `TaggedRegion` class extends `ipywidgets.Widget` and follows the same pattern as other layer types:
- Validates coordinates (minimum 3 points)
- Calculates data bounds for map fitting
- Syncs all properties with JavaScript frontend via traitlets

### JavaScript Frontend (`js/src/jupyter-gmaps.js`)

The frontend implementation includes:
- `TaggedRegionLayerView`: Renders polygons using Google Maps Polygon API
- `TaggedRegionLayerModel`: Handles data synchronization
- Info window generation with styled HTML content
- Click event handling for interactivity

## Development Notes

### Building

```bash
cd js
npm run build
cd ..
python setup.py develop
```

### Testing

See the example notebook at `examples/tagged_regions_example.ipynb` for comprehensive usage examples.

## Limitations & Future Enhancements

### Current Limitations
- Regions are static after creation (no dynamic editing UI)
- Single info window per region (no multi-section tabs)
- No export functionality (e.g., to GeoJSON)

### Potential Future Features
- Drawing tool for interactive region creation
- Import/export GeoJSON support
- Region search and filtering
- Custom info window templates
- Region clustering for dense datasets
- Edit mode for updating regions
- Multiple external links (not just Wikipedia)
- Image attachments in region metadata
- Time-based region data (historical changes)

## License

Same as the parent jupyter-gmaps project.

## Contributing

Follow the standard jupyter-gmaps contribution guidelines. For issues or feature requests related to tagged regions, please file an issue on the repository.
