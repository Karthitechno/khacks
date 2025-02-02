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
    radiusMinPixels: 20,
    radiusMaxPixels: 50,
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
        bootstrapURLKeys={{ key: "AIzaSyAQmWuNTAvV45gVfbpMkv2RMdB6NxtZWpo" }}
        center={{ lat: 20.5937, lng: 78.9629 }}
        zoom={4.8}
        options={{ disableDoubleClickZoom: true, styles: mapStyles}}
        onGoogleApiLoaded={({ map }) => handleApiLoaded(map)}
        yesIWantToUseGoogleMapApiInternals
      />
      <div id="tooltip" ref={tooltip}>
        
      <p>Capsize Probability:{details.p}</p>
        <p>Risk Level:{details.level}</p>
        <p>Wind Speed : {details.ws}</p>  
        <p>Wind Stress : {details.tau}</p>
        <p>Wave Height : {details.wave_height}</p>
        <p>Boat Length : {details.bt_ln}</p>
        <p>Boat Height : {details.bt_ht}</p>
        <p>Boat Breadth : {details.bt_br}</p>
        <p> latitude : {details.latitude}</p>
        <p>longitude:{details.longitude}</p>
        <p>Nearby Port:{details.Nearby_Port}</p>
        <p>Distance To Nearset Port : {details.distance}</p>
        <p></p>
      </div>
    </>
  );
};

export default DeckGLOverlay;
