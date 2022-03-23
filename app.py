import sys
from dash import Dash, html
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function, assign
import json
import amenities_mapper.cdp as cdp
import amenities_mapper.map_util as mu
import amenities_mapper.starbucks as starbucks
from dash.dependencies import Output, Input


# Get data to create amenity layers
lib_dict, pharm_dict, mur_dict, cafe_dicts = cdp.get_data_dicts()


# Create geojsons for amenities
geojson_starb = dlx.dicts_to_geojson(cafe_dicts)
geojson_libs = dlx.dicts_to_geojson(lib_dict)
geojson_pharms = dlx.dicts_to_geojson(pharm_dict)
geojson_murals = dlx.dicts_to_geojson(mur_dict)


# Get data to compute Shannon score
lib, pharm, murals = mu.geo_df()
sbucks = starbucks.starbucks_df()


# Get choropleth data for income and demographics
income_choro, demo_choro, colors = mu.choropleth_data()


# Customize colors for income data
bin_inc, colorscale_inc, bin_demo, colorscale_demo = colors
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)


# Create colorbars
ctg_demo = ["{:.1f}+".format(cls, bin_demo[i + 1]) for i, cls in
                        enumerate(bin_demo[:-1])] + ["{:.1f}+".format(bin_demo[-1])]
colorbar_demo = dlx.categorical_colorbar(categories=ctg_demo,
                                colorscale=colorscale_demo,
                                className = "Share of Black residents",
                                width = 300, height = 30, position = "bottomleft")
ctg_inc = ["{:.1f}+".format(cls, bin_inc[i + 1]) for i, cls in enumerate(bin_inc[:-1])] + ["{:.1f}+".format(bin_inc[-1])]
colorbar_inc = dlx.categorical_colorbar(categories=ctg_inc, colorscale=colorscale_inc,
                                className = "Per capita income in 1K$",
                                width = 300, height = 30, position = "bottomleft")


# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")


# Create geojsons for chloropleth
choro_income = dl.GeoJSON(data = json.loads(income_choro.to_json()),  # url to geojson file
                     options=dict(style=style_handle),  # how to style each polygon
                     zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
                     zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
                     hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),  # style applied on hover
                     hideout=dict(colorscale=colorscale_inc, classes=bin_inc, style=style, colorProp="income_per_1000"),
                     id="choro_income")
choro_demo = dl.GeoJSON(data = json.loads(demo_choro.to_json()),  # url to geojson file
                     options=dict(style=style_handle),  # how to style each polygon
                     zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
                     zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
                     hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),  # style applied on hover
                     hideout=dict(colorscale=colorscale_demo, classes=bin_demo, style=style, colorProp="share_BLACK"),
                     id="choro_demo")


# Create info panel function
def get_info(si=None):
    '''
    Displays Shannon index score for a clicked location on the map.
    Inputs:
        si: float
    Returns:
        html objects
    '''

    header = [html.H4("Amenities in Chicago Community Areas Within 15 Minutes Walking Distance")]
    if not si:
        return header + [html.P("Click anywhere in Chicago to calculate "\
                        "the density and diversity of amenities within walking "\
                        "distance of the selected coordinates")]
    return header + [html.B("Shannon Index Score: {:.4f}".format(si)) , html.Br(),
                    "A score above 0.0273 indicates that "\
                    "there is at least one amenity from each category, or several from few."
                    ]


# Create info control
info = html.Div(children=get_info(), id="info", className="info",
                style={"position": "absolute", "top": "10px", "left": "10px", "z-index": "1000"})


# Generate icons
# Credit to Github user pointhi for their icon images
draw_point = assign("""function(feature, latlng){
const point = L.icon({iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${feature.properties.color}.png`, iconSize: [20, 24]});
return L.marker(latlng, {icon: point});
}""")


# Create app
app = Dash()
app.layout = html.Div(children=[
    html.H1(children="Chicago Amenities"),
    dl.Map(
        [
            dl.LayersControl(
                [
                    dl.Overlay(
                        dl.LayerGroup([choro_income]), name='Community Area, Income', checked=True),
                    dl.Overlay(
                        dl.LayerGroup([choro_demo]), name='Share of Black residents', checked=True),  
                    dl.Overlay(
                        dl.LayerGroup(children=[
                            dl.TileLayer(),
                            dl.GeoJSON(data=geojson_starb,
                            cluster=True,
                            options=dict(pointToLayer=draw_point),
                            zoomToBounds=True)]), name='starbucks', checked=True),
                    dl.Overlay(
                        dl.LayerGroup(children=[
                            dl.TileLayer(),
                            dl.GeoJSON(data=geojson_pharms,
                            cluster=True,
                            options=dict(pointToLayer=draw_point),
                            zoomToBounds=True)]), name='pharmacies', checked=True),
                    dl.Overlay(
                        dl.LayerGroup(children=[
                            dl.TileLayer(),
                            dl.GeoJSON(data=geojson_murals,
                            cluster=True,
                            options=dict(pointToLayer=draw_point),
                            zoomToBounds=True)]), name='murals', checked=True),
                    dl.Overlay(
                        dl.LayerGroup(children=[
                            dl.TileLayer(),
                            dl.GeoJSON(data=geojson_libs,
                            cluster=True,
                            options=dict(pointToLayer=draw_point),
                            zoomToBounds=True)]), name='libraries', checked=True)]),
                dl.TileLayer(), colorbar_inc, colorbar_demo, info
                ],
        zoom=10,
        center=(41.8781, -87.5298), id='map',
    )],
    style={
        'width': '98%', 'height': '60vh', 'margin': "auto", "display": "block",
    }
)


# Add mouse click feature
@app.callback(Output("info", "children"), [Input("map", "click_lat_lng")])
def info_click(click_lat_lng):
    '''
    Computes Shannon index score and updates the display box with the Shannon score.
    Inputs:
        click_lat_lng: list of floats
    Returns:
        updates to the display box
    '''

    si = mu.compute_shannon_index(click_lat_lng, lib, pharm, murals, sbucks)
    return get_info(si)

if __name__ == '__main__':
    app.run_server()
