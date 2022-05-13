import React from "react";
import GoogleMapReact from "google-map-react";
import { GoogleMapsOverlay } from "@deck.gl/google-maps";
import { ScatterplotLayer } from "@deck.gl/layers";
import { HeatmapLayer, HexagonLayer } from '@deck.gl/aggregation-layers';
import mapStyles from "./map-styles";

const sourceData = './edited2.json';


const heatmap = () => new HeatmapLayer({
  id: 'heat',
  data: sourceData,
  getPosition: d => [Number(d.longitude), Number(d.latitude)],
  getWeight: d => d.level * 1.1,
  radiusPixels: 20,
});

const hexagon = () => new HexagonLayer({
  id: 'hex',
  data: sourceData,
  getPosition: d => {return [Number(d.longitude), Number(d.latitude)]},
  getElevationWeight: d => {return d.level * 1000},
  elevationScale: 1000,
  extruded: true,
  radius: 10609,         
  opacity: 0.6,        
  coverage: 0.88,
  lowerPercentile: 50
});

const DeckGLOverlay = () => {
  const handleApiLoaded = map => {
    const overlay = new GoogleMapsOverlay({});
    overlay.setMap(map);
    overlay.setProps({
      layers: [
        scatterplot(),
        heatmap(),
        hexagon()
      ]
    });
  };

  const tooltip = React.useRef(null)
  const [details,setDetails] = React.useState({})

  const scatterplot = () => new ScatterplotLayer({
    id: 'scatter',
    data: sourceData,
    opacity: 0.8,
    filled: true,
    radiusMinPixels: 2,
    radiusMaxPixels: 5,
    getPosition: d => [Number(d.longitude), Number(d.latitude)],
    getFillColor: d => d.level > 2 ? [200, 0, 40, 150] : [255, 140, 0, 100],
  
    pickable: true,
    onHover: ({object, x, y}) => {
        if(object){
          tooltip.current.style.display = 'block'
          tooltip.current.style.left = x + 'px'
          tooltip.current.style.top = y + 'px'
          setDetails(object)
        }
        else{
          tooltip.current.style.display = 'none'
        }
    },
  
    onClick: ({object, x, y}) => {
      console.log(object)
    },
  });

  return (
    
    <>
      <GoogleMapReact
        bootstrapURLKeys={{ key: "AIzaSyB_osK5Rg2Jpir8rp0h6GlHYR7pvLiCYTw" }}
        center={{ lat: 20.5937, lng: 78.9629 }}
        zoom={4.8}
        options={{ disableDoubleClickZoom: true, styles: mapStyles}}
        onGoogleApiLoaded={({ map }) => handleApiLoaded(map)}
        yesIWantToUseGoogleMapApiInternals
      />
      <div id="tooltip" ref={tooltip}>
        <p>Disaster : {details.disastertype}</p>  
        <p>Level : {details.level}</p>  
        <p>Location : {details.geolocation}</p>  
      </div>
    </>
  );
};

export default DeckGLOverlay;
