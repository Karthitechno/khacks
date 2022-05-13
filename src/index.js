import React from "react";
import ReactDOM from "react-dom";
import DeckGLOverlay from "./DeckGLOverlay";
import Menu from './Menu'
import Popup from './components/Popup'

import "./styles.css";

function App() {
  return (
    <div className="App">
      <DeckGLOverlay />
      {/* <Menu /> */}
      <Popup />
    </div>
  );
}

const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);
