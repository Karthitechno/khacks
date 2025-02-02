import React, { useState } from 'react';
import Popup from 'reactjs-popup';
import './Popup.css'

const ControlledPopup = () => {
    const [open, setOpen] = useState(true);
    const closeModal = () => setOpen(false);
    return (
        <div>
            <Popup open={open} closeOnDocumentClick onClose={closeModal}>
                <div className="modal">
                    <a className="close" onClick={closeModal}>
                        &times;
                    </a>
                    <p className='note'>
                        <strong>
                            Note
                        </strong><br />
                        <ul>
                            <li>This is a prototype, this is what we have done on the frontend so far.</li>
                            <li> The finished dashboard will be somewhat different with additional features. </li>
                            <li>Please hover over the data points to see details</li>
                        </ul>
                    </p>
                </div>
            </Popup>
        </div>
    );
};

export default ControlledPopup